---
type: AuditLog
title: audit.20260618T023048Z
timestamp: 2026-06-18T02:30:48Z
auditId: audit.20260618T023048Z
actor: codex
action: feishu.approval.project_notification_recovery_fix
targetRef: zhenzhi_knowledge/feishu.py
before: deploy-delete-could-remove-runtime-project-targets-and-approval-callback-ignored-events-were-not-audited
after: deploy-protects-runtime-knowledge-dirs-and-approval-callback-can-recreate-missing-project-targets
policyResult: root_cause_fix
---

## Details

Root cause: deployment used `rsync --delete` without protecting runtime knowledge object directories. Online project drafts created by the Feishu bot could be deleted while approval request cache under `.zhenzhi` remained, leaving approval callbacks without a target object to publish or notify from.

Fix: protect mutable knowledge object directories during deployment, audit ignored approval callbacks, and recreate missing project-init targets from the saved approval request before applying the approval result.
