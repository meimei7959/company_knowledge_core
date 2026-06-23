---
type: EvalCase
title: Agent improvement regression for kt-v1-workbench-user-copy-polish-test
description: Regression case generated from a failed or rejected Agent delivery.
timestamp: "2026-06-22T09:25:10Z"
evalId: eval-agent-improvement-kt-v1-workbench-user-copy-polish-test.20260622T092510820541Z
owner: agent.company.test
status: draft
targetRef: task-results/tr-kt-v1-workbench-user-copy-polish-test.md
agentTargetRef: agents/agent.company.test.md
sourceResultRef: task-results/tr-kt-v1-workbench-user-copy-polish-test.md
taskId: kt-v1-workbench-user-copy-polish-test
projectId: company-knowledge-core
requires:
  - summary
  - evidence or artifact refs
  - qualityEvaluation
  - handoff or terminal reason
  - next action
expected: TaskResult must include summary, evidence/artifacts, qualityEvaluation, handoff/terminal reason, and retry or escalation decision when it fails.
---

## Trigger

- taskId: kt-v1-workbench-user-copy-polish-test
- resultRef: task-results/tr-kt-v1-workbench-user-copy-polish-test.md
- agentId: agent.company.test

## Failure Reasons

- tests/checks reported failure

## Expected

TaskResult must include summary, evidence/artifacts, qualityEvaluation, handoff/terminal reason, and retry or escalation decision when it fails.

## Usage

This EvalCase is a draft regression guard. The responsible Agent or Skill maintainer should refine it, run it against the improved workflow/skill, and only promote it after review.
