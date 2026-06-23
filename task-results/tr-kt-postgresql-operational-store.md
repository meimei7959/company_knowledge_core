---
type: TaskResult
title: PostgreSQL operational store migration result
description: Result for KT-POSTGRESQL-OPERATIONAL-STORE.
timestamp: 2026-06-19T08:12:00Z
resultId: TR-KT-POSTGRESQL-OPERATIONAL-STORE
taskId: KT-POSTGRESQL-OPERATIONAL-STORE
projectId: company-knowledge-core
runnerId: local-codex
executorAgent: agent.company-knowledge-core.executor
status: submitted
summary: Runtime object indexing, retrieval chunks, RAG search, and API object search now use PostgreSQL through DATABASE_URL. SQLite is no longer a normal runtime backend, cache, or fallback.
outputRefs:
  - zhenzhi_knowledge/core.py
  - zhenzhi_knowledge/server.py
  - deploy/lighthouse/docker-compose.yml
  - deploy/lighthouse/.env.example
  - deploy/lighthouse/Dockerfile
  - pyproject.toml
  - tests/test_cli.py
knowledgeRefs: []
sourceMaterialRefs:
  - docs/architecture/core-architecture.md
  - docs/architecture/product-system-architecture.md
  - docs/tools/core-tool-contract.md
evidenceRefs:
  - task-results/tr-kt-postgresql-operational-store.md
  - knowledge/audit/audit.20260619T081200Z.md
testsOrChecks:
  - python3 -m unittest discover -s tests
  - python3 -m py_compile zhenzhi_knowledge/core.py zhenzhi_knowledge/server.py zhenzhi_knowledge/cli.py tests/test_cli.py
  - docker compose -f deploy/lighthouse/docker-compose.yml config --quiet
  - live PostgreSQL smoke: index rebuild/search and rag rebuild/search
  - live PostgreSQL API smoke: /health and /v0/objects
nextActions:
  - Configure production DATABASE_URL with the managed PostgreSQL instance or the Compose postgres service before deployment.
  - Run index rebuild and rag rebuild after production deploy to populate PostgreSQL from the Markdown bundle.
completedAt: 2026-06-19T08:12:00Z
---

## Summary

The runtime database path was migrated from `.zhenzhi/index.sqlite3` to PostgreSQL.

`DATABASE_URL` is now required and must use a PostgreSQL URL scheme. The object metadata index and retrieval chunks are created in PostgreSQL tables. CLI index/RAG commands and API object/RAG search read the same PostgreSQL schema locally and in production.

The Markdown/YAML bundle remains the portable exchange and audit artifact. Rebuild commands import the current bundle into PostgreSQL.

## Evidence

- `zhenzhi_knowledge/core.py` no longer imports `sqlite3` or uses `.zhenzhi/index.sqlite3`.
- `zhenzhi_knowledge/server.py` initializes PostgreSQL schema before API startup.
- `deploy/lighthouse/docker-compose.yml` provisions a `postgres:16-alpine` service and passes `DATABASE_URL` to the API.
- `deploy/lighthouse/.env.example` defines the PostgreSQL connection variables.
- `tests/test_cli.py` rejects missing and non-PostgreSQL `DATABASE_URL` values and no longer expects SQLite file creation.

## Verification

- `python3 -m unittest discover -s tests`: 76 tests passed.
- `python3 -m py_compile zhenzhi_knowledge/core.py zhenzhi_knowledge/server.py zhenzhi_knowledge/cli.py tests/test_cli.py`: passed.
- `docker compose -f deploy/lighthouse/docker-compose.yml config --quiet`: passed.
- Live PostgreSQL CLI smoke: `index rebuild`, `index search`, `rag rebuild`, and `rag search` passed against a temporary `postgres:16-alpine` container; no `.zhenzhi/index.sqlite3` was created.
- Live PostgreSQL API smoke: API server started with PostgreSQL, `/health` returned ok, and `/v0/objects` returned indexed objects.
- Negative API startup smoke: API startup without `DATABASE_URL` failed closed with `DATABASE_URL is required and must point to PostgreSQL`.

## Outputs

- PostgreSQL-only runtime storage path.
- Local/production Docker Compose PostgreSQL service.
- PostgreSQL dependency installed in the container image.
- Regression tests for PostgreSQL-only configuration.

## Next Actions

- Set real production `DATABASE_URL` and `POSTGRES_PASSWORD` outside Git.
- Rebuild indexes after deployment so production PostgreSQL is populated from the repository bundle.
