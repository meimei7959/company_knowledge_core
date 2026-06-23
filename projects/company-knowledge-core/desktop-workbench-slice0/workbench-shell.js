(function () {
  const readModel = window.ZHENZHI_DESKTOP_WORKBENCH_READ_MODEL;
  const liveReadModelKind = "real-v1-runtime-read-model";
  const root = document.getElementById("workbench-root");
  const nav = document.getElementById("surface-nav");
  const projectSelect = document.getElementById("project-select");
  const projectTitle = document.getElementById("project-title");
  const projectSummary = document.getElementById("project-summary");
  const runtimeSummary = document.getElementById("runtime-summary");
  const syncState = document.getElementById("sync-state");
  const packageBoundary = document.getElementById("package-boundary");
  const newProjectEntry = document.getElementById("new-project-entry");

  const surfaceLabels = {
    "home": "总览",
    "runtime-monitor": "运行监控",
    "project-console": "项目",
    "agent-team-manager": "主 Agent",
    "agent-ring-console": "协作设备",
    "result-center": "结果",
    "review-center": "审批/权限",
    "quality-dashboard": "质量",
    "notification-center": "通知",
    "settings-security": "设置",
    "recovery-center": "异常恢复",
    "requirement-center": "需求",
    "admin-governance": "治理",
    "operations-feedback": "运维",
    "knowledge-query": "知识"
  };

  const primarySurfaces = [
    "home",
    "runtime-monitor",
    "project-console",
    "agent-team-manager",
    "agent-ring-console",
    "result-center",
    "review-center",
    "recovery-center"
  ];

  const surfaceSections = {
    "runtime-monitor": ["runtimeMetrics", "devices", "agentSessions", "agentMessages", "taskPackages", "worktrees"],
    "project-console": ["pmControl", "projectCreateEntry", "taskFlow"],
    "agent-team-manager": ["agentSessions", "agentCurrentWork"],
    "agent-ring-console": ["collaborationWorkbench", "runnerLeases", "runnerHistory"],
    "result-center": ["acceptanceEvidence", "taskResults", "taskFlow"],
    "review-center": ["approvals", "permissionGatedActions", "settingsSecurity"],
    "quality-dashboard": ["projectProgress", "runnerLeases"],
    "notification-center": ["notifications"],
    "settings-security": ["settingsSecurity", "permissionGatedActions"],
    "recovery-center": ["pmControl", "recovery", "problemRunnerLeases", "problemTasks", "notifications", "settingsSecurity"],
    "requirement-center": ["projectProgress"],
    "admin-governance": ["settingsSecurity", "approvals"],
    "operations-feedback": ["recovery", "notifications"],
    "knowledge-query": ["projectProgress"]
  };

  const statusText = {
    active: "执行中",
    accepted: "已接受",
    available: "可用",
    blocked: "阻塞",
    busy: "忙碌",
    cancelled: "已取消",
    changes_requested: "需返修",
    completed: "已完成",
    degraded: "降级",
    delivered: "已送达",
    done: "已关闭",
    escalated: "已升级处理",
    failed: "失败",
    expiring: "即将到期",
    healthy: "健康",
    missing: "缺失",
    needs_permission: "待授权",
    not_required: "无需验收",
    offline: "离线",
    online: "在线",
    pending: "待处理",
    processing: "处理中",
    ready: "就绪",
    rejected: "已驳回",
    required: "需服务端授权",
    retried: "重试已登记",
    running: "执行中",
    safe_fallback: "安全只读",
    stale: "过期",
    taken_over: "已接管",
    submitted: "已提交，待评审",
    pending_authorization: "等待授权",
    recovery_pending: "等待恢复",
    writeback_failed: "回传失败",
    readonly: "只读",
    expired: "已过期",
    authorized: "已授权",
    revoked: "已撤销",
    waiting_acceptance: "待验收",
    waiting_runner: "待执行器 Runner",
    waiting_review: "待评审"
  };

  const metricLabels = {
    acceptanceRunCount: "验收运行",
    agentSessionCount: "岗位 Agent 会话",
    deliveredMessageCount: "已送达消息",
    deviceCount: "设备登记",
    messageCount: "消息总数",
    messagesWithTargetDeviceId: "含设备路由",
    onlineAgentSessionCount: "在线岗位 Agent",
    onlineDeviceCount: "在线设备",
    openTaskCount: "未关闭 V1 任务",
    productFinalAccepted: "验收证据已就绪",
    projectId: "项目",
    taskPackageCount: "任务包",
    v1TaskCount: "V1 任务",
    worktreeCount: "隔离工作区"
  };

  const roleNames = {
    "agent.company.project-manager": "项目经理 Agent",
    "agent.company.product-manager": "产品经理 Agent",
    "agent.company.development": "研发 Agent",
    "agent.company.design": "设计 Agent",
    "agent.company.test": "测试 Agent",
    "agent.company.operations": "运维 Agent",
    "agent.company.knowledge-query": "知识查询 Agent"
  };

  const ownerNames = {
    "Agent": "岗位 Agent",
    "Project Manager Agent": "项目经理 Agent",
    "Product Manager Agent": "产品经理 Agent",
    "Development Agent": "研发 Agent",
    "Design Agent": "设计 Agent",
    "Test Agent": "测试 Agent",
    "Operations": "运维 Agent",
    "Human Reviewer": "人工审核人",
    "System Admin": "系统管理员",
    "Notification Center": "通知中心",
    "Review Center": "审批中心",
    "Desktop Shell": "桌面工作台",
    "Agent Hub": "主 Agent",
    "Local Router": "本机路由器",
    "Scheduler": "调度器",
    "Runner history": "执行器历史"
  };

  const capabilityLabels = {
    acceptance: "验收",
    acceptance_criteria_definition: "验收标准定义",
    agent_runtime: "Agent 运行时",
    agent_worker: "Agent 执行",
    api: "接口",
    approval_relay: "审批中转",
    cross_platform: "跨平台",
    database: "数据库",
    desktop: "桌面端",
    design: "设计",
    development: "研发",
    environment_readiness: "环境就绪",
    governance: "治理",
    implementation: "实现",
    integration: "集成",
    local_router: "本机路由",
    migration: "迁移",
    orchestrator: "编排",
    product_acceptance: "产品验收",
    product_management: "产品管理",
    product_requirement: "产品需求",
    product_review: "产品评审",
    project_management: "项目管理",
    quality_gate: "质量门禁",
    requirement_traceability: "需求追踪",
    scheduler: "调度",
    scheduler_design: "调度设计",
    schema_migration: "结构迁移",
    task_result_validation: "任务结果校验",
    task_result_writeback: "任务结果写回",
    technical_solution: "技术方案",
    test: "测试",
    testing: "测试",
    validation: "验证",
    workbench: "工作台",
    workflow_engineering: "工作流工程",
    worktree: "工作区"
  };

  const projectLabels = {
    "company-knowledge-core": "真知公司知识核心"
  };

  const priorityLabels = {
    critical: "紧急",
    high: "高",
    normal: "普通",
    low: "低"
  };

  const permissionLabels = {
    "approval.confirm.resolve": "确认审批处理",
    "approval.callback.resolve": "审批回调处理",
    "central-api.status.retry": "中央状态重试",
    "project.create": "创建项目登记",
    "runner.invitation.create": "邀请同事电脑",
    "runner.registration.submit": "提交电脑注册申请",
    "tool.register.low_risk": "登记低风险工具",
    "tool.registration_request.create": "提交工具申请",
    "collaboration.invite.create": "邀请同事电脑",
    "collaboration.authorization.confirm": "确认授权范围",
    "collaboration.authorization.revoke": "撤销授权",
    "recovery.request.create": "创建恢复请求",
    "collaboration.device.disable": "禁用电脑",
    "runner.pairing.handoff": "执行器配对交接",
    "runner.lease.retry": "执行器 Runner 租约重试",
    "pm_control_lease.release": "释放 PM 主控",
    "pm_control_lease.takeover": "接管 PM 主控"
  };

  const fieldLabels = {
    TaskResult: "任务结果记录",
    acceptanceStatus: "验收状态",
    auditRef: "审计记录",
    auditSummary: "操作摘要",
    assignedDeviceLabel: "执行电脑",
    branch: "分支",
    businessStatus: "业务状态",
    capabilities: "能力",
    commonRulesEvaluation: "公共规则自检",
    contextRefs: "上下文引用数",
    deviceId: "设备",
    failureReasons: "失败原因",
    fromSessionId: "来源会话",
    heartbeat: "心跳",
    hostType: "设备类型",
    idempotencyKey: "防重复记录",
    lease: "租约",
    packageId: "任务包",
    path: "路径",
    permission: "权限",
    priority: "优先级",
    projectId: "项目",
    requiredCapabilities: "所需能力",
    routeType: "路由方式",
    routeReason: "分配理由",
    runner: "执行器 Runner",
    scopeAudit: "范围审计",
    pmControl: "PM 主控",
    primaryPm: "主控 PM",
    serverGate: "服务端授权",
    sessionId: "会话",
    targetDeviceId: "目标设备",
    taskId: "任务",
    taskStatus: "任务状态",
    testsOrChecks: "测试/检查记录",
    toSessionId: "目标会话",
    workspace: "仓库范围",
    repositoryRefs: "仓库范围",
    repositoryScopes: "仓库授权"
  };

  const panelCopy = {
    "v1-runtime-health": {
      title: "V1 路由状态",
      nextAction: "未关闭任务 0 个，本机设备 1 台，岗位 Agent 会话 4 个，设备路由消息已登记。",
      fallbackState: "实时状态过期时，只显示最近一次已核验证据。"
    },
    "product-final-acceptance": {
      title: "产品最终验收证据",
      nextAction: "产品经理 Agent 已记录 V1 单机闭环验收证据。",
      fallbackState: "实时状态过期时，只显示最近一次已核验证据。"
    },
    "pm-final-acceptance": {
      title: "项目经理流程验收证据",
      nextAction: "项目经理流程验收记录已关联。",
      fallbackState: "实时状态过期时，只显示最近一次已核验证据。"
    },
    "test-closed-loop": {
      title: "测试闭环验收证据",
      nextAction: "测试 Agent 闭环验证记录已关联。",
      fallbackState: "实时状态过期时，只显示最近一次已核验证据。"
    },
    "release-readiness": {
      title: "发布准备状态",
      nextAction: "查看桌面运行证据，再安排跨平台打包证明。",
      fallbackState: "中央状态同步过期时，只显示阻塞摘要。"
    },
    "agent-focus": {
      title: "Agent 当前重点",
      nextAction: "完成桌面工作台实现证据，并交给测试 Agent 回归。",
      fallbackState: "只显示最近一次已核验的 AgentRun，不把缓存任务当作当前执行。"
    },
    attention: {
      title: "待处理事项",
      nextAction: "处理审批回调或权限拒绝。",
      fallbackState: "回调重复或过期时，进入异常恢复中心。"
    },
    "approval-callback": {
      title: "审批回调",
      nextAction: "查看证据预览后批准或要求修改，再回到主窗口。",
      fallbackState: "回调重复时，显示上一次决定和审计记录。"
    },
    "permission-gate": {
      title: "权限拒绝恢复",
      nextAction: "从服务端权限策略申请执行器范围或工具 Owner 批准。",
      fallbackState: "服务端返回授权前，禁用会改状态的按钮。"
    },
    "review-needed": {
      title: "需要审核",
      nextAction: "用户开启系统通知权限后再发送通知。",
      fallbackState: "系统通知不可用时，使用工作台内通知中心。"
    },
    "sync-failed": {
      title: "同步失败",
      nextAction: "打开异常恢复中心，查看已脱敏诊断。",
      fallbackState: "企业代理状态可见前，不在后台反复重试。"
    },
    offline: {
      title: "中央 API 离线",
      nextAction: "显示最近同步时间，并禁用会改状态的动作。",
      fallbackState: "进入安全只读模式。"
    },
    "failed-sync": {
      title: "同步失败",
      nextAction: "收集已脱敏诊断，并保留审计记录。",
      fallbackState: "诊断中不得包含 token、原始正文或原始文件。"
    },
    "duplicate-callback": {
      title: "重复回调",
      nextAction: "显示已生效决定，并阻止重复写入。",
      fallbackState: "任何重试都必须带防重复键。"
    },
    "secure-storage": {
      title: "安全凭证存储",
      nextAction: "系统授权和中央审计通过后，只保存凭证引用。",
      fallbackState: "安全存储不可用时，使用仅本次会话模式。"
    },
    "deep-link": {
      title: "跳转链接",
      nextAction: "通过中央 API 解析审批和执行器配对链接。",
      fallbackState: "链接解析失败时，不改写租约状态。"
    },
    "enterprise-proxy": {
      title: "企业网络",
      nextAction: "重试前展示代理、VPN 和自定义证书诊断。",
      fallbackState: "网络状态可见前暂停重试。"
    }
  };

  const taskTitleLabels = {
    "kt-ai-native-agent-v1-product-requirement-structure": "V1 产品需求结构化",
    "kt-ai-native-agent-v1-product-review-technical-solutions": "V1 产品评审技术方案",
    "kt-ai-native-agent-v1-product-review-technical-solutions-retry": "V1 产品评审技术方案返修",
    "kt-ai-native-agent-v1-product-scope-review": "V1 产品范围评审",
    "kt-ai-native-agent-v1-tech-profile-skill-registry": "V1 技术方案：Agent 档案和技能注册",
    "kt-ai-native-agent-v1-tech-local-router-session-registry": "V1 技术方案：本机路由和会话注册",
    "kt-ai-native-agent-v1-tech-agent-runtime-orchestrator": "V1 技术方案：运行时和主 Agent 编排",
    "kt-ai-native-agent-v1-tech-worktree-console-harness": "V1 技术方案：工作区、控制台和验证工具",
    "kt-ai-native-agent-v1-dev-implementation": "V1 研发实现闭环",
    "kt-ai-native-agent-v1-dev-implementation-handoff": "V1 研发实现闭环交接",
    "kt-ai-native-agent-v1-test-closed-loop-acceptance": "V1 测试闭环验收",
    "kt-ai-native-agent-v1-test-closed-loop-acceptance-handoff": "V1 测试闭环验收交接",
    "kt-ai-native-agent-v1-product-final-acceptance": "V1 产品最终验收",
    "kt-ai-native-agent-v1-product-final-acceptance-handoff": "V1 产品最终验收交接",
    "kt-ai-native-agent-v1-product-final-acceptance-handoff-02": "V1 产品最终验收二次交接",
    "kt-ai-native-agent-v1-pm-product-final-acceptance-handoff": "V1 项目经理流程验收交接",
    "kt-ai-native-agent-v1-pm-product-final-acceptance": "V1 项目经理流程验收",
    "kt-ai-native-agent-v1-product-requirement-structure-handoff": "V1 产品需求结构化交接",
    "kt-ai-native-agent-v1-product-scope-review-handoff": "V1 产品范围评审交接",
    "kt-ai-native-agent-v1-product-review-technical-solutions-retry-handoff": "V1 产品评审技术方案返修交接",
    "kt-ai-native-agent-v1-tech-profile-skill-registry-handoff": "V1 技术方案：Agent 档案和技能注册交接",
    "kt-ai-native-agent-v1-tech-local-router-session-registry-handoff": "V1 技术方案：本机路由和会话注册交接",
    "kt-ai-native-agent-v1-tech-agent-runtime-orchestrator-handoff": "V1 技术方案：运行时和主 Agent 编排交接",
    "kt-ai-native-agent-v1-tech-worktree-console-harness-handoff": "V1 技术方案：工作区、控制台和验证工具交接",
    "kt-v1-local-router-runtime-acceptance-dev": "V1 本机路由运行证明：研发",
    "kt-v1-local-router-runtime-acceptance-dev-handoff": "V1 本机路由运行证明：研发交接",
    "kt-v1-local-router-runtime-acceptance-test": "V1 本机路由运行证明：测试",
    "kt-v1-local-router-runtime-acceptance-test-handoff": "V1 本机路由运行证明：测试交接"
  };

  const evidenceRequirementLabels = {
    outputRefs: "缺少输出引用",
    evidenceRefs: "缺少证据入口",
    testsOrChecks: "缺少测试/检查记录",
    operatingRuleRefs: "缺少运行规则记录",
    commonRulesEvaluation: "缺少公共规则自检"
  };

  const runtimeStages = [
    ["项目", "当前项目已选中"],
    ["主 Agent", "接收用户目标并拆成任务"],
    ["岗位 Agent", "项目/产品/研发/测试会话在线"],
    ["本机设备", "本机设备已登记"],
    ["执行器", "执行器 Runner 接任务并上报"],
    ["结果记录", "任务结果记录写回"],
    ["审批权限", "审批/权限/验收路由可见"],
    ["异常恢复", "失败、离线、重复回调可追溯"]
  ];

  const defaultProjectCreateValues = {
    name: "新项目名称",
    folder: "选择或填写项目文件夹",
    source: "新项目",
    goal: "说明 V1 要解决的用户问题、交付目标和验收口径",
    mainAgent: "主 Agent",
    productAgent: "产品 Agent",
    developmentAgent: "研发 Agent",
    testAgent: "测试 Agent",
    device: "本机设备"
  };

  function text(value) {
    return String(value ?? "");
  }

  function escapeHtml(value) {
    return text(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function role(value) {
    const raw = text(value);
    if (roleNames[raw] || ownerNames[raw]) return roleNames[raw] || ownerNames[raw];
    if (raw === "device.local") return "本机设备";
    if (raw.startsWith("agent.company.")) return "岗位 Agent";
    return displayCopy(raw) || "未指定";
  }

  function statusClass(status) {
    return `status ${text(status).replace(/_/g, "-")}`;
  }

  function isKnownStatusValue(value) {
    return Object.prototype.hasOwnProperty.call(statusText, text(value));
  }

  function statusLabel(status) {
    const raw = text(status);
    return statusText[raw] || raw.replace(/_/g, " ") || "未知";
  }

  function displayProject(value) {
    const raw = text(value);
    if (!raw) return raw;
    return projectLabels[raw] || displayCopy(raw);
  }

  function displayCapability(value) {
    const raw = text(value);
    if (!raw) return raw;
    return capabilityLabels[raw] || displayCopy(raw);
  }

  function displayCapabilityList(value) {
    return text(value).split(",")
      .map((item) => item.trim())
      .filter(Boolean)
      .map(displayCapability)
      .join("、");
  }

  function displayPermission(value) {
    const raw = text(value);
    if (!raw) return raw;
    return permissionLabels[raw] || displayCopy(raw);
  }

  function isLocalPathLike(value) {
    const raw = text(value);
    return raw.startsWith("/") || /^[A-Za-z]:[\\/]/.test(raw) || raw.includes("/Users/") || raw.includes("\\Users\\");
  }

  function displayRepositoryScope(value) {
    const raw = text(value);
    if (!raw) return "未登记";
    if (raw === "当前项目仓库" || raw === "已授权仓库范围") return raw;
    return isLocalPathLike(raw) ? "当前项目仓库" : displayCopy(raw);
  }

  function displayDevice(value) {
    const raw = text(value);
    if (!raw || raw === "缺失") return raw || "未登记";
    if (raw === "device.local") return "本机设备";
    return raw.startsWith("device.") ? "本机设备" : displayCopy(raw);
  }

  function displaySession(value) {
    const raw = text(value);
    if (!raw || raw === "缺失") return raw || "未登记";
    if (raw.includes("development")) return "研发 Agent 会话";
    if (raw.includes("product")) return "产品经理 Agent 会话";
    if (raw.includes("test")) return "测试 Agent 会话";
    if (raw.includes("group") || raw.includes("project-manager")) return "项目经理 Agent 会话";
    return raw.startsWith("session.") ? "岗位 Agent 会话" : displayCopy(raw);
  }

  function displayValue(label, value) {
    const rawLabel = text(label);
    const raw = text(value);
    if (isKnownStatusValue(raw)) return statusLabel(raw);
    if (rawLabel === "projectId") return displayProject(raw);
    if (rawLabel === "capabilities" || rawLabel === "requiredCapabilities") return displayCapabilityList(raw);
    if (rawLabel === "workspace") return displayRepositoryScope(raw);
    if (rawLabel === "repositoryRefs" || rawLabel === "repositoryScopes") return raw ? "已授权仓库范围" : "未登记";
    if (rawLabel === "permission") return displayPermission(raw);
    if (rawLabel === "deviceId" || rawLabel === "targetDeviceId") return displayDevice(raw);
    if (rawLabel === "sessionId" || rawLabel === "fromSessionId" || rawLabel === "toSessionId") return displaySession(raw);
    if (rawLabel === "runner") return raw && raw !== "未分配" ? "执行器 Runner" : "未分配";
    if (rawLabel === "TaskResult") return raw ? "已登记" : "未登记";
    if (rawLabel === "packageId") return raw ? "已登记" : "未登记";
    if (rawLabel === "path" || rawLabel === "branch") return raw ? "已登记" : "未登记";
    if (rawLabel === "serverGate") return raw === "required" ? "需服务端授权" : displayCopy(raw);
    if (rawLabel === "auditRef" || rawLabel === "idempotencyKey") return raw ? "已登记" : "未登记";
    if (rawLabel === "priority") return priorityLabels[raw] || displayCopy(raw);
    if (rawLabel === "routeType" && raw === "local") return "本机路由";
    if (rawLabel === "scopeAudit") return displayCopy(raw);
    if (isLocalPathLike(raw)) return "已脱敏路径";
    return displayCopy(raw);
  }

  function panelKey(item) {
    return text(item && (item.id || item.taskId || item.resultRef || item.packageId || item.messageId || item.sessionId || item.deviceId));
  }

  function copyOverride(item, field, fallback) {
    const override = panelCopy[panelKey(item)] || panelCopy[text(item && item.id)];
    return displayCopy((override && override[field]) || fallback);
  }

  function displayCopy(value) {
    let raw = text(value);
    if (!raw) return raw;
    const exactCopy = {
      "approval.confirm.resolve": "确认审批处理",
      "approval.callback.resolve": "审批回调处理",
      "central-api.status.retry": "中央状态重试",
      confirm_request: "确认请求",
      critical: "紧急",
      "device.local": "本机设备",
      high: "高",
      local: "本机路由",
      normal: "普通",
      projectProgress: "项目进度",
      result: "结果",
      "runner.lease.retry": "执行器 Runner 租约重试",
      "runner.pairing.handoff": "执行器配对交接",
      runtimeMetrics: "运行指标",
      task: "任务"
    };
    if (exactCopy[raw]) return exactCopy[raw];
    raw = raw.replace(/组\s*Agent/g, "主 Agent");
    raw = raw.replace(/Group Agent/g, "主 Agent");
    raw = raw.replace(/show-safe-fallback-not-current/g, "状态过期显示安全只读");
    raw = raw.replace(/local-v1-runtime-workbench/g, "本机 V1 运行工作台");
    raw = raw.replace(/live read model/g, "实时只读模型");
    raw = raw.replace(/read model/g, "只读模型");
    raw = raw.replace(/\bowner\b/g, "负责人");
    raw = raw.replace(/Review cancellation reason and create a retry task only if the 负责人 approves\./g, "复核取消原因；仅在负责人确认后创建重试任务。");
    raw = raw.replace(/Show approval 负责人/g, "显示审批负责人");
    raw = raw.replace(/Device:\s*([^.]*)\.\s*Current task:\s*none\./g, "设备：$1；当前任务：无。");
    raw = raw.replace(/Notification center/g, "通知中心");
    raw = raw.replace(/Human confirmation queue/g, "人工确认队列");
    raw = raw.replace(/Review high-risk confirm_request messages in the main control window\./g, "在主控窗口审核高风险确认请求。");
    raw = raw.replace(/Confirm messages/g, "确认消息");
    raw = raw.replace(/Device-aware routing/g, "按设备路由");
    raw = raw.replace(/V1 routes through device\.local now and keeps targetDeviceId for future Hub expansion\./g, "V1 当前通过本机设备路由，并保留目标设备字段供后续扩展。");
    raw = raw.replace(/Agent messages/g, "Agent 消息");
    raw = raw.replace(/Desktop packaging boundary/g, "桌面打包边界");
    raw = raw.replace(/Tauri\/Mac\/Windows packaging remains next desktop product boundary after live Console\./g, "Tauri、Mac、Windows 打包仍是实时控制台之后的桌面产品边界。");
    raw = raw.replace(/Run next V1 acceptance stage\./g, "推进下一轮 V1 验收阶段。");
    raw = raw.replace(/Review cancellation reason and create a retry task only if the owner approves\./g, "复核取消原因；仅在负责人确认后创建重试任务。");
    raw = raw.replace(/Review technical solution and release implementation task\./g, "评审技术方案，并释放研发实现任务。");
    raw = raw.replace(/Release Development technical solution tasks for V1 runtime slices\./g, "释放 V1 运行切片的研发技术方案任务。");
    raw = raw.replace(/Run Product Manager scope review and then release Development technical solution tasks\./g, "先执行产品经理范围评审，再释放研发技术方案任务。");
    raw = raw.replace(/Plan V2 multi-device Hub and desktop packaging work\./g, "规划 V2 多设备 Hub 和桌面打包工作。");
    raw = raw.replace(/Open V1 task recovery/g, "V1 任务恢复入口");
    raw = raw.replace(/No open V1 task remains\./g, "没有剩余未关闭 V1 任务。");
    raw = raw.replace(/Scheduler workbench/g, "调度工作台");
    raw = raw.replace(/Resolve confirm request/g, "处理确认请求");
    raw = raw.replace(/Retry stale runner/g, "重试过期执行器 Runner");
    raw = raw.replace(/Local Machine/g, "本机设备");
    raw = raw.replace(/Active implementation/g, "研发实现执行中");
    raw = raw.replace(/Monitor current work/g, "监控当前工作");
    raw = raw.replace(/V1 package execution/g, "V1 任务包执行");
    raw = raw.replace(/Use as baseline/g, "作为基线使用");
    raw = raw.replace(/Failed execution/g, "执行失败");
    raw = raw.replace(/Route to recovery/g, "转入异常恢复");
    raw = raw.replace(/Stale lease/g, "过期租约");
    raw = raw.replace(/Retry or cancel/g, "重试或取消");
    raw = raw.replace(/Package retry/g, "任务包重试");
    raw = raw.replace(/Require idempotency/g, "要求防重复");
    raw = raw.replace(/Permission escalation/g, "权限升级处理");
    raw = raw.replace(/Show approval owner/g, "显示审批负责人");
    raw = raw.replace(/No active lease/g, "无活动租约");
    raw = raw.replace(/\boffline\b/g, "离线");
    raw = raw.replace(/\bclaim\b/g, "接管");
    raw = raw.replace(/Local Router/g, "本机路由器");
    raw = raw.replace(/Agent Worker/g, "Agent 执行器");
    raw = raw.replace(/TaskPackage/g, "任务包");
    raw = raw.replace(/AgentMessage/g, "Agent 消息");
    raw = raw.replace(/TaskResult/g, "任务结果记录");
    raw = raw.replace(/Projects:\s*([A-Za-z0-9_.-]+)\.\s*Capabilities:\s*([^.]*)\./g, (_match, project, capabilities) => (
      `项目：${displayProject(project)}；能力：${displayCapabilityList(capabilities)}。`
    ));
    raw = raw.replace(/device\.local/g, "本机设备");
    raw = raw.replace(/session\.v1\.[A-Za-z0-9_.-]+/g, "岗位 Agent 会话");
    raw = raw.replace(/company-knowledge-core/g, "真知公司知识核心");
    raw = raw.replace(/\bdevelopment\b/g, "研发");
    raw = raw.replace(/\bimplementation\b/g, "实现");
    raw = raw.replace(/\bagent_runtime\b/g, "Agent 运行");
    raw = raw.replace(/\blocal_router\b/g, "本机路由");
    raw = raw.replace(/\bproject_management\b/g, "项目管理");
    raw = raw.replace(/Runner should claim the retry lease and write back fresh evidence\./g, "执行器 Runner 应接管重试租约，并写回新的证据。");
    raw = raw.replace(/Monitor runner scope, leases, and heartbeat\./g, "监控执行器 Runner 的范围、租约和心跳。");
    raw = raw.replace(/Show task, approval, and runner notifications from project records\./g, "显示任务、审批和执行器通知。");
    raw = raw.replace(/Show last verified.*live state is stale\./g, "实时状态过期时，只显示最近一次已核验证据。");
    raw = raw.replace(/write result/g, "写入任务结果记录");
    raw = raw.replace(/\/Users\/[^\s<>"'，。；、)）]+/g, "已脱敏路径");
    raw = raw.replace(/[A-Za-z]:\\[^\s<>"'，。；、)）]+/g, "已脱敏路径");
    return raw;
  }

  function displayFieldLabel(label) {
    const raw = text(label);
    return fieldLabels[raw] || displayCopy(raw);
  }

  function displayPanelTitle(item) {
    const key = panelKey(item);
    if (taskTitleLabels[key]) return taskTitleLabels[key];
    return copyOverride(item, "title", item.title || item.taskId || item.label || "未命名");
  }

  function evidenceLabel(ref) {
    const rawLabel = text(ref && (ref.label || ""));
    const objectType = text(ref && (ref.objectType || ""));
    const objectRef = text(ref && (ref.objectRef || ref));
    const byType = {
      AgentDevice: "设备登记",
      AgentRun: "Agent 运行记录",
      AgentRunner: "执行器 Runner 记录",
      AgentSession: "岗位 Agent 会话记录",
      AuditLog: "审计记录",
      Decision: "决策记录",
      Manifest: "桥接清单",
      NativeBridgeCommand: "本机桥接命令",
      NotificationRecord: "通知记录",
      Policy: "规则文件",
      ProductReview: "产品评审记录",
      ProjectTask: "任务记录",
      TaskResult: "任务结果记录",
      V1AcceptanceRun: "V1 验收运行记录",
      WorkbenchSurface: "工作台页面",
      Workflow: "工作流记录",
      WorkflowGate: "发布检查项"
    };
    if (byType[objectType]) return byType[objectType];
    if (/product-final/i.test(rawLabel)) return "产品验收记录";
    if (/pm-final/i.test(rawLabel)) return "项目经理验收记录";
    if (/test/i.test(rawLabel)) return "测试记录";
    if (/runner/i.test(rawLabel)) return "执行器 Runner 记录";
    if (/^[a-z0-9_.:-]+$/i.test(rawLabel) && objectRef) return "证据入口";
    return displayCopy(rawLabel || shortRef(objectRef));
  }

  function shortRef(value) {
    const raw = text(value);
    return raw.split("/").pop() || raw || "无引用";
  }

  function metricValue(key, value) {
    if (typeof value === "boolean") return value ? "有" : "无";
    return displayValue(key, value || value === 0 ? value : "n/a");
  }

  function asArray(value) {
    return Array.isArray(value) ? value : [];
  }

  function chips(items, className) {
    return asArray(items).filter(Boolean).map((item) => (
      `<span class="${className || "chip"}">${escapeHtml(displayCopy(item))}</span>`
    )).join("");
  }

  function evidenceTemplate(refs) {
    const values = asArray(refs).filter(Boolean);
    if (!values.length) return `<span class="missing">缺 evidenceRefs</span>`;
    return values.slice(0, 4).map((ref) => {
      const label = evidenceLabel(ref);
      const title = ref.objectRef || ref;
      return `<code title="${escapeHtml(title)}">${escapeHtml(label)}</code>`;
    }).join("");
  }

  function metaTemplate(items) {
    const pairs = asArray(items).filter((item) => item && item.value !== "" && item.value !== undefined && item.value !== null);
    if (!pairs.length) return "";
    return `
      <dl class="meta-grid">
        ${pairs.map((item) => `
          <div>
            <dt>${escapeHtml(displayFieldLabel(item.label))}</dt>
            <dd>${escapeHtml(displayValue(item.label, item.value))}</dd>
          </div>
        `).join("")}
      </dl>
    `;
  }

  function missingEvidence(item) {
    return Object.keys(evidenceRequirementLabels).filter((key) => {
      const value = item ? item[key] : undefined;
      if (Array.isArray(value)) return value.length === 0;
      if (value && typeof value === "object") return Object.keys(value).length === 0;
      return value === undefined || value === null || value === "";
    });
  }

  function evidenceWarnings(item) {
    if (!item || !item.evidenceChecklist) return "";
    const missing = missingEvidence(item);
    if (!missing.length) return "";
    return `
      <div class="warning-list" aria-label="证据完整性提醒">
        ${missing.map((key) => `<span>${evidenceRequirementLabels[key]}</span>`).join("")}
      </div>
    `;
  }

  function rowTemplate(item) {
    const status = item.status || item.taskStatus || "safe_fallback";
    return `
      <article class="item-row" data-panel-id="${escapeHtml(item.id || item.taskId || item.resultRef || "")}">
        <div class="item-main">
          <div class="item-title-line">
            <h3>${escapeHtml(displayPanelTitle(item))}</h3>
            <span class="${statusClass(status)}">${escapeHtml(statusLabel(status))}</span>
          </div>
          <p class="item-meta">${escapeHtml(role(item.owner || item.executorAgent || item.assignee || "未指定 owner"))}</p>
          <p class="item-next">${escapeHtml(copyOverride(item, "nextAction", item.nextAction || item.summary || item.fallbackState || "查看证据和下一步"))}</p>
          ${item.fallbackState ? `<p class="fallback">降级策略：${escapeHtml(copyOverride(item, "fallbackState", item.fallbackState))}</p>` : ""}
          ${metaTemplate(item.meta)}
          ${evidenceWarnings(item)}
          <div class="evidence">${evidenceTemplate(item.evidenceRefs)}</div>
        </div>
      </article>
    `;
  }

  function panelFromDevice(device) {
    return {
      id: device.deviceId || device.path,
      title: device.name || "本机设备",
      status: device.status || "safe_fallback",
      owner: "本机设备",
      nextAction: "V1 只有本机设备；仍展示路由字段，为后续 Hub 扩展准备。",
      fallbackState: "设备心跳过期时，只展示最近证据，不展示为当前在线。",
      meta: [
        { label: "deviceId", value: device.deviceId || "缺失" },
        { label: "hostType", value: device.hostType },
        { label: "workspace", value: "当前项目仓库" },
        { label: "capabilities", value: asArray(device.capabilities).join(", ") }
      ],
      evidenceRefs: [{ label: device.deviceId || "device", objectRef: device.path || "runtime/devices" }]
    };
  }

  function panelFromSession(session) {
    return {
      id: session.sessionId || session.path,
      title: role(session.agentId || session.sessionId),
      status: session.status || "safe_fallback",
      owner: session.agentId || "Agent",
      nextAction: `当前任务：${taskTitleLabels[session.currentTaskId] || text(session.currentTaskId || "无")}。会话通过本机路由注册。`,
      fallbackState: "会话离线时，不代签任务结果，不展示为当前执行。",
      meta: [
        { label: "sessionId", value: session.sessionId },
        { label: "deviceId", value: session.deviceId || "缺失" },
        { label: "projectId", value: session.projectId },
        { label: "capabilities", value: asArray(session.capabilities).join(", ") }
      ],
      evidenceRefs: [{ label: session.sessionId || "session", objectRef: session.path || "runtime/sessions" }]
    };
  }

  function panelFromMessage(message) {
    const routing = message.routing || {};
    return {
      id: message.messageId || message.path,
      title: `${role(message.fromAgentId)} -> ${role(message.toAgentId)}`,
      status: message.status || "safe_fallback",
      owner: "本机路由",
      nextAction: `消息类型：${displayCopy(message.messageType)}；优先级：${displayCopy(message.priority)}；目标设备：${displayDevice(routing.targetDeviceId || "缺失")}`,
      fallbackState: "路由失败时保留消息证据和目标设备，不静默重试。",
      meta: [
        { label: "routeType", value: routing.routeType || "缺失" },
        { label: "targetDeviceId", value: routing.targetDeviceId || "缺失" },
        { label: "fromSessionId", value: message.fromSessionId },
        { label: "toSessionId", value: message.toSessionId },
        { label: "contextRefs", value: asArray(message.contextRefs).length }
      ],
      evidenceRefs: [{ label: message.messageId || "message", objectRef: message.path || "runtime/messages" }]
    };
  }

  function panelFromTask(task) {
    return {
      id: task.taskId || task.taskRef,
      title: taskTitleLabels[task.taskId] || task.title || task.taskId || "任务",
      status: task.status || "safe_fallback",
      owner: task.assignee || task.leaseOwner || "agent.company.project-manager",
      nextAction: task.nextAction || task.currentStage || "查看任务证据",
      fallbackState: "取消、驳回、阻塞任务必须走 owner 明确重试，不自动恢复。",
      meta: [
        { label: "taskId", value: task.taskId },
        { label: "priority", value: task.priority },
        { label: "runner", value: task.assignedRunner || "未分配" },
        { label: "failureReasons", value: asArray(task.failureReasons).map(displayCopy).join(", ") }
      ],
      evidenceRefs: [{ label: task.taskId || "task", objectRef: task.taskRef || task.resultRef || "projects/company-knowledge-core/tasks" }]
    };
  }

  function panelFromPackage(taskPackage) {
    return {
      id: taskPackage.packageId,
      title: taskTitleLabels[taskPackage.taskId] || taskPackage.taskId || taskPackage.packageId,
      status: taskPackage.status || "safe_fallback",
      owner: taskPackage.toAgentId || taskPackage.assignee,
      nextAction: `任务包从 ${role(taskPackage.fromAgentId)} 交给 ${role(taskPackage.toAgentId)}。`,
      fallbackState: "任务包只展示调度证据，不在前端改写任务状态。",
      meta: [
        { label: "packageId", value: taskPackage.packageId },
        { label: "requiredCapabilities", value: asArray(taskPackage.requiredCapabilities).join(", ") },
        { label: "contextRefs", value: asArray(taskPackage.contextRefs).length }
      ],
      evidenceRefs: [{ label: taskPackage.packageId || "task package", objectRef: taskPackage.taskRef || "runtime/task-packages" }]
    };
  }

  function panelFromWorktree(worktree) {
    return {
      id: worktree.worktreeId || worktree.path,
      title: taskTitleLabels[worktree.taskId] || "隔离工作区",
      status: worktree.status || "safe_fallback",
      owner: worktree.agentId || "Agent",
      nextAction: "并行任务使用隔离工作区，避免同目录冲突。",
      fallbackState: "缺少隔离工作区证据时，不允许展示为可并行执行。",
      meta: [
        { label: "path", value: worktree.path },
        { label: "branch", value: worktree.branch },
        { label: "deviceId", value: worktree.deviceId || "本机默认" }
      ],
      evidenceRefs: [{ label: worktree.worktreeId || shortRef(worktree.path), objectRef: worktree.path || "runtime/worktrees" }]
    };
  }

  function panelFromLease(leaseState) {
    const audit = leaseState.scopeAudit || {};
    const leaseLabel = (leaseState.lease && leaseState.lease.label) || "无活动租约";
    return {
      id: leaseState.lease && leaseState.lease.objectRef,
      title: "执行器 Runner",
      status: leaseState.status,
      owner: "执行器 Runner",
      nextAction: `${displayCopy(leaseLabel)}；心跳 ${statusLabel(leaseState.heartbeat || "missing")}`,
      fallbackState: "租约过期、失败或离线时必须进入异常恢复，不自动 claim。",
      meta: [
        { label: "lease", value: leaseState.lease && leaseState.lease.label },
        { label: "heartbeat", value: leaseState.heartbeat },
        { label: "scopeAudit", value: audit.nextAction }
      ],
      evidenceRefs: audit.evidenceRefs || []
    };
  }

  function panelFromHistory(item) {
    return {
      id: item.label,
      title: item.label,
      status: item.status || "safe_fallback",
      owner: "执行器历史",
      nextAction: item.nextAction || "查看历史证据",
      fallbackState: "历史状态只做追溯，不覆盖当前租约。",
      evidenceRefs: [{ label: item.label || "history", objectRef: "runnerHistory" }]
    };
  }

  function panelFromTaskResult(item) {
    return {
      ...item,
      evidenceChecklist: true,
      id: item.resultRef || item.taskId,
      title: taskTitleLabels[item.taskId] || "任务结果记录",
      status: item.status || item.taskStatus || "submitted",
      owner: item.executorAgent,
      nextAction: item.status === "submitted"
        ? "已提交，等待后续测试、产品或项目经理路由；不等于已验收。"
        : (item.summary || "查看结果"),
      fallbackState: "缺证据字段时必须显式提示，不能进入最终验收。",
      meta: [
        { label: "TaskResult", value: item.resultRef },
        { label: "taskStatus", value: item.taskStatus },
        { label: "acceptanceStatus", value: item.acceptanceStatus },
        { label: "testsOrChecks", value: asArray(item.testsOrChecks).length }
      ],
      evidenceRefs: [{ label: shortRef(item.resultRef), objectRef: item.resultRef }]
    };
  }

  function actionPanel(action) {
    return {
      id: action.id,
      title: action.label || action.id,
      status: action.serverGate === "required" ? "needs_permission" : "ready",
      owner: action.permission,
      nextAction: "必须由服务端授权和审计后执行；前端只展示，不直接写状态。",
      fallbackState: "授权失败时保留审计记录和防重复记录。",
      meta: [
        { label: "permission", value: action.permission },
        { label: "serverGate", value: action.serverGate },
        { label: "idempotencyKey", value: action.idempotencyKey },
        { label: "auditRef", value: action.auditRef }
      ],
      evidenceRefs: [{ label: action.auditRef || action.id, objectRef: action.auditRef || "audit" }]
    };
  }

  function collaborationAction(action, fallbackLabel) {
    const label = action && action.label ? action.label : fallbackLabel;
    const reason = action && action.disabledReason ? action.disabledReason : "";
    const title = reason || "提交到中枢，经过权限、确认、幂等和审计后生效";
    const actionId = action && (action.permission || action.label || fallbackLabel);
    const idempotencyKey = action && action.idempotencyKey ? action.idempotencyKey : "";
    return `
      <button class="secondary-button" type="button" data-workbench-action="${escapeHtml(actionId || "")}" data-idempotency-key="${escapeHtml(idempotencyKey)}" ${reason ? "disabled aria-disabled=\"true\"" : ""} title="${escapeHtml(title)}">
        ${escapeHtml(label)}
      </button>
    `;
  }

  function registrationEntryTemplate(entry) {
    const action = entry.primaryAction || {};
    return `
      <article class="item-row collaboration-row registration-entry">
        <div class="item-main">
          <div class="item-title-line">
            <h3>${escapeHtml(entry.title || "登记入口")}</h3>
            <span class="${statusClass(entry.status || "ready")}">${escapeHtml(entry.statusLabel || statusLabel(entry.status || "ready"))}</span>
          </div>
          <p class="item-next">${escapeHtml(entry.description || "提交申请后由中枢校验权限。")}</p>
          <dl class="meta-grid">
            <div><dt>接口</dt><dd>${escapeHtml(entry.apiPath || "由中枢登记入口处理")}</dd></div>
            <div><dt>确认</dt><dd>${escapeHtml(entry.confirmationLabel || "提交前必须确认范围和风险")}</dd></div>
            <div><dt>边界</dt><dd>${escapeHtml(entry.guardrailLabel || "登记入口不直接改变执行结果")}</dd></div>
            <div><dt>审计</dt><dd>${escapeHtml(entry.auditLabel || "提交和审批都会留下记录")}</dd></div>
            <div><dt>防重复</dt><dd>${escapeHtml(action.idempotencyKey ? "已设置幂等键" : "等待中枢生成")}</dd></div>
          </dl>
          <div class="action-list compact-actions">${collaborationAction(action, "提交申请")}</div>
        </div>
      </article>
    `;
  }

  function collaborationSummaryTemplate(model) {
    const summary = model.summary || {};
    const metrics = [
      ["可接任务", summary.availableDeviceCountLabel || model.availableDeviceCountLabel || "0 台"],
      ["执行中", summary.runningTaskCountLabel || "0 项"],
      ["等待授权", summary.pendingAuthorizationCountLabel || "0 项"],
      ["需处理", summary.riskCountLabel || "0 项"]
    ];
    return `
      <section class="metric-strip collaboration-summary" aria-label="协作设备状态总览">
        ${metrics.map(([label, value]) => `
          <div class="metric">
            <span>${escapeHtml(label)}</span>
            <strong>${escapeHtml(value)}</strong>
          </div>
        `).join("")}
      </section>
    `;
  }

  function pairingRequestTemplate(request) {
    const action = request.primaryAction || {};
    return `
      <article class="item-row collaboration-row">
        <div class="item-main">
          <div class="item-title-line">
            <h3>${escapeHtml(request.displayTitle || "同事电脑请求接入")}</h3>
            <span class="${statusClass(request.status || "pending_authorization")}">${escapeHtml(request.statusLabel || statusLabel(request.status || "pending_authorization"))}</span>
          </div>
          <p class="item-meta">${escapeHtml(request.requesterLabel || "申请人待确认")} · ${escapeHtml(request.deviceLabel || "未命名的同事电脑")}</p>
          <p class="item-next">${escapeHtml(request.scopeSummary || "等待项目负责人确认授权范围。")}</p>
          ${request.riskLabel ? `<p class="fallback">${escapeHtml(request.riskLabel)}</p>` : ""}
          <div class="action-list compact-actions">${collaborationAction(action, "确认授权")}</div>
        </div>
      </article>
    `;
  }

  function collaborationDeviceTemplate(device) {
    const action = device.primaryAction || {};
    const activeAgents = asArray(device.activeAgentLabels).join("、") || "暂无工作中的 Agent";
    const tools = asArray(device.toolLabels).join("、") || "暂无工具上报";
    return `
      <article class="item-row collaboration-row">
        <div class="item-main">
          <div class="item-title-line">
            <h3>${escapeHtml(device.displayName || "未命名的同事电脑")}</h3>
            <span class="${statusClass(device.status || "ready")}">${escapeHtml(device.availabilityLabel || "需处理")}</span>
          </div>
          <p class="item-meta">${escapeHtml(device.ownerLabel || "负责人待确认")} · 最近在线：${escapeHtml(device.lastSeenLabel || "未知")}</p>
          <p class="item-next">当前任务：${escapeHtml(device.currentTaskLabel || "暂无任务")}</p>
          <p class="fallback">授权：${escapeHtml(device.authorizationSummary || "授权范围待确认")}</p>
          <dl class="meta-grid">
            <div><dt>工作中的 Agent</dt><dd>${escapeHtml(activeAgents)}</dd></div>
            <div><dt>执行器</dt><dd>${escapeHtml(device.executorLabel || "未上报")}</dd></div>
            <div><dt>模型</dt><dd>${escapeHtml(device.modelUsageLabel || "未上报")}</dd></div>
            <div><dt>Token</dt><dd>${escapeHtml(device.tokenUsageLabel || "未上报")}</dd></div>
            <div><dt>工具</dt><dd>${escapeHtml(tools)}</dd></div>
          </dl>
          <div class="evidence">${chips(device.workTypeLabels || [], "chip")}${chips(device.riskLabels || [], "risk-chip")}</div>
          <div class="action-list compact-actions">${collaborationAction(action, "查看")}</div>
        </div>
      </article>
    `;
  }

  function collaborationRouteTemplate(route) {
    return `
      <article class="item-row collaboration-row">
        <div class="item-main">
          <div class="item-title-line">
            <h3>${escapeHtml(route.taskLabel || "未命名任务")}</h3>
            <span class="${statusClass(route.status || "processing")}">${escapeHtml(route.businessStatus || "需处理")}</span>
          </div>
          <p class="item-meta">分配给：${escapeHtml(route.assignedDeviceLabel || "等待可用电脑")} · 下一责任人：${escapeHtml(route.nextOwnerLabel || "项目经理 Agent")}</p>
          <p class="item-next">为什么：${escapeHtml(route.routeReason || "正在匹配可执行同事电脑。")}</p>
          <dl class="meta-grid">
            <div><dt>所属需求</dt><dd>${escapeHtml(route.requirementLabel || "未关联需求")}</dd></div>
            <div><dt>负责 Agent</dt><dd>${escapeHtml(route.activeAgentLabel || route.nextOwnerLabel || "待确认")}</dd></div>
            <div><dt>执行器</dt><dd>${escapeHtml(route.executorLabel || "未上报")}</dd></div>
            <div><dt>模型</dt><dd>${escapeHtml(route.modelLabel || "未上报")}</dd></div>
            <div><dt>Token</dt><dd>${escapeHtml(route.tokenUsageLabel || "未上报")}</dd></div>
            <div><dt>工具</dt><dd>${escapeHtml(route.toolUsageLabel || "未上报")}</dd></div>
          </dl>
          <p class="fallback">卡点：${escapeHtml(route.blockerLabel || "暂无卡点")}；下一步：${escapeHtml(route.nextAction || "查看任务证据")}</p>
        </div>
      </article>
    `;
  }

  function recoveryItemTemplate(item) {
    return `
      <article class="item-row collaboration-row">
        <div class="item-main">
          <div class="item-title-line">
            <h3>${escapeHtml(item.title || "恢复事项")}</h3>
            <span class="${statusClass(item.status || "recovery_pending")}">${escapeHtml(item.statusLabel || "等待恢复")}</span>
          </div>
          <p class="item-meta">${escapeHtml(item.impactLabel || "影响待确认")} · 责任人：${escapeHtml(item.ownerLabel || "项目经理 Agent")}</p>
          <p class="item-next">${escapeHtml(item.displayMessage || "需要确认后继续。")}</p>
          <p class="fallback">下一步：${escapeHtml(item.nextAction || "等待、续租、转交或取消")}</p>
        </div>
      </article>
    `;
  }

  function auditSummaryTemplate(item) {
    return `
      <article class="action-row">
        <strong>${escapeHtml(item.actionLabel || "操作记录")}</strong>
        <span>${escapeHtml(item.actorLabel || "系统")} 对 ${escapeHtml(item.targetLabel || "协作对象")} 执行；影响：${escapeHtml(item.impactLabel || "已记录")}；结果：${escapeHtml(item.resultLabel || "待确认")}</span>
      </article>
    `;
  }

  function technicalDetailsTemplate(items) {
    const values = asArray(items);
    if (!values.length) return "";
    return `
      <details class="technical-details">
        <summary>查看技术详情/证据</summary>
        <div class="row-list">
          ${values.map((item) => `
            <article class="action-row">
              <strong>${escapeHtml(item.label || "脱敏技术引用")}</strong>
              <span>${escapeHtml(item.redactedValue || item.summary || "已脱敏")}</span>
            </article>
          `).join("")}
        </div>
      </details>
    `;
  }

  function renderCollaborationWorkbench() {
    const model = readModel.collaborationWorkbench || {};
    return `
      <section class="collaboration-hero" aria-label="协作设备入口">
        <div>
          <p class="eyebrow">项目中枢 / 协作设备</p>
          <h2>${escapeHtml(model.entryLabel || "协作设备")}</h2>
          <p>${escapeHtml(model.projectJoinPolicyLabel || "邀请同事电脑加入当前项目，并查看任务由哪台电脑执行。")}</p>
          ${model.readOnlyNotice ? `<p class="fallback">${escapeHtml(model.readOnlyNotice)}</p>` : ""}
        </div>
        <div class="collaboration-actions">
          ${asArray(model.primaryActions).map((action) => collaborationAction(action, action.label || "提交申请")).join("")}
        </div>
      </section>
      ${collaborationSummaryTemplate(model)}
      <section class="surface-section">
        <div class="section-head"><div><h2>登记入口</h2><p>创建项目、邀请电脑、注册工具；每次提交都要权限、确认、幂等和审计。</p></div><span>${asArray(model.registrationEntries).length}</span></div>
        <div class="registration-grid">${asArray(model.registrationEntries).length ? asArray(model.registrationEntries).map(registrationEntryTemplate).join("") : `<p class="empty">暂无登记入口</p>`}</div>
      </section>
      <div class="two-column collaboration-grid">
        <div>
          <section class="surface-section">
            <div class="section-head"><div><h2>接入与授权</h2><p>确认同事电脑能做什么，再允许接任务。</p></div><span>${asArray(model.pairingRequests).length}</span></div>
            <div class="row-list">${asArray(model.pairingRequests).length ? asArray(model.pairingRequests).map(pairingRequestTemplate).join("") : `<p class="empty">暂无接入申请</p>`}</div>
          </section>
          <section class="surface-section">
            <div class="section-head"><div><h2>设备与执行器</h2><p>第一列使用同事电脑名称，不展示内部引用。</p></div><span>${asArray(model.devices).length}</span></div>
            <div class="row-list">${asArray(model.devices).length ? asArray(model.devices).map(collaborationDeviceTemplate).join("") : `<p class="empty">还没有同事电脑加入这个项目</p>`}</div>
          </section>
        </div>
        <div>
          <section class="surface-section">
            <div class="section-head"><div><h2>任务路由</h2><p>${escapeHtml(model.activeRouteSummary || "等待调度器分配任务。")}</p></div><span>${asArray(model.routeBoard).length}</span></div>
            <div class="row-list">${asArray(model.routeBoard).length ? asArray(model.routeBoard).map(collaborationRouteTemplate).join("") : `<p class="empty">暂无任务路由</p>`}</div>
          </section>
          <section class="surface-section">
            <div class="section-head"><div><h2>异常恢复</h2><p>离线、超时、越权和回传失败都给出下一步。</p></div><span>${asArray(model.recoveryItems).length}</span></div>
            <div class="row-list">${asArray(model.recoveryItems).length ? asArray(model.recoveryItems).map(recoveryItemTemplate).join("") : `<p class="empty">暂无恢复事项</p>`}</div>
          </section>
        </div>
      </div>
      <section class="surface-section">
        <div class="section-head"><div><h2>操作记录</h2><p>写操作完成后显示可读摘要，底层审计留在证据层。</p></div><span>${asArray(model.auditSummaries).length}</span></div>
        <div class="action-list">${asArray(model.auditSummaries).length ? asArray(model.auditSummaries).map(auditSummaryTemplate).join("") : `<p class="empty">暂无操作记录</p>`}</div>
      </section>
      ${technicalDetailsTemplate(model.technicalDetails)}
    `;
  }

  function pmParticipantTemplate(participant) {
    const pm = participant.pm || {};
    const runner = participant.runner || {};
    const device = participant.device || {};
    const roleLabel = {
      primary: "主控 PM",
      collaborator: "协同 PM",
      standby: "备用 PM"
    }[participant.role] || "PM";
    return `
      <article class="item-row collaboration-row">
        <div class="item-main">
          <div class="item-title-line">
            <h3>${escapeHtml(pm.label || roleLabel)}</h3>
            <span class="${statusClass(participant.status || "ready")}">${escapeHtml(roleLabel)}</span>
          </div>
          <p class="item-meta">${escapeHtml(device.label || runner.label || "未登记电脑")}</p>
          <p class="item-next">${escapeHtml(participant.nextAction || "可查看项目状态。")}</p>
          <dl class="meta-grid">
            <div><dt>电脑</dt><dd>${escapeHtml(displayDevice(device.label || runner.label || "未登记"))}</dd></div>
            <div><dt>接管优先级</dt><dd>${escapeHtml(text(participant.standbyPriority || "非备用"))}</dd></div>
            <div><dt>能力</dt><dd>${escapeHtml(asArray(participant.capabilities).map(displayCapability).join("、") || "查看与建议")}</dd></div>
          </dl>
        </div>
      </article>
    `;
  }

  function pmTakeoverTemplate(record) {
    return `
      <article class="action-row">
        <strong>${escapeHtml((record.fromPm && record.fromPm.label) || "无前任主控")} -> ${escapeHtml((record.toPm && record.toPm.label) || "新主控 PM")}</strong>
        <span>${escapeHtml(record.occurredAt || "时间待记录")}；原因：${escapeHtml(record.reason || "未填写")}；接管前：${escapeHtml(statusLabel(record.previousLeaseStatus || "missing"))}；${escapeHtml(record.newLeaseIdLabel || "新租约已生成")}；${escapeHtml(record.auditRef ? "审计已记录" : "审计待补")}</span>
      </article>
    `;
  }

  function pmDenialTemplate(item) {
    return `
      <article class="action-row">
        <strong>${escapeHtml((item.requestPm && item.requestPm.label) || "PM 写入")}</strong>
        <span>${escapeHtml(item.displayMessage || "写入被拒绝。")} 下一步：${escapeHtml(item.nextAction || "联系主控 PM 或发起接管。")} ${item.auditRef ? "审计已记录。" : ""}</span>
      </article>
    `;
  }

  function renderPMControl() {
    const model = readModel.pmControl || {};
    const current = model.currentLease || {};
    const primary = current.primaryPm || {};
    const lease = current.lease || {};
    const participants = asArray(model.participants);
    const primaryParticipants = participants.filter((item) => item.role === "primary");
    const collaboratorParticipants = participants.filter((item) => item.role === "collaborator");
    const standbyParticipants = participants.filter((item) => item.role === "standby");
    const action = current.takeoverAction || current.releaseAction;
    return `
      <section class="surface-section pm-control-section" aria-label="PM 主控租约">
        <div class="section-head">
          <div>
            <p class="eyebrow">项目级调度 / PM 主控租约</p>
            <h2>PM 主控</h2>
            <p>${escapeHtml((model.healthExplanation && model.healthExplanation.nextAction) || current.nextAction || "只有当前主控 PM 可以改项目调度。")}</p>
          </div>
          <span>${escapeHtml(statusLabel(current.status || "missing"))}</span>
        </div>
        <div class="metric-strip">
          <div class="metric"><span>主控 PM</span><strong>${escapeHtml(primary.label || "暂无主控 PM")}</strong></div>
          <div class="metric"><span>租约健康</span><strong>${escapeHtml(statusLabel(current.status || "missing"))}</strong></div>
          <div class="metric"><span>心跳</span><strong>${escapeHtml(statusLabel(current.heartbeat || "offline"))}</strong></div>
          <div class="metric"><span>写入状态</span><strong>${escapeHtml(current.nextAction || "只读")}</strong></div>
        </div>
        <dl class="meta-grid">
          <div><dt>所在电脑</dt><dd>${escapeHtml((primaryParticipants[0] && primaryParticipants[0].device && primaryParticipants[0].device.label) || "未登记")}</dd></div>
          <div><dt>到期时间</dt><dd>${escapeHtml(current.expiresAt || "无有效租约")}</dd></div>
          <div><dt>最近心跳</dt><dd>${escapeHtml(current.lastHeartbeatAt || "暂无心跳")}</dd></div>
          <div><dt>防旧写入代际</dt><dd>${escapeHtml(current.leaseGenerationLabel || current.fencingTokenLabel || "等待主控租约")}</dd></div>
        </dl>
        <div class="action-list compact-actions">${action ? collaborationAction(action, action.label || "提交到中枢") : ""}</div>
        <div class="two-column collaboration-grid">
          <section class="pm-control-block">
            <div class="section-head"><div><h2>协同 PM</h2><p>可查看、准备建议；不能静默写项目调度。</p></div><span>${collaboratorParticipants.length}</span></div>
            <div class="row-list">${collaboratorParticipants.length ? collaboratorParticipants.map(pmParticipantTemplate).join("") : `<p class="empty">暂无协同 PM</p>`}</div>
          </section>
          <section class="pm-control-block">
            <div class="section-head"><div><h2>备用 PM</h2><p>主控过期、释放或确认接管后成为新主控。</p></div><span>${standbyParticipants.length}</span></div>
            <div class="row-list">${standbyParticipants.length ? standbyParticipants.map(pmParticipantTemplate).join("") : `<p class="empty">暂无备用 PM</p>`}</div>
          </section>
        </div>
        <section class="pm-control-block">
          <div class="section-head"><div><h2>接管记录</h2><p>记录前任、后任、原因、状态变化和审计。</p></div><span>${asArray(model.takeoverRecords).length}</span></div>
          <div class="action-list">${asArray(model.takeoverRecords).length ? asArray(model.takeoverRecords).map(pmTakeoverTemplate).join("") : `<p class="empty">暂无接管记录</p>`}</div>
        </section>
        <section class="pm-control-block">
          <div class="section-head"><div><h2>拒绝记录</h2><p>无租约、过期、非主控、项目不匹配都会拒绝并审计。</p></div><span>${asArray(model.denialSummaries).length}</span></div>
          <div class="action-list">${asArray(model.denialSummaries).length ? asArray(model.denialSummaries).map(pmDenialTemplate).join("") : `<p class="empty">暂无 PM 写入拒绝记录</p>`}</div>
        </section>
      </section>
    `;
  }

  function sectionTemplate(title, items, emptyText, intro) {
    const rows = items.length ? items.map(rowTemplate).join("") : `<p class="empty">${escapeHtml(displayCopy(emptyText))}</p>`;
    return `
      <section class="surface-section">
        <div class="section-head">
          <div>
            <h2>${escapeHtml(displayCopy(title))}</h2>
            ${intro ? `<p>${escapeHtml(displayCopy(intro))}</p>` : ""}
          </div>
          <span>${items.length}</span>
        </div>
        <div class="row-list">${rows}</div>
      </section>
    `;
  }

  function metricStrip(limitKeys) {
    const metrics = readModel.runtimeMetrics || {};
    const keys = limitKeys || [
      "openTaskCount",
      "onlineDeviceCount",
      "onlineAgentSessionCount",
      "messagesWithTargetDeviceId",
      "taskPackageCount",
      "worktreeCount",
      "productFinalAccepted"
    ];
    return `
      <section class="metric-strip" aria-label="V1 运行指标">
        ${keys.map((key) => `
          <div class="metric">
            <span>${escapeHtml(metricLabels[key] || key)}</span>
            <strong>${escapeHtml(metricValue(key, metrics[key]))}</strong>
          </div>
        `).join("")}
      </section>
    `;
  }

  function routeStatusPanels() {
    const metrics = readModel.runtimeMetrics || {};
    const problemCount = asArray(readModel.runnerLeases).filter((item) => ["stale", "failed", "offline", "blocked"].includes(item.status)).length
      + asArray(readModel.taskFlow).filter((item) => ["cancelled", "rejected", "blocked", "failed", "stale"].includes(item.status)).length;
    return [
      {
        id: "route-project",
        title: "项目",
        status: readModel.projectId ? "ready" : "missing",
        owner: "项目经理 Agent",
        nextAction: `当前项目：${displayProject(readModel.projectId)}。`,
        fallbackState: "后续接入多项目时，由项目选择器切换上下文。",
        evidenceRefs: [{ label: "project", objectType: "WorkbenchSurface", objectRef: "project-console" }]
      },
      {
        id: "route-main-agent",
        title: "主 Agent",
        status: "ready",
        owner: "主 Agent",
        nextAction: "主 Agent 负责接收目标、拆任务、调度和追踪状态。",
        fallbackState: "主 Agent 不代替岗位 Agent 产出最终结论。",
        evidenceRefs: [{ label: "agent-hub", objectType: "Policy", objectRef: "docs/agent-team/company-agent-team-operating-guide.md" }]
      },
      {
        id: "route-role-agent",
        title: "岗位 Agent",
        status: metrics.onlineAgentSessionCount ? "ready" : "missing",
        owner: "岗位 Agent",
        nextAction: `在线岗位 Agent 会话 ${text(metrics.onlineAgentSessionCount ?? 0)} 个。`,
        fallbackState: "岗位 Agent 离线时，不展示为当前执行。",
        evidenceRefs: [{ label: "sessions", objectType: "WorkbenchSurface", objectRef: "agent-team-manager" }]
      },
      {
        id: "route-device",
        title: "本机设备",
        status: metrics.onlineDeviceCount ? "ready" : "offline",
        owner: "本机路由",
        nextAction: `已登记 ${text(metrics.onlineDeviceCount ?? 0)} 台本机设备；当前执行目标是本机设备。`,
        fallbackState: "设备心跳过期时，进入安全只读。",
        evidenceRefs: [{ label: "device", objectType: "WorkbenchSurface", objectRef: "runtime-monitor" }]
      },
      {
        id: "route-runner",
        title: "执行器 Runner",
        status: asArray(readModel.runnerLeases).length ? "ready" : "missing",
        owner: "执行器 Runner",
        nextAction: `租约记录 ${text(asArray(readModel.runnerLeases).length)} 条；心跳、范围和异常可查。`,
        fallbackState: "租约过期或失败时进入异常恢复。",
        evidenceRefs: [{ label: "runner", objectType: "WorkbenchSurface", objectRef: "agent-ring-console" }]
      },
      {
        id: "route-result",
        title: "任务结果记录",
        status: asArray(readModel.taskResults).length ? "ready" : "missing",
        owner: "项目经理 Agent",
        nextAction: `任务结果记录 ${text(asArray(readModel.taskResults).length)} 条；用于后续测试、产品和项目经理验收路由。`,
        fallbackState: "缺少结果证据时，不进入最终验收。",
        evidenceRefs: [{ label: "result", objectType: "TaskResult", objectRef: "result-center" }]
      },
      {
        id: "route-approval",
        title: "审批/权限",
        status: "ready",
        owner: "审批中心",
        nextAction: `审批 ${text(asArray(readModel.approvals).length)} 条，权限动作 ${text(asArray(readModel.permissionGatedActions).length)} 条。`,
        fallbackState: "权限失败时保留审计记录和防重复键。",
        evidenceRefs: [{ label: "approval", objectType: "WorkbenchSurface", objectRef: "review-center" }]
      },
      {
        id: "route-recovery",
        title: "异常恢复",
        status: problemCount ? "degraded" : "ready",
        owner: "异常恢复中心",
        nextAction: `异常入口 ${text(problemCount)} 个；失败、离线、重复回调可追溯。`,
        fallbackState: "不在前端静默重试或改写任务状态。",
        evidenceRefs: [{ label: "recovery", objectType: "WorkbenchSurface", objectRef: "recovery-center" }]
      }
    ];
  }

  function projectCreateInstruction(values) {
    return [
      "请主 Agent 在真知中枢创建项目，并按以下信息生成项目初始化任务链：",
      `项目名称：${values.name}`,
      `项目文件夹：${values.folder}`,
      `项目来源：${values.source}`,
      `V1 目标：${values.goal}`,
      `默认 Agent 队伍：${values.mainAgent}、${values.productAgent}、${values.developmentAgent}、${values.testAgent}`,
      `执行设备：${values.device}`,
      "创建方式：工作台向中枢提交项目创建申请；通过权限、确认、幂等和审计后，建立项目 -> 主 Agent -> 岗位 Agent -> 本机设备/执行器 -> 任务结果记录的路由链路。",
      "受控流程：填写信息后生成创建包，不直接创建项目，不直接写文件；由中枢登记后注册 Runner 范围并建立任务链。",
      "重要边界：工作台负责登记入口，不直接派单、不修复任务、不写回结果、不批准验收。"
    ].join("\n");
  }

  function projectCreatePackageTemplate() {
    const values = defaultProjectCreateValues;
    return `
      <section id="project-create-entry" class="project-create-entry" aria-labelledby="project-create-title">
        <div class="section-head">
          <div>
            <p class="eyebrow">项目启动</p>
            <h2 id="project-create-title">新建项目</h2>
            <p>一个项目建议放在一个独立文件夹；创建时还会在真知中枢注册项目记录，后续才会出现在项目选择器里。</p>
          </div>
          <span>登记入口</span>
        </div>
        <div class="project-create-grid">
          <form class="project-create-form" aria-label="新建项目表单">
            <label>
              <span>项目名称</span>
              <input id="project-create-name" type="text" value="${escapeHtml(values.name)}">
            </label>
            <label>
              <span>项目文件夹</span>
              <input id="project-create-folder" type="text" value="${escapeHtml(values.folder)}">
            </label>
            <label>
              <span>项目来源</span>
              <select id="project-create-source">
                <option selected>新项目</option>
                <option>已有 Git</option>
              </select>
            </label>
            <label>
              <span>V1 目标</span>
              <textarea id="project-create-goal" rows="3">${escapeHtml(values.goal)}</textarea>
            </label>
            <fieldset>
              <legend>默认 Agent 队伍</legend>
              <div class="agent-team-grid">
                <label><span>主 Agent</span><input id="project-create-main-agent" type="text" value="${escapeHtml(values.mainAgent)}"></label>
                <label><span>产品 Agent</span><input id="project-create-product-agent" type="text" value="${escapeHtml(values.productAgent)}"></label>
                <label><span>研发 Agent</span><input id="project-create-development-agent" type="text" value="${escapeHtml(values.developmentAgent)}"></label>
                <label><span>测试 Agent</span><input id="project-create-test-agent" type="text" value="${escapeHtml(values.testAgent)}"></label>
              </div>
            </fieldset>
            <label>
              <span>执行设备</span>
              <input id="project-create-device" type="text" value="${escapeHtml(values.device)}">
            </label>
          </form>
          <div class="project-create-preview" aria-label="项目创建包预览">
            <h3>项目创建包预览</h3>
            <p>提交给中枢后先生成项目登记记录；通过权限、确认、幂等和审计后，工作台项目选择器才会出现新项目。</p>
            <pre id="project-create-command">${escapeHtml(projectCreateInstruction(values))}</pre>
            <div class="project-create-actions">
              <button id="copy-project-create-command" class="secondary-button" type="button">复制创建指令</button>
              <button id="submit-project-create-request" class="secondary-button" type="button" disabled aria-disabled="true" title="提交到中枢后进入权限、确认、幂等和审计流程">交给主 Agent 创建（需中枢授权）</button>
            </div>
            <p id="project-create-copy-state" class="fallback">下一步：提交项目创建申请；通过后由项目经理 Agent 初始化团队、Runner 范围和任务链。</p>
          </div>
        </div>
      </section>
    `;
  }

  function collectProjectCreateValues() {
    const getValue = (id, fallback) => {
      const element = document.getElementById(id);
      const value = element && "value" in element ? element.value : "";
      return text(value).trim() || fallback;
    };
    return {
      name: getValue("project-create-name", defaultProjectCreateValues.name),
      folder: getValue("project-create-folder", defaultProjectCreateValues.folder),
      source: getValue("project-create-source", defaultProjectCreateValues.source),
      goal: getValue("project-create-goal", defaultProjectCreateValues.goal),
      mainAgent: getValue("project-create-main-agent", defaultProjectCreateValues.mainAgent),
      productAgent: getValue("project-create-product-agent", defaultProjectCreateValues.productAgent),
      developmentAgent: getValue("project-create-development-agent", defaultProjectCreateValues.developmentAgent),
      testAgent: getValue("project-create-test-agent", defaultProjectCreateValues.testAgent),
      device: getValue("project-create-device", defaultProjectCreateValues.device)
    };
  }

  function updateProjectCreatePreview() {
    const target = document.getElementById("project-create-command");
    if (target) target.textContent = projectCreateInstruction(collectProjectCreateValues());
  }

  function projectCreateRequestPayload(values) {
    const projectKey = values.name.toLowerCase().replace(/[^a-z0-9\u4e00-\u9fa5]+/g, "-").replace(/^-+|-+$/g, "") || "new-project";
    return {
      requestType: "project.create",
      idempotencyKey: `workbench:project-create:${projectKey}`,
      projectId: projectKey,
      name: values.name,
      owner: "user.workbench",
      sourceMode: values.source === "已有 Git" ? "local_repo" : "new_project",
      repositoryRefs: values.folder && values.folder !== defaultProjectCreateValues.folder ? [values.folder] : [],
      defaultAssignees: [values.mainAgent, values.productAgent, values.developmentAgent, values.testAgent],
      visibility: ["project.owner"],
      sensitivity: "internal",
      permissions: ["project.create"],
      goal: values.goal,
      initialDevice: values.device,
      boundary: "登记项目，不直接派单、不写回结果、不批准验收"
    };
  }

  async function submitProjectCreateRequest() {
    const state = document.getElementById("project-create-copy-state");
    const values = collectProjectCreateValues();
    const payload = projectCreateRequestPayload(values);
    const apiBase = text(readModel.environment && readModel.environment.apiBaseUrl).replace(/\/$/, "");
    if (!apiBase) {
      if (state) state.textContent = `已生成项目创建申请，等待中枢 API 接入。防重复键：${payload.idempotencyKey}`;
      return;
    }
    try {
      const response = await fetch(`${apiBase}/v0/workbench/projects`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      if (state) state.textContent = `项目创建申请已提交中枢；审批和审计记录生成后会出现在项目详情。防重复键：${payload.idempotencyKey}`;
    } catch (_error) {
      if (state) state.textContent = `中枢暂未接收申请；已保留申请摘要和防重复键：${payload.idempotencyKey}`;
    }
  }

  function attachWorkbenchRegistrationControls() {
    for (const button of root.querySelectorAll("[data-workbench-action]")) {
      button.addEventListener("click", () => {
        const label = button.textContent.trim() || "登记申请";
        const key = button.getAttribute("data-idempotency-key") || "等待中枢生成";
        const syncState = document.getElementById("sync-state");
        if (syncState) {
          syncState.textContent = `${label} 已进入中枢登记流程；防重复键：${key}`;
        }
      });
    }
  }

  function attachProjectCreateControls(surface) {
    if (surface !== "project-console") return;
    const form = document.getElementById("project-create-entry");
    if (form) form.addEventListener("input", updateProjectCreatePreview);
    const copyButton = document.getElementById("copy-project-create-command");
    if (!copyButton) return;
    copyButton.addEventListener("click", async () => {
      const command = projectCreateInstruction(collectProjectCreateValues());
      const state = document.getElementById("project-create-copy-state");
      try {
        if (navigator.clipboard && navigator.clipboard.writeText) {
          await navigator.clipboard.writeText(command);
        }
        if (state) state.textContent = "创建指令已复制；这只复制文本，未创建项目。";
      } catch (_error) {
        if (state) state.textContent = "复制受限；请手动选中项目创建包预览文本。";
      }
    });
    const submitButton = document.getElementById("submit-project-create-request");
    if (submitButton) submitButton.addEventListener("click", submitProjectCreateRequest);
  }

  function runtimeStageStrip() {
    return `
      <section class="stage-strip" aria-label="V1 单机闭环阶段">
        ${runtimeStages.map(([label, description]) => `
          <div>
            <strong>${escapeHtml(label)}</strong>
            <span>${escapeHtml(description)}</span>
          </div>
        `).join("")}
      </section>
    `;
  }

  function renderHome() {
    const acceptance = asArray(readModel.acceptanceEvidence);
    const messages = asArray(readModel.agentMessages).slice(-6).reverse().map(panelFromMessage);
    const problemLeases = asArray(readModel.runnerLeases)
      .filter((item) => ["stale", "failed", "offline", "blocked"].includes(item.status))
      .slice(0, 5)
      .map(panelFromLease);
    return `
      ${metricStrip()}
      ${runtimeStageStrip()}
      ${renderPMControl()}
      ${sectionTemplate("路由链路", routeStatusPanels(), "暂无路由链路", "路由已建好：项目 -> 主 Agent -> 岗位 Agent -> 本机设备 -> 执行器 Runner -> 任务结果记录 -> 审批/权限 -> 异常恢复。")}
      <div class="two-column">
        <div>
          ${sectionTemplate("验收证据", acceptance, "暂无验收证据", "展示证据入口；状态不是研发签收。")}
          ${sectionTemplate("最近路由", messages, "暂无路由消息", "本机设备路由已登记，目标设备字段只作为底层记录。")}
        </div>
        <div>
          ${sectionTemplate("异常提醒", problemLeases, "暂无异常执行器", "过期、失败、离线会进入异常恢复中心。")}
          ${sectionTemplate("审批/权限", asArray(readModel.approvals), "暂无待处理审批", "审批独立于验收。")}
        </div>
      </div>
    `;
  }

  function renderRuntimeMetrics() {
    return sectionTemplate("运行指标", Object.keys(readModel.runtimeMetrics || {}).map((key) => ({
      id: key,
      title: metricLabels[key] || key,
      status: "ready",
      owner: "运行监控",
      nextAction: metricValue(key, (readModel.runtimeMetrics || {})[key]),
      fallbackState: "指标来自中央状态记录；过期时只显示安全只读状态。",
      evidenceRefs: [{ label: key, objectRef: "runtimeMetrics" }]
    })), "暂无运行指标");
  }

  function renderSection(name) {
    if (name === "runtimeMetrics") return renderRuntimeMetrics();
    if (name === "collaborationWorkbench") return renderCollaborationWorkbench();
    if (name === "pmControl") return renderPMControl();
    if (name === "projectCreateEntry") return projectCreatePackageTemplate();
    if (name === "devices") return sectionTemplate("设备", asArray(readModel.devices).map(panelFromDevice), "暂无设备", "V1 只有本机；路由字段保留。");
    if (name === "agentSessions") return sectionTemplate("Agent 会话", asArray(readModel.agentSessions).map(panelFromSession), "暂无会话", "独立 Agent 会话注册到本机路由。");
    if (name === "agentMessages") return sectionTemplate("本机路由消息", asArray(readModel.agentMessages).slice(-16).reverse().map(panelFromMessage), "暂无消息", "显示消息类型、优先级、路由类型和目标设备。");
    if (name === "taskPackages") return sectionTemplate("任务包", asArray(readModel.taskPackages).slice(-12).reverse().map(panelFromPackage), "暂无任务包", "主 Agent 调度产物。");
    if (name === "worktrees") return sectionTemplate("隔离工作区", asArray(readModel.worktrees).map(panelFromWorktree), "暂无工作区", "并行执行隔离。");
    if (name === "taskFlow") return sectionTemplate("任务流转", asArray(readModel.taskFlow).slice(-20).reverse().map(panelFromTask), "暂无任务", "已关闭、已驳回、已取消、阻塞都显示 owner 与下一步。");
    if (name === "agentCurrentWork") return sectionTemplate("当前工作", asArray(readModel.agentCurrentWork), "暂无当前工作", "岗位 Agent 产物不能由主线程代签。");
    if (name === "acceptanceEvidence") return sectionTemplate("验收证据", asArray(readModel.acceptanceEvidence), "暂无验收证据", "展示产品、PM、测试证据入口，不替代验收。");
    if (name === "runnerLeases") return sectionTemplate("执行器 Runner 与租约", asArray(readModel.runnerLeases).map(panelFromLease), "暂无执行器", "显示租约、心跳、范围审计。");
    if (name === "runnerHistory") return sectionTemplate("执行器历史", asArray(readModel.runnerHistory).map(panelFromHistory), "暂无执行器历史", "历史只追溯，不覆盖当前。");
    if (name === "taskResults") return sectionTemplate("任务结果记录", asArray(readModel.taskResults).slice(-16).reverse().map(panelFromTaskResult), "暂无任务结果记录", "已提交=待评审；缺证据显式提示。");
    if (name === "approvals") return sectionTemplate("审批队列", asArray(readModel.approvals), "暂无审批", "confirm_request 与人工确认独立显示。");
    if (name === "permissionGatedActions") return sectionTemplate("权限动作", asArray(readModel.permissionGatedActions).map(actionPanel), "暂无权限动作", "服务端授权、审计记录和防重复记录必须齐全。");
    if (name === "settingsSecurity") return sectionTemplate("安全设置", asArray(readModel.settingsSecurity), "暂无安全设置", "凭证只存引用，不存原始 secret。");
    if (name === "recovery") return sectionTemplate("恢复入口", asArray(readModel.recovery), "暂无恢复项", "安全只读、离线、重复回调、同步失败都有可追溯入口。");
    if (name === "notifications") return sectionTemplate("通知", asArray(readModel.notifications), "暂无通知", "通知异常进入恢复中心。");
    if (name === "problemRunnerLeases") {
      return sectionTemplate("异常 Runner", asArray(readModel.runnerLeases)
        .filter((item) => ["stale", "failed", "offline", "blocked"].includes(item.status))
        .map(panelFromLease), "暂无异常执行器", "过期租约、失败执行器、离线心跳显式展示。");
    }
    if (name === "problemTasks") {
      return sectionTemplate("需 owner 处理的任务", asArray(readModel.taskFlow)
        .filter((item) => ["cancelled", "rejected", "blocked", "failed", "stale"].includes(item.status))
        .slice(-12)
        .reverse()
        .map(panelFromTask), "暂无异常任务", "取消/驳回/阻塞不自动恢复。");
    }
    return sectionTemplate(surfaceLabels[name] || name, asArray(readModel[name]), "暂无数据");
  }

  function surfaceHeading(surface) {
    const metrics = readModel.runtimeMetrics || {};
    const kind = readModel.runtimeReadModelKind || "fixture-read-model";
    return `
      <div class="surface-heading">
        <div>
          <p class="eyebrow">${escapeHtml(kind === liveReadModelKind ? "本机运行 · 登记入口 + 监管只读" : "安全基线")}</p>
          <h2>${escapeHtml(surfaceLabels[surface] || surface)}</h2>
        </div>
        <div class="health-strip">
          <span>未关闭 <strong>${escapeHtml(text(metrics.openTaskCount ?? "n/a"))}</strong></span>
          <span>本机设备 <strong>${escapeHtml(text(metrics.onlineDeviceCount ?? "n/a"))}</strong></span>
          <span>设备路由 <strong>${escapeHtml(text(metrics.messagesWithTargetDeviceId ?? "n/a"))}</strong></span>
          <span>验收证据 <strong>${escapeHtml(metricValue("productFinalAccepted", metrics.productFinalAccepted))}</strong></span>
        </div>
      </div>
    `;
  }

  function renderWorkbench(surface) {
    const sections = surface === "home" ? [] : (surfaceSections[surface] || ["projectProgress"]);
    root.innerHTML = surfaceHeading(surface) + (surface === "home" ? renderHome() : sections.map(renderSection).join(""));
    attachProjectCreateControls(surface);
    attachWorkbenchRegistrationControls();
    root.focus();
    for (const button of nav.querySelectorAll(".nav-button")) {
      button.setAttribute("aria-current", button.dataset.surface === surface ? "page" : "false");
    }
  }

  function initializeWorkbench() {
    if (!readModel || readModel.sourceOfTruth !== "central-api-read-model") {
      root.innerHTML = "<section class=\"surface-section\"><h2>安全只读</h2><p>未加载到真实 read model，状态变更动作已禁用。</p></section>";
      return;
    }

    const surfaces = primarySurfaces.filter((surface) => asArray(readModel.surfaces).includes(surface));
    nav.innerHTML = surfaces.map((surface) => `
      <button class="nav-button" type="button" data-surface="${escapeHtml(surface)}">${escapeHtml(surfaceLabels[surface] || surface)}</button>
    `).join("");

    nav.addEventListener("click", (event) => {
      const button = event.target.closest(".nav-button");
      if (button) renderWorkbench(button.dataset.surface);
    });

    if (newProjectEntry) {
      newProjectEntry.addEventListener("click", () => renderWorkbench("project-console"));
    }

    const runtime = readModel.localRuntime || {};
    const metrics = readModel.runtimeMetrics || {};
    const collaboration = readModel.collaborationWorkbench || {};
    const projectName = displayProject(readModel.projectId || "company-knowledge-core");
    if (projectSelect) {
      projectSelect.innerHTML = `<option value="${escapeHtml(readModel.projectId || "company-knowledge-core")}" selected>${escapeHtml(projectName)}</option>`;
      projectSelect.setAttribute("aria-label", "项目选择");
    }
    if (projectTitle) projectTitle.textContent = projectName;
    if (projectSummary) projectSummary.textContent = collaboration.activeRouteSummary
      ? `本机单机闭环工作台保留；协作状态：${collaboration.availableDeviceCountLabel || "0 台可接任务"}；${collaboration.activeRouteSummary}`
      : "本机单机闭环工作台；项目建议一个独立文件夹，并在真知中枢注册项目记录；当前只生成创建包，不直接创建项目。";
    runtimeSummary.innerHTML = `
      <span>${escapeHtml(runtime.kind === "static-file-workbench" ? "本地静态工作台" : "本机运行")}</span>
      <strong>${escapeHtml(readModel.runtimeReadModelKind === liveReadModelKind ? "只读状态" : "安全只读基线")}</strong>
      <span>${escapeHtml(readModel.runtimeReadModelKind === liveReadModelKind ? "数据来自中央状态记录" : "安全只读基线")}</span>
      <span>未关闭 ${escapeHtml(text(metrics.openTaskCount ?? "n/a"))}</span>
    `;
    syncState.textContent = "同步策略：状态过期显示安全只读；状态过期时不当作当前事实";
    packageBoundary.textContent = displayCopy(runtime.packagingBoundary || "本地工作台，可后续包装为 Tauri v2 或 Electron");
    renderWorkbench("home");
  }

  window.renderZhenzhiDesktopWorkbench = renderWorkbench;
  initializeWorkbench();
})();
