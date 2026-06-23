---
type: AuditLog
title: audit.20260618T144000Z
timestamp: "2026-06-18T14:40:00Z"
auditId: audit.20260618T144000Z
actor: codex
action: feishu.card.lifecycle.close_superseded_card
targetRef: zhenzhi_knowledge/feishu.py
before: "project_create_mode sent a new project form card but left the old mode-selection card clickable"
after: "project_create_mode replaces the clicked mode-selection card with a static closed card and sends the new form separately"
policyResult: bot_gateway
---

## Details

The user found that after a new Feishu project creation card was sent, the old card remained visible and clickable. Clicking a superseded card can trigger stale callback state and surface Feishu client errors.

The project creation mode callback now follows a card lifecycle rule:

- replace the clicked choice card with a simple non-clickable closed card;
- send the actual project form as a separate interactive message;
- record callback response diagnostics with `card` and `toast` protocol fields only;
- test that the closed card has no `form` component and no stale `project_create_mode` action.

This pattern was added to the public Feishu card engineering lesson so future card flows close old actionable entries when a new card supersedes them.
