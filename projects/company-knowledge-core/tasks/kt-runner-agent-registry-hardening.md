---
type: ProjectTask
title: Runner and project Agent registry hardening
description: Make temporary Runner and project Agent registration safe, searchable, and ready for Agent Workbench integration.
timestamp: "2026-06-19T00:00:00Z"
taskId: TASK-RUNNER-AGENT-REGISTRY-HARDENING
taskType: engineering_action
projectId: company-knowledge-core
requester: meimei
assignee: agent.company-knowledge-core.executor
requiredCapabilities:
  - runner_registry
  - agent_registry
  - scheduler_api
requiredAgents:
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
  - zhenzhi_knowledge/core.py
  - zhenzhi_knowledge/cli.py
  - docs/protocols/agent-workbench-integration-brief.md
expectedOutput:
  - stable Runner registration API behavior
  - project Agent registration flow
  - duplicate-safe upsert and audit
resultRef: task-results/tr-task-runner-agent-registry-hardening.md
notificationRefs: []
auditRefs: []
completedAt: "2026-06-19T01:18:51Z"
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"engineering_action","category":"engineering","stage":"","requiredCapabilities":["engineering_action","runner_registry","agent_registry","scheduler_api"],"requiredTools":[],"sourceRefs":["zhenzhi_knowledge/core.py","zhenzhi_knowledge/cli.py","docs/protocols/agent-workbench-integration-brief.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"engineering","acceptancePath":"pm_review","reviewPath":"engineering_test","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
updatedAt: "2026-06-21T07:18:05Z"
---

## Request

Turn the temporary Runner and project Agent registration into a reliable central registry.

## Definition of Done

- Runner registration validates required fields and normalizes IDs.
- Runner upsert preserves stable identity and updates capability, project, repo, and data scope metadata.
- Project Agent registration can attach Agents to projects without duplicate links.
- CLI and HTTP API produce consistent records.
- Audit logs are created for register, upsert, attach project, and heartbeat.
- Tests cover register, upsert, heartbeat, project Agent attach, and duplicate prevention.

## Test Plan

- Unit test CLI `runner register` and `runner heartbeat`.
- HTTP lifecycle test for register, upsert, heartbeat.
- Test project Agent attach writes both Agent `allowedProjects` and Project `relatedAgents`.
- Run `python3 -m unittest tests.test_cli`.

## Self-Verification Checklist

- [x] Duplicate registration is safe.
- [x] Audit exists.
- [x] Project and Agent records are mutually linked.
- [x] Tests prove CLI and HTTP consistency.
