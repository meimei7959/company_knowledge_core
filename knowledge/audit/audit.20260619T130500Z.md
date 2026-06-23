---
type: AuditLog
title: audit.20260619T130500Z
timestamp: 2026-06-19T13:05:00Z
auditId: audit.20260619T130500Z
actor: agent.company-knowledge-core.knowledge-engineering
action: agent_team.operating_guide_gate.implemented
targetRef: docs/agent-team/company-agent-team-operating-guide.md
before: operating guide update rule existed as documentation
after: operating guide update rule enforced by task finish and bundle validation gates
policyResult: human_approval_required_for_cross_team_workflow_standard
---

## Audit

Implemented the mandatory Company Agent Team operating guide update gate.

Reason:

- The user required the guide to remain current whenever Agent responsibility, Skill, workflow, Scheduler, Agent Ring, or knowledge policy changes.
- A documentation-only rule is not enough; task closure and validation must enforce it.

Changes:

- Added structured guide gate fields to created tasks and TaskResult records.
- Added automatic detection for Agent/Skill/Workflow/Scheduler/Agent Ring/knowledge policy change tasks.
- Added runtime refusal when a guide-impacting task is closed without guide update evidence.
- Added bundle validation checks for guide gate fields.
- Updated the operating guide with field-level instructions and CLI usage.

Review note:

This is a cross-team operating standard and should remain subject to Knowledge Engineering review and human approval before becoming verified policy.
