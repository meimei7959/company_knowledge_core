---
type: AuditLog
title: audit.20260618T020420Z
timestamp: 2026-06-18T02:04:20Z
auditId: audit.20260618T020420Z
actor: codex
action: governance.review_agent_classification.define
targetRef: docs/workflows/knowledge-lifecycle.md
before: review-agent-quality-gate-only
after: review-agent-classifies-auto-observed-human-approval-clarification-conflict-reject
policyResult: user_requested
---

## Details

Clarified that the Knowledge Review Agent must classify every write candidate before deciding the route.

Low-risk lessons, pitfalls, issue reviews, integration notes, and debugging conclusions can be stored directly as observed/draft after the review agent passes them. Human approval remains required for verified knowledge, approved tools, policies, workflows, iron rules, permissions, security, approval, identity, notification, customer commitments, and cross-team standards.
