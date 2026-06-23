---
type: ActorContext
title: 梅晓华
description: Runtime context for a human, Agent, Runner, bot, or local workbench actor.
timestamp: "2026-06-20T09:55:33Z"
actorId: 梅晓华
actorKey: actor-bfdc41fb01
actorType: human
displayName: 梅晓华
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
outputPreference: 中文；先结论后依据；重要节点通知项目经理或人类 owner
preferredTools: []
capabilities: []
source: ""
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

- outputPreference: 中文；先结论后依据；重要节点通知项目经理或人类 owner
- notificationPreferences:
  - feishu
