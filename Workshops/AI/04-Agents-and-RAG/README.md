# 1) Ingest
curl -X POST http://localhost:8000/rag/ingest \
  -H "Content-Type: application/json" \
  -d '{"source_dir":"data/policies","reset":true}'

# 2) Search
curl -s http://localhost:8000/rag/search \
  -H "Content-Type: application/json" \
  -d '{"query":"delayed delivery refund","k":3}' | jq

# 3) RAG answer with citations
curl -s http://localhost:8000/rag/query \
  -H "Content-Type: application/json" \
  -d '{"question":"My package arrived 5 days late. Do I get a refund or a voucher?"}' | jq

# 4) Agent (LangGraph)
curl -s http://localhost:8000/agent/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"My package is 5 days late. If policy requires, open a ticket.","thread_id":"class-session"}' | jq
