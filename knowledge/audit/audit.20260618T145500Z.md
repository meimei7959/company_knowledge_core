---
type: AuditLog
title: audit.20260618T145500Z
timestamp: "2026-06-18T14:55:00Z"
auditId: audit.20260618T145500Z
actor: codex
action: feishu.card.callback_async_boundary.fix
targetRef: zhenzhi_knowledge/feishu.py
before: "card callbacks synchronously sent follow-up cards and some paths returned callback card updates"
after: "card callbacks return toast-only responses and send follow-up cards asynchronously"
policyResult: bot_gateway
---

## Details

The user reported that Feishu still showed `code: 200530` after clicking the project creation mode card, even though the bot sent the next project form card.

Server evidence showed the failing live event was `project_create_mode` and the callback had already reached the API. This means the visible failure was likely caused by the synchronous card callback path itself, not by the project intake business logic.

The Feishu card callback boundary is now stricter:

- `card.action.trigger` returns only a short `toast`;
- complex form cards and result cards are sent as asynchronous follow-up replies;
- the project group select no longer preselects `后续确认`, so the visible placeholder keeps the field meaning: `项目群协作：是否需要...`;
- repeated clicks on an old mode-selection card are idempotent and should send a fresh form instead of entering a stale flow.

The reusable Feishu card engineering lesson was updated to avoid synchronous OpenAPI sends or callback card updates in the callback response path.
