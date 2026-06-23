---
type: KnowledgeItem
title: Feishu interactive card implementation runbook after Agent Hub incident
description: End-to-end implementation path and failure checklist for Feishu bot interactive cards, based on the Agent Hub project creation card incident.
timestamp: 2026-06-18T16:45:00Z
owner: codex
status: draft
scope: engineering
sourceRef: feishu-card-agent-hub-incident-20260618
confidence: high
knowledgeType: runbook
projectId: company-knowledge-core
tags:
  - feishu
  - card
  - bot
  - callback
  - approval
  - async-job
  - runbook
evidenceRefs:
  - knowledge/engineering/feishu-card-json-v2-form-pattern.md
  - knowledge/audit/audit.20260618T151800Z.md
  - knowledge/audit/audit.20260618T160500Z.md
  - knowledge/audit/audit.20260618T161800Z.md
  - knowledge/audit/audit.20260618T163200Z.md
---

## Summary

2026-06-18 晚上，Agent Hub 的“创建项目”飞书交互卡连续出现多类问题：

- 卡片没有发出来，只看到成功提示。
- 卡片能渲染，但点击提交时报 `200530`。
- 改完按钮后又出现 `200341`。
- 用户先看到红色报错，随后又收到“项目草稿创建成功”卡片。
- 项目草稿创建成功后，审批通过缺少明确的结果通知卡。

最后跑通的正确路径是：

1. 卡片选择动作只做轻量回调，下一张复杂表单卡通过机器人消息异步发送。
2. 表单 submit 按钮只使用 `name + form_action_type + value`，不要混用 `behaviors: callback`。
3. 后端同时从 `action.value.action` 和 `action.name` 解析动作。
4. 飞书 callback 必须快速返回 `toast`，真正业务处理放入幂等后台 job。
5. 后台 job 完成后再发结果卡。
6. 审批通过/拒绝后也要发独立的结果卡；卡片失败时退回文本通知并写审计。

## What Went Wrong

### 1. Async card send failure was invisible

用户点击“已有仓库接入/老项目迁移”后，飞书只显示成功 toast，但没有出现后续表单卡。

根因：

- 后续表单卡是异步发送的。
- 异步线程吞掉了 Feishu OpenAPI 的 HTTP 错误。
- 没有审计记录，导致只能从用户截图猜问题。

正确做法：

- 所有异步发卡必须捕获 `HTTPError`。
- 审计里写入 Feishu 返回的错误体。
- 不要只记录 Python exception message。

### 2. Card JSON 2.0 is strict

本次遇到的真实 Feishu schema 错误包括：

- `input.multiline` 不被接受。
- `input.required` 在当前 JSON 2.0 形态下不稳定。
- `select_static.initial_option` 必须是字符串 value，不能是 option 对象。
- `select_static.label` 不被接受。
- `form` 容器里必须有合法 submit button。

正确做法：

- 表单先只用最小稳定组件：`input` + `button`。
- `select_static` 只有在真实飞书环境验证过后再引入。
- 不要从旧卡片示例或不同版本文档直接复制字段。

### 3. Do not mix submit and callback on one button

最关键的按钮错误：

```json
{
  "tag": "button",
  "form_action_type": "submit",
  "value": {
    "action": "project_create_submit"
  },
  "behaviors": [
    {
      "type": "callback",
      "value": {
        "action": "project_create_submit"
      }
    }
  ]
}
```

这个形态能渲染，但点击后飞书客户端可能直接报 `200530` 或 `200341`，事件甚至不到后端。

正确做法参考 AgentWork 的稳定实现：

```json
{
  "tag": "button",
  "text": {
    "tag": "plain_text",
    "content": "开始接入"
  },
  "type": "primary",
  "name": "project_create_submit|repoMode=existing",
  "form_action_type": "submit",
  "value": {
    "action": "project_create_submit",
    "repoMode": "existing"
  }
}
```

规则：

- form submit button 不要写 `behaviors`。
- 固定参数编码进 `name`。
- `value` 可以保留，但后端不能只依赖 `value.action`。

### 4. Callback acknowledgement and business result are two channels

用户看到“红色报错后又成功”，不是业务失败后又成功，而是两个通道表现不一致：

- 飞书按钮 callback 通道：客户端要求服务器快速返回合规响应。
- 机器人消息通道：后端业务处理完成后主动发结果卡。

之前的问题是：

- callback 里同步执行了创建项目、写启动清单、发审批等重活。
- callback 响应慢或不稳定，飞书客户端弹红色错误。
- 后端业务仍继续执行，所以后来又发了成功卡。

正确做法：

- callback 只做校验、幂等 job 预占、返回 `toast`。
- 业务逻辑放后台 job。
- job 完成后用机器人消息 API 发“已提交/失败”结果卡。

### 5. Project approval also needs result notification

项目创建卡提交成功后，只发“项目草稿创建成功”不够。

审批通过/拒绝是另一个业务节点，也必须通知：

- 提交人收到审批结果卡。
- 项目 Owner 收到项目已立项 onboarding 卡。
- 如果卡片通知失败，退回文本通知并写审计。

## Correct Implementation Path

### Step 1. Build a minimal stable form card

Use JSON 2.0:

```json
{
  "schema": "2.0",
  "config": {
    "wide_screen_mode": true
  },
  "header": {
    "template": "blue",
    "title": {
      "tag": "plain_text",
      "content": "已有仓库接入"
    }
  },
  "body": {
    "direction": "vertical",
    "elements": [
      {
        "tag": "markdown",
        "content": "只填 Git 地址和项目 Owner。其他信息会自动推断或后续补齐。"
      },
      {
        "tag": "form",
        "name": "form_main",
        "elements": [
          {
            "tag": "input",
            "name": "repoUrl",
            "element_id": "repoUrl",
            "label": {
              "tag": "plain_text",
              "content": "Git 地址"
            },
            "placeholder": {
              "tag": "plain_text",
              "content": "例如：https://github.com/company/project.git"
            },
            "default_value": ""
          },
          {
            "tag": "button",
            "text": {
              "tag": "plain_text",
              "content": "开始接入"
            },
            "type": "primary",
            "name": "project_create_submit|repoMode=existing",
            "form_action_type": "submit",
            "value": {
              "action": "project_create_submit",
              "repoMode": "existing"
            }
          }
        ]
      }
    ]
  }
}
```

### Step 2. Parse form submit defensively

Backend action resolution order:

1. `event.action.value.action`
2. `event.action.form_value.action`
3. parsed action from `event.action.name`

For button name:

```text
project_create_submit|repoMode=existing
```

parse into:

```json
{
  "action": "project_create_submit",
  "repoMode": "existing"
}
```

### Step 3. Keep callback response protocol-clean

Callback response should be minimal:

```json
{
  "toast": {
    "type": "success",
    "content": "已收到，正在后台处理。完成后我会发结果卡。"
  }
}
```

Do not return local debug fields:

```json
{
  "ok": true,
  "handled": "project_create_submit",
  "cardData": {}
}
```

### Step 4. Queue an idempotent background job

Use a job key based on:

- open message id
- action name
- normalized submitted form

Persist job metadata before starting work:

```text
.zhenzhi/feishu-card-jobs/<hash>.json
```

Job statuses:

- `queued`
- `running`
- `done`
- `failed`

If the same card is submitted again, return:

```text
这张卡已经提交过了，我正在处理或已经处理完成，请等结果卡。
```

Do not create another project or approval.

### Step 5. Send result card after the job finishes

Success card should contain business output:

- project name
- project id
- launch file path
- repository status
- approval instance
- approval document URL
- next steps

Failure card should contain:

- user-readable reason
- what to fix
- whether retry is safe

### Step 6. Notify approval result separately

Approval callbacks must trigger a new notification card.

Submitter card:

- title: `项目立项审批已通过` or `项目立项审批未通过`
- project name
- project id
- target file
- approval instance
- approval document
- next steps

Project Owner card on approved project init:

- title: `你负责的项目已立项：<项目名>`
- project id
- how to record meeting notes
- how to record project material
- how AgentRun and decisions should be written back

If interactive card sending fails:

1. send plain text fallback;
2. write `feishu.approval.notify_card_failed_text_fallback_sent`;
3. if fallback also fails, write `feishu.approval.notify_failed`.

## Diagnostic Decision Tree

### User sees no card after clicking

Check:

- Did callback event reach backend?
- Did async send write `feishu.async_reply.sent` or `feishu.async_reply.failed`?
- Does the failed audit include Feishu HTTP response body?

Likely cause:

- follow-up card send failed after callback returned.

### User sees card, click reports `200530` or `200341`

Check:

- Did `project_create_submit` reach backend?
- Is there any `.zhenzhi/feishu-card-events` record for the submit?

If no backend event exists:

- card JSON or button action shape is wrong;
- check for `behaviors` mixed with `form_action_type`;
- check unsupported fields in `input` / `select_static`.

If backend event exists:

- callback response shape or latency is wrong;
- callback must return protocol-clean toast quickly.

### User sees red error but later success card

Cause:

- business job completed;
- callback acknowledgement failed or timed out.

Fix:

- move business processing out of callback;
- return toast immediately;
- send success/failure as separate bot message.

### Draft success card appears but approval result is silent

Cause:

- project creation result and approval result are separate lifecycle events.

Fix:

- approval callback must send its own result card;
- owner onboarding must be sent after approved project init.

## Required Tests

Every Feishu interactive card feature must include tests for:

1. Card JSON does not contain unsupported fields.
2. Form submit button has `form_action_type`.
3. Form submit button does not contain `behaviors`.
4. Submit action can be parsed from `action.name`.
5. Production callback path with replies enabled returns immediately and queues a job.
6. Duplicate submit does not create duplicate business objects.
7. Job success sends a result card.
8. Job failure sends a failure card.
9. Approval result sends an interactive result card.
10. Card notification failure falls back to text and writes audit.

## Operational Rules For Future Agents

- Never implement Feishu cards only from local unit tests.
- Always verify one real Feishu send path before declaring success.
- Always distinguish:
  - callback acknowledgement;
  - follow-up card send;
  - background business job;
  - approval callback;
  - approval result notification.
- Never run heavy business logic inside Feishu card callback.
- Never swallow Feishu HTTP response bodies.
- Never expose raw internal IDs as the main user-facing instruction when a readable name exists.
- Do not ask users to click old cards after changing card JSON. Old cards keep old JSON.

## Current Project Reference

Implemented in:

- `zhenzhi_knowledge/feishu.py`
  - `submit_button`
  - `parse_form_submit_name`
  - `handle_card_action_event`
  - `start_card_submit_job`
  - `run_card_submit_job`
  - `notify_approval_result`
  - `send_feishu_direct_response`
- `tests/test_cli.py`
  - `test_feishu_project_create_submit_returns_immediately_when_replies_enabled`
  - `test_project_approval_sends_interactive_result_cards`
  - `test_project_owner_notification_failure_notifies_submitter`

Related reusable pattern:

- `knowledge/engineering/feishu-card-json-v2-form-pattern.md`
