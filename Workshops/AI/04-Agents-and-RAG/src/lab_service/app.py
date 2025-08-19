from fastapi import FastAPI
from .rag_api import router as rag_router

app = FastAPI(title="AI Academy - RAG & Agents API (Step 1)")

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

app.include_router(rag_router)
