---
type: TaskResult
title: Result for kt-v2-pm-control-lease-real-multicomputer-validation
description: Test Agent result for real multi-computer or equivalent independent host PM control lease conflict validation.
timestamp: "2026-06-23T06:45:43Z"
createdAt: "2026-06-23T06:45:43Z"
completedAt: "2026-06-23T06:45:43Z"
resultId: TR-kt-v2-pm-control-lease-real-multicomputer-validation
taskId: kt-v2-pm-control-lease-real-multicomputer-validation
projectId: company-knowledge-core
assignee: agent.company.test
runnerId: local.codex
runner: local.codex
leaseProof: ""
executorAgent: agent.company.test
status: submitted
summary: Real multi-host PM control lease validation failed because two independent PM clients acquired the same project primary lease concurrently. Test Agent created a development rework task and did not modify development code.
outputRefs:
  - projects/company-knowledge-core/test-reports/phase2-pm-control-lease-real-multicomputer-validation.md
  - projects/company-knowledge-core/tasks/kt-v2-pm-control-lease-concurrent-acquire-rework.md
evidenceRefs:
  - /private/tmp/pm_control_lease_real_multicomputer_20260623T064422Z.json
  - projects/company-knowledge-core/product-reviews/phase2-pm-control-lease-product-final-acceptance.md
  - projects/company-knowledge-core/test-reports/phase2-pm-control-lease-non-sandbox-api-validation.md
  - task-results/tr-kt-v2-pm-control-lease-secret-scan-rework.md
  - projects/company-knowledge-core/ops/phase2-pm-control-lease-api-readiness.md
testsOrChecks:
  - real_http_server_postgresql_readiness_health_passed
  - two_independent_host_runner_device_registration_passed
  - concurrent_primary_pm_acquire_failed_two_successes
  - valid_primary_write_passed
  - missing_lease_denial_audited_passed
  - collaborator_pm_write_denial_audited_passed
  - standby_pm_write_denial_audited_passed
  - project_mismatch_denial_audited_passed
  - healthy_primary_takeover_rejected_passed
  - expired_primary_standby_takeover_passed
  - stale_generation_denied_passed
  - workbench_pm_control_read_model_passed
checks:
  - python_validation_script_real_http_multi_host_failed_on_concurrent_acquire
  - evidence_json_written_to_private_tmp
  - development_rework_task_created
qualityEvaluation: {"type":"AgentResultEvaluation","status":"failed","passed":false,"decision":"repair_required","score":62,"attemptNumber":1,"maxAttempts":3,"retryable":true,"reasons":["Concurrent primary PM acquire allowed two successful leases for the same project.","This violates the one-project-one-primary-PM scheduling lease requirement."],"artifactRefsPresent":true,"evidenceRefsPresent":true,"testsOrChecksPresent":true,"expectedOutputCovered":true,"nextOwnerAgent":"agent.company.development"}
acceptancePolicy: {"version":"acceptance.v1","acceptanceStatus":"changes_requested","humanAcceptanceRequired":true,"acceptanceRequiredByDefault":true,"projectManager":"agent.company.project-manager","humanReviewer":"agent.company.project-manager","decisionReason":"Test Agent found a release-blocking concurrent acquire defect and created a development rework task.","requiresNextTaskCreation":true}
nextAction: agent.company.development should fix kt-v2-pm-control-lease-concurrent-acquire-rework, then agent.company.test should rerun real multi-host validation.
nextActions:
  - agent.company.development must fix kt-v2-pm-control-lease-concurrent-acquire-rework.
  - agent.company.test must rerun kt-v2-pm-control-lease-real-multicomputer-validation after the fix.
risks:
  - PM control lease acquire is not atomic under concurrent HTTP requests.
  - Production multi-computer orchestration may temporarily have more than one primary PM for one project until fixed.
blockers:
  - concurrent_pm_control_lease_acquire_allows_multiple_primary_leases
approvalRequest: {}
operatingRuleRefs: {"companyConstitution":"docs/agent-team/company-agent-constitution.md","taskRuntimeContract":"docs/agent-team/agent-task-runtime-contract.md","humanAcceptancePolicy":"docs/agent-team/human-acceptance-policy.md","roleOperatingSpec":"docs/agent-team/role-operating-specs.json","roleRules":"agents/agent.company.test.md","projectRules":"projects/company-knowledge-core/AGENTS.md"}
commonRulesEvaluation: {"version":"common-agent-rules.v1","status":"passed","passed":true,"checkedRules":["role_boundary","evidence_required","no_development_code_change_by_test_agent","durable_task_result"],"notes":["Test Agent did not modify development code.","A development rework task was created for the confirmed implementation defect."]}
---

# Task Result

测试已执行，结论为 changes_requested。失败点是共享中枢并发抢主控租约时两个 PM 都成功，已流转研发返工。
