---
type: AuditLog
title: PicPeek image opening iron rule
description: Added a global Agent iron rule that routes explicit image view/open requests to PicPeek first, records the official download site, and allows user-visible fallback to system Preview or a browser.
timestamp: "2026-07-02T07:59:53Z"
auditId: audit.20260702T075953Z
actor: agent.codex
action: agent-rules.picpeek-image-open
targetRef: docs/agent-team/company-agent-constitution.md
status: done
evidenceRefs:
  - AGENTS.md
  - docs/agent-team/company-agent-constitution.md
  - docs/agent-team/agent-task-runtime-contract.md
  - docs/memory/project-memory.md
  - tools/tool.picpeek.md
  - tools/index.md
policyResult: human_requested_iron_rule
---

# Audit

Human owner requested a cross-Agent iron rule: when a user asks to view or open an image, including "看图", "打开图片", "把图打开给我看一下", or equivalent wording, Agents must use PicPeek first.

Human owner also specified that PicPeek is downloaded from `https://picpeek.zknowai.com/`.

If PicPeek is unavailable, Agents must tell the user, then open the image with system Preview or a browser.

Rule propagated to the global repository instructions, company Agent constitution, task runtime contract, project memory, and ToolAsset registry so formal Agent tasks and local Agent sessions inherit the same behavior.
