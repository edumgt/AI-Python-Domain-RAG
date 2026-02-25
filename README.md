# Domain RAG MVP

A practical starter project for a domain-specific RAG service using FastAPI, Qdrant, PostgreSQL, Redis, and a vLLM-compatible OpenAI API endpoint.

## Features

- TXT and PDF upload
- Text extraction and cleanup
- Paragraph-based chunking with overlap
- SentenceTransformer embeddings
- Qdrant vector search
- vLLM OpenAI-compatible chat completion integration
- Chat log persistence in PostgreSQL

## Run

```bash
docker compose up --build
```

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs

## Test

### Health
```bash
curl http://localhost:8000/health
```

### Ingest text
```bash
curl -X POST http://localhost:8000/ingest/text \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "doc-001",
    "title": "LLM Domain Guide",
    "content": "Domain-specific LLM systems commonly start with RAG and add fine-tuning later if needed."
  }'
```

### Ingest file
```bash
curl -X POST http://localhost:8000/ingest/file -F "file=@./sample.txt"
```

### Chat
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How is a domain-specific LLM usually built?",
    "top_k": 4
  }'
```
