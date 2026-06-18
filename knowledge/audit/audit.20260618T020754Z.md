---
type: AuditLog
title: audit.20260618T020754Z
timestamp: 2026-06-18T02:07:54Z
auditId: audit.20260618T020754Z
actor: codex
action: workflow.agent_cli_intake_chain.define
targetRef: docs/workflows/knowledge-lifecycle.md
before: feishu-intake-path-only
after: feishu-and-agent-cli-intake-paths-share-extraction-review-governance
policyResult: user_requested
---

## Details

Added the second intake path for Codex, Claude, Antigravity, cloud Agents, and other local Agents pushing content through `zhenzhi-knowledge` CLI.

CLI-pushed content must first be recorded as AgentRun, SourceMaterial, ToolUpdate, or ProjectUpdate input, then converted by the Knowledge Extraction Agent into structured drafts, and finally classified by the Knowledge Review Agent for direct observed storage, clarification, conflict handling, rejection, or human approval.
