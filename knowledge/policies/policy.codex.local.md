---
type: Policy
title: Codex Local Policy
description: Policy for agent.codex.local.
timestamp: "2026-06-16T14:48:16Z"
policyId: policy.codex.local
agentId: agent.codex.local
owner: meimei
status: active
scope: company
allowedProjects:
  - company-knowledge-core
allowedKnowledgeScopes:
  - engineering
  - company
allowedToolRiskLevels:
  - L1
  - L2
writePermissions:
  - knowledge:draft
  - toolAsset:draft
requiresApproval:
  - publish_verified
  - call_L3_tool
  - access_customer_confidential
reviewer: meimei
reviewedAt: "2026-06-16T14:48:26Z"
---

## Notes

Policy changes require review before active use.
