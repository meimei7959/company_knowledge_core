---
name: requirement-clarification
description: Use when a product request is vague and needs users, scenarios, value, constraints, and open decisions clarified.
---

# Requirement Clarification

## Purpose

Convert vague intent into a clear product problem and decision-ready requirement.

## Triggers

- User says they want to build or change something but scope is unclear.
- Product direction, user group, or success criteria are missing.
- Evidence and assumptions are mixed together.

## Inputs

- User request.
- Project goal and constraints.
- Existing decisions, research, and source material.

## Workflow

1. Start from first principles: identify user, real problem, value, success metric, constraints, and unknowns before proposing a solution.
2. Separate facts, assumptions, and decisions.
3. Ask only the minimum blocking questions using a Socratic style: expose the highest-risk missing premise instead of asking a long survey.
4. Confirm product positioning, market positioning, business model, user role, scenario, success metric, and acceptance direction.
5. Propose default scope when risk is low, and mark every default as an assumption.
6. Hand off clarified requirement to `prd-high-quality-generation`, PRD, or project task creation.

## Outputs

- Requirement brief.
- Clarification questions.
- Assumption list.
- Recommended next step.

## Quality Gate

- The problem is clear before solution details.
- First-principles fields are explicit: user, problem, value, success metric.
- Socratic questions have challenged the highest-risk missing premise.
- Open questions are limited and actionable.
- Product positioning, market positioning, business model, scenario, and success metric are explicit or marked as blockers.
- Acceptance criteria can be derived from the result.

## Failure Routes

- Missing business owner: escalate to Project Manager Agent.
- Missing evidence: create research task.
- Conflicting goals: create decision request.
