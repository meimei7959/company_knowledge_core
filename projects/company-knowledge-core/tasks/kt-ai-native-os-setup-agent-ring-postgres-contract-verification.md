---
type: ProjectTask
title: AI Native OS setup - Agent Ring PostgreSQL contract verification
description: Provide a PostgreSQL DATABASE_URL test environment and run the live Agent Ring contract verification that was blocked during scheduler/runner testing.
timestamp: "2026-06-21T07:52:00Z"
taskId: kt-ai-native-os-setup-agent-ring-postgres-contract-verification
taskType: operations
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"operations","category":"engineering","stage":"environment_setup","requiredCapabilities":["operations","database","agent_ring","contract_testing"],"requiredTools":[],"sourceRefs":["scripts/agent_ring_contract.py","task-results/tr-kt-ai-native-os-test-scheduler-runner-result.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"engineering","acceptancePath":"test_then_pm_review","reviewPath":"ops_then_test","riskLevel":"medium","permissionPolicy":"approval_required_for_external_database","closurePolicy":"task_result_with_evidence","approvalRelayRequired":true,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
projectId: company-knowledge-core
requester: agent.company.project-manager
requiredCapabilities:
  - operations
  - database
  - agent_ring
  - contract_testing
requiredAgents:
  - agent.company.operations
  - agent.company.test
executorAgent: agent.company.operations
status: pending
priority: high
currentStage: environment_setup
requirementRefs:
  - ANOS-REQ-050
  - ANOS-REQ-051
  - ANOS-REQ-052
  - ANOS-REQ-053
  - ANOS-REQ-070
  - ANOS-REQ-071
sourceMaterialRefs:
  - scripts/agent_ring_contract.py
  - task-results/tr-kt-ai-native-os-test-scheduler-runner-result.md
expectedOutput:
  - Approved local or disposable PostgreSQL DATABASE_URL is available without storing secrets in repository files.
  - `python3 scripts/agent_ring_contract.py` runs successfully or returns a concrete integration defect for Development Agent repair.
  - TaskResult records environment source, secret-handling approach, command evidence, and next action.
---

# Trigger

Scheduler/Runner Test Agent could not execute `scripts/agent_ring_contract.py` because `DATABASE_URL is required and must point to PostgreSQL`.

# Closure Rules

- Do not store database credentials in this repository.
- If approval is needed to start or connect to PostgreSQL, return `approvalRequest` to PM/main window.
- If the contract script fails after environment setup, create a Development repair task with reproducible evidence.

