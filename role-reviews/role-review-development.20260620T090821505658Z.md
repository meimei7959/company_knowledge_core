---
type: RoleOperatingReview
title: "Role operating review: 研发 Agent"
description: Executable role operating-system readiness check.
timestamp: "2026-06-20T09:08:21Z"
reviewId: role-review-development.20260620T090821505658Z
roleId: development
roleName: 研发 Agent
projectId: ""
actor: system.project-manager
defaultAgentId: agent.company.development
status: ready
gapCount: 0
warningCount: 0
taskCount: 0
openTaskCount: 0
skillPackRef: docs/agent-team/development-agent-role-and-skill-pack.md
localSkillRef: skills/development-agent/SKILL.md
guideRef: docs/agent-team/company-agent-team-operating-guide.md
commonRulesRef: docs/agent-team/common-agent-operating-rules.md
qualityEvaluationTemplate: {"artifactTypes":["code refs","technical plan","test/check refs","rollback note"],"requiredEvidence":["需求/设计/任务上下文","代码变更引用","测试或检查输出","环境/迁移/风险说明"],"qualityChecks":["实现符合需求和设计","变更范围受控","测试或未测原因明确","安全/权限/迁移风险清楚"],"failureRoutes":["测试失败 -> 研发返工","需求冲突 -> 产品经理确认","设计冲突 -> 设计 Agent 确认","权限/环境阻塞 -> PM/Runner 修复"]}
followupTaskRefs: []
notificationRefs: []
---

## Summary

- role: 研发 Agent
- status: ready
- projectId: company
- defaultAgentId: agent.company.development
- skillPackRef: docs/agent-team/development-agent-role-and-skill-pack.md
- localSkillRef: skills/development-agent/SKILL.md

## Gaps

- none

## Warnings

- none

## Responsibilities

- 技术方案
- 代码实现
- 数据和接口
- 集成调试
- 自测
- 部署支持
- 工程知识沉淀

## Skills

- architecture-design
- frontend-development
- backend-development
- database-migration
- api-integration
- debugging
- automated-test
- deployment

## Workflow

- 读取上下文
- 出技术方案
- 实现代码
- 自测
- 记录证据和风险
- 提交 TaskResult
- 交给测试
- 按反馈返工

## Acceptance Checks

- 代码可运行
- 测试或检查有记录
- 变更范围清楚
- 风险和回滚清楚
- 没有绕过权限和安全边界

## Quality Evaluation Template

### Artifact Types

- code refs
- technical plan
- test/check refs
- rollback note

### Required Evidence

- 需求/设计/任务上下文
- 代码变更引用
- 测试或检查输出
- 环境/迁移/风险说明

### Quality Checks

- 实现符合需求和设计
- 变更范围受控
- 测试或未测原因明确
- 安全/权限/迁移风险清楚

### Failure Routes

- 测试失败 -> 研发返工
- 需求冲突 -> 产品经理确认
- 设计冲突 -> 设计 Agent 确认
- 权限/环境阻塞 -> PM/Runner 修复

## Boundaries

- 不做产品范围决策
- 不替设计决定体验
- 不替测试签发布质量
- 不直接发布未经审核知识
