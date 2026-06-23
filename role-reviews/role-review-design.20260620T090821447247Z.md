---
type: RoleOperatingReview
title: "Role operating review: 设计 Agent"
description: Executable role operating-system readiness check.
timestamp: "2026-06-20T09:08:21Z"
reviewId: role-review-design.20260620T090821447247Z
roleId: design
roleName: 设计 Agent
projectId: ""
actor: system.project-manager
defaultAgentId: agent.company.design
status: ready
gapCount: 0
warningCount: 0
taskCount: 0
openTaskCount: 0
skillPackRef: docs/agent-team/design-agent-role-and-skill-pack.md
localSkillRef: skills/design-agent/SKILL.md
guideRef: docs/agent-team/company-agent-team-operating-guide.md
commonRulesRef: docs/agent-team/common-agent-operating-rules.md
qualityEvaluationTemplate: {"artifactTypes":["user flow","interaction spec","state spec","frontend handoff"],"requiredEvidence":["PRD/验收标准","用户路径","设计系统或品牌约束","研发可行性反馈"],"qualityChecks":["主路径和异常路径完整","关键状态齐全","文案/层级/交互可用","研发能按交接实现"],"failureRoutes":["产品范围不清 -> 回产品经理","实现不可行 -> 回研发讨论","状态缺失 -> 设计补齐","体验风险高 -> 人类/PM 确认"]}
followupTaskRefs: []
notificationRefs: []
---

## Summary

- role: 设计 Agent
- status: ready
- projectId: company
- defaultAgentId: agent.company.design
- skillPackRef: docs/agent-team/design-agent-role-and-skill-pack.md
- localSkillRef: skills/design-agent/SKILL.md

## Gaps

- none

## Warnings

- none

## Responsibilities

- 用户流程
- 信息架构
- 交互设计
- 视觉质量
- 设计系统
- 可用性和可访问性
- 研发还原支持

## Skills

- user-flow-design
- information-architecture
- interaction-design
- visual-review
- design-system
- accessibility-check
- frontend-handoff

## Workflow

- 读取 PRD
- 梳理主路径和异常路径
- 设计 IA/交互/状态
- 与产品确认
- 与研发对齐
- 输出交接
- 支持测试验收

## Acceptance Checks

- 主路径完整
- 空态/错误/加载/权限状态齐全
- 文案和布局可实现
- 可访问性风险可见
- 交接材料可被研发使用

## Quality Evaluation Template

### Artifact Types

- user flow
- interaction spec
- state spec
- frontend handoff

### Required Evidence

- PRD/验收标准
- 用户路径
- 设计系统或品牌约束
- 研发可行性反馈

### Quality Checks

- 主路径和异常路径完整
- 关键状态齐全
- 文案/层级/交互可用
- 研发能按交接实现

### Failure Routes

- 产品范围不清 -> 回产品经理
- 实现不可行 -> 回研发讨论
- 状态缺失 -> 设计补齐
- 体验风险高 -> 人类/PM 确认

## Boundaries

- 不决定产品范围
- 不写生产代码
- 不签最终测试质量
