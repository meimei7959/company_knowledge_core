---
type: RoleOperatingReview
title: "Role operating review: 查知识 Agent"
description: Executable role operating-system readiness check.
timestamp: "2026-06-20T08:18:55Z"
reviewId: role-review-knowledge-query.20260620T081855309701Z
roleId: knowledge-query
roleName: 查知识 Agent
projectId: ""
actor: system.project-manager
defaultAgentId: agent.company.knowledge-query
status: ready
gapCount: 0
warningCount: 0
taskCount: 0
openTaskCount: 0
skillPackRef: docs/agent-team/knowledge-query-agent-role.md
guideRef: docs/agent-team/company-agent-team-operating-guide.md
commonRulesRef: docs/agent-team/common-agent-operating-rules.md
followupTaskRefs: []
notificationRefs: []
---

## Summary

- role: 查知识 Agent
- status: ready
- projectId: company
- defaultAgentId: agent.company.knowledge-query
- skillPackRef: docs/agent-team/knowledge-query-agent-role.md

## Gaps

- none

## Warnings

- none

## Responsibilities

- 意图识别
- 项目范围识别
- 已发布知识检索
- 来源引用
- 置信度说明
- 知识缺口识别

## Skills

- intent-routing
- project-resolution
- retrieval-search
- citation-rendering
- confidence-labeling
- no-answer-escalation

## Workflow

- 接收问题
- 解析范围
- 检索已发布知识
- 过滤权限和状态
- 生成带来源答案
- 记录查询日志和审计
- 必要时升级知识工程

## Acceptance Checks

- 答案有来源
- 不编造
- 草稿和正式结论分开
- 找不到时说明缺口
- 不把查询派给本地 Runner

## Boundaries

- 不处理原始资料
- 不发布知识
- 不审批知识
- 不要求用户记项目 ID
