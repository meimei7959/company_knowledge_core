---
type: AuditLog
title: audit.20260618T160500Z
timestamp: "2026-06-18T16:05:00Z"
auditId: audit.20260618T160500Z
actor: codex
action: feishu.card.submit_button_align_with_agentwork
targetRef: zhenzhi_knowledge/feishu.py
before: "form submit buttons mixed form_action_type submit with behaviors callback"
after: "form submit buttons follow AgentWork pattern with name, form_action_type and value only"
policyResult: bot_gateway
---

## Details

The user reported that the newly rendered project creation form still failed in the Feishu client with `code: 200530` when clicking the submit button.

The referenced AgentWork implementation uses Feishu JSON 2.0 form cards with:

- a `form` container;
- `input` fields with `name`;
- a submit `button` with `name`, `form_action_type: submit`, and `value`;
- no `behaviors` callback on the submit button.

Root cause hypothesis:

- The previous project form submit button mixed two action mechanisms on one button: `form_action_type: submit` and `behaviors: callback`.
- Feishu rendered the card but failed on client-side submit before the bot received a `project_create_submit` event.

Fix:

- remove `behaviors` from form submit buttons;
- encode fixed submit params into button `name`, e.g. `project_create_submit|repoMode=existing`;
- parse action and fixed params from `action.name` on the server when `action.value.action` is absent;
- update tests and the reusable Feishu card pattern knowledge.
