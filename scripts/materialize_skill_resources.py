#!/usr/bin/env python3
"""Create standard resource files for registered production skills."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs" / "agent-team" / "company-skill-registry.json"
ROLE_SPECS = ROOT / "docs" / "agent-team" / "role-operating-specs.json"


def write_if_changed(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return
    path.write_text(content, encoding="utf-8")


def main() -> int:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    roles = json.loads(ROLE_SPECS.read_text(encoding="utf-8")).get("roles", [])
    role_names = {role.get("roleId"): role.get("name") for role in roles}

    for skill in registry.get("skills", []):
        skill_id = str(skill["skillId"])
        skill_name = str(skill.get("name") or skill_id)
        skill_dir = ROOT / str(skill["skillDir"])
        owner_role = str(skill.get("ownerRole") or "")
        allowed_roles = [str(item) for item in skill.get("allowedRoles", [])]
        aliases = [str(item) for item in skill.get("aliases", [])]
        owner_name = role_names.get(owner_role, owner_role)
        allowed_names = [role_names.get(role, role) for role in allowed_roles]

        delivery = f"""# {skill_name} Delivery Card

## Skill ID

`{skill_id}`

## Owner Role

{owner_name} (`{owner_role}`)

## Allowed Roles

{", ".join(allowed_names)}

## Source References

- Company standard: `docs/agent-team/skill-delivery-standard.md`
- Shared contract: `skills/_shared/skill-output-contract.md`
- Mature package reference: `skills/_shared/references/mature-skill-package.md`
- External references registry: `docs/agent-team/skill-quality-sources.json`

## Job To Be Done

Use this skill when the Agent must perform `{skill_name}` as a repeatable production capability, not as a generic role discussion.

## Trigger Aliases

{chr(10).join(f"- `{alias}`" for alias in aliases) if aliases else "- none"}

## Execution Contract

1. Confirm the task input matches this skill.
2. Load the shared output contract.
3. Produce the skill output using `templates/output-template.md`.
4. Attach evidence and quality gate result.
5. If blocked, return the failure route with owner and next action.

## Done Means

- Output matches this skill's `SKILL.md`.
- Output follows the shared contract.
- Quality gate is explicit.
- Result can be handed to the next Agent without re-explaining context.
"""
        template = f"""# {skill_name} Output Template

## Request

- Project:
- Task ID:
- Requested by:
- Skill: `{skill_id}`

## Inputs

- Primary input:
- Context refs:
- Constraints:

## Result

-

## Evidence

-

## Quality Gate

- Completeness:
- Correctness:
- Risk:
- Handoff readiness:

## Next Step

-
"""
        example = f"""# {skill_name} Quality Example

## Acceptable Result Shape

The Agent uses `{skill_id}` only for tasks matching its triggers, names the input, produces a concrete artifact, includes evidence, runs the quality gate, and states the next handoff.

## Rejection Example

Reject or reroute when the task lacks required input, asks this skill to exceed its role boundary, contains secrets, or needs a different Agent.
"""
        write_if_changed(skill_dir / "references" / "delivery-card.md", delivery)
        write_if_changed(skill_dir / "templates" / "output-template.md", template)
        write_if_changed(skill_dir / "examples" / "quality-example.md", example)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

