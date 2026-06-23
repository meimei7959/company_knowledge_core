# Mature AI Native Operating System Roadmap

This document is the task-level roadmap for turning Company Knowledge Core from an Agent Hub plus scheduler into a mature AI-native company operating system.

The target is not a prototype. The target is an operating system that can run company work through digital employees, distributed computers, governed tools, auditable knowledge, automatic evaluation, controlled human oversight, and continuous self-improvement.

## Maturity Definition

A mature AI-native operating system is achieved only when these conditions are true:

1. Company work enters the system through Agent Hub, API, CLI, or Agent Ring, and becomes typed tasks or workflows.
2. Work is owned by accountable Agents and executed by registered Runners, not by informal human memory.
3. Every task has a state machine, context pack, execution contract, evaluation gate, notification trail, and audit trail.
4. Agent-to-Agent discussion produces decisions, follow-up tasks, or human-decision requests, not loose chat.
5. Knowledge is captured with source evidence, reviewed, published, indexed, and reused with status and scope.
6. Tools and skills are registered, versioned, permissioned, evaluated, and reusable across projects when safe.
7. Failures, rejections, low-quality outputs, and repeated manual interventions create improvement tasks and eval cases.
8. Any task can move from one computer to another without losing project context.
9. Human operators supervise, approve, or override; they are not required to manually push normal work forward.

## Operating System Subsystems

| Subsystem | Purpose | Current Evidence | Hardening Task |
| --- | --- | --- | --- |
| Agent Directory | Manage digital employee identity, role, skills, version, permissions, and reliability | `docs/agent-team/company-agent-team-operating-guide.md`, `projects/company-knowledge-core/agents.md` | `KT-OS-AGENT-DIRECTORY` |
| Runner Fabric | Manage distributed computers and local execution surfaces | `docs/protocols/agent-workbench-integration-brief.md`, `docs/scheduler/task-dispatch-model.md` | `KT-OS-RUNNER-FABRIC` |
| Workflow State Machine | Ensure all work advances through explicit lifecycle states | `docs/workflows/*`, existing ProjectTask files | `KT-OS-WORKFLOW-STATE-MACHINE` |
| Context Pack Engine | Make tasks portable across computers and sessions | `docs/protocols/project-context-sync-protocol.md` | `KT-OS-CONTEXT-PACK-ENGINE` |
| Knowledge Core | Govern source material, draft knowledge, review, publish, index, and conflict handling | `docs/workflows/knowledge-lifecycle.md`, `docs/workflows/knowledge-ingest-orchestration.md` | `KT-OS-KNOWLEDGE-CORE-GOVERNANCE` |
| Skill Registry | Version and evaluate reusable role capabilities | agent role and skill pack docs | `KT-OS-SKILL-REGISTRY-LIFECYCLE` |
| Tool Registry | Govern tools, risk levels, result persistence, and registration | `docs/tools/core-tool-contract.md`, `projects/company-knowledge-core/tools.md` | `KT-OS-TOOL-REGISTRY-POLICY` |
| Policy Engine | Decide auto-run, auto-accept, approval, escalation, and block rules | `knowledge/policies/*.md` | `KT-OS-POLICY-ENGINE` |
| Agent Collaboration Protocol | Let Agents discuss, decide, and hand off work like a company team | `docs/agent-team/company-agent-team-operating-guide.md`, `docs/protocols/agent-workbench-integration-brief.md` | `KT-OS-AGENT-COLLABORATION-PROTOCOL` |
| Evaluation Engine | Score every Agent deliverable and route retry, repair, accept, or escalate | `docs/workflows/evaluation-lifecycle.md` | `KT-OS-EVALUATION-ENGINE` |
| Event Bus and Notification | Notify the right Agent, Runner, PM Agent, requester, or human sponsor, with retry and audit | `projects/company-knowledge-core/tasks/kt-task-notification-loop.md` | `KT-OS-EVENT-NOTIFICATION-BUS` |
| Self-Improvement Pipeline | Convert failures into skill updates, eval cases, guide updates, and versioned rollout | company guide self-improvement section | `KT-OS-SELF-IMPROVEMENT-PIPELINE` |

## Operating Principles

- Do not create many tiny Agents. Keep a small set of role Agents and make them strong through skills, workflows, and evaluation.
- Do not treat documentation as completion. A task is complete only when the workflow, object contract, command/API behavior, notification, evaluation, or validation gate proves it.
- Do not let chat be the system of record. Conversations must resolve into `Decision`, `ProjectTask`, `KnowledgeTask`, `TaskResult`, `DiscussionSummary`, or `HumanDecisionRequest`.
- Do not let humans become hidden schedulers. Humans approve, reject, or override. Normal state transitions must be system-driven.
- Do not let knowledge become untraceable. Reusable answers must carry source, status, confidence, scope, and evidence.

## Six Master Tasks

The twelve subsystems above are the coverage matrix. Execution is organized into six master tasks to avoid redundant delivery tracks:

| Master Task | Covered Subsystems | Task Card |
| --- | --- | --- |
| OS execution spine | Workflow State Machine; Event Bus and Notification | `projects/company-knowledge-core/tasks/kt-os-execution-spine.md` |
| Digital worker and capability registry | Agent Directory; Skill Registry; Tool Registry | `projects/company-knowledge-core/tasks/kt-os-digital-worker-capability-registry.md` |
| Runner distributed execution network | Runner Fabric; Context Pack Engine | `projects/company-knowledge-core/tasks/kt-os-runner-execution-network.md` |
| Policy and quality gates | Policy Engine; Evaluation Engine | `projects/company-knowledge-core/tasks/kt-os-policy-quality-gates.md` |
| Knowledge governance loop | Knowledge Core | `projects/company-knowledge-core/tasks/kt-os-knowledge-governance-loop.md` |
| Collaboration and self-improvement loop | Agent Collaboration Protocol; Self-Improvement Pipeline | `projects/company-knowledge-core/tasks/kt-os-collaboration-self-improvement.md` |

The six master tasks are allowed to adjust their covered subsystem cards during implementation if that improves maturity, reduces redundancy, or closes a real operational gap. They must not weaken the completion gate.

## Completion Gate

The mature AI-native operating system goal is not complete until every hardening task below is `done` and has evidence for:

1. object/schema or file contract,
2. workflow state transitions,
3. CLI/API or protocol behavior,
4. notification behavior,
5. evaluation or validation behavior,
6. audit trail,
7. test or harness coverage.

If any subsystem has only a document and no runnable or verifiable flow, the operating system remains incomplete.

## Implementation Order

1. `KT-OS-EXECUTION-SPINE`
2. `KT-OS-DIGITAL-WORKER-CAPABILITY-REGISTRY`
3. `KT-OS-RUNNER-EXECUTION-NETWORK`
4. `KT-OS-POLICY-QUALITY-GATES`
5. `KT-OS-KNOWLEDGE-GOVERNANCE-LOOP`
6. `KT-OS-COLLABORATION-SELF-IMPROVEMENT`

This order hardens the execution spine first, then governance and continuous improvement.

## Acceptance Matrix

| Question | Required Answer Before Completion |
| --- | --- |
| Can a new company project start from Feishu without manual routing? | Yes: Agent Hub creates project/workflow tasks and notifies the PM Agent or configured sponsor. |
| Can the task be executed on a different computer? | Yes: Runner registry, capability match, claim lease, context pack, and result writeback are verified. |
| Can role Agents collaborate without human pushing? | Yes: discussion session produces a decision, task, or human-decision request. |
| Can bad output recover? | Yes: evaluation creates retry, repair, escalation, or improvement task. |
| Can humans see what happened? | Yes: NotificationRecord, AuditLog, TaskResult, and status dashboard expose the trail. |
| Can the company learn from work? | Yes: Knowledge Core and Self-Improvement Pipeline publish reviewed knowledge and update skills/evals. |
| Can employees reuse the system? | Yes: they interact through Agent Hub and do not need internal IDs or task syntax. |
