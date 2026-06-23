---
type: RoleOperatingReview
title: "Role operating review: 项目经理 Agent"
description: Executable role operating-system readiness check.
timestamp: "2026-06-20T08:18:54Z"
reviewId: role-review-project-manager.20260620T081854708081Z
roleId: project-manager
roleName: 项目经理 Agent
projectId: ""
actor: system.project-manager
defaultAgentId: agent.company.project-manager
status: ready
gapCount: 0
warningCount: 0
taskCount: 0
openTaskCount: 0
skillPackRef: docs/agent-team/project-manager-agent-skill-pack.md
guideRef: docs/agent-team/company-agent-team-operating-guide.md
commonRulesRef: docs/agent-team/common-agent-operating-rules.md
followupTaskRefs: []
notificationRefs: []
---

## Summary

- role: 项目经理 Agent
- status: ready
- projectId: company
- defaultAgentId: agent.company.project-manager
- skillPackRef: docs/agent-team/project-manager-agent-skill-pack.md

## Gaps

- none

## Warnings

- none

## Responsibilities

- 项目启动
- 任务拆解
- 跨岗位协同
- 风险和阻塞管理
- 验收路由
- 状态通知
- 交付闭环

## Skills

- project-intake
- task-decomposition
- project-health-check
- handoff-routing
- acceptance-routing
- notification-recovery
- retrospective-trigger

## Workflow

- 接收项目目标
- 建立或绑定项目
- 选择岗位 Agent
- 创建任务队列
- 执行 project health
- 路由 TaskResult
- 通知相关方
- 关闭或升级

## Acceptance Checks

- 项目 Owner 明确
- 任务有输入输出和验收标准
- 风险有 owner 和下一步
- TaskResult 有质量评价
- 通知链路有状态

## Boundaries

- 不替产品做产品决策
- 不替研发写生产代码
- 不替测试签最终质量
- 不替知识工程发布知识
