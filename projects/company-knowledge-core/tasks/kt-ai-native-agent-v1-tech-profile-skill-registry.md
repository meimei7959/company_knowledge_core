---
type: ProjectTask
title: AI Native Agent V1 Technical Solution - Agent Profile And Skill Registry
description: Development Agent technical solution for executable Agent Profile Service and Skill Registry.
timestamp: "2026-06-22T00:00:00+08:00"
taskId: kt-ai-native-agent-v1-tech-profile-skill-registry
taskType: technical_solution
projectId: company-knowledge-core
requester: agent.company.project-manager
assignee: agent.company.development
currentStage: technical_solution
technicalSolutionRequired: true
requiredCapabilities:
  - development
  - scheduler
  - agent_worker
requiredAgents:
  - agent.company.development
preferredRunner: runner.meimei-mac-local-dev-rt
assignedRunner: runner.meimei-mac-local-dev-rt
executorAgent: agent.company.development
leaseOwner: runner.meimei-mac-local-dev-rt
leaseExpiresAt: "2026-06-22T03:13:38Z"
status: done
priority: high
dueAt: []
sourceMaterialRefs:
  - /Users/meimei/Downloads/AI_Native_Agent协同系统_PRD_V1.0.docx
  - /Users/meimei/Downloads/AI_Native_Agent协同系统_技术方案_V1.0.docx
  - projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-product-requirement-structure.md
  - projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-product-scope-review.md
  - agents/
  - skills/
  - docs/agent-team/role-operating-specs.json
expectedOutput:
  - technical solution document
  - implementation task breakdown
  - migration plan from existing agent and skill files
resultRef: task-results/tr-kt-ai-native-agent-v1-tech-profile-skill-registry.md
notificationRefs:
  - notifications/notification.20260622T030255212558Z.md
  - notifications/notification.20260622T030338344309Z.md
  - notifications/notification.20260622T030338348075Z.md
  - notifications/notification.20260622T030338349041Z.md
  - notifications/notification.20260622T030338349895Z.md
  - notifications/notification.20260622T030353552515Z.md
auditRefs:
  - knowledge/audit/audit.20260622T000000-ai-native-agent-v1-upgrade-plan.md
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"technical_solution","category":"project","stage":"technical_solution","requiredCapabilities":["technical_solution","development","scheduler","agent_worker"],"requiredTools":[],"sourceRefs":["/Users/meimei/Downloads/AI_Native_Agent协同系统_PRD_V1.0.docx","/Users/meimei/Downloads/AI_Native_Agent协同系统_技术方案_V1.0.docx","projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-product-requirement-structure.md","projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-product-scope-review.md","agents/","skills/","docs/agent-team/role-operating-specs.json"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
updatedAt: "2026-06-22T03:03:53Z"
leaseTokenHash: 3645bf2ce33236be0c359b7f9ecec551a265930a2efbb284f2d816b8435d6a42
leaseProofHash: 3645bf2ce33236be0c359b7f9ecec551a265930a2efbb284f2d816b8435d6a42
leaseHeartbeatAt: "2026-06-22T03:03:38Z"
heartbeatAt: "2026-06-22T03:03:38Z"
taskVersion: 3
retryRequestedAt: "2026-06-22T03:02:55Z"
retryRequestedBy: agent.company.project-manager
retryReason: product-scope-accepted-release-development-technical-solution
retryHistory:
  - {"fromStatus":"blocked","reason":"product-scope-accepted-release-development-technical-solution","actor":"agent.company.project-manager","previousRunnerId":"","at":"2026-06-22T03:02:55Z"}
failureReasons:
  - product-scope-accepted-release-development-technical-solution
attemptNumber: 2
nextAction: Runner should claim the retry lease and write back fresh evidence.
leaseIssuedAt: "2026-06-22T03:03:38Z"
leaseVersion: 3
leaseAttempt: 1
completedAt: "2026-06-22T03:03:38Z"
followupTaskRefs:
  - projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-tech-profile-skill-registry-handoff.md
---

## Request

Produce the technical solution before implementation for Agent Profile Service and Skill Registry.

## Expected Output

- Machine-readable Agent Profile schema and storage path.
- Skill Registry metadata schema including input schema, output schema, tools, risk level, confirmation policy, and allowed agents.
- Loader strategy for existing `agents/*.md`, `skills/*/SKILL.md`, and role operating specs.
- Validation rules and tests.
- Implementation tasks and risks.

## Handling Notes

Blocked until Product Manager Agent completes V1 requirement structuring and scope review.
