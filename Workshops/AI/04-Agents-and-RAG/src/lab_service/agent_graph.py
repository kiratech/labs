"""Graph-based agent wiring for the workshop demo.

This module composes a small language-graph agent that:
- accepts a user question,
- consults the policy knowledge base via a search tool,
- performs simple calculations or ticket creation when required,
- and calls a Hugging Face chat model to produce the final answer.

Design notes
- The graph is intentionally simple: an "agent" node that calls the LLM
  and a "tools" node that runs tools when the LLM requests them.
- Tools return JSON-serialisable strings; the LLM is expected to call tools
  and consume their outputs. Tool outputs are included in the conversational
  state so the model can reason over them in subsequent turns.
- The SYSTEM_PROMPT encodes strict policy guardrails. Keep it up-to-date
  with policy documents and retrieval/tooling guidelines.
"""
from typing import TypedDict, Annotated
import operator
import json
from pathlib import Path
from datetime import datetime
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from .config import HF_MODEL_ID
from .rag_core import retrieve
import re


# Regex to detect policy IDs in retrieved text (e.g., 'RET-103', 'SLA-214', 'EXM-900')
ID_RE = re.compile(r"\b([A-Z]{3}-\d{3}(?:-[A-Z]+)?)\b")

@tool
def search_policies(query: str) -> str:
    """Tool: run semantic search against the policies KB.

    Return JSON with hits: [{'source': str, 'chunk': int, 'ids': [str], 'excerpt': str}].
    Each hit contains:
      - source: file path of the document
      - chunk: integer chunk index
      - ids: list of policy IDs like RET-103, SLA-214 found in the excerpt
      - excerpt: short text excerpt for context

    The LLM should parse the returned JSON to extract cited policy IDs
    and exact wording for answers and citations.
    """
    hits = retrieve(query, k=6)
    out = []
    for h in hits:
        text = h["text"]
        ids = sorted(set(ID_RE.findall(text)))
        out.append({
            "source": h["meta"]["source"],
            "chunk": h["meta"]["chunk"],
            "ids": ids,
            "excerpt": text  # excerpt used by the model for context
        })
    return json.dumps(out)

@tool
def calc(expression: str) -> str:
    """Tool: safely evaluate a simple arithmetic expression (e.g., '12*(3+4)').

    Returns the stringified result or an error message.

    Purpose
    - Use when the agent needs to compute exact euro amounts, apply caps, etc.

    Security note
    - eval is run with an empty __builtins__ to reduce risk. This is a demo
      helper; consider a proper expression evaluator for production.
    """
    try:
        out = str(eval(expression, {"__builtins__": {}}))
    except Exception as e:
        out = f"Error: {e}"
    return out

@tool
def create_ticket(category: str, description: str) -> str:
    """Tool: simulate ticket creation, persist it to disk, and return a JSON payload.

    Behaviour:
    - Generates a deterministic ticket id for demo purposes.
    - Persists the ticket JSON into the project's data/tickets directory as <ticket_id>.json.
    - Returns a JSON string with ticket_id and status.

    Notes:
    - This is a demo persistence mechanism. In production use a proper ticketing DB/service.
    """
    ticket_id = "TKT-" + str(abs(hash(category + description)) % 10_000)
    ticket = {
        "ticket_id": ticket_id,
        "status": "created",
        "category": category,
        "description": description,
        "created_at": datetime.utcnow().isoformat() + "Z",
    }

    # Persist ticket to data/tickets/<ticket_id>.json (create dir if needed)
    tickets_dir = Path(__file__).resolve().parents[2] / "data" / "tickets"
    try:
        tickets_dir.mkdir(parents=True, exist_ok=True)
        ticket_file = tickets_dir / f"{ticket_id}.json"
        # Write atomically: write to .tmp then rename
        tmp_file = ticket_file.with_suffix(".json.tmp")
        tmp_file.write_text(json.dumps(ticket, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp_file.replace(ticket_file)
    except Exception as e:
        # If persistence fails, still return created ticket info but include an error field.
        ticket["status"] = "created_with_persist_error"
        ticket["persist_error"] = str(e)

    return json.dumps({"ticket_id": ticket_id, "status": "created"})

# Public tools list bound to the chat model and used by the ToolNode.
TOOLS = [search_policies, calc, create_ticket]

class AgentState(TypedDict):
    """TypedDict describing the graph state for the agent nodes.

    messages: conversational messages list that the chat model consumes/produces.
    The graph nodes expect 'messages' to be a list of AnyMessage-like objects.
    """
    messages: Annotated[list[AnyMessage], operator.add]

# Configure the Hugging Face endpoint wrapper used as the LLM.
# Note: repo_id must be compatible with the invocation style used by ChatHuggingFace.
llm = HuggingFaceEndpoint(
    repo_id=HF_MODEL_ID,
    task="text-generation",
    max_new_tokens=512,
    do_sample=False,
    temperature=0,
)

# Wrap the HF endpoint into a ChatHuggingFace model and bind the tools so the
# model can produce tool calls in its output.
chat_model = ChatHuggingFace(llm=llm).bind_tools(TOOLS)

# ToolNode integrates the callable tools into the graph so they can be invoked
# when the LLM requests them.
tool_node = ToolNode(TOOLS)


def call_model(state: AgentState) -> AgentState:
    """Graph node: call the chat model with the current messages.

    The model returns a message-like object. We wrap it into the AgentState
    shape expected by the graph (a dict with 'messages').
    """
    response = chat_model.invoke(state["messages"])
    return {"messages": [response]}


def route_after_model(state: AgentState) -> str:
    """Decide next node after the model runs.

    If the last message contains tool_calls, route to the 'tools' node,
    otherwise end the graph run (END).
    """
    last = state["messages"][-1]
    if getattr(last, "tool_calls", None):
        return "tools"
    return END


# Construct a small state graph and compile it with an in-memory checkpointer.
_graph = StateGraph(AgentState)
_graph.add_node("agent", call_model)
_graph.add_node("tools", tool_node)
# Loop between tools and agent: tools -> agent (model consumes tool outputs)
_graph.add_edge("tools", "agent")
# agent node can conditionally route to tools or END based on the model output
_graph.add_conditional_edges("agent", route_after_model)
_graph.set_entry_point("agent")

# Use an in-memory saver for checkpointing conversational state during the demo.
checkpointer = MemorySaver()
agent_graph = _graph.compile(checkpointer=checkpointer)

# System prompt: strict guardrails for policy-bound behaviour.
# Keep this synchronized with the policy documents and RAG retrieval expectations.
SYSTEM_PROMPT = (
    "You are a policy-bound support agent. Follow these RULES strictly:\n"
    "1) Always start with a short PLAN before answering.\n"
    "2) Use tools only when needed:\n"
    "   - Use `search_policies` BEFORE answering any policy question, lists, IDs, thresholds, examples.\n"
    "   - Use `calc` to compute exact euro amounts and to apply any caps/limits.\n"
    "   - Use `create_ticket` if the retrieved sources explicitly require it.\n"
    "   When a tool is needed, emit a tool call. The final answer will be formatted by the system."
    "   Multiple tool calls are allowed. For instance: \n"
    "     - First call `search_policies` to find relevant policies.\n"
    "     - Then call `calc` to compute refund amounts based on retrieved policy data.\n"
    "     - Finally, if a ticket is mandated by a TCK-5xx clause, call `create_ticket` with the correct category and reason.\n"
    "3) When using `search_policies`, cite policy IDs (e.g., [RET-103], [SLA-214]) included in the tool output. "
    "   Use ONLY facts present in the retrieved sources; do NOT invent.\n"
    "4) If information is insufficient, say so explicitly and stop.\n"
    "5) Responses must be concise, in English. "
    "If refunds/vouchers apply, include the exact euro amount; if a ticket is opened, include type and ticket ID>\n"
    "6) If refunds or vouchers apply, compute exact values and check caps/limits before answering.\n"
    "7) Do not open tickets unless a retrieved clause (e.g., TCK-5xx) requires it; cite that clause.\n"
    "8) When any TCK-5xx clause mandates escalation, call `create_ticket` immediately with the correct `category` and a short `reason`. Do not ask the user for permission, do not invent ticket IDs, and do not claim success until the tool returns.\n"
    "9) If you mention a ticket in the answer, ensure it was created via the tool; otherwise, call the tool before replying.\n"
)

def run_agent_with_langgraph(question: str, thread_id: str | None = None) -> dict:
    """Run the compiled language-graph agent for a single user question.

    Parameters
    ----------
    question : str
        The user's natural language question.
    thread_id : str | None
        Optional thread identifier to correlate conversation state across calls.

    Returns
    -------
    dict
        A dictionary with:
          - final_answer: the assistant's final rendered text (string)
          - thread_id: the thread identifier used (string)

    Behaviour
    - Initializes the conversation with SYSTEM_PROMPT and the user's question.
    - Invokes the compiled agent_graph which will alternate between model and tools
      as needed until completion.
    - The final message is returned as 'final_answer'. Tool outputs (JSON strings)
      are expected to be consumed by the model in intermediate steps.
    """
    config = {"configurable": {"thread_id": thread_id or "default"}}
    initial: AgentState = {
        "messages": [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=question),
        ]
    }
    final_state = agent_graph.invoke(initial, config=config)
    last = final_state["messages"][-1]
    return {"final_answer": getattr(last, "content", ""), "thread_id": config["configurable"]["thread_id"]}
