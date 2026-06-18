---
type: AuditLog
title: audit.20260618T020549Z
timestamp: 2026-06-18T02:05:49Z
auditId: audit.20260618T020549Z
actor: codex
action: workflow.feishu_intake_two_agent_chain.define
targetRef: docs/workflows/feishu-intake-lifecycle.md
before: feishu-source-to-knowledge-candidate
after: feishu-source-to-extraction-agent-to-review-agent-to-route
policyResult: user_requested
---

## Details

Clarified the direct Feishu intake chain: the bot records Interaction and SourceMaterial, the Knowledge Extraction Agent converts material into structured drafts, and the Knowledge Review Agent reviews those drafts to decide direct observed storage, clarification, conflict handling, rejection, or human approval.
