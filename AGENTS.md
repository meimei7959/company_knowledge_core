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
knowledge review agent gate
human review when required
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
- Agent-summarized lessons, pitfalls, incidents, and integration notes may be written automatically as structured `draft` or `observed` knowledge when they include source evidence, scope, confidence, and applicability limits.
- Every knowledge write candidate must pass the Knowledge Review Agent gate before it is indexed for reuse, submitted to human approval, or promoted to a stronger status.
- The Knowledge Review Agent checks structure, category, source evidence, confidence, sensitivity, duplicate risk, conflict risk, reviewer-facing readability, and whether the target status/review path is correct.
- The Knowledge Review Agent may reject, request clarification, create ReviewRecord/IssueRecord, and draft the approval document. It must not approve its own output as `verified`, `approved`, `active`, or policy.
- Human approval is required only when knowledge becomes `verified`, changes an existing verified item, creates a policy/workflow/iron rule, or affects permissions, security, customer commitments, or cross-team operating standards.
- Reviewers approve the reusable conclusion, scope, and operational impact. They are not expected to re-read every raw log or reconstruct every debugging step.
