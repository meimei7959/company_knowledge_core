---
type: ProjectTask
title: Project status dashboard and Feishu project detail card
description: Make project, Agent, Runner, task, approval, and initialization status visible without requiring raw IDs.
timestamp: "2026-06-19T00:00:00Z"
taskId: TASK-PROJECT-STATUS-DASHBOARD
taskType: engineering_action
projectId: company-knowledge-core
requester: meimei
assignee: agent.company-knowledge-core.project-manager
requiredCapabilities:
  - feishu_cards
  - scheduler_api
  - project_status
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
  - zhenzhi_knowledge/feishu.py
  - zhenzhi_knowledge/server.py
expectedOutput:
  - project status API or renderer
  - Feishu card for project details
  - task status shown by project name, not raw project ID
resultRef: task-results/tr-task-project-status-dashboard.md
notificationRefs: []
auditRefs: []
completedAt: "2026-06-19T01:13:22Z"
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"engineering_action","category":"engineering","stage":"","requiredCapabilities":["engineering_action","feishu_cards","scheduler_api","project_status"],"requiredTools":[],"sourceRefs":["zhenzhi_knowledge/feishu.py","zhenzhi_knowledge/server.py"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"engineering","acceptancePath":"pm_review","reviewPath":"engineering_test","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
updatedAt: "2026-06-21T07:18:05Z"
---

## Request

Users should be able to ask about a project by name and see a readable project status card.

## Definition of Done

- Project lookup accepts project name or alias, not only project ID.
- Project status includes Project, Owner, project Agents, default Runner, current tasks, approvals, and latest TaskResult.
- Feishu card displays readable labels and next actions.
- Missing project, duplicate name, and no Runner cases produce helpful clarification.
- Existing text fallback still works if card sending fails.
- Tests cover name lookup, card render, fallback, and missing project cases.

## Test Plan

- Unit test project name resolution.
- Unit test Feishu project status card payload.
- Simulate project without Runner and project with `waiting_runner` task.
- Run `python3 -m unittest tests.test_cli`.

## Self-Verification Checklist

- [x] Users do not need to know raw project ID.
- [x] Card has next action.
- [x] Fallback text has the same business meaning.
- [x] Tests cover success and failure paths.
