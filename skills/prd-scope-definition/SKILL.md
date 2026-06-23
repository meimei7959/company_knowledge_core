---
name: prd-scope-definition
description: Use when writing PRD scope, non-goals, workflows, metrics, and acceptance criteria for a product requirement.
---

# PRD Scope Definition

## Purpose

Produce a PRD-ready scope that design, development, and testing can execute.

## Triggers

- A clarified requirement needs PRD structure.
- A feature needs acceptance criteria and release boundaries.
- Scope creep or ambiguous non-goals appear.

## Inputs

- Requirement brief.
- User scenarios.
- Evidence, constraints, and project goals.

## Workflow

1. Define positioning, users, workflow, and business value.
2. Run `prd-high-quality-generation` when the output is a product plan, PRD, test case set, acceptance checklist, or development handoff package.
3. State scope and non-goals.
4. Write acceptance criteria that can be tested.
5. Identify metrics and risks.
6. Route to design, development, and test tasks.

## Outputs

- PRD or product requirement card.
- Evidence pack and internal adversarial review result when `prd-high-quality-generation` applies.
- Acceptance criteria.
- Test cases or test directions when a complete PRD delivery package is requested.
- Metrics and risks.
- Handoff suggestions.

## Quality Gate

- Scope and non-goals are explicit.
- Acceptance criteria are observable.
- Evidence, assumptions, and decisions are separated.
- The PRD does not confuse product requirements with engineering tasks, implementation steps, database fields, or API details.
- Complete PRD delivery includes test cases, acceptance checklist, and development handoff.

## Failure Routes

- Requirement unclear: return to requirement clarification.
- Major product decision: request human approval.
- Acceptance criteria not testable: repair PRD scope.
