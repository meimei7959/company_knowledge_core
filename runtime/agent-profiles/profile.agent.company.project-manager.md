---
type: AgentProfile
title: V1 Agent Profile - agent.company.project-manager
description: Executable V1 Agent profile for single-machine Agent Runtime.
timestamp: "2026-06-22T03:19:27Z"
profileId: profile.agent.company.project-manager
agentId: agent.company.project-manager
projectId: company-knowledge-core
status: active
sessionMode: independent
roleSoulRef: agents/agent.company.project-manager.md
responsibilities: []
allowedSkills:
  - orchestrator
  - local_router
modelPolicy: {"mode":"inherit","defaultModel":"project_default"}
permissions: {"fileRead":true,"fileWrite":"project_scope","codeWrite":false}
outputContract: markdown_structured
---

## Runtime Contract

- Load role rules before execution.
- Use only allowed skills and project-scoped files.
- Write TaskResult evidence before handoff.
