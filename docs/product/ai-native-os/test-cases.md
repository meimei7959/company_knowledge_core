# AI Native OS Test Cases

Test IDs map to functional requirements in [Functional Requirements](requirements.md), which trace back to [Requirement Tree](requirement-tree.md). Acceptance gates are in [Acceptance Checklist](acceptance-checklist.md).

## Test Strategy

The Test Agent must cover:

- end-to-end workflows;
- module behavior;
- Agent collaboration;
- permissions and sensitivity;
- runner dispatch;
- review and approval;
- notifications;
- data consistency;
- metrics;
- regression.

No feature is accepted without at least one positive test, one negative or edge test, and one acceptance criterion check when user-facing.

## End-To-End Tests

| ID | Covers | Case | Expected |
| --- | --- | --- | --- |
| TC-E2E-001 | ANOS-REQ-001 to ANOS-REQ-152 | User submits rough product idea in Feishu. Product Manager Agent clarifies, creates RequirementState, PRD, ProjectTasks. Scheduler dispatches. Runner finishes. Test Agent verifies. Knowledge Review handles reusable lesson. Notifications and metrics update. | Complete chain closes with source, owner, evidence, audit, metrics, and readable notifications. |
| TC-E2E-002 | ANOS-REQ-001, 003, 080, 090 | User submits sensitive customer document. | SourceMaterial created with sensitivity; unauthorized Agents cannot access; review/approval path required. |
| TC-E2E-003 | ANOS-REQ-010 to 024 | Requirement changes after tasks are created. | Impact review lists affected tasks, designs, tests, PRD version, and owner decision. |
| TC-E2E-004 | ANOS-REQ-050 to 073 | Runner claims task, lease expires, another runner tries finish. | Invalid finish blocked; stale lease visible; repair/escalation task created. |
| TC-E2E-005 | ANOS-REQ-080 to 093 | Knowledge draft has weak evidence. | Knowledge Review requests changes; no verified index publish. |
| TC-E2E-006 | ANOS-REQ-100 to 114 | Skill update proposed for Product Manager Agent. | SkillAsset version requires tests and approval; failed eval blocks rollout. |
| TC-E2E-007 | ANOS-REQ-120 to 142 | Completed task notification fails. | NotificationRecord failure stored; Ops repair path created; owner can see status. |

## Agent Hub Tests

| ID | Requirement | Case | Expected |
| --- | --- | --- | --- |
| TC-HUB-001 | ANOS-REQ-001 | Submit plain text idea. | Requirement or project intake created; user sees confirmation. |
| TC-HUB-002 | ANOS-REQ-001 | Submit document link. | SourceMaterial registered and linked. |
| TC-HUB-003 | ANOS-REQ-002 | Submit ambiguous message. | System asks clarification instead of guessing. |
| TC-HUB-004 | ANOS-REQ-003 | Submit sensitive message from unauthorized user. | Restricted route; no unauthorized exposure. |
| TC-HUB-005 | ANOS-REQ-004 | View generated card. | Card shows readable title, status, owner, next action. |
| TC-HUB-006 | ANOS-REQ-005 | Click long-running action. | Callback returns quickly; async task and notification follow. |
| TC-HUB-007 | ANOS-REQ-006 | Bind to ambiguous project name. | Disambiguation options shown. |

## Requirement And PRD Tests

| ID | Requirement | Case | Expected |
| --- | --- | --- | --- |
| TC-REQ-001 | ANOS-REQ-010 | Create Requirement from Agent Hub. | Required fields present and audit written. |
| TC-REQ-002 | ANOS-REQ-011 | Missing business model. | RequirementState marks businessModel as missing. |
| TC-REQ-003 | ANOS-REQ-012 | Product Manager Agent clarification round. | 1-3 focused questions generated and stored. |
| TC-REQ-004 | ANOS-REQ-013 | PRD includes market claim without source. | Claim is marked assumption/inference or blocked. |
| TC-REQ-005 | ANOS-REQ-014 | Generate PRD v1 then revise. | Versions preserved and linked. |
| TC-REQ-006 | ANOS-REQ-015 | Approve Requirement without acceptance criteria. | Approval blocked with readable reason. |
| TC-REQ-007 | ANOS-REQ-016 | Create ProjectTasks from PRD. | Tasks link back to Requirement and criteria. |
| TC-REQ-008 | ANOS-REQ-012, ANOS-REQ-020 | 产品经理 Agent 写 PRD 时缺少 `prd-high-quality-generation` 分级协议证据。 | PRD 质量门禁失败；补齐默认 `light` 三项摘要，且 `requirementClarifier` 必须包含第一性原理拆解和苏格拉底问题记录，复杂任务 `full` 六工序证据后才能审批。 |
| TC-PRD-001 | ANOS-REQ-020 | Generate full PRD. | Contains required sections. |
| TC-PRD-002 | ANOS-REQ-021 | Pricing decision needed. | Decision request created for human owner. |
| TC-PRD-003 | ANOS-REQ-022 | Non-goals absent. | PRD quality gate fails. |
| TC-PRD-004 | ANOS-REQ-023 | Acceptance criterion not observable. | Test Agent blocks acceptance. |
| TC-PRD-005 | ANOS-REQ-024 | PRD changes after implementation starts. | Impact review generated. |
| TC-PRD-006 | ANOS-REQ-020, ANOS-REQ-023 | 完整 PRD 交付包缺少测试用例或开发交付包。 | 产品经理 Agent 不能标记交付完成；完整上线任务必须使用 `full` 协议。 |
| TC-PRD-007 | ANOS-REQ-020, ANOS-REQ-040 | PRD 辩论流程试图把 Controller 或 Reviewer 创建为公司级 Agent。 | 注册被阻止；Controller 和 Reviewer 只能作为产品经理 Agent 内部质量步骤出现。 |

## Project Console Tests

| ID | Requirement | Case | Expected |
| --- | --- | --- | --- |
| TC-PROJ-001 | ANOS-REQ-030 | Project owner opens console. | Health, blockers, next action visible. |
| TC-PROJ-002 | ANOS-REQ-031 | View Agent roster. | Eight business Agents and governance Agents show scope and status. |
| TC-PROJ-003 | ANOS-REQ-032 | Trace result to source. | Chain from TaskResult to SourceMaterial is visible. |
| TC-PROJ-004 | ANOS-REQ-033 | View active work queue. | Task runtime, runner, lease, status shown. |
| TC-PROJ-005 | ANOS-REQ-034 | Blocker exists. | Blocker has owner, reason, next action, notification state. |

## Agent Team Tests

| ID | Requirement | Case | Expected |
| --- | --- | --- | --- |
| TC-AGENT-001 | ANOS-REQ-040 | Register Product Manager Agent. | Profile includes scope, tools, skills, owner, status. |
| TC-AGENT-002 | ANOS-REQ-040 | Register all eight business Agents. | Agent Team Manager displays all roles. |
| TC-AGENT-003 | ANOS-REQ-041 | Governance Agent shown. | Separate from business execution roles. |
| TC-AGENT-004 | ANOS-REQ-042 | Capability report missing requirement_clarification. | Scheduler does not assign product discovery. |
| TC-AGENT-005 | ANOS-REQ-043 | Agent missing required skill. | Health check creates repair task. |
| TC-AGENT-006 | ANOS-REQ-044 | Agent calls unregistered tool. | Blocked and audited. |
| TC-AGENT-007 | ANOS-REQ-045 | Skill update without test evidence. | Approval blocked. |

## Scheduler And Runner Tests

| ID | Requirement | Case | Expected |
| --- | --- | --- | --- |
| TC-SCH-001 | ANOS-REQ-050 | Create product discovery task. | taskRuntime includes product acceptance path. |
| TC-SCH-002 | ANOS-REQ-051 | No eligible runner. | Task goes waiting_runner with reason. |
| TC-SCH-003 | ANOS-REQ-052 | Finish without lease token. | Finish rejected. |
| TC-SCH-004 | ANOS-REQ-053 | Stale lease. | Alert and repair path created. |
| TC-SCH-005 | ANOS-REQ-054 | Engineering task has no test evidence. | Cannot close. |
| TC-SCH-006 | ANOS-REQ-055 | Knowledge task lacks SourceMaterial. | Cannot close. |
| TC-SCH-007 | ANOS-REQ-056 | Product task lacks market/business model. | Cannot close. |
| TC-SCH-008 | ANOS-REQ-050, ANOS-REQ-054 | Project enters Release Candidate or launch closeout for software/Agent product needing soft copyright. | Project Manager Agent creates a `software_copyright_material_pack` task for Knowledge Engineering Agent; Project Manager does not generate or finalize the materials itself. |
| TC-RUN-001 | ANOS-REQ-060 | Runner registers capabilities. | Console shows machine, owner, heartbeat, load, scopes. |
| TC-RUN-002 | ANOS-REQ-061 | Runner has active leases. | Current leases and history visible. |
| TC-RUN-003 | ANOS-REQ-062 | Manual handoff completes task. | TaskResult, notification, audit written. |
| TC-RUN-004 | ANOS-REQ-063 | Runner requests unauthorized repo. | Access blocked and audited. |

## Result And Knowledge Tests

| ID | Requirement | Case | Expected |
| --- | --- | --- | --- |
| TC-RES-001 | ANOS-REQ-070 | TaskResult missing evidenceRefs. | Closure blocked. |
| TC-RES-002 | ANOS-REQ-071 | Product task result submitted. | Product acceptance path displayed. |
| TC-RES-003 | ANOS-REQ-072 | Result rejected. | Follow-up task or retry reason created. |
| TC-RES-004 | ANOS-REQ-073 | Same Agent failure repeats. | Improvement proposal/eval task created. |
| TC-KNO-001 | ANOS-REQ-080 | Knowledge draft from raw message only. | Blocked until SourceMaterial exists. |
| TC-KNO-002 | ANOS-REQ-081 | KnowledgeItem missing confidence. | Review pass blocked. |
| TC-KNO-003 | ANOS-REQ-082 | Duplicate/conflict detected. | Review routes conflict/clarification. |
| TC-KNO-004 | ANOS-REQ-083 | Search no verified answer. | Reviewable sources and gap returned. |
| TC-KNO-005 | ANOS-REQ-084 | Graph edge missing reason. | Edge rejected. |
| TC-KNO-006 | ANOS-REQ-080, ANOS-REQ-090 | Knowledge Engineering Agent prepares software copyright material pack. | Work package maps application form, source program material, manual/design document, applicant proof, ownership materials, screenshots, code evidence, missing items, and human finalization gate without fabricating legal facts or manual body text. |

## Review, Tool, Skill Tests

| ID | Requirement | Case | Expected |
| --- | --- | --- | --- |
| TC-REV-001 | ANOS-REQ-090 | High-risk tool request. | Routed to tool owner/human approval. |
| TC-REV-002 | ANOS-REQ-091 | Agent self-approves policy. | Blocked. |
| TC-REV-003 | ANOS-REQ-092 | Review change request. | Actionable comment with evidence and exact change. |
| TC-REV-004 | ANOS-REQ-093 | Review completed. | Requester and owner notified. |
| TC-REG-001 | ANOS-REQ-100 | ToolAsset missing owner. | Registration blocked. |
| TC-REG-002 | ANOS-REQ-101 | SkillAsset missing rollback path. | Approval blocked. |
| TC-REG-003 | ANOS-REQ-102 | Agent uses registered skill. | Usage recorded in AgentRun or TaskResult. |
| TC-REG-004 | ANOS-REQ-100, ANOS-REQ-102 | `china-software-copyright-submission-pack` is registered to Project Manager Agent instead of Knowledge Engineering Agent. | Role check fails; Project Manager may trigger and track the task, but material pack generation belongs to Knowledge Engineering Agent. |

## Metrics, Notification, Admin, Ops Tests

| ID | Requirement | Case | Expected |
| --- | --- | --- | --- |
| TC-MET-001 | ANOS-REQ-110 | Complete multiple tasks. | Dashboard shows throughput and completion time. |
| TC-MET-002 | ANOS-REQ-111 | Agent has failures and passes. | Agent quality metrics update. |
| TC-MET-003 | ANOS-REQ-112 | Requirement clarification completes. | Completeness and decision latency update. |
| TC-MET-004 | ANOS-REQ-113 | Knowledge reused in answer. | Reuse metric updates. |
| TC-MET-005 | ANOS-REQ-114 | EvalRun fails critical router case. | Release gate blocked. |
| TC-NOT-001 | ANOS-REQ-120 | Important state changes. | NotificationRecord created. |
| TC-NOT-002 | ANOS-REQ-121 | User receives notification. | Readable summary before raw ids. |
| TC-NOT-003 | ANOS-REQ-122 | Notification delivery fails. | Repair path created. |
| TC-ADM-001 | ANOS-REQ-130 | Admin changes permission. | Change permission-checked and audited. |
| TC-ADM-002 | ANOS-REQ-131 | Disable runner. | New tasks not assigned; active work paused/reassigned. |
| TC-ADM-003 | ANOS-REQ-132 | Secret entered in knowledge draft. | Secret storage blocked or redacted to secretRef. |
| TC-ADM-004 | ANOS-REQ-133 | View backup status. | Latest backup and restore state visible. |
| TC-OPS-001 | ANOS-REQ-140 | User rejects result with feedback. | Feedback links to requirement/task/Agent and improvement task. |
| TC-OPS-002 | ANOS-REQ-141 | Product Operator opens dashboard. | Adoption, tasks, reuse, satisfaction visible. |
| TC-OPS-003 | ANOS-REQ-142 | Start experiment without metric. | Blocked. |

## API And Integration Tests

| ID | Requirement | Case | Expected |
| --- | --- | --- | --- |
| TC-API-001 | ANOS-REQ-150 | Create Requirement through API. | Validated object created and returned. |
| TC-API-002 | ANOS-REQ-150 | Unauthorized review API call. | Fails safely. |
| TC-API-003 | ANOS-REQ-151 | Feishu and web console read same task. | Status and next action match. |
| TC-API-004 | ANOS-REQ-152 | API write updates Requirement. | AuditLog created. |

## Regression Gates

Every release must re-run existing coverage for:

- Feishu project creation and card callbacks.
- ProjectTask claim, lease, finish.
- Knowledge review pass/change/reject/human approval.
- Notification records.
- Permission checks.
- Graph export.
- Retrieval and citation.
- DeepSeek/router intent fixtures when enabled.
