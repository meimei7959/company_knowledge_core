---
type: ProjectTask
title: Company Knowledge Core project initialization
description: Finish initializing the Agent Hub and knowledge engineering central processor project.
timestamp: "2026-06-19T00:00:00Z"
taskId: PROJECT-INIT-COMPANY-KNOWLEDGE-CORE
taskType: project_initialization
projectId: company-knowledge-core
requester: meimei
assignee: agent.company-knowledge-core.project-manager
requiredCapabilities:
  - codex
  - git
  - knowledge_sync
  - project_initialization
  - scheduler_design
requiredAgents:
  - agent.company-knowledge-core.project-manager
  - agent.company-knowledge-core.knowledge-engineering
  - agent.company-knowledge-core.executor
preferredRunner:
  - runner.meimei-mac-codex
assignedRunner:
  - runner.meimei-mac-codex
executorAgent: []
leaseOwner: []
leaseExpiresAt: []
status: done
priority: high
dueAt: []
sourceMaterialRefs:
  - README.md
  - AGENTS.md
  - docs/strategy/zhenzhi-ai-native-knowledge-system.md
  - docs/architecture/central-processor-and-agent-ring.md
  - docs/protocols/agent-workbench-integration-brief.md
expectedOutput:
  - project-level task list with completion standards
  - initialized project docs and indexes
  - central processor follow-up tasks
  - evidence-backed TaskResult for project initialization
resultRef: task-results/tr-project-init-company-knowledge-core.md
notificationRefs:
  - notifications/notification.20260619T015750553994Z.md
auditRefs: []
completedAt: "2026-06-19T01:57:50Z"
updatedAt: "2026-06-21T07:18:05Z"
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"project_initialization","category":"project","stage":"","requiredCapabilities":["project_initialization","codex","git","knowledge_sync","scheduler_design"],"requiredTools":[],"sourceRefs":["README.md","AGENTS.md","docs/strategy/zhenzhi-ai-native-knowledge-system.md","docs/architecture/central-processor-and-agent-ring.md","docs/protocols/agent-workbench-integration-brief.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project_management","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
---

## Request

Complete the current project initialization work for the Agent Hub and knowledge engineering central processor.

The project must become operable as a real project, not only a discussion thread. It must have:

- clear positioning;
- current task list;
- task completion standards;
- project Agent registration intent;
- temporary Runner handoff;
- central processor capability backlog;
- a closeout path for the initialization task.

## Work Breakdown

This task controls the current phase. The child tasks are:

| Task | Purpose | Status |
| --- | --- | --- |
| [TASK-DOC-ENTRY-ALIGNMENT](kt-doc-entry-alignment.md) | Align README, AGENTS, docs index, and project index so newcomers can understand the project. | done |
| [TASK-PROJECT-STATUS-DASHBOARD](kt-project-status-dashboard.md) | Make project status visible from Feishu and the central API. | done |
| [TASK-RUNNER-AGENT-REGISTRY-HARDENING](kt-runner-agent-registry-hardening.md) | Harden temporary Runner and project Agent registration into a stable central model. | done |
| [TASK-TASK-NOTIFICATION-LOOP](kt-task-notification-loop.md) | Notify requester and project context when tasks are created, claimed, blocked, and finished. | done |
| [TASK-KNOWLEDGE-CAPTURE-REVIEW-PIPELINE](kt-knowledge-capture-review-pipeline.md) | Close the meeting/material capture to SourceMaterial, KnowledgeTask, Review, and KnowledgeItem flow. | done |
| [TASK-AGENT-WORKBENCH-CONTRACT-TESTS](kt-agent-workbench-contract-tests.md) | Provide contract tests for the external Agent Workbench team. | done |
| [TASK-DEPLOYMENT-OBSERVABILITY-OPS](kt-deployment-observability-ops.md) | Make deploy, health, logs, DeepSeek, Feishu, and task runtime observable. | done |
| [TASK-PROJECT-INITIALIZATION-CLOSEOUT](kt-project-initialization-closeout.md) | Produce final TaskResult, evidence, risks, and next actions for this initialization phase. | pending |

Completed foundation tasks remain listed in [tasks/index.md](index.md).

## Definition of Done

- Project task list exists and every active task has a clear completion standard.
- Existing completed foundation tasks remain linked and are not duplicated.
- Current project initialization task has a closeout task and evidence path.
- The project index, tasks index, and source-of-truth docs point to the same project direction.
- Agent Workbench integration scope is documented without constraining the workbench product design.
- Central processor follow-up work is broken into testable tasks, not vague themes.
- `python3 -m unittest tests.test_cli` passes after code-affecting changes.
- `python3 -m zhenzhi_knowledge --root /Users/meimei/Documents/company_knowledge_core validate` passes or any remaining validation gap is recorded with reason.

## Test Plan

- Verify all task links in `projects/company-knowledge-core/tasks/index.md`.
- Verify every new task card contains `Definition of Done`, `Test Plan`, and `Self-Verification Checklist`.
- Run unit tests if implementation code changes.
- Run bundle validation before marking initialization done.

## Self-Verification Checklist

- [x] Task list covers current project initialization.
- [x] Task list covers central processor capability follow-up.
- [x] Each task has explicit completion standards.
- [x] Project indexes link to the task list.
- [x] Initialization closeout task exists.
- [x] Evidence and tests are recorded in TaskResult before final closeout.
