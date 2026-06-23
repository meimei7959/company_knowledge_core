---
type: AuditLog
title: PM control lease real multi-computer validation failed
description: Test Agent executed equivalent independent-host validation and found concurrent primary PM lease acquisition can create two successful leases.
timestamp: "2026-06-23T06:45:43Z"
actor: agent.company.test
action: pm_control_lease.real_multicomputer_validation_failed
objectRef: projects/company-knowledge-core/tasks/kt-v2-pm-control-lease-real-multicomputer-validation.md
projectId: company-knowledge-core
taskId: kt-v2-pm-control-lease-real-multicomputer-validation
before: pending
after: changes_requested
policyResult: failed
details: |
  Test Agent used two independent runner/device/worktree identities against one real KnowledgeHTTPServer and PostgreSQL readiness central hub.
  Most protected write, denial audit, takeover, stale generation, and workbench read-model checks passed.
  Release-blocking failure: two independent PM clients concurrently acquired primary PM control lease for the same project.
  Development rework task created: projects/company-knowledge-core/tasks/kt-v2-pm-control-lease-concurrent-acquire-rework.md.
evidenceRefs:
  - projects/company-knowledge-core/test-reports/phase2-pm-control-lease-real-multicomputer-validation.md
  - task-results/tr-kt-v2-pm-control-lease-real-multicomputer-validation.md
  - projects/company-knowledge-core/tasks/kt-v2-pm-control-lease-concurrent-acquire-rework.md
  - /private/tmp/pm_control_lease_real_multicomputer_20260623T064422Z.json
---

# Audit
