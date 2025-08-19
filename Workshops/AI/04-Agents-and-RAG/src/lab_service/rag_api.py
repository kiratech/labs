from fastapi import APIRouter
from pydantic import BaseModel
from .rag_core import build_index, retrieve

router = APIRouter(prefix="/rag", tags=["RAG"])

class IngestReq(BaseModel):
    source_dir: str | None = None
    reset: bool = False

@router.post("/ingest")
def ingest(req: IngestReq):
    return build_index(req.source_dir, req.reset)

class SearchReq(BaseModel):
    query: str
    k: int = 4

@router.post("/search")
def search(req: SearchReq):
    return {"query": req.query, "results": retrieve(req.query, k=req.k)}
