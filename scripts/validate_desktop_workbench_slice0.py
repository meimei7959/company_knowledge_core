from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from html.parser import HTMLParser
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "projects" / "company-knowledge-core" / "desktop-workbench-slice0"
CHECKLIST_PATH = ARTIFACT_DIR / "slice0-proof-checklist.json"
MANIFEST_PATH = ARTIFACT_DIR / "native-bridge-manifest.json"
FRONTEND_PATH = ARTIFACT_DIR / "shared-frontend-foundation.ts"
SHELL_HTML_PATH = ARTIFACT_DIR / "workbench-shell.html"
SHELL_CSS_PATH = ARTIFACT_DIR / "workbench-shell.css"
SHELL_JS_PATH = ARTIFACT_DIR / "workbench-shell.js"
READ_MODEL_PATH = ARTIFACT_DIR / "workbench-read-model.js"
LIVE_READ_MODEL_PATH = ARTIFACT_DIR / "workbench-live-read-model.js"

REQUIRED_GATE_CATEGORIES = {
    "mac_packaging",
    "windows_packaging",
    "signing_notarization",
    "update_channels",
    "enterprise_network_proxy",
    "secure_storage_auth",
    "native_bridge",
    "deep_links",
    "notification_permission",
    "runner_pairing",
    "environment_release_permissions",
}

REQUIRED_COMMANDS = {
    "selectSourceFileReference",
    "requestNotificationPermission",
    "showNotification",
    "resolveDeepLink",
    "readLocalSetting",
    "writeLocalSetting",
    "storeCredentialReference",
    "getRunnerPairingDiagnostics",
    "handoffRunnerPairingProof",
    "collectRedactedDiagnostics",
}

REQUIRED_SHELL_FILES = {
    "workbench-shell.html",
    "workbench-shell.css",
    "workbench-shell.js",
    "workbench-read-model.js",
    "workbench-live-read-model.js",
}

REQUIRED_WORKBENCH_SURFACES = {
    "home",
    "requirement-center",
    "project-console",
    "agent-team-manager",
    "agent-ring-console",
    "result-center",
    "review-center",
    "quality-dashboard",
    "notification-center",
    "admin-governance",
    "operations-feedback",
    "knowledge-query",
    "settings-security",
    "recovery-center",
}

REQUIRED_READ_MODEL_SECTIONS = {
    "home",
    "projectProgress",
    "agentCurrentWork",
    "runnerLeases",
    "runnerHistory",
    "approvals",
    "notifications",
    "recovery",
    "settingsSecurity",
    "permissionGatedActions",
}

REQUIRED_COLLABORATION_SECTIONS = {
    "entryLabel",
    "projectJoinPolicyLabel",
    "availableDeviceCountLabel",
    "activeRouteSummary",
    "registrationEntries",
    "pairingRequests",
    "devices",
    "runners",
    "routeBoard",
    "recoveryItems",
    "evidenceItems",
    "auditSummaries",
    "technicalDetails",
}

REQUIRED_REGISTRATION_ENTRY_TITLES = {
    "创建项目",
    "邀请电脑",
    "提交电脑注册申请",
    "登记低风险工具",
    "提交工具申请",
}

REQUIRED_REGISTRATION_API_PATHS = {
    "/v0/workbench/projects",
    "/v0/workbench/runner-invitations",
    "/v0/runners/register",
    "/v0/workbench/tools",
    "/v0/workbench/tool-registration-requests",
}

FORBIDDEN_EXECUTION_CONTROL_PERMISSIONS = {
    "dispatchTask",
    "repairTask",
    "overwriteTaskResult",
    "editAgentRun",
    "forceCompleteTask",
    "claimAsWorkbench",
    "collaboration.task.transfer",
    "collaboration.lease.release",
    "collaboration.runner.pause",
    "collaboration.runner.resume",
}

REQUIRED_COLLABORATION_DEVICE_FIELDS = {
    "displayName",
    "ownerLabel",
    "availabilityLabel",
    "workTypeLabels",
    "authorizationSummary",
    "currentTaskLabel",
    "lastSeenLabel",
    "riskLabels",
    "primaryAction",
}

REQUIRED_COLLABORATION_ROUTE_FIELDS = {
    "taskLabel",
    "businessStatus",
    "assignedDeviceLabel",
    "routeReason",
    "blockerLabel",
    "nextOwnerLabel",
    "nextAction",
}

REQUIRED_WORKBENCH_TASK_CHAIN = {
    "kt-v1-workbench-codex-style-design": "agent.company.design",
    "kt-v1-workbench-codex-style-product-review": "agent.company.product-manager",
    "kt-v1-workbench-codex-style-dev": "agent.company.development",
    "kt-v1-workbench-codex-style-test": "agent.company.test",
    "kt-v1-workbench-codex-style-product-final-acceptance": "agent.company.product-manager",
    "kt-v1-workbench-codex-style-pm-final-acceptance": "agent.company.project-manager",
}

REQUIRED_PANEL_STATUSES = {
    "blocked",
    "running",
    "waiting_review",
    "needs_permission",
    "ready",
    "degraded",
    "offline",
    "failed",
    "safe_fallback",
    "stale",
}

FORBIDDEN_FRONTEND_MARKERS = {
    "@tauri-apps/api",
    "window.__TAURI__",
    "from \"electron\"",
    "from 'electron'",
    "require(\"electron\")",
    "require('electron')",
    "ipcRenderer",
    "BrowserWindow",
}

FORBIDDEN_LOCAL_MUTATION_WORDS = {
    "claimTaskLease",
    "mutateTaskLease",
    "direct task lease update",
    "writeTaskResult",
    "writeAgentRun",
    "executeUnregisteredTool",
    "storeRawCredential",
}

FORBIDDEN_VISIBLE_COPY = {
    "Active implementation",
    "Product final acceptance",
    "PM final acceptance",
    "Test closed-loop acceptance",
    "Product Agent accepted",
    "Show last verified evidence",
    "Product final result",
    "PM final result",
    "Test result",
    "TaskResult 写回",
    "Product final acceptance evidence must be ready",
    "Central API read model",
    "Acceptance route",
    "Release readiness",
    "Agent current focus",
    "Attention queue",
    "Run next V1 acceptance stage.",
    "Review cancellation reason",
    "Release Development technical solution tasks",
    "Run Product Manager scope review",
    "Review technical solution and release implementation task.",
    "Plan V2 multi-device Hub",
    "Human confirmation queue",
    "Review high-risk confirm_request messages",
    "Confirm messages",
    "Notification center",
    "Device-aware routing",
    "V1 routes through device.local",
    "Desktop packaging boundary",
    "Tauri/Mac/Windows packaging remains next desktop product boundary",
    "Projects:",
    "Capabilities:",
    "Runner scope and lease audit",
    "Open V1 task recovery",
    "No open V1 task remains.",
    "Scheduler workbench",
    "Resolve confirm request",
    "Retry stale runner",
    "Local Machine",
    "Monitor current work",
    "V1 package execution",
    "Use as baseline",
    "Failed execution",
    "Route to recovery",
    "Stale lease",
    "Retry or cancel",
    "Package retry",
    "Require idempotency",
    "Permission escalation",
    "Show approval owner",
    "No active lease",
    "中央状态只读视图",
    "真实运行状态只读视图",
    "组Agent",
    "组 Agent",
}

FORBIDDEN_INTERNAL_VISIBLE_TERMS = {
    "Agent Hub",
    "Group Agent",
    "Local Router",
    "TaskPackage",
    "AgentMessage",
    "TaskResult",
    "runtimeMetrics",
    "deviceId",
    "session.v1",
    "company-knowledge-core",
    "local-v1-runtime-workbench",
    "agent_runtime",
    "local_router",
    "project_management",
    "Runner scope and lease audit",
    "serverGate",
    "auditRef",
    "idempotencyKey",
    "Worktree",
}

FORBIDDEN_RAW_CAPABILITY_TEXT = {
    "development",
    "implementation",
    "agent_runtime",
    "local_router",
    "project_management",
}

FORBIDDEN_RAW_DOM_LABELS = {
    "routeType",
    "targetDeviceId",
    "fromSessionId",
    "toSessionId",
    "serverGate",
    "auditRef",
    "idempotencyKey",
    "evidenceRefs",
    "testsOrChecks",
    "operatingRuleRefs",
    "commonRulesEvaluation",
}

COLLABORATION_FORBIDDEN_MAIN_KEYS = {
    "runnerId",
    "deviceId",
    "leaseId",
    "claimId",
    "sessionId",
    "leaseToken",
    "leaseTokenHash",
    "leaseProofHash",
    "endpoint",
    "path",
    "rawStatus",
    "statusCode",
    "capabilityCode",
    "scopeCode",
}

FORBIDDEN_VISIBLE_PATH_MARKERS = {
    "/Users/",
    "\\Users\\",
    "projects/company-knowledge-core/desktop-workbench-slice0",
}

REQUIRED_ROUTE_COPY = {
    "项目",
    "本机设备",
    "主 Agent",
    "岗位 Agent",
    "执行器 Runner",
    "任务结果记录",
    "审批/权限",
    "异常恢复",
    "路由链路",
    "路由已建好",
}

REQUIRED_PROJECT_CREATE_COPY = {
    "新建项目",
    "项目选择",
    "独立文件夹",
    "真知中枢注册项目记录",
    "项目名称",
    "项目文件夹",
    "项目来源",
    "新项目",
    "已有 Git",
    "V1 目标",
    "默认 Agent 队伍",
    "主 Agent",
    "产品 Agent",
    "研发 Agent",
    "测试 Agent",
    "执行设备",
    "本机设备",
    "项目创建包预览",
    "复制创建指令",
    "交给主 Agent 创建（需中枢授权）",
    "工作台项目选择器才会出现新项目",
}

FORBIDDEN_FAKE_PROJECT_CREATE_SUCCESS = {
    "已创建成功",
    "创建成功",
    "项目已创建",
    "已成功创建",
    "新项目已创建",
}

STATUS_TEXT_PATTERN = re.compile(r"const statusText = \{(?P<body>.*?)\n  \};", re.DOTALL)
STATUS_LABEL_PATTERN = re.compile(r"^\s*(?P<status>[A-Za-z_][A-Za-z0-9_]*)\s*:\s*\"(?P<label>[^\"]+)\"", re.MULTILINE)


class VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        normalized = " ".join(data.split())
        if normalized:
            self.parts.append(normalized)


def visible_text_from_html(html: str) -> str:
    parser = VisibleTextParser()
    parser.feed(html)
    return "\n".join(parser.parts)
STATUS_LIKE_EXTRA_KEYS = {"heartbeat", "serverGate"}


def is_status_like_key(key: str) -> bool:
    normalized = re.sub(r"[^a-z0-9]", "", key.lower())
    if normalized in {"statuslabel", "businessstatus"}:
        return False
    extra = {re.sub(r"[^a-z0-9]", "", value.lower()) for value in STATUS_LIKE_EXTRA_KEYS}
    return normalized == "status" or normalized.endswith("status") or normalized in extra


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_read_model(path: Path) -> dict[str, Any]:
    source = path.read_text(encoding="utf-8").strip()
    prefix = "window.ZHENZHI_DESKTOP_WORKBENCH_READ_MODEL = "
    if not source.startswith(prefix) or not source.endswith(";"):
        raise ValueError("workbench-read-model.js must assign one JSON object to window.ZHENZHI_DESKTOP_WORKBENCH_READ_MODEL")
    return json.loads(source[len(prefix) : -1])


def extract_shell_status_labels(shell_js: str) -> dict[str, str]:
    match = STATUS_TEXT_PATTERN.search(shell_js)
    if not match:
        return {}
    return {item.group("status"): item.group("label") for item in STATUS_LABEL_PATTERN.finditer(match.group("body"))}


def collect_status_values(value: Any) -> set[str]:
    statuses: set[str] = set()
    if isinstance(value, dict):
        for key, nested in value.items():
            if is_status_like_key(str(key)) and isinstance(nested, str) and nested:
                statuses.add(nested)
            statuses.update(collect_status_values(nested))
    elif isinstance(value, list):
        for nested in value:
            statuses.update(collect_status_values(nested))
    return statuses


def validate_shell_status_labels(shell_js: str, read_models: list[tuple[str, dict[str, Any]]]) -> list[str]:
    problems: list[str] = []
    labels = extract_shell_status_labels(shell_js)
    if not labels:
        return ["workbench-shell.js: statusText mapping is required"]

    for status, label in sorted(labels.items()):
        if label == status.replace("_", " ") or not any(ord(char) > 127 for char in label):
            problems.append(f"workbench-shell.js: statusText.{status} must be a Chinese label, got {label!r}")

    required_statuses: set[str] = set()
    for _name, read_model in read_models:
        required_statuses.update(collect_status_values(read_model))

    missing = required_statuses - set(labels)
    if missing:
        problems.append(f"workbench-shell.js: statusText missing read model statuses {sorted(missing)}")
    return problems


def render_shell_surfaces_with_node() -> dict[str, str]:
    script = r"""
const fs = require("fs");
const vm = require("vm");

const elements = new Map();
function element(id) {
  if (!elements.has(id)) {
    elements.set(id, {
      id,
      innerHTML: "",
      textContent: "",
      dataset: {},
      setAttribute() {},
      focus() {},
      addEventListener() {},
      querySelectorAll() { return []; }
    });
  }
  return elements.get(id);
}

const context = {
  window: {},
  document: { getElementById: element },
  console: { log() {}, error() {} }
};
context.window.window = context.window;
context.window.document = context.document;
vm.createContext(context);

for (const file of ["workbench-read-model.js", "workbench-live-read-model.js", "workbench-shell.js"]) {
  vm.runInContext(fs.readFileSync(file, "utf8"), context, { filename: file });
}

const readModel = context.window.ZHENZHI_DESKTOP_WORKBENCH_READ_MODEL || {};
const root = element("workbench-root");
const rendered = { home: root.innerHTML };
const surfaces = Array.from(new Set(["home"].concat(readModel.surfaces || [])));
for (const surface of surfaces) {
  context.window.renderZhenzhiDesktopWorkbench(surface);
  rendered[surface] = root.innerHTML;
}
rendered.__chrome = [
  element("project-select").innerHTML,
  element("project-title").textContent,
  element("project-summary").textContent,
  element("surface-nav").innerHTML,
  element("runtime-summary").innerHTML,
  element("runtime-summary").textContent,
  element("sync-state").textContent,
  element("package-boundary").textContent
].join("\\n");
process.stdout.write(JSON.stringify(rendered));
"""
    completed = subprocess.run(
        ["node", "-e", script],
        cwd=ARTIFACT_DIR,
        text=True,
        capture_output=True,
        timeout=10,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError((completed.stderr or completed.stdout or "unknown node render failure").strip())
    return json.loads(completed.stdout)


def find_raw_status_detail_dom(rendered_surfaces: dict[str, str], raw_status_values: set[str]) -> list[str]:
    values = sorted(value for value in raw_status_values if value)
    if not values:
        return []
    pattern = re.compile(r"<dd>\s*(?P<value>" + "|".join(re.escape(value) for value in values) + r")\s*</dd>")
    problems: list[str] = []
    for surface, html in sorted(rendered_surfaces.items()):
        found = sorted({match.group("value") for match in pattern.finditer(html)})
        for value in found:
            problems.append(f"workbench-shell.js:{surface}: raw status detail DOM must be localized, found <dd>{value}</dd>")
    return problems


def validate_shell_visible_user_copy(root: Path, rendered_surfaces: dict[str, str]) -> list[str]:
    problems: list[str] = []
    html = "\n".join(rendered_surfaces.values())
    shell_html = SHELL_HTML_PATH.read_text(encoding="utf-8")
    visible_text = visible_text_from_html(html) + "\n" + visible_text_from_html(shell_html)

    for phrase in sorted(FORBIDDEN_VISIBLE_COPY):
        if phrase in visible_text:
            problems.append(f"desktop workbench visible DOM must not expose user-hostile copy: {phrase!r}")

    for phrase in sorted(FORBIDDEN_INTERNAL_VISIBLE_TERMS):
        if phrase in visible_text:
            problems.append(f"desktop workbench visible DOM must not expose unexplained internal term: {phrase!r}")

    for phrase in sorted(FORBIDDEN_RAW_CAPABILITY_TEXT):
        if re.search(rf"(?<![A-Za-z0-9_]){re.escape(phrase)}(?![A-Za-z0-9_])", visible_text):
            problems.append(f"desktop workbench visible DOM must translate raw capability value: {phrase!r}")

    for label in sorted(FORBIDDEN_RAW_DOM_LABELS):
        if f"<dt>{label}</dt>" in html or f">{label}<" in html:
            problems.append(f"desktop workbench visible DOM must explain internal field label {label!r} in Chinese")

    for required in sorted(REQUIRED_ROUTE_COPY):
        if required not in html and required not in shell_html:
            problems.append(f"desktop workbench visible DOM missing route-chain copy {required!r}")

    if "<select" not in shell_html or "project-select" not in shell_html or "项目选择" not in shell_html:
        problems.append("workbench-shell.html: project selector is required for user-facing project context")
    if "真知公司知识核心" not in visible_text:
        problems.append("desktop workbench visible DOM must show the current project as a Chinese readable name")
    return problems


def collect_values_for_keys(value: Any, keys: set[str]) -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            if str(key) in keys:
                if isinstance(nested, list):
                    found.extend(str(item) for item in nested if item)
                elif nested:
                    found.append(str(nested))
            found.extend(collect_values_for_keys(nested, keys))
    elif isinstance(value, list):
        for nested in value:
            found.extend(collect_values_for_keys(nested, keys))
    return found


def validate_shell_visible_path_redaction(read_models: list[dict[str, Any]], rendered_surfaces: dict[str, str]) -> list[str]:
    problems: list[str] = []
    html = "\n".join(rendered_surfaces.values())
    visible_text = visible_text_from_html(html)
    raw_values: set[str] = set(FORBIDDEN_VISIBLE_PATH_MARKERS)
    raw_values.add(str(ROOT))
    for read_model in read_models:
        raw_values.update(collect_values_for_keys(read_model, {"workspace", "repositoryRefs", "repositoryScopes"}))

    for raw in sorted(value for value in raw_values if value):
        if raw in visible_text:
            problems.append(f"desktop workbench visible DOM must redact local/repository path text: {raw!r}")
        if raw.startswith("/") and raw in html:
            problems.append(f"desktop workbench rendered main DOM must not carry raw local path value: {raw!r}")
    return problems


def validate_project_create_entry(rendered_surfaces: dict[str, str], shell_html: str, shell_js: str) -> list[str]:
    problems: list[str] = []
    html = "\n".join(rendered_surfaces.values()) + "\n" + shell_html
    visible_text = visible_text_from_html(html)
    source_text = shell_html + "\n" + shell_js

    for required in sorted(REQUIRED_PROJECT_CREATE_COPY):
        if required not in visible_text and required not in source_text:
            problems.append(f"desktop workbench project create entry missing copy {required!r}")

    for forbidden in sorted(FORBIDDEN_FAKE_PROJECT_CREATE_SUCCESS):
        if forbidden in visible_text or forbidden in source_text:
            problems.append(f"desktop workbench project create entry must not claim project creation success: {forbidden!r}")

    for required in [
        "填写信息后生成创建包",
        "不直接创建项目",
        "不直接写文件",
        "注册 Runner",
        "建立任务链",
        "项目 -> 主 Agent -> 岗位 Agent -> 本机设备/执行器 -> 任务结果记录",
    ]:
        if required not in visible_text and required not in source_text:
            problems.append(f"desktop workbench project create entry missing controlled-flow marker {required!r}")

    if 'id="new-project-entry"' not in shell_html:
        problems.append("workbench-shell.html: missing top-level 新建项目 entry button")
    if 'id="project-create-command"' not in shell_js:
        problems.append("workbench-shell.js: missing project creation package preview target")
    if "disabled aria-disabled=\"true\"" not in shell_js:
        problems.append("workbench-shell.js: handoff button must be visibly gated instead of directly creating projects")
    return problems


def validate_shell_rendered_status_details(read_models: list[tuple[str, dict[str, Any]]], shell_js: str) -> list[str]:
    labels = extract_shell_status_labels(shell_js)
    raw_status_values = set(labels)
    for _name, read_model in read_models:
        raw_status_values.update(collect_status_values(read_model))
    try:
        rendered = render_shell_surfaces_with_node()
    except Exception as exc:  # pragma: no cover - surfaced by validator output
        return [f"workbench-shell.js: unable to render shell status details for validation: {exc}"]
    return find_raw_status_detail_dom(rendered, raw_status_values)


def load_front_matter(path: Path) -> dict[str, str]:
    source = path.read_text(encoding="utf-8")
    if not source.startswith("---\n"):
        return {}
    end = source.find("\n---", 4)
    if end == -1:
        return {}
    values: dict[str, str] = {}
    for line in source[4:end].splitlines():
        if ":" not in line or line.startswith(" "):
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"')
    return values


def validate_checklist(checklist: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    gates = checklist.get("gates")
    if not isinstance(gates, list) or not gates:
        return ["slice0-proof-checklist.json: gates must be a non-empty list"]

    categories = {str(gate.get("category") or "") for gate in gates}
    missing = REQUIRED_GATE_CATEGORIES - categories
    if missing:
        problems.append(f"slice0-proof-checklist.json: missing gate categories {sorted(missing)}")

    allowed_statuses = set(checklist.get("allowedStatuses") or [])
    for gate in gates:
        gate_id = str(gate.get("id") or "<missing>")
        status = str(gate.get("status") or "")
        if status not in allowed_statuses:
            problems.append(f"{gate_id}: status {status!r} is not allowed")
        if not gate.get("proofIntent"):
            problems.append(f"{gate_id}: proofIntent is required")
        if not gate.get("executableCheck"):
            problems.append(f"{gate_id}: executableCheck is required")
        if status in {"manual_required", "external_blocked"} and not gate.get("blocker"):
            problems.append(f"{gate_id}: blocker is required for {status}")
        if status in {"manual_required", "external_blocked"} and not gate.get("ownerNeeded"):
            problems.append(f"{gate_id}: ownerNeeded is required for {status}")
        if gate.get("launchBlocking") is not True:
            problems.append(f"{gate_id}: launchBlocking must be true for Slice 0 gates")

    fallback = checklist.get("fallbackDecisionRequest") or {}
    if "Tauri" not in str(fallback.get("requiredWhen") or ""):
        problems.append("slice0-proof-checklist.json: fallbackDecisionRequest must name Tauri failure trigger")
    if "Product Manager Agent" not in str(fallback.get("recipient") or ""):
        problems.append("slice0-proof-checklist.json: fallback recipient must include Product Manager Agent")
    if "Project Manager Agent" not in str(fallback.get("recipient") or ""):
        problems.append("slice0-proof-checklist.json: fallback recipient must include Project Manager Agent")
    return problems


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    if manifest.get("shellIndependentFrontend") is not True:
        problems.append("native-bridge-manifest.json: shellIndependentFrontend must be true")
    if manifest.get("centralApiIsSourceOfTruth") is not True:
        problems.append("native-bridge-manifest.json: centralApiIsSourceOfTruth must be true")

    commands = manifest.get("commands")
    if not isinstance(commands, list) or not commands:
        return problems + ["native-bridge-manifest.json: commands must be a non-empty list"]

    command_names = {str(command.get("name") or "") for command in commands}
    missing = REQUIRED_COMMANDS - command_names
    if missing:
        problems.append(f"native-bridge-manifest.json: missing commands {sorted(missing)}")

    for command in commands:
        name = str(command.get("name") or "<missing>")
        if not command.get("permission"):
            problems.append(f"{name}: permission is required")
        if not command.get("purpose"):
            problems.append(f"{name}: purpose is required")
        forbidden_writes = " ".join(str(item) for item in command.get("forbiddenWrites") or [])
        if name == "handoffRunnerPairingProof":
            if "central API-issued" not in str(command.get("purpose") or ""):
                problems.append(f"{name}: purpose must require central API-issued proof")
            if "user confirmation" not in str(command.get("purpose") or ""):
                problems.append(f"{name}: purpose must require user confirmation")
        if name in {"getRunnerPairingDiagnostics", "handoffRunnerPairingProof"}:
            lower_forbidden = forbidden_writes.lower()
            for required_phrase in ["lease", "taskresult", "agentrun"]:
                if required_phrase not in lower_forbidden.replace(" ", ""):
                    problems.append(f"{name}: forbiddenWrites must block {required_phrase}")

    forbidden_mutations = set(manifest.get("forbiddenLocalRunnerMutations") or [])
    missing_forbidden = FORBIDDEN_LOCAL_MUTATION_WORDS - forbidden_mutations - {"direct task lease update"}
    if missing_forbidden:
        problems.append(f"native-bridge-manifest.json: missing forbiddenLocalRunnerMutations {sorted(missing_forbidden)}")
    return problems


def validate_frontend_source(source: str) -> list[str]:
    problems: list[str] = []
    for marker in sorted(FORBIDDEN_FRONTEND_MARKERS):
        if marker in source:
            problems.append(f"shared-frontend-foundation.ts: shell-specific marker found: {marker}")
    for required in [
        "WorkbenchShellAdapter",
        "NativeBridgePort",
        "NativeBridgeCommand",
        "DesktopWorkbenchReadModel",
        "WorkbenchSurface",
        "WorkbenchPanelState",
        "createWorkbenchFoundation",
        "forbiddenLocalRunnerMutations",
    ]:
        if required not in source:
            problems.append(f"shared-frontend-foundation.ts: missing {required}")
    return problems


def validate_shell_files(root: Path) -> list[str]:
    problems: list[str] = []
    for filename in sorted(REQUIRED_SHELL_FILES):
        path = ARTIFACT_DIR / filename
        if not path.exists():
            problems.append(f"missing desktop workbench shell artifact: {path.relative_to(root)}")
    if problems:
        return problems

    html = SHELL_HTML_PATH.read_text(encoding="utf-8")
    shell_js = SHELL_JS_PATH.read_text(encoding="utf-8")
    css = SHELL_CSS_PATH.read_text(encoding="utf-8")

    for required in ["workbench-read-model.js", "workbench-live-read-model.js", "workbench-shell.js", "workbench-shell.css", "workbench-root", "surface-nav", "project-select", "项目选择", "真知公司知识核心", "new-project-entry", "新建项目", "独立文件夹"]:
        if required not in html:
            problems.append(f"workbench-shell.html: missing {required}")
    if 'lang="zh-CN"' not in html:
        problems.append("workbench-shell.html: must declare zh-CN language")
    if "真知 V1 Agent 工作台" not in html:
        problems.append("workbench-shell.html: must use Chinese V1 workbench title")
    if html.find("workbench-read-model.js") > html.find("workbench-live-read-model.js"):
        problems.append("workbench-shell.html: live read model must load after baseline read model")
    if html.find("workbench-live-read-model.js") > html.find("workbench-shell.js"):
        problems.append("workbench-shell.html: shell must run after live read model")
    for forbidden in ["https://", "http://", "cdn.", "node_modules"]:
        if forbidden in html:
            problems.append(f"workbench-shell.html: external dependency not allowed in local slice: {forbidden}")
    for required in [
        "renderZhenzhiDesktopWorkbench",
        "permissionGatedActions",
        "runnerLeases",
        "runtimeMetrics",
        "agentMessages",
        "targetDeviceId",
        "settingsSecurity",
        "recovery",
        "sourceOfTruth",
        "submitted",
        "已提交，待评审",
        "缺少输出引用",
        "缺少证据入口",
        "缺少测试/检查记录",
        "缺少运行规则记录",
        "缺少公共规则自检",
        "routeType",
        "taskPackages",
        "worktrees",
        "serverGate",
        "auditRef",
        "idempotencyKey",
        "problemRunnerLeases",
        "problemTasks",
        "V1 只有本机",
        "路由已建好",
        "数据来自中央状态记录",
        "projectCreateEntry",
        "collaborationWorkbench",
        "renderCollaborationWorkbench",
        "协作设备",
        "接入与授权",
        "设备与执行器",
        "任务路由",
        "查看技术详情/证据",
        "项目创建包预览",
        "复制创建指令",
        "交给主 Agent 创建（需中枢授权）",
        "不直接写文件",
    ]:
        if required not in shell_js:
            problems.append(f"workbench-shell.js: missing render coverage marker {required}")
    for required in ["grid-template-columns", "minmax", "@media", "status-strip", "stage-strip", "warning-list", "meta-grid", "project-picker", "project-create-grid", "project-create-preview"]:
        if required not in css:
            problems.append(f"workbench-shell.css: missing responsive layout marker {required}")
    return problems


def validate_panel(panel: dict[str, Any], context: str) -> list[str]:
    problems: list[str] = []
    for field in ["id", "title", "status", "owner", "nextAction", "fallbackState", "evidenceRefs"]:
        if field not in panel:
            problems.append(f"{context}: missing {field}")
    if not isinstance(panel.get("evidenceRefs"), list) or not panel.get("evidenceRefs"):
        problems.append(f"{context}: evidenceRefs must be a non-empty list")
    return problems


def validate_live_read_model(read_model: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    if read_model.get("runtimeReadModelKind") != "real-v1-runtime-read-model":
        problems.append("workbench-live-read-model.js: runtimeReadModelKind must be real-v1-runtime-read-model")
    if read_model.get("fixture") is not False:
        problems.append("workbench-live-read-model.js: fixture must be false")
    if read_model.get("sourceOfTruth") != "central-api-read-model":
        problems.append("workbench-live-read-model.js: sourceOfTruth must be central-api-read-model")
    if "runtime-monitor" not in set(read_model.get("surfaces") or []):
        problems.append("workbench-live-read-model.js: runtime-monitor surface is required")
    if "agent-ring-console" not in set(read_model.get("surfaces") or []):
        problems.append("workbench-live-read-model.js: agent-ring-console surface is required for 协作设备")

    metrics = read_model.get("runtimeMetrics") or {}
    expected_metric_values = {
        "onlineDeviceCount": 1,
        "onlineAgentSessionCount": 4,
        "productFinalAccepted": True,
    }
    for key, expected in expected_metric_values.items():
        if metrics.get(key) != expected:
            problems.append(f"workbench-live-read-model.js: runtimeMetrics.{key} must be {expected!r}")
    if int(metrics.get("messagesWithTargetDeviceId") or 0) < 1:
        problems.append("workbench-live-read-model.js: messagesWithTargetDeviceId must be at least 1")
    if int(metrics.get("openTaskCount") or 0) != 0:
        problems.append("workbench-live-read-model.js: openTaskCount must be 0 for accepted V1")

    devices = read_model.get("devices") or []
    if not any(str(item.get("deviceId") or "") == "device.local" for item in devices if isinstance(item, dict)):
        problems.append("workbench-live-read-model.js: devices must include device.local")
    sessions = read_model.get("agentSessions") or []
    required_agents = {"agent.company.project-manager", "agent.company.product-manager", "agent.company.development", "agent.company.test"}
    session_agents = {str(item.get("agentId") or "") for item in sessions if isinstance(item, dict)}
    missing_agents = required_agents - session_agents
    if missing_agents:
        problems.append(f"workbench-live-read-model.js: missing Agent sessions {sorted(missing_agents)}")

    messages = read_model.get("agentMessages") or []
    if not any(str(((item.get("routing") or {}) if isinstance(item, dict) else {}).get("targetDeviceId") or "") == "device.local" for item in messages):
        problems.append("workbench-live-read-model.js: Agent messages must include targetDeviceId device.local")
    if not read_model.get("taskFlow"):
        problems.append("workbench-live-read-model.js: taskFlow must be populated from real tasks")
    if not read_model.get("taskResults"):
        problems.append("workbench-live-read-model.js: taskResults must be populated from real TaskResult files")
    acceptance = read_model.get("acceptanceEvidence") or []
    if not any("产品最终验收证据" in str(item.get("title") or "") and str(item.get("status") or "") == "ready" for item in acceptance if isinstance(item, dict)):
        problems.append("workbench-live-read-model.js: 产品最终验收证据 must be ready")
    problems.extend(validate_collaboration_workbench(read_model, "workbench-live-read-model.js"))
    return problems


def validate_workbench_agent_task_chain(root: Path) -> list[str]:
    problems: list[str] = []
    task_dir = root / "projects" / "company-knowledge-core" / "tasks"
    for task_id, assignee in REQUIRED_WORKBENCH_TASK_CHAIN.items():
        path = task_dir / f"{task_id}.md"
        if not path.exists():
            problems.append(f"desktop workbench agent chain missing task: {path.relative_to(root)}")
            continue
        front_matter = load_front_matter(path)
        if front_matter.get("taskId") != task_id:
            problems.append(f"{path.relative_to(root)}: taskId must be {task_id}")
        if front_matter.get("assignee") != assignee:
            problems.append(f"{path.relative_to(root)}: assignee must be {assignee}")
        if not front_matter.get("requester"):
            problems.append(f"{path.relative_to(root)}: requester is required")

    rules_path = root / "docs" / "agent-team" / "common-agent-operating-rules.md"
    project_manager_path = root / "agents" / "agent.company.project-manager.md"
    rules_text = rules_path.read_text(encoding="utf-8") if rules_path.exists() else ""
    pm_text = project_manager_path.read_text(encoding="utf-8") if project_manager_path.exists() else ""
    for required in ["主线程代工隔离", "未验收草稿", "Design 方案", "Product 评审", "Development 实现", "Test 验收"]:
        if required not in rules_text:
            problems.append(f"{rules_path.relative_to(root)}: missing main-thread bypass guard {required}")
    if "unaccepted draft" not in pm_text and "未验收草稿" not in pm_text:
        problems.append(f"{project_manager_path.relative_to(root)}: missing PM unaccepted draft guard")
    return problems


def collect_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, nested in value.items():
            keys.add(str(key))
            keys.update(collect_keys(nested))
    elif isinstance(value, list):
        for nested in value:
            keys.update(collect_keys(nested))
    return keys


def has_chinese_text(value: Any) -> bool:
    return any(ord(char) > 127 for char in str(value or ""))


def validate_collaboration_action(action: Any, context: str) -> list[str]:
    problems: list[str] = []
    if not isinstance(action, dict):
        return [f"{context}: primaryAction must be an object"]
    if not has_chinese_text(action.get("label")):
        problems.append(f"{context}: action label must be Chinese readable")
    if action.get("serverGate") != "required":
        problems.append(f"{context}: action must require server gate")
    permission = str(action.get("permission") or "")
    if permission in FORBIDDEN_EXECUTION_CONTROL_PERMISSIONS:
        problems.append(f"{context}: action must not expose execution-control permission {permission!r}")
    if not str(action.get("idempotencyKey") or "") and "view" not in permission:
        problems.append(f"{context}: action must carry an idempotencyKey for write/request entries")
    if not str(action.get("auditRef") or "") and "view" not in permission and "disabledReason" not in action:
        problems.append(f"{context}: action must expose audit boundary for write/request entries")
    return problems


def validate_registration_entries(entries: Any, source_name: str) -> list[str]:
    problems: list[str] = []
    if not isinstance(entries, list):
        return [f"{source_name}: collaborationWorkbench.registrationEntries must be a list"]
    titles = {str(item.get("title") or "") for item in entries if isinstance(item, dict)}
    missing_titles = REQUIRED_REGISTRATION_ENTRY_TITLES - titles
    if missing_titles:
        problems.append(f"{source_name}: registrationEntries missing {sorted(missing_titles)}")
    api_paths = {str(item.get("apiPath") or "") for item in entries if isinstance(item, dict)}
    missing_paths = REQUIRED_REGISTRATION_API_PATHS - api_paths
    if missing_paths:
        problems.append(f"{source_name}: registrationEntries missing API paths {sorted(missing_paths)}")
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            problems.append(f"{source_name}: registrationEntries[{index}] must be an object")
            continue
        for field in ["title", "description", "statusLabel", "apiPath", "confirmationLabel", "guardrailLabel", "auditLabel"]:
            if not entry.get(field):
                problems.append(f"{source_name}: registrationEntries[{index}] missing {field}")
        for field in ["title", "description", "statusLabel", "confirmationLabel", "guardrailLabel", "auditLabel"]:
            if not has_chinese_text(entry.get(field)):
                problems.append(f"{source_name}: registrationEntries[{index}].{field} must be Chinese readable")
        if "不直接" not in str(entry.get("guardrailLabel") or "") and "不会" not in str(entry.get("guardrailLabel") or "") and "只登记" not in str(entry.get("guardrailLabel") or "") and "未授权" not in str(entry.get("guardrailLabel") or ""):
            problems.append(f"{source_name}: registrationEntries[{index}].guardrailLabel must state a non-execution boundary")
        problems.extend(validate_collaboration_action(entry.get("primaryAction"), f"{source_name}: registrationEntries[{index}]"))
    return problems


def validate_collaboration_workbench(read_model: dict[str, Any], source_name: str = "workbench-read-model.js") -> list[str]:
    problems: list[str] = []
    model = read_model.get("collaborationWorkbench")
    if not isinstance(model, dict):
        return [f"{source_name}: collaborationWorkbench is required for Phase 2 协作设备"]

    missing = REQUIRED_COLLABORATION_SECTIONS - set(model)
    if missing:
        problems.append(f"{source_name}: collaborationWorkbench missing sections {sorted(missing)}")
    if model.get("entryLabel") != "协作设备":
        problems.append(f"{source_name}: collaborationWorkbench.entryLabel must be 协作设备")
    for field in ["projectJoinPolicyLabel", "availableDeviceCountLabel", "activeRouteSummary"]:
        if not has_chinese_text(model.get(field)):
            problems.append(f"{source_name}: collaborationWorkbench.{field} must be Chinese readable")
    if "readOnlyNotice" not in model or not has_chinese_text(model.get("readOnlyNotice")):
        problems.append(f"{source_name}: collaborationWorkbench.readOnlyNotice must describe readonly degradation in Chinese")

    problems.extend(validate_registration_entries(model.get("registrationEntries"), source_name))

    devices = model.get("devices")
    if not isinstance(devices, list) or len(devices) < 2:
        problems.append(f"{source_name}: collaborationWorkbench.devices must include at least two colleague devices")
    else:
        statuses = set()
        for index, device in enumerate(devices):
            if not isinstance(device, dict):
                problems.append(f"{source_name}: collaborationWorkbench.devices[{index}] must be an object")
                continue
            missing_fields = REQUIRED_COLLABORATION_DEVICE_FIELDS - set(device)
            if missing_fields:
                problems.append(f"{source_name}: collaborationWorkbench.devices[{index}] missing {sorted(missing_fields)}")
            for field in ["displayName", "ownerLabel", "availabilityLabel", "authorizationSummary", "currentTaskLabel", "lastSeenLabel"]:
                if not has_chinese_text(device.get(field)):
                    problems.append(f"{source_name}: collaborationWorkbench.devices[{index}].{field} must be Chinese readable")
            if str(device.get("displayName") or "").startswith(("runner.", "device.", "session.")):
                problems.append(f"{source_name}: collaborationWorkbench.devices[{index}].displayName must not fall back to an internal id")
            statuses.add(str(device.get("status") or ""))
            problems.extend(validate_collaboration_action(device.get("primaryAction"), f"{source_name}: collaborationWorkbench.devices[{index}]"))
        if not ({"ready", "pending_authorization", "offline"} <= statuses):
            problems.append(f"{source_name}: collaborationWorkbench.devices must cover ready, pending authorization, and offline states")

    pairing = model.get("pairingRequests")
    if not isinstance(pairing, list) or not pairing:
        problems.append(f"{source_name}: collaborationWorkbench.pairingRequests must include a pairing/authorization request")
    else:
        for index, request in enumerate(pairing):
            if isinstance(request, dict):
                for field in ["displayTitle", "requesterLabel", "deviceLabel", "statusLabel", "scopeSummary"]:
                    if not has_chinese_text(request.get(field)):
                        problems.append(f"{source_name}: collaborationWorkbench.pairingRequests[{index}].{field} must be Chinese readable")
                problems.extend(validate_collaboration_action(request.get("primaryAction"), f"{source_name}: collaborationWorkbench.pairingRequests[{index}]"))

    routes = model.get("routeBoard")
    if not isinstance(routes, list) or len(routes) < 2:
        problems.append(f"{source_name}: collaborationWorkbench.routeBoard must include multiple task routes")
    else:
        route_statuses = set()
        for index, route in enumerate(routes):
            if not isinstance(route, dict):
                problems.append(f"{source_name}: collaborationWorkbench.routeBoard[{index}] must be an object")
                continue
            missing_fields = REQUIRED_COLLABORATION_ROUTE_FIELDS - set(route)
            if missing_fields:
                problems.append(f"{source_name}: collaborationWorkbench.routeBoard[{index}] missing {sorted(missing_fields)}")
            for field in REQUIRED_COLLABORATION_ROUTE_FIELDS:
                if not has_chinese_text(route.get(field)):
                    problems.append(f"{source_name}: collaborationWorkbench.routeBoard[{index}].{field} must be Chinese readable")
            route_statuses.add(str(route.get("status") or ""))
        if not ({"processing", "pending_authorization", "writeback_failed"} <= route_statuses):
            problems.append(f"{source_name}: collaborationWorkbench.routeBoard must cover running, authorization, and writeback failure states")

    recovery = model.get("recoveryItems")
    if not isinstance(recovery, list) or len(recovery) < 2:
        problems.append(f"{source_name}: collaborationWorkbench.recoveryItems must cover offline/permission recovery")
    else:
        for index, item in enumerate(recovery):
            if isinstance(item, dict):
                for field in ["title", "statusLabel", "impactLabel", "ownerLabel", "displayMessage", "nextAction"]:
                    if not has_chinese_text(item.get(field)):
                        problems.append(f"{source_name}: collaborationWorkbench.recoveryItems[{index}].{field} must be Chinese readable")

    audits = model.get("auditSummaries")
    if not isinstance(audits, list) or not audits:
        problems.append(f"{source_name}: collaborationWorkbench.auditSummaries must include user-readable operation records")
    else:
        for index, item in enumerate(audits):
            if isinstance(item, dict):
                for field in ["actorLabel", "actionLabel", "targetLabel", "impactLabel", "resultLabel"]:
                    if not has_chinese_text(item.get(field)):
                        problems.append(f"{source_name}: collaborationWorkbench.auditSummaries[{index}].{field} must be Chinese readable")

    technical = model.get("technicalDetails")
    if not isinstance(technical, list) or not technical:
        problems.append(f"{source_name}: collaborationWorkbench.technicalDetails must include folded redacted evidence details")
    else:
        technical_keys = collect_keys(technical)
        forbidden_keys = COLLABORATION_FORBIDDEN_MAIN_KEYS & technical_keys
        if forbidden_keys:
            problems.append(f"{source_name}: collaborationWorkbench.technicalDetails must use redacted labels, not raw keys {sorted(forbidden_keys)}")
        for index, item in enumerate(technical):
            redacted = str((item or {}).get("redactedValue") or "")
            if not redacted or "***" not in redacted:
                problems.append(f"{source_name}: collaborationWorkbench.technicalDetails[{index}] must contain a redacted value")

    main_keys = collect_keys({key: value for key, value in model.items() if key != "technicalDetails"})
    forbidden_main = COLLABORATION_FORBIDDEN_MAIN_KEYS & main_keys
    if forbidden_main:
        problems.append(f"{source_name}: collaborationWorkbench main model must not expose raw internal keys {sorted(forbidden_main)}")
    return problems


def validate_read_model(read_model: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    if read_model.get("schemaVersion") != "desktop-workbench-read-model.v1":
        problems.append("workbench-read-model.js: schemaVersion must be desktop-workbench-read-model.v1")
    if read_model.get("sourceOfTruth") != "central-api-read-model":
        problems.append("workbench-read-model.js: sourceOfTruth must be central-api-read-model")
    if read_model.get("staleStatePolicy") != "show-safe-fallback-not-current":
        problems.append("workbench-read-model.js: staleStatePolicy must prevent stale current-state display")

    surfaces = set(read_model.get("surfaces") or [])
    missing_surfaces = REQUIRED_WORKBENCH_SURFACES - surfaces
    if missing_surfaces:
        problems.append(f"workbench-read-model.js: missing surfaces {sorted(missing_surfaces)}")

    missing_sections = REQUIRED_READ_MODEL_SECTIONS - set(read_model)
    if missing_sections:
        problems.append(f"workbench-read-model.js: missing sections {sorted(missing_sections)}")

    runtime = read_model.get("localRuntime") or {}
    if runtime.get("kind") != "static-file-workbench":
        problems.append("workbench-read-model.js: localRuntime.kind must be static-file-workbench")
    boundary = " ".join(str(value) for value in runtime.get("nextPackagingBoundary") or [])
    boundary_text = boundary + " " + str(runtime.get("packagingBoundary") or "")
    for required, aliases in {
        "Tauri": ["Tauri"],
        "Electron": ["Electron"],
        "Mac": ["Mac"],
        "Windows": ["Windows"],
        "secure storage": ["secure storage", "安全存储"],
    }.items():
        if not any(alias in boundary_text for alias in aliases):
            problems.append(f"workbench-read-model.js: packaging boundary must name {required}")

    platform_copy = read_model.get("platformCopy") or {}
    for platform, required_phrase in {"mac": "Keychain", "windows": "Windows Credential Manager"}.items():
        secure_storage = str((platform_copy.get(platform) or {}).get("secureStorage") or "")
        if required_phrase not in secure_storage:
            problems.append(f"workbench-read-model.js: {platform} secure storage copy must name {required_phrase}")

    seen_statuses: set[str] = set()
    for section in ["home", "projectProgress", "agentCurrentWork", "approvals", "notifications", "recovery", "settingsSecurity"]:
        values = read_model.get(section)
        if not isinstance(values, list) or not values:
            problems.append(f"workbench-read-model.js: {section} must be a non-empty list")
            continue
        for index, panel in enumerate(values):
            if isinstance(panel, dict):
                seen_statuses.add(str(panel.get("status") or ""))
                problems.extend(validate_panel(panel, f"workbench-read-model.js:{section}[{index}]"))

    runner_leases = read_model.get("runnerLeases")
    if not isinstance(runner_leases, list) or not runner_leases:
        problems.append("workbench-read-model.js: runnerLeases must be a non-empty list")
    else:
        for index, lease in enumerate(runner_leases):
            if not isinstance(lease, dict):
                problems.append(f"workbench-read-model.js: runnerLeases[{index}] must be an object")
                continue
            seen_statuses.add(str(lease.get("status") or ""))
            if "scopeAudit" not in lease:
                problems.append(f"workbench-read-model.js: runnerLeases[{index}] missing scopeAudit")
            else:
                problems.extend(validate_panel(lease["scopeAudit"], f"workbench-read-model.js:runnerLeases[{index}].scopeAudit"))

    history_statuses = {str(item.get("status") or "") for item in read_model.get("runnerHistory") or [] if isinstance(item, dict)}
    for required in ["active", "completed", "failed", "stale", "retried", "escalated"]:
        if required not in history_statuses:
            problems.append(f"workbench-read-model.js: runnerHistory missing {required}")

    missing_statuses = REQUIRED_PANEL_STATUSES - seen_statuses
    if missing_statuses:
        problems.append(f"workbench-read-model.js: missing core statuses {sorted(missing_statuses)}")

    actions = read_model.get("permissionGatedActions")
    if not isinstance(actions, list) or not actions:
        problems.append("workbench-read-model.js: permissionGatedActions must be a non-empty list")
    else:
        for action in actions:
            if action.get("serverGate") != "required":
                problems.append(f"{action.get('id', '<missing>')}: serverGate must be required")
            if not action.get("idempotencyKey"):
                problems.append(f"{action.get('id', '<missing>')}: idempotencyKey is required")
            if not action.get("auditRef"):
                problems.append(f"{action.get('id', '<missing>')}: auditRef is required")
    problems.extend(validate_collaboration_workbench(read_model, "workbench-read-model.js"))
    return problems


def validate(root: Path = ROOT) -> list[str]:
    global ARTIFACT_DIR, CHECKLIST_PATH, MANIFEST_PATH, FRONTEND_PATH
    global SHELL_HTML_PATH, SHELL_CSS_PATH, SHELL_JS_PATH, READ_MODEL_PATH, LIVE_READ_MODEL_PATH
    ARTIFACT_DIR = root / "projects" / "company-knowledge-core" / "desktop-workbench-slice0"
    CHECKLIST_PATH = ARTIFACT_DIR / "slice0-proof-checklist.json"
    MANIFEST_PATH = ARTIFACT_DIR / "native-bridge-manifest.json"
    FRONTEND_PATH = ARTIFACT_DIR / "shared-frontend-foundation.ts"
    SHELL_HTML_PATH = ARTIFACT_DIR / "workbench-shell.html"
    SHELL_CSS_PATH = ARTIFACT_DIR / "workbench-shell.css"
    SHELL_JS_PATH = ARTIFACT_DIR / "workbench-shell.js"
    READ_MODEL_PATH = ARTIFACT_DIR / "workbench-read-model.js"
    LIVE_READ_MODEL_PATH = ARTIFACT_DIR / "workbench-live-read-model.js"

    problems: list[str] = []
    for path in [CHECKLIST_PATH, MANIFEST_PATH, FRONTEND_PATH, SHELL_HTML_PATH, SHELL_CSS_PATH, SHELL_JS_PATH, READ_MODEL_PATH, LIVE_READ_MODEL_PATH]:
        if not path.exists():
            problems.append(f"missing artifact: {path.relative_to(root)}")
    if problems:
        return problems

    base_read_model = load_read_model(READ_MODEL_PATH)
    live_read_model = load_read_model(LIVE_READ_MODEL_PATH)
    shell_js = SHELL_JS_PATH.read_text(encoding="utf-8")

    problems.extend(validate_checklist(load_json(CHECKLIST_PATH)))
    problems.extend(validate_manifest(load_json(MANIFEST_PATH)))
    problems.extend(validate_frontend_source(FRONTEND_PATH.read_text(encoding="utf-8")))
    problems.extend(validate_shell_files(root))
    problems.extend(validate_shell_status_labels(shell_js, [("workbench-read-model.js", base_read_model), ("workbench-live-read-model.js", live_read_model)]))
    problems.extend(validate_shell_rendered_status_details([("workbench-read-model.js", base_read_model), ("workbench-live-read-model.js", live_read_model)], shell_js))
    try:
        rendered_surfaces = render_shell_surfaces_with_node()
    except Exception as exc:  # pragma: no cover - surfaced by validator output
        problems.append(f"workbench-shell.js: unable to render shell visible copy for validation: {exc}")
    else:
        problems.extend(validate_shell_visible_user_copy(root, rendered_surfaces))
        problems.extend(validate_shell_visible_path_redaction([base_read_model, live_read_model], rendered_surfaces))
        problems.extend(validate_project_create_entry(rendered_surfaces, SHELL_HTML_PATH.read_text(encoding="utf-8"), shell_js))
    problems.extend(validate_read_model(base_read_model))
    problems.extend(validate_live_read_model(live_read_model))
    problems.extend(validate_workbench_agent_task_chain(root))
    return problems


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT
    problems = validate(root)
    if problems:
        for problem in problems:
            print(problem)
        return 1
    print("desktop workbench slice0 artifacts: passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
