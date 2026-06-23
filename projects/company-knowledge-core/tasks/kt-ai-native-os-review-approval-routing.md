---
type: ProjectTask
title: AI Native OS review and approval routing
description: Define review, approval, and launch stop routing for AI Native OS implementation and release readiness.
timestamp: "2026-06-21T05:13:34Z"
taskId: kt-ai-native-os-review-approval-routing
taskType: review
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"review","category":"project","stage":"","requiredCapabilities":["review","review_gate","approval_routing","launch_governance"],"requiredTools":[],"sourceRefs":["docs/product/ai-native-os/agent-collaboration-contract.md","docs/product/ai-native-os/acceptance-checklist.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
projectId: company-knowledge-core
requester: agent.company.project-manager
requiredCapabilities:
  - review_gate
  - approval_routing
  - launch_governance
requiredAgents:
  - agent.core.knowledge-review
executorAgent: agent.core.knowledge-review
status: waiting_runner
priority: high
sourceMaterialRefs:
  - docs/product/ai-native-os/agent-collaboration-contract.md
  - docs/product/ai-native-os/acceptance-checklist.md
expectedOutput:
  - Approval matrix for scope, release, permissions, policies, verified knowledge, and tool/skill changes.
  - Launch stop condition checklist.
  - Review task templates for release readiness.
updatedAt: "2026-06-21T07:18:05Z"
notificationRefs:
  - notifications/notification.20260621T052918732898Z.md
  - notifications/notification.20260621T053349642814Z.md
  - notifications/notification.20260621T053430457019Z.md
  - notifications/notification.20260621T055524573605Z.md
  - notifications/notification.20260621T055554615486Z.md
  - notifications/notification.20260621T055613428432Z.md
  - notifications/notification.20260621T061855460721Z.md
  - notifications/notification.20260621T062940782296Z.md
assignedRunner: runner.meimei-mac-local-codex
---

## Acceptance

- Launch stop conditions are explicit.
- Human approval needs are visible before execution reaches release.
