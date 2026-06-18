---
type: AuditLog
title: audit.20260618T031220Z
timestamp: 2026-06-18T03:12:20Z
auditId: audit.20260618T031220Z
actor: codex
action: feishu.project_owner_notification.add
targetRef: zhenzhi_knowledge/feishu.py
before: project-init-approval-notified-only-submitter
after: project-init-approval-notifies-submitter-and-project-owner-with-onboarding
policyResult: root_cause_fix
---

## Details

Project initiation approval now notifies both the submitter and, when different, the project owner. The project owner message includes the project ID and concise usage instructions for meeting notes, source materials, lessons, local Agent workflow, and token application.
