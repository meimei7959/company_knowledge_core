#!/usr/bin/env bash
set -euo pipefail

DEFAULT_CENTRAL_SERVICE_URL="${AGENT_OS_CENTRAL_SERVICE_URL:-https://zknowai.com/knowledge-api}"
CENTRAL_SERVICE_URL="$DEFAULT_CENTRAL_SERVICE_URL"
PROJECT_ID=""
PROJECT_NAME=""
VERIFY_ONLY=0

usage() {
  cat <<'EOF'
Agent OS project initializer

Usage:
  bash agent-os-init.sh [options]

Options:
  --central-service-url URL   Central Agent OS service URL.
  --project-id ID             Project id. Default: sanitized current directory name.
  --project-name NAME         Project name. Default: current directory name.
  --verify-only               Verify current project without modifying files.
  -h, --help                  Show help.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --central-service-url)
      CENTRAL_SERVICE_URL="${2:-}"
      shift 2
      ;;
    --project-id)
      PROJECT_ID="${2:-}"
      shift 2
      ;;
    --project-name)
      PROJECT_NAME="${2:-}"
      shift 2
      ;;
    --verify-only)
      VERIFY_ONLY=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 is required." >&2
  exit 1
fi

PROJECT_ROOT="$(pwd)"
PROJECT_BASENAME="$(basename "$PROJECT_ROOT")"

if [[ -z "$PROJECT_NAME" ]]; then
  PROJECT_NAME="$PROJECT_BASENAME"
fi

if [[ -z "$PROJECT_ID" ]]; then
  PROJECT_ID="$(printf '%s' "$PROJECT_BASENAME" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9._-]+/-/g; s/^-+//; s/-+$//; s/-+/-/g')"
fi

if [[ -z "$PROJECT_ID" ]]; then
  echo "ERROR: project id is empty. Use --project-id." >&2
  exit 1
fi

verify_project() {
  local fail=0

  echo "Agent OS verification"
  echo "Project root: $PROJECT_ROOT"

  for path in "AGENTS.md" ".agent-os/project.json" ".agent-os/README.md" ".agent-os/feedback.sh"; do
    if [[ -f "$PROJECT_ROOT/$path" ]]; then
      echo "OK: $path exists"
    else
      echo "FAIL: $path missing"
      fail=1
    fi
  done

  if [[ -f "$PROJECT_ROOT/.agent-os/project.json" ]]; then
    python3 - "$PROJECT_ROOT/.agent-os/project.json" "$CENTRAL_SERVICE_URL" <<'PY'
import json
import sys
from pathlib import Path

data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
expected_url = sys.argv[2].rstrip("/")
ok = True

checks = [
    ("schemaVersion", data.get("schemaVersion") == "workspace-ai-context-v0"),
    ("controlPlaneMode", data.get("controlPlaneMode") == "central-service"),
    ("projectId", bool(data.get("projectId"))),
    ("projectName", bool(data.get("projectName"))),
    ("centralServiceUrl", str(data.get("centralServiceUrl") or "").rstrip("/") == expected_url),
    ("contextLayers", bool(data.get("contextLayers"))),
    ("planGate.requiredBeforeUnconfirmedWork", (data.get("planGate") or {}).get("requiredBeforeUnconfirmedWork") is True),
    ("independentReviewGate.requiredForHighImpactWork", (data.get("independentReviewGate") or {}).get("requiredForHighImpactWork") is True),
]

for name, passed in checks:
    print(("OK: " if passed else "FAIL: ") + name)
    ok = ok and passed

sys.exit(0 if ok else 1)
PY
  fi

  if [[ -f "$PROJECT_ROOT/AGENTS.md" ]]; then
    if grep -q "AGENT_OS_CONTEXT_V0_START" "$PROJECT_ROOT/AGENTS.md"; then
      echo "OK: AGENTS.md contains Agent OS context block"
    else
      echo "FAIL: AGENTS.md missing Agent OS context block"
      fail=1
    fi
    if grep -q "Independent Review" "$PROJECT_ROOT/AGENTS.md"; then
      echo "OK: AGENTS.md contains Independent Review Gate"
    else
      echo "FAIL: AGENTS.md missing Independent Review Gate"
      fail=1
    fi
  fi

  if command -v curl >/dev/null 2>&1; then
    if curl -fsS --max-time 10 "$CENTRAL_SERVICE_URL/health" >/dev/null 2>&1; then
      echo "OK: optional central service health reachable: $CENTRAL_SERVICE_URL/health"
    else
      echo "INFO: optional central service health not reachable from this shell: $CENTRAL_SERVICE_URL/health"
      echo "      Local setup is still valid if all file checks passed."
      echo "      In Codex/Claude/Antigravity sandbox runs, outbound network may be blocked."
      echo "      To verify service connectivity, run this in a normal terminal:"
      echo "      curl -fsS $CENTRAL_SERVICE_URL/health"
    fi
  else
    echo "INFO: curl not found; skipped optional central service health check"
  fi

  if [[ "$fail" -ne 0 ]]; then
    echo "RESULT: failed"
    return 1
  fi

  echo "RESULT: local Agent OS project files are valid"
}

if [[ "$VERIFY_ONLY" -eq 1 ]]; then
  verify_project
  exit $?
fi

mkdir -p "$PROJECT_ROOT/.agent-os"

export PROJECT_ROOT PROJECT_ID PROJECT_NAME CENTRAL_SERVICE_URL

python3 <<'PYINIT'
import json
import os
from pathlib import Path

root = Path(os.environ["PROJECT_ROOT"])
project_id = os.environ["PROJECT_ID"]
project_name = os.environ["PROJECT_NAME"]
central_service_url = os.environ["CENTRAL_SERVICE_URL"].rstrip("/")
agent_os_dir = root / ".agent-os"

project_json = {
    "schemaVersion": "workspace-ai-context-v0",
    "projectId": project_id,
    "projectName": project_name,
    "workspaceRoot": str(root),
    "centralServiceUrl": central_service_url,
    "controlPlaneMode": "central-service",
    "contextLayers": {
        "projectLayer": ["AGENTS.md", ".agent-os/project.json", "local project documents"],
        "capabilityLayer": [
            f"{central_service_url}/v0/workspace/client/manifest",
            f"{central_service_url}/v0/capabilities",
            "central role profiles",
            "central task/spec/guard rules",
            "central workspace client",
            "central feedback tools",
        ],
        "controlLayer": [
            f"{central_service_url}/v0/control-plane/status",
            "runner contract",
            "audit",
            "review",
            "approval",
            "knowledge governance",
            "lifecycle",
        ],
    },
    "executionAdapters": ["codex", "claude", "antigravity", "runner"],
    "planGate": {
        "requiredBeforeUnconfirmedWork": True,
        "requiredPlanFields": ["goal", "scope", "executionApproach", "deliverables", "acceptanceChecks"],
        "requiresSelfReviewAndImprovedPlan": True,
        "confirmedTasksMayExecuteDirectly": True,
    },
    "independentReviewGate": {
        "requiredForHighImpactWork": True,
        "triggerWhen": [
            "unconfirmed_work",
            "high_impact_change",
            "cross_role_work",
            "user_visible_change",
            "risky_or_ambiguous_goal",
        ],
        "flow": ["Draft Plan", "Self Review", "Improved Plan", "Independent Review", "Final Plan", "Human Confirm"],
        "requiredReviewFields": ["reviewerPerspective", "findings", "blockingIssues", "suggestedChanges", "decision"],
        "reviewerMapping": {
            "general_plan_or_acceptance": "project-manager",
            "product_or_user_impact": "product-manager",
            "technical_or_architecture_risk": "architecture",
            "implementation_or_regression_risk": "test",
            "operations_or_launch": "operations",
            "knowledge_policy_skill_tool_or_agent_asset": "knowledge-review",
        },
    },
    "feedback": {
        "systemIssueEndpoint": f"{central_service_url}/v0/defects",
        "capabilityFeedbackEndpoint": f"{central_service_url}/v0/capabilities/feedback",
        "feedbackCenterCommand": ".agent-os/feedback.sh \"<feedback message>\"",
        "tokenEnvCandidates": [
            "AGENT_OS_FEEDBACK_TOKEN",
            "ZHENZHI_KNOWLEDGE_API_TOKEN_PROD",
            "ZHENZHI_KNOWLEDGE_API_TOKEN",
        ],
        "fallbackOutbox": ".agent-os/feedback-outbox",
        "promotionGate": "PM review -> role review -> human confirmation before capability/control promotion",
    },
}

(agent_os_dir / "project.json").write_text(json.dumps(project_json, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(agent_os_dir / "README.md").write_text(
    f"# Agent OS 接入说明\n\n本项目已接入中心 Agent OS。\n\n- 项目 ID：`{project_id}`\n- 中心服务：`{central_service_url}`\n- 接入配置：`.agent-os/project.json`\n- Agent 入口：`AGENTS.md`\n- 反馈中心：`.agent-os/feedback.sh \"<反馈内容>\"`\n",
    encoding="utf-8",
)

feedback_script = r'''#!/usr/bin/env bash
set -euo pipefail

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 is required." >&2
  exit 1
fi

python3 - "$@" <<'PY'
import argparse
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request
import uuid
from pathlib import Path

def find_project_root(start: Path) -> Path:
    current = start.resolve()
    for candidate in [current, *current.parents]:
        if (candidate / ".agent-os" / "project.json").is_file():
            return candidate
    return current

def classify(message: str, explicit: str) -> str:
    if explicit and explicit != "auto":
        return explicit
    text = message.lower()
    if any(word in text for word in ["缺", "少", "技能", "能力", "skill", "capability"]):
        return "skill-gap"
    if any(word in text for word in ["规则", "约束", "agents.md", "流程", "规范", "rule"]):
        return "rule-suggestion"
    if any(word in text for word in ["问题", "失败", "报错", "不对", "bug", "issue", "broken", "error"]):
        return "system-issue"
    if any(word in text for word in ["好用", "有效", "不错", "建议保留", "复用", "useful", "good"]):
        return "capability-feedback-positive"
    return "general-feedback"

def token_from_env(token_env: str) -> str:
    for name in ["AGENT_OS_FEEDBACK_TOKEN", token_env, "ZHENZHI_KNOWLEDGE_API_TOKEN"]:
        value = os.environ.get(name, "").strip()
        if value:
            return value
    return ""

def write_outbox(root: Path, endpoint: str, payload: dict, reason: str) -> Path:
    outbox = root / ".agent-os" / "feedback-outbox"
    outbox.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = outbox / f"feedback.{stamp}.{uuid.uuid4().hex[:8]}.json"
    envelope = {
        "schemaVersion": "agent-os-feedback-v0",
        "status": "pending-submit",
        "createdAt": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "endpoint": endpoint,
        "reason": reason,
        "payload": payload,
        "reviewGate": "PM initial review -> role review -> human confirmation before promotion",
    }
    path.write_text(json.dumps(envelope, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path

def post_feedback(endpoint: str, token: str, payload: dict) -> dict:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))

def submit_outbox(root: Path, token: str) -> int:
    if not token:
        print("ERROR: feedback token missing. Set AGENT_OS_FEEDBACK_TOKEN or ZHENZHI_KNOWLEDGE_API_TOKEN_PROD.", file=sys.stderr)
        return 1
    outbox = root / ".agent-os" / "feedback-outbox"
    sent = root / ".agent-os" / "feedback-sent"
    sent.mkdir(parents=True, exist_ok=True)
    files = sorted(outbox.glob("*.json")) if outbox.exists() else []
    if not files:
        print("No pending feedback.")
        return 0
    ok = 0
    for path in files:
        envelope = json.loads(path.read_text(encoding="utf-8"))
        try:
            result = post_feedback(str(envelope["endpoint"]), token, envelope["payload"])
        except Exception as exc:
            print(f"FAIL: {path.name}: {exc}", file=sys.stderr)
            continue
        target = sent / path.name
        path.replace(target)
        ok += 1
        print(f"Submitted {path.name}: {result.get('feedbackRef', result.get('feedbackId', 'ok'))}")
    print(f"RESULT: submitted {ok}/{len(files)} pending feedback item(s)")
    return 0 if ok == len(files) else 1

parser = argparse.ArgumentParser(description="Submit simple Agent OS feedback to the central review queue.")
parser.add_argument("message", nargs="*", help="Feedback message. If omitted, stdin is used.")
parser.add_argument("--type", default="auto", choices=["auto", "skill-gap", "rule-suggestion", "system-issue", "capability-feedback", "capability-feedback-positive", "general-feedback"])
parser.add_argument("--actor", default=os.environ.get("AGENT_OS_FEEDBACK_ACTOR") or os.environ.get("USER") or "project-agent")
parser.add_argument("--rating", default="")
parser.add_argument("--capability-ref", default="agent-os:workspace-capability-layer")
parser.add_argument("--source-ref", action="append", default=[])
parser.add_argument("--token-env", default="ZHENZHI_KNOWLEDGE_API_TOKEN_PROD")
parser.add_argument("--central-service-url", default="")
parser.add_argument("--offline", action="store_true", help="Do not call the network; write feedback to local outbox.")
parser.add_argument("--submit-outbox", action="store_true", help="Submit .agent-os/feedback-outbox items when token/network are available.")
args = parser.parse_args()

root = find_project_root(Path.cwd())
config_path = root / ".agent-os" / "project.json"
config = json.loads(config_path.read_text(encoding="utf-8"))
central_url = (args.central_service_url or config.get("centralServiceUrl") or "").rstrip("/")
endpoint = ((config.get("feedback") or {}).get("capabilityFeedbackEndpoint") or f"{central_url}/v0/capabilities/feedback").rstrip("/")
token = token_from_env(args.token_env)

if args.submit_outbox:
    raise SystemExit(submit_outbox(root, token))

message = " ".join(args.message).strip()
if not message and not sys.stdin.isatty():
    message = sys.stdin.read().strip()
if not message:
    print("ERROR: feedback message is required.", file=sys.stderr)
    print("Usage: .agent-os/feedback.sh \"中心少一个软著材料整理技能\"", file=sys.stderr)
    raise SystemExit(2)

feedback_type = classify(message, args.type)
rating = args.rating or ("good" if feedback_type == "capability-feedback-positive" else "")
if not rating and feedback_type in {"skill-gap", "rule-suggestion", "system-issue"}:
    rating = "negative"
project_id = str(config.get("projectId") or root.name)
project_name = str(config.get("projectName") or root.name)
content = "\n".join([
    f"Source project: {project_id}",
    f"Project name: {project_name}",
    f"Feedback type: {feedback_type}",
    "",
    "Message:",
    message,
    "",
    "Required handling:",
    "- This is a candidate feedback item, not an approved company rule.",
    "- PM initial review is required.",
    "- Role/Knowledge Review is required before reusable promotion.",
    "- Human confirmation is required before updating Capability Layer or Control Layer.",
])
evidence_refs = [f"sourceProject:{project_id}", f"projectRoot:{root}", *[item for item in args.source_ref if item.strip()]]
payload = {
    "capabilityRef": args.capability_ref,
    "actor": args.actor,
    "content": content,
    "rating": rating,
    "feedbackType": feedback_type,
    "evidenceRefs": evidence_refs,
}

if args.offline or not token:
    reason = "offline requested" if args.offline else "feedback token missing"
    outbox_path = write_outbox(root, endpoint, payload, reason)
    print("Feedback captured locally")
    print("status: pending-submit")
    print(f"type: {feedback_type}")
    print(f"outbox: {outbox_path.relative_to(root)}")
    print("next: set AGENT_OS_FEEDBACK_TOKEN or ZHENZHI_KNOWLEDGE_API_TOKEN_PROD, then run .agent-os/feedback.sh --submit-outbox")
    raise SystemExit(0)

try:
    result = post_feedback(endpoint, token, payload)
except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as exc:
    outbox_path = write_outbox(root, endpoint, payload, f"submit failed: {exc}")
    print("Feedback captured locally")
    print("status: pending-submit")
    print(f"type: {feedback_type}")
    print(f"outbox: {outbox_path.relative_to(root)}")
    print(f"submitError: {exc}")
    raise SystemExit(0)

print("Feedback submitted")
print("status: pending-review")
print(f"type: {feedback_type}")
print(f"feedbackRef: {result.get('feedbackRef', '')}")
print("next: PM initial review -> role review -> human confirmation before promotion")
PY
'''

feedback_path = agent_os_dir / "feedback.sh"
feedback_path.write_text(feedback_script, encoding="utf-8")
feedback_path.chmod(0o755)

block = f"""<!-- AGENT_OS_CONTEXT_V0_START -->

## Workspace AI Context v0

This project is connected to the central Agent OS in `central-service` mode.

Connection:

- projectId: `{project_id}`
- projectName: `{project_name}`
- centralServiceUrl: `{central_service_url}`
- config: `.agent-os/project.json`

Context layers:

1. Project Layer: this `AGENTS.md`, `.agent-os/project.json`, and local project documents.
2. Capability Layer: central Agent OS role profiles, task/spec/guard rules, workspace client, and feedback tools.
3. Control Layer: central Control Plane Kernel lifecycle, runner contract, audit, review, approval, and knowledge governance rules.

Required Agent work pattern:

- If work is unclear, strategic, risky, user-visible, or not already decomposed into an approved task, output a Draft Plan first.
- The plan must include `goal`, `scope`, `executionApproach`, `deliverables`, and `acceptanceChecks`.
- The drafting Agent must Self Review the plan and improve it once.
- High-impact work must pass Independent Review from another role perspective before human confirmation.
- Independent Review must check goal, assumptions, risk, acceptance checks, role boundaries, evidence, and Control Layer constraints.
- Final Plan must state which review findings were accepted and which were not, with reasons.
- If a plan has already been confirmed and decomposed into specific tasks, execute directly under the task contract.

Default Independent Review perspectives:

- Project Manager: general plan, routing, acceptance, blockers, handoff.
- Product Manager: product, user impact, requirements, customer-facing content.
- Architecture: technical approach, architecture boundary, system risk.
- Development/Test: implementation path, code risk, regression risk.
- Operations: launch, campaign, customer touch, operational risk.
- Knowledge Review: reusable knowledge, policy, skill, tool, Agent, or governance changes.

Feedback Center:

- If the user says "反馈到中心", "提交反馈", "中心少一个技能", or asks to reuse a good local rule, run:
  `.agent-os/feedback.sh "<one-sentence feedback>"`
- Keep the employee experience short. Do not ask the user to fill long templates.
- Feedback is only a candidate. It must go through PM review, role/Knowledge Review, and human confirmation before promotion to Capability Layer or Control Layer.
- If the script writes `.agent-os/feedback-outbox/*.json`, tell the user it is captured locally and can be submitted when token/network is available.

Startup check prompt:

```text
先读取 AGENTS.md 和 .agent-os/project.json。
不要执行任务。
告诉我当前项目的 Project Layer、Capability Layer、Control Layer 分别是什么。
然后告诉我如果我要你做一个未确认任务，你应该先做什么，什么时候需要 Independent Review。
```

<!-- AGENT_OS_CONTEXT_V0_END -->
"""

agents_path = root / "AGENTS.md"
if agents_path.exists():
    existing = agents_path.read_text(encoding="utf-8")
    start = "<!-- AGENT_OS_CONTEXT_V0_START -->"
    end = "<!-- AGENT_OS_CONTEXT_V0_END -->"
    if start in existing and end in existing:
        before = existing.split(start, 1)[0].rstrip()
        after = existing.split(end, 1)[1].lstrip()
        new_text = before + "\n\n" + block + ("\n\n" + after if after else "")
    else:
        new_text = existing.rstrip() + "\n\n" + block
else:
    new_text = f"# {project_name} Agent Instructions\n\n" + block

agents_path.write_text(new_text.rstrip() + "\n", encoding="utf-8")
PYINIT

echo "Agent OS files written."
verify_project
