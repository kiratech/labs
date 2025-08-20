from fastapi import APIRouter
from pydantic import BaseModel
from .agent_graph import run_agent_with_langgraph

router = APIRouter(prefix="/agent", tags=["Agent"])

class AskReq(BaseModel):
    question: str
    thread_id: str | None = None

@router.post("/ask")
def ask(req: AskReq):
    return run_agent_with_langgraph(req.question, thread_id=req.thread_id)
