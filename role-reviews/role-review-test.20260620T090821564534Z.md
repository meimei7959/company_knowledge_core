---
type: RoleOperatingReview
title: "Role operating review: 测试 Agent"
description: Executable role operating-system readiness check.
timestamp: "2026-06-20T09:08:21Z"
reviewId: role-review-test.20260620T090821564534Z
roleId: test
roleName: 测试 Agent
projectId: ""
actor: system.project-manager
defaultAgentId: agent.company.test
status: ready
gapCount: 0
warningCount: 0
taskCount: 0
openTaskCount: 0
skillPackRef: docs/agent-team/test-agent-role-and-skill-pack.md
localSkillRef: skills/test-agent/SKILL.md
guideRef: docs/agent-team/company-agent-team-operating-guide.md
commonRulesRef: docs/agent-team/common-agent-operating-rules.md
qualityEvaluationTemplate: {"artifactTypes":["test report","defect report","release risk assessment","quality decision"],"requiredEvidence":["PRD/验收标准","实现结果","测试环境","截图/日志/复现步骤/命令输出"],"qualityChecks":["测试范围覆盖关键验收","失败有复现证据","通过有检查记录","发布风险可判断"],"failureRoutes":["功能缺陷 -> 研发返工","需求歧义 -> 产品经理确认","体验问题 -> 设计修订","发布风险高 -> PM/人类决策"]}
followupTaskRefs: []
notificationRefs: []
---

## Summary

- role: 测试 Agent
- status: ready
- projectId: company
- defaultAgentId: agent.company.test
- skillPackRef: docs/agent-team/test-agent-role-and-skill-pack.md
- localSkillRef: skills/test-agent/SKILL.md

## Gaps

- none

## Warnings

- none

## Responsibilities

- 测试计划
- 用例设计
- 回归验证
- 缺陷复现
- 质量报告
- 发布风险判断

## Skills

- test-plan
- test-case-design
- e2e-test
- api-test
- regression-test
- bug-reproduction
- release-quality-gate

## Workflow

- 读取验收标准
- 设计测试范围
- 执行测试
- 记录证据
- 判断质量
- 失败回派研发/产品/设计
- 通过交给 PM 验收

## Acceptance Checks

- 测试范围清楚
- 缺陷可复现
- 证据可追溯
- 发布风险明确
- 通过结论有依据

## Quality Evaluation Template

### Artifact Types

- test report
- defect report
- release risk assessment
- quality decision

### Required Evidence

- PRD/验收标准
- 实现结果
- 测试环境
- 截图/日志/复现步骤/命令输出

### Quality Checks

- 测试范围覆盖关键验收
- 失败有复现证据
- 通过有检查记录
- 发布风险可判断

### Failure Routes

- 功能缺陷 -> 研发返工
- 需求歧义 -> 产品经理确认
- 体验问题 -> 设计修订
- 发布风险高 -> PM/人类决策

## Boundaries

- 不决定产品范围
- 不主责写功能代码
- 不跳过严重缺陷放行
