---
type: Workflow
title: V1 工作台 Codex 风格中文实现方案
projectId: company-knowledge-core
taskId: kt-v1-workbench-codex-style-dev
agentId: agent.company.development
status: submitted
language: zh-CN
createdAt: "2026-06-22"
sourceRefs:
  - projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-dev.md
  - projects/company-knowledge-core/design/v1-workbench-codex-style-design.md
  - projects/company-knowledge-core/reviews/v1-workbench-codex-style-product-review.md
  - task-results/tr-kt-v1-workbench-codex-style-design.md
  - task-results/tr-kt-v1-workbench-codex-style-product-review.md
  - /Users/meimei/Downloads/AI_Native_Agent协同系统_PRD_V1.0.docx
  - /Users/meimei/Downloads/AI_Native_Agent协同系统_技术方案_V1.0.docx
outputRefs:
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.html
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.css
operatingRuleRefs:
  companyConstitution: docs/agent-team/company-agent-constitution.md
  taskRuntimeContract: docs/agent-team/agent-task-runtime-contract.md
  humanAcceptancePolicy: docs/agent-team/human-acceptance-policy.md
  commonRules: docs/agent-team/common-agent-operating-rules.md
  roleOperatingSpec: docs/agent-team/role-operating-specs.json
  roleRules: agents/agent.company.development.md
  projectRules: projects/company-knowledge-core/project.md
---

# V1 工作台 Codex 风格中文实现方案

## 研发边界

本任务只负责研发技术方案、工作台实现和自测证据。`submitted` 表示产物已提交等待后续岗位评审，不表示已验收。产品最终验收、PM 流程验收、测试闭环验收必须继续由对应 Agent 或人类 owner 判断。

工作台必须读取 `workbench-live-read-model.js` 覆盖后的真实 V1 runtime read model。静态 `workbench-read-model.js` 只作为结构基线和无 live 数据时的安全只读退路。

## 实现策略

1. 保留本地静态 HTML/CSS/JS 形态，不引入外部依赖，继续满足 Slice 0 可从磁盘打开的包装边界。
2. Shell 启动时以 `window.ZHENZHI_DESKTOP_WORKBENCH_READ_MODEL` 为唯一读取入口，且 HTML 加载顺序保持 `workbench-read-model.js` 后接 `workbench-live-read-model.js`，保证真实 live read model 覆盖基线。
3. 所有状态卡统一展示：中文状态、owner、下一步、fallback、证据引用、证据缺失提示。缺 `outputRef`、`evidenceRef`、`testsOrChecks`、`operatingRuleRefs`、`commonRulesEvaluation` 时显式提示。
4. 单机 V1 只显示 `device.local`，但设备、会话、消息、任务包和 worktree 均保留 `targetDeviceId`、`routeType`、`deviceId` 等路由字段，为 Hub 扩展准备。
5. 审批/权限独立于验收中心展示。审批动作只显示 server gate、permission、idempotencyKey、auditRef，不在前端执行状态写入。
6. 异常恢复独立展示 stale lease、failed runner、offline heartbeat、cancelled/rejected/blocked、通知异常和 safe fallback，不能把过期缓存写成当前状态。

## 覆盖矩阵

| 来源要求 | 产品评审要求 | 实现位置 | 校验方式 | 状态 |
| --- | --- | --- | --- | --- |
| PRD：V1 第一阶段先跑通“一台机器上的多个独立 Agent 会话 + Local Router + 组 Agent 调度”闭环。 | 工作台必须整体升级到 V1 单机闭环，不是逐条开发昨日 74 项。 | `workbench-shell.js` 首页、运行监控、Agent、Runner、任务流、结果中心；`workbench-live-read-model.js` 真实数据。 | `validate_desktop_workbench_slice0.py`、`tests.test_desktop_workbench_slice0`、live metrics 自测。 | implemented, self-tested |
| PRD：本机会话通信为后续跨设备 Hub 路由打基础。 | 单机设备路由必须展示 devices、sessions、messages，设备只有本机但 route 字段保留。 | 运行监控页设备、Agent 会话、Local Router 消息、任务包、worktree；消息卡展示 `routeType` 和 `targetDeviceId`。 | 校验 `targetDeviceId`、`device.local`、`messagesWithTargetDeviceId`；JS marker。 | implemented, self-tested |
| PRD：组 Agent 统一调度，拆任务、选 Agent、汇总结果。 | 工作台要回答当前推进到哪里、下一步谁负责、证据是否完整。 | 项目页任务流、Agent 页当前工作、结果中心 TaskResult、首页闭环摘要。 | 单元测试检查 taskFlow/taskResults/acceptanceEvidence，页面 copy marker。 | implemented, self-tested |
| PRD：Agent 具备角色、职责、Skill、模型策略、权限和输出约束。 | Agent 页覆盖岗位 Agent、在线状态、设备、当前任务、证据和交接提示。 | Agent 页面由 `agentSessions` 和 `agentCurrentWork` 渲染，角色中文化，保留 agentId。 | Shell 渲染 marker 和 live read model session 校验。 | implemented, self-tested |
| PRD：设备、workspace、worktree 等资源可注册、监控和分配。 | Runner 页展示能力、租约、心跳、范围审计。 | Runner 页 `runnerLeases`，运行监控页 `devices` 和 `worktrees`。 | Validator 原有 runnerLeases/scopeAudit；新增 shell 文案检查。 | implemented, self-tested |
| PRD：形成任务分派、执行、上报、汇总、确认、沉淀闭环。 | 验收中心必须展示 TaskResult 入口和验收路由。 | 结果中心 `acceptanceEvidence`、`taskResults`、`taskFlow`。 | 单元测试检查 taskResults submitted 语义与证据缺失提示。 | implemented, self-tested |
| 技术方案：Local Router 是 MVP 关键模块，会话启动后注册 Agent ID、Session ID、Project ID、状态。 | 运行监控页必须可看到本机路由注册关系。 | `panelFromSession`、`panelFromMessage`、运行监控多 section。 | live read model sessions/messages 校验。 | implemented, self-tested |
| 技术方案：统一 Agent Message Protocol，支持 task、handoff、status、result、confirm_request、notify。 | 消息路由要显示类型、优先级、上下文引用和目标设备。 | 消息卡字段：messageType、priority、contextRefs、routeType、targetDeviceId。 | JS shell marker 和自测检查。 | implemented, self-tested |
| 技术方案：Orchestrator pipeline 包含任务规划、Agent 匹配、资源检查、dispatch、monitor、aggregate、human confirmation、persist。 | 首页/项目页需呈现闭环阶段，不隐藏确认和持久化。 | 首页闭环阶段条，项目页任务流，审批页 confirm request。 | 静态 DOM/文本 marker 校验。 | implemented, self-tested |
| 技术方案：资源显式注册，路由抽象统一，本机先行。 | 设备只有本机但路由字段仍展示。 | 运行监控页设备路由字段、footer 包装边界。 | Validator + 单测。 | implemented, self-tested |
| 设计：中文 Codex 风格，短句、状态、下一步、证据优先，内部 ID 降级。 | 必须中文可读。 | HTML lang/title/topbar/footer；JS 状态、角色、字段、空态中文；CSS 收敛 Codex 风格。 | Validator 检查中文 marker，人工打开 HTML。 | implemented, self-tested |
| 设计：页面包括首页、运行监控、项目、Agent、Runner、验收、审批/权限、异常恢复。 | PRD 和技术方案覆盖不可留遗留项。 | `primarySurfaces` 覆盖 8 个主页面，其他 surface 可由 read model 继续扩展。 | Validator 检查 surface labels/sections。 | implemented, self-tested |
| 设计：验收页展示产品最终验收、PM 流程验收、测试闭环验收。 | `submitted` 不能写成已验收；证据缺失显式提示。 | 结果中心 acceptanceEvidence + TaskResult 卡；状态映射 `submitted=已提交，待评审`。 | 单元测试检查 JS 文案和 missing evidence markers。 | implemented, self-tested |
| 设计：审批/权限页独立显示 approvals、permissionGatedActions、serverGate、auditRef、安全设置。 | 权限/审批不能混成验收。 | Review Center 独立 section：审批队列、权限动作、安全设置。 | Validator marker + shell unit assertions。 | implemented, self-tested |
| 设计：异常恢复页覆盖 stale lease、failed runner、offline heartbeat、cancelled/rejected/blocked、通知异常、safe fallback。 | 异常恢复完整。 | Recovery Center 聚合 recovery、problem runner leases、problem tasks、notifications、safe fallback。 | 单元测试检查 recovery marker。 | implemented, self-tested |
| 产品评审：设计 approved，允许进入研发，但研发必须实现后交测试。 | 研发不替产品/测试下结论。 | 方案、TaskResult summary、UI copy 均区分“已提交/待评审/验收证据”。 | finish TaskResult acceptancePolicy。 | implemented, self-tested |
| 任务要求：必须接真实 `workbench-live-read-model.js`，不能 mock 冒充。 | live source 是 `real-v1-runtime-read-model` 且 fixture false。 | HTML 加载 live read model；JS runtime summary 显示 live source；无 mock 数据。 | Validator `validate_live_read_model` + 单测。 | implemented, self-tested |

## 自测计划

- `node --check projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js`
- `python3 scripts/validate_desktop_workbench_slice0.py /Users/meimei/Documents/company_knowledge_core`
- `python3 -m unittest tests.test_desktop_workbench_slice0`
- `python3 -m zhenzhi_knowledge --root /Users/meimei/Documents/company_knowledge_core validate`
- `git diff --check -- projects/company-knowledge-core/engineering/v1-workbench-codex-style-implementation-plan.md projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.html projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.css scripts/validate_desktop_workbench_slice0.py tests/test_desktop_workbench_slice0.py`

## 自测结果

- `node --check projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js`: pass
- `python3 scripts/validate_desktop_workbench_slice0.py /Users/meimei/Documents/company_knowledge_core`: pass
- `python3 -m unittest tests.test_desktop_workbench_slice0`: pass, 8 tests
- `python3 -m zhenzhi_knowledge --root /Users/meimei/Documents/company_knowledge_core validate`: pass
- `git diff --check -- <touched files>`: pass

## 研发说明

`python3 -m zhenzhi_knowledge validate` 首轮发现相关文档 frontmatter 使用了当前 schema 未登记的 `DesignArtifact`、`ProductReview`、`EngineeringPlan`。本次只对本任务相关三份文档修正为已支持类型：设计/实现方案使用 `Workflow`，产品评审使用 `ReviewRecord`；正文、决策和引用不变。
