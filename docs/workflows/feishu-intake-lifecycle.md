# Feishu Intake Lifecycle

## Purpose

Feishu/Lark groups can be used as customer communication channels for business domains such as GEO.

Core stores communication artifacts and source references. Business domains decide how to interpret and use them.

## Lifecycle

```txt
Chat message or file
-> Interaction
-> SourceMaterial
-> KnowledgeItem candidates
-> MissingFact queue
-> Customer confirmation
-> Confirmed KnowledgeItem
```

## Core Responsibilities

- Bind chat thread to project/customer.
- Preserve message/file source references.
- Store materials and interactions.
- Store missing fact records.
- Track confirmations.
- Audit durable writes.

## Domain Responsibilities

- Decide what information is missing.
- Prepare customer-facing questions.
- Generate domain deliverables after enough context exists.
