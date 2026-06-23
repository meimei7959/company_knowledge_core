---
type: ReviewRecord
title: Agent team growth and task fact V1 test plan
description: Test plan, fixture matrix, and acceptance matrix for ANOS-REQ-160-FUSION-V1 before development handoff execution.
timestamp: "2026-06-23T10:12:00Z"
projectId: company-knowledge-core
taskId: kt-agent-team-growth-task-fact-test-plan
status: submitted
ownerAgent: agent.company.test
reviewerAgent: agent.company.test
requirementRefs:
  - ANOS-REQ-160
  - ANOS-REQ-160-FUSION-V1
sourceRefs:
  - projects/company-knowledge-core/receiver-reviews/receiver-review.agent-team-growth-task-fact.test-plan.md
  - docs/product/ai-native-os/agent-team-growth-and-task-fact-prd.md
  - projects/company-knowledge-core/technical-solutions/agent-team-growth-and-task-fact-technical-solution.md
  - projects/company-knowledge-core/product-reviews/agent-team-growth-task-fact-architecture-product-review.md
  - docs/product/ai-native-os/task-execution-productization-acceptance-matrix.md
  - projects/company-knowledge-core/tasks/kt-agent-team-growth-task-fact-development.md
scope:
  - pm_controlled_worker_lifecycle
  - task_fact_view_v1_projection
  - gap_taxonomy
  - agent_team_capability_version
  - growth_signal_draft_routing
  - api_cli_workbench_parity
  - unsupported_same_project_multi_computer_execution
executionStatus: blocked_until_development_handoff
---

# Agent team growth and task fact V1 test plan

## Current status

Test-plan preparation is complete. Formal execution is blocked until Development Agent provides `task-results/tr-kt-agent-team-growth-task-fact-development.md` or equivalent handoff evidence.

This plan does not declare implementation passed. It defines fixtures, acceptance checks, pass/fail rules, and defect creation criteria for the later execution task.

## Test objective

Verify that `task-fact-view.v1` makes the PM-controlled worker lifecycle visible as a read-only fact projection, exposes lifecycle gaps instead of inferring success, preserves V0 compatibility, and routes growth signals without publishing unreviewed capability changes.

## Required development handoff before execution

Execution can start only when the Development TaskResult provides:

- changed files or implementation refs for projection, Scheduler/API/CLI/workbench, fixtures, and tests;
- runnable command list and environment assumptions;
- sample task IDs or fixture paths for PM parent and worker tasks;
- evidence for V0 compatibility and read-only behavior;
- capability version source/digest rule;
- growth signal creation or gap-display rule;
- known exclusions and unsupported same-project multi-computer behavior.

If this handoff is absent, all runtime acceptance items remain `blocked`, not `pass`.

## Fixture matrix

| Fixture ID | Priority | Purpose | Required records | Expected visible facts |
| --- | --- | --- | --- | --- |
| FX-001 | P0 | Happy path PM parent + worker lifecycle | Parent ProjectTask assigned to `agent.company.project-manager`; product, architecture, development, and test worker tasks; each worker has ReceiverReview, AgentRun, TaskResult, evidence, audit; parent has PM consolidation TaskResult. | `workerParticipation` lists role, input, boundary, result, evidence, and PM consolidation; worker result is not final parent conclusion by itself. |
| FX-002 | P0 | Missing ReceiverReview gap | Worker task lacks `receiverReviewRefs` before execution output. | `missing_worker_review` and `worker trace gap`; no accepted worker start claim. |
| FX-003 | P0 | Missing worker TaskResult gap | Worker task has ReceiverReview and AgentRun but no `resultRef`. | `missing_worker_result` and next owner shown; parent not complete. |
| FX-004 | P0 | Missing evidence/tests/checks gap | TaskResult exists but `evidenceRefs` or `testsOrChecks` is empty. | `result evidence gap`; no complete closed-loop label. |
| FX-005 | P0 | Missing audit/notification gap | Lifecycle records lack audit or notification refs after write/transition. | `audit gap` or notification gap with last known owner. |
| FX-006 | P0 | Capability version match | Parent task and runner both reference same `agentTeamCapabilityVersionRef`. | `capabilityVersion.match = true`, version source visible. |
| FX-007 | P0 | Capability version mismatch | Runner proves different or missing capability version. | `capability_version_mismatch`; Scheduler/API/CLI marks reject or gap according to implementation contract. |
| FX-008 | P0 | Same-project multi-computer competition negative | Two runners/computers attempt to claim or co-execute same project scope. | `unsupported_multi_computer_project_execution`; no accepted shared execution. |
| FX-009 | P0 | Different-project multi-computer allowed | Two computers run different projects with same capability version. | Both project facts visible independently; no shared claim queue for one project. |
| FX-010 | P0 | Quality failure growth signal | Worker TaskResult has `qualityEvaluation.passed = false`. | Draft AgentImprovementProposal or `learning loop gap`; source task and role linked. |
| FX-011 | P1 | Rework growth signal | PM consolidation requests changes or creates rework task. | Growth signal links rework cause, worker output, parent task, and follow-up. |
| FX-012 | P1 | Manual correction growth signal | Human/PM correction exists in ReviewRecord, AuditLog, or TaskResult. | Draft EvalCase/AgentImprovementProposal or explicit `learning loop gap`. |
| FX-013 | P1 | Repeated blocker growth signal | Same blocker appears two or more times for role/project. | Growth signal suggests review route; does not auto-publish rule. |
| FX-014 | P0 | Role-boundary violation | Test worker edits implementation, Development worker self-accepts product, or PM replaces owning Agent result. | Boundary violation visible; quality fail or growth signal created. |
| FX-015 | P0 | Legacy task compatibility | Old task lacks worker/capability/growth fields. | Existing V0 fields render; new blocks show `legacy gap`, not crash. |
| FX-016 | P0 | API/CLI/workbench parity | Same fixture exposed through API, CLI JSON/markdown, and workbench pane. | Same schema version, core values, gap codes, and readable labels across surfaces. |

## Gap taxonomy under test

Required machine-readable gaps and reasons:

- `missing_pm_controller`
- `missing_worker_review`
- `missing_worker_result`
- `worker trace gap`
- `result evidence gap`
- `learning loop gap`
- `capability version gap`
- `capability_version_mismatch`
- `audit gap`
- `growth_signal_gap`
- `unsupported_multi_computer_project_execution`
- `legacy gap`
- `status/result mismatch`
- `dangling ref`

Every gap must include source field/ref, human-readable meaning, next owner, and whether it blocks closeout.

## Acceptance matrix

| ID | Priority | Coverage | Method | Pass criteria |
| --- | --- | --- | --- | --- |
| V1-AC-001 | P0 | `task-fact-view.v1` schema | Unit/contract test | Projection returns `schemaVersion: task-fact-view.v1`, preserves V0-compatible identity/status/source/result keys, and adds V1 blocks. |
| V1-AC-002 | P0 | Read-only boundary | API/CLI/workbench review | No edit, claim, reassign, retry, accept, reject, close, knowledge-write, evidence-write, or lease mutation operation exists in fact view. |
| V1-AC-003 | P0 | PM parent control | Integration fixture FX-001 | Parent task identifies PM controller, worker refs, PM consolidation, result evidence, acceptance route, and next owner. |
| V1-AC-004 | P0 | Worker role boundary | Integration/negative fixtures FX-001, FX-014 | Worker role, input, allowed/forbidden actions, output format, evidence requirements, and handoff receiver are visible; boundary violation is not hidden. |
| V1-AC-005 | P0 | Worker result not final result | Integration fixture FX-001 | Worker TaskResult cannot be displayed as final parent conclusion without PM consolidation. |
| V1-AC-006 | P0 | Missing ReceiverReview | Negative fixture FX-002 | Missing worker review is marked with `missing_worker_review`; no false accepted-for-work state. |
| V1-AC-007 | P0 | Missing worker TaskResult | Negative fixture FX-003 | Missing result is marked with `missing_worker_result`; parent cannot show complete closed loop. |
| V1-AC-008 | P0 | Missing evidence/tests/checks | Negative fixture FX-004 | Missing evidence or checks produce `result evidence gap`; no passed/accepted inference. |
| V1-AC-009 | P0 | Missing audit/notification | Negative fixture FX-005 | Missing audit or notification refs are visible and assigned to next owner. |
| V1-AC-010 | P0 | Capability version match | Contract fixture FX-006 | Required version, runner version, source/digest, and match state are visible. |
| V1-AC-011 | P0 | Capability version mismatch | Scheduler/API/CLI fixture FX-007 | Mismatch is rejected or marked `capability_version_mismatch`; task is not silently assigned. |
| V1-AC-012 | P0 | Same-project multi-computer competition | Negative fixture FX-008 | Same-project claim/co-execution is rejected or marked unsupported; no accepted concurrent execution. |
| V1-AC-013 | P1 | Different-project multi-computer allowed | Fixture FX-009 | Different projects can run independently when capability versions match. |
| V1-AC-014 | P0 | Growth signal from quality failure | Fixture FX-010 | Failure creates draft improvement/eval refs or explicit `learning loop gap`; no auto-publication. |
| V1-AC-015 | P1 | Growth signal from rework/manual correction/repeated blocker | Fixtures FX-011, FX-012, FX-013 | Signal includes taskId, role, cause, evidence, reuse scope, and review route. |
| V1-AC-016 | P0 | API/CLI/workbench parity | Fixture FX-016 | API JSON, CLI JSON/markdown, and workbench show same facts/gaps; UI may format labels but cannot drop P0 gaps. |
| V1-AC-017 | P0 | Human-readable workbench | Workbench screenshot/DOM check | Primary labels explain task source, gap meaning, owner, and next step without relying on raw IDs alone. |
| V1-AC-018 | P0 | V0 compatibility | Regression fixture FX-015 | Existing V0 active status examples still render; legacy records show gaps rather than crash or false success. |
| V1-AC-019 | P0 | Governance and review route | Audit/TaskResult review | Growth signals remain draft/review-required; verified knowledge, policy, skill, role rule, permission, or security changes require review/human approval. |
| V1-AC-020 | P0 | No core object or execution-chain rewrite | Diff/architecture review | No new durable truth object duplicates ProjectTask/TaskResult/AgentRun/AgentRunner; Scheduler/Agent Ring writeback is not behaviorally replaced. |

## Suggested automated checks

Run after development handoff:

```bash
python3 -m zhenzhi_knowledge.cli validate
python3 -m unittest
git diff --check
```

Run or add targeted tests where implementation exposes them:

```bash
python3 -m zhenzhi_knowledge.cli task fact --project company-knowledge-core --task <fixture-task-id> --format json
python3 -m zhenzhi_knowledge.cli task fact --project company-knowledge-core --task <fixture-task-id> --format markdown
```

API/workbench checks should compare the same fixture task IDs against the CLI output and record evidence in the later test report.

## Defect creation rule

During formal execution, create or update a Defect when:

- any P0 acceptance item fails;
- implementation declares success while required evidence is missing;
- API/CLI/workbench disagree on a P0 fact or gap;
- same-project multi-computer execution is accepted instead of rejected/marked unsupported;
- growth signal auto-publishes unreviewed knowledge, skill, role rule, policy, or workflow;
- Test Agent would need to edit implementation files to make tests pass.

## Release blockers

- Development TaskResult missing.
- Any P0 item fails or remains untriaged.
- Implementation lacks executable entry point for projection or parity checks.
- Missing evidence is shown as success.
- Worker result bypasses PM consolidation.
- Capability mismatch is ignored.
- Same-project multi-computer competition is treated as supported.
- Growth signal becomes verified/company-level without review.

## Later execution report requirements

The later test execution TaskResult must include:

- development TaskResult ref;
- fixture IDs executed;
- exact commands and outputs or report refs;
- API/CLI/workbench parity evidence;
- screenshots or DOM/API evidence for workbench P0 items;
- defectRefs for failures;
- explicit blocked/fail/pass status for every P0 item.
