---
type: ProjectTask
title: Deployment and observability operations
description: Make the central processor deployable and observable for Feishu, DeepSeek, Runner, and task lifecycle issues.
timestamp: "2026-06-19T00:00:00Z"
taskId: TASK-DEPLOYMENT-OBSERVABILITY-OPS
taskType: engineering_action
projectId: company-knowledge-core
requester: meimei
assignee: agent.company-knowledge-core.executor
requiredCapabilities:
  - deployment
  - observability
  - feishu
  - deepseek
requiredAgents:
  - agent.company-knowledge-core.executor
preferredRunner:
  - runner.meimei-mac-codex
assignedRunner: []
executorAgent: []
leaseOwner: []
leaseExpiresAt: []
status: done
priority: medium
dueAt: []
sourceMaterialRefs:
  - deploy/lighthouse/deploy.sh
  - deploy/lighthouse/docker-compose.yml
  - docs/guides/team-usage-guide.md
expectedOutput:
  - deploy checklist
  - health and log inspection runbook
  - Feishu callback/card error diagnostics
  - DeepSeek routing metrics and eval status
resultRef: task-results/tr-task-deployment-observability-ops.md
notificationRefs:
  - notifications/notification.20260619T015434242186Z.md
auditRefs: []
completedAt: "2026-06-19T01:54:34Z"
updatedAt: "2026-06-21T07:18:05Z"
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"engineering_action","category":"engineering","stage":"","requiredCapabilities":["engineering_action","deployment","observability","feishu","deepseek"],"requiredTools":[],"sourceRefs":["deploy/lighthouse/deploy.sh","deploy/lighthouse/docker-compose.yml","docs/guides/team-usage-guide.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"engineering","acceptancePath":"pm_review","reviewPath":"engineering_test","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
---

## Request

Make operations boring enough that Feishu and Runner incidents can be diagnosed quickly.

## Definition of Done

- Deploy command and expected health check are documented.
- Server-side log inspection path is documented.
- Feishu card callback/card send errors have audit and runbook entries.
- DeepSeek API configuration is documented by environment variable names only, not secret values.
- Health endpoint covers bundle validation problems.
- Tests or manual verification prove deploy, health, and error logging paths.

## Test Plan

- Run local unit tests.
- Run deployment script when code changes require deploy.
- Verify `/knowledge-api/health` after deployment.
- Verify one known Feishu callback failure mode has searchable audit evidence.

## Self-Verification Checklist

- [x] Deploy path documented.
- [x] Health path documented.
- [x] Log path documented.
- [x] No secret value stored.
- [x] Feishu/DeepSeek diagnostics searchable.
