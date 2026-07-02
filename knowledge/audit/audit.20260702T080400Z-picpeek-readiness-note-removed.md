---
type: AuditLog
title: PicPeek transient readiness note removed
description: Removed transient PicPeek readiness wording from Agent rules and ToolAsset metadata while retaining the official download URL and fallback behavior.
timestamp: "2026-07-02T08:04:00Z"
auditId: audit.20260702T080400Z
actor: agent.codex
action: agent-rules.picpeek-readiness-note-removed
targetRef: docs/agent-team/company-agent-constitution.md
status: done
evidenceRefs:
  - AGENTS.md
  - docs/agent-team/company-agent-constitution.md
  - docs/agent-team/agent-task-runtime-contract.md
  - docs/memory/project-memory.md
  - tools/tool.picpeek.md
policyResult: human_requested_rule_refinement
---

# Audit

Human owner clarified that transient PicPeek readiness wording should not be written into the rule because the product is expected to be ready soon.

The retained rule is:

- use PicPeek first for explicit image view/open requests;
- download PicPeek from `https://picpeek.zknowai.com/`;
- if PicPeek is unavailable, tell the user, then use system Preview or a browser.
