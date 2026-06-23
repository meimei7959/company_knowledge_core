---
type: ProjectTask
title: AI Native OS Agent Directory hardening
description: Turn role Agent definitions into schedulable digital employee records with identity, contract, skills, permissions, version, and reliability signals.
timestamp: "2026-06-20T02:40:00Z"
taskId: KT-OS-AGENT-DIRECTORY
taskType: os_maturity_hardening
projectId: company-knowledge-core
requester: meimei
assignee: agent.company-knowledge-core.project-manager
requiredCapabilities:
  - agent_directory
  - role_contract
  - permission_model
  - reliability_metrics
requiredAgents:
  - agent.company-knowledge-core.project-manager
  - agent.company-knowledge-core.knowledge-engineering
preferredRunner: runner.meimei-mac-local-codex
assignedRunner: runner.meimei-mac-local-codex
executorAgent: agent.company-knowledge-core.project-manager
leaseOwner: []
leaseExpiresAt: []
status: waiting_runner
priority: high
dueAt: []
sourceMaterialRefs:
  - docs/agent-team/company-agent-team-operating-guide.md
  - projects/company-knowledge-core/agents.md
expectedOutput:
  - AgentDirectory contract
  - role input/output contracts
  - agent version and skill version fields
  - reliability and quality metrics fields
resultRef: []
notificationRefs:
  - notifications/notification.20260621T052918736808Z.md
auditRefs: []
updatedAt: "2026-06-21T07:18:05Z"
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"os_maturity_hardening","category":"project","stage":"","requiredCapabilities":["os_maturity_hardening","agent_directory","role_contract","permission_model","reliability_metrics"],"requiredTools":[],"sourceRefs":["docs/agent-team/company-agent-team-operating-guide.md","projects/company-knowledge-core/agents.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
---

## Goal

Make each company Agent a schedulable digital employee, not just a job description.

## Supports Mature OS Capability

Agent Directory.

## Requirements

- Every Agent record declares identity, role, accountable scope, input contract, output contract, skills, tools, permissions, escalation path, version, and reliability signals.
- The scheduler can select an accountable Agent without relying on human-readable role text.
- TaskResult records the accountable Agent version and skill version used.

## Completion Standard

- Agent records can be validated for required fields.
- Missing role contract, missing skill version, or missing permission scope fails validation.
- The company Agent guide and machine-readable Agent records stay aligned.

## Test Method

- Add validation cases for complete Agent records and incomplete Agent records.
- Verify one project task can resolve accountable Agent by role and capability.
- Verify TaskResult preserves Agent identity and version.
