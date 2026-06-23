---
type: ProjectTask
title: AI Native OS repair - TaskResult metadata migration for validate gate
description: Repair historical TaskResult objects or compatibility validation so tightened TaskResult metadata requirements do not block full repository validation.
timestamp: "2026-06-21T07:22:00Z"
taskId: kt-ai-native-os-repair-taskresult-metadata-migration
taskType: development
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"development","category":"engineering","stage":"repair","requiredCapabilities":["development","schema_migration","validation","task_result_writeback"],"requiredTools":[],"sourceRefs":["task-results/","zhenzhi_knowledge/core.py","tests/test_cli.py"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"engineering","acceptancePath":"test_then_pm_review","reviewPath":"development_repair_then_test","riskLevel":"high","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
projectId: company-knowledge-core
requester: agent.company.project-manager
requiredCapabilities:
  - development
  - schema_migration
  - validation
  - task_result_writeback
requiredAgents:
  - agent.company.development
executorAgent: agent.company.development
status: done
priority: critical
currentStage: repair
requirementRefs:
  - ANOS-REQ-070
  - ANOS-REQ-071
  - ANOS-REQ-072
  - ANOS-REQ-073
  - ANOS-REQ-080
  - ANOS-REQ-081
sourceMaterialRefs:
  - zhenzhi_knowledge/core.py
  - task-results/
expectedOutput:
  - Full `python3 -m zhenzhi_knowledge --root /Users/meimei/Documents/company_knowledge_core validate` no longer fails because of historical TaskResult metadata gaps.
  - Repair approach is explicit: either migrate historical TaskResult frontmatter safely or make validator apply compatible defaults for pre-contract legacy records.
  - Regression tests prove new TaskResults still require runner, leaseProof, risks, blockers, nextAction, checks, approvalRequest, qualityEvaluation, createdAt, operatingRuleRefs, and commonRulesEvaluation.
  - TaskResult for this repair includes exact changed files, tests, risks, and next action.
assignedRunner: runner.meimei-mac-local-codex
leaseOwner: runner.meimei-mac-local-codex
leaseTokenHash: 0a1df29783f43ddadae9dcbd9eb46e4a5ca1696c67f0527fb76916bb1537d0d9
leaseProofHash: 0a1df29783f43ddadae9dcbd9eb46e4a5ca1696c67f0527fb76916bb1537d0d9
leaseIssuedAt: "2026-06-21T08:01:03Z"
leaseExpiresAt: "2026-06-21T09:01:03Z"
leaseHeartbeatAt: "2026-06-21T08:01:03Z"
heartbeatAt: "2026-06-21T08:01:03Z"
leaseVersion: 3
leaseAttempt: 2
taskVersion: 4
updatedAt: "2026-06-21T08:12:52Z"
notificationRefs:
  - notifications/notification.20260621T072134035000Z.md
  - notifications/notification.20260621T074620290810Z.md
  - notifications/notification.20260621T074620291464Z.md
  - notifications/notification.20260621T074620292068Z.md
  - notifications/notification.20260621T080103746336Z.md
  - notifications/notification.20260621T081109122519Z.md
  - notifications/notification.20260621T081109124158Z.md
  - notifications/notification.20260621T081109124745Z.md
  - notifications/notification.20260621T081252171426Z.md
staleLeaseOwner: runner.meimei-mac-local-codex
staleLeaseDetectedAt: "2026-06-21T07:46:20Z"
staleLeaseReason: lease_expired
resultRef: task-results/tr-kt-ai-native-os-repair-taskresult-metadata-migration.md
completedAt: "2026-06-21T08:11:09Z"
followupTaskRefs:
  - projects/company-knowledge-core/tasks/kt-ai-native-os-repair-taskresult-metadata-migration-handoff.md
---

# Root Cause

Recent TaskResult contract tightening made historical TaskResult files fail repository validation. Full unittest passes, but full validate reports 406 missing-field lines across existing `task-results/*.md`.

# Repair Rules

- Do not weaken the new contract for newly created TaskResult files.
- Do not fabricate misleading runner or lease evidence for historical records.
- If migrating historical records, mark compatibility/default provenance clearly.
- If changing validator behavior, legacy compatibility must be narrow, auditable, and tested.
- Do not repair unrelated product logic in this task.

# Required Verification

- Run full unittest discovery.
- Run full repository validate.
- Add or update focused tests for legacy TaskResult compatibility or migration behavior.
