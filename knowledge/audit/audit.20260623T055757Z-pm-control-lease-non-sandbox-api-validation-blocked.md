---
type: AuditLog
title: PM control lease non-sandbox API validation blocked
description: Test Agent attempted non-sandbox HTTP/API validation and recorded environment readiness blocker.
timestamp: "2026-06-23T05:57:57Z"
actor: agent.company.test
action: pm_control_lease.non_sandbox_api_validation_blocked
target: projects/company-knowledge-core/tasks/kt-v2-pm-control-lease-non-sandbox-api-validation.md
projectId: company-knowledge-core
policyResult: blocked
evidenceRefs:
  - projects/company-knowledge-core/test-reports/phase2-pm-control-lease-non-sandbox-api-validation.md
  - task-results/tr-kt-v2-pm-control-lease-non-sandbox-api-validation.md
---

# Audit

Test Agent attempted non-sandbox HTTP/API validation for PM control lease.

Result: blocked by missing PostgreSQL/API readiness on this machine. No development code was changed, and no development rework was opened because the failure is an environment readiness blocker.
