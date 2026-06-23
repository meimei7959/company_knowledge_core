---
type: Workflow
title: AI Native OS Agent Execution Governance
description: Project Manager Agent guardrails for sub-agent approval routing, test-failure repair flow, and 74-requirement delivery execution.
timestamp: "2026-06-21T06:16:06Z"
controlId: control.ai-native-os.agent-execution-governance
projectId: company-knowledge-core
ownerAgent: agent.company.project-manager
status: active
sourceMaterialRefs:
  - projects/company-knowledge-core/coordination/auto-execution-system-delivery-plan.md
  - projects/company-knowledge-core/coordination/ai-native-os-requirement-delivery-control.md
  - projects/company-knowledge-core/coordination/ai-native-os-development-stage-control.md
---
# AI Native OS Agent Execution Governance

## PM Corrections

Two execution defects were observed during the auto-execution-system delivery run:

1. A sub-agent used a tool that required approval in the sub-agent window, which can stall execution because the Project Manager Agent cannot see or approve it from the main control window.
2. When the Test Agent returned two failures, the Project Manager Agent repaired the implementation directly instead of assigning a repair task back to the Development Agent.

Both defects are workflow blockers. They prove that task creation alone is not enough; execution must preserve approval routing, role ownership, and repair loops.

## Approval Relay Rule

Sub-agents must not start tool calls that are likely to require user approval inside their own window.

When a sub-agent needs approval, it must stop and return an approval request to the Project Manager Agent with:

- requested tool or command;
- reason;
- expected write/read scope;
- risk;
- fallback if denied.

The Project Manager Agent then decides one of:

- run the required inspection or command in the main window;
- ask the human owner in the main window;
- split the task into a no-approval subtask;
- block the task and create a visible blocker.

Approval prompts hidden in a sub-agent window are treated as `blocked`, not as active work.

## Test Failure Repair Rule

When Test Agent reports failures:

1. Project Manager Agent records the failed tests and failure reason.
2. Project Manager Agent creates or reopens a Development repair task.
3. Development Agent fixes the defect and writes TaskResult evidence.
4. Test Agent reruns the failed test and required regression set.
5. Project Manager Agent accepts only after the test evidence is green.

Project Manager Agent must not directly patch implementation code after Test Agent failure except for emergency stabilization. If PM performs an emergency patch, it must create an incident record and a follow-up Development Agent review task.

## Context Budget Recovery Rule

When Development, Product, Test, or Project Manager Agent reaches context-window or token-budget limits, this is a recoverable pause, not completion and not failure.

Required behavior:

- record the current task, last completed evidence, pending tool/action, and next step;
- wait for the thread, sub-agent, or tool state to recover;
- after recovery, restore state from ProjectTask, TaskResult, AgentRun, AuditLog, NotificationRecord, and coordination documents;
- continue from the last durable checkpoint;
- do not restart the same work from scratch unless the previous output is missing or invalid;
- do not mark the task done without TaskResult evidence;
- do not mark the task failed unless the same recovery condition repeats three times and a blocker record explains what is needed.

Project Manager Agent owns monitoring this recovery loop. If a sub-agent is paused by context budget, Project Manager Agent keeps the work item open and continues waiting or reschedules it; it does not silently abandon the 74-requirement delivery chain.

## 74-Requirement Delivery Rule

For the AI Native OS 74 requirements:

- Development Agent first produces technical solution packages by requirement slice.
- Product Manager Agent reviews the technical solution for product fit, scope, and acceptance meaning.
- Project Manager Agent moderates the review and resolves risks or blockers.
- Only accepted technical solutions move to implementation.
- Implementation completion triggers Test Agent execution.
- Test failure triggers Development repair.
- Test pass triggers Product Manager and Project Manager acceptance.

## Desktop Workbench Product Constraint

The workbench is a desktop client, not only a web page.

Delivery must prefer a cross-platform technology that supports Mac and Windows from one maintained codebase. The technical solution must compare at least:

- Tauri with web frontend;
- Electron with web frontend;
- native split implementations.

The preferred direction is a single cross-platform desktop shell with a shared frontend and local/API integration layer, unless the Development Agent proves a better option.

## PM Acceptance Gate

Project Manager Agent cannot accept a 74-requirement implementation slice unless:

- no sub-agent approval is stuck in a child window;
- any needed approval was relayed to the main control flow;
- no context/token budget pause is being treated as completion, failure, or abandonment;
- failed tests, if any, were repaired by Development Agent and retested by Test Agent;
- Product Manager Agent accepted product scope and acceptance semantics;
- Test Agent accepted requirement coverage and regression evidence;
- TaskResult evidence links requirementRefs, outputRefs, evidenceRefs, risks, and nextActions.
