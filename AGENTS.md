# Agent Rules — CasePilot

## Stack
- Backend: FastAPI (Python 3.11)
- Frontend: Streamlit (hackathon speed; no custom CSS framework)
- Orchestration: LangGraph
- Vector store: ChromaDB, one collection per matter
- Metadata + audit log: SQLite for the demo, Postgres-ready schema
- Integration: MCP mock CMS server (local), adapter interface for real CMS later

## Rules
- Never invent legal deadline rules. All deadline logic lives in
  `app/legal/deadlines.py` with unit tests. If a rule is unclear, stop and ask.
- Every AI answer must return `{answer, citations: [{doc_id, chunk_id, page}]}`.
- Every write action goes through `app/cms/adapter.py` and requires an
  `approved_by` field.
- No real client data, no PII in fixtures.
- Do not modify files outside the current feature scope.
- Run `pytest` before marking a feature complete.
