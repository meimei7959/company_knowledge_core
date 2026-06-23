---
type: RoleOperatingReview
title: "Role operating review: 知识工程 Agent"
description: Executable role operating-system readiness check.
timestamp: "2026-06-20T08:18:55Z"
reviewId: role-review-knowledge-engineering.20260620T081855225973Z
roleId: knowledge-engineering
roleName: 知识工程 Agent
projectId: ""
actor: system.project-manager
defaultAgentId: agent.company-knowledge-core.knowledge-engineering
status: ready
gapCount: 0
warningCount: 0
taskCount: 0
openTaskCount: 0
skillPackRef: docs/agent-team/knowledge-engineering-agent-skill-pack.md
guideRef: docs/agent-team/company-agent-team-operating-guide.md
commonRulesRef: docs/agent-team/common-agent-operating-rules.md
followupTaskRefs: []
notificationRefs: []
---

## Summary

- role: 知识工程 Agent
- status: ready
- projectId: company
- defaultAgentId: agent.company-knowledge-core.knowledge-engineering
- skillPackRef: docs/agent-team/knowledge-engineering-agent-skill-pack.md

## Gaps

- none

## Warnings

- none

## Responsibilities

- 资料登记
- 原文解析
- 证据包
- 知识结构化
- 审核治理
- 发布索引
- 修订归档

## Skills

- source-classification
- source-reader
- evidence-packet
- knowledge-extraction
- citation-builder
- review-routing
- publish-index

## Workflow

- 登记 SourceMaterial
- 解析原文
- 构建证据包
- 生成结构化草稿
- 质量评价
- Review
- 必要时审批
- 发布索引
- 通知提交人

## Acceptance Checks

- 原文可追溯
- 每个结论有证据
- 状态和范围正确
- 审核/审批/发布/索引闭环
- 不把 draft 当 verified

## Boundaries

- 不替查知识做快速问答
- 不无证据总结
- 不自批 verified
- 不存储 secret
