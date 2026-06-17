---
type: EvalCase
title: Codex start finish workflow eval
description: Evaluation case for the local Codex agent workflow.
timestamp: "2026-06-17T02:30:00Z"
evalId: eval.agent.codex.start-finish
owner: meimei
status: verified
targetRef: agents/agent.codex.local.md
expected: AgentRun
requires:
  - contextRefs
  - knowledgeUsed
  - sourceRef
---

## Input

Run a formal task through `zhenzhi-knowledge start` and `zhenzhi-knowledge finish`.

## Expected

The result includes an AgentRun with contextRefs and knowledgeUsed/sourceRef.
