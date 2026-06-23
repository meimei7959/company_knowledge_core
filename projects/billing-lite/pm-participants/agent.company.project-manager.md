---
type: ProjectPmParticipant
title: agent.company.project-manager
description: PM participant state for project-level control lease.
timestamp: "2026-06-23T12:33:33Z"
projectId: billing-lite
pmAgentId: agent.company.project-manager
role: primary
runnerId: runner.billing-lite-local-pm-codex
deviceId: meimei-mac-codex
status: active
standbyPriority: 0
capabilities:
  - acceptance.route
  - notification.schedule
  - pm_schedule_write
  - project.schedule
  - recovery.route
  - task.create
  - task.update
currentLeaseId: pmlease.billing-lite.20260623T123333794462Z
displayName: agent.company.project-manager
lastActiveAt: "2026-06-23T12:33:33Z"
updatedAt: "2026-06-23T12:33:33Z"
---

## Boundary

Primary PM may write project scheduling with a valid PM control lease. Collaborator and standby PMs are read-only until takeover succeeds.
