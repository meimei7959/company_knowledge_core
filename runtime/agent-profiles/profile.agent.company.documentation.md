---
type: AgentProfile
title: V1 Agent Profile - agent.company.documentation
description: Executable V1 Agent profile for single-machine Agent Runtime.
timestamp: "2026-06-22T03:19:27Z"
profileId: profile.agent.company.documentation
agentId: agent.company.documentation
projectId: company-knowledge-core
status: active
sessionMode: independent
roleSoulRef: ""
responsibilities: []
allowedSkills:
  - documentation
modelPolicy: {"mode":"inherit","defaultModel":"project_default"}
permissions: {"fileRead":true,"fileWrite":"project_scope","codeWrite":false}
outputContract: markdown_structured
---

## Runtime Contract

- Load role rules before execution.
- Use only allowed skills and project-scoped files.
- Write TaskResult evidence before handoff.
