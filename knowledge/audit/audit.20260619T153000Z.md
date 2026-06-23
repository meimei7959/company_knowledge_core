---
type: AuditLog
title: audit.20260619T153000Z
timestamp: 2026-06-19T15:30:00Z
auditId: audit.20260619T153000Z
actor: agent.company-knowledge-core.knowledge-engineering
action: agent_team.acceptance_gate.implemented
targetRef: docs/agent-team/company-agent-team-operating-guide.md
before: role handoff could create the next ProjectTask immediately after finish
after: role handoff waits for PM notification and human or auto acceptance before creating the next ProjectTask
policyResult: guide_updated
---

## Details

用户指出每个岗位交付后需要通知项目经理，由项目经理判断是否需要人类验收；默认需要人类验收，通过后才进入下一环节。

本次更新：

- `TaskResult` 增加 `acceptancePolicy`，记录验收状态、项目经理 Agent、人类验收人、原因和后续任务要求。
- `finish_project_task` 不再直接把通过的岗位交付推给下一岗位，而是先进入验收门。
- `accept_project_task_result` 负责验收通过、自动验收、拒绝和要求修改，并创建下一岗位或返工任务。
- CLI、HTTP API 和飞书卡片动作统一调用同一套验收函数。
- 知识工程内部抽取、Review、Publish 链路允许内部自动验收继续流转；成为 verified、policy、权限或跨团队规则时仍需人类审批。
- 工作指南同步更新，明确 TaskResult -> PM 通知 -> 人类/自动验收 -> 下一任务或返工的闭环规则。

## Verification

- 定点验收链路测试通过：finish 后无下一任务；human accept 后创建下一岗位任务；changes_requested 后创建返工任务；飞书卡片动作可写回验收决策。
