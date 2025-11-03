"""FastAPI router exposing simple RAG endpoints: ingest, retrieve and generate.

This module provides thin HTTP adapters over the rag_core utilities. Keep
business logic in rag_core; these endpoints are responsible for request
validation (Pydantic models) and for returning well-typed responses.

Endpoints
- POST /rag/ingest   -> trigger (re)ingestion of KB files
- POST /rag/retrieve -> run semantic search against the KB
- POST /rag/generate  -> run RAG generation using top-k retrieved chunks
"""
from fastapi import APIRouter
from .models import IngestReq, SearchReq, QueryReq
from .rag_core import ingest, retrieve, generate, RAGResponse

router = APIRouter(prefix="/rag", tags=["RAG"])

@router.post("/ingest")
def ingest_api(req: IngestReq):
    """Trigger ingestion of markdown/plain-text files into the vector store.

    Parameters
    ----------
    req : IngestReq
        - source_dir: optional path to scan (defaults to configured KB_DIR)
        - reset: if True, clear existing collection before ingesting

    Returns
    -------
    dict
        Summary containing indexed_files and chunks added.
    """
    # Thin adapter: delegate to rag_core.ingest which handles file IO and persistence.
    return ingest(req.source_dir, req.reset)

@router.post("/retrieve")
def retrieve_api(req: SearchReq):
    """Run a semantic retrieval against the policies collection.

    Parameters
    ----------
    req : SearchReq
        - query: query text
        - k: number of top results to return

    Returns
    -------
    dict
        Echoes the query and returns the list of retrieval hits under "results".
        Each result includes text, snippet, meta and score.
    """
    return {"query": req.query, "results": retrieve(req.query, k=req.k)}

@router.post("/generate", response_model=RAGResponse)
def generate_api(req: QueryReq):
    """Produce a RAG answer using top-k retrieved context.

    Parameters
    ----------
    req : QueryReq
        - question: user question
        - k: number of retrieved chunks to pass to the model

    Returns
    -------
    RAGResponse
        Structured response with 'answer' and 'citations'.
    """
    # Delegate to rag_core.generate which performs retrieval, calls the model,
    # and formats the RAGResponse. Any HF/IO errors propagate as HTTP 500.
    return generate(req.question, k=req.k)
