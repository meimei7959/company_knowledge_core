---
name: retrieval-gap-routing
description: Use when knowledge search cannot answer reliably and the system must create a follow-up task or ask for missing context.
---

# Retrieval Gap Routing

## Purpose

Turn "no answer" into a closed-loop knowledge improvement path.

## Triggers

- Search returns no verified answer.
- Results are draft-only or conflict.
- User asks a question requiring missing project context.

## Inputs

- Question.
- Search results and statuses.
- Project or public scope.

## Workflow

1. Explain what is missing.
2. Decide whether to ask clarification or create a knowledge task.
3. Preserve the original question as source context.
4. Notify Knowledge Engineering Agent or Project Manager Agent.
5. Return a clear interim answer to the user.

## Outputs

- Missing-evidence note.
- KnowledgeTask or clarification prompt.
- Notification target.

## Quality Gate

- User understands why no answer was given.
- Follow-up has owner and task id when needed.
- Draft material is not upgraded silently.

## Failure Routes

- User scope unclear: ask one clarification.
- Knowledge task cannot be created: escalate to Project Manager Agent.
- Conflicting evidence: create ConflictRecord.
