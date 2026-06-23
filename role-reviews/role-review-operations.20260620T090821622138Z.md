---
type: RoleOperatingReview
title: "Role operating review: 运营 Agent"
description: Executable role operating-system readiness check.
timestamp: "2026-06-20T09:08:21Z"
reviewId: role-review-operations.20260620T090821622138Z
roleId: operations
roleName: 运营 Agent
projectId: ""
actor: system.project-manager
defaultAgentId: agent.company.operations
status: ready
gapCount: 0
warningCount: 0
taskCount: 0
openTaskCount: 0
skillPackRef: docs/agent-team/operations-agent-role-and-skill-pack.md
localSkillRef: skills/operations-agent/SKILL.md
guideRef: docs/agent-team/company-agent-team-operating-guide.md
commonRulesRef: docs/agent-team/common-agent-operating-rules.md
qualityEvaluationTemplate: {"artifactTypes":["operations plan","content/campaign task list","feedback record","retrospective"],"requiredEvidence":["产品/发布目标","渠道或活动数据","用户反馈来源","执行记录"],"qualityChecks":["目标和指标明确","动作可追踪","数据和反馈有来源","复盘能产生下一步"],"failureRoutes":["反馈影响产品 -> 产品经理任务","经验可复用 -> 知识工程任务","质量或发布风险 -> 测试/PM","渠道执行阻塞 -> PM 协调"]}
followupTaskRefs: []
notificationRefs: []
---

## Summary

- role: 运营 Agent
- status: ready
- projectId: company
- defaultAgentId: agent.company.operations
- skillPackRef: docs/agent-team/operations-agent-role-and-skill-pack.md
- localSkillRef: skills/operations-agent/SKILL.md

## Gaps

- none

## Warnings

- none

## Responsibilities

- 运营计划
- 内容和渠道
- 活动执行
- 用户反馈
- 数据复盘
- 增长实验
- 运营知识沉淀

## Skills

- content-planning
- channel-operations
- campaign-planning
- community-feedback
- growth-experiment
- ops-retrospective
- sop-writing

## Workflow

- 接收运营目标
- 制定计划
- 拆内容和渠道任务
- 执行或调度执行
- 收集数据
- 复盘
- 沉淀知识并反馈产品

## Acceptance Checks

- 目标和指标清楚
- 执行动作可追踪
- 数据来源明确
- 复盘能生成下一步
- 用户反馈进入产品或知识闭环

## Quality Evaluation Template

### Artifact Types

- operations plan
- content/campaign task list
- feedback record
- retrospective

### Required Evidence

- 产品/发布目标
- 渠道或活动数据
- 用户反馈来源
- 执行记录

### Quality Checks

- 目标和指标明确
- 动作可追踪
- 数据和反馈有来源
- 复盘能产生下一步

### Failure Routes

- 反馈影响产品 -> 产品经理任务
- 经验可复用 -> 知识工程任务
- 质量或发布风险 -> 测试/PM
- 渠道执行阻塞 -> PM 协调

## Boundaries

- 不承担默认 SRE
- 不擅自承诺客户结果
- 不绕过品牌和合规要求
