---
type: TaskResult
title: Result for kt-v2-pm-control-lease-secret-scan-rework
description: Development rework result for PM control lease persistence secret scan failure.
timestamp: "2026-06-23T06:28:00Z"
resultId: TR-kt-v2-pm-control-lease-secret-scan-rework
taskId: kt-v2-pm-control-lease-secret-scan-rework
projectId: company-knowledge-core
assignee: agent.company.development
runnerId: local.codex
runner: local.codex
leaseProof: ""
executorAgent: agent.company.development
status: submitted
summary: Reworked PM control lease persistence so generated lease files store leaseGeneration, deduplicationRef, and leaseProofHash instead of fencingToken, idempotencyKey, or leaseTokenHash, while keeping HTTP/CLI compatibility with older request fields.
outputRefs:
  - zhenzhi_knowledge/core.py
  - zhenzhi_knowledge/server.py
  - zhenzhi_knowledge/cli.py
  - tests/test_cli.py
  - projects/company-knowledge-core/desktop-workbench-slice0/shared-frontend-foundation.ts
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-read-model.js
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-live-read-model.js
knowledgeRefs: []
sourceMaterialRefs:
  - projects/company-knowledge-core/tasks/kt-v2-pm-control-lease-secret-scan-rework.md
  - projects/company-knowledge-core/test-reports/phase2-pm-control-lease-non-sandbox-api-validation.md
evidenceRefs:
  - tests/test_cli.py
  - task-results/tr-kt-v2-pm-control-lease-secret-scan-rework.md
testsOrChecks:
  - targeted_pm_control_rework_tests_passed_3_tests
  - desktop_workbench_slice0_tests_passed_14_tests
  - cli_tests_passed_185_tests
  - bundle_validate_passed
  - git_diff_check_passed
checks:
  - python3 -m unittest tests.test_cli.CliTests.test_pm_control_lease_core_guard_takeover_and_read_model tests.test_cli.CliTests.test_pm_control_lease_api_routes_and_protected_task_create tests.test_cli.CliTests.test_pm_control_lease_cli_commands_and_task_flags
  - python3 -m unittest tests.test_desktop_workbench_slice0
  - python3 -m unittest tests.test_cli
  - python3 -m zhenzhi_knowledge.cli validate
  - git diff --check
nextActions:
  - Testing Agent should rerun kt-v2-pm-control-lease-non-sandbox-api-validation against the prepared PostgreSQL/API readiness environment.
nextAction: handoff_to_testing_agent_for_non_sandbox_api_revalidation
risks:
  - Development self-tests cover storage naming, old-field compatibility, bundle validation, and local HTTP/CLI paths. The release-level non-sandbox API revalidation remains owned by agent.company.test.
blockers: []
approvalRequest: {}
operatingRuleRefs: {"companyConstitution":"docs/agent-team/company-agent-constitution.md","taskRuntimeContract":"docs/agent-team/agent-task-runtime-contract.md","humanAcceptancePolicy":"docs/agent-team/human-acceptance-policy.md","roleOperatingSpec":"docs/agent-team/role-operating-specs.json","roleRules":"agents/agent.company.development.md","projectRules":"projects/company-knowledge-core/AGENTS.md"}
commonRulesEvaluation: {"version":"common-agent-rules.v1","status":"passed","passed":true,"checkedRules":["source_materials_read","root_cause_before_fix","systemic_flow_covered","tests_or_checks","task_result_written","role_boundary_respected"],"reasons":[],"ruleIssueRequired":false}
qualityEvaluation: {"type":"AgentResultEvaluation","status":"passed","passed":true,"decision":"handoff_ready","score":95,"retryable":false,"reasons":[],"artifactRefsPresent":true,"evidenceRefsPresent":true,"testsOrChecksPresent":true,"expectedOutputCovered":true,"nextOwnerAgent":"agent.company.test"}
createdAt: "2026-06-23T06:28:00Z"
completedAt: "2026-06-23T06:28:00Z"
updatedAt: "2026-06-23T06:28:00Z"
---

## Summary

Fixed PM control lease storage naming so real lease creation no longer writes secret-like field names into PM lease files.

## Changes

- PM control lease files now persist `leaseGeneration`, `deduplicationRef`, and `leaseProofHash`.
- HTTP/API compatibility remains: older callers may still submit `fencingToken` and `idempotencyKey`; new callers can submit `leaseGeneration`.
- CLI now accepts `--lease-generation` and `--pm-lease-generation`, while keeping old flags as compatibility aliases.
- Project task records created through PM lease context now store `pmControlLeaseGeneration`.
- Workbench PM control display now shows "防旧写入代际".
- Regression tests assert generated PM lease files no longer persist legacy token-like field names and pass secret scanning.

## Handoff

- handoffTo: agent.company.test
- terminalReason: development rework complete; testing Agent must rerun release-level non-sandbox HTTP/API validation.
