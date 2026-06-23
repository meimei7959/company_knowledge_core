---
type: Workflow
title: Auto Execution System Delivery Plan
description: Project Manager Agent delivery plan for turning the current task management model into a stable automatic execution system.
timestamp: "2026-06-21T05:53:52Z"
planId: plan.auto-execution-system.delivery
projectId: company-knowledge-core
ownerAgent: agent.company.project-manager
status: active
sourceMaterialRefs:
  - projects/company-knowledge-core/coordination/ai-native-os-development-stage-control.md
  - projects/company-knowledge-core/coordination/ai-native-os-requirement-delivery-control.md
  - docs/scheduler/task-dispatch-model.md
---
# Auto Execution System Delivery Plan

## PM Objective

Build the minimum stable automatic execution system. Completion means work can move from task creation to runner claim, agent execution, TaskResult writeback, PM review, next-task creation, testing, and acceptance without manual command-by-command steering.

## Delivery Slices

| Slice | Task | Owner | Exit Criteria |
| --- | --- | --- | --- |
| PM Autopilot | kt-autoexec-dev-pm-autopilot-runtime | agent.company.development | Scheduler can run finite autopilot cycles, choose the right next task, and expose decisions. |
| Agent Worker | kt-autoexec-dev-agent-worker-runtime | agent.company.development | Worker can claim matching tasks and write TaskResult for technical solution tasks. |
| State And Flow | kt-autoexec-dev-state-result-flow | agent.company.development | Task stages and TaskResult-driven transitions are explicit and testable. |
| Workbench Data | kt-autoexec-dev-workbench-data-api | agent.company.development | Workbench can read agent activity, stale work, blockers, requirement coverage, and PM decisions. |
| Closed Loop Test | kt-autoexec-test-closed-loop-suite | agent.company.test | Automated tests prove the minimum closed loop. |
| PM Acceptance | kt-autoexec-pm-final-acceptance | agent.company.project-manager | PM accepts or blocks based on evidence, not task existence. |

## Required End-To-End Flow

1. Product or PM creates a dispatchable task.
2. PM Autopilot ranks tasks by priority, stage, dependency, and launch impact.
3. Matching Agent Worker claims the task.
4. Worker creates execution context and performs the stage work.
5. Worker writes TaskResult with outputRefs, evidenceRefs, requirementRefs, nextActions, and openRisks.
6. PM Autopilot reviews the TaskResult and creates or releases next-step work.
7. Test Worker validates the flow.
8. PM Agent accepts only when the closed-loop test and evidence pass.

## Role Integrity Corrections

- Sub-agent approval prompts must be relayed to the Project Manager Agent and handled in the main control flow; hidden child-window approval prompts count as blockers.
- Test failures must return to Development Agent as repair work; Project Manager Agent must not silently patch implementation after Test Agent failure.
- Product Manager Agent must participate in technical-solution review before 74-requirement implementation work is released.

## Workbench Relationship

The workbench is required for visibility and intervention, but it is not the execution engine.

The execution engine is complete only when PM Autopilot, Agent Worker, TaskResult transitions, and tests work without a human manually calling each step.

The workbench is complete only when it can show:

- which Agent is running which task;
- stale lease and blocked task state;
- PM Autopilot decisions;
- TaskResult evidence and nextActions;
- requirement coverage and missing evidence;
- manual controls for pause, retry, reassign, accept, and reject.

## Final Acceptance Standard

Project Manager Agent cannot accept this delivery until:

- scheduler priority chooses high-priority technical solution work before medium design work;
- autopilot CLI runs finite cycles and returns decision evidence;
- development worker writes a technical solution TaskResult;
- TaskResult creates or enables next-step flow;
- test suite covers the full loop;
- repository validation passes;
- remaining gaps to external Agent Ring or real LLM execution are explicit and non-hidden.
