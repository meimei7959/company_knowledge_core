---
type: AuditLog
title: audit.20260623T120000Z-billing-lite-path-prevention
timestamp: "2026-06-23T12:00:00Z"
auditId: audit.20260623T120000Z-billing-lite-path-prevention
actor: agent.company.project-manager
action: process.lesson.record
targetRef: projects/billing-lite/lessons.md
before: missing_prevention_rule
after: path_prevention_rule_recorded
policyResult: workflow_issue_recorded
---

## Details

intent=prevent_new_project_path_confusion
incident=Initial Billing Lite intake created central project records before creating the user-visible Documents workspace.
rootCause=The intake flow did not explicitly distinguish entity workspace from central record path.
prevention=Require new project intake to resolve entity workspace and central record path separately; create or verify entity workspace first when user refers to Finder, 文稿, 本地, or screenshots.
updatedRefs=projects/billing-lite/lessons.md, docs/guides/teammate-agent-new-project-onboarding.md, projects/billing-lite/log.md
