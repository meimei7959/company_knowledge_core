---
name: development-engineering-quality-gate
description: Use for Development Agent work in company_knowledge_core before and after code changes. Enforces scoped implementation, large-file/god-module control, high-risk core-file review, required tests, TaskResult evidence, and handoff to Test/Architecture.
---

# Development Engineering Quality Gate

## Purpose

Keep Development Agent changes maintainable, scoped, testable, and reviewable in the AI-native OS codebase.

## Triggers

Use for every Development Agent implementation, bugfix, refactor, migration, CLI/API/workbench change, or generated code patch.

## Inputs

- ProjectTask, requirement, defect, or technical solution ref.
- ReceiverReview decision.
- Expected changed files and high-risk paths.
- Test/check expectations.
- Architecture review ref when required.

## Hard Rules

1. Do not code before upstream `ReceiverReview` is `accepted_for_work` or `accepted_with_assumptions`.
2. Keep the change scoped to the task. No unrelated refactor, formatting churn, dependency churn, or metadata churn.
3. Do not add new logic to existing god files when a local module boundary is available.
4. Touching high-risk files requires architecture review evidence:
   - `zhenzhi_knowledge/core.py`
   - `zhenzhi_knowledge/cli.py`
   - `zhenzhi_knowledge/server.py`
   - `zhenzhi_knowledge/feishu.py`
   - scheduler, runner, TaskResult, AuditLog, Review, PM lease, permission, or knowledge indexing paths.
5. Any change to Scheduler, Runner, TaskResult, AgentRun, AuditLog, Review, permission, acceptance, notification, database, or index behavior requires targeted tests or an explicit blocker.
6. Development Agent cannot sign final QA, product acceptance, architecture approval, or verified knowledge.
7. TaskResult must include code refs, test/check refs or exact untested reason, risks, rollback/migration notes, quality evaluation, and handoff target.

## Before Editing

State:

- task and requirement refs;
- files expected to change;
- high-risk files expected to be touched;
- tests/checks expected;
- whether architecture review is required;
- rollback or migration risk.

## Workflow

1. Confirm ReceiverReview is accepted.
2. Identify task scope, high-risk files, required tests, and architecture-review need.
3. Implement only the scoped change.
4. Run targeted tests/checks.
5. Run the development quality toolkit.
6. Repair failures or route to Architecture/Test/PM with blocker evidence.
7. Write TaskResult with code refs, quality gate verdict, tests, risk, rollback, and handoff.

## After Editing

Run the narrowest meaningful tests first, then broader checks when feasible. Always run the project quality toolkit:

```bash
python3 scripts/quality/development_quality_gate.py --root .
```

Use flags only when evidence exists:

```bash
python3 scripts/quality/development_quality_gate.py --root . --architecture-review-ref <ref>
python3 scripts/quality/development_quality_gate.py --root . --allow-missing-tests <reason>
```

## Outputs

- Implementation summary.
- Changed file refs.
- Quality gate command and verdict.
- Test/check refs or blocker reason.
- Architecture review ref when required.
- Risk, rollback, and handoff.

## Quality Gate

Pass only when the change is scoped, high-risk files have review evidence, large-file/long-symbol findings are resolved or routed, required tests are present or explicitly blocked, and TaskResult evidence is complete.

## Failure Routes

- Quality gate `fail`: repair before handoff, or route to Architecture/PM with blocker evidence.
- High-risk file touched without review: hand off to Architecture Agent.
- Tests missing for required area: hand off to Test Agent or record exact environment blocker.
- Repeated same-class failure: create or link `AgentImprovementProposal` and `EvalCase`.

## Output Contract

Development TaskResult must include:

- changed files and why;
- quality gate command and verdict;
- test/check commands and results;
- known risks and rollback;
- architecture review ref when required;
- handoff to Test Agent, Architecture Agent, or PM with clear next action.
