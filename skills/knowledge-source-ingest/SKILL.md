---
name: knowledge-source-ingest
description: Use when receiving raw material, links, documents, meeting notes, screenshots, or transcripts for knowledge processing.
---

# Knowledge Source Ingest

## Purpose

Register raw material safely and prepare it for structured knowledge extraction.

## Triggers

- User submits material to record knowledge.
- CLI receives local notes, docs, links, screenshots, or transcripts.
- A project task needs source evidence.

## Inputs

- Raw content or source link.
- Project or public knowledge scope.
- Submitter and sensitivity context.

## Workflow

1. Classify source type and scope.
2. Store or reference original material as SourceMaterial.
3. Preserve source path, URL, timestamp, and submitter.
4. Create a knowledge processing task when extraction is needed.
5. Route to Knowledge Review Gate before reusable publication.

## Outputs

- SourceMaterial.
- KnowledgeTask or ProjectTask.
- Evidence packet.

## Quality Gate

- Original source is traceable.
- Scope and sensitivity are explicit.
- No raw material is treated as reusable knowledge directly.

## Failure Routes

- Unreadable source: create blocked TaskResult with reason.
- Missing scope: ask submitter to choose project or public knowledge.
- Sensitive content: require review before indexing.
