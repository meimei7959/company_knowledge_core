---
type: ProjectTask
title: Mature AI Native OS digital worker and capability registry
description: Consolidate Agent Directory, Skill Registry, and Tool Registry into one governed capability layer.
timestamp: "2026-06-20T03:00:00Z"
taskId: KT-OS-DIGITAL-WORKER-CAPABILITY-REGISTRY
taskType: os_master_task
projectId: company-knowledge-core
requester: meimei
assignee: agent.company-knowledge-core.project-manager
requiredCapabilities:
  - agent_directory
  - skill_registry
  - tool_registry
  - permission_model
requiredAgents:
  - agent.company-knowledge-core.project-manager
  - agent.company-knowledge-core.knowledge-engineering
preferredRunner: []
assignedRunner: []
executorAgent: []
leaseOwner: []
leaseExpiresAt: []
status: done
priority: critical
dueAt: []
sourceMaterialRefs:
  - projects/company-knowledge-core/tasks/kt-os-agent-directory.md
  - projects/company-knowledge-core/tasks/kt-os-skill-registry-lifecycle.md
  - projects/company-knowledge-core/tasks/kt-os-tool-registry-policy.md
expectedOutput:
  - schedulable Agent records
  - skill lifecycle and version contract
  - tool invocation and persistence policy
  - capability reliability report
resultRef: task-results/tr-kt-os-digital-worker-capability-registry.md
notificationRefs: []
auditRefs: []
completedAt: "2026-06-20T03:30:00Z"
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"os_master_task","category":"project","stage":"","requiredCapabilities":["os_master_task","agent_directory","skill_registry","tool_registry","permission_model"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/tasks/kt-os-agent-directory.md","projects/company-knowledge-core/tasks/kt-os-skill-registry-lifecycle.md","projects/company-knowledge-core/tasks/kt-os-tool-registry-policy.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
updatedAt: "2026-06-21T07:18:05Z"
---

## Goal

The system must know which digital employee can do what, with which skills and tools, under which permissions, and with what reliability.

## Covers

- `KT-OS-AGENT-DIRECTORY`
- `KT-OS-SKILL-REGISTRY-LIFECYCLE`
- `KT-OS-TOOL-REGISTRY-POLICY`

## Completion Standard

- Agent records include role contract, permissions, allowed tools, knowledge scopes, and version.
- Skills are registered or referenced with owner, scope, version, eval requirement, and rollout state.
- Tool invocation is separate from tool result persistence.
- Capability reports expose quality and reliability signals.

## Test Method

- Agent and project-agent registration tests.
- Tool dry-run, approval, and persistence-policy tests.
- Agent capability report test.
- Validation blocks missing required role/capability fields.
