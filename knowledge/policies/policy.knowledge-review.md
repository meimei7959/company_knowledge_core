---
type: Policy
title: Knowledge Review Agent Policy
description: Runtime policy for reviewing draft knowledge and routing approval.
timestamp: "2026-06-19T00:00:00Z"
policyId: policy.knowledge-review
agentId: agent.core.knowledge-review
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
  - review:write
  - audit:write
  - task:create
requiresApproval:
  - publish_verified
  - approve_policy
  - approve_tool
  - approve_permission
reviewer: meimei
reviewedAt: "2026-06-19T00:00:00Z"
---

## Notes

Knowledge Review Agent may evaluate and route reusable knowledge candidates.

It must not grant final approval for verified knowledge, active policy, approved tools, permissions, security changes, customer commitments, or cross-team standards.
