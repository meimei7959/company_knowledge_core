---
type: Workflow
title: Agent team growth task fact V1 quality remediation plan
description: Architecture remediation boundary for DEF-AGTGTF-QUALITY-GATE-001 after ANOS-REQ-160-FUSION-V1 development quality gate failure.
timestamp: "2026-06-23T10:09:40Z"
solutionId: agent-team-growth-task-fact-quality-remediation-plan
projectId: company-knowledge-core
ownerAgent: agent.company.architecture
status: draft
requirementRefs:
  - ANOS-REQ-160-FUSION-V1
defectRefs:
  - DEF-AGTGTF-QUALITY-GATE-001
sourceRefs:
  - projects/company-knowledge-core/tasks/kt-agtgtf-quality-architecture-review.md
  - projects/company-knowledge-core/defects/def-agtgtf-quality-gate-001.md
  - task-results/tr-kt-agent-team-growth-task-fact-development.md
  - projects/company-knowledge-core/technical-solutions/agent-team-growth-and-task-fact-technical-solution.md
  - scripts/quality/development_quality_gate.py
  - skills/development-engineering-quality-gate/SKILL.md
---

# Agent team growth task fact V1 quality remediation plan

## Decision

DEF-AGTGTF-QUALITY-GATE-001 is valid. The V1 implementation passed functional checks, but it placed new task-fact V1 projection logic and V1 test fixture logic into existing god files. That violates the Development Engineering Quality Gate rule: do not add new logic to existing god files when a local module boundary is available.

Architecture decision:

- `build_task_fact_view` must be split out of `zhenzhi_knowledge/core.py` into a task-fact read-model module.
- Task fact V1 tests must be split out of `tests/test_cli.py` into a dedicated task-fact test module.
- `zhenzhi_knowledge/core.py` may retain a stable compatibility wrapper or import for existing CLI/API/server callers.
- CLI and HTTP API must continue to return the same projection contract; no parallel reader may be created.
- Full-repository gate failures caused by unrelated historical or parallel work must be tracked separately and must not block this V1 remediation once the V1-owned paths pass.

## Gate evidence

Commands executed by Architecture Agent:

| Command | Result |
| --- | --- |
| `python3 -m zhenzhi_knowledge.cli validate` | pass, output `valid` |
| `git diff --check` | pass, no output |
| `python3 scripts/quality/development_quality_gate.py --root . --architecture-review-ref projects/company-knowledge-core/technical-solutions/agent-team-growth-and-task-fact-technical-solution.md --json` | fail, 5697 changed files, mixed historical and current findings |
| `python3 scripts/quality/development_quality_gate.py --root . --architecture-review-ref projects/company-knowledge-core/technical-solutions/agent-team-growth-and-task-fact-technical-solution.md --json --paths zhenzhi_knowledge/core.py tests/test_cli.py` | fail on task-fact implementation and test concentration plus pre-existing god-file findings |

Task-specific reproduction showed:

- `zhenzhi_knowledge/core.py` has `large_file_over_limit`, `large_growth`, and `long_symbol build_task_fact_view at line 3808 is 243 lines`.
- `tests/test_cli.py` has `large_file_over_limit`, `large_growth`, `long_symbol CliTests`, and `long_symbol test_task_fact_view_core_cli_api_and_p0_gaps at line 1340 is 478 lines`.
- Diff attribution shows the task-fact V1 test neighborhood added about 627 lines, including about 583 lines inside or adjacent to the task-fact V1 monolithic test.
- `build_task_fact_view` is imported by CLI and server and is used by workbench read model, so the public symbol must remain stable even when implementation moves.

## Must fix in this V1 remediation

These failures are part of ANOS-REQ-160-FUSION-V1 and must be repaired before Development Agent hands the work back to Test Agent or Project Manager Agent:

| Failure | Path | Required remediation |
| --- | --- | --- |
| `long_symbol` | `zhenzhi_knowledge/core.py`, `build_task_fact_view` | Move task-fact projection implementation into a dedicated module such as `zhenzhi_knowledge/task_fact_view.py` or `zhenzhi_knowledge/task_fact_view/__init__.py`. Keep only a small wrapper/import in `core.py`. |
| V1-caused `large_growth` | `zhenzhi_knowledge/core.py` | Remove V1 projection implementation growth from `core.py`. New V1 logic must live behind the module boundary. |
| V1-caused `large_file_over_limit` | `zhenzhi_knowledge/core.py` | The whole historical file cannot be reduced in this V1 task, but no new task-fact V1 logic may remain there except compatibility glue. |
| `long_symbol` | `tests/test_cli.py`, `test_task_fact_view_core_cli_api_and_p0_gaps` | Move V1 fixture setup and assertions into dedicated test classes and helper functions in a task-fact test file. Split lifecycle, CLI/API parity, workbench, gaps, growth, and capability assertions. |
| V1-caused `large_growth` | `tests/test_cli.py` | Remove task-fact V1 bulk from `tests/test_cli.py`. Leave at most a narrow legacy CLI smoke test if needed. |
| V1-caused `large_file_over_limit` | `tests/test_cli.py` | The whole historical test file can remain a tracked debt, but V1 must not add its main coverage there. |

Functional behavior that must stay unchanged:

- V0-compatible keys stay present.
- V1 fields trigger `schemaVersion: task-fact-view.v1`.
- CLI `task fact`, HTTP `GET /v0/projects/{projectId}/tasks/{taskId}/fact-view`, and workbench selected task fact view use the same read model.
- Missing evidence, missing receiver review, missing worker result, growth-signal gap, capability mismatch, and unsupported same-project multi-computer execution remain visible as machine-readable gaps.

## Historical debt follow-up

These findings are real engineering debt but not V1-specific blockers after V1-owned code is extracted. They must be tracked as follow-up quality tasks:

| Tracking id | Finding | Evidence | Follow-up scope |
| --- | --- | --- | --- |
| `FOLLOWUP-QUALITY-GOD-FILES-CORE-001` | `zhenzhi_knowledge/core.py` is 18633 lines and has many long symbols unrelated to task fact V1. | Full gate `large_file_over_limit`, `large_growth`, multiple `long_symbol` entries. | Plan staged core module extraction by domain: project lifecycle, workbench read models, review/approval, requirement tree, validation, metrics. |
| `FOLLOWUP-QUALITY-GOD-FILES-CLI-001` | `zhenzhi_knowledge/cli.py` is 2217 lines and has long `make_parser` and `main`. | Full gate `large_file_over_limit`, `large_growth`, `long_symbol`. | Split command groups behind parser factories and command handlers. |
| `FOLLOWUP-QUALITY-GOD-FILES-FEISHU-001` | `zhenzhi_knowledge/feishu.py` is 5506 lines. | Full gate `large_file_over_limit`, `large_growth`. | Split Feishu card, routing, callback, and API adapter surfaces. |
| `FOLLOWUP-QUALITY-GOD-FILES-TEST-001` | `tests/test_cli.py` is 12140 lines with many unrelated long test methods. | Full gate `large_file_over_limit`, `large_growth`, `CliTests` long class, many long historical methods. | Incrementally move domain tests into dedicated test modules. |
| `FOLLOWUP-QUALITY-GOD-FILES-SERVER-001` | `zhenzhi_knowledge/server.py` warns at 891 lines and grew by 721 lines. | Full gate `large_growth`, `large_file_warning`. | Split route handling and server adapters when server work resumes. |
| `FOLLOWUP-QUALITY-SCRIPTS-001` | Some scripts and skill scripts exceed line or symbol limits. | `scripts/agent_ring_contract.py`, `scripts/validate_desktop_workbench_slice0.py`, `skills/.../softcopyright.py`. | Create script-specific quality debt tasks outside ANOS-REQ-160-FUSION-V1. |

These follow-ups are traceable from this plan and DEF-AGTGTF-QUALITY-GATE-001. They should be turned into ProjectTask or Defect records by Project Manager Agent before full-repository gate is used as a release blocker.

## Path-scoped quality gate policy

Task-specific `--paths` is allowed for this remediation because the worktree contains thousands of unrelated changed files and the full gate cannot isolate ANOS-REQ-160-FUSION-V1 ownership.

Allowed path groups:

| Group | Required paths |
| --- | --- |
| V1 projection module | New task-fact read-model module, for example `zhenzhi_knowledge/task_fact_view.py` or `zhenzhi_knowledge/task_fact_view/` |
| Compatibility wrappers | `zhenzhi_knowledge/core.py` only if the remediation changes the public wrapper/import |
| CLI/API adapters | `zhenzhi_knowledge/cli.py` and `zhenzhi_knowledge/server.py` only if the remediation changes task-fact command or route wiring |
| V1 tests | New dedicated task-fact test file, for example `tests/test_task_fact_view.py` |
| Legacy test shim | `tests/test_cli.py` only if it keeps or adjusts a narrow CLI smoke test |

Required command shape:

```bash
python3 scripts/quality/development_quality_gate.py \
  --root . \
  --architecture-review-ref projects/company-knowledge-core/technical-solutions/agent-team-growth-task-fact-quality-remediation-plan.md \
  --paths zhenzhi_knowledge/task_fact_view.py tests/test_task_fact_view.py
```

If adapter files are touched, add them to `--paths` and classify any remaining god-file findings as either fixed V1 failures or historical debt in the Development TaskResult. A path-scoped pass over new V1-owned module and test files is mandatory. A full gate run is still required as evidence, but known historical findings above do not block this remediation.

## Development task sequence

| Order | Task | Pass standard |
| --- | --- | --- |
| 1 | Extract task-fact read model module | `build_task_fact_view` public entry remains importable from `zhenzhi_knowledge.core`; implementation lives in a dedicated task-fact module; `core.py` contains only compatibility glue for this feature; CLI/server/workbench still use one shared projector. |
| 2 | Split task-fact V1 tests | `tests/test_task_fact_view.py` or equivalent owns V1 fixture and assertions; task-fact V1 tests are split by behavior; no V1 monolithic 400+ line test remains in `tests/test_cli.py`; legacy smoke in `tests/test_cli.py` is narrow. |
| 3 | Re-run focused functional checks | Focused task-fact V1 tests pass; CLI JSON and HTTP API parity remain covered; workbench selected task fact view remains covered; V0 compatibility remains covered. |
| 4 | Re-run project checks | `python3 -m zhenzhi_knowledge.cli validate` passes; `git diff --check` passes; path-scoped development quality gate over V1-owned paths passes. |
| 5 | Record residual debt | Development TaskResult lists full gate residual findings under the follow-up tracking ids in this plan; it must not claim full gate clean unless those separate debts are actually fixed. |

## Acceptance boundary

Project Manager Agent may send the remediated V1 work to Test Agent when:

- the mandatory V1 failures above are fixed;
- path-scoped gate over V1-owned module and test paths passes;
- validate and diff-check pass;
- focused V1 tests and relevant CLI/API/workbench parity checks pass;
- Development TaskResult links this architecture remediation plan and records residual historical debt without treating it as solved.

Project Manager Agent must not close DEF-AGTGTF-QUALITY-GATE-001 as fully resolved until either the full gate passes or the historical follow-up tasks are created and accepted as separate release debt.
