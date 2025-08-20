from fastapi import FastAPI
from .rag_api import router as rag_router
from .agent_api import router as agent_router

app = FastAPI(title="AI Academy - RAG & Agents API")

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

app.include_router(rag_router)
app.include_router(agent_router)