---
type: AuditLog
title: PM control lease non-sandbox API validation passed after rework
description: Test Agent reran the non-sandbox PM control lease HTTP/API route suite after development rework and accepted the result.
timestamp: "2026-06-23T06:40:00Z"
actor: agent.company.test
action: pm_control_lease.non_sandbox_api_validation_passed
objectRef: projects/company-knowledge-core/tasks/kt-v2-pm-control-lease-non-sandbox-api-validation.md
projectId: company-knowledge-core
taskId: kt-v2-pm-control-lease-non-sandbox-api-validation
before: changes_requested
after: accepted
policyResult: passed
details: |
  Test Agent used the local readiness environment to start a real KnowledgeHTTPServer with PostgreSQL readiness.
  The rerun passed 38 checks in a temporary validation bundle.
  Real PM lease creation no longer breaks /health.
  PM lease persistence no longer triggers secret scanning.
  Old client field compatibility, protected writes, denial audits, denied-write no-target behavior, release, takeover, expired/stale rejection, and workbench PM control read model all passed.
evidenceRefs:
  - projects/company-knowledge-core/test-reports/phase2-pm-control-lease-non-sandbox-api-validation.md
  - task-results/tr-kt-v2-pm-control-lease-non-sandbox-api-validation.md
  - /private/tmp/pm_control_lease_revalidation.json
---

# Audit
