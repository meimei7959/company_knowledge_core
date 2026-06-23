---
type: ProjectTask
title: Production closed-loop acceptance
description: Verify the real Feishu -> central processor -> task -> runner/manual handoff -> result -> notification loop in production-like conditions.
timestamp: "2026-06-19T02:10:00Z"
taskId: TASK-PRODUCTION-CLOSED-LOOP-ACCEPTANCE
taskType: product_acceptance
projectId: company-knowledge-core
requester: meimei
assignee: agent.company-knowledge-core.project-manager
requiredCapabilities:
  - feishu
  - deployment
  - task_lifecycle
  - observability
requiredAgents:
  - agent.company-knowledge-core.project-manager
  - agent.company-knowledge-core.executor
preferredRunner:
  - runner.meimei-mac-codex
assignedRunner: []
executorAgent: []
leaseOwner: []
leaseExpiresAt: []
status: done
priority: high
dueAt: []
sourceMaterialRefs:
  - docs/ops/central-processor-ops-runbook.md
  - docs/agent-team/agent-hub-product-workflows.md
  - docs/protocols/agent-workbench-integration-brief.md
expectedOutput:
  - production acceptance checklist
  - verified Feishu event callback
  - verified Feishu card callback
  - verified project creation and task initialization
  - verified task status and notification loop
resultRef: task-results/tr-task-production-closed-loop-acceptance.md
notificationRefs:
  - notifications/notification.20260619T025703896205Z.md
auditRefs: []
completedAt: "2026-06-19T02:57:03Z"
updatedAt: "2026-06-21T07:18:05Z"
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"product_acceptance","category":"project","stage":"","requiredCapabilities":["product_acceptance","feishu","deployment","task_lifecycle","observability"],"requiredTools":[],"sourceRefs":["docs/ops/central-processor-ops-runbook.md","docs/agent-team/agent-hub-product-workflows.md","docs/protocols/agent-workbench-integration-brief.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
---

## Goal

Make the central processor usable from the real Feishu entrance, not only from local tests.

The user should be able to create or query a project from Feishu, see readable cards and replies, let the central processor create tasks, see blocked/waiting_runner states when Agent Ring is not ready, and receive a final notification when a task result is written back.

## Scope

Included:

- Feishu event callback.
- Feishu card callback.
- DeepSeek routing fallback behavior.
- Project creation flow.
- Project initialization task creation.
- Manual Runner handoff when Agent Ring is unavailable.
- Task finish and requester notification.
- Health and log checks.

Excluded:

- Full Agent Workbench implementation.
- Real distributed Agent Ring execution.
- Product UI outside Feishu.

## Definition of Done

- `/knowledge-api/health` returns `ok: true` in the target environment.
- Feishu text message callback reaches the server and creates searchable audit evidence.
- Feishu interactive card callback reaches the server and either completes or writes a readable failure audit.
- "创建项目" can produce a project draft, project initialization task, and approval or next-action record.
- If Agent Ring is disabled or no Runner matches, the task is marked `waiting_runner` with a readable next action.
- A local or temporary Runner/manual flow can finish the task and create a `TaskResult`.
- Requester notification is written and, when Feishu send is enabled, delivered or auditable as failed.
- Known card failure classes such as callback misconfiguration or stale card action are documented with audit/log paths.
- No secret value is written into docs, task files, audit body, or screenshots.

## Test Plan

- Run `python3 -m zhenzhi_knowledge --root /Users/meimei/Documents/company_knowledge_core validate`.
- Run `python3 -m unittest tests.test_cli`.
- Use Feishu private chat to send `新手引导`, `创建项目`, `查知识`, and `记录知识`.
- Submit at least one interactive project creation card.
- Check `knowledge/audit/`, `.zhenzhi/feishu-card-events/`, `.zhenzhi/feishu-card-jobs/`, `notifications/`, and `task-results/`.
- Verify `/knowledge-api/health` after deployment.
- Record actual message IDs, task IDs, result refs, and remaining issues in the TaskResult.

## Self-Verification Checklist

- [ ] Feishu message callback verified.
- [ ] Feishu card callback verified.
- [ ] Project creation flow verified.
- [ ] Manual Runner fallback verified.
- [ ] TaskResult and notification verified.
- [ ] Health and logs checked.
- [ ] No secrets stored.
