---
type: Workflow
title: AI Native Agent V1 Single-Machine Closed Loop Upgrade Plan
description: Project Manager Agent plan for upgrading the existing company knowledge core into the PRD/technical-solution-defined V1 single-machine Agent collaboration loop.
timestamp: "2026-06-22T00:00:00+08:00"
planId: plan.ai-native-agent-v1-single-machine-upgrade
projectId: company-knowledge-core
ownerAgent: agent.company.project-manager
status: active
sourceMaterialRefs:
  - /Users/meimei/Downloads/AI_Native_Agent协同系统_PRD_V1.0.docx
  - /Users/meimei/Downloads/AI_Native_Agent协同系统_技术方案_V1.0.docx
auditRefs:
  - knowledge/audit/audit.20260622T000000-ai-native-agent-v1-upgrade-plan.md
---

# PM Verdict

The attached PRD and technical solution define a narrower and more executable V1 than the previous full AI Native OS delivery queue.

V1 target is not Feishu live path, cross-device Hub, full distributed runner, or polished desktop packaging. V1 target is:

One computer can run multiple independent formal Agent sessions, register them to a Local Router, let a Group Agent/Orchestrator create Task Packages, dispatch work to role Agents, receive status/results, isolate development in worktrees, route test failures back to Development Agent, require human confirmation for high-risk actions, and write final evidence into the project knowledge/task system.

# Scope Correction

The prior 74 ANOS-REQ functional requirements remain useful implementation inventory, but they are not the right release boundary for this V1.

For V1, release boundary is the single-machine closed loop from the new PRD:

1. Agent Profile can define at least Product, Architect, Development, Test, and Documentation Agents.
2. Local Router can register at least Group/Product/Development/Test sessions on this computer.
3. Group Agent can convert a user goal into a task graph and Task Packages.
4. Target Agent Runtime can receive a Task Package, load its profile/skills/context/model policy, execute, validate output, and report status/result.
5. Development work can be isolated with worktree allocation.
6. Test Agent can test the development worktree and return pass/fail evidence.
7. Failed tests create repair tasks for Development Agent, not silent PM edits.
8. Product Manager Agent owns product acceptance; Test Agent owns test verdict; Project Manager Agent owns orchestration and evidence reconciliation.

# Reuse Matrix

| V1 capability | Reuse from current system | Required upgrade |
| --- | --- | --- |
| Agent definitions | `agents/*.md`, `docs/agent-team/role-operating-specs.json` | Add machine-readable Agent Profile schema/loader with role soul, responsibilities, skills, model policy, permissions, output contract. |
| Skills | `skills/*/SKILL.md`, role skill packs | Add Skill Registry metadata: input schema, output schema, allowed agents, risk level, confirmation policy. |
| Task lifecycle | `templates/project-task.md`, `templates/task-result.md`, `zhenzhi_knowledge/core.py` | Add TaskPackage and AgentMessage objects that bridge ProjectTask to runtime delivery. |
| Scheduler/runner checks | `runner_can_schedule_task`, runner heartbeat, distributed proof harness | Refactor local V1 path into Session Registry + Local Router; runner proof cannot be the release proof by itself. |
| Runtime rules | `docs/agent-team/agent-task-runtime-contract.md`, common rules, human acceptance policy | Enforce at runtime: every Agent execution must load layered rules and record refs in TaskResult. |
| Workbench/status | `desktop-workbench-slice0/*`, workbench tests | Upgrade into V1 console read model for sessions, task graph, messages, worktrees, approvals, and stale leases. |
| Worktree proof | `desktop-native-proof`, distributed runner proof harness | Add minimal Worktree Manager API for local dev/test isolation. Native packaging remains later scope. |
| Governance/evidence | audit logs, validation tests, product/test reviews | Add closed-loop acceptance harness based on the new V1 PRD scenario. |

# Gap List

| Gap | Why it blocks V1 | Owner |
| --- | --- | --- |
| Agent Profile Service absent as executable service | Agent still exists mostly as documents/role specs; runtime cannot load a formal profile deterministically. | Development Agent |
| Skill Registry absent as executable registry | Skill use is not centrally constrained by allowed agent, risk, input/output schema. | Development Agent |
| Local Router absent as formal runtime component | Formal Agents cannot register sessions, route messages, or prove online/busy/failed state. | Development Agent |
| Agent Runtime absent | A task cannot yet be delivered to a formal Agent session that loads profile/context/skill/model policy and reports result. | Development Agent |
| Group Agent/Orchestrator not wired to runtime | PM can plan, but plans are not automatically converted to routed Task Packages. | Development Agent with PM review |
| Worktree Manager minimal slice not integrated | Dev/Test isolation is not guaranteed in the V1 runtime path. | Development Agent |
| Console read model incomplete for V1 | Human cannot reliably see which formal Agent is doing what or where approval is blocked. | Development Agent |
| V1 acceptance harness missing | Existing tests prove slices, not the full PRD scenario from session registration to final knowledge write. | Test Agent |

# Delivery Organization

## Phase 0: Product Requirement Structuring

Task: `kt-ai-native-agent-v1-product-requirement-structure`

Product Manager Agent must transform the attached PRD and technical solution into an executable V1 product package before Development Agent writes technical solutions.

This is not a full rewrite of the PRD. It is a product structuring step:

- business goals;
- user scenarios;
- product requirements;
- functional requirements;
- acceptance criteria;
- requirement-to-test mapping;
- V1/V2/V3 boundary.

Exit: Product Manager Agent writes the V1 executable product package and acceptance matrix.

## Phase 1: Product Scope Lock

Task: `kt-ai-native-agent-v1-product-scope-review`

Product Manager Agent reviews the structured product package and confirms V1 scope:

- in scope: Agent Profile, Skill Registry, Session Registry, Local Router, Task Package, Orchestrator, Agent Runtime, worktree isolation, V1 console, closed-loop tests;
- out of V1 release gate: Central Hub, Feishu/enterprise entry, full distributed runner, complete native desktop packaging/signing/updater, long-term Agent memory.

Exit: Product Manager Agent writes acceptance criteria and non-negotiables.

## Phase 2: R&D Technical Solution

Tasks:

- `kt-ai-native-agent-v1-tech-profile-skill-registry`
- `kt-ai-native-agent-v1-tech-local-router-session-registry`
- `kt-ai-native-agent-v1-tech-agent-runtime-orchestrator`
- `kt-ai-native-agent-v1-tech-worktree-console-harness`

Development Agent must output technical solution based on the Product Manager Agent's V1 executable product package, not directly from the raw PRD. Product Manager Agent reviews the solution against the product package. Project Manager Agent releases implementation only after review.

Exit: technical solution covers data model, API, CLI, runtime flow, persistence, tests, risk controls, migration from existing files.

## Phase 3: Core Implementation

Implementation order:

1. Agent Profile Service + Skill Registry.
2. Session Registry + Local Router.
3. TaskPackage + AgentMessage object model and CLI/API.
4. Agent Runtime worker that can claim/r receive a routed task and write TaskResult.
5. Group Agent Orchestrator that turns user goal into Task Graph and dispatches Task Packages.
6. Minimal Worktree Manager for development/test isolation.
7. Console/read model for Agent sessions, task graph, messages, worktrees, approvals, and blockers.

Exit: local command can start/register at least Group, Product, Development, and Test sessions.

## Phase 4: Test Agent Closed-Loop Verification

Task: `kt-ai-native-agent-v1-test-closed-loop-acceptance`

Test Agent executes the PRD acceptance scenario:

1. Start Group Agent, Product Agent, Development Agent, Test Agent sessions on this computer.
2. Verify all sessions register to Local Router and display online.
3. Send goal: "design Local Router module".
4. Verify Group Agent creates Task Package and dispatches it to Architect/Development Agent.
5. Verify target Agent returns technical result.
6. Verify Group Agent summarizes result and requests confirmation before development.
7. Verify Development Agent receives implementation task in isolated worktree.
8. Verify Test Agent runs against that worktree and returns pass/fail report.
9. Verify failed test creates Development repair task.
10. Verify high-risk merge/write action enters human confirmation.
11. Verify accepted result writes TaskResult, audit evidence, and knowledge/task refs.

Exit: Test Agent TaskResult is pass with evidence refs. Any failure must route back to Development Agent.

## Phase 5: PM/Product Acceptance

Project Manager Agent checks process integrity:

- no role verdict came from main thread;
- no test failure was fixed by PM directly;
- no Codex subagent hidden approval prompt is counted as V1 Agent execution;
- every formal Agent run has session ID, task ID, message ID, output refs, test/check refs, and audit refs.

Product Manager Agent performs final product acceptance:

- confirms V1 scope is satisfied;
- confirms V2/V3 items are not falsely claimed;
- records whether V1 can be released as "single-machine closed loop".

# Non-Negotiable Operating Rules

- V1 delivery proof must use formal Agent sessions through Local Router, not Codex subagents as the execution model.
- Main thread can orchestrate, reconcile, and unblock, but cannot replace Product/Development/Test verdicts.
- Development Agent must produce technical solution before implementation.
- Product Manager Agent must review PRD alignment before release to implementation.
- Test Agent owns pass/fail. Failed test results create repair tasks for Development Agent.
- Token/context exhaustion is pause/resume state, not completion or failure.
- Hidden approval prompts in child windows are blockers; approvals must be surfaced to the main control path or console.
- High-risk delete/merge/deploy/external-send/database-change actions require human confirmation and audit.

# V1 Done Definition

V1 is done only when all are true:

- Product Manager Agent accepted V1 scope and acceptance criteria.
- Development Agent implemented the V1 runtime path.
- Test Agent passed the complete PRD acceptance scenario.
- Project Manager Agent accepted process evidence.
- Repository validation passes.
- Workbench/console shows enough state for human supervision.
- Open items are clearly marked V2/V3, not hidden V1 blockers.
