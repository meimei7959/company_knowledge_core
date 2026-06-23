---
type: AuditLog
title: audit.20260623T061412012459Z
timestamp: "2026-06-23T06:14:12Z"
auditId: audit.20260623T061412012459Z
actor: agent.company.project-manager.standby
action: pm_control_lease.denied
targetRef: "task:E2E-STANDBY-6c4f84f1"
before: ""
after: denied
policyResult: pm_control_lease_not_primary
---

## Details

projectId=pm-lease-api-e2e-20260623141411
requestPmAgentId=agent.company.project-manager.standby
currentPrimaryPmAgentId=agent.company.project-manager
action=task.create
reasonCode=pm_control_lease_not_primary
leaseId=pmlease.pm-lease-api-e2e-20260623141411.20260623T061411906651Z
currentLeaseStatus=active
sourceChannel=api
targetRef=task:E2E-STANDBY-6c4f84f1
