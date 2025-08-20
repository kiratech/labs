from pathlib import Path
from typing import List, Dict, Any
from chromadb import PersistentClient
from chromadb.utils import embedding_functions
from pydantic import BaseModel
from huggingface_hub import InferenceClient

from .config import (
    PERSIST_DIR,
    KB_DIR,
    EMB_MODEL,
    HUGGINGFACEHUB_API_TOKEN,
    HF_MODEL_ID,
)


# ---------------------------
# Vector store (Chroma)
# ---------------------------
def _chroma():
    return PersistentClient(path=PERSIST_DIR)


def _collection():
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMB_MODEL)
    return _chroma().get_or_create_collection("policies", embedding_function=ef)


def build_index(source_dir: str | None = None, reset: bool = False) -> Dict[str, Any]:
    source = Path(source_dir or KB_DIR)
    col = _collection()
    if reset:
        _chroma().delete_collection("policies")
        col = _collection()

    files_indexed = 0
    docs, ids, metas = [], [], []
    for p in source.rglob("*"):
        if p.suffix.lower() in {".md", ".txt"}:
            text = p.read_text(encoding="utf-8", errors="ignore")
            # simple chunking for demo
            chunks = [text[i:i + 2000] for i in range(0, len(text), 1600)]
            for k, ch in enumerate(chunks):
                ids.append(f"{p.stem}-{files_indexed}-{k}")
                docs.append(ch)
                metas.append({"source": str(p), "chunk": k})
            files_indexed += 1

    if docs:
        col.add(documents=docs, ids=ids, metadatas=metas)

    return {"indexed_files": files_indexed, "chunks": len(docs)}


def retrieve(query: str, k: int = 4):
    res = _collection().query(query_texts=[query], n_results=k)
    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]
    dists = res.get("distances", [[]])[0]
    out = []
    for d, m, s in zip(docs, metas, dists):
        snippet = d[:400] + ("..." if len(d) > 400 else "")
        out.append({"text": d, "snippet": snippet, "meta": m, "score": float(s)})
    return out


# ---------------------------
# RAG answer with citations
# ---------------------------
class RAGResponse(BaseModel):
    answer: str
    citations: List[Dict[str, Any]]


def _format_sources(ctx: List[Dict[str, Any]]) -> str:
    lines = []
    for i, c in enumerate(ctx, 1):
        src = c["meta"]["source"]
        ch = c["meta"]["chunk"]
        lines.append(f"[{i}] {src} (chunk {ch})\n{c['text']}\n")
    return "\n".join(lines)


def answer_with_citations(question: str, k: int = 4) -> RAGResponse:
    """
    Use Hugging Face's OpenAI-compatible Router for chat completions.
    The model stays a Hub repo id. We ask the model to return strict JSON;
    if it doesn't, we fall back to attaching top-k sources.
    """
    ctx = retrieve(question, k=k)
    if not ctx:
        return RAGResponse(answer="No documents found in the knowledge base.", citations=[])

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

    client =  InferenceClient(provider="novita", api_key=HUGGINGFACEHUB_API_TOKEN)

    chat = client.chat.completions.create(
        model=HF_MODEL_ID,                                # e.g., "meta-llama/Meta-Llama-3-8B-Instruct"
        messages=[{"role":"system","content":system},
                  {"role":"user","content":user}],
        temperature=0.2,
        max_tokens=512,
    )

    content = chat.choices[0].message.content or ""

    import json
    try:
        data = json.loads(content)
        ans = data.get("answer", "")
        cits = data.get("citations", [])
    except Exception:
        ans = content
        cits = [{"source": c["meta"]["source"], "chunk": c["meta"]["chunk"]} for c in ctx]

    return RAGResponse(answer=ans, citations=cits)