---
type: EvalRun
title: Agent team growth and task fact V1 test report
projectId: company-knowledge-core
taskId: kt-agent-team-growth-task-fact-test-execution
testerAgent: agent.company.test
status: done
decision: test_passed
createdAt: "2026-06-23T09:45:29Z"
updatedAt: "2026-06-23T09:45:29Z"
requirementRefs:
  - ANOS-REQ-160
  - ANOS-REQ-160-FUSION-V1
sourceRefs:
  - projects/company-knowledge-core/tasks/kt-agent-team-growth-task-fact-test-execution.md
  - projects/company-knowledge-core/test-plans/agent-team-growth-task-fact-test-plan.md
  - task-results/tr-kt-agent-team-growth-task-fact-development.md
  - docs/product/ai-native-os/agent-team-growth-and-task-fact-prd.md
  - docs/product/ai-native-os/task-execution-productization-acceptance-matrix.md
evidenceRefs:
  - tests/test_cli.py
  - task-results/tr-kt-agent-team-growth-task-fact-development.md
  - knowledge/audit/audit.20260623T094529Z-agent-team-growth-task-fact-test-execution.md
defectRefs: []
blockedBy: []
---

# Agent team growth and task fact V1 test report

## Conclusion

Test status: `passed`.

Task-fact V1 behavior checks passed. Final repository validation and diff whitespace checks passed. No implementation Defect or Development bugfix task was created.

This report does not perform Product acceptance.

## Commands and Results

| Check | Command / method | Result |
| --- | --- | --- |
| Focused task fact V1 unittest | `python3 -m unittest -v tests.test_cli.CliTests.test_task_fact_view_core_cli_api_and_p0_gaps` | passed, 1 test |
| Full CLI regression file | `boost python3 -m unittest tests.test_cli` | passed, 194 tests, 14 skipped |
| Independent formal fixture probe | `ctx_execute` JavaScript temporary bundle invoking `build_task_fact_view` | passed capability mismatch, same-project unsupported, different-project allowed, all read-only |
| Bundle validation | `python3 -m zhenzhi_knowledge.cli validate` | `valid` |
| Diff whitespace check | `git diff --check` | passed |

## Evidence Summary

- Focused unittest covers `task-fact-view.v1` happy path `PM-V1`, sparse gap path `SPARSE-V1`, V0 compatibility, CLI JSON output, HTTP API output, and workbench `selectedTaskFactView`.
- Independent fixture probe confirmed `CAP-MISMATCH` reports `capability_version_mismatch`, `SAME-PROJECT-RACING` reports `unsupported_multi_computer_project_execution`, and `DIFFERENT-PROJECT` keeps `projectIsolation: single_project_execution`.
- Workbench evidence is read-model/API evidence: `workbench_project_execution_read_model` exposes the same `selectedTaskFactView` schema as core/API. No separate DOM surface was changed by the development task.

## Acceptance Matrix

| ID | Priority | Status | Evidence |
| --- | --- | --- | --- |
| V1-AC-001 | P0 | pass | Focused unittest asserts `schemaVersion: task-fact-view.v1`, V0 compatibility remains available, and V1 fact blocks are present. |
| V1-AC-002 | P0 | pass | Projection returns `readOnly: true`; CLI/API/workbench paths call read-model builders only. |
| V1-AC-003 | P0 | pass | `PM-V1` exposes PM controller, worker refs, worker result/evidence, and consolidation refs. |
| V1-AC-004 | P0 | pass | Worker identity, role refs, ReceiverReview refs, result refs, evidence refs, and missing-boundary gaps are visible. |
| V1-AC-005 | P0 | pass | Worker result refs stay under `workerParticipation.consolidationRefs`; parent result remains separate. |
| V1-AC-006 | P0 | pass | `SPARSE-V1` reports `missing_receiver_review` and `missing_worker_review`. |
| V1-AC-007 | P0 | pass | `SPARSE-V1` reports `missing_worker_result`. |
| V1-AC-008 | P0 | pass | Focused unittest verifies result evidence gaps including `worker.evidenceRefs` and missing `testsOrChecks`. |
| V1-AC-009 | P0 | pass | `SPARSE-V1` reports `missing_audit`; audit refs are exposed in V1 facts. |
| V1-AC-010 | P0 | pass | `PM-V1` reports matching capability version; independent fixture confirms match state. |
| V1-AC-011 | P0 | pass | Independent `CAP-MISMATCH` fixture reports `capability_version_mismatch` and `match: false`. |
| V1-AC-012 | P0 | pass | Independent `SAME-PROJECT-RACING` fixture reports `unsupported_multi_computer_project_execution`. |
| V1-AC-013 | P1 | pass | Independent `DIFFERENT-PROJECT` fixture keeps capability match and does not report unsupported same-project execution. |
| V1-AC-014 | P0 | pass | Quality failure / required signal path produces growth refs or `growth_signal_gap`; no auto-publication is performed. |
| V1-AC-015 | P1 | pass_with_scope_note | Implementation supports generic `qualitySignals` values for rework, manual correction, and repeated blocker; test evidence covers shared growth refs/gap behavior, not Product acceptance of each future workflow source. |
| V1-AC-016 | P0 | pass | CLI JSON, HTTP API JSON, and workbench read model expose the same V1 schema and PM controller. |

## Notes

- The first validation run failed because the newly created Test ReceiverReview used an invalid decision value; this was a Test Agent artifact error, fixed before final validation.
- A transient validation failure was observed while the local skill package was incomplete; after the package resources appeared in the workspace, final validation returned `valid`.
- No implementation files were changed during test execution.
