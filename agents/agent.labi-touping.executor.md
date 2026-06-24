---
type: Agent
title: 蜡笔投屏 执行 Agent
description: 通过本地 Runner 驱动 Codex、Claude 或本地工具完成项目初始化和执行任务。
timestamp: "2026-06-24T11:40:05Z"
agentId: agent.labi-touping.executor
owner: 梅晓华
aiTool: codex
status: draft
riskLevel: L1
allowedProjects:
  - labi-touping
allowedTools: []
allowedKnowledgeScopes:
  - company
  - engineering
humanApprovalRequired: true
updatedAt: "2026-06-24T11:40:05Z"
requiredCapabilities:
  - codex
  - git
  - local_execution
  - project_initialization
---

## Purpose

通过本地 Runner 驱动 Codex、Claude 或本地工具完成项目初始化和执行任务。

## Operating Notes

- Must run start before formal work.
- Must run finish after formal work.
