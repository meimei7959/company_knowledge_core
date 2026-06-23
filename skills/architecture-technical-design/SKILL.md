---
name: architecture-technical-design
description: Use when Architecture Agent must create an architecture or technical方案 before engineering work, especially for system boundaries, modules, interfaces, data models, security, reliability, performance, migration, rollback, or long-term evolution.
---

# Architecture Technical Design

## Purpose

Create an executable architecture and technical plan before Development Agent starts implementation.

## Triggers

- A task affects more than one module, service, repository, or data model.
- A task changes API contracts, permissions, persistence, deployment, reliability, or performance.
- Product, Design, Development, or Test Agent disagrees about the technical path.
- Existing code has accumulated structural debt and needs a bounded refactor plan.

## Inputs

- Project goal, PRD, acceptance criteria, and design handoff.
- Current repository structure, relevant modules, interfaces, schemas, and deployment constraints.
- Known risks, incidents, blockers, non-functional requirements, and forbidden changes.

## Workflow

1. State the problem, target outcome, and decision scope.
2. Map current architecture: modules, owners, data flow, external dependencies, and constraints.
3. Propose the target architecture with boundaries, interface/data contracts, non-functional requirements, rollout, rollback, and migration steps.
4. Compare alternatives and explain tradeoffs.
5. List implementation slices for Development Agent and verification focus for Test Agent.
6. Mark must-fix risks, accepted risks, and follow-up knowledge items.

## Outputs

- `TechnicalArchitecturePlan` with scope, current state, target state, module boundaries, interfaces, data model, security/reliability/performance notes, rollout, rollback, risks, and implementation slices.
- `ArchitectureDecision` for irreversible or cross-team decisions.
- Handoff summary for Development Agent and Test Agent.

## Quality Gate

- Development Agent can implement from the plan without inventing architecture.
- Interface and data contracts are explicit enough to test.
- Risks have owners, severity, mitigation, and acceptance status.
- The plan explains why rejected alternatives were not chosen.

## Failure Routes

- Missing product decision: return to Product Manager Agent.
- Missing interaction state: return to Design Agent.
- Missing repository or runtime evidence: ask Project Manager Agent to route discovery.
- Organization-level architecture change: escalate to Project Manager Agent for human decision.
