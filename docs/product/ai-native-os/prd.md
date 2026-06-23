# AI Native OS Complete Launch PRD

## Product Positioning

Zhenzhi AI Native OS is the work operating system for an AI-native company.

It is not only a knowledge base, not only an Agent chat interface, and not only a project management tool. It is the central product layer that makes humans, Agents, tools, runners, source material, tasks, reviews, and knowledge operate as one traceable production system.

## Product Promise

Any employee can submit a rough idea, customer request, document, incident, or task. The OS clarifies the requirement, assigns the right Agent roles, dispatches execution to eligible Agent Ring runners, captures results, reviews reusable knowledge, notifies owners, and measures quality.

## Complete Launch Scope

The complete launch product includes:

- Agent Hub intake.
- Requirement Center.
- PRD and Decision Center.
- Project Console.
- Agent Team Manager.
- Scheduler and Task Center.
- Agent Ring Console.
- Result Center.
- Knowledge Core and Knowledge Search.
- Review Center.
- Tool and Skill Registry.
- Quality and Evaluation Dashboard.
- Notification Center.
- Admin and Governance Console.
- Operations and Feedback Center.
- API and Integration Gateway.

## Human Roles

| Role | Responsibility |
| --- | --- |
| System Admin | Configure organization, permissions, Agents, tools, runners, gateways, audit, retention, and backup. |
| Project Owner | Own product direction, scope, priority, approval, and final acceptance. |
| Requirement Submitter | Submit ideas, customer requests, documents, incidents, or tasks; answer clarification questions; receive status. |
| Human Reviewer | Approve high-impact knowledge, tool, permission, policy, customer, security, or cross-team decisions. |
| Team Member | Search knowledge, submit tasks, inspect results, and collaborate with Agents. |
| Runner Admin | Register and operate distributed computers that run Agent Ring. |
| Product Operator | Monitor feedback, adoption, operational quality, growth loops, and launch readiness. |

## Business Agent Roles

| Agent | Product Role | Main Output |
| --- | --- | --- |
| Project Manager Agent | Project initialization, task orchestration, milestone closure, risk, notification, cross-Agent coordination. | Launch state, task plan, risk list, owner notification. |
| Product Manager Agent | Requirement clarification, market and competitor analysis, product plan, PRD, acceptance criteria. | Requirement state, PRD, decision request, acceptance criteria. |
| Knowledge Query Agent | Answer employee and Agent questions from reviewed knowledge with source, confidence, and gap. | Cited answer, confidence, missing knowledge task. |
| Knowledge Engineering Agent | Read source material, build evidence packet, draft structured knowledge, write TaskResult. | Evidence packet, KnowledgeItem draft, TaskResult. |
| Design Agent | Information architecture, interaction flow, UI specification, usability review. | UX flow, page spec, design handoff, usability findings. |
| Development Agent | Technical design, implementation, debugging, integration, engineering delivery. | Code change, technical notes, implementation TaskResult. |
| Test Agent | Test plan, cases, automation, defect reproduction, quality gate. | Test cases, test report, defects, release quality verdict. |
| Operations Agent | Launch operations, feedback collection, growth experiment, content/process operations, operations review. | Launch plan, feedback report, operation metrics, improvement tasks. |

## Governance Agent Roles

| Agent | Product Role |
| --- | --- |
| Knowledge Steward Agent | Maintain rules, boundaries, object model, registry classification, governance proposals. |
| Knowledge Review Agent | Review reusable knowledge for evidence, structure, sensitivity, conflicts, duplicate risk, and approval route. |
| Knowledge Ops Agent | Maintain connector, gateway, permission checks, audit, evaluation, sync, backup, and recovery. |

## Runner And Tool Roles

| Role | Responsibility |
| --- | --- |
| Agent Ring Runner | Distributed computer execution node. Registers capability, tools, repository access, data scope, heartbeat, load, and lease state. |
| Codex Local Builder | Local engineering execution tool available through an authorized runner. |
| Antigravity Local Builder | Local execution tool available through an authorized runner. |
| ToolAsset | Registered tool with owner, approval, risk level, allowed Agents, and audit requirements. |
| SkillAsset | Registered Agent skill package with version, owner, scope, tests, and rollout state. |

## End-To-End Product Flow

```txt
Submit request
-> classify intent and sensitivity
-> create SourceMaterial or direct Requirement
-> Product Manager Agent clarifies requirement when needed
-> create PRD, acceptance criteria, and decision requests
-> Project Manager Agent creates project plan and ProjectTasks
-> Scheduler normalizes taskRuntime and matches runner
-> Agent Ring runner claims task with lease
-> assigned Agent executes with approved tools and context pack
-> TaskResult writes outputs, evidence, risks, and next action
-> Test Agent or acceptance gate verifies result
-> Knowledge Engineering Agent drafts reusable knowledge when produced
-> Knowledge Review Agent reviews and routes approval
-> Notification Center updates owner and submitter
-> Metrics Dashboard records quality, time, failure, and reuse
```

## Core Product Objects

| Object | Purpose |
| --- | --- |
| Requirement | Durable product/business need with state, owner, source, assumptions, and acceptance path. |
| RequirementState | Field-level clarity state for user, problem, market, business model, scope, metric, and acceptance. |
| PRDDocument | Approved or draft product requirement document generated from Requirement. |
| AcceptanceCriteria | Observable criteria for product, design, engineering, test, and operations acceptance. |
| Project | Work container with owner, goal, scope, Agents, runners, tasks, decisions, and knowledge. |
| ProjectTask / KnowledgeTask | Schedulable work item for Agent or runner execution. |
| TaskResult | Structured result with output, evidence, risk, blockers, and next action. |
| SourceMaterial | Original input, document, message, meeting, file, link, or reference. |
| Agent | Durable role identity with scope, tools, permissions, and status. |
| AgentRunner | External computer execution node. |
| AgentWorkSession | A single Agent work episode with context, actions, outputs, and trace refs. |
| ToolAsset | Registered tool and approval contract. |
| SkillAsset | Registered skill package and lifecycle contract. |
| KnowledgeItem | Reviewed or draft reusable knowledge. |
| ReviewRecord | Review result for knowledge, requirement, tool, skill, permission, or release gate. |
| Decision | Human or approved system decision with owner and impact. |
| NotificationRecord | Durable user or Agent notification. |
| AuditLog | Immutable-ish trace of important state changes. |
| EvalCase / EvalRun | Quality and regression evaluation assets. |
| MetricsReport | Product, Agent, task, knowledge, and operations metrics. |

## Product Modules

### Agent Hub

Entry through Feishu, API, and future web UI. It classifies intent, captures source, asks safe clarification questions, creates Requirement, Project, SourceMaterial, KnowledgeTask, or status query.

### Requirement Center

Owns rough ideas through clarified product requirements. It stores field-level clarity state, assumptions, PRD versions, acceptance criteria, decision needs, and links to ProjectTasks.

### PRD And Decision Center

Shows product plan, business model, market positioning, scope, non-goals, open decisions, owner approvals, and downstream impact.

### Project Console

Shows project health, tasks, Agents, runners, source material, decisions, results, review status, notifications, and metrics.

### Agent Team Manager

Registers and manages business Agents, governance Agents, local builder Agents, allowed tools, allowed knowledge scopes, skill packs, role health, and capability reports.

### Scheduler And Task Center

Normalizes taskRuntime, checks required capability, tool, source, permission, review path, and acceptance path. Dispatches to eligible runners and manages claim, lease, heartbeat, retry, cancellation, and stale task repair.

### Agent Ring Console

Shows runners, heartbeat, load, available Agents, tools, repositories, data scopes, leases, failure history, and manual handoff state.

### Result Center

Displays TaskResult, output artifacts, evidence, risk, blockers, acceptance status, follow-up tasks, and writeback quality.

### Knowledge Core

Keeps SourceMaterial, KnowledgeItem, review state, graph edges, citations, confidence, sensitivity, duplicates, conflicts, and search retrieval.

### Review Center

Routes product decisions, knowledge drafts, tool requests, skill updates, permission requests, customer commitments, policy changes, and release gates to the right reviewer.

### Tool And Skill Registry

Registers tools and skills with owner, version, risk, approval, allowed Agents, tests, usage history, and rollback state.

### Quality And Evaluation Dashboard

Measures Agent success rate, task completion time, clarification completeness, acceptance pass rate, review pass rate, retry rate, failure root causes, knowledge reuse, and user satisfaction.

### Notification Center

Sends and records user, Agent, owner, reviewer, and ops notifications. Supports waiting, blocked, completed, rejected, approved, retry, and escalation states.

### Admin And Governance Console

Controls organization, roles, permissions, scopes, secrets policy, data retention, audit, backup, integration settings, and emergency disable.

### Operations And Feedback Center

Collects user feedback, launch health, operations incidents, growth experiments, usage metrics, and improvement proposals.

### API And Integration Gateway

Provides validated interfaces for Feishu, Agent Ring, web console, local CLI, material ingestion, knowledge query, task runtime, review, notification, metrics, and admin operations.

## Quality Definition

The product is mature, efficient, and high-quality only when:

- requirements can be clarified without hidden human context;
- tasks can be dispatched to eligible Agents and runners;
- results can be accepted or rejected against observable criteria;
- reusable knowledge is evidence-backed and reviewable;
- every important state change is auditable;
- failures produce repair tasks or clear owner next action;
- metrics show throughput, quality, reuse, and risk.

## Launch Blocking Rules

Do not launch if:

- Requirement cannot link to source, owner, and acceptance criteria.
- ProjectTask can dispatch without capability and permission checks.
- TaskResult can close without evidence or next action.
- Reusable knowledge can bypass Knowledge Review.
- Tool or Skill can be used without registration and owner.
- Runner can execute without heartbeat, lease, and audit.
- Human owner cannot see blocked, waiting, approved, rejected, and done states.
- Test Agent cannot run end-to-end acceptance cases.
