---
type: ProjectTask
title: AI Native OS product console surfaces
description: Implement the web product console surfaces required by the complete AI Native OS launch package.
timestamp: "2026-06-21T05:13:34Z"
taskId: kt-ai-native-os-dev-console-surfaces
taskType: development
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"development","category":"engineering","stage":"technical_solution","requiredCapabilities":["development","frontend_development","product_console","workflow_ui"],"requiredTools":[],"sourceRefs":["docs/product/ai-native-os/prd.md","docs/product/ai-native-os/requirements.md","docs/product/ai-native-os/development-handoff.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"engineering","acceptancePath":"test_then_pm_review","reviewPath":"engineering_test","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
projectId: company-knowledge-core
requester: agent.company.project-manager
requiredCapabilities:
  - frontend_development
  - product_console
  - workflow_ui
requiredAgents:
  - agent.company.development
executorAgent: agent.company.development
status: waiting_runner
priority: high
technicalSolutionRequired: true
currentStage: technical_solution
sourceMaterialRefs:
  - docs/product/ai-native-os/prd.md
  - docs/product/ai-native-os/requirements.md
  - docs/product/ai-native-os/development-handoff.md
requirementRefs:
  - ANOS-REQ-001
  - ANOS-REQ-002
  - ANOS-REQ-003
  - ANOS-REQ-004
  - ANOS-REQ-005
  - ANOS-REQ-006
  - ANOS-REQ-030
  - ANOS-REQ-031
  - ANOS-REQ-032
  - ANOS-REQ-033
  - ANOS-REQ-034
  - ANOS-REQ-040
  - ANOS-REQ-041
  - ANOS-REQ-042
  - ANOS-REQ-043
  - ANOS-REQ-044
  - ANOS-REQ-045
expectedOutput:
  - Technical solution covering route map, component boundaries, workflow states, data dependencies, test strategy, risks, and TaskResult evidence shape.
  - Console implementation for Requirement Center, Project Console, Agent Team Manager, Scheduler, Agent Ring, Result Center, Review Center, Tool/Skill Registry, Quality Dashboard, Notification, Admin, Ops, and API visibility.
  - UI tests or screenshots for critical workflows.
  - TaskResult with outputRefs and evidenceRefs.
updatedAt: "2026-06-21T07:18:05Z"
notificationRefs:
  - notifications/notification.20260621T052918726774Z.md
  - notifications/notification.20260621T053349636602Z.md
  - notifications/notification.20260621T053430450845Z.md
  - notifications/notification.20260621T055518605355Z.md
  - notifications/notification.20260621T055524565988Z.md
  - notifications/notification.20260621T055554608261Z.md
  - notifications/notification.20260621T055613421815Z.md
  - notifications/notification.20260621T061855444776Z.md
  - notifications/notification.20260621T062940736616Z.md
assignedRunner: runner.meimei-mac-local-codex
---

## Scope

Implement DEV-003 console surfaces as operational tools, not marketing pages.

## Acceptance

- Technical solution is accepted by Project Manager Agent before broad implementation starts.
- User can inspect work state, blockers, runners, results, review state, and launch readiness.
- Console does not hide raw workflow failures behind generic status text.
