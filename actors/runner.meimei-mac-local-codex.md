---
type: ActorContext
title: 梅晓华 Mac 本地 Codex 临时 Runner
description: Runtime context for a human, Agent, Runner, bot, or local workbench actor.
timestamp: "2026-06-20T09:55:33Z"
actorId: runner.meimei-mac-local-codex
actorKey: runner.meimei-mac-local-codex
actorType: runner
displayName: 梅晓华 Mac 本地 Codex 临时 Runner
owner: system.scheduler
status: active
defaultProject: company-knowledge-core
currentProject: company-knowledge-core
allowedProjects:
  - company-knowledge-core
allowedKnowledgeScopes:
  - company
  - engineering
notificationPreferences:
  - feishu
outputPreference: 使用本地 Codex 手动接管任务；完成后写回 TaskResult、测试结果和后续动作
preferredTools:
  - agent.codex.local
  - agent.company.project-manager
  - agent.company-knowledge-core.knowledge-engineering
  - agent.company.knowledge-query
  - agent.company.product-manager
  - agent.company.design
  - agent.company.development
  - agent.company.test
  - agent.company.operations
capabilities:
  - codex
  - knowledge_capture
  - project_management
  - product_management
  - design
  - development
  - test
  - operations
  - knowledge_query
source: runners/runner.meimei-mac-local-codex.md
memoryPolicy: {"companyMemory":"reviewed reusable knowledge, shared skills, shared evals, and operating guide updates","projectMemory":"project goals, tasks, decisions, source materials, task results, and project-scoped lessons","taskMemory":"current task input, evidence, output, quality evaluation, and handoff state","actorContext":"identity, permission, preference, current work context, and feedback; not reusable truth by itself","promotionRule":"actor feedback may create improvement proposals; reusable conclusions require review before becoming project or company memory"}
lastSeenAt: "2026-06-20T09:55:33Z"
---

## Purpose

ActorContext tells the scheduler who is acting, what they can access, how they prefer to receive output, and which memory layers should be loaded. It is runtime context, not reusable knowledge.

## Memory Layers

- companyMemory: reviewed reusable knowledge, shared skills, shared evals, and operating guide updates
- projectMemory: project goals, tasks, decisions, source materials, task results, and project-scoped lessons
- taskMemory: current task input, evidence, output, quality evaluation, and handoff state
- actorContext: identity, permission, preference, current work context, and feedback; not reusable truth by itself
- promotionRule: actor feedback may create improvement proposals; reusable conclusions require review before becoming project or company memory

## Preferences

- outputPreference: 使用本地 Codex 手动接管任务；完成后写回 TaskResult、测试结果和后续动作
- notificationPreferences:
  - feishu
