# Core Architecture

## Purpose

Company Knowledge Core is the working foundation for Zhenzhi's AI-native team.

It does not start as a large platform. It starts as an OKF-compatible Git knowledge bundle plus a local connector that makes Codex, Antigravity, and other local agents read project context before work and write knowledge updates after work.

## Current Architecture

```txt
OKF-compatible Git Bundle
  Markdown/YAML knowledge files, index.md, log.md

zhenzhi-knowledge Local Connector
  init, register, start, finish, review, sync

Agent Workflow
  context pack before task, AgentRun and draft updates after task

Agent/CLI Intake
  Codex, Claude, Antigravity, cloud Agent, or local Agent pushes content through zhenzhi-knowledge

Knowledge Extraction Agent
  turns Feishu materials or Agent/CLI pushes into structured drafts

Knowledge Review Agent Gate
  structure check, source check, conflict check, sensitivity check, approval document drafting

Local Index
  frontmatter scan, SQLite metadata index, full-text search

Future Online Layer
  Knowledge API, Agent Gateway, auth, policy, audit, RAG
```

## Core Owns

- Project.
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

## Core Does Not Own

- Full source code. Code lives in Git repositories.
- Full project management implementation. Project cards are the temporary source of truth until the product is ready.
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
- Agent registration.
- Project registration.
- ToolAsset registration.
- Agent start/finish workflow.
- Knowledge Review Agent gate.
- Human review and sync workflow.

Do not build first:

- Full Web platform.
- Complex graph database.
- Hosted-only model infrastructure.
- Automatic verified publication.
