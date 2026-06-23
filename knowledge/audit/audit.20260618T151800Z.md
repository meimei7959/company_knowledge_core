---
type: AuditLog
title: audit.20260618T151800Z
timestamp: "2026-06-18T15:18:00Z"
auditId: audit.20260618T151800Z
actor: codex
action: feishu.card.async_reply.observability_and_submit_button_fix
targetRef: zhenzhi_knowledge/feishu.py
before: "async follow-up card errors were swallowed and submit buttons had no form_action_type"
after: "async follow-up card errors are audited and form buttons include form_action_type submit"
policyResult: bot_gateway
---

## Details

The user clicked the old-project creation mode and saw only a success toast with no follow-up card.

Manual text reply to the same Feishu `open_message_id` succeeded, proving message ID and permissions were valid. Manual interactive-card reply failed with Feishu `HTTP 400`:

```text
Failed to create card content
ErrPath: ROOT -> body -> elements -> [1](tag: form)
ErrMsg: there is no submit button in the form container, at least one
```

Root cause:

- `send_feishu_response_later` swallowed all exceptions, hiding the real Feishu API error.
- The previous minimization removed `form_action_type: submit`, so Feishu no longer considered the form to have a submit button.

Fix:

- restore `form_action_type: submit` on form submit buttons;
- keep the project creation form free of unverified `select_static`;
- pass bundle/action context into async follow-up sends;
- write `feishu.async_reply.sent` and `feishu.async_reply.failed` AuditLog entries so future card send failures include the Feishu response body.
