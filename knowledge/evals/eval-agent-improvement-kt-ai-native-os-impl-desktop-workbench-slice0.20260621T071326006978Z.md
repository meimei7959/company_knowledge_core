---
type: EvalCase
title: Agent improvement regression for kt-ai-native-os-impl-desktop-workbench-slice0
description: Regression case generated from a failed or rejected Agent delivery.
timestamp: "2026-06-21T07:13:26Z"
evalId: eval-agent-improvement-kt-ai-native-os-impl-desktop-workbench-slice0.20260621T071326006978Z
owner: agent.company.development-engineer
status: draft
targetRef: task-results/tr-kt-ai-native-os-impl-desktop-workbench-slice0.md
agentTargetRef: agent.company.development-engineer
sourceResultRef: task-results/tr-kt-ai-native-os-impl-desktop-workbench-slice0.md
taskId: kt-ai-native-os-impl-desktop-workbench-slice0
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

- taskId: kt-ai-native-os-impl-desktop-workbench-slice0
- resultRef: task-results/tr-kt-ai-native-os-impl-desktop-workbench-slice0.md
- agentId: agent.company.development-engineer

## Failure Reasons

- missing tests/checks
- common rule: engineering/test task missing tests or checks

## Expected

TaskResult must include summary, evidence/artifacts, qualityEvaluation, handoff/terminal reason, and retry or escalation decision when it fails.

## Usage

This EvalCase is a draft regression guard. The responsible Agent or Skill maintainer should refine it, run it against the improved workflow/skill, and only promote it after review.
