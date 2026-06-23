---
type: AuditLog
title: audit.20260621T074620287163Z
timestamp: "2026-06-21T07:46:20Z"
auditId: audit.20260621T074620287163Z
actor: agent.company.project-manager
action: scheduler.lease.stale_repair
targetRef: projects/company-knowledge-core/tasks/kt-ai-native-os-impl-scheduler-runner-result-retry.md
before: processing
after: waiting_runner
policyResult: lease_expired
---

## Details

{"taskId": "kt-ai-native-os-impl-scheduler-runner-result-retry", "taskRef": "projects/company-knowledge-core/tasks/kt-ai-native-os-impl-scheduler-runner-result-retry.md", "previousRunnerId": "runner.meimei-mac-local-codex", "status": "waiting_runner", "reason": "lease_expired", "priority": "critical"}
