---
type: AuditLog
title: audit.20260618T033337Z
timestamp: 2026-06-18T03:33:37Z
auditId: audit.20260618T033337Z
actor: codex
action: knowledge.learning_material_governance.add
targetRef: docs/strategy/zhenzhi-ai-native-knowledge-system.md
before: learning-materials-not-explicitly-modeled
after: learning-materials-enter-as-SourceMaterial-and-extract-to-agent-readable-notes
policyResult: governance_alignment
---

## Details

Added learning material intake rules for web articles, public account articles, video/audio, documents, images, screenshots, packages, binaries, model files, and datasets. Raw material remains referenced by sourceRef/storageRef/contentHash. Reusable output must pass material extraction and Knowledge Review Agent routing before entering searchable knowledge.
