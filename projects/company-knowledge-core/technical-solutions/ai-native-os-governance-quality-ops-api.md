---
type: Workflow
title: AI Native OS governance, quality, notification, admin, operations, and API technical solution
projectId: company-knowledge-core
taskId: kt-ai-native-os-tech-solution-governance-quality-ops-api
ownerAgent: agent.company.development
status: draft
requirementRefs:
  - ANOS-REQ-080
  - ANOS-REQ-081
  - ANOS-REQ-082
  - ANOS-REQ-083
  - ANOS-REQ-084
  - ANOS-REQ-090
  - ANOS-REQ-091
  - ANOS-REQ-092
  - ANOS-REQ-093
  - ANOS-REQ-100
  - ANOS-REQ-101
  - ANOS-REQ-102
  - ANOS-REQ-110
  - ANOS-REQ-111
  - ANOS-REQ-112
  - ANOS-REQ-113
  - ANOS-REQ-114
  - ANOS-REQ-120
  - ANOS-REQ-121
  - ANOS-REQ-122
  - ANOS-REQ-130
  - ANOS-REQ-131
  - ANOS-REQ-132
  - ANOS-REQ-133
  - ANOS-REQ-140
  - ANOS-REQ-141
  - ANOS-REQ-142
  - ANOS-REQ-150
  - ANOS-REQ-151
  - ANOS-REQ-152
evidenceRefs:
  - docs/product/ai-native-os/requirements.md
  - docs/product/ai-native-os/acceptance-checklist.md
  - projects/company-knowledge-core/tasks/kt-ai-native-os-tech-solution-governance-quality-ops-api.md
  - projects/company-knowledge-core/coordination/ai-native-os-agent-execution-governance.md
updatedAt: "2026-06-21T00:00:00+08:00"
---

# AI Native OS Governance / Quality / Ops / API Technical Solution

## 1. Scope

This solution owns the control plane that makes AI Native OS safe to operate:

- Knowledge Core governance: source-first knowledge, reviewable citations, graph traceability.
- Review Center: typed review routes, human approval boundaries, actionable comments, result notification.
- Tool and Skill Registry: approved tool/skill lifecycle, rollback, usage capture.
- Quality and Evaluation Dashboard: durable operational metrics and release-blocking evals.
- Notification Center: readable, retryable, auditable user-visible messages.
- Admin and Governance Console: RBAC, disable paths, secret references, retention, backup/restore visibility.
- Operations and Feedback Center: feedback capture, adoption metrics, improvement tasks, experiments.
- API and Integration Gateway: one central contract for Feishu, CLI, web console, desktop shell, and Agent Ring.

Out of scope: implementation code, UI component details, concrete database migration, and test file edits.

## 2. Architecture

Use one shared governance state layer behind all product surfaces. Feishu callbacks, local CLI, web/desktop console, and Agent Ring call the same command/query contracts; none owns private status semantics.

Core modules:

| Module | Owns | Primary requirements |
| --- | --- | --- |
| Knowledge Governance | SourceMaterial guard, KnowledgeItem validation, KnowledgeReview, cited retrieval, graph edge validation | ANOS-REQ-080..084 |
| Review Center | ReviewRoute, ReviewRequest, ReviewComment, ApprovalDecision, review notifications | ANOS-REQ-090..093 |
| Registry | ToolAsset, SkillAsset, approval route, rollout state, usage capture | ANOS-REQ-100..102 |
| Quality Metrics | MetricEvent, dashboard aggregation, EvalCase, EvalRun, release gates | ANOS-REQ-110..114 |
| Notification Center | NotificationRecord, template renderer, delivery outbox, retry and repair task | ANOS-REQ-120..122 |
| Admin Console | organization/user/role/permission/integration management, disable paths, secretRef, backup status | ANOS-REQ-130..133 |
| Ops Feedback | FeedbackRecord, ImprovementTask link, adoption metrics, Experiment | ANOS-REQ-140..142 |
| API Gateway | validated endpoints, command envelope, authz, audit writer, idempotency | ANOS-REQ-150..152 |

Every write flows through:

```txt
validated command -> permission check -> domain guard -> state write -> AuditLog -> MetricEvent -> NotificationRecord when user-visible
```

All write commands use an idempotency key. AuditLog is part of the transaction where possible; outbox delivery is async and retryable.

## 3. Shared Contracts

### 3.1 Command Envelope

Every create/update/approve/reject/claim/finish/admin action uses:

| Field | Purpose |
| --- | --- |
| actorRef | human, Agent, runner, or integration identity |
| actorRole | role used for permission decision |
| sourceChannel | feishu, api, cli, console, desktop, agent_ring |
| commandType | typed action name |
| objectRef | target object, optional for create |
| projectRef | project scope for permission and metrics |
| idempotencyKey | duplicate prevention |
| reason | human-readable reason for risky or review actions |
| evidenceRefs | source material, test, task result, review, or audit evidence |
| requestedStatus | target state when applicable |

### 3.2 Status Semantics

Use the product status vocabulary everywhere: `draft`, `clarifying`, `decision_needed`, `approved`, `in_progress`, `reviewing`, `done`, `blocked`, `rejected`.

Allowed integration-specific state is only a derived display field, for example Feishu card label or Agent Ring lease status. Core status remains canonical.

### 3.3 Required Write Side Effects

| Write type | Required side effects |
| --- | --- |
| create/update object | AuditLog, MetricEvent |
| approval/rejection | AuditLog, ReviewResult, NotificationRecord |
| knowledge promotion | AuditLog, KnowledgeReview, optional human ApprovalDecision |
| tool/skill enablement | AuditLog, ReviewRoute, rollout state |
| disable asset | AuditLog, active work pause/reassign event, notification to owner |
| failed notification | retry state, repair task or Ops alert when critical |

## 4. Knowledge Governance Design

### 4.1 Source-first Guard

Reusable knowledge creation must require `sourceMaterialRefs` or equivalent durable source object references before a KnowledgeItem draft can be created.

Guard rules:

- Raw Feishu messages, meeting notes, screenshots, transcripts, and imports become SourceMaterial first.
- KnowledgeItem direct creation from raw text is rejected unless it references registered SourceMaterial.
- Knowledge capture task closure requires SourceMaterial, draft KnowledgeItem, evidenceRefs, and reviewPath.
- Raw material registration is never blocked by knowledge review; review only gates reusable knowledge promotion.

### 4.2 KnowledgeItem Validation

Required fields:

- category under `knowledge/<category>/`;
- source evidence;
- confidence;
- sensitivity;
- scope and applicability limits;
- review state;
- owner or accountable Agent;
- duplicate/conflict check result;
- graph impact summary when edges are added or changed.

Missing required fields keep the item in `draft` or `blocked`; it cannot pass review.

### 4.3 Knowledge Review

Knowledge Review Agent produces a KnowledgeReview record with:

- structure check;
- source/evidence check;
- confidence check;
- sensitivity and secret scan result;
- duplicate risk;
- conflict risk;
- graph impact;
- reviewer-facing readability;
- status path check: draft, observed, verified, approved, active, rejected.

Review outcomes: `pass`, `changes_requested`, `clarification_required`, `conflict_detected`, `human_approval_required`, `reject`.

Human approval is required before verified knowledge, policy/workflow/iron rule, permissions/security/customer commitments, or cross-team operating standards become reusable stronger truth.

### 4.4 Knowledge Search

Knowledge query returns:

- answer summary;
- citation list with objectRef, source label, review status, and sensitivity-safe excerpt;
- confidence;
- gaps and missing knowledge path;
- whether answer is verified, observed, or only source-backed.

If no verified answer exists, search may return reviewable sources and a suggested KnowledgeTask instead of pretending certainty.

### 4.5 Knowledge Graph

KnowledgeGraphEdge requires:

- fromRef and toRef;
- edge type;
- reason;
- evidenceRef or source object;
- sensitivity inherited from endpoints/evidence;
- audit reference.

Edges without reason/evidence are rejected. GraphSnapshot remains an index artifact, not independent truth.

## 5. Review / Approval Design

### 5.1 Review Routing

ReviewRoute is selected by object type, risk, owner, and approval requirement.

| Object/action | Default route | Human approval trigger |
| --- | --- | --- |
| KnowledgeItem | Knowledge Review Agent | verified status, policy/workflow/iron rule, security/customer/cross-team impact |
| Requirement/PRD | Product Manager Agent quality gate | high-impact product decision, owner/criteria approval |
| Decision | Product Manager Agent + owner | pricing, legal, security, customer commitment, cross-team standard |
| ToolAsset | Tool Owner + governance | high-risk execution, permission expansion |
| SkillAsset | Skill Owner + governance | approval without tests is blocked; rollout requires owner |
| Permission/integration | Admin/Governance | any grant, revoke, secret, external integration |
| Release gate | Test Agent + PM + Project Manager | critical EvalRun failure blocks release |

Agents can recommend. They cannot self-approve outputs requiring human approval.

### 5.2 Review Request Shape

Every review card or console row must show:

- readable title and business label;
- object type and requested action;
- owner and requester;
- evidence summary and links;
- risk/sensitivity;
- exact requested decision;
- next action if approved/rejected;
- raw ids only as secondary detail.

### 5.3 Actionable Comments

Review comments must include:

- issue summary;
- affected object field or section;
- why it matters;
- requested change;
- blocker severity;
- due owner when known.

Vague comments such as "needs improvement" are rejected by validation.

### 5.4 Review Result Notification

Every review result creates NotificationRecord for requester and owner with:

- object label;
- review result;
- reason;
- requested change or next action;
- link/ref to review and object.

## 6. Tool and Skill Registry Design

### 6.1 ToolAsset

Required fields:

- owner;
- risk;
- status: draft, approved, disabled, deprecated;
- allowed Agents;
- allowed runners/data scopes;
- permissions;
- approval route;
- audit requirements;
- rollback/disable behavior;
- compatibility notes.

High-risk tool execution requires approval route confirmation before use. Unregistered or unauthorized tool call is blocked and audited.

### 6.2 SkillAsset

Required fields:

- owner;
- version;
- scope and trigger;
- resources and dependencies;
- tests and evidenceRefs;
- compatibility;
- rollout state;
- rollback path;
- status.

Skill cannot be approved without tests. Skill update produces an impact check for Agents using it.

### 6.3 Usage Capture

AgentRun or TaskResult must record:

- toolRefs used;
- skillRefs used;
- version when known;
- command/action category;
- evidence produced;
- policy decision for risky calls.

Audit can answer which Agent used what to produce which result.

## 7. Notification Design

### 7.1 NotificationRecord

Required fields:

- recipient;
- channel;
- status;
- readable body;
- objectRef;
- projectRef;
- delivery state;
- retry count and next retry;
- idempotency key;
- failure reason;
- repairTaskRef when needed.

### 7.2 Readable Templates

Templates prioritize:

```txt
project/name -> business status -> next action -> owner -> link/ref -> raw id
```

Examples:

- review approved/rejected;
- task blocked/stale;
- runner lease stale;
- failed notification repair;
- asset disabled and active work paused;
- critical eval failure release block.

### 7.3 Retry and Repair

Use outbox delivery with bounded retries. Critical notification failure creates Ops alert and repair task when:

- review result was not delivered;
- critical task/blocker/stale lease alert failed;
- approval request failed;
- security/permission change notification failed.

## 8. Quality and Evaluation Dashboard

### 8.1 Metric Events

Metrics are derived from durable records, not ephemeral UI state.

| Metric family | Source records |
| --- | --- |
| task throughput/completion time/retry/blocked/stale | ProjectTask, KnowledgeTask, TaskResult, AgentRun, lease events |
| acceptance pass rate | ReviewResult, Product/Test/Knowledge acceptance records |
| Agent quality | AgentRun, TaskResult, ReviewResult, user acceptance, repair tasks |
| requirement quality | RequirementState, PRDDocument, Decision, AcceptanceCriteria, ProjectTask links |
| knowledge quality | KnowledgeReview, KnowledgeItem, ConflictRecord, duplicate check, retrieval logs |
| notification health | NotificationRecord |
| adoption/ops | FeedbackRecord, active users, completed tasks, knowledge reuse, satisfaction |

Filters: project, Agent, runner, task type, object type, risk, status, time.

### 8.2 Quality Indicators

Required dashboard indicators:

- task throughput;
- median and p95 completion time;
- acceptance pass rate;
- retry rate;
- blocked rate;
- stale rate;
- Agent success rate and review pass rate;
- failure causes;
- improvement task count and age;
- requirement clarification completeness;
- PRD quality gate pass rate;
- decision latency;
- acceptance coverage;
- knowledge review pass/conflict/duplicate/reuse/stale rates;
- critical notification failure count;
- release-blocking EvalRun count.

### 8.3 EvalCase / EvalRun

EvalCase supports:

- router classification;
- retrieval citation/confidence/gap behavior;
- role boundary behavior;
- task lifecycle;
- review routing;
- notification failure;
- permission/unauthorized tool;
- graph edge validation.

EvalRun records case version, target build/config, result, severity, evidenceRefs, owner, and release gate impact. High-severity failure blocks release.

## 9. Admin and Governance Console

### 9.1 Admin Objects

Admin can manage:

- organization;
- users and roles;
- Agents and governance Agents;
- runners;
- tools and skills;
- permissions and data scopes;
- integrations;
- data retention;
- backups and restore status.

All admin changes are permission-checked and audited.

### 9.2 Disable Paths

Admin can disable Agent, tool, skill, runner, or integration.

Disable behavior:

- new usage is blocked immediately;
- active work is paused, cancelled, or reassigned according to object type;
- owner and impacted project owners are notified;
- AuditLog and MetricEvent are written;
- rollback path is shown.

### 9.3 Secrets

Secret values are never stored in knowledge files, user-visible records, TaskResult summaries, or AuditLog bodies.

Only `secretRef` is stored. Access requests are audited with actor, reason, objectRef, and permission decision.

### 9.4 Backup / Restore Visibility

Ops view shows:

- latest successful backup;
- latest failed backup and reason;
- restore procedure ref;
- latest restore drill or verification record;
- retention policy;
- owner and next check time.

Backup/restore status unknown is a launch stop condition.

## 10. Operations and Feedback Design

### 10.1 FeedbackRecord

Operations Agent collects feedback from completed work and usage.

Required fields:

- projectRef;
- requirementRef;
- AgentRef;
- resultRef;
- user or source channel;
- sentiment or score when available;
- feedback summary;
- evidenceRefs;
- improvementTaskRef when action is needed.

### 10.2 Adoption Metrics

Product Operator dashboard shows:

- active users;
- active Agents;
- active runners;
- completed tasks;
- knowledge reuse;
- satisfaction;
- adoption by project/channel;
- feedback-to-improvement conversion.

### 10.3 Experiments

Growth or operations experiment requires:

- hypothesis;
- audience;
- metric;
- start/end;
- owner;
- result;
- decision.

Experiment cannot start without metric. Completed experiment writes decision and optionally creates follow-up tasks.

## 11. API and Integration Gateway

### 11.1 Endpoint Groups

Expose validated API endpoints for:

- requirements;
- projects;
- tasks;
- runners and leases;
- results;
- reviews and approvals;
- knowledge query and knowledge review;
- notifications;
- metrics and evals;
- admin assets and permissions.

Every write endpoint uses the command envelope, authz, idempotency, validation, AuditLog, and consistent error shape.

### 11.2 Integration Consistency

Feishu, local CLI, web console, desktop shell, and Agent Ring must use the same central contracts:

- same object ids;
- same status vocabulary;
- same review routes;
- same permission decision;
- same AuditLog semantics;
- same NotificationRecord model.

Adapters may format display cards differently but cannot invent private lifecycle states.

### 11.3 Error Shape

Unauthorized or invalid requests fail safely:

| Field | Purpose |
| --- | --- |
| errorCode | stable machine code |
| message | readable user-facing summary |
| objectRef | target when safe to reveal |
| blockerReason | missing permission/evidence/approval/lease/etc. |
| nextAction | what user/Agent should do |
| auditRef | write attempt audit where applicable |

Sensitive details are redacted.

## 12. Requirement Coverage Map

| Requirement | Design coverage |
| --- | --- |
| ANOS-REQ-080 | Source-first guard blocks reusable knowledge before SourceMaterial registration. |
| ANOS-REQ-081 | KnowledgeItem required fields and validation. |
| ANOS-REQ-082 | KnowledgeReview checks and outcomes. |
| ANOS-REQ-083 | Knowledge search answer/citation/confidence/gap contract. |
| ANOS-REQ-084 | Graph edge evidence/reason/audit validation. |
| ANOS-REQ-090 | ReviewRoute matrix by object type, risk, owner, approval need. |
| ANOS-REQ-091 | Human approval boundaries and no self-approval rule. |
| ANOS-REQ-092 | Actionable comment schema. |
| ANOS-REQ-093 | Review result NotificationRecord. |
| ANOS-REQ-100 | ToolAsset schema, approval route, audit requirements. |
| ANOS-REQ-101 | SkillAsset schema, test requirement, rollback path. |
| ANOS-REQ-102 | Tool/skill usage capture in AgentRun or TaskResult. |
| ANOS-REQ-110 | Throughput/completion/pass/retry/blocked/stale metrics. |
| ANOS-REQ-111 | Agent quality indicators and improvement task links. |
| ANOS-REQ-112 | Requirement quality indicators. |
| ANOS-REQ-113 | Knowledge quality indicators. |
| ANOS-REQ-114 | EvalCase/EvalRun and release-blocking severity. |
| ANOS-REQ-120 | NotificationRecord schema. |
| ANOS-REQ-121 | Readable notification templates. |
| ANOS-REQ-122 | Retry, Ops alert, repair task path. |
| ANOS-REQ-130 | Admin object management, permission check, audit. |
| ANOS-REQ-131 | Disable path for Agent/tool/skill/runner/integration. |
| ANOS-REQ-132 | secretRef-only storage and audited access. |
| ANOS-REQ-133 | Backup/restore status visibility. |
| ANOS-REQ-140 | FeedbackRecord links completed work and improvement tasks. |
| ANOS-REQ-141 | Adoption/active/completed/reuse/satisfaction metrics. |
| ANOS-REQ-142 | Experiment schema and metric-before-start guard. |
| ANOS-REQ-150 | Endpoint groups and validated write contracts. |
| ANOS-REQ-151 | Shared central state contracts for all integrations. |
| ANOS-REQ-152 | AuditLog for create/update/approve/reject/claim/finish writes. |

## 13. Implementation Slices

1. Governance contract slice
   - Define command envelope, error shape, AuditLog side effect contract, status vocabulary usage, and idempotency behavior.
   - Acceptance: all write routes can state required audit and error behavior before implementation.

2. Knowledge governance slice
   - Add SourceMaterial guard, KnowledgeItem validation, KnowledgeReview outcomes, graph edge validation, and search response contract.
   - Acceptance: source-first, review, search, and graph launch gates have direct test cases.

3. Review and approval slice
   - Implement ReviewRoute matrix, review request/comment/result records, human approval boundary, and review result notification.
   - Acceptance: no self-approval for human-gated objects.

4. Registry and admin slice
   - Implement ToolAsset/SkillAsset contracts, disable paths, secretRef rules, admin permission checks, backup/restore status.
   - Acceptance: unauthorized tool/secret/disable cases fail safely and write audit.

5. Notification slice
   - Implement NotificationRecord, readable templates, delivery outbox, retry, failure repair path.
   - Acceptance: failed critical notification creates visible repair path.

6. Quality and eval slice
   - Implement MetricEvent aggregation, dashboard filters, EvalCase/EvalRun release gate.
   - Acceptance: high-severity EvalRun failure blocks release.

7. Operations feedback slice
   - Implement FeedbackRecord, adoption metrics, improvement task link, experiment guard.
   - Acceptance: feedback links to project/requirement/Agent/result and action path.

8. API gateway slice
   - Implement endpoint groups with shared command envelope for Feishu, CLI, console/desktop, and Agent Ring.
   - Acceptance: no integration-specific private status semantics.

## 14. Test Strategy

### 14.1 Unit Tests

- KnowledgeItem validation rejects missing category/source/confidence/sensitivity/scope/review state.
- Source-first guard rejects direct reusable knowledge from raw message.
- KnowledgeGraphEdge rejects missing reason/evidence.
- Review comment validation rejects non-actionable comments.
- ToolAsset and SkillAsset validation rejects missing owner/risk/tests/rollback where required.
- NotificationRecord validation requires recipient/channel/body/objectRef/delivery state.
- Experiment validation rejects start without metric.
- API command envelope rejects missing actor/idempotency/permission context.

### 14.2 Contract Tests

- Each write endpoint emits AuditLog.
- Unauthorized request returns safe error shape without sensitive detail.
- Feishu, CLI, console/desktop, and Agent Ring adapters map to same status vocabulary.
- ReviewRoute selection matches object type/risk/approval requirement.
- Secret handling stores only secretRef.

### 14.3 Lifecycle Tests

- Raw material -> SourceMaterial -> KnowledgeTask -> KnowledgeItem draft -> KnowledgeReview -> human approval when verified -> searchable answer with citations.
- Review request -> actionable comment -> approval/rejection -> requester/owner notification.
- Tool/skill approval -> AgentRun usage capture -> disable -> active work pause/reassign.
- Task/result/review events -> MetricEvent -> dashboard filter by project/Agent/runner/task type/time.
- Critical notification delivery failure -> retry -> Ops alert -> repair task.
- EvalRun high-severity failure -> release gate blocked.

### 14.4 Negative / Launch Stop Tests

Map directly to launch stop conditions:

- reusable knowledge bypasses review: blocked;
- Agent self-approves verified knowledge: blocked;
- unregistered tool usage: blocked and audited;
- auth material in knowledge/user-visible record: blocked/redacted;
- write without AuditLog: test failure;
- backup/restore status unknown: launch gate failure;
- critical E2E or EvalRun failure: release gate blocked.

## 15. Product Manager Agent Discussion Questions

1. Verified knowledge policy: should `observed` knowledge be reusable in answers with clear confidence, or only shown as reviewable source until human verification?
2. Notification priority: which events must page/alert Ops immediately versus only appear in Project Console?
3. Review SLA: what default due times should apply to knowledge review, approval, high-risk tool/skill changes, and release gates?
4. Admin disable semantics: when a runner/tool/Agent is disabled, should active tasks pause by default or auto-reassign when eligible runner exists?
5. Dashboard launch bar: what minimum metric set must be visible for first launch claim versus later optimization?
6. Experiment governance: who can approve growth/ops experiments that affect customer-facing behavior?
7. API consumers: should desktop shell call the same public API only, or allow a local privileged adapter for offline/desktop-only actions?

## 16. Risks and Rollback

| Risk | Impact | Mitigation | Rollback |
| --- | --- | --- | --- |
| Review routing too strict | Work queues stall | staged rollout by object type, visible blocker reasons | temporarily downgrade non-human-gated routes to Agent review with audit |
| Notification retries create noise | Users receive duplicates | idempotency key, delivery dedupe, template versioning | disable affected channel adapter, keep console notifications |
| Metrics aggregation lags | Dashboard stale | derive from durable records, show freshness timestamp | fall back to raw record counts and hide stale aggregates |
| Admin disable pauses too much work | Delivery interruption | impact preview before disable, owner notification | re-enable asset or reassign paused tasks |
| Secret redaction false positive | Legit output blocked | allow reviewed exception as secretRef metadata only | restore previous redaction rule version |
| API contract drift across adapters | Feishu/CLI/Agent Ring disagreement | contract tests and shared DTO/schema package | freeze adapter release, roll back adapter mapping |
| Knowledge review backlog | Search cannot promote knowledge | queue metrics, SLA, reviewer assignment | keep answers source-backed with gap labels; no verified promotion |

## 17. Review Readiness

This solution is ready for Product Manager Agent and Project Manager Agent review. It intentionally stops before implementation and test edits.
