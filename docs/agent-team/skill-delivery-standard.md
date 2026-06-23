# Skill Delivery Standard

## Purpose

This standard defines when an Agent skill is considered production-ready.

A skill is not a role card. A role owns work. A skill is a reusable capability that tells an Agent how to complete one repeatable task with inputs, workflow, outputs, quality gates, and failure routes.

## Reference Sources

The skill system uses external repositories only as design references. Do not copy third-party skill content into company skills.

Reference source records live in `docs/agent-team/skill-quality-sources.json`.

## Delivery Levels

### Level 1: Instruction Skill

Use for low-risk reasoning work.

Required:

- `SKILL.md`
- required production sections
- role binding in `docs/agent-team/company-skill-registry.json`

### Level 2: Packaged Skill

Use for company production skills.

Required:

- `SKILL.md`
- `references/delivery-card.md`
- `templates/output-template.md`
- `examples/quality-example.md`
- shared output contract reference: `skills/_shared/skill-output-contract.md`

### Level 3: Executable Skill

Use for high-risk, repeatable, integration, governance, or verification work.

Required:

- all Level 2 files
- deterministic validation or helper script, either skill-local under `scripts/` or shared under `skills/_shared/scripts/`
- executable test or example that proves the skill can be checked

## Production Skill Required Sections

Every production `SKILL.md` must include these sections:

- `Purpose`
- `Triggers`
- `Inputs`
- `Workflow`
- `Outputs`
- `Quality Gate`
- `Failure Routes`

## Mature Skill Package Rules

Every active company skill must:

1. be registered in `docs/agent-team/company-skill-registry.json`;
2. be referenced by at least one role in `docs/agent-team/role-operating-specs.json`;
3. declare allowed roles;
4. include a real workflow, not only job responsibilities;
5. include output shape and quality gate;
6. include failure routes;
7. include packaged resources under `references/`, `templates/`, and `examples/`;
8. be validated by `zhenzhi-knowledge skill validate`;
9. be covered by `tests/test_skill_system.py`.

## Acceptance Standard

A skill change is complete only when all commands pass:

```bash
python3 scripts/validate_skill_system.py
python3 -m zhenzhi_knowledge.cli skill validate
python3 -m zhenzhi_knowledge.cli validate
python3 -m unittest tests.test_skill_system
```

## Change Control

When a skill changes, update:

- the skill package;
- the skill registry if callable scope changes;
- role specs if role-to-skill binding changes;
- operating guide if routing or handoff changes;
- Feishu guide if user-facing behavior changes.

