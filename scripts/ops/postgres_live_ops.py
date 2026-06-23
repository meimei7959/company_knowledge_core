#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from zhenzhi_knowledge.core import Bundle, KnowledgeError  # noqa: E402
from zhenzhi_knowledge.operational_store import (  # noqa: E402
    backup_readiness,
    ensure_operational_schema,
    live_readiness_report,
    operational_store_status,
    rollback_operational_schema,
    write_readiness_artifact,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Feishu/API/PostgreSQL live readiness and operational-store ops.")
    parser.add_argument("--root", default=str(REPO_ROOT), help="Company Knowledge Core bundle root.")
    sub = parser.add_subparsers(dest="command", required=True)

    readiness = sub.add_parser("readiness", help="Validate Feishu/API/PostgreSQL live environment and write evidence artifact.")
    readiness.add_argument("--check-feishu-api", action="store_true", help="Call Feishu token API from this network.")
    readiness.add_argument("--migrate", action="store_true", help="Apply operational schema before readiness status.")

    sub.add_parser("migrate", help="Apply additive operational-store schema.")
    sub.add_parser("status", help="Show operational-store schema/table status.")
    sub.add_parser("backup-readiness", help="Check backup/pg_dump evidence refs are present.")

    rollback = sub.add_parser("rollback", help="Rollback operational-store migration in cloned/restored DB.")
    rollback.add_argument("--to", required=True, help="Rollback target. Only 'base' is supported.")
    rollback.add_argument("--allow-destructive", action="store_true", help="Required; use only after backup/clone verification.")

    args = parser.parse_args(argv)
    bundle = Bundle(Path(args.root).resolve())

    try:
        if args.command == "readiness":
            report = live_readiness_report(check_feishu_api=args.check_feishu_api, migrate=args.migrate)
            report["artifactRef"] = write_readiness_artifact(bundle, report)
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 0 if report["status"] == "ready" else 2
        if args.command == "migrate":
            print(json.dumps(ensure_operational_schema("scripts/ops/postgres_live_ops.py"), ensure_ascii=False, indent=2))
            return 0
        if args.command == "status":
            print(json.dumps(operational_store_status(), ensure_ascii=False, indent=2))
            return 0
        if args.command == "backup-readiness":
            report = backup_readiness()
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 0 if report["ready"] else 2
        if args.command == "rollback":
            print(json.dumps(rollback_operational_schema(args.to, args.allow_destructive), ensure_ascii=False, indent=2))
            return 0
    except KnowledgeError as exc:
        print(json.dumps({"ok": False, "error": str(exc), "nextAction": "Fix environment or run against cloned staging DB, then retry."}, ensure_ascii=False, indent=2))
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
