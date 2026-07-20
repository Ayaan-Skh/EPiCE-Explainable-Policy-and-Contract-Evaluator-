# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

EPiCE (Explainable Policy & Contract Evaluator) is a RAG system for insurance claim analysis. A natural-language claim query ("46M knee surgery Pune 3 month policy") is parsed into structured fields, matched against policy-document chunks via semantic search, and an LLM produces an explainable approve/reject decision citing specific clauses. Python/FastAPI backend + Next.js frontend.

## Commands

Backend runs from the repo root (imports assume it, e.g. `from src.pipeline import ...`).

```bash
# One-time setup: chunk + embed a policy doc into the vector store
python main.py --setup --reset                 # uses data/raw/insurance_policy.txt
python main.py --setup --document path/to.pdf  # or a specific doc

# CLI usage
python main.py --query "46M knee surgery Pune 3 month policy"
python main.py --batch queries.txt --output results.json
python main.py --status

# API server (localhost:8000, Swagger at /docs)
python -m api.main                             # honors PORT, reloads when ENV=development
uvicorn api.main:app --reload                  # dev alternative

# Frontend (localhost:3000)
cd frontend && npm install && npm run dev
npm run build && npm run lint

# Docker (both services)
docker compose up --build -d
```

Dependencies: `pip install -r requirements.txt` (Python 3.11/3.12). `python-magic` needs libmagic — the Dockerfile installs `libmagic1`; on **Windows** install `python-magic-bin` instead.

## Testing reality

There is no configured test runner (no pytest.ini/pyproject/conftest, no test functions). The README's `pytest tests/ -v` does **not** work as written. `tests/test_document_processor.py` is a manual script of top-level code with hardcoded relative paths (`../data/...`) — run it from inside `tests/`, not from the repo root. `src/test_groq.py` is a similar throwaway probe. Treat these as scratch scripts, not a suite.

## Architecture

**Pipeline orchestration** ([src/pipeline.py](src/pipeline.py)) — `InsuranceQAPipeline` wires the four ML components and owns two flows:
- `setup()`: load doc → chunk → validate → create ChromaDB collection → embed + store.
- `process_query()`: parse → semantic search (top_k) → LLM decision → assemble structured result dict.

The four components it composes:
- [src/document_processor.py](src/document_processor.py) — `DocumentProcessor`: TXT/PDF/DOCX parsing (magic-byte detection + extension fallback), section extraction, `RecursiveCharacterTextSplitter` chunking (500/50).
- [src/embeddings.py](src/embeddings.py) — `EmbeddingsManager`: `all-MiniLM-L6-v2` SentenceTransformer (384-dim) + a persistent ChromaDB client. Embeddings are supplied manually (`embedding_function=None`); search returns documents/metadatas/distances/ids.
- [src/query_parser.py](src/query_parser.py) — `Query_parser`: regex + rapidfuzz extraction into the `ParseQuery` Pydantic model (age, gender, procedure, location, policy_duration_months, is_emergency). Known locations/procedures are hardcoded lists/dicts.
- [src/decision_engine.py](src/decision_engine.py) — `DecisionEngine`: builds a strict prompt, calls the LLM, and parses the reply into the `Decision` Pydantic model. Has a JSON-extraction fallback (`_parse_llm_response` → `_fallback_parse`) and never raises on failure — it returns a conservative rejected `Decision` instead.

**API layer** ([api/](api/)) — `api/main.py` builds the FastAPI app (CORS + lifespan); all routes live in [api/routes.py](api/routes.py) under the `/api` prefix. The pipeline is a lazily-initialized module-level **singleton** (`get_pipeline()`); it tries to load an existing vector store on first init and sets `is_setup` accordingly. Pydantic request/response models are in [api/models.py](api/models.py). [api/history_cache.py](api/history_cache.py) adds an in-memory response cache (5-min TTL) and JSON-file query history — additive, wrapping the pipeline, not part of core logic. [api/pdf_export.py](api/pdf_export.py) renders results to PDF via reportlab.

**Frontend** ([frontend/](frontend/)) — Next.js **16** App Router (React 19, Tailwind v4). Route pages live in `frontend/app/` (`page`, `query`, `upload`, `batch`, `analytics`); shared components and the API client live in `frontend/src/` (`src/lib/api.ts` is the typed client). Note the split: routes in `app/`, everything else in `src/`.

## Non-obvious facts / gotchas

- **Vector store location is hardcoded.** `InsuranceQAPipeline` passes `persist_directory="policy_documents"`, so the ChromaDB store persists to `./policy_documents/` at the repo root (collection name also `"policy_documents"`) — *not* `models/vector_store`. The README's `VECTOR_DB_PATH` and `EMBEDDING_MODEL` env vars are **not read anywhere**; path and model are hardcoded.
- **Default LLM model is `llama-3.1-8b-instant`**, not the 70b model the README advertises. The provider is chosen at *import time* from `LLM_PROVIDER` (groq/ollama/openai); groq requires `GROQ_API_KEY`.
- **Queries need setup first.** `POST /api/query` returns 503 until a policy document has been processed (via `--setup`, `/api/upload-file`, or `/api/upload`). The store must physically exist in `policy_documents/`.
- **First request is slow** — the SentenceTransformer model loads on first pipeline init (singleton), and on Render's free tier the service also cold-starts.
- **Two upload endpoints:** `/api/upload-file` handles real uploads (PDF/DOCX/TXT, 10 MB cap, saved to `data/raw/uploads/`); `/api/upload` is a placeholder that just re-processes the bundled `data/raw/insurance_policy.txt`.
- **Env config:** backend `.env` (`GROQ_API_KEY`, `LLM_PROVIDER`, `LLM_MODEL`, `CORS_ORIGINS` comma-separated); frontend `NEXT_PUBLIC_API_URL` — `src/lib/api.ts` auto-appends `/api` if absent. `NEXT_PUBLIC_*` is inlined at **build time**, so for Docker it's a build ARG in `frontend/Dockerfile` (passed via `docker-compose.yml`), not a runtime env var. Deploy target is Render (API) + Vercel (frontend); see [DEPLOYMENT.md](DEPLOYMENT.md).
- **Logging** writes timestamped files under `logs/` in the current working directory ([src/logger.py](src/logger.py)); errors across `src/` are wrapped in `CustomException` ([src/exception.py](src/exception.py)).
