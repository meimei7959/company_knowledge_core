---
type: RoleOperatingReview
title: "Role operating review: 项目经理 Agent"
description: Executable role operating-system readiness check.
timestamp: "2026-06-24T05:06:34Z"
reviewId: role-review-project-manager.20260624T050634959678Z
roleId: project-manager
roleName: 项目经理 Agent
projectId: company-knowledge-core
actor: agent.company.project-manager
defaultAgentId: agent.company.project-manager
status: ready
gapCount: 0
warningCount: 0
taskCount: 30
openTaskCount: 12
roleProfileRef: docs/agent-team/project-manager-agent-skill-pack.md
skillRegistryRef: docs/agent-team/company-skill-registry.json
skillRefs:
  - project-task-decomposition
  - project-health-orchestration
capabilityTags:
  - project-intake
  - task-decomposition
  - project-health-check
  - handoff-routing
  - acceptance-routing
  - notification-recovery
  - retrospective-trigger
guideRef: docs/agent-team/company-agent-team-operating-guide.md
commonRulesRef: docs/agent-team/common-agent-operating-rules.md
qualityEvaluationTemplate: {"artifactTypes":["ProjectManagerReview","ProjectTask","NotificationRecord","acceptancePolicy"],"requiredEvidence":["项目记录","任务队列","TaskResult","Runner/通知/审批状态"],"qualityChecks":["项目状态判断有证据","风险和决策有 owner","需要人类验收时已通知","不替代其他岗位产出"],"failureRoutes":["缺项目上下文 -> 项目初始化修复任务","通知失败 -> 通知重试/死信处理","跨岗位产物缺失 -> 回派对应岗位","重大决策缺 owner -> 人类确认"]}
followupTaskRefs: []
notificationRefs: []
---

## Summary

- role: 项目经理 Agent
- status: ready
- projectId: company-knowledge-core
- defaultAgentId: agent.company.project-manager
- roleProfileRef: docs/agent-team/project-manager-agent-skill-pack.md
- skillRegistryRef: docs/agent-team/company-skill-registry.json

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
- 上线软著材料任务触发和追踪

## Production Skills

- project-task-decomposition
- project-health-orchestration

## Capability Tags

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
- Release Candidate 或上线关闭前判断是否需要软著材料任务
- 编辑前判定文件/产物归属
- 执行 project health
- 路由 TaskResult
- 通知相关方
- 关闭或升级

## Acceptance Checks

- 项目 Owner 明确
- 任务有输入输出和验收标准
- 需要软著的项目已路由知识工程 Agent 准备材料包
- 风险有 owner 和下一步
- TaskResult 有质量评价
- 通知链路有状态

## Quality Evaluation Template

### Artifact Types

- ProjectManagerReview
- ProjectTask
- NotificationRecord
- acceptancePolicy

### Required Evidence

- 项目记录
- 任务队列
- TaskResult
- Runner/通知/审批状态

### Quality Checks

- 项目状态判断有证据
- 风险和决策有 owner
- 需要人类验收时已通知
- 不替代其他岗位产出

### Failure Routes

- 缺项目上下文 -> 项目初始化修复任务
- 通知失败 -> 通知重试/死信处理
- 跨岗位产物缺失 -> 回派对应岗位
- 重大决策缺 owner -> 人类确认

## Boundaries

- 不替产品做产品决策
- 不替研发写生产代码
- 不替测试签最终质量
- 不替知识工程发布知识
- 编辑任何文件前先判定产物归属，非 PM 产物只创建任务或交接
