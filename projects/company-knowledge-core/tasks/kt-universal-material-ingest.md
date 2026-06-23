---
type: ProjectTask
title: Universal material ingest pipeline
description: Build a general intake path for URLs, Feishu docs, meeting notes, files, screenshots, media, packages, datasets, and other source materials.
timestamp: "2026-06-19T02:10:00Z"
taskId: TASK-UNIVERSAL-MATERIAL-INGEST
taskType: knowledge_engineering
projectId: company-knowledge-core
requester: meimei
assignee: agent.company-knowledge-core.knowledge-engineering
requiredCapabilities:
  - material_ingest
  - source_material
  - knowledge_capture
  - review_gate
requiredAgents:
  - agent.company-knowledge-core.knowledge-engineering
  - agent.company-knowledge-core.executor
preferredRunner:
  - runner.meimei-mac-codex
assignedRunner: []
executorAgent: []
leaseOwner: []
leaseExpiresAt: []
status: done
priority: high
dueAt: []
sourceMaterialRefs:
  - docs/workflows/feishu-intake-lifecycle.md
  - docs/workflows/knowledge-lifecycle.md
  - docs/tools/core-tool-contract.md
expectedOutput:
  - material ingest command or server function
  - SourceMaterial records for supported material types
  - KnowledgeTask creation for parse/structure work
  - evidence-backed draft KnowledgeItem output path
  - Feishu short-command support for common material types
resultRef: task-results/tr-task-universal-material-ingest.md
notificationRefs:
  - notifications/notification.20260619T025613787383Z.md
auditRefs: []
completedAt: "2026-06-19T02:56:13Z"
updatedAt: "2026-06-21T07:18:05Z"
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"knowledge_engineering","category":"project","stage":"","requiredCapabilities":["knowledge_engineering","material_ingest","source_material","knowledge_capture","review_gate"],"requiredTools":[],"sourceRefs":["docs/workflows/feishu-intake-lifecycle.md","docs/workflows/knowledge-lifecycle.md","docs/tools/core-tool-contract.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
---

## Goal

Turn "帮我把这份资料保存起来" into a reliable knowledge engineering workflow.

The system should preserve the original source, classify material type, store metadata, create a processing task, and only create reusable knowledge after structured extraction and review.

## Scope

Supported first-stage material types:

- URL or public article.
- Feishu doc or meeting note.
- Uploaded document.
- Screenshot or image.
- Video/audio summary reference.
- Installation package, binary, model file, or dataset metadata.
- Freeform pasted text.

The first stage may store metadata and source references without fully parsing every binary/media type.

## Definition of Done

- A single intake interface can register all supported material types as `SourceMaterial`.
- SourceMaterial preserves sourceRef, materialType, submitter, project, title, sensitivity, license/copyright hint, content hash when available, and extraction status.
- Long or heavy materials create a `KnowledgeTask` instead of being summarized directly by the Feishu router.
- Generated drafts include summary, structured knowledge, evidence refs, scope, confidence, limits, original source path, and review status.
- Binary/package/model/dataset inputs are not placed into RAG body by default; only metadata, hash, source, risk, owner, and verification notes are stored.
- Screenshot/image inputs record OCR or visual-summary method and confidence when used.
- Feishu supports short commands for common cases such as "记录资料", "记录会议纪要", "记录学习资料", and "记录安装包".
- Review gate prevents unreviewed material summaries from becoming verified knowledge.

## Test Plan

- Unit test SourceMaterial creation for pasted text, URL, Feishu doc, screenshot/image metadata, and binary/package metadata.
- Unit test KnowledgeTask creation includes project context, source refs, expected output, and assignee.
- Unit test draft KnowledgeItem contains evidence refs and original source path.
- Unit test Feishu intake command routes to material capture, not direct verified knowledge.
- Run `python3 -m unittest tests.test_cli`.
- Run `python3 -m zhenzhi_knowledge --root /Users/meimei/Documents/company_knowledge_core validate`.

## Self-Verification Checklist

- [ ] General material intake exists.
- [ ] SourceMaterial metadata complete.
- [ ] Heavy work becomes KnowledgeTask.
- [ ] Draft knowledge is evidence-backed.
- [ ] Binary/media handling avoids raw dump.
- [ ] Feishu short commands covered.
- [ ] Review gate enforced.
