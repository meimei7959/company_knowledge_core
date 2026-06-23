---
type: AuditLog
title: audit.20260618T163200Z
timestamp: "2026-06-18T16:32:00Z"
auditId: audit.20260618T163200Z
actor: codex
action: feishu.project_approval_result_card_notification
targetRef: zhenzhi_knowledge/feishu.py
before: "project approval result notification used plain text only and could be missed after project draft creation"
after: "project approval callbacks send interactive result cards to submitter and project owner with text fallback"
policyResult: bot_gateway
---

## Details

Project creation already sent a draft-created result card, but approval pass/fail needed its own explicit notification.

Fix:

- Add direct Feishu response sending by `open_id` for both text and interactive cards.
- Project approval result now sends an interactive card to the submitter.
- Project owner onboarding now sends an interactive card when the project init approval is approved.
- If interactive card sending fails, notification falls back to text and writes an audit record.

Checks:

- `test_project_approval_sends_interactive_result_cards`
- `test_project_owner_notification_failure_notifies_submitter`
- project creation async callback tests still pass.
