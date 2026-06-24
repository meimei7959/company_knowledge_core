---
type: Project
title: Company Knowledge Core
description: Project context for Company Knowledge Core.
timestamp: "2026-06-16T14:43:11Z"
projectId: company-knowledge-core
owner: meimei
humanOwner: 梅晓华
status: draft
scope: project
members:
  - meimei
relatedRepos:
  - /Users/meimei/Documents/company_knowledge_core
workspaceRef: /Users/meimei/Documents/company_knowledge_core
workspaceConfirmation: confirmed
relatedAgents:
  - agent.codex.local
  - agent.antigravity.local
  - agent.company.project-manager
  - agent.company.knowledge-query
  - agent.company.product-manager
  - agent.company.design
  - agent.company.development
  - agent.company.test
  - agent.company.operations
relatedTools:
  - tool.zhenzhi-knowledge
updatedAt: "2026-06-24T03:32:46Z"
lastProjectManagerReviewRef: projects/company-knowledge-core/pm-reviews/pm-review.20260624T033246176974Z.md
health: blocked
---

## Goal

Build Zhenzhi's AI-native central processor: Agent Hub entry, scheduler, and knowledge engineering foundation, so distributed Agent Workbench runners can share project context, tasks, reusable tools, experience, decisions, review state, permissions, and audit evidence.

## Scope

Project/task orchestration, Feishu Agent Hub intake, Agent and Runner registry, task lifecycle, Agent Ring integration contract, project context sync, SourceMaterial and KnowledgeItem review pipeline, ToolAsset registry, review/audit, retrieval, evaluation, stale detection, backup, and API/Gateway prototype.

## Current Focus

Continue from initialized central processor to the next acceptance phase:

1. verify the real Feishu production closed loop;
2. prepare the Agent Workbench integration package;
3. build universal material ingest;
4. implement knowledge graph phase one.

These four tasks are the current验收 scope. They should be completed with evidence before the next human acceptance review.

Active task list: [projects/company-knowledge-core/tasks/index.md](tasks/index.md).
