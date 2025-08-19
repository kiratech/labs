from pathlib import Path
from typing import Dict, Any
from chromadb import PersistentClient
from chromadb.utils import embedding_functions
from .config import PERSIST_DIR, KB_DIR, EMB_MODEL

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
            chunks = [text[i:i+2000] for i in range(0, len(text), 1600)]
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
