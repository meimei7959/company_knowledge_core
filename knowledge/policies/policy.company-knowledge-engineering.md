---
type: Policy
title: Company Knowledge Engineering Agent Policy
description: Runtime write policy for source-material extraction and draft knowledge writeback.
timestamp: "2026-06-19T00:00:00Z"
policyId: policy.company-knowledge-engineering
agentId: agent.company-knowledge-core.knowledge-engineering
owner: meimei
status: active
scope: company
allowedProjects:
  - company-knowledge-core
allowedKnowledgeScopes:
  - company
  - engineering
  - governance
allowedToolRiskLevels:
  - L1
  - L2
writePermissions:
  - knowledge:draft
  - taskResult:write
  - audit:write
requiresApproval:
  - publish_verified
  - call_L3_tool
  - access_customer_confidential
reviewer: meimei
reviewedAt: "2026-06-19T00:00:00Z"
---

## Notes

Knowledge Engineering Agent may extract SourceMaterial into evidence-backed TaskResult records and KnowledgeItem drafts.

It must not approve, verify, publish, or index its own reusable output. Drafts must enter Knowledge Review Agent gate.
