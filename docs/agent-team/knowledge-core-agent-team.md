# Knowledge Core Agent Team

## Purpose

The knowledge core Agent team maintains the stable, durable operation of the company knowledge engineering foundation.

Knowledge Engineering Agent is the umbrella execution and governance workflow owner for source-material processing. It reads task cards and SourceMaterial, uses reader tools and local skills, builds evidence packets, writes TaskResult, drafts KnowledgeItem candidates, routes review and governance checks, handles approval paths, writes allowed knowledge states, updates indexes, and emits notifications.

Review, Steward, and Ops are sub-agent roles inside the Knowledge Engineering Agent workflow, not independent standalone Agents:

- Steward sub-agent role: rules, boundaries, classification, structure.
- Review sub-agent role: quality gate, evidence, conflict, approval routing.
- Ops sub-agent role: connector, gateway, validation, evaluation, audit, sync, recovery.

Knowledge Query Agent is not another governance owner. It is the lightweight runtime role that serves already published knowledge behind the bot and API.

Every created project also gets project-scoped execution Agents. The default initialization owner is `agent.<project>.project-manager`, shown to the user as the Project Manager Agent or Project Initialization Agent. It is project-scoped, not a company governance Agent.

The final human owner for the company knowledge core is 梅晓华.

Every project has a human project owner. Agent work may complete most project tasks, but the project owner remains accountable for project direction, scope, approvals, and final responsibility.

Agents may propose, execute, review, route, and block. Agents do not replace human owners for high-impact knowledge, tool, permission, security, policy, customer, or cross-team decisions.

## Team Members

| Agent | Primary Question | Main Ownership |
| --- | --- | --- |
| Knowledge Engineering Agent | How does this material become governed, source-backed, reusable knowledge? | Material intake, evidence packet, structured draft, TaskResult writeback, review routing, governance checks, approval path, allowed writeback, indexing, notification |
| Project Manager Agent | Is this project ready to start real work? | Project initialization closure, launch plan, task decomposition, Agent team, Runner handoff, result notification |
| Product Manager Agent | What should we build, for whom, why now, and how will we know it works? | Product discovery, market research, requirement clarification, PRD, acceptance criteria |
| Knowledge Query Agent | What does the company already know? | Fast service-side retrieval, citations, query logs, delivery state, audit |

Knowledge Engineering Agent profile:

- [Company Knowledge Core Knowledge Engineering Agent](../../agents/agent.company-knowledge-core.knowledge-engineering.md)
- [Knowledge Engineering Agent Skill Pack](knowledge-engineering-agent-skill-pack.md)
- [Knowledge Ingest Orchestration Workflow](../workflows/knowledge-ingest-orchestration.md)

Project Manager Agent profile is generated per project during project creation. Its default id is `agent.<project>.project-manager`.

Product Manager Agent is a company-level role. Its default id is `agent.company.product-manager`. A project-scoped actor such as `agent.<project-id>.product-manager` may execute project tasks, but the role identity and operating spec stay company-level.

Product Manager Agent reference:

- [Product Manager Agent Role And Skill Pack](product-manager-agent-role-and-skill-pack.md)

Knowledge Query Agent reference:

- [Knowledge Query Agent Role](knowledge-query-agent-role.md)

Project Manager Agent responsibilities:

- Own `ProjectTask` items with `taskType: project_initialization`.
- Read the generated `launch.md`, project record, approval status, and repo/group/Agent intake fields.
- Convert missing launch data into concrete clarification, approval, or execution tasks.
- Decide whether initialization can proceed through Agent Ring or needs manual runner handoff.
- Keep startup milestones limited to M0 intake, M1 approval/ownership, M2 initialization, and M3 first work queue.
- Propose business milestones only after reading project facts and getting human owner confirmation.
- Coordinate project-scoped knowledge engineering and executor Agents without becoming their reviewer.
- Include Product Manager Agent by default unless first intake clearly says product work is already complete or not needed.
- Assign product requirement clarification to Product Manager Agent or a named human product owner, not to the generic Project Manager Agent.
- Treat requested frontend/backend/test/ops/domain roles as candidate Agents or first ProjectTasks until runner, permission, and ownership are confirmed.
- Verify repository initialization, project group binding, Agent roster, Review rules, and first milestone.
- Write or require a `TaskResult` with evidence, risks, blockers, and next action before the project is considered launched.
- Notify requester and project owner when initialization is done, blocked, or waiting for approval.

Project Manager Agent boundaries:

- Does not approve its own high-impact output.
- Does not publish reusable knowledge without the Knowledge Engineering Agent review sub-agent gate.
- Does not create or use unregistered tools.
- Does not hide missing repo, group, Runner, or approval state behind a green project status.
- Does not replace the human project owner.

## Project Manager Agent Initialization

Project Manager Agent initialization is closed only when the Agent has read the launch context, verified startup state, written result evidence, and produced the first executable task path.

Required tools:

- `tool.zhenzhi-knowledge`: sync pull, start, task pull, task finish, finish, sync push, status, audit search.
- Agent Ring runner registry and lease API through the central processor.
- Git/repository inspection through the selected Runner; read-only until approved changes are allowed.
- Feishu project group, approval, and notification gateway through Agent Hub.
- Knowledge Review queue for reusable knowledge, policy, permission, or tool outputs.

Initialization workflow:

```txt
Pull context
-> read project.md / launch.md / project_initialization task / agents.md / tools.md
-> verify M0-M3 startup milestones
-> inspect existing repo or prepare new repo creation checklist
-> verify default Agent team and product manager decision
-> verify project group, approval, Runner/manual handoff
-> create or list first ProjectTasks
-> write TaskResult and AgentRun/manual handoff record
-> notify requester and project owner
```

Completion criteria:

- Project draft and `launch.md` match the current intake.
- Human project Owner and approval state are explicit.
- Existing repo is inspected, or new repo creation is represented as an approved/pending action.
- README, AGENTS, review rules, and project directory expectations are ready or blocked with owner.
- Product Manager Agent decision is recorded, including skip reason when product is not needed.
- Project group is created, bound, deliberately skipped, or blocked with owner.
- Agent team has allowed project scope and clear role boundaries.
- Runner or manual handoff path is explicit.
- First ProjectTasks exist, or every missing first task has blocker, owner, and next action.
- `TaskResult`, `AgentRun`/manual handoff record, notification, and audit trail are written.

Evaluation result:

| Result | Meaning |
| --- | --- |
| `pass` | Completion criteria are satisfied, or remaining gaps have owner, blocker reason, and next action. |
| `blocked` | Repo access, project Owner, approval, Runner, or required context is missing and no safe manual path exists. |
| `needs_human_approval` | Repo creation, permission changes, member invitations, customer commitments, policy changes, or high-risk tools are required. |
| `needs_repair` | TaskResult, AgentRun, notification, audit trail, first task list, or `launch.md` status is missing or inconsistent. |

## Project Manager Agent Operating Loop

After initialization, Project Manager Agent becomes the project follow-up owner. It does not do every task; it keeps ownership, evidence, risks, and next actions moving.

Operating cadence:

- Daily: inspect active tasks, Runner lease/heartbeat, blockers, approvals, due dates, and unread project material.
- Twice weekly: send project progress, risk, decision, and next-action summary to project Owner and project group.
- Weekly: review milestone health, stale tasks, blocked approvals, tool/permission gaps, and knowledge capture quality.
- On every TaskResult: close, create follow-up ProjectTask, request repair, send to Review, or escalate.

Progress control:

- Every active task must have owner, expected output, status, due/review date, and next action.
- Milestone progress is based on accepted TaskResult and evidence, not chat optimism.
- Scope, priority, date, permission, or customer-commitment changes must become Decision records or approval requests.
- Product discovery, implementation, test, ops, material ingest, tool request, and review-prep work stay separate when ownership differs.

Risk radar:

| Risk | Signal | Action |
| --- | --- | --- |
| Schedule | due date passed, milestone lacks evidence, task age grows | mark at_risk, assign owner, update next action |
| Ownership | missing owner, unreachable owner, stale Runner | alert Owner/Ops, reassign or manual handoff |
| Dependency | approval, repo access, tool permission, product decision, customer input blocked | create blocker record and decision request |
| Scope | unapproved work appears, requirement conflict, Product Manager output missing | create Decision/approval request |
| Quality | missing evidence/tests, Review rejection, repeated repair | request repair or Review/Steward support |
| Knowledge | lesson/decision not captured, reusable output bypasses Review | route to Knowledge Review |
| Communication | group not bound, notification failed, Owner unseen blocker | resend/escalate through Agent Hub |

Status report format:

```txt
state: on_track | at_risk | blocked | needs_decision
progress: <what changed since last update>
activeTasks: <owner / status / due or review date / next action>
risks: <severity / owner / needed decision / deadline>
decisionsNeeded: <human owner decisions>
nextActions: <3-5 actions>
evidence: <TaskResult / AgentRun / Review / audit refs>
```

## Feishu Entry Model

The existing knowledge engineering bot is the front door for Agent work.

It should be presented to employees as an Agent Hub, with two context modes:

```txt
Private chat
-> Company Agent Hub mode
-> Project creation, knowledge lookup, token requests, tool/skill requests, Agent routing

Project group chat
-> Project assistant mode
-> Project materials, meeting notes, project Agent coordination, review routing, handoff
```

Do not create one Feishu bot for every company Agent by default. One bot should route through Agent Gateway to the right Agent role, runtime, project context, permissions, and audit path.

Recommended menu configuration:

- [Agent Hub Feishu Menu](agent-hub-feishu-menu.md)

Employee-facing usage guide:

- [桢知 Agent Hub 使用手册](../guides/agent-hub-user-guide.md)

Menu clicks are shortcuts only. They do not grant permission or bypass review.

## Tool Use And Result Storage

Tool use, project writeback, knowledge publication, and status promotion are separate decisions.

```txt
Tool call
-> result returned to requester
-> optional project draft writeback
-> optional knowledge draft
-> Review Gate
-> human approval for verified/approved/active/high-risk outcomes
```

Default rule:

- Low-risk registered tools can be discovered and dry-run broadly.
- High-risk or external side-effect execution requires explicit approval.
- Tool results are not reusable knowledge by default.
- Project writeback requires project membership or owner approval.
- Knowledge publication requires review and the correct human owner approval.

## Human Ownership

| Scope | Human Owner Rule | Agent Role |
| --- | --- | --- |
| Company knowledge core | 梅晓华 is final human owner | Agents maintain, review, operate, and escalate |
| Project | Project owner is final human owner | Agents execute project work and produce reviewable evidence |
| ToolAsset | Tool owner is accountable | Agents check manifest, risk, approval, and runtime use |
| SkillAsset | Skill owner is accountable | Agents check scope, applicability, and review status |
| Policy or permission | Human approval owner is accountable | Agents draft, review, enforce, and audit |

## Collaboration Model

```txt
Proposal or runtime signal
-> Knowledge Engineering Agent steward sub-agent classifies scope and ownership when needed
-> Knowledge Engineering Agent review sub-agent checks quality, source, risk, conflict, and approval route
-> Knowledge Engineering Agent ops sub-agent enforces registry, permission, gateway, audit, eval, and sync behavior
-> Human reviewer approves only when policy requires it
-> Knowledge Engineering Agent ops sub-agent records durable status changes and operational evidence
```

## Normal Knowledge Write Flow

```txt
Human or Agent submits candidate
-> Knowledge Engineering Agent extracts source material into TaskResult and KnowledgeItem draft when raw material processing is needed
-> Scheduler evaluates TaskResult and creates review, retry, or repair follow-up task
-> Knowledge Engineering Agent review sub-agent checks structure, source, confidence, scope, sensitivity, duplicate risk, and conflict risk
-> Knowledge Engineering Agent steward sub-agent resolves unclear ownership, scope, or object boundary
-> Knowledge Engineering Agent review sub-agent returns pass_as_observed, needs_clarification, needs_human_approval, conflict_detected, or reject
-> Knowledge Engineering Agent ops sub-agent records AuditLog and ensures index/gateway state reflects the allowed status
-> Human owner remains accountable for any verified, approved, active, high-risk, or cross-team outcome
```

## Project Initialization Flow

```txt
Agent Hub receives create-project intent
-> DeepSeek extracts fields and asks for missing required data
-> Project draft + launch.md + project Agent roster
-> project_initialization ProjectTask assigned to Project Manager Agent
-> owner approval when required
-> Scheduler assigns to matching Agent Ring runner, or marks waiting_runner
-> Project Manager Agent verifies repo, group, default Agent team, Runner, Review rules, and startup milestones
-> Product clarification goes to Product Manager Agent by default, or is skipped only when launch.md records a no-product reason
-> Project Manager Agent turns other requested roles into candidate Agents or first ProjectTasks
-> TaskResult + AgentRun/manual handoff record + first ProjectTask list
-> requester/project owner notification
-> project enters active work through Scheduler dispatch of first ProjectTasks
```

## Skill And Tool Registry Flow

```txt
SkillAsset or ToolAsset manifest submitted
-> Knowledge Engineering Agent steward sub-agent classifies public, domain, project, or personal/experimental scope
-> Knowledge Engineering Agent review sub-agent checks owner, source, use boundary, risk, side effects, sensitive data, duplicate risk, and reviewer readability
-> Human Tool Owner or Security Reviewer approves when required
-> Knowledge Engineering Agent ops sub-agent allows runtime use only after registry status, Agent permission, project permission, approval, and audit rules pass
```

## Runtime Tool Invocation Flow

```txt
Agent requests tool use
-> Knowledge Engineering Agent ops sub-agent / Gateway checks ToolAsset registry entry
-> Check Agent identity, project, scope, status, risk, required approval, and audit requirement
-> Block unregistered, blocked, deprecated, over-scoped, or unapproved high-risk tools
-> Execute only with minimum required permission
-> Write AgentRun and AuditLog evidence
```

## Conflict Handling

```txt
Review or Ops finds conflict
-> Knowledge Engineering Agent review sub-agent creates or references ConflictRecord
-> Knowledge Engineering Agent steward sub-agent decides whether conflict is object-model, policy, registry, or project-boundary related
-> Project Owner, Knowledge Reviewer, Tool Owner, or Security Reviewer resolves based on object type
-> Knowledge Engineering Agent ops sub-agent records final status change and audit trail
```

## Staleness And Quality Flow

```txt
Knowledge Engineering Agent ops sub-agent runs stale scan, eval, metrics, or validation
-> Failed or stale target becomes IssueRecord, ReviewRecord, or ConflictRecord candidate
-> Knowledge Engineering Agent review sub-agent routes it to observed update, clarification, human approval, conflict, or rejection
-> Knowledge Engineering Agent steward sub-agent updates lifecycle or governance rules when repeated failures show systemic risk
```

## Decision Rights

| Decision | Agent Recommendation | Human Approval Needed |
| --- | --- | --- |
| Low-risk observed lesson | Review | No, if gate passes |
| Verified KnowledgeItem | Review | Yes |
| Approved ToolAsset or SkillAsset | Steward + Review | Yes, by owner |
| Active Policy | Steward + Review | Yes |
| Permission/security/customer commitment change | Steward + Review + Ops | Yes |
| Runtime block for unsafe tool call | Ops | No, fail closed |
| Directory/object model change | Steward | Usually yes when cross-team impact exists |

Governance approval means approval by the responsible governance role: 梅晓华 remains the current company knowledge core owner, project owner role for project-scoped decisions, Tool Owner for tools, Skill Owner for skills, and Security Reviewer for permission or security impact. In the AI-native operating model, these roles may later be implemented as owner Agents with explicit authority and audit.

## Escalation Rules

- Steward is called when ownership, scope, boundary, or governance path is unclear.
- Review is called before any candidate becomes reusable, indexed, verified, approved, or active.
- Ops is called when execution, gateway, audit, sync, eval, backup, or permission behavior is involved.
- Human review is required for verified knowledge, approved tools or skills, active policies, permission/security changes, customer commitments, and cross-team operating standards.

## Anti-Patterns

- Do not let project-private tools become public just because they are useful once.
- Do not let an Agent call an unregistered tool.
- Do not store raw chat, screenshots, recordings, transcripts, exports, source code copies, or secrets as reusable knowledge.
- Do not allow the same Agent to draft, review, approve, and publish high-impact changes.
- Do not treat missing audit, missing owner, missing scope, or missing source as minor formatting issues.
