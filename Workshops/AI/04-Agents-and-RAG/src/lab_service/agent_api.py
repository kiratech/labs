"""API endpoints for agent interactions.

This module exposes a single FastAPI router for agent-related operations.
Endpoints call into the language-graph agent implementation and return
the agent response. Designed to be lightweight: validation and business
logic live in the agent implementation.

Endpoints
- POST /agent/ask   -> Handle a user question via the language-graph agent.
"""
from fastapi import APIRouter
from .agent_graph import run_agent_with_langgraph
from .models import AskReq

router = APIRouter(prefix="/agent", tags=["Agent"])

@router.post("/ask")
def ask(req: AskReq):
    """Handle a user question and run the language-graph agent.

    Parameters
    ----------
    req : AskReq
        Request body containing:
        - question: the user's question string
        - thread_id: optional identifier to continue a conversation thread

    Returns
    -------
    dict | Any
        The agent response produced by run_agent_with_langgraph. The exact
        shape depends on the agent implementation (typically a dict with
        answer, sources, and metadata).

    Notes
    -----
    Exceptions raised by the agent implementation are propagated to the
    FastAPI framework and will be converted to HTTP error responses.
    """
    return run_agent_with_langgraph(req.question, thread_id=req.thread_id)
