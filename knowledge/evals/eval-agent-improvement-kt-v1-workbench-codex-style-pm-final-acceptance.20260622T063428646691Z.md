---
type: EvalCase
title: Agent improvement regression for kt-v1-workbench-codex-style-pm-final-acceptance
description: Regression case generated from a failed or rejected Agent delivery.
timestamp: "2026-06-22T06:34:28Z"
evalId: eval-agent-improvement-kt-v1-workbench-codex-style-pm-final-acceptance.20260622T063428646691Z
owner: agent.company.project-manager
status: draft
targetRef: task-results/tr-kt-v1-workbench-codex-style-pm-final-acceptance.md
agentTargetRef: agents/agent.company.project-manager.md
sourceResultRef: task-results/tr-kt-v1-workbench-codex-style-pm-final-acceptance.md
taskId: kt-v1-workbench-codex-style-pm-final-acceptance
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

- taskId: kt-v1-workbench-codex-style-pm-final-acceptance
- resultRef: task-results/tr-kt-v1-workbench-codex-style-pm-final-acceptance.md
- agentId: agent.company.project-manager

## Failure Reasons

- tests/checks reported failure

## Expected

TaskResult must include summary, evidence/artifacts, qualityEvaluation, handoff/terminal reason, and retry or escalation decision when it fails.

## Usage

This EvalCase is a draft regression guard. The responsible Agent or Skill maintainer should refine it, run it against the improved workflow/skill, and only promote it after review.
