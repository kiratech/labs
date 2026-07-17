"""Pydantic request/response models used by the RAG & Agents FastAPI services.

This module defines lightweight DTOs for incoming API requests and for the
RAG response payload. Keep these models minimal and stable since they form
the public contract of the HTTP endpoints.
"""
from pydantic import BaseModel
from typing import List, Dict, Any


class AskReq(BaseModel):
    """Request body for the /agent/ask endpoint.

    Attributes
    ----------
    question : str
        User's free-text question to the language agent.
    thread_id : str | None
        Optional identifier to continue a conversation thread (preserved by the caller).
    """
    question: str
    thread_id: str | None = None


class IngestReq(BaseModel):
    """Request for (re)ingesting documents into the retriever/embedding store.

    Attributes
    ----------
    source_dir : str | None
        Optional path containing documents to ingest. If omitted, use configured KB_DIR.
    reset : bool
        If True, clear existing persisted embeddings/vector DB before ingesting.
    """
    source_dir: str | None = None
    reset: bool = False


class SearchReq(BaseModel):
    """Simple search/retrieval request.

    Used when invoking the retriever directly.

    Attributes
    ----------
    query : str
        Query text to search the KB.
    k : int
        Number of top documents to return (default: 4).
    """
    query: str
    k: int = 4


class QueryReq(BaseModel):
    """RAG-style query payload for the /rag/generate endpoint.

    Attributes
    ----------
    question : str
        The user's natural language question to answer using RAG.
    k : int
        Number of retrieved documents to use as context (default: 4).
    """
    question: str
    k: int = 4


class RAGResponse(BaseModel):
    """Canonical RAG response returned by /rag/generate.

    Attributes
    ----------
    answer : str
        Generated answer text produced by the model using retrieved context.
    citations : list[dict]
        List of citation metadata for the retrieved documents used to form the answer.
        Each dict should minimally include source identifiers and optional excerpt/score.
        Example item: {"id": "20_shipping_sla.md#SLA-214", "text": "...", "score": 0.92}
    """
    answer: str
    citations: List[Dict[str, Any]]
