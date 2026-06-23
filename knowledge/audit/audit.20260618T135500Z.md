---
type: AuditLog
title: audit.20260618T135500Z
timestamp: "2026-06-18T13:55:00Z"
auditId: audit.20260618T135500Z
actor: codex
action: knowledge.update
targetRef: knowledge/engineering/feishu-card-json-v2-form-pattern.md
before: "card JSON 2.0 sending pattern only"
after: "added card.action.trigger callback response boundary and diagnostics pattern"
policyResult: knowledge_review_required
---

## Details

Updated the Feishu card engineering lesson after a live `code: 200530` card submit failure.

The documented root cause is protocol boundary leakage: callback HTTP responses must return only official Feishu fields such as `toast` and `card`, while internal debug fields must be stored separately.

The fix also adds `.zhenzhi/feishu-card-events/` diagnostics so future card click failures can be traced from server evidence rather than chat screenshots only.
