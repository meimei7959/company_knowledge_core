#!/usr/bin/env python3
"""Static quality gate for company_knowledge_core Development Agent work."""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
from pathlib import Path
from typing import Any


HIGH_RISK_FILES = {
    "zhenzhi_knowledge/core.py",
    "zhenzhi_knowledge/cli.py",
    "zhenzhi_knowledge/server.py",
    "zhenzhi_knowledge/feishu.py",
}

CODE_PREFIXES = ("zhenzhi_knowledge/", "scripts/")
TEST_PREFIXES = ("tests/",)
SKIP_PARTS = {".git", "node_modules", "__pycache__", ".venv", "dist", "build"}


def run_git(root: Path, args: list[str]) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def changed_files(root: Path, base: str) -> list[str]:
    tracked = run_git(root, ["diff", "--name-only", "--diff-filter=ACMRTUXB", base])
    staged = run_git(root, ["diff", "--cached", "--name-only", "--diff-filter=ACMRTUXB"])
    untracked = run_git(root, ["ls-files", "--others", "--exclude-standard"])
    return sorted(set(tracked + staged + untracked))


def selected_files(root: Path, paths: list[str], base: str) -> list[str]:
    if not paths:
        return changed_files(root, base)
    selected: list[str] = []
    for item in paths:
        path = (root / item).resolve()
        if path.is_dir():
            for child in path.rglob("*"):
                if child.is_file():
                    selected.append(str(child.relative_to(root)))
        elif path.exists():
            selected.append(str(path.relative_to(root)))
        else:
            selected.append(item)
    return sorted(set(selected))


def old_line_count(root: Path, base: str, rel: str) -> int | None:
    result = subprocess.run(
        ["git", "show", f"{base}:{rel}"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return len(result.stdout.splitlines())


def is_skipped(path: Path) -> bool:
    return any(part in SKIP_PARTS for part in path.parts)


def function_lengths(path: Path) -> list[tuple[str, int, int]]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    items: list[tuple[str, int, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            end = getattr(node, "end_lineno", None)
            if end:
                items.append((node.name, node.lineno, end - node.lineno + 1))
    return items


def add(findings: list[dict[str, Any]], severity: str, code: str, path: str, detail: str) -> None:
    findings.append({"severity": severity, "code": code, "path": path, "detail": detail})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--base", default="HEAD")
    parser.add_argument("--paths", nargs="*", default=[], help="Optional task-scoped files or directories to scan instead of the whole Git working tree.")
    parser.add_argument("--max-file-lines", type=int, default=1200)
    parser.add_argument("--warn-file-lines", type=int, default=800)
    parser.add_argument("--max-growth-lines", type=int, default=200)
    parser.add_argument("--max-function-lines", type=int, default=120)
    parser.add_argument("--architecture-review-ref", default="")
    parser.add_argument("--allow-missing-tests", default="")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    files = [f for f in selected_files(root, args.paths, args.base) if not is_skipped(Path(f))]
    findings: list[dict[str, Any]] = []

    code_changed = any(f.startswith(CODE_PREFIXES) and f.endswith((".py", ".js", ".ts", ".tsx")) for f in files)
    tests_changed = any(f.startswith(TEST_PREFIXES) for f in files)

    for rel in files:
        path = root / rel
        if not path.exists() or path.is_dir():
            continue

        if rel in HIGH_RISK_FILES and not args.architecture_review_ref:
            add(findings, "fail", "high_risk_file_requires_architecture_review", rel, "High-risk core file changed without architecture review ref.")

        if path.suffix == ".py":
            line_count = len(path.read_text(encoding="utf-8", errors="ignore").splitlines())
            previous = old_line_count(root, args.base, rel)
            growth = None if previous is None else line_count - previous
            if line_count > args.max_file_lines and (growth is None or growth > 0):
                add(findings, "fail", "large_file_over_limit", rel, f"{line_count} lines exceeds {args.max_file_lines}; move new logic behind a module boundary.")
            elif line_count > args.warn_file_lines:
                add(findings, "warn", "large_file_warning", rel, f"{line_count} lines exceeds warning threshold {args.warn_file_lines}.")
            if growth is not None and growth > args.max_growth_lines:
                add(findings, "fail", "large_growth", rel, f"File grew by {growth} lines; split or justify architecture boundary.")
            for name, lineno, length in function_lengths(path):
                if length > args.max_function_lines:
                    add(findings, "fail", "long_symbol", rel, f"{name} at line {lineno} is {length} lines; split or justify.")

    if code_changed and not tests_changed and not args.allow_missing_tests:
        add(findings, "fail", "tests_required", ".", "Code changed without tests/ update; pass --allow-missing-tests only with blocker reason.")

    has_fail = any(item["severity"] == "fail" for item in findings)
    has_warn = any(item["severity"] == "warn" for item in findings)
    verdict = "fail" if has_fail else "warn" if has_warn else "pass"
    payload = {
        "tool": "development_quality_gate",
        "verdict": verdict,
        "changedFiles": files,
        "architectureReviewRef": args.architecture_review_ref,
        "allowMissingTests": args.allow_missing_tests,
        "findings": findings,
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"development_quality_gate: {verdict}")
        print(f"changed files: {len(files)}")
        for item in findings:
            print(f"- {item['severity']}: {item['code']} {item['path']} - {item['detail']}")
    return 1 if has_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
