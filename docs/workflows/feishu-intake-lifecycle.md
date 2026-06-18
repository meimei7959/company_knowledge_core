# Feishu Intake Lifecycle

## Purpose

Feishu/Lark groups can be used as customer communication channels for business domains such as GEO.

Core stores communication artifacts and source references. Business domains decide how to interpret and use them.

## Lifecycle

```txt
Feishu message or file
-> Interaction
-> SourceMaterial
-> Knowledge Extraction Agent
-> KnowledgeDraft candidates
-> Knowledge Review Agent
-> auto observed / clarification / conflict / human approval / reject
-> stored KnowledgeItem or approved publication
```

## Core Responsibilities

- Bind chat thread to project/customer.
- Preserve message/file source references.
- Store materials and interactions.
- Run Knowledge Extraction Agent to turn SourceMaterial into structured drafts.
- Run Knowledge Review Agent to classify the draft route.
- Store auto-approved observed/draft knowledge after machine review passes.
- Store missing fact records when clarification is required.
- Track confirmations.
- Audit durable writes.

## Agent Responsibilities

Knowledge Extraction Agent:

- reads the Feishu message, file, meeting note, or thread;
- creates SourceMaterial references;
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
