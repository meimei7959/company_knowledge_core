# Feishu Intake Lifecycle

## Purpose

Feishu/Lark groups can be used as customer communication channels, team source-material intake channels, and learning-material intake channels.

Core stores communication artifacts and source references. Business domains decide how to interpret and use domain material. Learning material is extracted into reusable learning notes, skill notes, patterns, or issue notes before Agent use.

## Lifecycle

```txt
Feishu message, URL, article, video, audio, image, document, package, or file
-> Interaction
-> SourceMaterial
-> material-specific extractor
-> Knowledge Extraction Agent
-> KnowledgeDraft candidates
-> Knowledge Review Agent
-> auto observed / clarification / conflict / human approval / reject
-> stored KnowledgeItem or approved publication
```

## Core Responsibilities

- Bind chat thread to project/customer.
- Preserve message/file source references.
- Preserve URL, file token, storageRef, contentHash, materialType, license, and sensitivity metadata.
- Store materials and interactions.
- Route material to the right extractor: web/article, public account, transcript, OCR, document parser, or package registrar.
- Run Knowledge Extraction Agent to turn SourceMaterial into structured drafts.
- Run Knowledge Review Agent to classify the draft route.
- Store auto-approved observed/draft knowledge after machine review passes.
- Store missing fact records when clarification is required.
- Track confirmations.
- Audit durable writes.

## Agent Responsibilities

Knowledge Extraction Agent:

- reads the Feishu message, URL, file, meeting note, learning material, or thread;
- creates SourceMaterial references;
- uses the material-specific extraction output instead of treating raw files as knowledge;
- extracts structured KnowledgeDraft candidates;
- preserves project, submitter, sourceRef, confidence, sensitivity, and evidence;
- does not decide whether the draft can be published.

Knowledge Review Agent:

- reviews the extracted draft, not the raw chat as the primary object;
- checks classification, required fields, source evidence, duplicate/conflict risk, sensitivity, and readability;
- decides whether the draft is `auto_observed`, `clarification_required`, `conflict_required`, `human_approval_required`, or `reject`;
- writes ReviewRecord and AuditLog;
- creates the approval document only when human approval is required.

## Domain Responsibilities

- Decide what information is missing.
- Prepare customer-facing questions.
- Generate domain deliverables after enough context exists.

## Learning Material Intake

Supported examples:

- `学习资料：<URL 或文章内容>`
- `公众号文章：<链接、转发正文、截图或 PDF>`
- `视频资料：<链接或上传文件>`
- `安装包：<项目ID 或用途>\n<文件、版本、来源、许可、安装说明>`

Default behavior:

- The robot stores the original reference as SourceMaterial.
- The extractor creates a human-readable summary, key points, applicable skills, risk/limitations, and source metadata.
- The Knowledge Extraction Agent turns useful parts into `learning_note`, `skill_note`, `pattern`, or `issue` drafts.
- Low-risk learning notes can be machine-reviewed into `observed/draft` directly.
- Policy changes, verified knowledge, customer commitments, sensitive material, unclear license, high-risk package use, or cross-team rules require human approval.

The robot should not reply with long explanations. It should tell the submitter only: material recognized, missing fields if any, draft route, and whether approval is needed.
