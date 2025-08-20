from typing import TypedDict, Annotated
import operator
import json
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from .config import HF_MODEL_ID
from .rag_core import retrieve

@tool
def search_policies(query: str) -> str:
    """Search the internal knowledge base (RAG) and return a JSON list of
    matches with fields: source, chunk, text."""
    hits = retrieve(query, k=4)
    return json.dumps(
        [{"source": h["meta"]["source"], "chunk": h["meta"]["chunk"], "text": h["text"]} for h in hits]
    )

@tool
def calc(expression: str) -> str:
    """Evaluate a simple arithmetic expression (e.g., '12*(3+4)').
    Returns the stringified result or an error message."""
    try:
        out = str(eval(expression, {"__builtins__": {}}))
    except Exception as e:
        out = f"Error: {e}"
    return out

@tool
def create_ticket(category: str, description: str) -> str:
    """Simulate creating a support ticket and return a JSON payload with
    ticket_id and status."""
    ticket_id = "TKT-" + str(abs(hash(category + description)) % 10_000)
    return json.dumps({"ticket_id": ticket_id, "status": "created"})

TOOLS = [search_policies, calc, create_ticket]

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]

# Hugging Face chat model
llm = HuggingFaceEndpoint(
    repo_id=HF_MODEL_ID,
    task="text-generation",
    max_new_tokens=512,
    do_sample=False,
)
chat_model = ChatHuggingFace(llm=llm)   # LangChain wrapper for HF chat models
tool_node = ToolNode(TOOLS)

def call_model(state: AgentState) -> AgentState:
    response = chat_model.invoke(state["messages"])
    return {"messages": [response]}

def route_after_model(state: AgentState) -> str:
    last = state["messages"][-1]
    if getattr(last, "tool_calls", None):
        return "tools"
    return END

_graph = StateGraph(AgentState)
_graph.add_node("agent", call_model)
_graph.add_node("tools", tool_node)
_graph.add_edge("tools", "agent")
_graph.add_conditional_edges("agent", route_after_model)
_graph.set_entry_point("agent")

checkpointer = MemorySaver()
agent_graph = _graph.compile(checkpointer=checkpointer)

SYSTEM_PROMPT = (
    "You are a support agent. First, outline a brief plan, then use tools when needed:\n"
    "- search_policies for KB-based answers (cite sources)\n"
    "- calc for small computations\n"
    "- create_ticket when escalation is required by policy\n"
    "Respond in concise English. Do not fabricate facts not present in sources."
)

def run_agent_with_langgraph(question: str, thread_id: str | None = None) -> dict:
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
