"""FastAPI application entrypoint for the RAG & Agents workshop services.

This module creates the FastAPI app, registers routers for the
RAG (retrieval-augmented generation) and language-graph agent APIs,
and exposes a lightweight healthcheck endpoint.

Keep this file minimal: application configuration, middleware and
business logic should live in their respective modules (rag_api,
agent_api, etc.). Routers are included at import-time so their
prefixes and tags control the OpenAPI schema.
"""

from fastapi import FastAPI
from .rag_api import router as rag_router
from .agent_api import router as agent_router

app = FastAPI(title="AI Academy - RAG & Agents API")

@app.get("/healthz")
def healthz():
    """Liveness/health endpoint.

    Returns a simple status dict used by orchestrators or uptime checks.
    Keep this endpoint deterministic and fast — do not perform heavy IO here.
    """
    return {"status": "ok"}

# Include routers after app creation. Order does not affect routing but
# influence the generated OpenAPI ordering. Each router defines its own prefix.
app.include_router(rag_router)
app.include_router(agent_router)