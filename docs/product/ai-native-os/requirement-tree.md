# AI Native OS Requirement Tree

This document defines real product requirements before they are decomposed into functional requirements.

The detailed `ANOS-REQ-*` items in [Functional Requirements](requirements.md) are implementation-facing functional requirements. They are not the whole requirement set by themselves.

## Requirement Definition

A requirement states:

```txt
who needs what outcome, in what real scenario, because of what pain or goal,
under what constraints, with what business value, and how success will be accepted
```

## Business Requirements

| ID | Business Requirement | Why It Matters | Success Signal |
| --- | --- | --- | --- |
| BR-001 | The company needs an operating system for AI-native work so human requests, Agent work, local runners, reviews, and reusable knowledge form one traceable production loop. | Without this, Agent work stays scattered across chats, files, local computers, and hidden human memory. | A request can be traced from intake to requirement, task, runner, result, review, knowledge, notification, and metrics. |
| BR-002 | The company needs high-quality Agent output that can be accepted, reviewed, reused, and improved. | Agent speed without evidence and quality gates creates rework and knowledge pollution. | Outputs include evidence, acceptance criteria, review path, and quality metrics. |
| BR-003 | The company needs distributed local execution without losing central governance. | Codex, Claude, local models, and tools run on different computers, but the organization needs one source of truth. | Runners execute only authorized tasks and write back TaskResult, audit, and notification. |
| BR-004 | The company needs reusable organizational knowledge from real work. | Knowledge must come from evidence-backed work results, not raw dumps or unsupported summaries. | SourceMaterial and TaskResult can produce reviewed KnowledgeItem with citations and confidence. |
| BR-005 | The company needs product, engineering, test, design, operations, and governance Agents to collaborate as a team. | A single generic Agent cannot reliably own all roles and quality boundaries. | Eight business Agents and governance Agents have distinct contracts, handoffs, and health checks. |

## User Roles

| ID | Role | Context | Core Job |
| --- | --- | --- | --- |
| ROLE-001 | Requirement Submitter | Has idea, customer request, document, incident, or task. | Submit work without knowing system structure and receive clear next action. |
| ROLE-002 | Project Owner | Owns scope, approval, and final direction. | See project state, decisions, risks, acceptance, and blockers. |
| ROLE-003 | Product Manager Agent | Clarifies demand and product direction. | Turn rough input into requirement tree, PRD, acceptance criteria, and task proposals. |
| ROLE-004 | Project Manager Agent | Coordinates execution. | Convert product package into Agent task queue, dependency plan, risk tracking, and launch readiness. |
| ROLE-005 | Design Agent | Designs user experience. | Convert product requirements into flows, page states, and design acceptance criteria. |
| ROLE-006 | Development Agent | Builds product. | Implement approved functional requirements with evidence and tests. |
| ROLE-007 | Test Agent | Verifies product quality. | Derive and execute tests from requirements and acceptance criteria. |
| ROLE-008 | Operations Agent | Runs launch and improvement loops. | Collect feedback, monitor operations metrics, and create improvement tasks. |
| ROLE-009 | Knowledge Query Agent | Answers from reviewed knowledge. | Return cited answers, confidence, and gaps. |
| ROLE-010 | Knowledge Engineering Agent | Converts source to reusable knowledge. | Build evidence packets and reviewable knowledge drafts. |
| ROLE-011 | Knowledge Review Agent | Protects reusable knowledge quality. | Review evidence, sensitivity, conflicts, and approval route. |
| ROLE-012 | Knowledge Steward Agent | Protects structure and governance boundaries. | Classify object model, policy, registry, and scope issues. |
| ROLE-013 | Knowledge Ops Agent | Protects runtime operations. | Handle connectors, gateway, permissions, audit, eval, sync, backup, and recovery. |
| ROLE-014 | System Admin | Operates the platform. | Configure users, Agents, runners, tools, skills, integrations, audit, and recovery. |
| ROLE-015 | Agent Ring Runner Admin | Operates distributed computers. | Register runners, monitor leases, scopes, heartbeat, and failures. |

## User Scenarios And Requirements

| ID | Role | Scenario | Pain / Goal | User Requirement | Product Requirement |
| --- | --- | --- | --- | --- | --- |
| UREQ-001 | Requirement Submitter | Submits a rough idea in Feishu. | Does not know how to write PRD or pick Agents. | Submit in natural language and get guided clarification plus visible status. | Product must classify intent, create SourceMaterial/Requirement, ask focused questions, and notify next action. |
| UREQ-002 | Product Manager Agent | Receives vague demand. | Feature lists can be mistaken for requirements. | Build requirement tree before functional decomposition. | Product must store business, user, product, functional, non-functional, test, and acceptance mapping. |
| UREQ-003 | Project Owner | Reviews product direction. | Cannot approve work if assumptions and tradeoffs are hidden. | See PRD, decisions needed, assumptions, evidence, risks, and acceptance criteria. | Product must expose PRD versions, Decision records, evidence, and approval state. |
| UREQ-004 | Project Manager Agent | Receives complete product package. | Needs to coordinate many Agents without losing traceability. | Convert product package into executable task queue with owners and blockers. | Product must link requirements to ProjectTasks, Agent roles, dependencies, and launch gates. |
| UREQ-005 | Development Agent | Starts implementation. | Wrong or incomplete requirements cause rework. | Receive scoped task with context, acceptance criteria, allowed tools, dependencies, and tests. | Product must generate taskRuntime and handoff package from approved functional requirements. |
| UREQ-006 | Test Agent | Plans verification. | Cannot test vague success statements. | Get observable acceptance criteria mapped to requirements. | Product must map each functional requirement to test cases and acceptance gates. |
| UREQ-007 | Design Agent | Designs flows. | Needs user scenario and constraints before UI decisions. | Receive target roles, workflows, non-goals, states, and usability criteria. | Product must expose product requirements and scenario context to design tasks. |
| UREQ-008 | Agent Ring Runner Admin | Runs local execution nodes. | Distributed execution can drift from central state. | See runner eligibility, lease, heartbeat, scope, and failure state. | Product must provide Agent Ring Console and enforce runner authorization. |
| UREQ-009 | Knowledge Engineering Agent | Turns work results into reusable knowledge. | Raw material and task outputs can lack evidence. | Receive source refs and result evidence before drafting knowledge. | Product must require SourceMaterial and TaskResult links for knowledge drafts. |
| UREQ-010 | Knowledge Review Agent | Reviews reusable knowledge. | Low-quality or sensitive knowledge can pollute reuse. | Review structure, evidence, confidence, sensitivity, duplicate, conflict, and approval path. | Product must route KnowledgeItem through Review Center before promotion. |
| UREQ-011 | Knowledge Query Agent | Answers employee or Agent questions. | Answers without citations are unsafe. | Return cited answer, confidence, and gap when no verified answer exists. | Product must search reviewed knowledge and expose citation/gap state. |
| UREQ-012 | Operations Agent | Runs launch and improvement. | Product can ship without feedback and quality loop. | See adoption, feedback, task quality, failures, and improvement opportunities. | Product must provide Operations and Quality Dashboard metrics. |
| UREQ-013 | System Admin | Governs platform. | Unauthorized tools, skills, runners, or secrets can create risk. | Configure permissions, tool/skill approval, runner access, audit, backup, and disable paths. | Product must provide Admin and Governance Console with audit-backed write controls. |
| UREQ-014 | Human Reviewer | Reviews high-impact decisions. | Agent must not self-approve customer/security/policy/verified knowledge decisions. | Receive clear review package with evidence, risk, recommendation, and action buttons. | Product must route high-impact decisions to human approval. |
| UREQ-015 | Team Member | Searches for prior work knowledge. | Prior decisions and lessons are hard to find. | Ask a question and get reviewed answer, source, confidence, and related gaps. | Product must provide Knowledge Query with citations, permissions, and follow-up KnowledgeTask creation. |

## Functional Requirement Mapping

| User Requirement | Functional Requirement Areas |
| --- | --- |
| UREQ-001 | ANOS-REQ-001 to ANOS-REQ-006, ANOS-REQ-120 to ANOS-REQ-122 |
| UREQ-002 | ANOS-REQ-010 to ANOS-REQ-016, ANOS-REQ-020 to ANOS-REQ-024 |
| UREQ-003 | ANOS-REQ-020 to ANOS-REQ-024, ANOS-REQ-090 to ANOS-REQ-093 |
| UREQ-004 | ANOS-REQ-030 to ANOS-REQ-034, ANOS-REQ-050 to ANOS-REQ-056 |
| UREQ-005 | ANOS-REQ-050 to ANOS-REQ-056, ANOS-REQ-070 to ANOS-REQ-073 |
| UREQ-006 | ANOS-REQ-023, ANOS-REQ-110 to ANOS-REQ-114 |
| UREQ-007 | ANOS-REQ-020 to ANOS-REQ-024, ANOS-REQ-040 to ANOS-REQ-045 |
| UREQ-008 | ANOS-REQ-060 to ANOS-REQ-063 |
| UREQ-009 | ANOS-REQ-080 to ANOS-REQ-084 |
| UREQ-010 | ANOS-REQ-090 to ANOS-REQ-093 |
| UREQ-011 | ANOS-REQ-083, ANOS-REQ-080 to ANOS-REQ-084 |
| UREQ-012 | ANOS-REQ-110 to ANOS-REQ-114, ANOS-REQ-140 to ANOS-REQ-142 |
| UREQ-013 | ANOS-REQ-100 to ANOS-REQ-102, ANOS-REQ-130 to ANOS-REQ-133, ANOS-REQ-150 to ANOS-REQ-152 |
| UREQ-014 | ANOS-REQ-021, ANOS-REQ-090 to ANOS-REQ-093 |
| UREQ-015 | ANOS-REQ-083, ANOS-REQ-120 to ANOS-REQ-122 |

## Requirement Quality Gate

A functional requirement is ready for development only when:

- it maps to a user requirement in this document;
- the user requirement maps to a business requirement;
- acceptance criteria are observable;
- tests exist in [Test Cases](test-cases.md);
- launch gate exists in [Acceptance Checklist](acceptance-checklist.md) when user-facing or high-risk;
- owner, source, assumptions, and decision needs are visible.

