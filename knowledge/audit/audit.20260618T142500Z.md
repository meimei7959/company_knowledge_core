---
type: AuditLog
title: audit.20260618T142500Z
timestamp: "2026-06-18T14:25:00Z"
auditId: audit.20260618T142500Z
actor: codex
action: feishu.card.callback_flow.fix
targetRef: zhenzhi_knowledge/feishu.py
before: "project_create_mode callback updated the clicked card directly into a complex form card"
after: "project_create_mode callback returns toast only and sends the complex form as a separate interactive reply"
policyResult: bot_gateway
---

## Details

The live Feishu client still showed `code: 200530` for a newly generated project creation card.

Server evidence showed the callback reached the API and returned HTTP 200. The card event record showed a clean callback response shape, but the failing action was `project_create_mode`, which attempted to update the clicked card directly into a complex form card.

The flow now avoids complex callback card updates:

- The callback response returns only a Toast.
- The next project form is sent as a separate interactive bot reply.
- Tests assert that the callback response has only `toast` and that the follow-up card is sent through `send_feishu_response`.
