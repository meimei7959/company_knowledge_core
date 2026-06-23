# Core Project Memory

## Current Decision

The system starts as an Agent Hub intake service, an OKF-compatible Git bundle, a central scheduler, and Agent Ring protocol contracts.

It should solve the current team problem first:

- employees need one entrance for project creation, source-material intake, knowledge search, tool requests, and status tracking;
- projects need task cards so work is scheduled to distributed Agent Ring runners instead of disappearing in chat;
- distributed computers need to register their Agents, tools, models, repo access, data scopes, load, and heartbeat;
- local Codex / Antigravity / Claude / model Agents need shared project context;
- tools and experience must stop living only on personal machines;
- useful external learning materials must become structured Agent-readable notes instead of scattered links and files;
- every significant local Agent or project-owner task must read context before work and write task results after work.

## Source Of Truth

The main strategy document is:

- `docs/strategy/zhenzhi-ai-native-knowledge-system.md`

README should point to that document. Other docs must align with it.

## Operating Model

Daily workflow for formal Agent work:

```txt
sync pull -> start -> Agent work -> finish -> review -> sync push
```

Agent must use `zhenzhi-knowledge start` before formal work.

Agent must use `zhenzhi-knowledge finish` after formal work.

No Agent task is complete without AgentRun and knowledge update draft.

Task workflow for Feishu intake or assigned work:

```txt
submitter sends material/request -> Agent Hub registers SourceMaterial -> creates ProjectTask/KnowledgeTask -> Scheduler matches Agent Ring Runner -> Runner claims task -> local Codex/Claude/model/tool work -> Runner writes TaskResult -> review/notification
```

Knowledge ingest closed loop:

```txt
SourceMaterial -> KnowledgeTask -> TaskResult -> qualityEvaluation -> ReviewTask -> ReviewOutcome -> indexed / approval_required / changes_requested / clarification_required / conflict_resolution / rejected -> notification
```

Agent Hub is an entrance. The central processor schedules and records. Agent Ring is the external workstation/connector that executes on distributed computers.

Reusable tools are ToolAsset records. Reviewed writes and status changes must create AuditLog.

## Engineering Iron Rules

- Every problem requires root-cause analysis before fixing. Do not make a single-point symptom fix without understanding why the problem happened.
- Repeated, workflow-level, integration, approval, permission, identity, callback, notification, and knowledge-governance issues require systemic repair across the whole affected lifecycle: input parsing, identity mapping, stored object, human-facing document, approval/API call, callback handling, audit, and user notification where applicable.
- Human-facing documents are for reviewers and operators. Prefer names, labels, business actions, and concise summaries; keep IDs and paths only as secondary system information.
- Fixes must include tests at the right level of risk. Workflow, integration, and governance fixes must include lifecycle tests and, when relevant, a real integration verification before marking them done.
- A workflow is not complete when it merely creates the next task. It is complete only when every state has a next hop, failed Agent output is evaluated and retried or repaired, successful output reaches a terminal published/approved/rejected/clarification state, and the requester is notified.
- For future Agent teams, especially the development team Agents, define the terminal product outcome before implementation. Then build orchestration, evaluation, retry, escalation, notification, audit, and end-to-end tests around that outcome.

## Memory Layers

- OKF-compatible Markdown/YAML files: first-stage human/Agent-readable memory.
- Git history: change audit and rollback.
- Task cards and TaskResult files: first-stage project coordination memory.
- AgentRunner records: first-stage distributed execution registry.
- Local index: fast metadata and full-text retrieval.
- Future vector index: semantic recall, not source of truth.
- Future Knowledge API / Agent Gateway: permissioned access and audit.

## Anti-Goals

- Do not build a large Web platform first.
- Do not use vector search as the only memory layer.
- Do not make the Feishu bot the executor of all engineering tasks.
- Do not implement Agent Ring inside this repository; define protocol and central records here, leave runtime implementation to the Agent Ring project.
- Do not store secrets, tokens, keys, or passwords.
- Do not treat raw articles, videos, screenshots, transcripts, packages, binaries, model files, or datasets as reusable knowledge. Store references and hashes, then extract structured notes.
- Do not let Agent publish verified knowledge without review.
- Do not let any reusable knowledge write bypass the Knowledge Engineering Agent review sub-agent gate.
- Knowledge Engineering Agent review sub-agent checks source, structure, category, sensitivity, duplicates, conflicts, reviewer readability, and review path before indexing, approval, or promotion.
- Do not let Agent call unregistered tools.
- Do not embed GEO-specific schema into core.
