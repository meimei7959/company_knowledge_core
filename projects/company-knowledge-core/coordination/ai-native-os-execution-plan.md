---
type: Workflow
title: AI Native OS Execution Coordination Plan
description: Project Manager Agent execution coordination plan for the complete AI Native OS product package.
timestamp: "2026-06-21T05:13:34Z"
planId: plan.ai-native-os.execution
projectId: company-knowledge-core
ownerAgent: agent.company.project-manager
sourceTaskRef: projects/company-knowledge-core/tasks/kt-ai-native-os-project-manager-handoff.md
sourceMaterialRefs:
  - docs/product/ai-native-os/index.md
  - docs/product/ai-native-os/prd.md
  - docs/product/ai-native-os/requirements.md
  - docs/product/ai-native-os/agent-collaboration-contract.md
  - docs/product/ai-native-os/development-handoff.md
  - docs/product/ai-native-os/test-cases.md
  - docs/product/ai-native-os/acceptance-checklist.md
status: active
---
# AI Native OS Execution Coordination Plan

## PM Decision

The Project Manager Agent accepts the Product Manager Agent handoff.

Reason product handoff did not automatically execute before this run:

- the product package created a `pending` ProjectTask;
- no runner lease or scheduler claim converted that task into PM work;
- no auto-trigger rule currently turns `agent.company.product-manager` completion into `agent.company.project-manager` execution output.

PM correction in this plan:

- convert the product package into an executable task queue;
- assign role owners;
- define quality and approval gates;
- record launch risks and dependencies;
- close the handoff task with TaskResult and AgentRun evidence.
- control delivery against the 74-requirement baseline in `projects/company-knowledge-core/coordination/ai-native-os-requirement-delivery-control.md`.

## Execution Milestones

| Milestone | Goal | Exit Criteria | Owner |
| --- | --- | --- | --- |
| M0 Handoff Accepted | Product package becomes execution plan. | This plan, task queue, TaskResult, AgentRun, audit record exist. | agent.company.project-manager |
| M1 Technical Solutions Ready | Development and design tasks are dispatchable and technically planned. | Requirement, console, scheduler, governance, and design slices have accepted technical solutions or reviewable blockers. | agent.company.development |
| M2 Integration Spine Ready | Core product flow can run end to end. | Requirement -> PRD -> project -> agent team -> scheduler -> result -> review path works in local validation. | agent.company.development |
| M3 Acceptance Suite Ready | Test and review gates cover launch scope. | Test cases map to requirements and acceptance checklist gates. | agent.company.test |
| M4 Launch Readiness | Release can be accepted or blocked with evidence. | Acceptance checklist has pass/fail evidence, unresolved risks, and approval routing. | agent.company.project-manager |

## Work Queue

| Task | Agent | Scope | Gate |
| --- | --- | --- | --- |
| kt-ai-native-os-dev-requirement-prd-domain | agent.company.development | Requirement Center, PRD, Decision Center data model and flows. | Technical solution accepted, then ANOS-REQ requirement and PRD tests pass. |
| kt-ai-native-os-dev-console-surfaces | agent.company.development | Web console surfaces across product modules. | Technical solution accepted, then console acceptance and UI route checks pass. |
| kt-ai-native-os-dev-scheduler-runner-result | agent.company.development | Scheduler, Agent Ring, runner state, result center, stale lease repair. | Technical solution accepted, then scheduler and runner tests pass. |
| kt-ai-native-os-dev-governance-quality-ops | agent.company.development | Review, tool/skill registry, quality dashboard, notification, admin, API gateway. | Technical solution accepted, then governance, quality, notification, API tests pass. |
| kt-ai-native-os-design-console-experience | agent.company.design | Console interaction model and role-specific views. | Product console review accepts information architecture. |
| kt-ai-native-os-test-acceptance-suite | agent.company.test | E2E, negative, regression, EvalRun release gates. | AC-TEST-001 through AC-TEST-005 pass. |
| kt-ai-native-os-knowledge-governance-mapping | agent.core.knowledge-ops | Knowledge object, review, graph, audit, source material mapping. | Knowledge acceptance gates pass. |
| kt-ai-native-os-review-approval-routing | agent.core.knowledge-review | Review paths, human approval matrix, launch stop rules. | Approval routes are explicit and testable. |
| kt-ai-native-os-ops-launch-readiness | agent.company.operations | Deployment, monitoring, notification, backup, rollback readiness. | Operations acceptance gates pass. |

## Owner And Approval Matrix

| Area | Delivery Owner | Reviewer | Approval Trigger |
| --- | --- | --- | --- |
| Product scope and requirement changes | agent.company.product-manager | meimei | Any scope change, MVP downgrade, or launch requirement removal. |
| Execution plan and schedule | agent.company.project-manager | meimei | Milestone change, launch blocker, cross-agent dependency. |
| Code implementation | agent.company.development | agent.company.test | Merge/release readiness. |
| Test acceptance | agent.company.test | agent.company.project-manager | Critical E2E, negative, or regression failure. |
| Knowledge/governance | agent.core.knowledge-ops | agent.core.knowledge-review | Verified knowledge, policy, permission, tool approval impact. |
| Operations launch | agent.company.operations | meimei | Production deployment, integration secret, rollback decision. |

## Dependencies

- Product package must remain complete launch scope; do not silently reduce to MVP or P0/P1.
- Scheduler must support multi-runtime task dispatch and owner-visible blocked state.
- Agent Ring runner state must expose claim, lease, heartbeat, stale repair, result writeback.
- Every product requirement must map to test cases and acceptance gates.
- Human approval remains required for verified knowledge, policy, permissions, production release, or customer-facing commitment.

## Risk Register

| Risk | Severity | Owner | Mitigation |
| --- | --- | --- | --- |
| PM handoff tasks can remain pending without scheduler claim. | High | agent.company.project-manager | Add auto-trigger or scheduled scan for product-manager completion and PM handoff tasks. |
| Product scope is large and cross-cutting. | High | agent.company.project-manager | Execute by integrated slices with acceptance gates, not isolated docs. |
| Runner and lease state can block execution visibility. | High | agent.company.development | Prioritize scheduler-runner-result task before launch readiness. |
| Test mapping may lag requirements. | Medium | agent.company.test | Require ANOS-REQ to TC to AC traceability before launch. |
| Governance changes may require human approval. | Medium | agent.core.knowledge-review | Route policy, permission, verified knowledge, and tool approval changes to human review. |

## Launch Readiness Tracker

| Gate | Source | Current State |
| --- | --- | --- |
| Product Acceptance | acceptance-checklist.md | Waiting for implementation evidence. |
| Requirement Acceptance | requirements.md, test-cases.md | Waiting for ANOS-REQ traceability. |
| Agent Acceptance | agent-collaboration-contract.md | Waiting for runtime role validation. |
| Execution Acceptance | development-handoff.md | Waiting for scheduler and runner implementation. |
| Knowledge Acceptance | acceptance-checklist.md | Waiting for knowledge governance mapping. |
| Review And Governance Acceptance | acceptance-checklist.md | Waiting for review route tests. |
| Console Acceptance | prd.md, requirements.md | Waiting for product console implementation. |
| Test Acceptance | test-cases.md | Waiting for E2E, negative, regression, EvalRun evidence. |
| Operations Acceptance | acceptance-checklist.md | Waiting for deployment and monitoring readiness. |

## Notification Plan

- Notify project owner when M0 is complete and execution queue exists.
- Notify each assigned Agent when its ProjectTask is ready to claim.
- Notify project manager on any blocked task, stale lease, failed acceptance gate, or human approval requirement.
- Notify product manager when implementation raises scope ambiguity or acceptance conflict.

## Next PM Actions

1. Claim one high-priority task at a time on `runner.meimei-mac-local-codex`.
2. Require technical solution output before broad development starts.
3. Watch task queue until each owner claims or explicitly declines.
4. Run project status after every task result writeback.
5. Reconcile delivered `requirementRefs` against the 74-requirement control baseline.
6. Escalate if scheduler cannot auto-claim PM handoff tasks.
7. Do not mark launch ready until acceptance-checklist.md gates have evidence.
