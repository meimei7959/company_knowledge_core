#!/usr/bin/env bash
set -euo pipefail

DEFAULT_CENTRAL_SERVICE_URL="${AGENT_OS_CENTRAL_SERVICE_URL:-https://124.221.138.151/knowledge-api}"
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

  for path in "AGENTS.md" ".agent-os/project.json" ".agent-os/README.md"; do
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
    if curl -fsS --max-time 5 "$CENTRAL_SERVICE_URL/health" >/dev/null 2>&1; then
      echo "OK: central service health reachable: $CENTRAL_SERVICE_URL/health"
    else
      echo "WARN: central service health not reachable: $CENTRAL_SERVICE_URL/health"
      echo "      File setup can still be correct; check network, service, certificate, token, or URL."
    fi
  else
    echo "WARN: curl not found; skipped central service health check"
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

python3 <<'PY'
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
    },
}

(agent_os_dir / "project.json").write_text(json.dumps(project_json, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(agent_os_dir / "README.md").write_text(
    f"# Agent OS 接入说明\n\n本项目已接入中心 Agent OS。\n\n- 项目 ID：`{project_id}`\n- 中心服务：`{central_service_url}`\n- 接入配置：`.agent-os/project.json`\n- Agent 入口：`AGENTS.md`\n",
    encoding="utf-8",
)

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
PY

echo "Agent OS files written."
verify_project
