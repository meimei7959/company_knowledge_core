---
type: ToolAsset
title: PicPeek
description: Local image viewing tool used as the preferred surface when users ask Agents to view or open images.
resource: https://picpeek.zknowai.com/
timestamp: "2026-07-02T08:03:08Z"
toolId: tool.picpeek
owner: shenyingjun5
repoRef: /Users/meimei/Documents/picpeek/01_源码镜像/picpeek
entrypoint: PicPeek local app
version: ""
status: testing
scope: company
riskLevel: L1
invocationPolicy: user_requested_default_image_viewer
requiresApproval: []
executionMode: local_app
downloadUrl: https://picpeek.zknowai.com/
allowedAgents: []
allowedProjects: []
secretsRequired: []
capabilities:
  - image_view
  - local_image_open
  - dual_folder_image_compare
sourceRefs:
  - user-provided official site: https://picpeek.zknowai.com/
knownIssues:
  - If PicPeek is unavailable, Agents must tell the user before falling back to system Preview or a browser.
lastVerifiedAt: ""
---

# PicPeek

## Purpose

PicPeek is the preferred local image opening surface for Agent workflows when the user asks to view or open an image.

## Invocation Policy

- Agents must try PicPeek first for explicit image view/open requests.
- If PicPeek is unavailable, Agents must tell the user before using system Preview or a browser.
- PicPeek availability failures should be reported to the user before fallback, not treated as silent task completion.

## Source

Official download site provided by the human owner:

- `https://picpeek.zknowai.com/`
