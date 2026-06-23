---
type: ProjectTask
title: PostgreSQL operational store migration
description: Replace SQLite runtime index/retrieval paths with PostgreSQL for both local development and production.
timestamp: "2026-06-19T08:45:00Z"
taskId: KT-POSTGRESQL-OPERATIONAL-STORE
taskType: architecture_migration
projectId: company-knowledge-core
requester: 梅晓华
assignee: agent.company-knowledge-core.executor
status: done
priority: high
dueAt: ""
sourceMaterialRefs:
  - docs/architecture/core-architecture.md
  - docs/architecture/product-system-architecture.md
  - docs/tools/core-tool-contract.md
expectedOutput:
  - PostgreSQL-backed storage/index/retrieval implementation.
  - Local development PostgreSQL setup.
  - Production Docker Compose PostgreSQL service or external DATABASE_URL support.
  - Migration/export path from existing Markdown bundle and legacy SQLite artifacts.
  - Regression tests proving local and production use the same PostgreSQL schema.
resultRef: task-results/tr-kt-postgresql-operational-store.md
notificationRefs: []
auditRefs:
  - knowledge/audit/audit.20260619T081200Z.md
assignedRunner: ""
leaseOwner: ""
leaseProofHash: ""
leaseExpiresAt: ""
heartbeatAt: ""
taskVersion: 1
completedAt: "2026-06-19T08:12:00Z"
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"architecture_migration","category":"project","stage":"","requiredCapabilities":["architecture_migration"],"requiredTools":[],"sourceRefs":["docs/architecture/core-architecture.md","docs/architecture/product-system-architecture.md","docs/tools/core-tool-contract.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
updatedAt: "2026-06-21T07:18:05Z"
---

# PostgreSQL Operational Store Migration

## Goal

Use PostgreSQL as the only runtime database backend for the central processor in both local development and production.

SQLite must be removed from normal runtime paths. It may exist only as a legacy artifact to migrate away from, not as a local cache, local dev backend, or fallback compatibility path.

## Rationale

Using PostgreSQL online and SQLite locally creates correctness drift:

- identifier and field casing behavior differs;
- JSON behavior differs;
- collation and ordering differ;
- index and constraint semantics differ;
- transaction and locking semantics differ;
- query planner and full-text search behavior differ.

Local development must exercise the same PostgreSQL schema and SQL semantics as production.

## Required Scope

- Introduce `DATABASE_URL` as required runtime config for API and normal CLI commands.
- Add local PostgreSQL development setup, preferably Docker Compose.
- Add production PostgreSQL configuration in `deploy/lighthouse/docker-compose.yml` or support managed PostgreSQL through `DATABASE_URL`.
- Replace `.zhenzhi/index.sqlite3` usage in:
  - object metadata index;
  - retrieval chunks;
  - RAG search;
  - graph/index queries where applicable.
- Keep Markdown/YAML bundle as portable exchange/export/audit artifact.
- Provide explicit import/export or write-through behavior between Markdown bundle and PostgreSQL.
- Fail closed when PostgreSQL is unavailable in production.
- Remove tests that assert SQLite file creation and replace them with PostgreSQL-backed tests.

## Non-Goals

- Do not introduce a graph database in this task.
- Do not make PostgreSQL store plaintext secrets.
- Do not remove Markdown export/audit artifacts.
- Do not redesign the whole product UI.

## Completion Standard

- `python3 -m zhenzhi_knowledge ... index rebuild` writes to PostgreSQL.
- `python3 -m zhenzhi_knowledge ... index search` reads from PostgreSQL.
- `python3 -m zhenzhi_knowledge ... rag rebuild` writes retrieval chunks to PostgreSQL.
- `python3 -m zhenzhi_knowledge ... rag search` reads retrieval chunks from PostgreSQL.
- Feishu knowledge search uses PostgreSQL retrieval state.
- API server starts only when PostgreSQL is configured.
- Local dev setup uses PostgreSQL, not SQLite.
- Production deploy provisions or connects to PostgreSQL.
- No normal test expects `.zhenzhi/index.sqlite3`.

## Test Method

- Unit tests for PostgreSQL object index rebuild/search.
- Unit tests for PostgreSQL retrieval rebuild/search with sourceRefs.
- Integration test using local PostgreSQL service.
- API health test confirms DB connection.
- Feishu search regression test confirms source-bearing answer from PostgreSQL retrieval.
- Migration test imports existing Markdown objects into PostgreSQL.
- Negative test: API startup fails when `DATABASE_URL` is absent in production mode.

## Rollout Plan

1. Add PostgreSQL dependency and connection module.
2. Add schema migration SQL.
3. Add local dev PostgreSQL compose service.
4. Port object index.
5. Port retrieval chunks.
6. Port graph/index reads where needed.
7. Update tests.
8. Deploy with PostgreSQL volume or managed database.
9. Remove SQLite from normal runtime.
