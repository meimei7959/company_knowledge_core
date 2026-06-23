---
name: project-task-decomposition
description: Use when converting a project goal into executable tasks, role handoffs, acceptance checks, and clear next actions.
---

# Project Task Decomposition

## Purpose

Turn a project goal into tasks that can be claimed by the right Agent or Runner.

## Triggers

- A new project is created or migrated.
- A project manager must split work across product, design, development, test, operations, or knowledge roles.
- A vague request needs executable task cards.

## Inputs

- Project goal and current project record.
- Known constraints, repository, approval state, and Runner state.
- Existing tasks and TaskResult evidence.

## Workflow

1. Identify the desired outcome and non-goals.
2. Decide which role owns each part of the work.
3. Create one task per independently verifiable result.
4. Add input references, output contract, acceptance checks, and notification target.
5. Mark human acceptance only when decision or release approval is needed.

## Outputs

- ProjectTask list.
- Handoff order.
- Acceptance policy per task.
- Risks and missing context.

## Quality Gate

- Every task has one owner role, one assignee or routing rule, and observable acceptance criteria.
- No task depends on hidden chat context only.
- Cross-role handoff has clear input and output refs.

## Failure Routes

- Missing goal: return to requester for clarification.
- Missing owner: escalate to Project Manager Agent.
- Missing Runner: set `manual-runner-required` or equivalent manual handoff state.
