# Core Architecture

## Purpose

Company Knowledge Core is the central processor for Zhenzhi's AI-native team: scheduler plus knowledge engineering.

It does not start as a large platform. It starts as an Agent Hub intake service, an OKF-compatible Git knowledge bundle, scheduler state, and protocol contracts that allow external Agent Ring workstations to connect distributed computers.

## Current Architecture

```txt
Agent Hub Intake
  Feishu bot intent routing, project creation, material intake, task dispatch, status notification

Central Scheduler
  task matching, runner selection, lease, heartbeat, retry, status transition

OKF-compatible Git Bundle
  Markdown/YAML project, task, source, runner, result, knowledge, index.md, log.md files

zhenzhi-knowledge Local Connector
  init, register, task pull/start/finish/status, start, finish, review, sync

Project / Task Coordination
  Project cards, ProjectTask / KnowledgeTask cards, requester, required capabilities, runner assignment, status, result, notifications

Agent Ring Integration
  external runner registration, capability reporting, task claim, heartbeat, TaskResult writeback

Agent/CLI Intake
  Codex, Claude, Antigravity, cloud Agent, or local Agent pushes content through zhenzhi-knowledge

Material Intake
  Feishu URL/file/video/article/package or CLI push becomes SourceMaterial with sourceRef/storageRef/contentHash

Material Processing
  server performs light recognition; heavy parsing, summarizing, and structuring are assigned to external Agent Ring runners

TaskResult Writeback
  Agent Ring writes summary, runner id, executor Agent, output refs, evidence refs, KnowledgeItem drafts, and next actions

Knowledge Engineering Agent review sub-agent Gate
  structure check, source check, license check, conflict check, sensitivity check, approval document drafting

PostgreSQL Database
  stores central objects, task queue, runner registry, notifications, audit metadata, retrieval chunks, graph edges, leases, heartbeats, and Feishu idempotency state

Knowledge Graph Management
  parseable object references, materialized KnowledgeGraphEdge records, impact analysis, stale propagation, GraphSnapshot export

Future Online Layer
  Knowledge API, Agent Gateway, auth, policy, audit, RAG, project management UI
```

## Core Owns

- Project.
- AgentRunner.
- ProjectTask / KnowledgeTask.
- TaskResult.
- NotificationRecord.
- Agent.
- ToolAsset.
- SourceMaterial.
- KnowledgeItem.
- AgentRun.
- Decision.
- Policy.
- ConflictRecord.
- EvalCase / EvalRun.
- MetricsReport.
- AuditLog.
- KnowledgeGraphEdge.
- GraphSnapshot.

## Core Does Not Own

- Full source code. Code lives in Git repositories.
- Full project management product UI. Project and task cards are the temporary source of truth until the product is ready.
- Agent Ring implementation. It is an external workstation/connector project.
- Direct execution on distributed computers. This project schedules, records, reviews, and audits; Agent Ring executes.
- Secret values, tokens, keys, or credentials.
- GEO-specific schemas.
- Customer-facing business-domain schemas.

## Boundary Rule

```txt
business domains -> knowledge core references
knowledge core -/-> business-domain implementation
```

Core may store references, summaries, decisions, and lessons from domain work. Core must not embed domain-specific object models as its own schema.

## First Implementation Boundary

First build:

- OKF-compatible directory and templates.
- `zhenzhi-knowledge` local connector.
- Project/task/source/result directory structure.
- AgentRunner registry structure and Agent Ring protocol docs.
- ProjectTask / KnowledgeTask creation and status workflow.
- Agent registration.
- Project registration.
- ToolAsset registration.
- SourceMaterial registration workflow.
- TaskResult writeback workflow.
- Agent start/finish workflow.
- Knowledge Engineering Agent review sub-agent gate.
- KnowledgeGraphEdge extraction from existing object references.
- Impact analysis before stale marking, verified publication, approved tool changes, and policy changes.
- Human review and sync workflow.
- PostgreSQL storage backend for the online central processor.

Do not build first:

- Full Web platform.
- Complex graph database.
- Standalone graph source of truth.
- Hosted-only model infrastructure.
- Agent Ring desktop/service runtime.
- Central bot execution for every engineering task.
- Automatic verified publication.

## Database Boundary

PostgreSQL is the required database for the central processor in production and local development.

SQLite must not be used as the production database, local development database, task queue, runner registry, retrieval index, audit/query store, or compatibility cache. The current SQLite implementation is a migration target only and should be removed from the runtime path.

The reason is correctness, not just scale: PostgreSQL and SQLite differ in identifier casing, JSON behavior, collations, indexes, constraints, transactions, locking, and query semantics. Local development must exercise the same PostgreSQL schema and SQL semantics as production.

The OKF-compatible Markdown bundle remains the portable exchange, review, and audit artifact format. PostgreSQL is the operational store. Markdown and PostgreSQL must stay synchronized through explicit import/export or write-through paths, not through hidden local cache behavior.

PostgreSQL owns these tables or equivalent relational records:

- objects and frontmatter metadata;
- projects, agents, runners, tasks, source materials, task results, notifications, audits;
- retrieval chunks and source references;
- knowledge graph edges and graph snapshots;
- leases, heartbeats, idempotency keys, and Feishu event state.

Local developer setup must run PostgreSQL, for example through Docker Compose, and use `DATABASE_URL`. `.zhenzhi/*.sqlite3` files are legacy artifacts and must not be required for normal commands after migration.
