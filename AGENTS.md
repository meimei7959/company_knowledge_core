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

## Engineering Iron Rules

- For every problem, first identify the root cause before fixing. Do not patch only the visible symptom.
- If the problem is repeated, workflow-level, integration-related, approval-related, permission-related, identity-related, notification-related, or knowledge-governance-related, apply a systemic fix across the full affected flow.
- A systemic fix must check upstream input, internal data model, generated human-facing output, callback/result handling, audit trail, and user notification where applicable.
- Human-facing artifacts must be written for the actual human reader. Do not expose raw internal IDs, paths, or status codes as the primary explanation when names, labels, business meaning, or readable summaries can be resolved.
- After fixing, add or update tests at the right level of risk. For workflow, integration, or governance issues, tests must cover the full lifecycle, not only the failing line. If live integration is involved, verify the real external API path before declaring the flow working.

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
