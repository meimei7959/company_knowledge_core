---
type: ToolAsset
title: Knowledge Material Reader Toolkit
description: Reader toolkit registry for turning Feishu, file, web, media, image, and repository source materials into evidence packets.
resource: local-agent-skills
timestamp: "2026-06-19T08:15:00Z"
toolId: tool.knowledge-material-readers
owner: knowledge-core
repoRef: local-agent-skills
entrypoint: agent-workbench skill resolver
version: 0.1.0
status: testing
scope: company
riskLevel: L2
invocationPolicy: agent_policy_allowed
requiresApproval: []
executionMode: local_runner_required
allowedAgents:
  - agent.company-knowledge-core.knowledge-engineering
allowedProjects:
  - company-knowledge-core
secretsRequired: []
capabilities:
  - material_classification
  - source_extraction
  - feishu_doc_read
  - feishu_minutes_read
  - feishu_drive_read
  - pdf_read
  - office_document_read
  - spreadsheet_read
  - web_article_read
  - public_account_fallback
  - video_transcript_read
  - image_ocr
  - repo_doc_read
  - evidence_packet_build
inputSchemaRef: docs/agent-team/knowledge-engineering-agent-skill-pack.md#required-skill-groups
outputSchemaRef: docs/agent-team/knowledge-engineering-agent-skill-pack.md#evidence-packet-builder
knownIssues:
  - Some web, public account, and video sources may require user-provided export, transcript, or permission.
  - This ToolAsset is a registry contract; concrete execution happens in the local Agent Runner or Codex skill environment.
lastVerifiedAt: ""
---

# Knowledge Material Reader Toolkit

## Purpose

This ToolAsset registers the standard reader toolkit for the Knowledge Engineering Agent.

It is a capability contract, not a single binary. Agent Ring or a manual Codex session resolves the actual local reader skill based on the source type.

## Included Reader Families

- Feishu/Lark document readers.
- Feishu/Lark minutes and meeting readers.
- Feishu drive file readers.
- PDF and OCR readers.
- Office document readers.
- Spreadsheet readers.
- Web article readers.
- Public account fallback readers.
- Video/audio transcript readers.
- Image/screenshot OCR readers.
- Repository documentation readers.
- Package/binary/model/dataset registrars.

## Input Schema

Required input:

- `taskId`
- `sourceMaterialRef`
- `sourceRef` or `storageRef`
- `materialType` when known
- `projectId`
- `requestedOutput`

Optional input:

- `license`
- `sensitivity`
- `expectedReader`
- `fallbackAllowed`
- `scopeNote`

## Output Schema

The reader toolkit must return or write:

- source metadata;
- raw snapshot reference or storage reference;
- content hash;
- evidence packet;
- extraction confidence;
- extraction warnings;
- next action when blocked.

## Policy

- Default execution is allowed only for registered Knowledge Engineering Agent tasks.
- High-risk external side effects are not allowed through this ToolAsset.
- Login-required sources must use local user/workbench permission and must not store credentials in the knowledge core.
- Copyrighted source text must not be copied into reusable knowledge beyond short evidence snippets.
- Results are not reusable knowledge until Knowledge Review Agent gate passes.

## Reference

- Skill pack: `docs/agent-team/knowledge-engineering-agent-skill-pack.md`
- Lifecycle: `docs/workflows/knowledge-lifecycle.md`
