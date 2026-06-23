---
type: RoleOperatingReview
title: "Role operating review: 查知识 Agent"
description: Executable role operating-system readiness check.
timestamp: "2026-06-20T09:08:21Z"
reviewId: role-review-knowledge-query.20260620T090821737238Z
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
localSkillRef: skills/knowledge-query-agent/SKILL.md
guideRef: docs/agent-team/company-agent-team-operating-guide.md
commonRulesRef: docs/agent-team/common-agent-operating-rules.md
qualityEvaluationTemplate: {"artifactTypes":["knowledge answer","citation list","query log","gap/escalation note"],"requiredEvidence":["已发布知识检索结果","来源路径","项目/权限范围","查询日志"],"qualityChecks":["答案只基于允许状态知识","引用清楚","草稿和正式结论分离","找不到时说明缺口"],"failureRoutes":["无答案 -> 知识工程任务建议","项目范围不明 -> 澄清","权限风险 -> 拒答/升级","索引失败 -> 知识工程 ops 修复"]}
followupTaskRefs: []
notificationRefs: []
---

## Summary

- role: 查知识 Agent
- status: ready
- projectId: company
- defaultAgentId: agent.company.knowledge-query
- skillPackRef: docs/agent-team/knowledge-query-agent-role.md
- localSkillRef: skills/knowledge-query-agent/SKILL.md

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

## Quality Evaluation Template

### Artifact Types

- knowledge answer
- citation list
- query log
- gap/escalation note

### Required Evidence

- 已发布知识检索结果
- 来源路径
- 项目/权限范围
- 查询日志

### Quality Checks

- 答案只基于允许状态知识
- 引用清楚
- 草稿和正式结论分离
- 找不到时说明缺口

### Failure Routes

- 无答案 -> 知识工程任务建议
- 项目范围不明 -> 澄清
- 权限风险 -> 拒答/升级
- 索引失败 -> 知识工程 ops 修复

## Boundaries

- 不处理原始资料
- 不发布知识
- 不审批知识
- 不要求用户记项目 ID
