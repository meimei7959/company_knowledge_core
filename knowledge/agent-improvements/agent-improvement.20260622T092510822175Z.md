---
type: AgentImprovementProposal
title: Improve agent.company.test after kt-v1-workbench-user-copy-polish-test
description: Agent self-improvement proposal generated from task quality evaluation or human acceptance feedback.
timestamp: "2026-06-22T09:25:10Z"
proposalId: agent-improvement.20260622T092510822175Z
owner: agent.company.test
status: draft
agentId: agent.company.test
projectId: company-knowledge-core
taskId: kt-v1-workbench-user-copy-polish-test
resultRef: task-results/tr-kt-v1-workbench-user-copy-polish-test.md
trigger: qualityEvaluation
failureReasons:
  - tests/checks reported failure
reuseScope: company
evalCaseRefs:
  - knowledge/evals/eval-agent-improvement-kt-v1-workbench-user-copy-polish-test.20260622T092510820541Z.md
recommendedActions:
  - Update the responsible Agent skill pack or workflow checklist when the failure is repeatable.
  - Keep the EvalCase as a regression guard before closing the improvement.
  - If the change affects company-level roles, skills, workflow, scheduler, Agent Ring, or knowledge policy, update the company Agent Team guide.
reviewOwner: agent.company.project-manager
---

## Summary

`agent.company.test` 在任务 `kt-v1-workbench-user-copy-polish-test` 中触发改进闭环。这个记录不是最终知识，而是后续 Skill / workflow / EvalCase 修复的入口。

## Trigger

- trigger: qualityEvaluation
- resultRef: task-results/tr-kt-v1-workbench-user-copy-polish-test.md
- reuseScope: company

## Failure Reasons

- tests/checks reported failure

## Eval Cases

- knowledge/evals/eval-agent-improvement-kt-v1-workbench-user-copy-polish-test.20260622T092510820541Z.md

## Recommended Actions

- Update the responsible Agent skill pack or workflow checklist when the failure is repeatable.
- Keep the EvalCase as a regression guard before closing the improvement.
- If the change affects company-level roles, skills, workflow, scheduler, Agent Ring, or knowledge policy, update the company Agent Team guide.

## Reuse Policy

- `company`: 可复用给所有员工、所有项目和所有 Agent Ring Runner，但必须通过 Review 后再成为正式 Skill / 指南 / Eval。
- `project`: 只进入本项目上下文，除非知识工程 Agent 判断可以抽象为公司级经验。
