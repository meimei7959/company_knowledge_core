#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.agent_feedback import parse_system_issue_args, report_system_issue, system_issue_main  # noqa: E402


def parse_args():
    return parse_system_issue_args(prog="report_system_issue.py")


def main() -> int:
    return system_issue_main(prog="report_system_issue.py")


if __name__ == "__main__":
    raise SystemExit(main())
