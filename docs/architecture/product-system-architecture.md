# Product System Architecture

## Positioning

Company Knowledge Core is the central processor for Zhenzhi's AI-native operating system.

It is not only a knowledge base. It is the product backend for:

- project initialization;
- task orchestration;
- distributed Agent execution;
- structured knowledge synchronization;
- review, audit, and notification;
- project portability across computers.

The system must let any eligible Agent Ring runner continue a project without losing context.

## Product Layers

```txt
Agent Hub / API / CLI
  user and Agent entrypoints

Central Scheduler
  task creation, matching, lease, heartbeat, retry, reassignment

Knowledge Core
  project memory, source material, structured knowledge, decisions, task results

Governance
  review, policy, approval, audit, conflict handling, notification

Protocol Layer
  Agent Ring protocol, context sync protocol, future external integrations

External Agent Ring
  workstation/connector on distributed computers; not implemented here

Distributed Computers
  local Codex, Claude, local models, tools, repositories, browser automation
```

## Core Product Flows

### Project Creation

```txt
Agent Hub receives project request
-> central processor creates Project
-> scheduler creates initialization tasks
-> repository and environment requirements are recorded
-> Agent team and Agent Ring runner requirements are recorded
-> project channel / notifications are linked
```

Project creation is not only a knowledge record. It is the start of a real project workspace and task graph.

### Knowledge Intake

```txt
message / meeting note / file / URL
-> SourceMaterial
-> KnowledgeTask
-> scheduler assigns Agent Ring runner
-> runner extracts, summarizes, and structures with evidence
-> TaskResult + KnowledgeItem draft
-> review gate
-> reusable knowledge
```

Raw material is preserved as source evidence. Summaries must cite the source.

### Distributed Execution

```txt
ProjectTask / KnowledgeTask
-> scheduler matches runner by capability, permission, data scope, load
-> runner claims with lease
-> runner pulls project/task context bundle
-> local Agent executes
-> runner writes TaskResult, AgentRun, artifacts, handoff note
```

The central processor records state. Agent Ring executes outside this repository.

### Project Portability

```txt
computer A works
-> writes structured result and handoff
-> central processor updates project memory
-> computer B pulls ProjectContextBundle
-> computer B continues
```

Portability depends on structured synchronization, not chat history.

## System Modules

| Module | Responsibility | Current Form | Future Form |
| --- | --- | --- | --- |
| Agent Hub | Feishu bot and menu entrypoint | bot handlers and product docs | multi-channel Agent entrance |
| Scheduler | task routing and runner assignment | task records, protocol docs, CLI states | PostgreSQL-backed service + queue + policy engine |
| Knowledge Core | structured project memory | OKF-compatible Markdown bundle | PostgreSQL + search + knowledge graph |
| Protocols | external system contracts | docs under `docs/protocols/` | versioned API contracts |
| Runner Registry | distributed computer state | `runners/` records | PostgreSQL online runner registry |
| Task Store | work queue and lifecycle | `tasks/`, project tasks | PostgreSQL durable task service |
| Source Store | raw material metadata | `sources/`, project sources | object storage + PostgreSQL metadata DB |
| Result Store | execution outputs | `task-results/`, AgentRun | PostgreSQL result API + artifact store |
| Review Gate | quality and governance | workflow docs, review rules | review service + approval integration |
| Audit | traceability | AuditLog objects | append-only audit stream |

## Directory Responsibilities

```txt
docs/strategy/      product and strategy source of truth
docs/architecture/  product, core, and integration architecture
docs/protocols/     contracts for Agent Ring and context sync
docs/scheduler/     dispatch model and task routing rules
docs/schemas/       object model and frontmatter contracts
docs/workflows/     lifecycle rules
docs/guides/        human-facing usage guides
agents/             registered Agent identities and roles
runners/            central records for external Agent Ring runners
projects/           project memory and project-scoped tasks/sources
tasks/              central task queue records
sources/            central source material records
task-results/       central result writeback records
knowledge/          reviewed or reviewable reusable knowledge
templates/          object creation templates
zhenzhi_knowledge/  first-stage CLI/API implementation
tests/              harness and regression checks
```

## Non-Negotiable Invariants

- Central processor is the source of truth for project state.
- Production and local development use PostgreSQL. SQLite is not an accepted runtime backend.
- Agent Ring implementation stays external.
- Distributed computers are replaceable execution nodes.
- Raw material becomes SourceMaterial before reusable knowledge.
- Task execution writes TaskResult and AgentRun before notification or review.
- KnowledgeItem must cite evidence and confidence.
- Secrets are references only, never plain values.
- Existing object fields must be preserved; unknown fields should not be dropped.
- New capabilities must add templates, docs, validation, and tests at the right risk level.

## Evolution Path

1. Keep current OKF-compatible bundle as the source of truth.
2. Add PostgreSQL as the operational store for both local development and production.
3. Add stronger object schemas and validation without breaking existing Markdown records.
3. Add scheduler service while preserving task files as portable records.
4. Add Agent Ring API integration around the documented protocol.
5. Move hot state to database/API when needed, keeping export back to the bundle.
6. Add project management UI on top of the same Project / Task / Source / Result model.

The architecture should grow by adding modules around stable contracts, not by replacing the existing knowledge bundle.
