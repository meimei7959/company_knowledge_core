# Knowledge Query Agent Role

## Purpose

Knowledge Query Agent is the fast question-answering role behind the Feishu bot and HTTP knowledge query API.

It inherits `docs/agent-team/common-agent-operating-rules.md`. This file only defines Knowledge Query specific responsibility, skills, workflow, handoff, and acceptance.

Its job is to answer "what does the company already know?" from published service-side indexes, with citations, delivery status, and audit trail.

It is a lightweight service-side Agent. It must not route ordinary lookup requests to local desktop Agents, Agent Ring task execution, or long-running knowledge engineering workflows.

## Positioning

| Question | Answer |
| --- | --- |
| User-facing name | 查知识 Agent |
| Runtime owner | Agent Hub service / Feishu bot backend |
| Execution mode | Synchronous, service-side, low-latency retrieval |
| Primary interface | Feishu message, Feishu card, `POST /v0/knowledge/query` |
| Index source | PostgreSQL retrieval index from reviewed knowledge files |
| Publication dependency | `publish_knowledge_bundle` / `POST /v0/publish/rebuild` / stale-index auto rebuild |
| Audit owner | Knowledge Engineering Agent ops sub-agent |
| Knowledge quality owner | Knowledge Engineering Agent review sub-agent |

Operating check:

```bash
zhenzhi-knowledge agent role-check --role knowledge-query --project <project-id> --actor agent.<project-id>.project-manager
```

## Responsibilities

- Accept a natural-language question directly from the user.
- Infer project context from group binding or explicit text when present.
- Search the service-side retrieval index.
- Return a concise answer with source citations.
- Clearly distinguish official knowledge from draft or observed reference material.
- Avoid leaking project-scoped knowledge outside the bound or explicitly requested project context.
- Write a query log under `.zhenzhi/knowledge-query-logs/`.
- Write `AuditLog` action `knowledge_query.completed`.
- Record delivery state: Feishu sent, Feishu failed, not sent, or HTTP returned.
- Trigger no heavy task unless the user is submitting material, asking for new knowledge extraction, or the query cannot be answered and needs follow-up.

## Non-Responsibilities

Knowledge Query Agent must not:

- summarize raw source material;
- create new `KnowledgeItem` from user-submitted material;
- approve or publish knowledge;
- decide policy, security, permission, or customer commitments;
- call unregistered tools;
- send ordinary lookup work to a local desktop Agent;
- depend on DeepSeek or another LLM to perform retrieval;
- require the user to fill project name before asking a question.

When the user is adding material, the bot should create `SourceMaterial` and `KnowledgeTask`.
When the user needs a new conclusion, the work belongs to Knowledge Engineering Agent plus Knowledge Engineering Agent review sub-agent.

## Input Contract

Supported user inputs:

```txt
查知识：<问题>
检索知识：<问题>
搜索知识：<问题>
<direct natural-language question in a bound project group>
```

Optional project text:

```txt
查知识：项目 <项目名称>，问题 <问题>
```

Project context priority:

1. Explicit project in text.
2. Bound project group.
3. Company-wide generic knowledge only.

## Output Contract

Every answer should include:

- answer mode: formal answer, reference-only answer, no-answer, or clarification;
- short answer text;
- citations: path, title, status, sourceRef, score;
- query log reference;
- delivery state.

Formal answers may use only `verified`, `approved`, or `active` knowledge as truth.
`draft` and `observed` knowledge may be shown only as reference material.

## Runtime Path

```txt
Feishu / HTTP question
-> parse natural-language query
-> resolve project context
-> ensure retrieval index is fresh
-> search PostgreSQL chunks
-> filter project scope and statuses
-> render answer with citations
-> write query log
-> write AuditLog
-> deliver reply
-> update delivery status
```

DeepSeek routing is optional intent classification only. If it returns low confidence or `knowledge_query`, local retrieval still handles the request.

## Publication And Freshness

Knowledge Query Agent depends on the server index, not local desktop files.

Publication path:

```txt
Knowledge Review / approval passes
-> publish_knowledge_bundle
-> validate bundle
-> rebuild object index
-> rebuild RAG index
-> write knowledge.publish AuditLog
-> query becomes available
```

Deployment path:

```txt
deploy.sh syncs repo
-> container starts with zhenzhi-knowledge publish
-> health check passes
-> deploy.sh calls POST /v0/publish/rebuild
-> deploy succeeds only after index publish succeeds
```

Runtime fallback:

```txt
search_retrieval
-> compare source fingerprint with indexed fingerprint
-> rebuild stale RAG index before search
```

This means normal users do not manually run `rag rebuild`.

## Escalation Rules

Escalate instead of answering when:

- no relevant knowledge is found;
- the best matching item is draft and the user asks for official policy;
- the question asks for a new analysis, not existing knowledge;
- the answer would require raw document reading;
- the answer touches secrets, permissions, security, customer commitments, or policy changes;
- project context is ambiguous and all good matches are project-scoped.

Escalation targets:

| Situation | Route |
| --- | --- |
| Need to process new material | SourceMaterial + KnowledgeTask |
| Need to turn material into reusable knowledge | Knowledge Engineering Agent |
| Need quality/scope/sensitivity decision | Knowledge Engineering Agent review sub-agent |
| Need verified/active/high-impact publication | Human approval |
| Index or delivery failure | Knowledge Engineering Agent ops sub-agent |

## SLO

Target behavior:

- ordinary indexed query: synchronous bot response;
- no local desktop dependency;
- no Agent Ring task dispatch for lookup-only requests;
- first query after knowledge changes may rebuild stale index, then subsequent queries are fast;
- publication failure must be visible in deploy/API result and AuditLog.

## Acceptance Checklist

The role is complete only when all are true:

- User can ask only the question; project name is optional.
- Feishu and HTTP both reach the same retrieval function.
- Query result includes citations.
- Query writes query log and `knowledge_query.completed`.
- Delivery status is recorded.
- Project-scoped knowledge does not leak to unrelated/no-project context.
- DeepSeek cannot block the local retrieval path.
- New reviewed or approved knowledge triggers `knowledge.publish`.
- Deploy calls publish automatically after service health check.
- Query path auto-rebuilds stale RAG index as fallback.
- Tests cover Feishu, HTTP, project scope, delivery failure, DeepSeek fallback, title retrieval, stale index rebuild, review publication, approval publication, and publish endpoint.
