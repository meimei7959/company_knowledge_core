---
type: AuditLog
title: audit.20260618T024458Z
timestamp: 2026-06-18T02:44:58Z
auditId: audit.20260618T024458Z
actor: codex
action: feishu.project_init_idempotency_fix
targetRef: zhenzhi_knowledge/feishu.py
before: project-init-could-create-duplicate-approvals-for-same-project-target
after: project-init-reuses-existing-project-or-pending-approval
policyResult: root_cause_fix
---

## Details

Added project-level idempotency to the Feishu project initiation flow. If the project is already verified/approved/active, the bot reports the existing project instead of creating another approval. If the same project target already has a pending approval request, the bot reuses that approval instead of creating a duplicate.
