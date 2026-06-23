---
type: EvalCase
title: Agent improvement regression for project-approval-notification-closed-loop
description: Regression case generated from a failed or rejected Agent delivery.
timestamp: "2026-06-20T15:50:04Z"
evalId: eval-agent-improvement-project-approval-notification-closed-loop.20260620T155004658404Z
owner: agent.company.development
status: draft
targetRef: task-results/tr-project-approval-notification-closed-loop.md
agentTargetRef: agents/agent.company.development.md
sourceResultRef: task-results/tr-project-approval-notification-closed-loop.md
taskId: project-approval-notification-closed-loop
projectId: agent-hub
requires:
  - summary
  - evidence or artifact refs
  - qualityEvaluation
  - handoff or terminal reason
  - next action
expected: TaskResult must include summary, evidence/artifacts, qualityEvaluation, handoff/terminal reason, and retry or escalation decision when it fails.
---

## Trigger

- taskId: project-approval-notification-closed-loop
- resultRef: task-results/tr-project-approval-notification-closed-loop.md
- agentId: agent.company.development

## Failure Reasons

- missing KnowledgeItem draft

## Expected

TaskResult must include summary, evidence/artifacts, qualityEvaluation, handoff/terminal reason, and retry or escalation decision when it fails.

## Usage

This EvalCase is a draft regression guard. The responsible Agent or Skill maintainer should refine it, run it against the improved workflow/skill, and only promote it after review.
