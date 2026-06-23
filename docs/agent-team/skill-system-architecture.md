# Agent Skill System Architecture

## Purpose

This document separates Agent roles from executable skills.

- Role: who owns work, where boundaries are, and what quality bar applies.
- Skill: how to complete one repeatable task with inputs, workflow, outputs, validation, and failure routing.
- Tool or script: deterministic execution helper used by a skill.

## Rules

1. Role documents must live in `agents/` or `docs/agent-team/`.
2. Production skills must live in `skills/<skill-id>/SKILL.md`.
3. A `skills/<skill-id>/SKILL.md` must not be only a job description.
4. Every production skill must be registered in `docs/agent-team/company-skill-registry.json`.
5. Role specs must bind roles to skills through `skillRefs`, not by pointing to a role-shaped `SKILL.md`.
6. `zhenzhi-knowledge skill validate` and `zhenzhi-knowledge validate` must pass before a role/skill change is complete.
7. Active company skills must satisfy `docs/agent-team/skill-delivery-standard.md`.
8. External skill repositories may be used as references only; reference records live in `docs/agent-team/skill-quality-sources.json`.

## Production Skill Shape

Each skill must include:

- Purpose
- Triggers
- Inputs
- Workflow
- Outputs
- Quality Gate
- Failure Routes

Long references, checklists, templates, or examples should be placed under `references/`. Deterministic work should be placed under `scripts/`.

## Mature Skill Package Shape

For this Agent Team, a production skill is not complete when it only has `SKILL.md`.

Every active company skill must include:

- `SKILL.md`: concise trigger, workflow, output, quality gate, and failure route.
- `references/delivery-card.md`: owner role, allowed roles, source references, done definition, and handoff rules.
- `templates/output-template.md`: output shape the Agent fills during execution.
- `examples/quality-example.md`: acceptable result shape and rejection examples.

Shared resources live under:

- `skills/_shared/skill-output-contract.md`
- `skills/_shared/references/mature-skill-package.md`
- `skills/_shared/templates/skill-output-template.md`
- `skills/_shared/examples/skill-quality-example.md`

High-risk or repeatable skills should add deterministic helpers under `scripts/` or rely on shared validation scripts.

## Validation Gates

The skill system is valid only when all checks pass:

```bash
python3 scripts/validate_skill_system.py
python3 -m zhenzhi_knowledge.cli skill validate
python3 -m zhenzhi_knowledge.cli validate
python3 -m unittest tests.test_skill_system
```

## Role To Skill Binding

`docs/agent-team/role-operating-specs.json` remains the source of truth for role responsibilities. Each role must include:

- `roleProfileRef`: role identity and responsibility card.
- `skillRegistryRef`: `docs/agent-team/company-skill-registry.json`.
- `skillRefs`: active skill IDs that the role can use.

## Change Control

Any role or skill change is an Agent Team operating-system change. It must update:

- the role spec when responsibilities or role boundaries change;
- the skill registry when callable capabilities change;
- the skill folder when execution method changes;
- the company Agent Team operating guide when the change affects how humans or Agents route work.
