---
type: RoleOperatingReview
title: "Role operating review: 知识工程 Agent"
description: Executable role operating-system readiness check.
timestamp: "2026-06-20T09:08:21Z"
reviewId: role-review-knowledge-engineering.20260620T090821679380Z
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
localSkillRef: skills/knowledge-engineering-agent/SKILL.md
guideRef: docs/agent-team/company-agent-team-operating-guide.md
commonRulesRef: docs/agent-team/common-agent-operating-rules.md
qualityEvaluationTemplate: {"artifactTypes":["SourceMaterial","evidence packet","KnowledgeItem draft","ReviewRecord","publish/index result"],"requiredEvidence":["原始资料引用","内容 hash 或稳定位置","证据片段","审核记录"],"qualityChecks":["结论有证据","范围/状态/置信度正确","敏感和冲突检查完成","发布和索引有审计"],"failureRoutes":["原文不可读 -> blocked TaskResult","证据不足 -> 修复/重试","冲突风险 -> ConflictRecord","需要 verified/policy -> 人类审批"]}
followupTaskRefs: []
notificationRefs: []
---

## Summary

- role: 知识工程 Agent
- status: ready
- projectId: company
- defaultAgentId: agent.company-knowledge-core.knowledge-engineering
- skillPackRef: docs/agent-team/knowledge-engineering-agent-skill-pack.md
- localSkillRef: skills/knowledge-engineering-agent/SKILL.md

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

## Quality Evaluation Template

### Artifact Types

- SourceMaterial
- evidence packet
- KnowledgeItem draft
- ReviewRecord
- publish/index result

### Required Evidence

- 原始资料引用
- 内容 hash 或稳定位置
- 证据片段
- 审核记录

### Quality Checks

- 结论有证据
- 范围/状态/置信度正确
- 敏感和冲突检查完成
- 发布和索引有审计

### Failure Routes

- 原文不可读 -> blocked TaskResult
- 证据不足 -> 修复/重试
- 冲突风险 -> ConflictRecord
- 需要 verified/policy -> 人类审批

## Boundaries

- 不替查知识做快速问答
- 不无证据总结
- 不自批 verified
- 不存储 secret
