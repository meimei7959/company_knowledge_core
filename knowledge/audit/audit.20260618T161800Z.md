---
type: AuditLog
title: audit.20260618T161800Z
timestamp: "2026-06-18T16:18:00Z"
auditId: audit.20260618T161800Z
actor: codex
action: feishu.card.submit_async_ack_fix
targetRef: zhenzhi_knowledge/feishu.py
before: "card submit callback executed project creation and approval synchronously before acknowledging Feishu"
after: "card submit callback queues an idempotent background job and immediately returns a toast"
policyResult: bot_gateway
---

## Details

The user saw a red Feishu client error first, then later received a successful project creation card and approval notification.

Root cause:

- Feishu card submit has two paths: the immediate card callback acknowledgement and later bot replies.
- The server received the submit event and completed the business work, but the immediate callback path was too heavy because it created the project draft, wrote files, created an approval document, and called Feishu approval before returning.
- Feishu client treated the callback acknowledgement as failed, while the backend business path continued and later sent a success card.

Fix:

- In production reply mode, form submit callbacks now reserve an idempotent `.zhenzhi/feishu-card-jobs/<hash>.json` job.
- The callback immediately returns a toast: `已收到，正在后台处理。完成后我会发结果卡。`
- The background job runs the original submit business logic and sends the final success/failure card.
- Offline/tests with replies disabled still run synchronously so existing deterministic CLI tests remain stable.

Acceptance check:

- Added a test that verifies project creation submit returns immediately when replies are enabled.
- Existing project creation tests still pass.
