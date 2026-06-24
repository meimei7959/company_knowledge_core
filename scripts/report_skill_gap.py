#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.agent_feedback import parse_skill_gap_args, report_skill_gap, skill_gap_main  # noqa: E402


def parse_args():
    return parse_skill_gap_args(prog="report_skill_gap.py")


def main() -> int:
    return skill_gap_main(prog="report_skill_gap.py")


if __name__ == "__main__":
    raise SystemExit(main())
