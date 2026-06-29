---
type: TaskResult
title: Task Result
description: Result of assigned task work.
timestamp: 2026-06-18T00:00:00Z
resultId: TR-YYYYMMDD-001
taskId: KT-YYYYMMDD-001
projectId: project-id
workSourceType: feature
requirementRefs: []
requirementObjectRefs: []
acceptanceCriteriaRefs: []
defectRefs: []
defectObjectRefs: []
incidentRefs: []
operationRefs: []
knowledgeTaskRefs: []
researchQuestion:
sourceReason:
receiverReviewRefs: []
runnerId: runner.example
executorAgent: agent.example
status: submitted
summary: ""
outputRefs: []
knowledgeRefs: []
sourceMaterialRefs: []
evidenceRefs: []
testsOrChecks: []
nextActions: []
executionContractEvaluation:
  version: execution-contract-evaluation.v1
  status: pending
  passed: false
  required: true
  freshnessRequired: true
  contractRef:
  storedSourceFactsHash:
  currentSourceFactsHash:
  ruleRef: docs/workflows/execution-contract-lifecycle.md
  reasons: []
pmCanClose: false
pmCloseoutScope: ""
pmDeliveryGate:
  enforce: false
  requirementRefs: []
  requireProductAcceptance: true
operatingRuleRefs:
  companyConstitution: docs/agent-team/company-agent-constitution.md
  taskRuntimeContract: docs/agent-team/agent-task-runtime-contract.md
  humanAcceptancePolicy: docs/agent-team/human-acceptance-policy.md
  commonRules: docs/agent-team/common-agent-operating-rules.md
  agentTeamGuide: docs/agent-team/company-agent-team-operating-guide.md
  roleOperatingSpec: docs/agent-team/role-operating-specs.json
  roleRules:
  projectRules:
commonRulesEvaluation:
  version: common-agent-rules.v1
  status: pending
  passed: false
  reasons: []
completedAt:
---

## Summary

What was completed by the Agent Ring runner.

## Traceability

- Inherit workSourceType and linked refs from the source task.
- Feature results must preserve requirementRefs and acceptanceCriteriaRefs.
- Bugfix results must preserve defectRefs and defectObjectRefs.
- ReceiverReview refs show which downstream gate accepted or blocked the upstream artifact.
- PM closeout, PM acceptance, release acceptance, or final acceptance results must set `pmDeliveryGate.enforce: true` and list the relevant `requirementRefs`.
- A PM delivery gate can close only after linked Development, Test, and required Product Manager acceptance TaskResults pass validation.
- If a PM closeout artifact is only a process/status note and not a delivery acceptance gate, set `pmCloseoutScope: process_status_only` and include evidence refs.

## Evidence

- Link each conclusion to SourceMaterial, document section, timestamp, commit, test, or other evidence.

## Outputs

- KnowledgeItem drafts, project updates, tool updates, or external deliverables.

## Next Actions

- Follow-up tasks, review needs, blockers, or notifications.

## Execution Contract

- Confirm the TaskResult was produced from the current `executionContract`.
- If stale, refresh the task contract and rerun the affected work before closing.

## Common Operating Rules

- Confirm the Agent read the layered rule refs before work.
- Record rule failures as retry, repair, escalation, or OperatingRuleIssue.
