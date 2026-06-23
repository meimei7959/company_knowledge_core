---
type: AuditLog
title: audit.20260623T120500Z-new-project-workspace-confirmation-rule
timestamp: "2026-06-23T12:05:00Z"
auditId: audit.20260623T120500Z-new-project-workspace-confirmation-rule
actor: agent.company.project-manager
action: process.rule.refine
targetRef: docs/guides/teammate-agent-new-project-onboarding.md
before: local_workspace_path_could_be_inferred_without_confirmation
after: workspace_path_requires_user_confirmation_or_pending_confirmation
policyResult: workflow_rule_refined
---

## Details

intent=avoid_cross_machine_workspace_path_assumption
reason=梅晓华指出 that a path valid on one computer may be wrong on another computer.
rule=When creating a new project, an Agent may infer a candidate entity workspace from the current computer, but must confirm it with the user unless the user supplied an explicit absolute path. In unattended flows, record workspaceRef as pending_confirmation.
updatedRefs=projects/billing-lite/lessons.md, docs/guides/teammate-agent-new-project-onboarding.md
