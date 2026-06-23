window.ZHENZHI_DESKTOP_WORKBENCH_READ_MODEL = {
  "schemaVersion": "desktop-workbench-read-model.v1",
  "projectId": "company-knowledge-core",
  "taskId": "kt-ai-native-os-impl-desktop-client-cross-platform",
  "sourceOfTruth": "central-api-read-model",
  "generatedAt": "2026-06-21T13:30:00Z",
  "staleStatePolicy": "show-safe-fallback-not-current",
  "localRuntime": {
    "kind": "static-file-workbench",
    "openPath": "projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.html",
    "packagingBoundary": "当前仓库没有 npm、Electron、Tauri、Rust 或签名工具链。本切片是与外壳无关的本地桌面工作台，可直接从磁盘打开，后续可包装为 Tauri v2 或 Electron。",
    "nextPackagingBoundary": [
      "确定 Tauri v2 或 Electron 的 Owner。",
      "补充已签名的 Mac 和 Windows 打包项目。",
      "接入实时中央 API 传输和安全存储插件。",
      "在两个平台运行安装、更新、跳转链接、通知、企业代理和执行器 Runner 配对冒烟测试。"
    ]
  },
  "platformCopy": {
    "mac": {
      "secureStorage": "凭证引用存入 Keychain；工作台不得保存原始 token。",
      "deepLink": "跳转链接在这台 Mac 上显示为已注册。",
      "background": "只有用户开启通知权限后，才允许显示 Dock 角标。"
    },
    "windows": {
      "secureStorage": "凭证引用存入 Windows Credential Manager；工作台不得保存原始 token。",
      "deepLink": "跳转链接在这台 Windows 电脑上显示为已注册。",
      "background": "只有后台运行能力开启后，才允许在系统托盘显示执行器 Runner 状态。"
    }
  },
  "surfaces": [
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
    "recovery-center"
  ],
  "home": [
    {
      "id": "release-readiness",
      "title": "发布准备状态",
      "status": "blocked",
      "owner": "项目经理 Agent",
      "nextAction": "查看桌面运行证据，再安排跨平台打包证明。",
      "fallbackState": "中央状态同步过期时，只显示阻塞摘要。",
      "evidenceRefs": [
        {"label": "缺口验收标准", "objectType": "ProductReview", "objectRef": "projects/company-knowledge-core/product-reviews/ai-native-os-full-product-gap-acceptance-criteria.md"}
      ]
    },
    {
      "id": "agent-focus",
      "title": "Agent 当前重点",
      "status": "running",
      "owner": "研发 Agent",
      "nextAction": "完成桌面工作台实现证据，并交给测试 Agent 回归。",
      "fallbackState": "只显示最近一次已核验的 AgentRun，不把缓存任务当作当前执行。",
      "evidenceRefs": [
        {"label": "实现任务", "objectType": "ProjectTask", "objectRef": "projects/company-knowledge-core/tasks/kt-ai-native-os-impl-desktop-client-cross-platform.md"}
      ]
    },
    {
      "id": "attention",
      "title": "待处理事项",
      "status": "needs_permission",
      "owner": "人工审核人",
      "nextAction": "处理审批回调或权限拒绝。",
      "fallbackState": "回调重复或过期时，进入异常恢复中心。",
      "evidenceRefs": [
        {"label": "审批中心", "objectType": "WorkbenchSurface", "objectRef": "review-center"}
      ]
    }
  ],
  "projectProgress": [
    {
      "id": "gap-002",
      "title": "GAP-002 跨平台桌面客户端",
      "status": "running",
      "owner": "研发 Agent",
      "nextAction": "提供可运行的桌面工作台切片和打包边界说明。",
      "fallbackState": "签名版 Mac 和 Windows 打包证明完成前，只能算部分完成。",
      "evidenceRefs": [
        {"label": "已接受的方案评审", "objectType": "ProductReview", "objectRef": "projects/company-knowledge-core/product-reviews/ai-native-os-full-product-gap-solution-product-review.md"}
      ]
    },
    {
      "id": "acceptance-route",
      "title": "验收路由",
      "status": "waiting_review",
      "owner": "测试 Agent",
      "nextAction": "运行桌面工作台校验和产品证据矩阵。",
      "fallbackState": "缺少测试 Agent 结果前，不释放项目经理最终验收。",
      "evidenceRefs": [
        {"label": "配套测试任务", "objectType": "ProjectTask", "objectRef": "kt-ai-native-os-test-desktop-client-cross-platform"}
      ]
    }
  ],
  "agentCurrentWork": [
    {
      "id": "current-task",
      "title": "桌面客户端实现",
      "status": "running",
      "owner": "agent.company.development",
      "nextAction": "提交任务结果记录，附带校验器和测试证据。",
      "fallbackState": "租约丢失时，先显示恢复步骤再重试。",
      "evidenceRefs": [
        {"label": "任务结果记录目标", "objectType": "TaskResult", "objectRef": "task-results/tr-kt-ai-native-os-impl-desktop-client-cross-platform.md"}
      ]
    },
    {
      "id": "work-timeline",
      "title": "工作时间线",
      "status": "ready",
      "owner": "主 Agent",
      "nextAction": "读取上下文、实现、校验、写入任务结果记录并交接。",
      "fallbackState": "中央 API 不可用时，时间线保持只读。",
      "evidenceRefs": [
        {"label": "运行契约", "objectType": "Policy", "objectRef": "docs/agent-team/agent-task-runtime-contract.md"}
      ]
    }
  ],
  "runnerLeases": [
    {
      "runner": {"label": "本机桌面执行器 Runner", "objectType": "AgentRunner", "objectRef": "runner.meimei-mac-local-dev"},
      "lease": {"label": "桌面客户端实现租约", "objectType": "ProjectTaskLease", "objectRef": "lease.kt-ai-native-os-impl-desktop-client-cross-platform"},
      "status": "active",
      "heartbeat": "online",
      "nextAction": "继续在仓库范围内实现。",
      "scopeAudit": {
        "id": "scope-audit-local",
        "title": "执行器 Runner 范围和审计",
        "status": "ready",
        "owner": "调度器",
        "nextAction": "只允许修改 desktop-workbench-slice0、直接桌面校验脚本、任务结果记录和审计记录。",
        "fallbackState": "阻止超出任务范围的资料、仓库、工具或知识写入。",
        "evidenceRefs": [
          {"label": "执行器范围规则", "objectType": "Policy", "objectRef": "runner_scope_required"}
        ]
      }
    },
    {
      "runner": {"label": "Windows 打包执行器 Runner", "objectType": "AgentRunner", "objectRef": "runner.windows-signing-required"},
      "lease": {"label": "后续 Windows 打包证明租约", "objectType": "ProjectTaskLease", "objectRef": "lease.pending-windows-package-proof"},
      "status": "stale",
      "heartbeat": "offline",
      "nextAction": "补齐 Windows 执行器、证书 Owner、安装器策略和冒烟矩阵。",
      "scopeAudit": {
        "id": "scope-audit-windows",
        "title": "过期租约恢复",
        "status": "stale",
        "owner": "项目经理 Agent",
        "nextAction": "把过期打包证明升级处理，不静默重试。",
        "fallbackState": "明确展示打包阻塞。",
        "evidenceRefs": [
          {"label": "Slice 0 检查清单", "objectType": "Workflow", "objectRef": "projects/company-knowledge-core/desktop-workbench-slice0/slice0-proof-checklist.json"}
        ]
      }
    }
  ],
  "runnerHistory": [
    {"label": "实现进行中", "status": "active", "nextAction": "继续"},
    {"label": "Slice 0 测试", "status": "completed", "nextAction": "作为基线"},
    {"label": "Windows 证明", "status": "stale", "nextAction": "升级处理"},
    {"label": "重复回调", "status": "failed", "nextAction": "打开异常恢复中心"},
    {"label": "打包重试", "status": "retried", "nextAction": "要求防重复键"},
    {"label": "权限拒绝", "status": "escalated", "nextAction": "展示可读拒绝原因"}
  ],
  "approvals": [
    {
      "id": "approval-callback",
      "title": "审批回调",
      "status": "waiting_review",
      "owner": "人工审核人",
      "nextAction": "查看证据预览后批准或要求修改，再回到主窗口。",
      "fallbackState": "回调重复时，显示上一次决定和审计记录。",
      "evidenceRefs": [
        {"label": "人类验收策略", "objectType": "Policy", "objectRef": "docs/agent-team/human-acceptance-policy.md"}
      ]
    },
    {
      "id": "permission-gate",
      "title": "权限拒绝恢复",
      "status": "needs_permission",
      "owner": "系统管理员",
      "nextAction": "从服务端权限策略申请执行器范围或工具 Owner 批准。",
      "fallbackState": "服务端返回授权前，禁用会改状态的按钮。",
      "evidenceRefs": [
        {"label": "审计事件", "objectType": "AuditLog", "objectRef": "audit.permission.denied.desktop"}
      ]
    }
  ],
  "notifications": [
    {
      "id": "review-needed",
      "title": "需要审核",
      "status": "ready",
      "owner": "通知中心",
      "nextAction": "用户开启系统通知权限后再发送通知。",
      "fallbackState": "系统通知不可用时，使用工作台内通知中心。",
      "evidenceRefs": [
        {"label": "通知记录", "objectType": "NotificationRecord", "objectRef": "notification.desktop.review-needed"}
      ]
    },
    {
      "id": "sync-failed",
      "title": "同步失败",
      "status": "degraded",
      "owner": "运维 Agent",
      "nextAction": "打开异常恢复中心，查看已脱敏诊断。",
      "fallbackState": "企业代理状态可见前，不在后台反复重试。",
      "evidenceRefs": [
        {"label": "诊断记录", "objectType": "AuditLog", "objectRef": "audit.desktop.sync-failed"}
      ]
    }
  ],
  "recovery": [
    {
      "id": "offline",
      "title": "中央 API 离线",
      "status": "offline",
      "owner": "运维 Agent",
      "nextAction": "显示最近同步时间，并禁用会改状态的动作。",
      "fallbackState": "进入安全只读模式。",
      "evidenceRefs": [
        {"label": "网络策略", "objectType": "Policy", "objectRef": "enterprise_network_proxy"}
      ]
    },
    {
      "id": "failed-sync",
      "title": "同步失败",
      "status": "failed",
      "owner": "运维 Agent",
      "nextAction": "收集已脱敏诊断，并保留审计记录。",
      "fallbackState": "诊断中不得包含 token、原始正文或原始文件。",
      "evidenceRefs": [
        {"label": "桥接清单", "objectType": "Manifest", "objectRef": "projects/company-knowledge-core/desktop-workbench-slice0/native-bridge-manifest.json"}
      ]
    },
    {
      "id": "duplicate-callback",
      "title": "重复回调",
      "status": "safe_fallback",
      "owner": "审批中心",
      "nextAction": "显示已生效决定，并阻止重复写入。",
      "fallbackState": "任何重试都必须带防重复键。",
      "evidenceRefs": [
        {"label": "回调状态", "objectType": "Decision", "objectRef": "decision.approval.callback.idempotent"}
      ]
    }
  ],
  "settingsSecurity": [
    {
      "id": "secure-storage",
      "title": "安全凭证存储",
      "status": "needs_permission",
      "owner": "系统管理员",
      "nextAction": "系统授权和中央审计通过后，只保存凭证引用。",
      "fallbackState": "安全存储不可用时，使用仅本次会话模式。",
      "evidenceRefs": [
        {"label": "桥接权限", "objectType": "NativeBridgeCommand", "objectRef": "storeCredentialReference"}
      ]
    },
    {
      "id": "deep-link",
      "title": "跳转链接",
      "status": "ready",
      "owner": "桌面工作台",
      "nextAction": "通过中央 API 解析审批和执行器配对链接。",
      "fallbackState": "链接解析失败时，不改写租约状态。",
      "evidenceRefs": [
        {"label": "桥接权限", "objectType": "NativeBridgeCommand", "objectRef": "resolveDeepLink"}
      ]
    },
    {
      "id": "enterprise-proxy",
      "title": "企业网络",
      "status": "degraded",
      "owner": "运维 Agent",
      "nextAction": "重试前展示代理、VPN 和自定义证书诊断。",
      "fallbackState": "网络状态可见前暂停重试。",
      "evidenceRefs": [
        {"label": "Slice 0 证明门", "objectType": "WorkflowGate", "objectRef": "enterprise-network-proxy"}
      ]
    }
  ],
  "collaborationWorkbench": {
    "entryLabel": "协作设备",
    "projectJoinPolicyLabel": "创建项目、邀请电脑、提交电脑注册申请、登记低风险工具、申请高风险工具；运行中的任务状态只看不改。",
    "readOnlyNotice": "登记入口可提交申请；任务派发、修复、结果写回和验收结论不在工作台直接操作。",
    "availableDeviceCountLabel": "2 台可接任务",
    "activeRouteSummary": "2 个任务执行中，1 个等待授权，1 个等待验收。",
    "summary": {
      "availableDeviceCountLabel": "2 台",
      "runningTaskCountLabel": "2 项",
      "pendingAuthorizationCountLabel": "1 项",
      "riskCountLabel": "2 项"
    },
    "primaryActions": [
      {"label": "创建项目", "permission": "project.create", "serverGate": "required", "idempotencyKey": "workbench:create-project:company-knowledge-core", "auditRef": "audit.workbench.project-create"},
      {"label": "邀请电脑", "permission": "runner.invitation.create", "serverGate": "required", "idempotencyKey": "workbench:runner-invite:company-knowledge-core", "auditRef": "audit.workbench.runner-invite"},
      {"label": "提交电脑注册申请", "permission": "runner.registration.submit", "serverGate": "required", "idempotencyKey": "workbench:runner-register:company-knowledge-core", "auditRef": "audit.workbench.runner-register"},
      {"label": "登记低风险工具", "permission": "tool.register.low_risk", "serverGate": "required", "idempotencyKey": "workbench:tool-register:company-knowledge-core", "auditRef": "audit.workbench.tool-register"},
      {"label": "提交工具申请", "permission": "tool.registration_request.create", "serverGate": "required", "idempotencyKey": "workbench:tool-request:company-knowledge-core", "auditRef": "audit.workbench.tool-request"}
    ],
    "registrationEntries": [
      {
        "title": "创建项目",
        "description": "登记项目名称、目标、负责人、资料范围和默认治理规则；创建后进入项目选择器。",
        "status": "ready",
        "statusLabel": "可提交",
        "apiPath": "/v0/workbench/projects",
        "confirmationLabel": "确认项目名称、Owner、可见范围、仓库范围和敏感级别。",
        "guardrailLabel": "只创建项目登记，不直接派发任务。",
        "auditLabel": "提交、审批、拒绝和范围变更都会写审计。",
        "primaryAction": {"label": "创建项目", "permission": "project.create", "serverGate": "required", "idempotencyKey": "workbench:create-project:company-knowledge-core", "auditRef": "audit.workbench.project-create"}
      },
      {
        "title": "邀请电脑",
        "description": "生成短期配对码和接入范围；配对码只用于首次注册，不直接领取任务。",
        "status": "needs_permission",
        "statusLabel": "需授权",
        "apiPath": "/v0/workbench/runner-invitations",
        "confirmationLabel": "确认项目范围、Runner Owner、能力范围、资料范围和有效期。",
        "guardrailLabel": "邀请不会自动授权电脑接任务；中枢只保存配对码哈希。",
        "auditLabel": "邀请、过期、消费和拒绝都会写审计。",
        "primaryAction": {"label": "邀请电脑", "permission": "runner.invitation.create", "serverGate": "required", "idempotencyKey": "workbench:runner-invite:company-knowledge-core", "auditRef": "audit.workbench.runner-invite"}
      },
      {
        "title": "提交电脑注册申请",
        "description": "Runner 上报机器摘要、Owner、客户端版本、Agent、Codex/Claude/本地模型能力、工具和仓库范围。",
        "status": "pending_authorization",
        "statusLabel": "等待授权",
        "apiPath": "/v0/runners/register",
        "confirmationLabel": "确认申请范围没有超过邀请范围；重复设备、过期邀请和越权申请必须可读提示。",
        "guardrailLabel": "未授权电脑保持 pending_authorization，不获得项目可调度范围。",
        "auditLabel": "注册申请、配对消费、授权和拒绝都会写审计。",
        "primaryAction": {"label": "提交电脑注册申请", "permission": "runner.registration.submit", "serverGate": "required", "idempotencyKey": "workbench:runner-register:company-knowledge-core", "auditRef": "audit.workbench.runner-register"}
      },
      {
        "title": "登记低风险工具",
        "description": "登记只读、低风险、无密钥工具名称、用途、版本、操作范围和 Runner 范围。",
        "status": "ready",
        "statusLabel": "可登记",
        "apiPath": "/v0/workbench/tools",
        "confirmationLabel": "确认工具不含密钥、不扩大项目权限、不接收自由 shell 片段。",
        "guardrailLabel": "只登记能力；具体电脑可用性仍由 Runner 健康上报。",
        "auditLabel": "工具登记和范围变更都会写审计。",
        "primaryAction": {"label": "登记低风险工具", "permission": "tool.register.low_risk", "serverGate": "required", "idempotencyKey": "workbench:tool-register:company-knowledge-core", "auditRef": "audit.workbench.tool-register"}
      },
      {
        "title": "提交工具申请",
        "description": "写权限、外部 API、需要凭据或高风险工具先进入审批申请，不会直接启用。",
        "status": "waiting_review",
        "statusLabel": "走审批",
        "apiPath": "/v0/workbench/tool-registration-requests",
        "confirmationLabel": "确认可执行操作、项目范围、Runner 范围、数据范围、有效期、风险和撤销路径。",
        "guardrailLabel": "高风险工具不会直接启用，必须由工具负责人或系统管理员审批。",
        "auditLabel": "工具申请、审批、拒绝和授权范围都会写审计。",
        "primaryAction": {"label": "提交工具申请", "permission": "tool.registration_request.create", "serverGate": "required", "idempotencyKey": "workbench:tool-request:company-knowledge-core", "auditRef": "audit.workbench.tool-request"}
      }
    ],
    "pairingRequests": [
      {
        "displayTitle": "同事电脑请求接入",
        "requesterLabel": "李四",
        "deviceLabel": "李四的 Windows 工作站",
        "status": "pending_authorization",
        "statusLabel": "等待授权",
        "scopeSummary": "申请测试、资料整理和只读项目资料。",
        "riskLabel": "需要项目负责人确认代码仓库访问。",
        "primaryAction": {"label": "确认授权", "permission": "collaboration.authorization.confirm", "serverGate": "required", "idempotencyKey": "workbench:runner-authorization:lisi-windows", "auditRef": "audit.workbench.runner-authorization", "disabledReason": "安全只读基线仅展示申请"}
      }
    ],
    "devices": [
      {
        "displayName": "张三的 MacBook Pro",
        "ownerLabel": "张三",
        "status": "ready",
        "availabilityLabel": "可接任务",
        "workTypeLabels": ["开发", "测试"],
        "authorizationSummary": "当前项目 + 指定代码仓库 + 项目资料",
        "currentTaskLabel": "阶段二工作台研发切片",
        "activeAgentLabels": ["研发 Agent", "测试 Agent"],
        "toolLabels": ["Codex", "git", "pytest"],
        "executorLabel": "Codex",
        "modelUsageLabel": "gpt-5.5",
        "tokenUsageLabel": "输入 18.2k / 输出 4.1k / 总计 22.3k",
        "lastSeenLabel": "刚刚",
        "riskLabels": [],
        "primaryAction": {"label": "查看", "permission": "collaboration.device.view", "serverGate": "required"}
      },
      {
        "displayName": "李四的 Windows 工作站",
        "ownerLabel": "李四",
        "status": "pending_authorization",
        "availabilityLabel": "等待授权",
        "workTypeLabels": ["测试", "资料整理"],
        "authorizationSummary": "等待确认仓库和资料范围",
        "currentTaskLabel": "暂无任务",
        "activeAgentLabels": ["测试 Agent"],
        "toolLabels": ["Claude", "浏览器检查"],
        "executorLabel": "Claude",
        "modelUsageLabel": "Claude Sonnet",
        "tokenUsageLabel": "尚未开始",
        "lastSeenLabel": "5 分钟前",
        "riskLabels": ["权限不足"],
        "primaryAction": {"label": "确认授权", "permission": "collaboration.authorization.confirm", "serverGate": "required", "idempotencyKey": "workbench:runner-authorization:lisi-windows", "auditRef": "audit.workbench.runner-authorization", "disabledReason": "安全只读基线仅展示申请"}
      },
      {
        "displayName": "王五的 Linux 电脑",
        "ownerLabel": "王五",
        "status": "offline",
        "availabilityLabel": "离线",
        "workTypeLabels": ["开发"],
        "authorizationSummary": "当前项目 + 只读代码仓库",
        "currentTaskLabel": "结果暂未同步完成",
        "activeAgentLabels": ["研发 Agent"],
        "toolLabels": ["Codex", "git"],
        "executorLabel": "Codex",
        "modelUsageLabel": "gpt-5.4",
        "tokenUsageLabel": "上次上报 7.6k",
        "lastSeenLabel": "18 分钟前",
        "riskLabels": ["只读", "回传失败"],
        "primaryAction": {"label": "创建恢复请求", "permission": "recovery.request.create", "serverGate": "required", "idempotencyKey": "workbench:recovery-request:writeback-failed", "auditRef": "audit.workbench.recovery-request", "disabledReason": "需要 Scheduler 确认旧任务占用状态"}
      }
    ],
    "runners": [
      {"displayName": "张三电脑上的 Codex 执行入口", "ownerLabel": "张三", "availabilityLabel": "可接任务"},
      {"displayName": "李四电脑上的测试执行入口", "ownerLabel": "李四", "availabilityLabel": "等待授权"}
    ],
    "routeBoard": [
      {
        "taskLabel": "阶段二工作台研发切片",
        "requirementLabel": "阶段二方案二中枢监管",
        "status": "processing",
        "businessStatus": "执行中",
        "assignedDeviceLabel": "张三的 MacBook Pro",
        "activeAgentLabel": "研发 Agent",
        "executorLabel": "Codex",
        "modelLabel": "gpt-5.5",
        "tokenUsageLabel": "22.3k token",
        "toolUsageLabel": "git、pytest、浏览器检查",
        "routeReason": "具备开发能力，已授权当前项目，设备在线且负载较低。",
        "blockerLabel": "暂无卡点",
        "nextOwnerLabel": "研发 Agent",
        "nextAction": "提交任务结果后交测试 Agent 验收"
      },
      {
        "taskLabel": "多设备路由验收",
        "requirementLabel": "真实双机 Runner 验收",
        "status": "pending_authorization",
        "businessStatus": "等待授权",
        "assignedDeviceLabel": "李四的 Windows 工作站",
        "activeAgentLabel": "测试 Agent",
        "executorLabel": "Claude",
        "modelLabel": "Claude Sonnet",
        "tokenUsageLabel": "未开始",
        "toolUsageLabel": "浏览器检查、测试脚本",
        "routeReason": "具备测试能力，但需要负责人确认仓库访问。",
        "blockerLabel": "等待项目负责人授权",
        "nextOwnerLabel": "项目负责人",
        "nextAction": "确认授权或换一台可执行电脑"
      },
      {
        "taskLabel": "回传失败恢复演练",
        "requirementLabel": "异常恢复能力",
        "status": "writeback_failed",
        "businessStatus": "结果暂未同步完成",
        "assignedDeviceLabel": "王五的 Linux 电脑",
        "activeAgentLabel": "研发 Agent",
        "executorLabel": "Codex",
        "modelLabel": "gpt-5.4",
        "tokenUsageLabel": "7.6k token",
        "toolUsageLabel": "git、单元测试",
        "routeReason": "原设备持有任务占用，但心跳已过期。",
        "blockerLabel": "同事电脑离线，结果证据未完整回传",
        "nextOwnerLabel": "项目经理 Agent",
        "nextAction": "创建恢复请求，由 Scheduler 决定等待、转交或取消"
      }
    ],
    "recoveryItems": [
      {
        "title": "同事电脑暂时离线",
        "status": "recovery_pending",
        "statusLabel": "等待恢复",
        "impactLabel": "回传失败恢复演练不会继续在这台电脑上执行",
        "ownerLabel": "项目经理 Agent",
        "displayMessage": "任务不会永久停在执行中；需要确认等待、转交或取消。",
        "nextAction": "释放任务占用并重新匹配可执行电脑"
      },
      {
        "title": "这台电脑不能读取当前任务所需资料",
        "status": "blocked",
        "statusLabel": "权限不足",
        "impactLabel": "不会产生任务结果",
        "ownerLabel": "项目负责人",
        "displayMessage": "缺少资料范围授权；可发起授权或换设备。",
        "nextAction": "发起授权"
      }
    ],
    "evidenceItems": [
      {"title": "任务结果已回传", "statusLabel": "待验收", "summary": "任务结果、执行记录、检查项和证据入口已登记。"}
    ],
    "auditSummaries": [
      {"actorLabel": "项目负责人", "actionLabel": "确认授权", "targetLabel": "张三的 MacBook Pro", "impactLabel": "允许执行开发和测试任务", "resultLabel": "已记录"},
      {"actorLabel": "项目经理 Agent", "actionLabel": "创建恢复请求", "targetLabel": "回传失败恢复演练", "impactLabel": "旧任务占用进入等待恢复", "resultLabel": "待处理"}
    ],
    "technicalDetails": [
      {"label": "脱敏设备引用", "redactedValue": "dev-***-mac"},
      {"label": "脱敏任务占用引用", "redactedValue": "lease-***-recovery"},
      {"label": "脱敏执行记录引用", "redactedValue": "run-***-phase2"}
    ]
  },
  "pmControl": {
    "currentLease": {
      "primaryPm": {"label": "项目经理 Agent", "objectType": "Agent", "objectRef": "agent.company.project-manager"},
      "lease": {"label": "当前 PM 主控租约", "objectType": "PMControlLease", "objectRef": "projects/company-knowledge-core/pm-control-leases/current"},
      "project": {"label": "真知公司知识核心", "objectType": "Project", "objectRef": "projects/company-knowledge-core/project.md"},
      "status": "healthy",
      "heartbeat": "online",
      "expiresAt": "2026-06-23T23:59:00Z",
      "lastHeartbeatAt": "2026-06-23T23:45:00Z",
      "leaseGenerationLabel": "已记录防旧写入代际",
      "nextAction": "只有当前主控 PM 可以改项目调度。",
      "releaseAction": {"id": "pm-control-release", "label": "释放主控", "permission": "pm_control_lease.release", "idempotencyKey": "desktop:pm-release:company-knowledge-core", "serverGate": "required", "auditRef": "audit.pm-control-release"},
      "auditRefs": [{"label": "PM 租约审计", "objectType": "AuditLog", "objectRef": "audit.pm-control.acquired"}]
    },
    "participants": [
      {"pm": {"label": "项目经理 Agent", "objectType": "Agent", "objectRef": "agent.company.project-manager"}, "role": "primary", "status": "running", "runner": {"label": "本机桌面执行器 Runner", "objectType": "AgentRunner", "objectRef": "runner.meimei-mac-local-dev"}, "device": {"label": "本机设备", "objectType": "AgentDevice", "objectRef": "device.local"}, "standbyPriority": 0, "capabilities": ["project_management", "scheduler"], "nextAction": "持有主控租约，可写项目调度。"},
      {"pm": {"label": "产品经理 Agent", "objectType": "Agent", "objectRef": "agent.company.product-manager"}, "role": "collaborator", "status": "ready", "runner": {"label": "产品协作会话", "objectType": "AgentRunner", "objectRef": "runner.product"}, "device": {"label": "本机设备", "objectType": "AgentDevice", "objectRef": "device.local"}, "standbyPriority": 0, "capabilities": ["product_management"], "nextAction": "可查看项目并准备建议；写入需主控合并或接管。"},
      {"pm": {"label": "备用项目经理 Agent", "objectType": "Agent", "objectRef": "agent.company.project-manager.standby"}, "role": "standby", "status": "ready", "runner": {"label": "备用电脑", "objectType": "AgentRunner", "objectRef": "runner.pm-standby"}, "device": {"label": "备用电脑", "objectType": "AgentDevice", "objectRef": "device.pm-standby"}, "standbyPriority": 1, "capabilities": ["project_management", "scheduler"], "nextAction": "主控失联或释放后可接管。"}
    ],
    "takeoverRecords": [
      {"recordRef": "projects/company-knowledge-core/pm-takeovers/pmtakeover.demo.md", "occurredAt": "2026-06-23T10:00:00Z", "fromPm": {"label": "旧项目经理 Agent", "objectType": "Agent", "objectRef": "agent.company.project-manager.old"}, "toPm": {"label": "项目经理 Agent", "objectType": "Agent", "objectRef": "agent.company.project-manager"}, "operator": "项目 Owner", "reason": "主控租约过期后恢复调度", "previousLeaseStatus": "expired", "newLeaseIdLabel": "已生成新主控租约", "auditRef": {"label": "接管审计", "objectType": "AuditLog", "objectRef": "audit.pm-control.taken-over"}}
    ],
    "denialSummaries": [
      {"auditRef": "knowledge/audit/audit.pm-control-denied-demo.md", "timestamp": "2026-06-23T10:05:00Z", "requestPm": {"label": "协同 PM：产品经理 Agent", "objectType": "Agent", "objectRef": "agent.company.product-manager"}, "action": "task.create", "reasonCode": "pm_control_lease_not_primary", "displayMessage": "写入被拒绝：你不是当前主控 PM。当前主控是项目经理 Agent。", "nextAction": "联系主控 PM 合并，或在主控失联后发起接管。"}
    ],
    "healthExplanation": {"id": "pm-control-health", "title": "PM 主控租约", "status": "ready", "owner": "项目经理 Agent", "nextAction": "当前由项目经理 Agent 主控此项目，租约健康。其他 PM 可以查看和准备建议，但不能直接改项目调度。", "fallbackState": "状态过期时只显示安全只读，不允许前端写调度。", "evidenceRefs": [{"label": "PM 租约审计", "objectType": "AuditLog", "objectRef": "audit.pm-control.acquired"}]}
  },
  "permissionGatedActions": [
    {
      "id": "pm-control-release",
      "label": "释放主控",
      "permission": "pm_control_lease.release",
      "idempotencyKey": "desktop:pm-release:company-knowledge-core",
      "serverGate": "required",
      "auditRef": "audit.pm-control-release"
    },
    {
      "id": "retry-sync",
      "label": "重试同步",
      "permission": "central-api.status.retry",
      "idempotencyKey": "desktop:retry-sync:kt-ai-native-os-impl-desktop-client-cross-platform",
      "serverGate": "required",
      "auditRef": "audit.desktop.retry-sync"
    },
    {
      "id": "resolve-approval-callback",
      "label": "处理回调",
      "permission": "approval.callback.resolve",
      "idempotencyKey": "desktop:approval-callback:review-needed",
      "serverGate": "required",
      "auditRef": "audit.desktop.approval-callback"
    },
    {
      "id": "handoff-runner-pairing",
      "label": "交接执行器配对",
      "permission": "runner.pairing.handoff",
      "idempotencyKey": "desktop:runner-pairing:local-dev",
      "serverGate": "required",
      "auditRef": "audit.desktop.runner-pairing"
    }
  ]
};
