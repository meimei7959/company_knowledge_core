---
type: Workflow
title: AI Native OS Development Stage Control
description: Project Manager Agent stage control for turning AI Native OS requirement slices into technical solution, implementation, test, and acceptance work.
timestamp: "2026-06-21T05:43:36Z"
controlId: control.ai-native-os.development-stage
projectId: company-knowledge-core
ownerAgent: agent.company.project-manager
sourceMaterialRefs:
  - projects/company-knowledge-core/coordination/ai-native-os-requirement-delivery-control.md
  - projects/company-knowledge-core/coordination/ai-native-os-execution-plan.md
  - docs/product/ai-native-os/requirements.md
  - docs/product/ai-native-os/development-handoff.md
status: active
---
# AI Native OS Development Stage Control

## PM Decision

Development Agents must not directly start broad implementation from the 74-requirement package.

Because this is a system-level product with scheduler, runner, evidence, governance, console, and API impact, each development slice must first produce a technical solution. Project Manager Agent uses that solution to control sequence, dependency, risk, and test readiness.

## Stage Flow

| Stage | Owner | Output | PM Gate |
| --- | --- | --- | --- |
| S1 Requirement Slice Intake | Project Manager Agent | Assigned requirement slice and owner. | Requirement refs are explicit and complete. |
| S2 Technical Solution | Development Agent | Technical solution for the assigned slice. | Architecture, data model, API, task/result lifecycle, tests, risks, and rollout are reviewable. |
| S3 Solution Review | Project Manager Agent, Test Agent, Knowledge Review Agent when governance is affected | Review notes and approval or blocker. | No implementation starts until critical blockers are closed or explicitly accepted. |
| S4 Implementation | Development Agent | Code/docs/schema changes with evidence. | TaskResult includes implemented requirementRefs, outputRefs, evidenceRefs, blockers, and nextActions. |
| S5 Test Execution | Test Agent | Requirement-to-test evidence and launch blockers. | No requirement leakage; failed gates become blockers. |
| S6 Acceptance And Flow-Forward | Project Manager Agent | Status, follow-up tasks, release gate decision. | Scheduler tick creates or claims next task; launch readiness reconciles all 74 requirements. |

## Technical Solution Required Content

Each development slice must produce a technical solution before implementation with:

- covered `requirementRefs`;
- current-state diagnosis and affected modules;
- proposed architecture and object model changes;
- API, CLI, scheduler, runner, or UI contract changes;
- data migration or compatibility plan;
- implementation slices and order;
- test strategy mapped to requirement refs and acceptance gates;
- risk, dependency, approval, and rollback notes;
- expected TaskResult evidence shape.

## PM Review Criteria

Project Manager Agent blocks implementation when:

- requirement refs are missing or do not match the assigned slice;
- the solution hides a cross-module dependency;
- scheduler, runner, TaskResult, audit, notification, or review-gate impact is not covered;
- tests cannot prove the assigned requirement refs;
- human approval is required but not routed;
- the plan cannot be executed by the registered runner and Agent team.

## Current AI Native OS Development Slices

| Development Task | Stage Now | Next Required Output |
| --- | --- | --- |
| kt-ai-native-os-dev-requirement-prd-domain | Technical solution required | Requirement and PRD domain technical solution. |
| kt-ai-native-os-dev-console-surfaces | Technical solution required | Console surface architecture and route/component plan. |
| kt-ai-native-os-dev-scheduler-runner-result | Technical solution required | Scheduler, runner, lease, result, and stale repair technical solution. |
| kt-ai-native-os-dev-governance-quality-ops | Technical solution required | Governance, quality, notification, admin, ops, and API technical solution. |

## Flow-Forward Rule

After a technical solution TaskResult is accepted, Project Manager Agent must create or activate implementation work for the same `requirementRefs`, then run scheduler tick. After implementation TaskResult, Project Manager Agent must trigger test execution and acceptance reconciliation.
