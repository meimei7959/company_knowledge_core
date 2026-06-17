# Company Knowledge Core Instructions

This project defines Zhenzhi's AI-native knowledge engineering foundation.

## Current Phase

The OKF-compatible bundle structure, templates, connector contract, core object model, and domain boundary are confirmed.

Current phase: controlled implementation of the local connector, memory workflow, governance checks, harness checks, and API/Gateway prototype.

## Source Of Truth

Main strategy:

- `docs/strategy/zhenzhi-ai-native-knowledge-system.md`

README, architecture, schemas, tools, memory, harness, and workflows must stay aligned with that document.

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
- Secret values, tokens, keys, or passwords.
- GEO-specific schemas.
- Customer-facing business-domain schemas.
- Hosted-only model assumptions. Local agents must be supported.

## Agent Workflow Rule

Formal Agent work must follow:

```txt
zhenzhi-knowledge sync pull
zhenzhi-knowledge start
Agent work
zhenzhi-knowledge finish
human review
zhenzhi-knowledge sync push
```

Agent must read the generated context pack before work and must generate AgentRun plus draft updates after work.

## Safety

- All write tools must create AuditLog.
- verified knowledge requires human review.
- approved tools require Tool Owner approval.
- Agent must not call unregistered tools.
- secret values must not be stored in knowledge files.
- Do not use this repository as a raw file dump.
- Knowledge must be structured, categorized, sourced, confidence-marked, and reviewable before it becomes reusable.
- Raw documents, screenshots, transcripts, exports, and temporary notes stay outside the knowledge bundle until summarized into approved object types.
- KnowledgeItem files must live under `knowledge/<category>/`, not directly under `knowledge/`.
