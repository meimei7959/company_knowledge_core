---
type: Workflow
title: AI Native OS Feishu/API and PostgreSQL live technical solution
description: Technical solution for Feishu/API live delivery and PostgreSQL/API route live acceptance gaps.
timestamp: "2026-06-21T12:27:07Z"
solutionId: ts-ai-native-os-feishu-api-postgres-live
taskId: kt-ai-native-os-gap-tech-feishu-api-postgres-live
projectId: company-knowledge-core
ownerAgent: agent.company.development
runnerId: runner.meimei-mac-local-dev-rt
status: draft
sensitivity: internal
sourceRefs:
  - .zhenzhi/context/task.kt-ai-native-os-gap-tech-feishu-api-postgres-live.md
  - projects/company-knowledge-core/tasks/kt-ai-native-os-gap-tech-feishu-api-postgres-live.md
  - projects/company-knowledge-core/product-reviews/ai-native-os-requirement-tree-final-product-acceptance.md
codeRefs:
  - zhenzhi_knowledge/feishu.py
  - zhenzhi_knowledge/server.py
  - zhenzhi_knowledge/core.py
  - tests/test_cli.py
reviewPath: product_and_pm_review
implementationAllowedBeforeReview: false
---

# AI Native OS Feishu/API and PostgreSQL live technical solution

## Decision

This task produces technical solution only. No production implementation is done here.

Frontmatter status stays `draft` to match repository schema. Review state: submitted for Product Manager and Project Manager review through the linked TaskResult.

Implementation remains blocked until Product Manager Agent and Project Manager Agent accept this solution.

## Root cause

The final product acceptance did not reject the object model or local workflow. It rejected launch readiness because two external surfaces still lack live, end-to-end proof:

- Feishu/API live delivery is mostly covered by local handlers and fake senders, but not by a real Feishu app, real message/card delivery, callback retry, permission failure, notification writeback, audit evidence, and human-readable user output.
- PostgreSQL/API route acceptance has a runtime index path and local HTTP server, but live acceptance still has skip risk. Current code can degrade when `DATABASE_URL` is absent, and tests use local server/fake database surfaces instead of a real operational store migration and API route acceptance gate.

Therefore the fix must be systemic across ingress, permission, persistence, audit, notification, API result, observability, rollback, and live evidence. A line-level patch would only hide the acceptance gap.

## Current code baseline

- Feishu event ingress is `handle_feishu_event` in `zhenzhi_knowledge/feishu.py`. It verifies the Feishu token, rejects encrypted events, routes URL verification, approval events, card action events, and `im.message.receive_v1`.
- Message idempotency exists through `claim_feishu_message_event`, `complete_feishu_message_event`, and `fail_feishu_message_event`. It writes event records under the bundle and counts duplicate message callbacks.
- Card action handling exists in `handle_card_action_event`. It normalizes form values, saves card action events, reserves card submit jobs by hash, queues async processing when reply delivery is enabled, and returns duplicate-submit copy.
- Notification and repair primitives exist in `zhenzhi_knowledge/core.py`, including `create_task_notification`, `list_notifications`, `mark_notification_delivery`, and notification repair paths.
- HTTP routes exist in `zhenzhi_knowledge/server.py`. `/integrations/feishu/events` accepts Feishu callbacks before API bearer auth; `/v0/*` routes use bearer token auth when configured. Existing routes cover snapshot, objects, retrieval, audit, tasks, notifications, runner register/heartbeat, task claim/pull/finish, graph, command validation, admin disable, and metrics.
- PostgreSQL runtime store exists as `DATABASE_URL` / `ZHENZHI_KNOWLEDGE_DATABASE_URL`, `connect_database`, and `ensure_database_schema`, currently creating `objects` and `chunks`.
- Tests include local HTTP API/gateway coverage, shared API envelope/safe error coverage, Feishu approval/card/idempotency coverage, notification failure coverage, and PostgreSQL URL validation. These are useful regression tests but not live launch evidence.

## Target acceptance

The implementation program is accepted only when all items below have live evidence:

- A real Feishu app sends a text message to the gateway and receives a human-readable response.
- A real Feishu interactive card is delivered, submitted, retried, and duplicate-submitted without double execution.
- A real Feishu callback with missing/wrong token is rejected, audited, and does not create reusable knowledge or task state.
- A real permission failure, such as missing app scope or missing reviewer/open_id mapping, produces user-readable feedback, NotificationRecord, and AuditLog.
- API routes accept valid bearer token, reject invalid token, return stable safe errors, and write audit/notification state when routes mutate objects.
- PostgreSQL operational store is migrated, writable by the service role, readable by the API route, observable, backupable, and rollbackable.
- Existing skip paths are either removed from the live acceptance suite or converted to explicit blocker evidence. No launch-ready conclusion may rely on skipped live Feishu, live API, or live PostgreSQL tests.

## Architecture

### Feishu live delivery path

1. Feishu sends URL verification or event callback to `POST /integrations/feishu/events`.
2. Gateway verifies `FEISHU_VERIFICATION_TOKEN`. Encrypted events stay blocked unless `FEISHU_ENCRYPT_KEY` support is implemented and tested.
3. Event is normalized into a durable operational event record before business handling.
4. Message events call the existing Feishu response builder, send text or card reply, and write delivery status.
5. Card callbacks reserve an idempotency job, enqueue work once, and return immediate card replacement.
6. Failures write AuditLog, NotificationRecord, and a user-readable response where Feishu permits a response.

### API live delivery path

1. Non-Feishu `/v0/*` routes require `Authorization: Bearer <token>` when API token is configured.
2. Mutating routes normalize command envelopes with actor, project, object, idempotency key, source channel, and requested action.
3. Each mutation writes AuditLog with readable actor/project/object labels.
4. API responses use stable machine fields plus readable `message`, `blockerReason`, and `nextAction`.
5. Gateway and runner routes return enough evidence refs for PM/test agents to verify without digging through raw IDs.

### PostgreSQL operational store

PostgreSQL becomes the live operational acceptance store for API and gateway state, while file bundle remains source-of-truth artifact storage until a later migration decision.

Minimum operational tables:

- `operational_events`: webhook/API event id, source channel, idempotency key, actor, project, target ref, status, error class, readable summary, created/updated timestamps.
- `api_command_envelopes`: command id, route, actor, permission decision, idempotency key, request hash, response hash, audit ref, notification refs.
- `feishu_delivery_attempts`: event id, message id, card id, job key, delivery method, Feishu response code, retry count, final status.
- `migration_versions`: version, applied at, applied by, checksum, rollback notes.

Existing `objects` and `chunks` stay for runtime index/search. Migration must be additive first.

## Implementation slices

### Slice 0: live readiness gate

Scope:

- Add a readiness command or script that validates Feishu env vars, API token, callback URL, PostgreSQL URL, database connection, schema version, API server port, and outbound Feishu API reachability.
- It must not print secrets. It may print only secret presence, secret ref, app id suffix, host, database name, and role name.
- It produces a readiness artifact under project evidence.

Paired test task:

- `kt-ai-native-os-test-feishu-api-postgres-readiness`
- Verify missing Feishu token, missing app secret, wrong Postgres scheme, unavailable DB, missing API token, and happy path against staging.

Acceptance:

- No live implementation task may start unless readiness says `ready` or records an explicit blocker.

### Slice 1: Feishu webhook ingress and token failure

Scope:

- Keep `/integrations/feishu/events` separate from bearer auth, but require Feishu verification token or encryption verification.
- Persist every accepted/rejected callback as `operational_events` and AuditLog.
- Add explicit handling for unsupported encrypted events: clear operator message, audit reason, and follow-up implementation task if encryption is required by the app.

Paired test task:

- `kt-ai-native-os-test-feishu-live-webhook-token`
- Use real Feishu URL verification and a signed/verified live callback. Replay with wrong token and assert 4xx, AuditLog, no task creation, no notification delivery marked sent.

Acceptance:

- Evidence includes Feishu app callback configuration screenshot/export, callback request id, API response, audit ref, and operational event row.

### Slice 2: Feishu real message and card delivery

Scope:

- Send real text response and real interactive card from `send_feishu_incoming_response` / `send_feishu_response_later`.
- Capture Feishu API response code/body summary and map permission failures to readable output.
- Ensure card fallback text path remains available if interactive card send fails.

Paired test task:

- `kt-ai-native-os-test-feishu-live-message-card`
- In a staging chat, send a project/knowledge command, receive a card, submit the card, and verify result card.

Acceptance:

- Evidence includes message id, card job key, delivery attempt row, Feishu delivery status, audit ref, notification ref if a human must be notified, and human-readable final message.

### Slice 3: duplicate callback and idempotent card submit

Scope:

- Preserve current message idempotency and card submit job key behavior.
- Move or mirror idempotency state into PostgreSQL operational tables so duplicate callbacks are safe across process restarts and multiple API instances.
- Define final duplicate behavior:
  - message duplicate returns `duplicate: true`, does not rebuild task/result/knowledge.
  - card duplicate returns already-submitted replacement card, does not rerun submit logic.
  - retry after failed transient send may retry delivery but not duplicate business mutation.

Paired test task:

- `kt-ai-native-os-test-feishu-live-duplicate-callback`
- Replay same Feishu event id/message id/card action at least three times, including concurrent calls if staging allows.

Acceptance:

- Exactly one business mutation, one primary audit action, duplicate counters greater than zero, and user-readable duplicate status.

### Slice 4: permission failures, notifications, and human-readable output

Scope:

- Map Feishu permission failures into typed error classes:
  - app credential invalid
  - bot not in chat
  - missing send message/card scope
  - missing approval scope
  - reviewer/open_id not resolvable
  - project/runner scope denied
- For critical failures, create NotificationRecord for owner/reviewer/submitter and mark delivery pending/failed/sent through `/v0/notifications/delivery`.
- Human-facing output must lead with names, project labels, task titles, and action needed; raw IDs are secondary evidence only.

Paired test task:

- `kt-ai-native-os-test-feishu-live-permission-notification`
- Run at least two real permission failures: one Feishu app scope failure and one project/reviewer mapping failure.

Acceptance:

- Evidence includes Feishu error summary, user-facing output, NotificationRecord, AuditLog, repair/next action, and no secret leakage.

### Slice 5: PostgreSQL operational store migration

Scope:

- Add migration framework and additive migration for operational tables.
- Add `zhenzhi-knowledge db migrate`, `db status`, and `db rollback --to <version>` or equivalent script.
- Enforce least-privilege roles:
  - migration owner role applies DDL.
  - API service role reads/writes operational tables, objects, chunks.
  - read-only observability role reads views only.
- Add migration checksums and rollback notes.

Paired test task:

- `kt-ai-native-os-test-postgres-live-migration`
- Apply migration to staging Postgres, verify schema, insert operational event through API path, run rollback in a cloned/restored staging DB.

Acceptance:

- Evidence includes migration version, schema diff, role grants, backup snapshot id, rollback result, and no destructive rollback on production-like data.

### Slice 6: API route live acceptance

Scope:

- Exercise real HTTP routes against a running server profile, not only in-process tests.
- Required routes:
  - `GET /health`
  - `GET /v0/snapshot`
  - `GET /v0/audit`
  - `GET /v0/notifications`
  - `POST /v0/gateway/context`
  - `POST /v0/knowledge/query`
  - `POST /v0/runners/register`
  - `POST /v0/runners/heartbeat`
  - `POST /v0/tasks/claim`
  - `POST /v0/tasks/pull`
  - `POST /v0/tasks/finish`
  - `POST /v0/notifications/delivery`
  - `POST /v0/command/validate`
- Every mutating route records or references an AuditLog/operational event.
- Invalid bearer token and malformed payload return stable safe errors.

Paired test task:

- `kt-ai-native-os-test-api-route-live-acceptance`
- Run against staging API with real bearer token and Postgres enabled. Include unauthorized, malformed, duplicate idempotency, and success cases.

Acceptance:

- Evidence includes request/response summaries, route coverage table, status codes, audit refs, operational event rows, and zero skipped route checks.

### Slice 7: observability and launch evidence

Scope:

- Add metrics for:
  - Feishu callback accepted/rejected/failed/duplicate.
  - Feishu delivery sent/failed/fallback text sent.
  - API unauthorized/malformed/success/error by route.
  - PostgreSQL migration/schema version/connection latency/write failures.
  - Notification pending/sent/failed/repair created.
- Add launch evidence bundle generator that compiles Feishu, API, Postgres, audit, notification, and rollback proof.

Paired test task:

- `kt-ai-native-os-test-live-evidence-pack`
- Generate launch evidence from staging after slices 1-6.

Acceptance:

- Product Manager can review one evidence pack without reconstructing raw logs.

## Environment readiness

Required staging environment:

- Feishu app id and app secret stored as secret refs, not repository files.
- Feishu verification token configured.
- Feishu event encryption disabled, or encryption key support implemented before live acceptance.
- Feishu app has message, card, approval, and bot chat scopes required by selected scenarios.
- Bot is installed in a staging chat with named human reviewers/testers.
- Public callback URL points to `/integrations/feishu/events` over HTTPS.
- API profile has non-empty bearer token.
- PostgreSQL 14+ or project-approved version with TLS, backup, service role, migration role, and read-only observability role.
- Staging bundle root is separate from local developer bundle.
- Runner `runner.meimei-mac-local-dev-rt` has scope for this technical solution only; live implementation should use its own runner/task leases.

Readiness output must classify each item as `ready`, `blocked`, or `not_required_for_this_slice`.

## Secret handling

- Never write Feishu app secret, verification token, API token, database password, or webhook signing/encryption material into knowledge files, task files, audit details, logs, screenshots, or test output.
- Use secret refs in TaskResult evidence.
- Redact URLs that embed credentials.
- Store only credential presence, secret owner, expiry, environment, and rotation date.

## Rollback

Rollback is per slice:

- Feishu webhook rollback: disable callback URL or route traffic to maintenance endpoint; keep old local/manual intake available.
- Feishu card rollback: disable interactive card send flag and use text fallback.
- Duplicate/idempotency rollback: keep PostgreSQL operational events read-only, fall back to file event records, and block multi-instance live acceptance until fixed.
- Permission/notification rollback: keep audit writes enabled; disable external delivery and mark notifications `pending_retry`.
- PostgreSQL migration rollback: restore from staging backup for destructive test; for production-like data use additive down migration only if it preserves data. Otherwise mark rollback as forward-fix.
- API route rollback: disable new mutating routes by profile or feature flag; keep `GET /health` and read-only diagnostics.
- Evidence rollback: never delete evidence; supersede with new evidence record and audit reason.

Rollback acceptance requires proof that:

- No secret leaked.
- No verified knowledge was promoted by failed live flow.
- Duplicate retries after rollback do not re-execute business mutation.
- Human owner sees readable rollback status and next action.

## Skip elimination strategy

Current local tests may skip when sandbox socket bind is unavailable, and startup can intentionally record `Retrieval skipped: DATABASE_URL is required and must point to PostgreSQL.` These are acceptable local regression behaviors, not launch evidence.

Live acceptance must add a separate no-skip suite:

- Fail immediately if `DATABASE_URL` is absent, wrong scheme, or unreachable.
- Fail immediately if API server cannot bind in staging.
- Fail immediately if Feishu callback URL is not reachable from Feishu.
- Fail immediately if Feishu app lacks required scopes.
- Emit blocker TaskResult if an external permission cannot be granted; do not mark accepted.
- Report skipped local tests separately from live acceptance. Local sandbox skip cannot satisfy AI-NATIVE-OS-PROD-GAP-004 or AI-NATIVE-OS-PROD-GAP-005.

## Paired implementation and test queue

| Order | Development slice | Paired test task | Product evidence |
| --- | --- | --- | --- |
| 0 | readiness gate | `kt-ai-native-os-test-feishu-api-postgres-readiness` | readiness report |
| 1 | Feishu webhook ingress/token failure | `kt-ai-native-os-test-feishu-live-webhook-token` | callback/audit/operational event |
| 2 | real message/card delivery | `kt-ai-native-os-test-feishu-live-message-card` | message/card/result card |
| 3 | duplicate callback/card submit | `kt-ai-native-os-test-feishu-live-duplicate-callback` | one mutation plus duplicate counters |
| 4 | permission failure/notification/readable output | `kt-ai-native-os-test-feishu-live-permission-notification` | NotificationRecord, AuditLog, user copy |
| 5 | Postgres migration/roles/rollback | `kt-ai-native-os-test-postgres-live-migration` | schema, grants, backup, rollback |
| 6 | API route live acceptance | `kt-ai-native-os-test-api-route-live-acceptance` | route coverage, auth, safe errors |
| 7 | launch evidence pack | `kt-ai-native-os-test-live-evidence-pack` | PM-readable evidence bundle |

## Open risks

- Feishu encrypted events are explicitly unsupported in current code. If the enterprise Feishu app requires encryption, encryption support becomes a prerequisite implementation slice.
- Live Feishu approval APIs may require additional tenant scopes or reviewer identity mapping. Treat missing permission as blocker, not degraded success.
- PostgreSQL operational tables introduce dual-write risk while file bundle remains source of truth. Implementation must make file write success and operational event status explicit.
- Multi-instance API deployment needs Postgres-backed idempotency before it can be called live distributed safe.

## PM review checklist

- Does the solution keep implementation blocked until review?
- Are Feishu live message, card, callback retry, permission failure, notification, audit, and human-readable output covered?
- Are PostgreSQL operational store, migration, rollback, permissions, API route live checks, and observability covered?
- Are skip paths eliminated from live acceptance instead of explained away?
- Are paired test tasks clear enough for Test Agent execution?

## Recommendation

Ready for Product Manager and Project Manager technical-solution review. Not ready for implementation until accepted.
