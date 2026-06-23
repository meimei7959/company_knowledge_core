---
type: ProjectTask
title: Feishu card workflow closure
description: Ensure every Feishu menu and model-routed intent returns a card or reply that drives the next step.
timestamp: "2026-06-18T00:00:00Z"
taskId: KT-FEISHU-CARD-WORKFLOW
taskType: engineering_action
projectId: company-knowledge-core
requester: zhenzhi-central-processor
assignee: zhenzhi-knowledge-core
requiredCapabilities:
  - feishu_cards
  - workflow_design
  - project_creation
  - task_status
requiredAgents:
  - product-agent
  - scheduler-agent
preferredRunner: []
assignedRunner: []
executorAgent: []
leaseOwner: []
leaseExpiresAt: []
status: done
priority: medium
dueAt: []
sourceMaterialRefs:
  - docs/agent-team/deepseek-feishu-routing-plan.md
  - docs/agent-team/agent-hub-product-workflows.md
expectedOutput:
  - card states for create project, capture material, query knowledge, token, tool request, status
  - confirmation cards before durable actions
  - task cards with human-readable names and next actions
  - tests for menu shortcuts and free-text flows
resultRef: task-results/tr-kt-feishu-card-workflow.md
notificationRefs: []
auditRefs: []
completedAt: "2026-06-18T11:29:18Z"
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"engineering_action","category":"engineering","stage":"","requiredCapabilities":["engineering_action","feishu_cards","workflow_design","project_creation","task_status"],"requiredTools":[],"sourceRefs":["docs/agent-team/deepseek-feishu-routing-plan.md","docs/agent-team/agent-hub-product-workflows.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"engineering","acceptancePath":"pm_review","reviewPath":"engineering_test","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
updatedAt: "2026-06-21T07:18:05Z"
---

## Request

Make Feishu interaction productized and closed-loop.

Every entry should either answer, ask one clear clarification, create a reviewable record, or create a task with status and next step. Do not make users remember internal IDs when names can be resolved.

## Definition of Done

- Every current menu shortcut has a corresponding text/card response with purpose, required fields, next action, and safety boundary.
- Create project, capture material, query knowledge, access credential, tool request, status, and review queue flows have confirmation or clarification states.
- Durable actions require confirmation or approval before write, publish, permission, credential, or external side effects.
- Task cards include readable project name, title, requester, status, next step, and task id as secondary reference.
- Group and private chat behavior are consistent with safety rules.

## Test Plan

- Unit tests for all Feishu menu shortcut replies.
- E2E tests for create project card with existing repo and new repo paths.
- E2E tests for knowledge query, material capture, meeting note capture, access credential request, tool request, and status query.
- Snapshot or assertion tests verify user-facing replies do not require raw project IDs when names are available.
- Safety tests verify high-risk card actions do not execute without approval.
- Run `python3 -m zhenzhi_knowledge --root /Users/meimei/Documents/company_knowledge_core validate`.
- Run `python3 -m unittest tests.test_cli`.

## Self-Verification Checklist

- Confirm every menu item in `docs/agent-team/agent-hub-feishu-menu.md` has a tested reply path.
- Confirm cards explain what happens next rather than only listing commands.
- Confirm private-only flows are private-only.
- Confirm no card exposes secret values or unsafe direct action buttons.
