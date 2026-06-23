---
type: AuditLog
title: audit.20260618T150800Z
timestamp: "2026-06-18T15:08:00Z"
auditId: audit.20260618T150800Z
actor: codex
action: feishu.card.submit_schema.minimize
targetRef: zhenzhi_knowledge/feishu.py
before: "project creation form mixed form_action_type submit, callback behavior, and select_static in one form"
after: "project creation form uses plain input fields and a single callback button submit path"
policyResult: bot_gateway
---

## Details

The user reported repeated Feishu `code: 200530` after clicking the project creation form.

Server evidence showed recent live failures created `project_create_mode` records but no `project_create_submit` records. The bot therefore never received the submit event. This points to a card client/schema submit failure rather than project creation business logic.

The card is simplified to isolate and stabilize the submit path:

- remove `form_action_type: submit` from the submit button;
- keep only the proven `behaviors: callback` path;
- still keep the submit button inside the form so field values can be collected;
- replace the `select_static` project group control with a plain optional input;
- keep card callback responses toast-only and follow-up cards asynchronous.

The Feishu card engineering lesson was updated with the rule: render-success is not submit-success; if no callback event reaches the server, treat the card submit JSON shape as invalid.
