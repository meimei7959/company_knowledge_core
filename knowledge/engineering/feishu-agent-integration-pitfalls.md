---
type: KnowledgeItem
title: Feishu Bot and Agent Integration Pitfalls
description: Reusable lessons from building Feishu bot approval, identity, notification, and retry handling flows.
timestamp: 2026-06-18T01:49:48Z
owner: codex
status: draft
scope: engineering
sourceRef: feishu-bot-implementation-20260618
confidence: high
knowledgeType: lesson
projectId: company-knowledge-core
tags:
  - feishu
  - bot
  - agent
  - approval
  - idempotency
  - identity
  - notification
---

## Context

When building the knowledge engineering Feishu bot, several issues appeared that are likely to repeat in future Feishu bots or Agent integrations:

- The same Feishu message was processed more than once because Feishu retried the callback.
- A project creation request created duplicate approval documents and duplicate approval instances.
- Approval documents exposed internal IDs such as `user_id`, `open_id`, object paths, and raw statuses to human reviewers.
- Approval creation initially failed because the Feishu approval API requires the correct identity field semantics.
- Approval success updated internal state but did not notify the requester.

These are not isolated bugs. They are integration lifecycle problems.

## Root Causes

1. External callback systems retry delivery.

Feishu may retry event callbacks after a delay. If the bot treats every callback as new work, repeated delivery causes repeated side effects.

2. Message handling was not idempotent.

The first implementation used `message_id` only for replying, not as a persistent deduplication key. Business actions such as project creation, document creation, and approval creation were executed again on retry.

3. Identity values were mixed across API boundaries.

Feishu messaging APIs, approval APIs, contact APIs, and document permission APIs may require different identity fields. For example:

- message reply uses message ID;
- direct message sending uses `open_id`;
- approval creation request body uses `user_id`;
- document permission sharing uses `open_id`.

Using a valid ID in the wrong field still fails or produces unreadable output.

4. Human-facing documents were generated from internal system values.

Reviewers need names, labels, business meaning, and concise summaries. Internal IDs and paths are useful only as secondary system information.

5. Callback result handling stopped at internal state changes.

After approval callbacks, the system updated status and AuditLog but did not notify the submitter. A complete lifecycle must include user notification.

## Systemic Solution Pattern

Use this pattern for Feishu bots, approval bots, and Agent webhook integrations.

### 1. Define the lifecycle before coding

For each incoming event, define:

- unique external event key;
- internal idempotency key;
- side effects;
- human-facing reply;
- approval or review path;
- callback handling;
- audit record;
- user notification.

### 2. Add persistent idempotency

Use the external event ID as a durable key.

For Feishu message events:

- use `message.message_id` as the idempotency key;
- persist a processing record before side effects;
- on duplicate delivery, return success immediately;
- do not create objects, documents, approvals, or replies again.

Recommended states:

- `processing`
- `completed`
- `failed`
- `completed_legacy`

For systems already running before idempotency is added, also check historical AuditLog records so old retried messages are treated as already processed.

### 3. Map identities explicitly

Do not pass one identity type through all APIs blindly.

Maintain an explicit conversion layer:

- `open_id` for Feishu IM send/share APIs where required;
- `user_id` for approval form contact fields and approval instance creation where required;
- display name for human-facing documents and messages;
- raw IDs only in system information sections.

### 4. Generate reviewer-first documents

Approval documents must answer:

- What is being approved?
- Which project or business object is affected?
- Who submitted it?
- Who owns it?
- What changes if approved?
- What evidence or source material supports it?
- Are there conflicts or risks?

Place paths, internal IDs, and raw statuses in a `System Information` section at the end.

### 5. Notify the requester after callback completion

Approval callbacks should:

- verify the instance code and approval code;
- handle idempotency for repeated approval callbacks;
- update the target object status;
- write AuditLog;
- notify the submitter of approval or rejection;
- include useful links, project ID, and final status.

### 6. Test the whole lifecycle

Do not only test the failing line.

Minimum tests:

- first delivery creates exactly one set of side effects;
- retry of the same message creates no new side effects;
- retry after old AuditLog exists is also deduplicated;
- approval callback updates state once;
- repeated approval callback is idempotent;
- requester notification is sent once;
- human-facing document contains names and labels, not only IDs.

## Applies When

Use this lesson when building:

- Feishu bots;
- approval workflows;
- webhook-based Agents;
- local or hosted Agent gateways;
- any integration that receives external callbacks and creates side effects;
- any workflow where a human reviews an Agent-generated document.

## Checklist

- [ ] Did we identify the root cause before fixing?
- [ ] Is there a durable idempotency key?
- [ ] Are side effects guarded by idempotency?
- [ ] Are retries acknowledged without repeating work?
- [ ] Are identity types mapped per API?
- [ ] Are human-facing documents readable by non-developers?
- [ ] Are raw IDs kept as secondary system information?
- [ ] Does callback handling update state, audit, and notify users?
- [ ] Are lifecycle tests added?
- [ ] Was the real external API path verified where relevant?

