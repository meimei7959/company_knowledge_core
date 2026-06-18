---
type: AuditLog
title: audit.20260618T020125Z
timestamp: 2026-06-18T02:01:25Z
auditId: audit.20260618T020125Z
actor: codex
action: governance.knowledge_review_agent.define
targetRef: docs/workflows/knowledge-lifecycle.md
before: human-review-or-direct-draft
after: knowledge-review-agent-gate-before-index-approval-promotion
policyResult: user_requested
---

## Details

Defined the Knowledge Review Agent gate for all reusable knowledge write candidates.

The gate checks structure, source evidence, category, confidence, sensitivity, duplicates, conflicts, reviewer readability, and the correct review path before knowledge is indexed, submitted for approval, or promoted.

The Knowledge Review Agent may write ReviewRecord, IssueRecord, and approval documents, but cannot approve its own output as verified, approved, active, policy, permission, security, or cross-team standard knowledge.
