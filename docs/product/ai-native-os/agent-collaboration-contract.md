# AI Native OS Agent Collaboration Contract

This contract defines how human users, eight business Agents, governance Agents, and runners cooperate.

## Universal Agent Rules

Every Agent must:

- read assigned context before work;
- use only allowed tools and knowledge scopes;
- write structured output;
- link source evidence;
- expose assumptions and blockers;
- return next action;
- write TaskResult or ReviewRecord when work changes durable state;
- never approve its own high-impact output.

## Eight Business Agents

| Agent | Input | Output | Blocks When |
| --- | --- | --- | --- |
| Project Manager Agent | Project, Requirement, launch state, task queue, runner state, owner decisions. | Project plan, task decomposition, risk list, owner notification, closure verdict. | Owner, repo, approval, runner, first tasks, or notification path missing. |
| Product Manager Agent | Rough idea, SourceMaterial, market context, project goal, owner answers. | RequirementState, PRD, acceptance criteria, decision request, ProjectTask proposals. | Target user, problem, scenario, market, business model, success metric, or acceptance criteria missing. |
| Knowledge Query Agent | User/Agent question, project/context scope, permission. | Cited answer, confidence, source refs, gap, follow-up KnowledgeTask. | No permission, no reliable answer, or conflicting knowledge. |
| Knowledge Engineering Agent | SourceMaterial, KnowledgeTask, reader tools, evidence requirements. | Evidence packet, structured KnowledgeItem draft, TaskResult, review route. | Source missing, evidence insufficient, sensitivity unclear, or review path missing. |
| Design Agent | PRD, workflows, brand/design constraints, user scenarios. | IA, user flow, page/state spec, interaction notes, design acceptance criteria. | Requirement ambiguous, user scenario missing, or product decision unresolved. |
| Development Agent | Approved requirement/task, design spec, technical context, acceptance criteria. | Code, API/schema changes, migration, implementation notes, TaskResult. | Missing repo/tool permission, unclear acceptance, failing tests, or unsafe scope. |
| Test Agent | Requirement, acceptance criteria, implementation result, risk profile. | Test plan, test cases, automation, defect report, release quality verdict. | Acceptance criteria unobservable, environment missing, or critical defect open. |
| Operations Agent | Release plan, user segment, feedback, metrics, support context. | Launch operations plan, feedback report, growth/ops experiment, improvement tasks. | No owner, metric, audience, or rollback/response plan. |

## Governance Agents

| Agent | Input | Output | Cannot Do |
| --- | --- | --- | --- |
| Knowledge Steward Agent | Governance question, object model change, registry ambiguity, conflict. | Classification decision, boundary proposal, policy/workflow draft. | Approve own policy as final. |
| Knowledge Review Agent | Knowledge draft, source evidence, TaskResult, conflict/duplicate context. | Review result, change request, conflict route, approval route. | Approve own output as verified or policy. |
| Knowledge Ops Agent | Runtime failure, connector issue, permission issue, audit/eval/backup signal. | Ops diagnosis, repair task, metric, alert, recovery result. | Bypass security or approval gates. |

## Runner And Local Builder Agents

| Role | Contract |
| --- | --- |
| Agent Ring Runner | Registers capabilities, tools, repos, data scopes, heartbeat, load. Claims task with lease. Executes through allowed local Agent/tool. Writes result and heartbeat. |
| Codex Local Builder | Executes coding/documentation tasks through runner context and allowed repository scope. |
| Antigravity Local Builder | Executes allowed local work through runner context. |

## Standard Handoff Fields

Every Agent-to-Agent handoff must include:

- objectRef;
- owner;
- current status;
- sourceRefs;
- evidenceRefs;
- assumptions;
- blockers;
- decisions needed;
- required capabilities;
- acceptance criteria;
- allowed tools;
- next action;
- due or escalation rule when applicable.

## Main Collaboration Flows

### Requirement To Build

```txt
Submitter
-> Product Manager Agent clarifies Requirement
-> Project Manager Agent creates task plan
-> Design Agent specifies UX when needed
-> Development Agent implements
-> Test Agent verifies
-> Product Manager Agent accepts product intent
-> Project Manager Agent closes and notifies
```

### Material To Knowledge

```txt
Submitter / Agent Hub
-> SourceMaterial
-> Knowledge Engineering Agent extracts evidence
-> Knowledge Review Agent reviews
-> human approval when required
-> KnowledgeItem indexed
-> Knowledge Query Agent can answer with citation
```

### Tool Or Skill Change

```txt
Requester
-> ToolAsset / SkillAsset draft
-> Knowledge Steward classification when needed
-> Knowledge Ops security/runtime check
-> human owner approval when required
-> registry update
-> Agent Team Manager rollout
-> EvalRun / tests
```

### Runner Execution

```txt
Scheduler
-> eligible runner
-> claim with lease
-> context pack
-> local Agent/tool execution
-> TaskResult
-> acceptance/review path
-> notification and metrics
```

## Conflict Rules

- Product disagreement goes to Product Owner or Project Owner.
- Knowledge conflict goes to Knowledge Review Agent, then human approval if verified knowledge or policy is impacted.
- Permission conflict goes to Admin or Tool Owner.
- Runner failure goes to Knowledge Ops Agent.
- Scope conflict goes to Project Manager Agent plus Product Manager Agent.
- Customer/security/legal commitment goes to human owner; Agent can recommend only.

## Done Definition For Agent Work

Agent work is done only when:

- output is written to durable object or artifact;
- evidence and assumptions are visible;
- acceptance or review path is satisfied or blocked with owner;
- notification exists for affected human owner/requester;
- audit log exists for state change;
- follow-up task exists when work is incomplete.

