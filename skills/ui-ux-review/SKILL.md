---
name: ui-ux-review
description: Use when reviewing UI/UX quality, information hierarchy, conversion path, accessibility, and design-system consistency.
---

# UI/UX Review

## Purpose

Find product-facing UX issues and produce concrete fixes.

## Triggers

- A screenshot, Figma design, page, or feature flow needs design review.
- A frontend result looks hard to understand or use.
- A card, form, menu, dashboard, or workflow needs simplification.

## Inputs

- Screenshot, Figma link, running page, PRD, or interaction description.
- Target user and task.
- Existing design-system constraints.

## Workflow

1. Identify the user's primary task on the screen.
2. Check hierarchy, readability, affordance, state, empty/error/loading coverage, and accessibility.
3. Rank issues by impact.
4. Suggest concrete layout, copy, component, or flow changes.
5. Hand off implementation notes to Design or Development Agent.

## Outputs

- UX issue list with severity.
- Recommended design changes.
- Accessibility and responsive risks.
- Handoff checklist.

## Quality Gate

- Every issue explains user impact.
- Suggestions are concrete enough for implementation.
- Review covers desktop and mobile when relevant.

## Failure Routes

- Missing target user/task: ask Product Manager Agent.
- Missing visual evidence: request screenshot or Figma context.
- Engineering feasibility unclear: route to Development Agent.
