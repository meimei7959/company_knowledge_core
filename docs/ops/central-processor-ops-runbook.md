# Central Processor Ops Runbook

## Purpose

This runbook is for operating the Company Knowledge Core central processor after Feishu, DeepSeek, and Agent Ring integration.

It covers deployment, health checks, logs, Feishu card/callback diagnostics, DeepSeek router diagnostics, and task runtime inspection. It must not contain secret values.

## Runtime Configuration

Server environment variables:

```txt
ZHENZHI_KNOWLEDGE_API_TOKEN
FEISHU_APP_ID
FEISHU_APP_SECRET
FEISHU_VERIFICATION_TOKEN
FEISHU_CALLBACK_URL
FEISHU_ALLOW_UNSIGNED_EVENTS
FEISHU_REPLY_ENABLED
DATABASE_URL
ZHENZHI_KNOWLEDGE_API_PORT
FEISHU_DEEPSEEK_ROUTER_ENABLED
DEEPSEEK_API_KEY
DEEPSEEK_API_BASE
DEEPSEEK_MODEL
DEEPSEEK_TIMEOUT_SECONDS
DEEPSEEK_INPUT_PRICE_PER_1M
DEEPSEEK_OUTPUT_PRICE_PER_1M
ZHENZHI_KNOWLEDGE_BACKUP_REF
ZHENZHI_KNOWLEDGE_PG_DUMP_REF
```

Rules:

- Store real values only in server env, `.env`, or secret storage.
- Do not write token values, cookies, private keys, or model keys into knowledge files, task files, audit details, screenshots, or docs.
- The bundle may store only secret refs, owners, scopes, expiry, and audit records.

## Deploy

Deploy to Lighthouse:

```bash
bash deploy/lighthouse/deploy.sh
```

Expected behavior:

- syncs repository files to `/opt/projects/company_knowledge_core/repo`;
- syncs `deploy/lighthouse/.env` to the server deployment directory;
- runs Docker Compose for container `zhenzhi-knowledge-api`;
- binds the app to `127.0.0.1:8765`;
- exposes public route `/knowledge-api/` through Nginx when the Agent Work site config exists.

The deploy script rejects missing `.env` and `ZHENZHI_KNOWLEDGE_API_TOKEN=CHANGE_ME`.

## Health Check

Local server:

```bash
python3 -m zhenzhi_knowledge --root /Users/meimei/Documents/company_knowledge_core api serve --host 127.0.0.1 --port 8765
```

Production health URL:

```txt
http://124.221.138.151/knowledge-api/health
```

Healthy response:

```json
{"ok": true, "problems": []}
```

If `ok` is false, the `problems` list is the first diagnostic source. `/health` runs bundle validation and operational-store status, so schema, status, frontmatter, category, and PostgreSQL problems should appear there before debugging Feishu or Agent Ring.

## Feishu/API/PostgreSQL Live Readiness

Run readiness before claiming live evidence:

```bash
python3 scripts/ops/postgres_live_ops.py --root /Users/meimei/Documents/company_knowledge_core readiness --migrate
```

From staging network, include the Feishu API probe:

```bash
python3 scripts/ops/postgres_live_ops.py --root /Users/meimei/Documents/company_knowledge_core readiness --migrate --check-feishu-api
```

Expected ready output:

```json
{"status": "ready", "artifactRef": ".zhenzhi/evidence/feishu-api-postgres-readiness-<timestamp>.json"}
```

If status is `blocked`, do not treat local tests as live evidence. Fix the named blocker or attach the readiness artifact to the TaskResult as environment-blocked evidence.

Operational store commands:

```bash
python3 scripts/ops/postgres_live_ops.py --root /Users/meimei/Documents/company_knowledge_core migrate
python3 scripts/ops/postgres_live_ops.py --root /Users/meimei/Documents/company_knowledge_core status
python3 scripts/ops/postgres_live_ops.py --root /Users/meimei/Documents/company_knowledge_core backup-readiness
```

Rollback is for a cloned/restored staging database only:

```bash
python3 scripts/ops/postgres_live_ops.py --root /Users/meimei/Documents/company_knowledge_core rollback --to base --allow-destructive
```

Do not run rollback on production-like data unless a backup snapshot and rollback approval are already recorded.

## Log Inspection

On Lighthouse:

```bash
ssh <server>
cd /opt/projects/company_knowledge_core/repo/deploy/lighthouse
docker compose -p zhenzhi_knowledge ps
docker compose -p zhenzhi_knowledge logs --tail=200 zhenzhi-knowledge-api
```

If the server uses legacy Compose:

```bash
docker-compose -p zhenzhi_knowledge logs --tail=200 zhenzhi-knowledge-api
```

Look for:

- HTTP `400` from malformed card callback payloads;
- HTTP `401` from missing or wrong API token;
- Feishu API error code and body from reply/card send failures;
- DeepSeek timeout or API errors;
- bundle validation errors surfaced by `/health`.

## Feishu Callback And Card Diagnostics

Important audit actions:

```txt
feishu.message.receive
feishu.reply.failed
feishu.async_reply.sent
feishu.async_reply.failed
feishu.card.action
feishu.card.action.failed
feishu.card.job
feishu.permission.notification
```

Where to inspect:

```txt
knowledge/audit/
notifications/
.zhenzhi/feishu-card-events/
.zhenzhi/feishu-card-jobs/
.zhenzhi/evidence/
```

Known failure classes:

| Symptom | Likely Cause | Check |
| --- | --- | --- |
| Card button shows `200530` | card callback not configured, callback URL wrong, or old card still points to stale interaction | Feishu callback config, `.zhenzhi/feishu-card-events/`, `feishu.async_reply.failed` |
| Card submit shows `200341` | card JSON/action schema unsupported by Feishu client or callback failed | card action payload, server logs, card event record |
| Text fallback appears after card error | interactive card send failed and fallback text was sent | `feishu.reply.failed` includes `fallbackTextSent: true` |
| No bot reply | event callback not reaching server or verification token mismatch | server logs, `feishu.reject`, `/integrations/feishu/events` route |
| Permission/scope failure | app credential invalid, bot not in chat, or missing message/card scope | `feishu.permission.notification`, `feishu_delivery_attempts`, readiness artifact |

Operational rule:

- For every new interactive card, keep a stable fallback text.
- When replacing a broken card, send a new card and make the old action harmless in the callback handler.
- Treat old card clicks as stale UI, not as user errors.

## DeepSeek Router Diagnostics

DeepSeek is only a Feishu intent router. It must not execute engineering tasks, publish verified knowledge, change permissions, reveal secrets, or bypass review.

Important audit actions:

```txt
feishu.router.metric
feishu.router.decision
feishu.router.failed
feishu.router.tool_rejected
```

Metric fields:

```txt
model
mode
latencyMs
promptTokens
completionTokens
totalTokens
estimatedCostUSD
errorClass
fallback
chatScope
messageId
```

Diagnosis:

- If `fallback=true`, the bot should continue with deterministic fallback routing.
- If `errorClass` appears repeatedly, inspect `DEEPSEEK_API_BASE`, `DEEPSEEK_MODEL`, timeout, and server network.
- If cost estimates are zero, check optional price env vars; this is not a routing failure.
- If tool suggestions are rejected, inspect `feishu.router.tool_rejected`; unregistered or high-risk tool calls should become approval or task records.

## Agent Ring / Runner Runtime Diagnostics

Primary API flow:

```txt
POST /v0/runners/register
POST /v0/runners/heartbeat
GET  /v0/tasks?status=pending&assignee=<runnerId>
POST /v0/tasks/claim
POST /v0/tasks/pull
POST /v0/tasks/heartbeat
POST /v0/tasks/finish
```

Use the contract harness before blaming Agent Ring:

```bash
python3 scripts/agent_ring_contract.py
```

The harness validates auth, registration, heartbeat, task query, claim, pull, finish, missing capability, stale version, invalid lease, expired lease, and final bundle validation.

Use the production closed-loop acceptance harness before declaring the central processor ready:

```bash
python3 scripts/production_closed_loop_acceptance.py
```

The harness creates a temporary bundle and verifies the current no-Agent-Ring bridge:

- project registration;
- project Agent registration;
- temporary Runner registration;
- SourceMaterial intake;
- automatic KnowledgeTask creation;
- `waiting_runner` handoff;
- runner claim, lease, pull, context generation, and finish;
- evidence-backed KnowledgeItem draft creation;
- task notification records;
- graph export and graph impact;
- final bundle validation.

It does not call the live Feishu tenant, DeepSeek, Codex, Claude, browser, or external network. Use it to verify the central processor lifecycle. Live Feishu acceptance still requires clicking the actual bot menu/card in Feishu after deployment.

## API Smoke Inspection

Before live Feishu acceptance, verify the central processor API paths that the bot and Agent Ring depend on:

- `POST /v0/materials/ingest`: registers `SourceMaterial`, rejects obvious secret-like content, requires `storageRef` for oversized inline content, and can create a linked `KnowledgeTask`.
- `POST /v0/graph/export`: rebuilds generated graph edges, writes a `GraphSnapshot`, and records audit logs.
- `POST /v0/graph/impact`: returns incoming, outgoing, and affected refs. It must not rewrite `graph/edges/` unless `rebuild: true` is passed.

If Feishu card submission succeeds but no project/material/task appears, inspect callback events under `.zhenzhi/feishu-card-events/` and submit jobs under `.zhenzhi/feishu-card-jobs/` before retrying deployment.

## Task Runtime Inspection

Inspect task state:

```bash
python3 -m zhenzhi_knowledge --root /Users/meimei/Documents/company_knowledge_core task status <TASK_ID>
```

Inspect project tasks:

```txt
projects/<project-id>/tasks/
task-results/
notifications/
knowledge/audit/
```

Task status meaning:

- `pending`: task created, no Runner lease.
- `waiting_runner`: task is ready, but no Agent Ring Runner or temporary local Runner has taken it.
- `processing`: a Runner has claimed the task and work is in progress. Lease details live in `assignedRunner`, `leaseOwner`, `leaseExpiresAt`, and `heartbeatAt`.
- `waiting_acceptance`: TaskResult passed machine checks and is waiting for project-manager or human acceptance.
- `changes_requested`: the result needs repair or rework before it can proceed.
- `blocked`: missing capability, missing credential, source unavailable, policy gate, or another blocker.
- `done`: result accepted and task closed.
- `rejected`: result rejected and task closed.

Do not use result or gate names as task routing status. Lease metadata, TaskResult values, quality decisions, approval states, and human-acceptance policy values must stay in their own fields, not `ProjectTask.status`.

## Minimum Incident Report

Every incident note should include:

- date/time;
- user-facing symptom;
- message ID, task ID, project ID, or runner ID;
- health response;
- relevant audit action;
- server log excerpt path or command;
- root cause;
- fix;
- regression test or contract check.
