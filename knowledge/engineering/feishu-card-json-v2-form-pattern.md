---
type: KnowledgeItem
title: Feishu Card JSON 2.0 Form Pattern
description: Reusable lessons for building Feishu interactive form cards that submit field values through card.action.trigger.
timestamp: 2026-06-18T13:18:27Z
owner: codex
status: draft
scope: engineering
sourceRef: feishu-card-debug-20260618
confidence: high
knowledgeType: lesson
projectId: company-knowledge-core
tags:
  - feishu
  - card
  - bot
  - callback
  - form
  - json-v2
---

## Context

When building the Agent Hub Feishu bot, the bot received `创建项目` messages correctly but sending an interactive card reply failed with Feishu `HTTP 400`.

The visible symptom was that the user saw no card response or only the text fallback.

The first failure was in the Feishu reply API while creating card content.

A later failure appeared after the card rendered successfully: the user clicked a card button and Feishu showed `code: 200530`. The bot business logic was not the only thing to validate; the card callback response itself also had to match Feishu's callback protocol exactly.

## Evidence

- Official callback documentation: https://open.feishu.cn/document/feishu-cards/card-callback-communication.md
- Official card entity documentation: https://open.feishu.cn/document/cardkit-v1/card/create.md
- Real Feishu API error:
  - `unknown property, property: multiline, path: ROOT -> body -> elements -> [1](tag: input)`
  - `expected string for initial_option, but: map[text:map[content:已有仓库接入 tag:plain_text] value:existing]`
  - `unknown property, property: label, path: ROOT -> body -> elements -> [5](tag: select_static)`
  - `formActionType only in form`
- Live smoke result after fixes:
  - `send_feishu_response(... project_create_card("existing") ...)`
  - result: `sent ok`
- Official callback response requirement:
  - `card.action.trigger` callback responses support `toast` and `card`.
  - For JSON cards, `card` must be shaped as `{"type": "raw", "data": <card JSON 2.0>}`.
  - Internal diagnostic keys such as `ok`, `handled`, and `cardData` must not be returned to Feishu.
- Live `code: 200530` still occurred when a mode-selection callback tried to update the original card into a complex form card.
  - Server logs showed Feishu reached the endpoint and received HTTP 200.
  - `.zhenzhi/feishu-card-events/` showed clean response keys.
  - A later live event still showed `code: 200530` even when the callback returned only a toast, because the callback synchronously called the Feishu reply API before returning.
  - The robust fix is to keep the card callback response minimal and fast, then send the complex form or result card asynchronously as a separate bot reply.

## Root Cause

Feishu card JSON 2.0 is strict. Fields that are tolerated by local tests or copied from old card examples may be rejected by the Feishu API.

The broken card had four schema mistakes:

1. `input.multiline` is not accepted.
2. `input.required` is not accepted in the tested card JSON 2.0 shape.
3. `select_static.initial_option` must be a string option value, not an option object.
4. `select_static.label` is not accepted.
5. A button with `form_action_type: submit` must be inside a `form` container.

The second broken layer was the callback response boundary:

1. The HTTP endpoint returned a mixed object intended for local debugging.
2. The mixed object contained the official `toast` and `card` fields plus internal keys.
3. Feishu card callbacks must receive the official callback response shape only.
4. Local tests asserted internal debug fields instead of asserting the actual Feishu protocol response.

The third broken layer was using callback card update for complex form transitions:

1. Mode selection returned a new card with a `form` container directly in the callback response.
2. Feishu accepted the HTTP request but the client still showed `code: 200530`.
3. The safer pattern is to keep callback responses minimal and send the next complex form as a separate interactive message or reply.

The fourth broken layer was callback latency and old card lifecycle:

1. The mode-selection callback sent the next form card through the Feishu reply API before returning its callback response.
2. The user saw the next form card, but the Feishu client still showed `code: 200530`.
3. Treat card callbacks as a short acknowledgement path only.
4. Long work, Feishu OpenAPI sends, result cards, and follow-up forms should run after the callback response has been returned.
5. Old cards should be made harmless and idempotent. Do not try to close an old card through the same synchronous callback until that update path is live-verified.

The fifth broken layer was a render-valid but submit-invalid form shape:

1. The project form card rendered in Feishu, but clicking the submit button still showed `code: 200530`.
2. Server event records showed no `project_create_submit` callback after the click.
3. Therefore the failure happened in the Feishu client before the request reached the bot.
4. Removing `form_action_type: submit` made the follow-up card fail to send with Feishu `HTTP 400`: `there is no submit button in the form container, at least one`.
5. The stabilized shape is: plain `input` fields, no unverified `select_static`, and a button inside the form with `form_action_type: submit`.
6. Async follow-up card failures must be audited with Feishu's response body. Do not swallow `HTTPError`.
7. Do not mix `form_action_type: submit` and `behaviors: callback` on the same form submit button. A known working AgentWork implementation uses a submit button with `name`, `form_action_type`, and `value`, but no `behaviors`.
8. The server should parse the submitted action from both `action.value.action` and button `action.name`. Encode fixed submit params into `name`, e.g. `project_create_submit|repoMode=existing`, because Feishu form submit may not preserve all button `value` fields consistently.

## Working Pattern

Use card JSON 2.0.

Put display text outside the form. Put all fields and the submit button inside one `form` component.

Use `name` on each field so Feishu returns submitted values in `action.form_value`.

Minimal shape:

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
      "content": "创建项目启动卡"
    }
  },
  "body": {
    "direction": "vertical",
    "elements": [
      {
        "tag": "markdown",
        "content": "填写后提交。"
      },
      {
        "tag": "form",
        "element_id": "form_main",
        "name": "form_main",
        "elements": [
          {
            "tag": "input",
            "name": "projectName",
            "element_id": "projectName",
            "label": {
              "tag": "plain_text",
              "content": "项目名称"
            },
            "placeholder": {
              "tag": "plain_text",
              "content": "请输入项目名称"
            },
            "default_value": ""
          },
          {
            "tag": "select_static",
            "name": "repoMode",
            "element_id": "repoMode",
            "placeholder": {
              "tag": "plain_text",
              "content": "仓库类型：请选择"
            },
            "options": [
              {
                "text": {
                  "tag": "plain_text",
                  "content": "已有仓库接入"
                },
                "value": "existing"
              }
            ],
            "initial_option": "existing"
          },
          {
            "tag": "button",
            "text": {
              "tag": "plain_text",
              "content": "提交"
            },
            "type": "primary",
            "name": "project_create_submit|repoMode=existing",
            "form_action_type": "submit",
            "value": {
              "action": "project_create_submit"
            }
          }
        ]
      }
    ]
  }
}
```

## Callback Handling

Configure Feishu callback:

- callback type: `card.action.trigger`
- request URL: the same bot event endpoint can be used if routing handles event type correctly.

The callback payload returns:

- `event.action.value`: custom button value.
- `event.action.form_value`: submitted form values keyed by component `name`.

The server must respond within 3 seconds.

Callback response must be protocol-clean.

Keep callback handling shallow:

- Return a `toast` immediately after validating the callback shape.
- Do not create projects, write large files, call approval APIs, parse documents, or send result cards before returning the callback response.
- Put slow work into an idempotent background job keyed by the card message, action, and submitted form hash.
- Send the final result as a separate bot reply after the job finishes.
- A red Feishu client error followed by a later success card means the callback acknowledgement path failed or timed out while the business path still completed.

For simple result cards, a raw card response is acceptable:

```json
{
  "toast": {
    "type": "success",
    "content": "已提交"
  },
  "card": {
    "type": "raw",
    "data": {
      "schema": "2.0",
      "config": {
        "wide_screen_mode": true,
        "update_multi": true
      },
      "header": {
        "template": "green",
        "title": {
          "tag": "plain_text",
          "content": "已提交"
        }
      },
      "body": {
        "direction": "vertical",
        "elements": []
      }
    }
  }
}
```

Do not return local-only fields such as:

```json
{
  "ok": true,
  "handled": "project_create_submit",
  "cardData": {}
}
```

Persist callback diagnostics separately. Store at least event type, action name, form keys, response keys, response card type, and hashes of submitted values. Do not rely on Feishu chat UI screenshots as the only evidence.

For transitions that produce a complex form card, prefer this two-step pattern:

1. Callback response:

```json
{
  "toast": {
    "type": "success",
    "content": "已收到，正在发送新的项目启动卡。"
  }
}
```

2. Server-side asynchronous follow-up message:

```json
{
  "msg_type": "interactive",
  "card": {
    "schema": "2.0",
    "body": {
      "elements": [
        {
          "tag": "form",
          "elements": []
        }
      ]
    }
  }
}
```

This avoids forcing Feishu to update the clicked card or call the reply API during the synchronous callback.

## Debugging Procedure

Do not debug card failures only from the chat UI. The UI may look like "no response".

Use this sequence:

1. Check whether the Feishu message event reached the server.
2. Check the persisted event record for `replyError`.
3. For card clicks, check `.zhenzhi/feishu-card-events/` and confirm the request reached the server.
4. If the request reached the server but Feishu still errors, validate the HTTP response body against official `card.action.trigger` callback response shape.
5. If Feishu returns `HTTP 400`, capture and persist the response body.
6. Fix the exact schema error named by Feishu.
7. Run local tests that assert the real callback response, not internal debug fields.
8. Deploy.
9. Run a live smoke using the real Feishu reply API and a real callback click when possible.
10. Keep a text fallback so the user is not left with silence if card delivery fails.

## Guardrails

- Do not put unverified properties into card JSON.
- Do not assume Card JSON 1.0 examples work in Card JSON 2.0.
- Do not put `form_action_type: submit` on a button outside a `form`.
- Do not use object-shaped `initial_option` for `select_static`; use the option value string.
- Add fallback text for every interactive card response.
- Persist Feishu error body, not only `HTTP Error 400`.
- Card callback responses must return only official protocol fields.
- Keep internal diagnostics in audit files or `.zhenzhi/feishu-card-events/`, not in the callback HTTP response.
- Do not use callback card update for complex form-to-form transitions; return a toast and send the next form as a separate asynchronous bot message.
- Do not call Feishu reply/update APIs synchronously inside the card callback path.
- If a new card supersedes an old interactive card, make repeated old-card clicks idempotent first. Close or replace the old card only through a separately verified update path.
- For `select_static`, avoid preselecting a default option when the visible label would disappear. Use a label-like placeholder such as `项目群协作：是否需要创建项目群`.
- A form container must include at least one button with `form_action_type: submit`; otherwise Feishu rejects the card content.
- Prefer plain `input` fields for the first live-verified form. Add `select_static` only after the plain form can be submitted end-to-end.
- If a card renders but clicking submit produces `code: 200530` and no event file appears, treat the card JSON submit shape as invalid even if message sending succeeded.
- If async card sending fails, persist Feishu's HTTP error body in AuditLog before returning success to the user.

## Applies When

Use this pattern when building:

- Feishu bot interactive cards.
- Agent Hub menu cards.
- Project intake forms.
- Knowledge intake forms.
- Tool or skill request cards.
- Any card that must return structured field values to a bot gateway.
