---
type: Agent
title: 桢知科技官网 执行 Agent
description: 通过本地 Runner 驱动 Codex、Claude 或本地工具完成项目初始化和执行任务。
timestamp: "2026-06-25T03:09:35Z"
agentId: agent.zknowai-official-website.executor
owner: 梅晓华
aiTool: codex
status: draft
riskLevel: L1
allowedProjects:
  - zknowai-official-website
allowedTools: []
allowedKnowledgeScopes:
  - company
  - engineering
humanApprovalRequired: true
updatedAt: "2026-06-25T03:09:35Z"
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
