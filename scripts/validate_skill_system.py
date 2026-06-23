#!/usr/bin/env python3
"""Validate production Agent skill packages."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_REF = "docs/agent-team/company-skill-registry.json"
ROLE_SPECS_REF = "docs/agent-team/role-operating-specs.json"
STANDARD_REF = "docs/agent-team/skill-delivery-standard.md"
SOURCE_REF = "docs/agent-team/skill-quality-sources.json"
SHARED_CONTRACT_REF = "skills/_shared/skill-output-contract.md"
SHARED_RESOURCE_REFS = [
    "skills/_shared/references/mature-skill-package.md",
    "skills/_shared/templates/skill-output-template.md",
    "skills/_shared/examples/skill-quality-example.md",
]
REQUIRED_SECTIONS = {
    "Purpose",
    "Triggers",
    "Inputs",
    "Workflow",
    "Outputs",
    "Quality Gate",
    "Failure Routes",
}
REQUIRED_PACKAGE_FILES = [
    "references/delivery-card.md",
    "templates/output-template.md",
    "examples/quality-example.md",
]


def read_json(ref: str) -> dict:
    return json.loads((ROOT / ref).read_text(encoding="utf-8"))


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    raw = text[4:end]
    body = text[end + 5 :]
    data: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip().strip('"')
    return data, body


def sections(body: str) -> set[str]:
    found: set[str] = set()
    for line in body.splitlines():
        match = re.match(r"^##\s+(.+?)\s*$", line)
        if match:
            found.add(match.group(1).strip())
    return found


def validate() -> list[str]:
    problems: list[str] = []
    for ref in [REGISTRY_REF, ROLE_SPECS_REF, STANDARD_REF, SOURCE_REF, SHARED_CONTRACT_REF, *SHARED_RESOURCE_REFS]:
        if not (ROOT / ref).exists():
            problems.append(f"missing required skill system file: {ref}")

    if problems:
        return problems

    registry = read_json(REGISTRY_REF)
    role_specs = read_json(ROLE_SPECS_REF)
    source_registry = read_json(SOURCE_REF)
    if len(source_registry.get("sources", [])) < 3:
        problems.append(f"{SOURCE_REF}: must record at least 3 external mature skill references")

    roles = {str(role.get("roleId")): role for role in role_specs.get("roles", [])}
    registered = registry.get("skills")
    if not isinstance(registered, list) or not registered:
        return problems + [f"{REGISTRY_REF}: skills must be a non-empty list"]

    skill_ids = {str(skill.get("skillId")) for skill in registered}
    role_skill_refs = {
        str(skill_id)
        for role in roles.values()
        for skill_id in role.get("skillRefs", [])
    }

    for role_id, role in sorted(roles.items()):
        missing = [skill for skill in role.get("skillRefs", []) if skill not in skill_ids]
        if missing:
            problems.append(f"{ROLE_SPECS_REF}: {role_id} references unknown skills {missing}")
        if len(role.get("skillRefs", [])) < 2:
            problems.append(f"{ROLE_SPECS_REF}: {role_id} must have at least two production skills")

    for skill in registered:
        skill_id = str(skill.get("skillId") or "")
        skill_dir_ref = str(skill.get("skillDir") or "")
        if not skill_id or not skill_dir_ref:
            problems.append(f"{REGISTRY_REF}: skill missing skillId or skillDir")
            continue
        if skill_id not in role_skill_refs:
            problems.append(f"{REGISTRY_REF}: {skill_id} is not referenced by any role")
        if skill.get("status") != "active":
            continue
        skill_dir = ROOT / skill_dir_ref
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            problems.append(f"{skill_dir_ref}: missing SKILL.md")
            continue
        frontmatter, body = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
        if frontmatter.get("name") != skill_id:
            problems.append(f"{skill_dir_ref}/SKILL.md: frontmatter name must be {skill_id}")
        missing_sections = sorted(REQUIRED_SECTIONS - sections(body))
        if missing_sections:
            problems.append(f"{skill_dir_ref}/SKILL.md: missing sections {missing_sections}")
        if "职责" in body and "Workflow" not in sections(body):
            problems.append(f"{skill_dir_ref}/SKILL.md: looks like role description, not executable workflow")
        for rel_path in REQUIRED_PACKAGE_FILES:
            path = skill_dir / rel_path
            if not path.exists():
                problems.append(f"{skill_dir_ref}: missing packaged skill resource {rel_path}")
            elif len(path.read_text(encoding="utf-8").strip()) < 80:
                problems.append(f"{skill_dir_ref}/{rel_path}: resource is too thin")

    return problems


def main() -> int:
    problems = validate()
    if problems:
        for problem in problems:
            print(problem)
        return 1
    print("skill system valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

