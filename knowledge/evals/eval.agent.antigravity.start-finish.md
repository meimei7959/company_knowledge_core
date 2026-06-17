---
type: EvalCase
title: Antigravity start finish workflow eval
description: Evaluation case for the local Antigravity agent workflow.
timestamp: "2026-06-17T02:30:00Z"
evalId: eval.agent.antigravity.start-finish
owner: meimei
status: verified
targetRef: agents/agent.antigravity.local.md
expected: AgentRun
---

## Input

Run a formal task through `zhenzhi-knowledge start` and `zhenzhi-knowledge finish`.

## Expected

The result includes an AgentRun with contextRefs and knowledgeUsed/sourceRef.
