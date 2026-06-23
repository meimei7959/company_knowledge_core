# AI Native OS Launch Acceptance Checklist

This checklist defines formal launch acceptance. Every item must pass or have a signed exception from the human owner.

## Product Acceptance

| ID | Gate | Pass Criteria |
| --- | --- | --- |
| AC-PROD-001 | Product positioning | Product clearly states AI-native organization OS positioning and difference from knowledge base, chat bot, and project tool. |
| AC-PROD-002 | Complete role model | Human roles, eight business Agents, governance Agents, runners, tools, and skills are represented in product and docs. |
| AC-PROD-003 | Complete flow | Request-to-requirement-to-task-to-runner-to-result-to-review-to-knowledge-to-metrics flow works end to end. |
| AC-PROD-004 | No MVP scope leakage | Product does not ship as partial pilot under complete-launch claim. |

## Requirement Acceptance

| ID | Gate | Pass Criteria |
| --- | --- | --- |
| AC-REQ-001 | Requirement object | Requirement has owner, source, status, sensitivity, RequirementState, PRD, tasks, decisions, acceptance criteria, and audit. |
| AC-REQ-002 | Clarification | Missing target user/problem/scenario/market/business model/success metric/acceptance blocks approval. |
| AC-REQ-003 | PRD | PRD contains positioning, market, business model, workflows, requirements, metrics, risks, open decisions. |
| AC-REQ-004 | Decision | High-impact decisions require human owner approval. |
| AC-REQ-005 | Traceability | Requirement links to SourceMaterial, PRD, ProjectTask, TaskResult, tests, and acceptance. |

## Agent Acceptance

| ID | Gate | Pass Criteria |
| --- | --- | --- |
| AC-AGENT-001 | Eight business Agents | Each business Agent has profile, capability, tools, skill, input/output contract, and health check. |
| AC-AGENT-002 | Governance Agents | Steward, Review, and Ops Agents are separate and cannot self-approve high-impact output. |
| AC-AGENT-003 | Handoff | Every Agent handoff includes objectRef, owner, source, evidence, assumptions, blockers, decisions, acceptance, next action. |
| AC-AGENT-004 | Tool safety | Agent cannot use unregistered or unauthorized tool. |
| AC-AGENT-005 | Skill lifecycle | Skill has owner, version, tests, approval, rollout, rollback. |

## Execution Acceptance

| ID | Gate | Pass Criteria |
| --- | --- | --- |
| AC-EXE-001 | Scheduler | Every dispatchable task has taskRuntime and acceptancePath. |
| AC-EXE-002 | Runner matching | Task is assigned only to eligible runner and Agent. |
| AC-EXE-003 | Lease | Claim, heartbeat, stale, finish, retry, and cancellation work and are audited. |
| AC-EXE-004 | Result | TaskResult includes output, evidence, risk, blockers, next action, executor, runner, source links. |
| AC-EXE-005 | Manual handoff | Manual runner path still writes durable result, notification, and audit. |

## Knowledge Acceptance

| ID | Gate | Pass Criteria |
| --- | --- | --- |
| AC-KNO-001 | Source-first | Reusable knowledge cannot be produced without SourceMaterial or equivalent source reference. |
| AC-KNO-002 | Review | Knowledge Review checks structure, source, confidence, sensitivity, duplicate, conflict, graph, readability, and status. |
| AC-KNO-003 | Search | Knowledge query returns citations, confidence, and gaps. |
| AC-KNO-004 | Graph | Graph edge is traceable to source object or evidence. |

## Review And Governance Acceptance

| ID | Gate | Pass Criteria |
| --- | --- | --- |
| AC-GOV-001 | Review routes | Knowledge, requirement, decision, tool, skill, permission, release gate use correct review route. |
| AC-GOV-002 | Human approval | Verified knowledge, policy/workflow/iron rule, permission/security/customer commitments, and high-impact product decisions require human approval. |
| AC-GOV-003 | Audit | All create/update/approve/reject/claim/finish actions write audit records. |
| AC-GOV-004 | Secrets | Secret values are not stored in knowledge files or user-visible records. |

## Console Acceptance

| ID | Gate | Pass Criteria |
| --- | --- | --- |
| AC-UI-001 | Requirement Center | User can inspect requirement state, questions, answers, PRD, decisions, tasks, acceptance. |
| AC-UI-002 | Project Console | Owner can inspect project health, Agents, tasks, runners, blockers, results, reviews, notifications. |
| AC-UI-003 | Agent Team Manager | Admin can inspect role status, scope, tools, skills, health, capability. |
| AC-UI-004 | Agent Ring Console | Admin can inspect runners, heartbeat, load, leases, history, scopes. |
| AC-UI-005 | Review Center | Reviewer can act on review queue with evidence and readable summaries. |
| AC-UI-006 | Quality Dashboard | Metrics are visible by project, Agent, runner, task type, and time. |
| AC-UI-007 | Admin Console | Admin can manage permissions, integrations, assets, retention, backup, disable paths. |

## Test Acceptance

| ID | Gate | Pass Criteria |
| --- | --- | --- |
| AC-TEST-001 | Test coverage | Every ANOS-REQ has mapped test case. |
| AC-TEST-002 | E2E | TC-E2E-001 through TC-E2E-007 pass. |
| AC-TEST-003 | Negative cases | Permission, missing evidence, stale lease, missing criteria, unauthorized tool, failed notification tests pass. |
| AC-TEST-004 | Regression | Existing Feishu, task, runner, review, notification, permission, graph, retrieval tests pass. |
| AC-TEST-005 | Release gate | Critical EvalRun failure blocks release. |

## Operations Acceptance

| ID | Gate | Pass Criteria |
| --- | --- | --- |
| AC-OPS-001 | Monitoring | Failure, stale task, notification failure, runner heartbeat, and review backlog are visible. |
| AC-OPS-002 | Backup | Backup and restore procedure has latest successful record. |
| AC-OPS-003 | Feedback | User feedback links to project, requirement, Agent, result, and improvement task. |
| AC-OPS-004 | Metrics | Adoption, active Agents, completed tasks, acceptance pass, knowledge reuse, satisfaction visible. |
| AC-OPS-005 | Rollback | Tool, skill, runner, Agent, integration can be disabled or rolled back. |

## Launch Stop Conditions

Do not launch if any condition is true:

- Requirement can be approved without acceptance criteria.
- Task can be closed without TaskResult evidence.
- Runner can finish without valid lease.
- Agent can use unregistered tool.
- Reusable knowledge can bypass review.
- Human owner cannot see blockers and next action.
- Sensitive material can be exposed to unauthorized Agent or user.
- Critical end-to-end test fails.
- Backup/restore status unknown.
- Audit trail missing for write actions.

