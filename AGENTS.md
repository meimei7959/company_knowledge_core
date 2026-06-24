# Company Knowledge Core Instructions

This project defines Zhenzhi's AI-native central processor: scheduler plus knowledge engineering.

## Current Phase

The OKF-compatible bundle structure, task/source/result templates, Agent Ring protocol contract, core object model, and domain boundary are confirmed.

Current phase: controlled implementation of the Agent Hub intake model, scheduler workflow, Agent Ring integration contract, governance checks, harness checks, and API/Gateway prototype.

## Source Of Truth

Main strategy:

- `docs/strategy/zhenzhi-ai-native-knowledge-system.md`

README, architecture, schemas, tools, memory, harness, and workflows must stay aligned with that document.

## Core Owns

- Project.
- AgentRunner registry record.
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
- Secret values, tokens, keys, or passwords.
- GEO-specific schemas.
- Customer-facing business-domain schemas.
- Hosted-only model assumptions. Local agents must be supported.
- Agent Ring implementation. It is external to this repository.
- Direct execution on distributed computers. This project schedules and records; Agent Ring executes.

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

Assigned task work through Agent Ring must follow:

```txt
Agent Ring registers runner and capabilities
Scheduler assigns or exposes matching task
Agent Ring claims task with lease
Agent Ring prepares context
local Codex / Claude / model / tool executes on the selected computer
Agent Ring writes TaskResult and AgentRun
knowledge review agent gate when knowledge was produced
```

Agent Hub may create tasks, but Scheduler and Agent Ring handle distributed execution.

### Layered Operating Rules

Every formal Agent task must load the short layered rules before work:

- `docs/agent-team/company-agent-constitution.md`
- `docs/agent-team/agent-task-runtime-contract.md`
- `docs/agent-team/human-acceptance-policy.md`
- role rules from `agents/<agent>.md` or `docs/agent-team/role-operating-specs.json`
- project rules from `projects/<project>/project.md` or `projects/<project>/AGENTS.md`

Every `TaskResult` must record `operatingRuleRefs` and pass `commonRulesEvaluation`; otherwise the work is not complete.

## Engineering Iron Rules

- For every problem, first identify the root cause before fixing. Do not patch only the visible symptom.
- If the problem is repeated, workflow-level, integration-related, approval-related, permission-related, identity-related, notification-related, or knowledge-governance-related, apply a systemic fix across the full affected flow.
- A systemic fix must check upstream input, internal data model, generated human-facing output, callback/result handling, audit trail, and user notification where applicable.
- Context-window exhaustion, token budget exhaustion, compaction, resumable sub-agent pause, or temporary tool wait is not task completion or task failure. Record the checkpoint, wait or resume, restore state from durable task/result/audit evidence, and continue until the task is done, explicitly blocked, handed off, rejected, or cancelled by the human owner.
- Human-facing artifacts must be written for the actual human reader. Do not expose raw internal IDs, paths, or status codes as the primary explanation when names, labels, business meaning, or readable summaries can be resolved.
- After fixing, add or update tests at the right level of risk. For workflow, integration, or governance issues, tests must cover the full lifecycle, not only the failing line. If live integration is involved, verify the real external API path before declaring the flow working.

## Safety

- All write tools must create AuditLog.
- verified knowledge requires human review.
- approved tools require Tool Owner approval.
- Agent must not call unregistered tools.
- secret values must not be stored in knowledge files.
- Do not use this repository as a raw file dump.
- Feishu/Lark material intake must register SourceMaterial and create a ProjectTask/KnowledgeTask when processing is needed; it must not directly publish reusable knowledge.
- TaskResult must link to its task, runner, executor Agent, source material, evidence, and outputs.
- Review gates must not block raw material registration, task creation, task result writeback, notifications, or audit records. These are traceable work state, not reusable truth.
- Knowledge must be structured, categorized, sourced, confidence-marked, and reviewable before it becomes reusable.
- Raw documents, screenshots, transcripts, exports, and temporary notes may be registered as SourceMaterial references with safety checks, but they do not become reusable knowledge until summarized into approved object types.
- KnowledgeItem files must live under `knowledge/<category>/`, not directly under `knowledge/`.
- Agent-summarized lessons, pitfalls, incidents, and integration notes may be written automatically as structured `draft` or `observed` knowledge when they include source evidence, scope, confidence, and applicability limits.
- Every knowledge write candidate must pass the Knowledge Review Agent gate before it is indexed for reuse, submitted to human approval, or promoted to a stronger status.
- The Knowledge Review Agent checks structure, category, source evidence, confidence, sensitivity, graph impact, duplicate risk, conflict risk, reviewer-facing readability, and whether the target status/review path is correct.
- The Knowledge Review Agent may reject, request clarification, create ReviewRecord/IssueRecord, and draft the approval document. It must not approve its own output as `verified`, `approved`, `active`, or policy.
- Human approval is required only when knowledge becomes `verified`, changes an existing verified item, creates a policy/workflow/iron rule, or affects permissions, security, customer commitments, or cross-team operating standards.
- Reviewers approve the reusable conclusion, scope, and operational impact. They are not expected to re-read every raw log or reconstruct every debugging step.
- KnowledgeGraphEdge records and GraphSnapshot exports are management/index artifacts, not independent truth. They must be traceable to source objects or evidence, inherit sensitivity from endpoints/evidence, exclude secrets, and remain auditable.
- Agent feedback `skill-gap` creates draft SkillAsset plus Knowledge Engineering review work and must not write directly on `main`. It must run with `--central-root` pointing at a Git repository on `feedback/*` or `codex/*`; blocked runs must fail before any file is written. `system-issue` may write on `main` because it only records Defect intake and PM triage state.
