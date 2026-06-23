# DeepSeek Feishu Routing Plan

## Purpose

Feishu remains the primary user-facing entrance.

DeepSeek paid API will be used by the Feishu bot as the lightweight reasoning and routing layer. The bot should understand user intent, extract structured fields, ask clarifying questions, create cards, and decide whether a request can be handled immediately or must become a central task for Agent Ring.

DeepSeek is not the execution layer. The central processor and Agent Ring remain responsible for durable state, distributed execution, review, audit, and knowledge synchronization.

## DeepSeek Configuration

The Feishu bot uses DeepSeek as an OpenAI-compatible routing adapter, not as an execution engine.

Runtime configuration:

```txt
FEISHU_DEEPSEEK_ROUTER_ENABLED=true
DEEPSEEK_API_KEY=<server secret, never committed>
DEEPSEEK_API_BASE=https://api.deepseek.com/chat/completions
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_TIMEOUT_SECONDS=8
DEEPSEEK_INPUT_PRICE_PER_1M=<optional cost estimate>
DEEPSEEK_OUTPUT_PRICE_PER_1M=<optional cost estimate>
```

The API key must live in server secret storage or runtime environment. The knowledge bundle may store only a `secretRef`, owner, scope, expiry, and audit records.

## Model Selection

Default:

- use `DEEPSEEK_MODEL`, default `deepseek-chat`;
- temperature `0`;
- JSON object output;
- intent routing, field extraction, short replies, card drafting, and status explanation.

Escalation can be handled later by changing `DEEPSEEK_MODEL` or adding a second router profile. Tool execution must always happen in our server-side controlled tool layer.

## What The Feishu Bot Can Handle Directly

The bot may directly handle these actions after DeepSeek routing:

| User Need | Bot Action | Persistence |
| --- | --- | --- |
| New user asks what this bot does | answer with guide/card | no durable task |
| User chooses menu shortcut | map menu to known flow | no durable task unless needed |
| Create project request | extract fields, ask missing questions, create project draft/task | Project + ProjectTask |
| Existing repo project | extract repo URL/name/goal/agents/group choice | Project + init task |
| New repo project | extract repo name/goal/agents/group choice | Project + repo init task |
| Knowledge query | search reviewed knowledge and answer with sources | no write unless feedback |
| Material submission | register SourceMaterial and create KnowledgeTask | SourceMaterial + Task |
| Meeting note submission | register SourceMaterial and create KnowledgeTask | SourceMaterial + Task |
| Access credential request | create credential request flow; never post secret value to group; persist `secretRef` only | AccessCredentialRequest + Notification/Audit record |
| Tool/skill request | extract ToolAsset/SkillAsset candidate fields and submit review task | ToolAsset draft + task |
| Status query | read task/project status and explain in human language | no write |
| Dangerous request | refuse direct execution and create approval task if appropriate | Audit/approval task |

## What Must Become A Task For Agent Ring

DeepSeek should route these into central tasks:

| Request Type | Why Bot Should Not Directly Execute | Task Type |
| --- | --- | --- |
| Long document or meeting minute extraction | needs evidence citation, source preservation, structured knowledge | `knowledge_capture` |
| Codebase analysis or repo initialization | needs local repo, Git, IDE, shell, tests | `project_init` / `engineering_action` |
| Product/engineering implementation | must run on a distributed computer with tools and context | `engineering_action` |
| Knowledge publication as verified | needs review gate and audit | `knowledge_capture` -> review |
| Permission, deletion, access credential, secret, customer commitment | high risk and approval required | credential request / `tool_request` / approval task |
| Cross-project migration or handoff | requires project context bundle and conflict handling | `handoff` |
| Any action needing local browser/session/files | only Agent Ring has local environment | suitable task |
| Any action with uncertain intent | ask clarification first; if still complex, task | suitable task |

## Routing Decision Schema

DeepSeek should output a structured routing decision:

```json
{
  "intent": "create_project | knowledge_query | capture_material | credential_request | tool_or_skill_request | summon_agent | status_query | dangerous_request | clarify",
  "confidence": 0.0,
  "risk": "L0 | L1 | L2 | L3",
  "directHandle": false,
  "taskType": "project_init | knowledge_capture | engineering_action | tool_request | handoff | none",
  "requiredFields": {},
  "missingFields": [],
  "toolSuggestions": [],
  "reason": ""
}
```

Rules:

- Low confidence must ask clarification.
- High-risk intent must not execute directly.
- Durable writes must use registered server-side functions.
- Tool suggestions are suggestions from the model; the server ignores or rejects unregistered suggestions.
- Every task creation must produce a human-readable card.

## Observability

Every DeepSeek routing attempt writes a structured audit metric with:

- model and mode;
- latencyMs;
- promptTokens, completionTokens, totalTokens when provider usage is available;
- estimatedCostUSD when price env vars are configured;
- errorClass and fallback flag;
- chat scope and message id.

The metric must not store the full user prompt, API key, secret value, or raw model response. Failed model calls and malformed JSON must record a fallback metric and return to deterministic safe handling.

## Safety Boundary

DeepSeek may:

- classify intent;
- extract fields;
- draft replies/cards;
- choose from registered safe tool functions;
- explain status and next steps;
- recommend task creation.

DeepSeek must not directly:

- delete or modify knowledge;
- grant permissions;
- reveal secrets;
- publish verified knowledge;
- execute shell/code/Git;
- promise customer-facing commitments;
- bypass review;
- call unregistered tools.

## First Implementation Tasks

1. Add DeepSeek API configuration and secret reference.
2. Add routing prompt and JSON schema.
3. Add server-side validator for model routing output.
4. Map routing decisions to existing Feishu flows and cards.
5. Route complex work to ProjectTask / KnowledgeTask.
6. Add DeepSeek usage logs, cost tracking, and error fallback.
7. Add eval cases for common Feishu messages and high-risk requests.

## Open Questions

- Whether default model should always be `deepseek-v4-flash`, with `deepseek-v4-pro` only for risky/ambiguous requests.
- Whether every DeepSeek call should pass `user_id` based on Feishu open_id hash.
- How much project context should be included in the bot prompt before routing tasks to Agent Ring.
- Whether we want a deterministic fallback router when DeepSeek API fails.
