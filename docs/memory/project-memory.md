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
- Do not let Agent call unregistered tools.
- Do not embed GEO-specific schema into core.
