#!/usr/bin/env python3
"""Two-host Agent Ring proof evidence harness.

This script records evidence for real distributed runner runs. It does not
create proof tasks; the coordinator must prepare proof task ids first.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_VERIFY_STEPS = {
    "runner_register",
    "runner_heartbeat",
    "runner_list",
    "task_claim",
    "task_pull",
    "task_heartbeat",
    "task_finish",
    "task_cancel",
    "task_retry",
    "task_handoff",
    "notification_list",
    "audit_list",
    "stale_lease_reclaim",
    "runner_isolation_rejected",
}


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_json(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def hash_token(value: str) -> str:
    if not value:
        return ""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def read_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"leases": {}}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"state file must contain an object: {path}")
    data.setdefault("leases", {})
    return data


def write_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_lease(args: argparse.Namespace, task_id: str) -> str:
    if args.lease_token:
        return args.lease_token
    state = read_state(Path(args.state_file))
    token = str(state.get("leases", {}).get(task_id, ""))
    if not token:
        raise SystemExit(f"missing lease token for {task_id}; pass --lease-token or run claim first")
    return token


def save_lease(args: argparse.Namespace, task_id: str, token: str) -> None:
    state_path = Path(args.state_file)
    state = read_state(state_path)
    state.setdefault("leases", {})[task_id] = token
    write_state(state_path, state)


def api_token(args: argparse.Namespace) -> str:
    if args.token:
        return args.token
    token = os.environ.get(args.token_env, "")
    if not token:
        raise SystemExit(f"missing API token; set {args.token_env} or pass --token")
    return token


def request_json(args: argparse.Namespace, method: str, path: str, payload: dict[str, Any] | None = None) -> tuple[int, dict[str, Any]]:
    base = args.base_url.rstrip("/")
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Authorization": f"Bearer {api_token(args)}"}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(base + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=args.timeout_seconds) as response:
            body = json.loads(response.read().decode("utf-8"))
            return response.status, body
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8")
        try:
            body = json.loads(raw)
        except json.JSONDecodeError:
            body = {"error": raw}
        return exc.code, body


def summarize_response(body: dict[str, Any]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for key in ("apiVersion", "kind", "runnerRef", "resultRef", "auditRef", "errorCode", "message", "blockerReason"):
        if key in body:
            summary[key] = body[key]
    if "leaseToken" in body:
        summary["leaseTokenHash"] = hash_token(str(body["leaseToken"]))
    if isinstance(body.get("task"), dict):
        task = body["task"]
        summary["task"] = {
            "taskId": task.get("taskId"),
            "status": task.get("status"),
            "runnerId": task.get("runnerId"),
            "leaseOwner": task.get("leaseOwner"),
            "leaseExpiresAt": task.get("leaseExpiresAt"),
        }
    if isinstance(body.get("taskResult"), dict):
        result = body["taskResult"]
        summary["taskResult"] = {
            "resultId": result.get("resultId"),
            "taskId": result.get("taskId"),
            "runnerId": result.get("runnerId"),
            "executorAgent": result.get("executorAgent"),
            "status": result.get("status"),
        }
    return summary


def append_event(args: argparse.Namespace, event: dict[str, Any]) -> None:
    path = Path(args.evidence_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    base = {
        "observedAt": now_utc(),
        "proofRunId": args.proof_run_id,
        "scenario": args.scenario,
        "hostLabel": args.host_label,
        "runnerId": args.runner_id,
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({**base, **event}, sort_keys=True) + "\n")


def call_step(
    args: argparse.Namespace,
    step: str,
    method: str,
    path: str,
    payload: dict[str, Any] | None,
    expected_status: int = 200,
    expect_error: bool = False,
) -> dict[str, Any]:
    status, body = request_json(args, method, path, payload)
    ok = status == expected_status if expect_error else status == 200
    append_event(
        args,
        {
            "step": step,
            "method": method,
            "path": path,
            "payloadHash": sha256_json(payload or {}),
            "httpStatus": status,
            "ok": ok,
            "expectedError": expect_error,
            "response": summarize_response(body),
        },
    )
    if not ok:
        raise SystemExit(f"{step}: expected HTTP {expected_status if expect_error else 200}, got {status}: {body}")
    return body


def register(args: argparse.Namespace) -> None:
    payload = {
        "runnerId": args.runner_id,
        "name": args.name or args.runner_id,
        "hostType": args.host_type,
        "mode": args.mode,
        "agents": args.agent,
        "capabilities": args.capability,
        "availableProjects": args.project,
        "repoAccess": args.repo,
        "dataScopes": args.data_scope,
        "ringVersion": args.ring_version,
    }
    call_step(args, "runner_register", "POST", "/v0/runners/register", payload)


def heartbeat_runner(args: argparse.Namespace) -> None:
    payload = {
        "runnerId": args.runner_id,
        "status": args.status,
        "load": args.load,
        "capabilities": args.capability,
        "availableProjects": args.project,
    }
    call_step(args, "runner_heartbeat", "POST", "/v0/runners/heartbeat", payload)


def list_runners(args: argparse.Namespace) -> None:
    query = urllib.parse.urlencode({"projectId": args.project_id}) if args.project_id else ""
    path = "/v0/runners" + (f"?{query}" if query else "")
    call_step(args, "runner_list", "GET", path, None)


def list_notifications(args: argparse.Namespace) -> None:
    params = {"projectId": args.project_id, "taskId": args.task_id, "limit": str(args.limit)}
    query = urllib.parse.urlencode({key: value for key, value in params.items() if value})
    path = "/v0/notifications" + (f"?{query}" if query else "")
    call_step(args, "notification_list", "GET", path, None)


def list_audit(args: argparse.Namespace) -> None:
    params = {"projectId": args.project_id, "target": args.target or args.task_id}
    query = urllib.parse.urlencode({key: value for key, value in params.items() if value})
    path = "/v0/audit" + (f"?{query}" if query else "")
    call_step(args, "audit_list", "GET", path, None)


def claim(args: argparse.Namespace) -> None:
    payload: dict[str, Any] = {"taskId": args.task_id, "runnerId": args.runner_id, "leaseSeconds": args.lease_seconds}
    if args.expected_version is not None:
        payload["expectedVersion"] = args.expected_version
    body = call_step(args, args.step_name, "POST", "/v0/tasks/claim", payload)
    save_lease(args, args.task_id, str(body.get("leaseToken", "")))


def heartbeat_task(args: argparse.Namespace) -> None:
    payload = {
        "taskId": args.task_id,
        "runnerId": args.runner_id,
        "leaseToken": load_lease(args, args.task_id),
        "leaseSeconds": args.lease_seconds,
    }
    call_step(args, "task_heartbeat", "POST", "/v0/tasks/heartbeat", payload)


def pull(args: argparse.Namespace) -> None:
    payload = {"taskId": args.task_id, "runnerId": args.runner_id, "leaseToken": load_lease(args, args.task_id)}
    call_step(args, "task_pull", "POST", "/v0/tasks/pull", payload)


def finish(args: argparse.Namespace) -> None:
    payload = {
        "taskId": args.task_id,
        "result": args.result,
        "summary": args.summary,
        "outputRefs": args.output_ref,
        "evidenceRefs": args.evidence_ref,
        "testsOrChecks": args.test_or_check,
        "runnerId": args.runner_id,
        "leaseToken": load_lease(args, args.task_id),
        "executorAgent": args.executor_agent,
    }
    call_step(args, "task_finish", "POST", "/v0/tasks/finish", payload)


def finish_expect_rejected(args: argparse.Namespace) -> None:
    payload = {
        "taskId": args.task_id,
        "summary": args.summary,
        "runnerId": args.runner_id,
        "leaseToken": args.lease_token or "invalid-distributed-proof-token",
        "executorAgent": args.executor_agent,
    }
    call_step(args, "runner_isolation_rejected", "POST", "/v0/tasks/finish", payload, expected_status=args.expected_status, expect_error=True)


def cancel(args: argparse.Namespace) -> None:
    payload = {
        "taskId": args.task_id,
        "actor": args.actor,
        "reason": args.reason,
        "runnerId": args.runner_id,
        "leaseToken": load_lease(args, args.task_id),
    }
    call_step(args, "task_cancel", "POST", "/v0/tasks/cancel", payload)


def retry(args: argparse.Namespace) -> None:
    payload = {
        "taskId": args.task_id,
        "actor": args.actor,
        "reason": args.reason,
        "runnerId": args.runner_id,
        "leaseToken": args.lease_token or "",
        "preferredRunner": args.preferred_runner,
    }
    call_step(args, "task_retry", "POST", "/v0/tasks/retry", payload)


def handoff(args: argparse.Namespace) -> None:
    payload = {
        "taskId": args.task_id,
        "actor": args.actor,
        "handoffTo": args.to,
        "summary": args.summary,
        "runnerId": args.runner_id,
        "leaseToken": load_lease(args, args.task_id),
        "evidenceRefs": args.evidence_ref,
        "artifactRefs": args.artifact_ref,
        "nextAction": args.next_action,
        "preferredRunner": args.preferred_runner,
    }
    call_step(args, "task_handoff", "POST", "/v0/tasks/handoff", payload)


def verify(args: argparse.Namespace) -> None:
    events: list[dict[str, Any]] = []
    for raw_path in args.evidence:
        path = Path(raw_path)
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            event = json.loads(line)
            event["_source"] = f"{path}:{line_no}"
            events.append(event)
    if not events:
        raise SystemExit("no evidence events found")

    runner_ids = {str(event.get("runnerId", "")) for event in events if event.get("runnerId")}
    host_labels = {str(event.get("hostLabel", "")) for event in events if event.get("hostLabel")}
    proof_ids = {str(event.get("proofRunId", "")) for event in events if event.get("proofRunId")}
    steps = {str(event.get("step", "")) for event in events}
    missing = REQUIRED_VERIFY_STEPS - steps
    problems: list[str] = []
    if len(runner_ids) < 2:
        problems.append("expected evidence from at least two distinct runnerId values")
    if len(host_labels) < 2:
        problems.append("expected evidence from at least two distinct hostLabel values")
    if len(proof_ids) != 1:
        problems.append(f"expected one proofRunId across evidence, found {sorted(proof_ids)}")
    if missing:
        problems.append(f"missing required evidence steps: {sorted(missing)}")
    failed = [event for event in events if not event.get("ok")]
    if failed:
        problems.append(f"{len(failed)} evidence events have ok=false")
    rejected = [event for event in events if event.get("step") == "runner_isolation_rejected" and event.get("expectedError")]
    if not rejected:
        problems.append("runner isolation rejection event must be an expected HTTP error")
    stale = [event for event in events if event.get("step") == "stale_lease_reclaim"]
    if stale and len({event.get("runnerId") for event in stale}) < 1:
        problems.append("stale lease reclaim event must identify reclaiming runner")

    if problems:
        for problem in problems:
            print(f"FAIL: {problem}")
        raise SystemExit(1)
    print(
        "PASS distributed runner evidence contract: "
        f"{len(events)} events, runners={sorted(runner_ids)}, hosts={sorted(host_labels)}, proofRunId={next(iter(proof_ids))}"
    )


def simulate_phase2(args: argparse.Namespace) -> None:
    """Write local two-runner evidence for development self-check only."""
    path = Path(args.evidence_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    proof_run_id = args.proof_run_id if args.proof_run_id != "distributed-proof.manual" else "phase2-simulated-proof.dev"
    scenario = "phase2-local-simulation"
    runners = [
        ("runner.phase2.local-dev-a", "host-a"),
        ("runner.phase2.local-test-b", "host-b"),
    ]
    steps = [
        ("runner_register", runners[0], {"runnerRef": "dev-a"}),
        ("runner_heartbeat", runners[0], {"message": "online"}),
        ("runner_register", runners[1], {"runnerRef": "test-b"}),
        ("runner_heartbeat", runners[1], {"message": "online"}),
        ("runner_list", runners[0], {"message": "two runners visible"}),
        ("task_claim", runners[0], {"leaseToken": "simulated-lease-a"}),
        ("task_pull", runners[0], {"message": "context scoped"}),
        ("task_heartbeat", runners[0], {"message": "lease alive"}),
        ("task_finish", runners[0], {"resultRef": "task-results/simulated-dev-a.md"}),
        ("task_claim", runners[1], {"leaseToken": "simulated-lease-b"}),
        ("task_finish", runners[1], {"resultRef": "task-results/simulated-test-b.md"}),
        ("task_cancel", runners[1], {"message": "cancel recorded"}),
        ("task_retry", runners[1], {"message": "retry recorded"}),
        ("task_handoff", runners[0], {"message": "handoff to test"}),
        ("notification_list", runners[0], {"message": "notifications visible"}),
        ("audit_list", runners[0], {"auditRef": "audit.phase2.simulated"}),
        ("stale_lease_reclaim", runners[1], {"leaseToken": "simulated-reclaim"}),
        ("runner_isolation_rejected", runners[1], {"errorCode": "permission_denied", "message": "expected isolation rejection"}),
    ]
    with path.open("w", encoding="utf-8") as handle:
        for step, (runner_id, host_label), response in steps:
            event = {
                "observedAt": now_utc(),
                "proofRunId": proof_run_id,
                "scenario": scenario,
                "hostLabel": host_label,
                "runnerId": runner_id,
                "step": step,
                "method": "SIMULATED",
                "path": "local-development-self-check",
                "payloadHash": sha256_json({"step": step, "runnerId": runner_id}),
                "httpStatus": 400 if step == "runner_isolation_rejected" else 200,
                "ok": True,
                "expectedError": step == "runner_isolation_rejected",
                "response": summarize_response(response),
                "simulationNotice": "研发自测入口；不能替代最终真实双 host 验收。",
            }
            handle.write(json.dumps(event, sort_keys=True) + "\n")
    print(f"wrote simulated Phase 2 evidence to {path}")


def common_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--base-url", default=os.environ.get("ZK_API_BASE_URL", "http://127.0.0.1:8765"))
    parser.add_argument("--token-env", default="ZHENZHI_KNOWLEDGE_API_TOKEN")
    parser.add_argument("--token", default="")
    parser.add_argument("--timeout-seconds", type=int, default=20)
    parser.add_argument("--proof-run-id", default=os.environ.get("ZK_PROOF_RUN_ID", "distributed-proof.manual"))
    parser.add_argument("--scenario", default="manual")
    parser.add_argument("--runner-id", default=os.environ.get("ZK_RUNNER_ID", ""))
    parser.add_argument("--host-label", default=os.environ.get("ZK_HOST_LABEL", ""))
    parser.add_argument("--evidence-file", default=os.environ.get("ZK_EVIDENCE_FILE", "artifacts/distributed-runner-proof/evidence.jsonl"))
    parser.add_argument("--state-file", default=os.environ.get("ZK_STATE_FILE", ".zhenzhi/distributed-runner-proof-state.json"))
    parser.add_argument("--lease-token", default="")


def add_task_id(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--task-id", required=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Record and verify real distributed Agent Ring runner proof evidence.")
    common_parser(parser)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("register")
    p.set_defaults(func=register)
    p.add_argument("--name", default="")
    p.add_argument("--host-type", default="real-runner")
    p.add_argument("--mode", default="unattended")
    p.add_argument("--agent", action="append", default=["agent.company.development"])
    p.add_argument("--capability", action="append", default=["development", "agent_worker", "scheduler", "distributed_execution"])
    p.add_argument("--project", action="append", default=["company-knowledge-core"])
    p.add_argument("--repo", action="append", default=["/Users/meimei/Documents/company_knowledge_core"])
    p.add_argument("--data-scope", action="append", default=["local_repo"])
    p.add_argument("--ring-version", default="distributed-proof-0.1")

    p = sub.add_parser("heartbeat-runner")
    p.set_defaults(func=heartbeat_runner)
    p.add_argument("--status", default="online")
    p.add_argument("--load", default="0")
    p.add_argument("--capability", action="append", default=["development", "agent_worker", "scheduler", "distributed_execution"])
    p.add_argument("--project", action="append", default=["company-knowledge-core"])

    p = sub.add_parser("list-runners")
    p.set_defaults(func=list_runners)
    p.add_argument("--project-id", default="company-knowledge-core")

    p = sub.add_parser("list-notifications")
    p.set_defaults(func=list_notifications)
    p.add_argument("--project-id", default="company-knowledge-core")
    p.add_argument("--task-id", default="")
    p.add_argument("--limit", type=int, default=50)

    p = sub.add_parser("list-audit")
    p.set_defaults(func=list_audit)
    p.add_argument("--project-id", default="company-knowledge-core")
    p.add_argument("--task-id", default="")
    p.add_argument("--target", default="")

    p = sub.add_parser("claim")
    p.set_defaults(func=claim)
    add_task_id(p)
    p.add_argument("--expected-version", type=int, default=None)
    p.add_argument("--lease-seconds", type=int, default=600)
    p.add_argument("--step-name", choices=["task_claim", "stale_lease_reclaim"], default="task_claim")

    p = sub.add_parser("heartbeat-task")
    p.set_defaults(func=heartbeat_task)
    add_task_id(p)
    p.add_argument("--lease-seconds", type=int, default=600)

    p = sub.add_parser("pull")
    p.set_defaults(func=pull)
    add_task_id(p)

    p = sub.add_parser("finish")
    p.set_defaults(func=finish)
    add_task_id(p)
    p.add_argument("--result", default="done")
    p.add_argument("--summary", required=True)
    p.add_argument("--executor-agent", default="agent.company.development")
    p.add_argument("--output-ref", action="append", default=[])
    p.add_argument("--evidence-ref", action="append", default=[])
    p.add_argument("--test-or-check", action="append", default=[])

    p = sub.add_parser("finish-expect-rejected")
    p.set_defaults(func=finish_expect_rejected)
    add_task_id(p)
    p.add_argument("--summary", default="runner isolation rejection probe")
    p.add_argument("--executor-agent", default="agent.company.development")
    p.add_argument("--expected-status", type=int, default=400)

    p = sub.add_parser("cancel")
    p.set_defaults(func=cancel)
    add_task_id(p)
    p.add_argument("--actor", default="agent-ring")
    p.add_argument("--reason", required=True)

    p = sub.add_parser("retry")
    p.set_defaults(func=retry)
    add_task_id(p)
    p.add_argument("--actor", default="agent-ring")
    p.add_argument("--reason", required=True)
    p.add_argument("--preferred-runner", default="")

    p = sub.add_parser("handoff")
    p.set_defaults(func=handoff)
    add_task_id(p)
    p.add_argument("--actor", default="agent-ring")
    p.add_argument("--to", required=True)
    p.add_argument("--summary", required=True)
    p.add_argument("--preferred-runner", default="")
    p.add_argument("--evidence-ref", action="append", default=[])
    p.add_argument("--artifact-ref", action="append", default=[])
    p.add_argument("--next-action", default="")

    p = sub.add_parser("verify")
    p.set_defaults(func=verify)
    p.add_argument("--evidence", action="append", required=True)

    p = sub.add_parser("simulate-phase2")
    p.set_defaults(func=simulate_phase2)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command not in {"verify", "simulate-phase2"}:
        if not args.runner_id:
            raise SystemExit("--runner-id or ZK_RUNNER_ID is required")
        if not args.host_label:
            raise SystemExit("--host-label or ZK_HOST_LABEL is required")
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
