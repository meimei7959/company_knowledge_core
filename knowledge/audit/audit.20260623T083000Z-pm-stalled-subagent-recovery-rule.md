---
type: AuditLog
title: PM stalled sub Agent recovery rule update
description: Record workflow rule fix after a delegated Product Agent stalled and PM nearly proposed fallback artifact creation.
timestamp: "2026-06-23T08:30:00Z"
auditId: audit.20260623T083000Z-pm-stalled-subagent-recovery-rule
actor: agent.company.project-manager
action: pm.stalled_subagent_recovery_rule_updated
targetRefs:
  - agents/agent.company.project-manager.md
  - docs/agent-team/project-manager-agent-skill-pack.md
  - docs/agent-team/company-agent-team-operating-guide.md
status: observed
riskLevel: medium
---

# PM stalled sub Agent recovery rule update

## Trigger

During product planning orchestration, the first delegated Product Agent stalled without timely progress. PM closed the stalled run and re-dispatched a smaller Product Agent task, but PM also suggested preparing a fallback product skeleton.

## Correction

PM fallback artifact creation is a role-boundary violation. When a sub Agent stalls, PM must terminate or interrupt the run, record the stall, re-dispatch to the same owning role with a smaller scope and explicit timeout, and wait for the owning role TaskResult.

## Updated Rules

- PM may recover workflow execution.
- PM may not produce PRD, design, architecture, development, test, product acceptance, or knowledge-answer artifacts for the stalled role.
- If no replacement Agent is available, PM marks the task `blocked` or `needs_decision`.
- Any human-requested PM role takeover must be recorded as an explicit exception and remains unaccepted until the owning role or human reviewer approves it.

## Evidence

- `agents/agent.company.project-manager.md`
- `docs/agent-team/project-manager-agent-skill-pack.md`
- `docs/agent-team/company-agent-team-operating-guide.md`
