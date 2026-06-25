#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


AGENT_ID_RE = re.compile(r"^agent\.[a-z0-9][a-z0-9.-]*$")
FIELD_RE = re.compile(r"^\s*(?:[-*]\s*)?`?(primaryAgent|upstreamAgent|downstreamAgent|handoffChain|escalationAgents)`?\s*[:：]\s*(.+?)\s*$")
SKIP_DIRS = {".git", "node_modules", ".venv", "__pycache__", "01_源码镜像", "source", "dist", "build"}


def candidate_files(workspace: Path) -> list[Path]:
    files: list[Path] = []
    for path in workspace.rglob("*.md"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        lower_name = path.name.lower()
        if "outcome" in lower_name or lower_name.startswith("os-"):
            files.append(path)
    return sorted(files)


def normalize_values(raw: str) -> list[str]:
    value = raw.strip().strip("`")
    if not value or value.lower() in {"none", "null", "无", "空", "留空"}:
        return []
    if "->" in value or "→" in value:
        return [value]
    if "," in value or "，" in value or "/" in value:
        return re.split(r"\s*[,，/]\s*", value)
    return [value]


def looks_like_comment(raw: str) -> bool:
    return any(marker in raw for marker in ["结构化列表", "每项", "后续", "只有风险", "当前阶段"])


def validate_file(path: Path, workspace: Path) -> list[str]:
    problems: list[str] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    for lineno, line in enumerate(lines, start=1):
        match = FIELD_RE.match(line)
        if not match:
            continue
        field, raw = match.groups()
        if field == "handoffChain" and looks_like_comment(raw):
            problems.append(f"{path.relative_to(workspace)}:{lineno}: handoffChain must be a structured list, not an explanatory sentence")
            continue
        for value in normalize_values(raw):
            value = value.strip().strip("`")
            if not value:
                continue
            if field in {"primaryAgent", "upstreamAgent", "downstreamAgent"} and len(normalize_values(raw)) > 1:
                problems.append(f"{path.relative_to(workspace)}:{lineno}: {field} must contain exactly one canonical Agent id")
                break
            if not AGENT_ID_RE.fullmatch(value):
                problems.append(f"{path.relative_to(workspace)}:{lineno}: {field} must use canonical Agent id list items, got {value!r}")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate local project OutcomeSlice Agent routing fields.")
    parser.add_argument("--workspace", default=".", help="Project workspace to scan.")
    args = parser.parse_args(argv)
    workspace = Path(args.workspace).expanduser().resolve()
    if not workspace.exists():
        print(f"workspace not found: {workspace}", file=sys.stderr)
        return 2
    problems: list[str] = []
    for path in candidate_files(workspace):
        problems.extend(validate_file(path, workspace))
    if problems:
        print("workspace OutcomeSlice validation failed:")
        for problem in problems:
            print(f"- {problem}")
        return 1
    print("workspace OutcomeSlice validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
