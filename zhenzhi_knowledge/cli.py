from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .core import (
    Bundle,
    KnowledgeError,
    default_config,
    find_bundle_root,
    finish_task,
    git,
    install_connector,
    load_config,
    make_agent,
    make_project,
    make_tool,
    invoke_tool,
    rebuild_index,
    rebuild_retrieval_index,
    create_conflict,
    create_metrics_report,
    create_eval_case,
    create_backup,
    detect_stale,
    bulk_review,
    export_api_snapshot,
    gateway_context,
    list_review_queue,
    review_path,
    search_index,
    make_policy,
    run_eval_case,
    restore_backup,
    resolve_conflict,
    search_audit_logs,
    search_retrieval,
    save_config,
    start_task,
    validate_bundle,
)
from .server import serve


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="zhenzhi-knowledge")
    parser.add_argument("--root", default=None, help="knowledge bundle root")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init")
    p_init.add_argument("--user-id", default=os.environ.get("USER", "unknown"))
    p_init.add_argument("--ai-tool", default="codex")
    p_init.add_argument("--agent-id", default=None)
    p_init.add_argument("--remote", default="")

    p_install = sub.add_parser("install")
    p_install.add_argument("--user-id", default=os.environ.get("USER", "unknown"))
    p_install.add_argument("--ai-tool", default="codex")
    p_install.add_argument("--agent-id", default=None)
    p_install.add_argument("--remote", default="")
    p_install.add_argument("--default-project", default="")
    p_install.add_argument("--register-agent", action="store_true")
    p_install.add_argument("--agent-name", default="")
    p_install.add_argument("--purpose", default="local AI development")
    p_install.add_argument("--no-rebuild-index", action="store_true")

    sub.add_parser("status")
    p_profile = sub.add_parser("profile")
    p_profile_sub = p_profile.add_subparsers(dest="profile_command", required=True)
    p_profile_use = p_profile_sub.add_parser("use")
    p_profile_use.add_argument("name")

    p_sync = sub.add_parser("sync")
    p_sync_sub = p_sync.add_subparsers(dest="sync_command", required=True)
    p_sync_sub.add_parser("pull")
    p_sync_sub.add_parser("push")

    p_agent = sub.add_parser("agent")
    p_agent_sub = p_agent.add_subparsers(dest="agent_command", required=True)
    p_agent_register = p_agent_sub.add_parser("register")
    p_agent_register.add_argument("--agent-id", required=True)
    p_agent_register.add_argument("--name", required=True)
    p_agent_register.add_argument("--owner", required=True)
    p_agent_register.add_argument("--tool", default="codex")
    p_agent_register.add_argument("--purpose", required=True)

    p_project = sub.add_parser("project")
    p_project_sub = p_project.add_subparsers(dest="project_command", required=True)
    p_project_register = p_project_sub.add_parser("register")
    p_project_register.add_argument("--project-id", required=True)
    p_project_register.add_argument("--name", required=True)
    p_project_register.add_argument("--owner", required=True)

    p_tool = sub.add_parser("tool")
    p_tool_sub = p_tool.add_subparsers(dest="tool_command", required=True)
    p_tool_register = p_tool_sub.add_parser("register")
    p_tool_register.add_argument("--tool-id", required=True)
    p_tool_register.add_argument("--name", required=True)
    p_tool_register.add_argument("--owner", required=True)
    p_tool_register.add_argument("--repo", required=True)
    p_tool_register.add_argument("--entrypoint", required=True)
    p_tool_register.add_argument("--risk", default="L1")
    p_tool_invoke = p_tool_sub.add_parser("invoke")
    p_tool_invoke.add_argument("--tool-id", required=True)
    p_tool_invoke.add_argument("--project", required=True)
    p_tool_invoke.add_argument("--agent", required=True)
    p_tool_invoke.add_argument("--input", required=True)
    p_tool_invoke.add_argument("--execute", action="store_true")

    p_policy = sub.add_parser("policy")
    p_policy_sub = p_policy.add_subparsers(dest="policy_command", required=True)
    p_policy_register = p_policy_sub.add_parser("register")
    p_policy_register.add_argument("--policy-id", required=True)
    p_policy_register.add_argument("--title", required=True)
    p_policy_register.add_argument("--agent-id", required=True)
    p_policy_register.add_argument("--owner", required=True)
    p_policy_register.add_argument("--allow-project", action="append", default=[])
    p_policy_register.add_argument("--allow-scope", action="append", default=[])
    p_policy_register.add_argument("--allow-risk", action="append", default=[])

    p_start = sub.add_parser("start")
    p_start.add_argument("--project", required=True)
    p_start.add_argument("--agent", required=True)
    p_start.add_argument("--task", required=True)
    p_start.add_argument("--retrieval-limit", type=int, default=5)

    p_finish = sub.add_parser("finish")
    p_finish.add_argument("--project", required=True)
    p_finish.add_argument("--agent", required=True)
    p_finish.add_argument("--summary", required=True)
    p_finish.add_argument("--result", default="completed")
    p_finish.add_argument("--no-reusable-lesson", action="store_true")
    p_finish.add_argument("--no-tool-update", action="store_true")

    p_review = sub.add_parser("review")
    p_review_sub = p_review.add_subparsers(dest="review_command", required=True)
    p_review_list = p_review_sub.add_parser("list")
    p_review_list.add_argument("--type", dest="object_type", default="")
    p_review_update = p_review_sub.add_parser("update")
    p_review_update.add_argument("--target", required=True)
    p_review_update.add_argument("--status", required=True)
    p_review_update.add_argument("--reviewer", required=True)
    p_review_bulk = p_review_sub.add_parser("bulk")
    p_review_bulk.add_argument("--type", dest="object_type", default="")
    p_review_bulk.add_argument("--from-status", default="")
    p_review_bulk.add_argument("--to-status", required=True)
    p_review_bulk.add_argument("--reviewer", required=True)
    p_review_bulk.add_argument("--limit", type=int, default=0)

    p_index = sub.add_parser("index")
    p_index_sub = p_index.add_subparsers(dest="index_command", required=True)
    p_index_sub.add_parser("rebuild")
    p_index_search = p_index_sub.add_parser("search")
    p_index_search.add_argument("--type", dest="object_type", default="")
    p_index_search.add_argument("--status", default="")
    p_index_search.add_argument("--project-id", default="")
    p_index_search.add_argument("--agent-id", default="")
    p_index_search.add_argument("--tool-id", default="")
    p_index_search.add_argument("--risk-level", default="")
    p_index_search.add_argument("--text", default="")

    p_rag = sub.add_parser("rag")
    p_rag_sub = p_rag.add_subparsers(dest="rag_command", required=True)
    p_rag_sub.add_parser("rebuild")
    p_rag_search = p_rag_sub.add_parser("search")
    p_rag_search.add_argument("--query", required=True)
    p_rag_search.add_argument("--project-id", default="")
    p_rag_search.add_argument("--scope", action="append", default=[])
    p_rag_search.add_argument("--limit", type=int, default=5)

    p_conflict = sub.add_parser("conflict")
    p_conflict_sub = p_conflict.add_subparsers(dest="conflict_command", required=True)
    p_conflict_create = p_conflict_sub.add_parser("create")
    p_conflict_create.add_argument("--type", dest="conflict_type", required=True)
    p_conflict_create.add_argument("--owner", required=True)
    p_conflict_create.add_argument("--summary", required=True)
    p_conflict_create.add_argument("--affected", action="append", default=[])
    p_conflict_resolve = p_conflict_sub.add_parser("resolve")
    p_conflict_resolve.add_argument("--target", required=True)
    p_conflict_resolve.add_argument("--owner", required=True)
    p_conflict_resolve.add_argument("--resolution", required=True)

    p_audit = sub.add_parser("audit")
    p_audit_sub = p_audit.add_subparsers(dest="audit_command", required=True)
    p_audit_search = p_audit_sub.add_parser("search")
    p_audit_search.add_argument("--project-id", default="")
    p_audit_search.add_argument("--agent-id", default="")
    p_audit_search.add_argument("--tool-id", default="")
    p_audit_search.add_argument("--target", default="")

    p_metrics = sub.add_parser("metrics")
    p_metrics_sub = p_metrics.add_subparsers(dest="metrics_command", required=True)
    p_metrics_report = p_metrics_sub.add_parser("report")
    p_metrics_report.add_argument("--owner", default="system")

    p_stale = sub.add_parser("stale")
    p_stale_sub = p_stale.add_subparsers(dest="stale_command", required=True)
    p_stale_scan = p_stale_sub.add_parser("scan")
    p_stale_scan.add_argument("--owner", default="system")

    p_eval = sub.add_parser("eval")
    p_eval_sub = p_eval.add_subparsers(dest="eval_command", required=True)
    p_eval_case = p_eval_sub.add_parser("case")
    p_eval_case_sub = p_eval_case.add_subparsers(dest="eval_case_command", required=True)
    p_eval_case_create = p_eval_case_sub.add_parser("create")
    p_eval_case_create.add_argument("--eval-id", required=True)
    p_eval_case_create.add_argument("--title", required=True)
    p_eval_case_create.add_argument("--owner", required=True)
    p_eval_case_create.add_argument("--target-ref", required=True)
    p_eval_case_create.add_argument("--input", required=True)
    p_eval_case_create.add_argument("--expected", required=True)
    p_eval_run = p_eval_sub.add_parser("run")
    p_eval_run.add_argument("--eval-id", required=True)
    p_eval_run.add_argument("--actual", required=True)
    p_eval_run.add_argument("--runner", required=True)

    p_backup = sub.add_parser("backup")
    p_backup_sub = p_backup.add_subparsers(dest="backup_command", required=True)
    p_backup_create = p_backup_sub.add_parser("create")
    p_backup_create.add_argument("--output", default="")
    p_backup_restore = p_backup_sub.add_parser("restore")
    p_backup_restore.add_argument("--archive", required=True)
    p_backup_restore.add_argument("--overwrite", action="store_true")

    p_api = sub.add_parser("api")
    p_api_sub = p_api.add_subparsers(dest="api_command", required=True)
    p_api_sub.add_parser("export")
    p_api_serve = p_api_sub.add_parser("serve")
    p_api_serve.add_argument("--host", default="127.0.0.1")
    p_api_serve.add_argument("--port", type=int, default=8765)

    p_gateway = sub.add_parser("gateway")
    p_gateway_sub = p_gateway.add_subparsers(dest="gateway_command", required=True)
    p_gateway_context = p_gateway_sub.add_parser("context")
    p_gateway_context.add_argument("--project", required=True)
    p_gateway_context.add_argument("--agent", required=True)
    p_gateway_context.add_argument("--task", required=True)

    sub.add_parser("validate")
    return parser


def bundle_from_args(args: argparse.Namespace) -> Bundle:
    return Bundle(Path(args.root).resolve() if args.root else find_bundle_root())


def cmd_init(bundle: Bundle, args: argparse.Namespace) -> None:
    agent_id = args.agent_id or f"agent.{args.user_id}.builder"
    config = default_config(bundle, args.user_id, args.ai_tool, agent_id, args.remote)
    save_config(bundle, config)
    print(f"initialized {bundle.config_path}")


def cmd_status(bundle: Bundle) -> None:
    config = load_config(bundle)
    profile_name = config.get("activeProfile", "local")
    profile = config.get("profiles", {}).get(profile_name, {})
    problems = validate_bundle(bundle)
    print(f"root: {bundle.root}")
    print(f"profile: {profile_name}")
    print(f"backend: {profile.get('backend', '')}")
    print(f"valid: {'yes' if not problems else 'no'}")
    if problems:
        print("problems:")
        for problem in problems:
            print(f"- {problem}")


def active_profile(bundle: Bundle) -> dict:
    config = load_config(bundle)
    profile_name = config.get("activeProfile", "local")
    profile = dict(config.get("profiles", {}).get(profile_name, {}))
    profile["name"] = profile_name
    return profile


def resolve_api_base_url(profile: dict) -> str:
    raw = str(profile.get("apiBaseUrl", "")).strip()
    if raw.startswith("${") and raw.endswith("}"):
        env_name = raw[2:-1]
        raw = os.environ.get(env_name, "")
    if not raw:
        raise KnowledgeError("active api profile has no apiBaseUrl")
    return raw.rstrip("/")


def api_request(bundle: Bundle, method: str, path: str, payload: dict | None = None) -> dict:
    profile = active_profile(bundle)
    base = resolve_api_base_url(profile)
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"} if body else {}
    token_env = str(profile.get("apiTokenEnv", "")).strip()
    token = os.environ.get(token_env, "") if token_env else str(profile.get("apiToken", "")).strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(
        base + path,
        data=body,
        headers=headers,
        method=method,
    )
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def use_api_backend(bundle: Bundle) -> bool:
    return active_profile(bundle).get("backend") == "api"


def main(argv: list[str] | None = None) -> int:
    parser = make_parser()
    args = parser.parse_args(argv)
    bundle = bundle_from_args(args)
    try:
        if args.command == "init":
            cmd_init(bundle, args)
        elif args.command == "install":
            agent_id = args.agent_id or f"agent.{args.user_id}.builder"
            paths = install_connector(
                bundle,
                args.user_id,
                args.ai_tool,
                agent_id,
                args.remote,
                args.default_project,
                args.register_agent,
                args.agent_name,
                args.purpose,
                not args.no_rebuild_index,
            )
            for path in paths:
                print(path)
        elif args.command == "status":
            cmd_status(bundle)
        elif args.command == "profile":
            config = load_config(bundle)
            if args.name not in config.get("profiles", {}):
                raise KnowledgeError(f"unknown profile: {args.name}")
            config["activeProfile"] = args.name
            save_config(bundle, config)
            print(f"active profile: {args.name}")
        elif args.command == "sync":
            if args.sync_command == "pull":
                try:
                    print(git(bundle, ["pull", "--ff-only"]))
                except KnowledgeError as exc:
                    path = create_conflict(bundle, "git_pull", "system", str(exc), ["git:pull"])
                    print(f"created conflict: {path}", file=sys.stderr)
                    return 2
            elif args.sync_command == "push":
                try:
                    print(git(bundle, ["push"]))
                except KnowledgeError as exc:
                    path = create_conflict(bundle, "git_push", "system", str(exc), ["git:push"])
                    print(f"created conflict: {path}", file=sys.stderr)
                    return 2
        elif args.command == "agent":
            path = make_agent(bundle, args.agent_id, args.name, args.owner, args.tool, args.purpose)
            print(path)
        elif args.command == "project":
            path = make_project(bundle, args.project_id, args.name, args.owner)
            print(path)
        elif args.command == "tool":
            if args.tool_command == "register":
                path = make_tool(bundle, args.tool_id, args.name, args.owner, args.repo, args.entrypoint, args.risk)
                print(path)
            elif args.tool_command == "invoke":
                if use_api_backend(bundle):
                    result = api_request(
                        bundle,
                        "POST",
                        "/v0/tool/invoke",
                        {
                            "toolId": args.tool_id,
                            "projectId": args.project,
                            "agentId": args.agent,
                            "input": args.input,
                            "execute": args.execute,
                        },
                    )
                else:
                    result = invoke_tool(bundle, args.tool_id, args.project, args.agent, args.input, args.execute)
                print(json.dumps(result, indent=2, ensure_ascii=False))
        elif args.command == "policy":
            path = make_policy(
                bundle,
                args.policy_id,
                args.title,
                args.agent_id,
                args.owner,
                args.allow_project,
                args.allow_scope,
                args.allow_risk,
            )
            print(path)
        elif args.command == "start":
            path = start_task(bundle, args.project, args.agent, args.task, args.retrieval_limit)
            print(path)
        elif args.command == "finish":
            path = finish_task(bundle, args.project, args.agent, args.summary, args.result, args.no_reusable_lesson, not args.no_tool_update)
            print(path)
        elif args.command == "review":
            if args.review_command == "list":
                queue = list_review_queue(bundle)
                for item in queue:
                    if args.object_type and item["type"] != args.object_type:
                        continue
                    print(f"{item['path']}\t{item['type']}\t{item['status']}\t{item['owner']}\t{item['title']}")
            elif args.review_command == "update":
                if use_api_backend(bundle):
                    print(
                        json.dumps(
                            api_request(
                                bundle,
                                "POST",
                                "/v0/review/update",
                                {"target": args.target, "status": args.status, "reviewer": args.reviewer},
                            ),
                            indent=2,
                            ensure_ascii=False,
                        )
                    )
                else:
                    path = review_path(bundle, Path(args.target), args.status, args.reviewer)
                    print(path)
            elif args.review_command == "bulk":
                paths = bulk_review(bundle, args.object_type, args.from_status, args.to_status, args.reviewer, args.limit or None)
                for path in paths:
                    print(path)
        elif args.command == "index":
            if args.index_command == "rebuild":
                count = rebuild_index(bundle)
                print(f"indexed {count} objects")
            elif args.index_command == "search":
                filters = {
                    "type": args.object_type,
                    "status": args.status,
                    "projectId": args.project_id,
                    "agentId": args.agent_id,
                    "toolId": args.tool_id,
                    "riskLevel": args.risk_level,
                    "text": args.text,
                }
                if use_api_backend(bundle):
                    query = urlencode({key: value for key, value in filters.items() if value})
                    rows = api_request(bundle, "GET", "/v0/objects" + (f"?{query}" if query else "")).get("objects", [])
                else:
                    rows = search_index(bundle, filters)
                for row in rows:
                    print(f"{row['path']}\t{row['type']}\t{row['status']}\t{row['title']}")
        elif args.command == "rag":
            if args.rag_command == "rebuild":
                count = rebuild_retrieval_index(bundle)
                print(f"indexed {count} chunks")
            elif args.rag_command == "search":
                if use_api_backend(bundle):
                    params: list[tuple[str, str]] = [("query", args.query), ("limit", str(args.limit))]
                    if args.project_id:
                        params.append(("projectId", args.project_id))
                    params.extend(("scope", scope) for scope in args.scope)
                    rows = api_request(bundle, "GET", f"/v0/rag/search?{urlencode(params)}").get("chunks", [])
                else:
                    rows = search_retrieval(bundle, args.query, project_id=args.project_id, scopes=args.scope, limit=args.limit)
                for row in rows:
                    print(f"{row['score']}\t{row['path']}#{row['chunkId']}\t{row['sourceRef']}")
        elif args.command == "conflict":
            if args.conflict_command == "create":
                path = create_conflict(bundle, args.conflict_type, args.owner, args.summary, args.affected)
                print(path)
            elif args.conflict_command == "resolve":
                path = resolve_conflict(bundle, Path(args.target), args.owner, args.resolution)
                print(path)
        elif args.command == "audit":
            if args.audit_command == "search":
                if use_api_backend(bundle):
                    query = urlencode(
                        {
                            key: value
                            for key, value in {
                                "projectId": args.project_id,
                                "agentId": args.agent_id,
                                "toolId": args.tool_id,
                                "target": args.target,
                            }.items()
                            if value
                        }
                    )
                    rows = api_request(bundle, "GET", "/v0/audit" + (f"?{query}" if query else "")).get("auditLogs", [])
                else:
                    rows = search_audit_logs(bundle, args.project_id, args.agent_id, args.tool_id, args.target)
                for row in rows:
                    print(f"{row['path']}\t{row['action']}\t{row['actor']}\t{row['targetRef']}\t{row['policyResult']}")
        elif args.command == "metrics":
            path = create_metrics_report(bundle, args.owner)
            print(path)
        elif args.command == "stale":
            paths = detect_stale(bundle, args.owner)
            for path in paths:
                print(path)
        elif args.command == "eval":
            if args.eval_command == "case":
                path = create_eval_case(bundle, args.eval_id, args.title, args.owner, args.target_ref, args.input, args.expected)
                print(path)
            elif args.eval_command == "run":
                path = run_eval_case(bundle, args.eval_id, args.actual, args.runner)
                print(path)
        elif args.command == "backup":
            if args.backup_command == "create":
                path = create_backup(bundle, Path(args.output) if args.output else None)
                print(path)
            elif args.backup_command == "restore":
                paths = restore_backup(bundle, Path(args.archive), args.overwrite)
                for path in paths:
                    print(path)
        elif args.command == "api":
            if args.api_command == "export":
                result = api_request(bundle, "GET", "/v0/snapshot") if use_api_backend(bundle) else export_api_snapshot(bundle)
                print(json.dumps(result, indent=2, ensure_ascii=False))
            elif args.api_command == "serve":
                serve(bundle, args.host, args.port)
        elif args.command == "gateway":
            if args.gateway_command == "context":
                if use_api_backend(bundle):
                    result = api_request(bundle, "POST", "/v0/gateway/context", {"projectId": args.project, "agentId": args.agent, "task": args.task})
                else:
                    result = gateway_context(bundle, args.project, args.agent, args.task)
                print(json.dumps(result, indent=2, ensure_ascii=False))
        elif args.command == "validate":
            problems = validate_bundle(bundle)
            if problems:
                for problem in problems:
                    print(problem)
                return 1
            print("valid")
        return 0
    except KnowledgeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
