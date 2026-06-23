---
name: interaction-state-spec
description: Use when defining user flow, interaction states, empty/loading/error/permission states, and frontend handoff rules.
---

# Interaction State Spec

## Purpose

Make an interaction implementable by covering the full user journey and all required UI states.

## Triggers

- A feature needs frontend implementation.
- A form or card flow is unclear.
- A previous implementation missed states or user guidance.

## Inputs

- PRD or requirement brief.
- Current UI or desired workflow.
- Product constraints and design-system rules.

## Workflow

1. Map main path and alternate paths.
2. Define empty, loading, error, success, permission, disabled, and submitted states.
3. Define form fields, selectable options, validation, and disabled-card behavior.
4. Describe copy rules in human-readable Chinese.
5. Hand off to Development and Test Agents.

## Outputs

- Interaction spec.
- State matrix.
- Frontend handoff checklist.
- Testable acceptance items.

## Quality Gate

- No visible state is left implicit.
- Repeated submission and stale card behavior are covered.
- The output can be tested without asking the designer again.

## Failure Routes

- Product scope unclear: return to Product Manager Agent.
- Missing component constraints: request design-system reference.
- Technical limitation: ask Development Agent for feasibility.
