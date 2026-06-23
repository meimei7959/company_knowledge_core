import importlib.util
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = REPO_ROOT / "scripts" / "validate_desktop_workbench_slice0.py"
ARTIFACT_DIR = REPO_ROOT / "projects" / "company-knowledge-core" / "desktop-workbench-slice0"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_desktop_workbench_slice0", VALIDATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class DesktopWorkbenchSlice0Tests(unittest.TestCase):
    def test_slice0_artifacts_validate(self) -> None:
        validator = load_validator()
        self.assertEqual([], validator.validate(REPO_ROOT))

    def test_workbench_read_model_covers_desktop_client_core_states(self) -> None:
        validator = load_validator()
        read_model = validator.load_read_model(ARTIFACT_DIR / "workbench-read-model.js")

        self.assertEqual("central-api-read-model", read_model["sourceOfTruth"])
        for section in [
            "projectProgress",
            "agentCurrentWork",
            "runnerLeases",
            "approvals",
            "notifications",
            "recovery",
            "settingsSecurity",
        ]:
            self.assertTrue(read_model[section], section)

        history_statuses = {item["status"] for item in read_model["runnerHistory"]}
        self.assertTrue({"active", "completed", "failed", "stale", "retried", "escalated"} <= history_statuses)

    def test_live_workbench_read_model_uses_real_v1_runtime_state(self) -> None:
        validator = load_validator()
        read_model = validator.load_read_model(ARTIFACT_DIR / "workbench-live-read-model.js")

        self.assertEqual("real-v1-runtime-read-model", read_model["runtimeReadModelKind"])
        self.assertFalse(read_model["fixture"])
        self.assertIn("runtime-monitor", read_model["surfaces"])
        self.assertEqual(0, read_model["runtimeMetrics"]["openTaskCount"])
        self.assertEqual(1, read_model["runtimeMetrics"]["onlineDeviceCount"])
        self.assertEqual(4, read_model["runtimeMetrics"]["onlineAgentSessionCount"])
        self.assertTrue(read_model["runtimeMetrics"]["productFinalAccepted"])
        self.assertGreaterEqual(read_model["runtimeMetrics"]["messagesWithTargetDeviceId"], 1)
        self.assertTrue(any(item["deviceId"] == "device.local" for item in read_model["devices"]))
        self.assertTrue(any(item["routing"]["targetDeviceId"] == "device.local" for item in read_model["agentMessages"]))
        self.assertTrue(any(item["title"] == "产品最终验收证据" and item["status"] == "ready" for item in read_model["acceptanceEvidence"]))

    def test_workbench_actions_are_server_gated_and_idempotent(self) -> None:
        validator = load_validator()
        read_model = validator.load_read_model(ARTIFACT_DIR / "workbench-read-model.js")

        for action in read_model["permissionGatedActions"]:
            self.assertEqual("required", action["serverGate"])
            self.assertTrue(action["idempotencyKey"].startswith("desktop:"))
            self.assertIn("audit.", action["auditRef"])

    def test_static_shell_declares_packaging_boundary(self) -> None:
        validator = load_validator()
        read_model = validator.load_read_model(ARTIFACT_DIR / "workbench-read-model.js")
        runtime = read_model["localRuntime"]

        self.assertEqual("static-file-workbench", runtime["kind"])
        self.assertIn("Tauri", runtime["packagingBoundary"])
        self.assertIn("Electron", runtime["packagingBoundary"])
        self.assertIn("Mac", " ".join(runtime["nextPackagingBoundary"]))
        self.assertIn("Windows", " ".join(runtime["nextPackagingBoundary"]))

    def test_shell_uses_live_read_model_and_chinese_status_semantics(self) -> None:
        validator = load_validator()
        html = (ARTIFACT_DIR / "workbench-shell.html").read_text(encoding="utf-8")
        shell_js = (ARTIFACT_DIR / "workbench-shell.js").read_text(encoding="utf-8")

        self.assertIn('lang="zh-CN"', html)
        self.assertIn('id="project-select"', html)
        self.assertIn("项目选择", html)
        self.assertIn('id="new-project-entry"', html)
        self.assertIn("新建项目", html)
        self.assertIn("独立文件夹", html)
        self.assertIn("真知公司知识核心", html)
        self.assertLess(html.index("workbench-read-model.js"), html.index("workbench-live-read-model.js"))
        self.assertLess(html.index("workbench-live-read-model.js"), html.index("workbench-shell.js"))
        self.assertIn("real-v1-runtime-read-model", shell_js)
        self.assertIn("projectCreateEntry", shell_js)
        self.assertIn("项目创建包预览", shell_js)
        self.assertIn("复制创建指令", shell_js)
        self.assertIn("交给主 Agent 创建（需中枢授权）", shell_js)
        self.assertIn("不直接写文件", shell_js)
        self.assertNotIn("已创建成功", shell_js)
        self.assertIn('submitted: "已提交，待评审"', shell_js)
        status_labels = validator.extract_shell_status_labels(shell_js)
        self.assertEqual("已关闭", status_labels["done"])
        self.assertEqual("离线", status_labels["offline"])
        self.assertEqual("重试已登记", status_labels["retried"])
        self.assertEqual("已升级处理", status_labels["escalated"])
        self.assertEqual("已接受", status_labels["accepted"])
        self.assertEqual("需服务端授权", status_labels["required"])
        self.assertEqual([], validator.validate_shell_status_labels(shell_js, [
            ("workbench-read-model.js", validator.load_read_model(ARTIFACT_DIR / "workbench-read-model.js")),
            ("workbench-live-read-model.js", validator.load_read_model(ARTIFACT_DIR / "workbench-live-read-model.js")),
        ]))
        self.assertIn("不等于已验收", shell_js)
        self.assertIn("缺少输出引用", shell_js)
        self.assertIn("缺少证据入口", shell_js)
        self.assertIn("缺少测试/检查记录", shell_js)
        self.assertIn("缺少运行规则记录", shell_js)
        self.assertIn("缺少公共规则自检", shell_js)

    def test_shell_localizes_status_detail_dom_values(self) -> None:
        validator = load_validator()
        shell_js = (ARTIFACT_DIR / "workbench-shell.js").read_text(encoding="utf-8")
        read_models = [
            ("workbench-read-model.js", validator.load_read_model(ARTIFACT_DIR / "workbench-read-model.js")),
            ("workbench-live-read-model.js", validator.load_read_model(ARTIFACT_DIR / "workbench-live-read-model.js")),
        ]

        self.assertIn("function displayValue", shell_js)
        self.assertIn("<dd>${escapeHtml(displayValue(item.label, item.value))}</dd>", shell_js)
        self.assertEqual(
            ["workbench-shell.js:synthetic: raw status detail DOM must be localized, found <dd>offline</dd>"],
            validator.find_raw_status_detail_dom({"synthetic": "<dl><dd>offline</dd><dd>已关闭</dd></dl>"}, {"offline", "done"}),
        )
        self.assertEqual([], validator.validate_shell_rendered_status_details(read_models, shell_js))

    def test_shell_separates_permissions_recovery_and_device_routing(self) -> None:
        shell_js = (ARTIFACT_DIR / "workbench-shell.js").read_text(encoding="utf-8")

        for marker in [
            "协作设备",
            "collaborationWorkbench",
            "renderCollaborationWorkbench",
            "接入与授权",
            "设备与执行器",
            "任务路由",
            "查看技术详情/证据",
            "审批/权限",
            "permissionGatedActions",
            "serverGate",
            "auditRef",
            "idempotencyKey",
            "异常恢复",
            "problemRunnerLeases",
            "problemTasks",
            "过期租约",
            "失败执行器",
            "离线心跳",
            "routeType",
            "targetDeviceId",
            "V1 只有本机",
            "路由链路",
            "路由已建好",
            "数据来自中央状态记录",
            "主 Agent",
            "岗位 Agent",
            "任务结果记录",
        ]:
            self.assertIn(marker, shell_js)

    def test_phase2_collaboration_read_model_is_user_readable(self) -> None:
        validator = load_validator()
        for filename in ["workbench-read-model.js", "workbench-live-read-model.js"]:
            read_model = validator.load_read_model(ARTIFACT_DIR / filename)
            model = read_model["collaborationWorkbench"]

            self.assertEqual("协作设备", model["entryLabel"])
            self.assertGreaterEqual(len(model["devices"]), 2)
            self.assertGreaterEqual(len(model["routeBoard"]), 2)
            self.assertTrue(model["pairingRequests"])
            self.assertGreaterEqual(len(model["registrationEntries"]), 5)
            self.assertTrue(model["recoveryItems"])
            self.assertTrue(model["auditSummaries"])
            self.assertEqual([], validator.validate_collaboration_workbench(read_model, filename))
            self.assertEqual(
                {
                    "创建项目",
                    "邀请电脑",
                    "提交电脑注册申请",
                    "登记低风险工具",
                    "提交工具申请",
                },
                {entry["title"] for entry in model["registrationEntries"]},
            )
            self.assertEqual(
                {
                    "/v0/workbench/projects",
                    "/v0/workbench/runner-invitations",
                    "/v0/runners/register",
                    "/v0/workbench/tools",
                    "/v0/workbench/tool-registration-requests",
                },
                {entry["apiPath"] for entry in model["registrationEntries"]},
            )
            for entry in model["registrationEntries"]:
                self.assertIn("confirmationLabel", entry)
                self.assertIn("idempotencyKey", entry["primaryAction"])
                self.assertIn("auditRef", entry["primaryAction"])
                self.assertEqual("required", entry["primaryAction"]["serverGate"])

            device = model["devices"][0]
            for field in [
                "displayName",
                "ownerLabel",
                "availabilityLabel",
                "workTypeLabels",
                "authorizationSummary",
                "currentTaskLabel",
                "lastSeenLabel",
                "riskLabels",
                "primaryAction",
            ]:
                self.assertIn(field, device)

            route = model["routeBoard"][0]
            for field in [
                "taskLabel",
                "businessStatus",
                "assignedDeviceLabel",
                "routeReason",
                "blockerLabel",
                "nextOwnerLabel",
                "nextAction",
            ]:
                self.assertIn(field, route)

    def test_phase2_pm_control_read_model_and_dom_are_user_readable(self) -> None:
        validator = load_validator()
        for filename in ["workbench-read-model.js", "workbench-live-read-model.js"]:
            read_model = validator.load_read_model(ARTIFACT_DIR / filename)
            model = read_model["pmControl"]

            self.assertEqual("healthy", model["currentLease"]["status"])
            self.assertEqual("项目经理 Agent", model["currentLease"]["primaryPm"]["label"])
            self.assertTrue(any(item["role"] == "primary" for item in model["participants"]))
            self.assertTrue(any(item["role"] == "collaborator" for item in model["participants"]))
            self.assertTrue(any(item["role"] == "standby" for item in model["participants"]))
            self.assertTrue(model["takeoverRecords"])
            self.assertTrue(model["denialSummaries"])
            self.assertIn("nextAction", model["currentLease"])

        shell_js = (ARTIFACT_DIR / "workbench-shell.js").read_text(encoding="utf-8")
        for marker in [
            "renderPMControl",
            "PM 主控",
            "协同 PM",
            "备用 PM",
            "租约健康",
            "接管记录",
            "拒绝记录",
            "只有当前主控 PM 可以改项目调度",
        ]:
            self.assertIn(marker, shell_js)

        rendered = validator.render_shell_surfaces_with_node()
        visible_text = validator.visible_text_from_html(rendered["project-console"])
        for marker in ["PM 主控", "项目经理 Agent", "协同 PM", "备用 PM", "租约健康", "接管记录", "拒绝记录"]:
            self.assertIn(marker, visible_text)
        for forbidden in ["leaseId", "fencingToken", "pmlease.", "reasonCode"]:
            self.assertNotIn(forbidden, visible_text)

    def test_phase2_collaboration_visible_dom_hides_internal_ids(self) -> None:
        validator = load_validator()
        rendered = validator.render_shell_surfaces_with_node()
        html = rendered["agent-ring-console"]
        visible_text = validator.visible_text_from_html(html)

        for marker in ["协作设备", "接入与授权", "设备与执行器", "任务路由", "异常恢复", "操作记录"]:
            self.assertIn(marker, visible_text)
        for marker in ["张三的 MacBook Pro", "李四的 Windows 工作站", "分配给：", "为什么：", "下一责任人："]:
            self.assertIn(marker, visible_text)
        for forbidden in ["runnerId", "deviceId", "sessionId", "leaseId", "claimId", "endpoint", "capabilityCode", "scopeCode"]:
            self.assertNotIn(forbidden, visible_text)

    def test_runtime_monitor_visible_dom_hides_local_paths_and_raw_runtime_fields(self) -> None:
        validator = load_validator()
        read_model = validator.load_read_model(ARTIFACT_DIR / "workbench-live-read-model.js")
        rendered = validator.render_shell_surfaces_with_node()
        html = rendered["runtime-monitor"]
        visible_text = validator.visible_text_from_html(html)

        def collect_values(value, keys):
            found = []
            if isinstance(value, dict):
                for key, nested in value.items():
                    if key in keys:
                        if isinstance(nested, list):
                            found.extend(str(item) for item in nested if item)
                        elif nested:
                            found.append(str(nested))
                    found.extend(collect_values(nested, keys))
            elif isinstance(value, list):
                for nested in value:
                    found.extend(collect_values(nested, keys))
            return found

        raw_path_values = collect_values(read_model, {"workspace", "repositoryRefs", "repositoryScopes"})
        self.assertIn("/Users/meimei/Documents/company_knowledge_core", raw_path_values)

        for allowed_label in ["当前项目仓库", "仓库范围"]:
            self.assertIn(allowed_label, visible_text)
        for forbidden in [
            "/Users/",
            "/Users/meimei/Documents/company_knowledge_core",
            "projects/company-knowledge-core/desktop-workbench-slice0",
            "workspace",
            "repositoryRefs",
            "repositoryScopes",
            "runtimeMetrics",
            "sessionId",
            "runnerId",
            "deviceId",
            "capabilityCode",
            "agent_runtime",
            "local_router",
            "online",
            "delivered",
        ]:
            self.assertNotIn(forbidden, visible_text)
        for raw_value in raw_path_values:
            if raw_value.startswith("/"):
                self.assertNotIn(raw_value, visible_text)
                self.assertNotIn(raw_value, html)

    def test_shell_rendered_dom_uses_user_copy_for_workbench_routes(self) -> None:
        validator = load_validator()
        rendered = validator.render_shell_surfaces_with_node()

        self.assertEqual([], validator.validate_shell_visible_user_copy(REPO_ROOT, rendered))
        html = "\n".join(rendered.values())
        visible_text = validator.visible_text_from_html(html)
        for marker in ["项目", "本机设备", "主 Agent", "岗位 Agent", "执行器 Runner", "任务结果记录", "审批/权限", "异常恢复", "路由已建好"]:
            self.assertIn(marker, visible_text)
        for marker in ["项目选择", "真知公司知识核心", "本机单机闭环工作台", "数据来自中央状态记录"]:
            self.assertIn(marker, visible_text)
        for marker in [
            "新建项目",
            "一个项目建议放在一个独立文件夹",
            "真知中枢注册项目记录",
            "项目名称",
            "项目文件夹",
            "项目来源",
            "V1 目标",
            "默认 Agent 队伍",
            "产品 Agent",
            "研发 Agent",
            "测试 Agent",
            "执行设备",
            "项目创建包预览",
            "复制创建指令",
            "交给主 Agent 创建（需中枢授权）",
            "工作台项目选择器才会出现新项目",
        ]:
            self.assertIn(marker, visible_text)
        for forbidden in ["已创建成功", "创建成功", "项目已创建", "已成功创建"]:
            self.assertNotIn(forbidden, visible_text)
        for marker in ["通知中心", "人工确认队列", "项目：", "能力：", "执行器 Runner 租约重试"]:
            self.assertIn(marker, visible_text)
        for forbidden in [
            "Product final acceptance",
            "PM final acceptance",
            "Test closed-loop acceptance",
            "Product Agent accepted",
            "Show last verified evidence",
            "Product final result",
            "PM final result",
            "Test result",
            "TaskResult 写回",
            "Run next V1 acceptance stage.",
            "Review cancellation reason",
            "Human confirmation queue",
            "Notification center",
            "Projects:",
            "Capabilities:",
            "Device-aware routing",
            "Desktop packaging boundary",
            "Release Development technical solution tasks",
            "runtimeMetrics",
            "deviceId",
            "session.v1",
            "company-knowledge-core",
            "development",
            "implementation",
            "agent_runtime",
            "local_router",
            "project_management",
            "local-v1-runtime-workbench",
            "中央状态只读视图",
            "真实运行状态只读视图",
            "Runner scope and lease audit",
            "serverGate",
            "auditRef",
            "idempotencyKey",
            "Agent Hub",
            "TaskResult",
            "组Agent",
            "组 Agent",
        ]:
            self.assertNotIn(forbidden, visible_text)

    def test_workbench_updates_require_agent_task_chain(self) -> None:
        validator = load_validator()
        problems = validator.validate_workbench_agent_task_chain(REPO_ROOT)

        self.assertEqual([], problems)
        expected = {
            "kt-v1-workbench-codex-style-design": "agent.company.design",
            "kt-v1-workbench-codex-style-product-review": "agent.company.product-manager",
            "kt-v1-workbench-codex-style-dev": "agent.company.development",
            "kt-v1-workbench-codex-style-test": "agent.company.test",
            "kt-v1-workbench-codex-style-product-final-acceptance": "agent.company.product-manager",
            "kt-v1-workbench-codex-style-pm-final-acceptance": "agent.company.project-manager",
        }
        self.assertEqual(expected, validator.REQUIRED_WORKBENCH_TASK_CHAIN)


if __name__ == "__main__":
    unittest.main()
