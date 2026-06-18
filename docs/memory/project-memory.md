# Core Project Memory

## Current Decision

The knowledge engineering system starts as an OKF-compatible Git bundle plus a local connector.

It should solve the current team problem first:

- local Codex / Antigravity agents need shared project context;
- tools and experience must stop living only on personal machines;
- every significant Agent task must read context before work and write updates after work.

## Source Of Truth

The main strategy document is:

- `docs/strategy/zhenzhi-ai-native-knowledge-system.md`

README should point to that document. Other docs must align with it.

## Operating Model

Daily workflow:

```txt
sync pull -> start -> Agent work -> finish -> review -> sync push
```

Agent must use `zhenzhi-knowledge start` before formal work.

Agent must use `zhenzhi-knowledge finish` after formal work.

No Agent task is complete without AgentRun and knowledge update draft.

Reusable tools are ToolAsset records. Reviewed writes and status changes must create AuditLog.

## Engineering Iron Rules

- Every problem requires root-cause analysis before fixing. Do not make a single-point symptom fix without understanding why the problem happened.
- Repeated, workflow-level, integration, approval, permission, identity, callback, notification, and knowledge-governance issues require systemic repair across the whole affected lifecycle: input parsing, identity mapping, stored object, human-facing document, approval/API call, callback handling, audit, and user notification where applicable.
- Human-facing documents are for reviewers and operators. Prefer names, labels, business actions, and concise summaries; keep IDs and paths only as secondary system information.
- Fixes must include tests at the right level of risk. Workflow, integration, and governance fixes must include lifecycle tests and, when relevant, a real integration verification before marking them done.

## Memory Layers

- OKF-compatible Markdown/YAML files: first-stage human/Agent-readable memory.
- Git history: change audit and rollback.
- Local index: fast metadata and full-text retrieval.
- Future vector index: semantic recall, not source of truth.
- Future Knowledge API / Agent Gateway: permissioned access and audit.

## Anti-Goals

- Do not build a large Web platform first.
- Do not use vector search as the only memory layer.
- Do not store secrets, tokens, keys, or passwords.
- Do not let Agent publish verified knowledge without review.
- Do not let any reusable knowledge write bypass the Knowledge Review Agent gate.
- Knowledge Review Agent checks source, structure, category, sensitivity, duplicates, conflicts, reviewer readability, and review path before indexing, approval, or promotion.
- Do not let Agent call unregistered tools.
- Do not embed GEO-specific schema into core.
