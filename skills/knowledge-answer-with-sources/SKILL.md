---
name: knowledge-answer-with-sources
description: Use when answering user or Agent questions from approved knowledge with citations, confidence, and missing-evidence notes.
---

# Knowledge Answer With Sources

## Purpose

Answer from reusable knowledge and show where the answer came from.

## Triggers

- User asks a knowledge question.
- Agent needs project or company knowledge.
- Search results need summarization with source references.

## Inputs

- User question.
- Optional project name.
- Search results and KnowledgeItem metadata.

## Workflow

1. Resolve project name when provided.
2. Search verified/approved knowledge first.
3. Use observed/draft only as clearly labeled reference.
4. Summarize answer in Chinese.
5. Include source refs, confidence, and missing-evidence note.

## Outputs

- Answer.
- Source list.
- Confidence and scope.
- Follow-up route if answer is missing.

## Quality Gate

- No unsupported conclusion is presented as fact.
- Sources are visible and readable.
- Project and public knowledge are not mixed silently.

## Failure Routes

- No reliable answer: route to retrieval gap.
- Ambiguous project: ask clarification.
- Draft-only evidence: label as not official.
