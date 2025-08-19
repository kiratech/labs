# AI Academy - Agents & RAG (Step 1)

Questo step crea l'app FastAPI con:
- Endpoint `/rag/ingest` per indicizzare i documenti markdown in `data/policies/` (Chroma + sentence-transformers)
- Endpoint `/rag/search` per recupero top-k (senza generazione LLM)

## Setup
```bash
cd ai-academy-agents-rag
python -m venv .venv && source .venv/bin/activate   # oppure conda/mamba
pip install -r requirements.txt
cp .env.example .env
uvicorn src.lab_service.app:app --reload
```

## Prova
1) Ingestione
```bash
curl -X POST http://localhost:8000/rag/ingest -H "Content-Type: application/json" -d '{"reset": true}'
```

2) Ricerca
```bash
curl -s http://localhost:8000/rag/search -H "Content-Type: application/json"   -d '{"query":"ritardo spedizione rimborso", "k": 3}' | jq
```
