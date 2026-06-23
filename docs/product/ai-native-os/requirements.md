# AI Native OS Functional Requirements

This document contains implementation-facing functional requirements.

It is not the complete requirement set by itself. The real business, user, and product requirements are defined in [Requirement Tree](requirement-tree.md). Each functional requirement here must trace back to that tree, and must be implemented with traceable tests in [Test Cases](test-cases.md) and launch gates in [Acceptance Checklist](acceptance-checklist.md).

Status vocabulary:

- `draft`: created but not confirmed.
- `clarifying`: waiting for requirement clarification.
- `decision_needed`: human owner must choose.
- `approved`: ready for downstream execution.
- `in_progress`: assigned or executing.
- `reviewing`: waiting for review or acceptance.
- `done`: accepted and closed.
- `blocked`: cannot continue without owner action.
- `rejected`: reviewed and rejected with reason.

## Agent Hub

| ID | Requirement | Acceptance |
| --- | --- | --- |
| ANOS-REQ-001 | Agent Hub must accept natural language request, document link, file reference, meeting note, or task instruction from Feishu and API. | Input creates SourceMaterial, Requirement, Project, KnowledgeTask, or status query with visible confirmation. |
| ANOS-REQ-002 | Agent Hub must classify intent into project creation, requirement clarification, knowledge query, knowledge capture, task status, approval action, or admin request. | Classification result is stored and auditable; ambiguous intent asks clarification. |
| ANOS-REQ-003 | Agent Hub must detect sensitivity and permission risk before routing. | Sensitive material is not exposed to unauthorized Agent or user. |
| ANOS-REQ-004 | Agent Hub must create readable user-facing cards/messages. | Human sees business label, status, next action, owner, and link/ref; raw internal IDs are secondary. |
| ANOS-REQ-005 | Agent Hub must support async callback handling. | Card callback returns quickly; long work continues as task and sends later notification. |
| ANOS-REQ-006 | Agent Hub must let user bind request to existing project or create new project. | Ambiguous project names trigger disambiguation. |

## Requirement Center

| ID | Requirement | Acceptance |
| --- | --- | --- |
| ANOS-REQ-010 | System must create a durable Requirement object for product/business needs. | Requirement has id, title, sourceRefs, owner, submitter, status, sensitivity, projectRef, and audit. |
| ANOS-REQ-011 | Requirement must store field-level RequirementState. | target user, problem, scenario, alternative, value, market position, business model, scope, non-goals, constraints, metric, acceptance criteria, evidence, assumptions, decision owner are marked known/assumed/missing/needs_approval. |
| ANOS-REQ-012 | Product Manager Agent must run Socratic clarification when required fields are missing. | Agent asks 1-3 highest-value questions per round and records answers in RequirementState. |
| ANOS-REQ-013 | Requirement Center must separate evidence, inference, assumption, and decision needed. | PRD and task handoff display each category separately. |
| ANOS-REQ-014 | Requirement must support versioned PRD generation. | Each PRDDocument links to Requirement, sourceRefs, author Agent, reviewer, and version. |
| ANOS-REQ-015 | Requirement cannot become approved until acceptance criteria and owner are present. | Attempted approval without them returns blocker. |
| ANOS-REQ-016 | Requirement must link downstream ProjectTasks. | User can inspect which tasks came from which requirement and criteria. |

## PRD And Decision Center

| ID | Requirement | Acceptance |
| --- | --- | --- |
| ANOS-REQ-020 | Product Manager Agent must generate PRD with positioning, market positioning, business model, workflows, requirements, metrics, risks, and open decisions. | PRD passes quality gate and links sourceRefs. |
| ANOS-REQ-021 | High-impact product, customer, pricing, security, legal, or cross-team decision must create Decision request. | Decision has human owner, options, tradeoffs, recommendation, deadline, and audit. |
| ANOS-REQ-022 | PRD must include non-goals and scope boundaries. | Development Agent can identify out-of-scope work without asking original submitter. |
| ANOS-REQ-023 | AcceptanceCriteria must be observable and testable. | Test Agent can derive cases from criteria. |
| ANOS-REQ-024 | PRD changes after task creation must create impact review. | Affected ProjectTasks, designs, tests, and results are listed. |

## Project Console

| ID | Requirement | Acceptance |
| --- | --- | --- |
| ANOS-REQ-030 | Project Console must show project health from launch, requirements, tasks, Agents, runners, reviews, and notifications. | Owner sees current state, blockers, next action, and responsible role. |
| ANOS-REQ-031 | Project must show Agent roster and role boundaries. | Eight business Agents and governance Agents display status, scope, tools, and current work. |
| ANOS-REQ-032 | Project must show source material and evidence chain. | Requirement, task, result, and knowledge can trace back to source. |
| ANOS-REQ-033 | Project must show first and active work queues. | Tasks display type, runtime, required capabilities, assignee/runner, status, lease, and acceptance path. |
| ANOS-REQ-034 | Project must show risks and blockers. | Blocker has owner, reason, next action, and notification state. |

## Agent Team Manager

| ID | Requirement | Acceptance |
| --- | --- | --- |
| ANOS-REQ-040 | System must manage eight business Agents as first-class product roles. | Each Agent has profile, allowed projects, tools, knowledge scopes, skills, risk level, status, and owner. |
| ANOS-REQ-041 | System must manage governance Agents separately from business Agents. | Steward, Review, and Ops Agents cannot be confused with execution roles. |
| ANOS-REQ-042 | Agent must have capability report. | Scheduler can match task to Agent capability and runner capability. |
| ANOS-REQ-043 | Agent role health check must detect missing skill, scope, tool, or output contract. | Failed check creates repair task or governance issue. |
| ANOS-REQ-044 | Agent cannot call unregistered tool. | Tool call is blocked and audited. |
| ANOS-REQ-045 | Agent skill package must support version and tests. | Skill update requires owner, version, test evidence, rollout state, and rollback path. |

## Scheduler And Task Center

| ID | Requirement | Acceptance |
| --- | --- | --- |
| ANOS-REQ-050 | Scheduler must normalize every dispatchable task into taskRuntime. | Runtime includes taskType, required capabilities, required tools, sourceRefs, acceptancePath, reviewPath, risk, and permission. |
| ANOS-REQ-051 | Scheduler must match task to eligible runner and Agent. | Mismatch produces waiting_runner or blocked with reason. |
| ANOS-REQ-052 | Runner claim must create lease owner, token, and expiry. | Finish without valid lease fails. |
| ANOS-REQ-053 | Scheduler must handle heartbeat, stale lease, retry, cancellation, and escalation. | Stale critical task alerts Project Manager Agent and Ops. |
| ANOS-REQ-054 | Engineering task acceptance must depend on engineering/test evidence, not knowledge draft. | Task cannot close only because text was generated. |
| ANOS-REQ-055 | Knowledge capture task acceptance must depend on SourceMaterial, draft KnowledgeItem, and review path. | Missing evidence blocks closure. |
| ANOS-REQ-056 | Product discovery task acceptance must depend on RequirementState and PRD quality gate. | Missing target user, market, business model, or criteria blocks closure. |

## Agent Ring Console

| ID | Requirement | Acceptance |
| --- | --- | --- |
| ANOS-REQ-060 | Runner registry must show runner id, machine, owner, heartbeat, load, status, Agents, tools, repositories, and data scopes. | Admin can tell which runner can execute which work. |
| ANOS-REQ-061 | Runner must expose current leases and task history. | Stale or failed lease is visible and repairable. |
| ANOS-REQ-062 | Runner must support manual handoff before full Agent Ring product exists. | Manual handoff still writes AgentRun or equivalent record, TaskResult, NotificationRecord, and AuditLog. |
| ANOS-REQ-063 | Runner cannot access source, repo, tool, or knowledge outside allowed scope. | Unauthorized access is blocked and audited. |

## Result Center

| ID | Requirement | Acceptance |
| --- | --- | --- |
| ANOS-REQ-070 | TaskResult must include summary, outputRefs, evidenceRefs, risks, blockers, nextAction, executorAgent, runner, and source links. | Result without required fields cannot close task. |
| ANOS-REQ-071 | Result Center must support product acceptance, test acceptance, knowledge review, and human approval. | Correct acceptance path is displayed from taskRuntime. |
| ANOS-REQ-072 | Rejected result must create follow-up task or retry reason. | Owner sees exact gap and next action. |
| ANOS-REQ-073 | Failed Agent result must create improvement proposal when failure is repeatable or systemic. | Eval or repair task links to failure evidence. |

## Knowledge Core

| ID | Requirement | Acceptance |
| --- | --- | --- |
| ANOS-REQ-080 | SourceMaterial must be registered before reusable knowledge is produced. | Direct publication from raw message is blocked. |
| ANOS-REQ-081 | KnowledgeItem must include category, source evidence, confidence, sensitivity, scope, and review state. | Missing fields block review pass. |
| ANOS-REQ-082 | Knowledge Review must check structure, source, confidence, sensitivity, duplicate risk, conflict risk, graph impact, readability, and status path. | Review result records pass, changes requested, clarification, conflict, human approval, or reject. |
| ANOS-REQ-083 | Knowledge search must return answer with citations, confidence, and gaps. | No verified answer can still return reviewable sources and missing knowledge path. |
| ANOS-REQ-084 | Knowledge graph edges must be traceable to source object or evidence. | Edge without reason/evidence is rejected. |

## Review Center

| ID | Requirement | Acceptance |
| --- | --- | --- |
| ANOS-REQ-090 | Review Center must route reviews by object type, risk, owner, and approval requirement. | Knowledge, requirement, decision, tool, skill, permission, and release gate use distinct paths. |
| ANOS-REQ-091 | Human approval is required for verified knowledge, policy/workflow/iron rule, permission/security/customer commitments, and high-impact product decisions. | Agent cannot self-approve. |
| ANOS-REQ-092 | Review comments must be actionable. | Reviewer sees readable summary, evidence, risk, and exact requested change. |
| ANOS-REQ-093 | Review result must notify requester and owner. | Notification links to object, result, reason, and next action. |

## Tool And Skill Registry

| ID | Requirement | Acceptance |
| --- | --- | --- |
| ANOS-REQ-100 | ToolAsset must include owner, risk, status, allowed Agents, permissions, approval route, and audit requirements. | High-risk execution requires approval. |
| ANOS-REQ-101 | SkillAsset must include owner, version, scope, trigger, resources, tests, compatibility, status, and rollback path. | Skill cannot be approved without tests. |
| ANOS-REQ-102 | Tool and skill usage must be recorded in AgentRun or TaskResult. | Audit can answer which Agent used what to produce which result. |

## Quality And Evaluation Dashboard

| ID | Requirement | Acceptance |
| --- | --- | --- |
| ANOS-REQ-110 | Dashboard must show task throughput, completion time, acceptance pass rate, retry rate, blocked rate, and stale rate. | Metrics can filter by project, Agent, runner, task type, and time. |
| ANOS-REQ-111 | Dashboard must show Agent quality. | Includes success rate, review pass rate, user acceptance, failure causes, and improvement tasks. |
| ANOS-REQ-112 | Dashboard must show requirement quality. | Includes clarification completeness, PRD quality gate pass, decision latency, and acceptance coverage. |
| ANOS-REQ-113 | Dashboard must show knowledge quality. | Includes review pass rate, conflict rate, duplicate risk, reuse, stale candidates. |
| ANOS-REQ-114 | EvalCase and EvalRun must support regression tests for router, retrieval, role behavior, and task lifecycle. | Failed eval blocks release gate when severity is high. |

## Notification Center

| ID | Requirement | Acceptance |
| --- | --- | --- |
| ANOS-REQ-120 | NotificationRecord must be created for important user-visible events. | Includes recipient, channel, status, body, objectRef, delivery state, and retry. |
| ANOS-REQ-121 | Notifications must be readable. | User sees project/name/status/next action before raw id. |
| ANOS-REQ-122 | Failed notification must create repair path. | Critical notification failure alerts Ops and project owner when needed. |

## Admin And Governance Console

| ID | Requirement | Acceptance |
| --- | --- | --- |
| ANOS-REQ-130 | Admin can manage organization, users, Agents, runners, tools, skills, permissions, integrations, and data retention. | Changes are permission-checked and audited. |
| ANOS-REQ-131 | Admin can disable Agent, tool, skill, runner, or integration. | Disabled asset cannot be used; active work is paused or reassigned. |
| ANOS-REQ-132 | Secret values must not be stored in knowledge files. | Secret handling stores only secretRef and audits access request. |
| ANOS-REQ-133 | Backup and restore status must be visible. | Ops can confirm latest successful backup and recovery procedure. |

## Operations And Feedback Center

| ID | Requirement | Acceptance |
| --- | --- | --- |
| ANOS-REQ-140 | Operations Agent must collect feedback from completed work and user usage. | Feedback links to project, requirement, Agent, result, and improvement task. |
| ANOS-REQ-141 | Product Operator can see adoption, active users, active Agents, completed tasks, knowledge reuse, and satisfaction. | Metrics update from durable records. |
| ANOS-REQ-142 | Growth or operations experiment must have hypothesis, audience, metric, start/end, result, and decision. | Experiment without metric cannot start. |

## API And Integration Gateway

| ID | Requirement | Acceptance |
| --- | --- | --- |
| ANOS-REQ-150 | API must expose validated endpoints for requirement, project, task, runner, result, review, knowledge query, notification, metrics, and admin. | Unauthorized request fails safely. |
| ANOS-REQ-151 | Feishu, local CLI, web console, and Agent Ring must use same central state contracts. | No integration has private status semantics that diverge from core. |
| ANOS-REQ-152 | API must produce audit records for writes. | Create/update/approve/reject/claim/finish actions are auditable. |
