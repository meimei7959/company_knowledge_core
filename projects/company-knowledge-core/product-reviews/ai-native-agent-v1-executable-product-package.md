---
type: ReviewRecord
title: AI Native Agent V1 Executable Product Package
description: Product Manager Agent bootstrap output that structures the attached PRD and technical solution into executable V1 product requirements and acceptance criteria.
timestamp: "2026-06-22T00:00:00+08:00"
reviewId: product-review-ai-native-agent-v1-executable-product-package
projectId: company-knowledge-core
owner: agent.company.product-manager
status: submitted
sourceMaterialRefs:
  - /Users/meimei/Downloads/AI_Native_Agent协同系统_PRD_V1.0.docx
  - /Users/meimei/Downloads/AI_Native_Agent协同系统_技术方案_V1.0.docx
taskRefs:
  - projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-product-requirement-structure.md
---

# Product Verdict

The attached PRD and technical solution are sufficient as source material, but not sufficient as direct development input.

V1 must be executed from this structured product package:

Raw PRD and technical solution -> Product requirement structure -> Product scope lock -> Development technical solution -> Product review -> Implementation -> Test Agent closed-loop acceptance -> PM/Product final acceptance.

# V1 Business Goal

Prove that one computer can run a real Agent collaboration loop:

- multiple formal role Agent sessions exist;
- sessions register to a Local Router;
- Group Agent/Orchestrator creates Task Packages;
- role Agents receive tasks, execute, report status, and write TaskResult;
- Development and Test work is isolated by worktree where needed;
- failed tests route back to Development Agent;
- high-risk actions require human confirmation;
- project knowledge/task/audit records preserve evidence.

# User Scenarios

## Scenario 1: Project Manager Starts A V1 Agent Team

The user gives a project goal to the Group Agent/Project Manager control surface. The system creates or loads Product, Development, Test, and Documentation/Architect role Agents, registers their sessions, and displays them online.

Acceptance:

- Group/Product/Development/Test sessions are visible in Session Registry.
- Each session has agentId, sessionId, projectId, status, heartbeat, capabilities, and current task.

## Scenario 2: Product Work Hands Off To Development

Product Manager Agent structures the PRD into a V1 product package and acceptance matrix. Project Manager Agent releases Development Agent technical solution tasks only after product scope is locked.

Acceptance:

- Product package includes business goal, user scenarios, product requirements, functional requirements, acceptance criteria, and V1/V2/V3 boundary.
- Development technical solution tasks remain blocked before product package is submitted.

## Scenario 3: Group Agent Dispatches Runtime Work

Group Agent turns a goal into Task Graph and Task Packages, chooses the target Agent by capability/resource status, and sends an AgentMessage through Local Router.

Acceptance:

- TaskPackage records taskId, projectId, required agent role, context refs, output contract, risk level, and confirmation policy.
- AgentMessage records fromAgent, toAgent, fromSession, toSession, messageType, payload, status, and routing metadata.

## Scenario 4: Development And Test Close The Loop

Development Agent receives implementation work in an isolated worktree. Test Agent tests the worktree and returns pass/fail evidence. Failures create Development repair tasks.

Acceptance:

- Development task has worktree binding.
- Test report references the same worktree.
- Failed test cannot be silently fixed by PM; it must create a Development Agent repair task.

# Product Requirements

| ID | Requirement | V1 Acceptance |
| --- | --- | --- |
| V1-PRD-001 | Agent is a formal role runtime, not a prompt or Skill. | Agent Profile includes role soul, responsibilities, allowed skills, model policy, permissions, and output contract. |
| V1-PRD-002 | Skill is separate from Agent. | Skill Registry records input/output schema, tools, risk level, confirmation policy, and allowed agents. |
| V1-PRD-003 | Local Router supports single-machine Agent communication. | At least four sessions register and can exchange task/result/status messages. |
| V1-PRD-004 | Group Agent/Orchestrator owns task planning and routing. | User goal produces Task Graph and Task Packages. |
| V1-PRD-005 | Agent Runtime executes formal Task Packages. | Runtime loads profile, rules, context, skill, model policy, validates output, and writes TaskResult. |
| V1-PRD-006 | Resource/worktree isolation is available for dev/test. | Development work can bind to a local worktree; Test Agent can test that worktree. |
| V1-PRD-007 | Human can supervise execution. | Console/read model shows sessions, tasks, messages, worktrees, approvals, stale leases, and blockers. |
| V1-PRD-008 | Risk controls are enforced. | Delete, merge, deploy, external send, database change, and high-cost model calls require confirmation. |
| V1-PRD-009 | Role boundaries are enforced. | Product verdict comes from Product Manager Agent, implementation from Development Agent, pass/fail from Test Agent, orchestration from PM/Group Agent. |
| V1-PRD-010 | V1 proof is not Codex subagent proof. | Acceptance evidence comes from formal session registry, router messages, runtime TaskResult, and tests. |

# Functional Requirements

| Area | Functional Requirements |
| --- | --- |
| Agent Profile | Create/load/list profiles; validate role, responsibilities, skills, model policy, permissions, output contract. |
| Skill Registry | Create/load/list skills; validate allowed agents, schemas, tools, risk and confirmation policy. |
| Session Registry | Register, heartbeat, list, mark busy/idle/failed/offline, detect stale sessions. |
| Local Router | Send task/handoff/status/result/confirm_request/notify messages between local sessions. |
| Task Package | Compile ProjectTask plus context refs and output contract into runtime-deliverable package. |
| Agent Runtime | Receive package, load profile/rules/context, select skill, execute, validate, write status/result. |
| Orchestrator | Build Task Graph, select Agent, dispatch packages, watch progress, create repair tasks, summarize. |
| Worktree Manager | Allocate, bind, list, release local worktrees for implementation/test tasks. |
| Console | Display Agent sessions, task graph, message flow, worktrees, approvals, blockers, stale leases. |
| Acceptance Harness | Prove PRD V1 scenario end to end on one machine. |

# V1 / Later Boundary

| Scope | Decision |
| --- | --- |
| Agent Profile, Skill Registry, Session Registry, Local Router | V1 required |
| TaskPackage, AgentMessage, Agent Runtime, Orchestrator | V1 required |
| Minimal Worktree Manager and Console status | V1 required |
| Central Hub and cross-device routing | V2/V3 carryover |
| Feishu/enterprise entry | V4 carryover |
| Full native desktop packaging, signing, updater, OS secure storage | Later desktop product scope |
| Long-term Agent memory/growth | V5 carryover |

# Test Mapping

| Acceptance Test | Covers |
| --- | --- |
| Start Group/Product/Development/Test sessions and register Local Router | V1-PRD-001, V1-PRD-003 |
| Send user goal and generate Task Graph/Task Package | V1-PRD-004 |
| Route TaskPackage to Development Agent and receive result | V1-PRD-003, V1-PRD-005 |
| Allocate worktree for Development Agent | V1-PRD-006 |
| Test Agent runs against worktree and returns report | V1-PRD-006 |
| Failed test creates Development repair task | V1-PRD-009 |
| High-risk action creates confirmation request | V1-PRD-008 |
| Console shows sessions/messages/tasks/worktrees/blockers | V1-PRD-007 |

# Product Release Gate

Product Manager Agent can accept V1 only when:

- all V1 required capabilities above have implementation evidence;
- Test Agent passes the full single-machine closed-loop scenario;
- Project Manager Agent verifies role-boundary evidence;
- no V2/V3/V4 item is claimed as complete inside V1;
- repository validation and focused runtime tests pass.
