# Evaluation Lifecycle

## Purpose

Evaluation ensures that agent work is judged before it becomes approved knowledge or a delivery record.

## Lifecycle

```txt
Draft output
-> EvalRun or ReviewRecord
-> IssueRecord if failed
-> revision task
-> revised output
-> re-evaluation
-> approval
-> durable writeback
```

## Core Responsibilities

- Store EvalCase and EvalRun records.
- Store ReviewRecord records.
- Store IssueRecord records.
- Preserve target references.
- Preserve reviewer/evaluator identity.
- Preserve status and audit trail.

## Domain Responsibilities

- Define evaluation criteria.
- Run domain-specific evaluation.
- Create revision requirements.
- Decide which outputs need human approval.
