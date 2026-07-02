---
type: AuditLog
title: PicPeek official download source
description: Recorded the PicPeek official download site in Agent rules and the ToolAsset registry.
timestamp: "2026-07-02T08:03:08Z"
auditId: audit.20260702T080308Z
actor: agent.codex
action: toolasset.picpeek-download-source
targetRef: tools/tool.picpeek.md
status: done
evidenceRefs:
  - AGENTS.md
  - docs/agent-team/company-agent-constitution.md
  - docs/agent-team/agent-task-runtime-contract.md
  - docs/memory/project-memory.md
  - tools/tool.picpeek.md
  - tools/index.md
policyResult: human_requested_tool_registry_update
---

# Audit

Human owner specified the PicPeek official download site:

- `https://picpeek.zknowai.com/`

The rule now tells Agents to use PicPeek first for explicit image view/open requests, tell the user if PicPeek is unavailable, then fall back to system Preview or a browser.
