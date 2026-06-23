---
type: AuditLog
title: audit.20260619T134500Z
timestamp: 2026-06-19T13:45:00Z
auditId: audit.20260619T134500Z
actor: agent.company-knowledge-core.knowledge-engineering
action: agent_team.role_handoff_flow.documented
targetRef: docs/agent-team/company-agent-team-operating-guide.md
before: guide defined role responsibilities but lacked an explicit cross-role handoff flow
after: guide includes standard project flow, role handoff table, rework branches, and project manager horizontal responsibility
policyResult: human_approval_required_for_cross_team_workflow_standard
---

## Audit

Documented how company-level Agent roles cooperate across a complete project lifecycle.

Reason:

- The user asked to review whether all岗位职责 are complete and whether the roles can connect the whole project flow.
- The previous guide had role-level responsibilities but did not explicitly define the handoff between roles.

Changes:

- Added `岗位协同主流程`.
- Added a standard project flow from Agent Hub intake to project management, product, design, engineering, testing, operations, knowledge engineering, and knowledge query.
- Added a role handoff table with input, output, owner, and downstream Agent.
- Added rework and branch rules.
- Clarified Project Manager Agent's horizontal orchestration responsibility.

Review note:

This change affects cross-role operating flow and should remain subject to Knowledge Engineering review and human approval before becoming verified policy.
