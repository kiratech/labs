"""Core RAG utilities: ingestion, retrieval and generation.

This module provides a tiny pipeline for:
- indexing markdown/text policy files into a persistent Chroma collection
  (ingest).
- performing semantic retrieval against the collection (retrieve).
- formatting retrieved context and calling a Hugging Face InferenceClient
  (OpenAI-compatible router/chat completions) to produce a final answer
  with citations (generate).

Notes / operational guidance
- PERSIST_DIR, EMB_MODEL, HUGGINGFACEHUB_API_TOKEN and HF_MODEL_ID are
  configured in lab_service.config. Ensure HF_MODEL_ID points to a
  model/router that supports the OpenAI-compatible chat/completions
  endpoint if you call client.chat.completions.create(...) (otherwise
  the hub may return 404).
- The ingestion logic uses simple fixed-size chunking for demo purposes;
  production systems should use a semantic/overlap-aware chunker.
"""
from pathlib import Path
from typing import List, Dict, Any
from chromadb import PersistentClient
from chromadb.utils import embedding_functions
from huggingface_hub import InferenceClient

from .config import (
    PERSIST_DIR,
    KB_DIR,
    EMB_MODEL,
    HUGGINGFACEHUB_API_TOKEN,
    HF_MODEL_ID,
)
from .models import RAGResponse

def _chroma():
    """Create a PersistentClient pointing at the configured PERSIST_DIR.

    Returns
    -------
    chromadb.PersistentClient
        Client instance to interact with the persistent Chroma DB.
    """
    # Chroma stores collections on-disk at PERSIST_DIR when using PersistentClient
    return PersistentClient(path=PERSIST_DIR)


def _collection():
    """Get or create the 'policies' collection with the configured embedding fn.

    The collection is created with a SentenceTransformer embedding function
    backed by EMB_MODEL (a sentence-transformers model id). This ensures
    documents and queries are encoded consistently.
    """
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMB_MODEL)
    return _chroma().get_or_create_collection("policies", embedding_function=ef)


def ingest(source_dir: str | None = None, reset: bool = False) -> Dict[str, Any]:
    """Index markdown/text files from source_dir (or KB_DIR) into Chroma.

    The function:
    - walks the source directory recursively,
    - reads .md and .txt files,
    - splits each file into fixed-size chunks (simple demo strategy),
    - stores documents, ids and metadata into the 'policies' collection.

    Parameters
    ----------
    source_dir : str | None
        Path to scan for documents. If None, uses configured KB_DIR.
    reset : bool
        If True, deletes the existing 'policies' collection before ingesting.

    Returns
    -------
    dict
        Summary with number of indexed files and total chunks added.
    """
    source = Path(source_dir or KB_DIR)
    col = _collection()
    if reset:
        # Delete and recreate to ensure a clean state when requested
        _chroma().delete_collection("policies")
        col = _collection()

    files_indexed = 0
    docs, ids, metas = [], [], []
    for p in source.rglob("*"):
        # Only ingest markdown and plain text files
        if p.suffix.lower() in {".md", ".txt"}:
            text = p.read_text(encoding="utf-8", errors="ignore")
            # Simple chunking for demo: chunk length 2000, overlap ~400
            chunks = [text[i:i + 2000] for i in range(0, len(text), 1600)]
            for k, ch in enumerate(chunks):
                ids.append(f"{p.stem}-{files_indexed}-{k}")
                docs.append(ch)
                metas.append({"source": str(p), "chunk": k})
            files_indexed += 1

    if docs:
        # Bulk-add to the collection
        col.add(documents=docs, ids=ids, metadatas=metas)

    return {"indexed_files": files_indexed, "chunks": len(docs)}


def retrieve(query: str, k: int = 4):
    """Run a semantic retrieval query against the 'policies' collection.

    Parameters
    ----------
    query : str
        Natural language query text.
    k : int
        Number of top results to return.

    Returns
    -------
    list[dict]
        List of hits with keys: text, snippet, meta, score.
        - text: full chunk text
        - snippet: short excerpt for quick display
        - meta: metadata dict (includes 'source' and 'chunk')
        - score: similarity/distance score as float
    """
    res = _collection().query(query_texts=[query], n_results=k)
    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]
    dists = res.get("distances", [[]])[0]
    out = []
    for d, m, s in zip(docs, metas, dists):
        snippet = d[:400] + ("..." if len(d) > 400 else "")
        out.append({"text": d, "snippet": snippet, "meta": m, "score": float(s)})
    return out


def _format_sources(ctx: List[Dict[str, Any]]) -> str:
    """Serialize retrieved context into a plain-text block for the model prompt.

    The format enumerates sources ([1], [2], ...) and includes each chunk's
    text. This string is intended to be attached to the user prompt so the
    model can refer to explicit passages.

    Parameters
    ----------
    ctx : list[dict]
        Retrieval results as returned by retrieve().

    Returns
    -------
    str
        Multi-line string containing numbered sources and their corresponding text.
    """
    lines = []
    for i, c in enumerate(ctx, 1):
        src = c["meta"]["source"]
        ch = c["meta"]["chunk"]
        # Keep the full chunk in the prompt; the model can use snippet if needed.
        lines.append(f"[{i}] {src} (chunk {ch})\n{c['text']}\n")
    return "\n".join(lines)


def generate(question: str, k: int = 4) -> RAGResponse:
    """Produce a RAG-formatted answer calling a Hugging Face InferenceClient.

    Steps:
    1. Retrieve top-k relevant chunks from the KB.
    2. Build a system + user prompt that instructs the model to answer ONLY
       using the provided sources and to return strict JSON.
    3. Call the InferenceClient chat/completions endpoint.
    4. Parse the model output as JSON; if parsing fails, fall back to returning
       the raw content and attaching the top-k sources as citations.

    Important:
    - HF_MODEL_ID must refer to a model/router that exposes an OpenAI-compatible
      chat/completions endpoint when using client.chat.completions.create(...).
      Otherwise the Hugging Face Hub may return 404/Not Found.
    - HUGGINGFACEHUB_API_TOKEN should be set for private models or router usage.

    Parameters
    ----------
    question : str
        User question to answer.
    k : int
        Number of retrieved context chunks to pass to the model.

    Returns
    -------
    RAGResponse
        answer: final text (or raw model content on parse failure)
        citations: list of dicts with keys 'source' and 'chunk'
    """
    ctx = retrieve(question, k=k)
    if not ctx:
        return RAGResponse(answer="No documents found in the knowledge base.", citations=[])

    # Guidance to the model: be strict and only use the provided sources.
    system = (
        "You are a helpful assistant that must answer ONLY using the provided sources. "
        "If the information is not present in the sources, explicitly say so. "
        "Answer in concise English. Always include citations as [1], [2], ..."
    )
    user = (
        f"Question: {question}\n\n"
        f"Sources:\n{_format_sources(ctx)}\n\n"
        "Return a valid JSON object with the following shape: "
        "{'answer': str, 'citations': [{'source': str, 'chunk': int}]}"
    )

    # Create the InferenceClient. The `provider` and invocation style can vary
    # depending on how HF_MODEL_ID is exposed (router, custom provider, etc.).
    client =  InferenceClient(provider="together", api_key=HUGGINGFACEHUB_API_TOKEN)

    # Call the chat completions API. This may raise HTTP errors from the hub
    # (e.g., 404 if the route/model is not available) — let exceptions bubble
    # up to the caller or handle them where the generate() function is used.
    chat = client.chat.completions.create(
        model=HF_MODEL_ID,                                
        messages=[{"role":"system","content":system},
                  {"role":"user","content":user}],
        temperature=0.2,
        max_tokens=512,
    )

    content = chat.choices[0].message.content or ""

    import json
    try:
        # Expect the model to return a strict JSON object per the prompt.
        data = json.loads(content)
        ans = data.get("answer", "")
        cits = data.get("citations", [])
    except Exception:
        # If parsing fails, return the raw content and attach the retrieved sources
        # as fallback citations so the caller can still show provenance.
        ans = content
        cits = [{"source": c["meta"]["source"], "chunk": c["meta"]["chunk"]} for c in ctx]

    return RAGResponse(answer=ans, citations=cits)