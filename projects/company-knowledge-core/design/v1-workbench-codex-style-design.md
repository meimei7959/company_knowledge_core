---
type: Workflow
title: V1 工作台 Codex 风格中文设计方案
projectId: company-knowledge-core
taskId: kt-v1-workbench-codex-style-design
agentId: agent.company.design
status: submitted
language: zh-CN
createdAt: "2026-06-22"
sourceRefs:
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.html
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.css
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-live-read-model.js
operatingRuleRefs:
  companyConstitution: docs/agent-team/company-agent-constitution.md
  commonRules: docs/agent-team/common-agent-operating-rules.md
  taskRuntimeContract: docs/agent-team/agent-task-runtime-contract.md
  humanAcceptancePolicy: docs/agent-team/human-acceptance-policy.md
  roleSpec: agents/agent.company.design.md
  projectContext: projects/company-knowledge-core/project.md
---

# V1 工作台 Codex 风格中文设计方案

## 设计定位

V1 工作台是给项目 Owner、项目经理 Agent 和各岗位 Agent 使用的本地桌面控制台。它不替代 Agent Ring、不直接执行分布式任务，只呈现 Central API read model 的真实状态、证据、权限门和恢复路径。

本方案基于当前 Slice0 静态壳：

- `workbench-shell.html`：左侧导航、顶部摘要、主内容、底部同步和包边界。
- `workbench-shell.js`：根据 read model 渲染 surface、section、状态、证据和权限动作。
- `workbench-shell.css`：浅色、低噪音、密集信息布局。
- `workbench-live-read-model.js`：真实 V1 read model，包含 11 个 surface、运行指标、任务流、结果、Runner、审批、通知、恢复、权限动作。

设计目标：做成中文 Codex 风格工作台，强调“当前能做什么、为什么可信、下一步谁处理”。界面要像一个本地 Agent 控制台，不像营销页，也不做装饰化大屏。

## Codex 风格原则

1. 以任务和证据为中心：任何状态卡片都必须有状态、Owner、下一步、证据入口。
2. 默认为只读观察：没有明确权限和审批前，所有破坏性动作显示为“需要授权”，不直接执行。
3. 信息密度高但不拥挤：导航短、标题短、卡片可扫读，减少解释性长段落。
4. 状态语言稳定：同一状态在所有页面使用同一中文词、颜色和优先级。
5. 先中文业务含义，再内部引用：主文案显示“待验收”“租约过期”“需要授权”，内部 ID 只作为次级证据。
6. 异常不藏起来：失败、过期、离线、降级和只读 fallback 都要有恢复动作。
7. 不替岗位下结论：设计只表达信息架构和交互，不写产品验收结论、研发完成结论或测试通过结论。

## 全局信息层级

### 页面骨架

- 左侧导航：稳定 surface 入口，默认只显示 V1 主路径。
- 顶部摘要：当前 read model 类型、运行环境、未关闭任务数。
- 主内容区：页面标题、健康条、主卡片区、权限动作区。
- 底部状态条：同步策略和本地包边界。

### 卡片层级

每个列表项统一为四层：

1. 主标题：人能理解的任务、Agent、Runner 或审批名称。
2. 状态标签：`正常`、`执行中`、`待验收`、`待授权`、`阻塞`、`失败`、`过期`、`降级`、`离线`、`只读`。
3. 下一步：一句话说明该看什么、谁处理、是否需要审批。
4. 证据：最多展示 3 个证据 chip，完整引用放 hover 或详情页。

### 状态优先级

页面排序建议：

1. `failed` / `blocked` / `offline`：红色风险，必须给恢复路径。
2. `needs_permission` / `waiting_review`：黄色或蓝色待人工动作。
3. `stale` / `degraded` / `safe_fallback`：灰蓝状态，说明不是最新但可追溯。
4. `running`：正在执行，显示 lease 或当前任务。
5. `ready` / `online` / `done` / `submitted` / `completed` / `delivered`：正常证据态。

## 导航设计

V1 主导航保留 8 个一级入口：

| 导航 | 中文名 | 目的 |
| --- | --- | --- |
| `home` | 首页 | 一屏判断系统是否可用、是否有人要处理。 |
| `runtime-monitor` | 运行监控 | 看设备、会话、消息、运行指标和任务流。 |
| `project-console` | 项目 | 看项目进展、任务流和可交付证据。 |
| `agent-team-manager` | Agent | 看岗位 Agent 在线状态、当前任务和交接。 |
| `agent-ring-console` | Runner | 看 Runner 能力、租约、心跳和范围审计。 |
| `result-center` | 验收 | 看 TaskResult、验收证据和交付状态。 |
| `review-center` | 审批/权限 | 看人审队列、权限门和待确认动作。 |
| `recovery-center` | 异常恢复 | 看离线、过期、失败、重试和升级路径。 |

`quality-dashboard`、`notification-center`、`settings-security` 可作为次级入口，后续在“更多”中露出。V1 首屏不应把所有 11 个 surface 同时推给用户。

## 首页

### 首页目标

用户打开工作台后，5 秒内知道：

- Central API read model 是否加载成功。
- 当前 V1 是否有未关闭任务。
- 设备、Agent 会话、消息路由是否正常。
- 是否有待验收、待授权或异常恢复动作。
- 最近可信证据在哪里。

### 首页布局

1. 顶部指标条：
   - 未关闭任务
   - 在线设备
   - 在线 Agent
   - 设备路由消息
   - 产品验收

2. 左列：验收门和最近路由。
   - “验收门”展示 `acceptanceEvidence`，优先显示 Product、PM、Test 三类证据。
   - “最近路由”展示最新 `agentMessages`，格式为“发送方 -> 接收方 / 目标设备 / 优先级”。

3. 右列：Agent 状态和待处理动作。
   - “Agent 状态”展示 `agentSessions`，突出在线、当前任务、设备。
   - “待处理动作”展示 `approvals` 和 `permissionGatedActions` 的高优先级项。

### 首页中文文案

- `V1 runtime health` 显示为“V1 运行健康度”。
- `Product final acceptance` 显示为“产品最终验收”。
- `PM final acceptance` 显示为“PM 流程验收”。
- `Test closed-loop acceptance` 显示为“测试闭环验收”。
- `Open V1 tasks: 0` 显示为“未关闭 V1 任务：0”。
- `Show last verified evidence when live state is stale` 显示为“实时状态过期时，展示最近一次可追溯证据”。

## 运行监控

### 页面目标

运行监控用于判断本地工作台是否还连着真实运行态。它不是性能大屏，而是 Agent 工作流的运行事实列表。

### 信息结构

1. 运行指标：来自 `runtimeMetrics`。
   - 项目
   - 设备数 / 在线设备
   - Agent 会话 / 在线会话
   - 消息数 / 已送达消息
   - 带目标设备的消息
   - 任务包、工作区、验收运行数
   - V1 任务数、未关闭任务

2. 设备：来自 `devices`。
   - 设备名
   - 在线状态
   - 主机类型
   - workspace
   - capabilities

3. Agent 会话：来自 `agentSessions`。
   - Agent 岗位
   - 设备
   - 当前任务
   - 会话证据

4. 消息路由：来自 `agentMessages`。
   - from Agent
   - to Agent
   - message type
   - target device
   - priority
   - delivered 状态

5. 任务流和验收证据：只展示最近项，作为运行事实的上下文。

### 交互要求

- 指标点击后过滤下方列表，例如点击“已送达消息”只显示消息路由。
- 消息列表默认按时间倒序，展示最近 16 条。
- 当 `sourceOfTruth` 不是 `central-api-read-model` 时，整页进入“安全只读”状态。

## 项目

### 页面目标

项目页用于回答“当前项目推进到哪里、下一步谁负责、证据是否完整”。不在此页做产品范围判断。

### 信息结构

1. 项目健康摘要：
   - 当前 focus
   - 未关闭任务
   - 最近 TaskResult
   - 当前风险数量

2. 项目进展：来自 `projectProgress`。
   - 任务标题
   - 状态
   - Owner
   - 下一步
   - 任务文件证据

3. 任务流：来自 `taskFlow`。
   - `done`、`rejected`、`cancelled` 分组显示。
   - 取消任务必须显示“取消原因入口”，不能只显示 cancelled。

4. 任务包：来自 `taskPackages`。
   - 任务包已生成、是否可被 Runner 消费、关联工作区。

### 中文文案原则

- `offline` 在项目页不直接翻成“离线”时，需要结合语义写成“已取消或不再活跃”，避免用户误解为设备离线。
- `Review cancellation reason and create a retry task only if the owner approves` 显示为“查看取消原因；仅在 Owner 批准后创建重试任务”。
- 项目页避免“完成了”“通过了”等结论性词，除非该词来自对应 TaskResult。

## Agent

### 页面目标

Agent 页用于看岗位 Agent 是否在线、正在处理什么、是否有交接或阻塞。它不让用户直接替 Agent 写岗位结论。

### 信息结构

1. Agent 总览：
   - 项目经理
   - 产品经理
   - 设计
   - 研发
   - 测试
   - 运维或知识岗位

2. 当前工作：来自 `agentCurrentWork` 和 `agentSessions`。
   - 角色名称
   - 所在设备
   - 当前任务
   - 会话状态
   - 最近证据

3. 交接提示：
   - 如果 TaskResult 有 handoff，展示“交给谁”和“下一步”。
   - 如果缺少对应岗位 TaskResult，显示“缺岗位结果”，不允许 PM 或主线程代签。

### 角色命名

当前 `roleNames` 只有 PM、产品、研发、测试。设计规范建议补齐显示映射：

| Agent ID | 中文名 |
| --- | --- |
| `agent.company.project-manager` | 项目经理 |
| `agent.company.product-manager` | 产品经理 |
| `agent.company.design` | 设计 |
| `agent.company.development` | 研发 |
| `agent.company.test` | 测试 |
| `agent.company.operations` | 运维 |
| `agent.company.knowledge-query` | 查知识 |

## Runner

### 页面目标

Runner 页用于看 Agent Ring 外部执行资源是否可用、租约是否有效、能力范围是否合规。

### 信息结构

1. Runner 列表：来自 `runnerLeases`。
   - Runner 名称
   - 当前租约
   - 状态
   - 心跳
   - nextAction
   - scope audit 证据

2. 租约状态：
   - 有 active lease：显示任务、租约到期、心跳。
   - 无 active lease：显示“暂无租约”，但保留能力范围。
   - `stale`：显示“租约过期”，突出恢复入口。
   - `failed`：显示“执行失败”，突出失败证据和重试条件。

3. 能力范围：
   - projects
   - capabilities
   - permission policy
   - 是否允许当前项目

4. Runner 历史：来自 `runnerHistory`，用于恢复中心和审计，不作为首页主要信息。

### 文案示例

- `lease_expired`：租约已过期。
- `Monitor runner scope, leases, and heartbeat`：监控 Runner 范围、租约和心跳。
- `No active lease`：暂无活跃租约。
- `safe_fallback`：只读回退。

## 验收

### 页面目标

验收页用于汇总 TaskResult 和岗位验收证据，帮助 PM 判断是否进入验收路由。设计页不能替产品、测试或 PM 下结论。

### 信息结构

1. 验收证据：来自 `acceptanceEvidence`。
   - 产品最终验收
   - PM 流程验收
   - 测试闭环验收
   - 每条展示对应 TaskResult 入口

2. 任务结果：来自 `taskResults`。
   - taskId
   - executorAgent
   - result/status
   - summary
   - output/evidence refs

3. 验收路由：
   - PM review
   - human review required
   - changes requested
   - blocked

4. 证据完整性提醒：
   - 缺 outputRef
   - 缺 evidenceRef
   - 缺 testsOrChecks
   - 缺 operatingRuleRefs
   - 缺 commonRulesEvaluation

### 交互规则

- 点击 TaskResult 打开详情抽屉：摘要、输出、证据、检查、规则引用、质量评价、交接。
- 对“submitted”只显示“已提交结果”，不显示“已通过”。
- 对 Product/Test/PM 的 accepted 文案必须引用对应 TaskResult，不由工作台生成。

## 审批/权限

### 页面目标

审批/权限页聚合所有需要人类确认、工具 Owner 批准、Runner scope 检查的动作。它要让用户知道“为什么不能直接执行”。

### 信息结构

1. 人审队列：来自 `approvals`。
   - 标题
   - 状态
   - Owner
   - 下一步
   - 消息或审批证据

2. 权限门动作：来自 `permissionGatedActions`。
   - 动作名称
   - 所需 permission
   - serverGate
   - auditRef
   - 是否可在本地工作台发起申请

3. 安全设置：来自 `settingsSecurity`。
   - secure storage
   - token 不落盘
   - Keychain / Credential Manager 边界

### 文案原则

- 不说“权限不足”就结束，要给“需要谁批准、批准什么、证据在哪里”。
- 对高风险动作使用完整句子：“此操作需要人类确认后才能继续，因为它会影响权限、审批或生产安全。”
- 审批按钮文案使用动词加对象：`申请授权`、`查看确认消息`、`打开审批证据`、`复制审计引用`。

## 异常恢复

### 页面目标

恢复页用于把失败、离线、过期、取消、降级、只读 fallback 变成可处理的下一步。

### 信息结构

1. 当前恢复摘要：来自 `recovery`。
   - 未关闭 V1 任务
   - 是否需要重试
   - 是否需要人类确认
   - 是否只读 fallback

2. Runner 异常：
   - stale lease
   - failed runner
   - offline heartbeat
   - nextAction

3. 项目任务异常：
   - cancelled
   - rejected
   - blocked
   - retry condition

4. 通知异常：
   - 通知中心状态
   - 未送达通知
   - PM 是否已收到完成节点

### 恢复路径文案

- “查看证据”：打开失败或取消的来源。
- “创建重试任务”：只在 Owner 批准后显示可执行。
- “升级给 PM”：规则冲突、连续恢复失败或证据不足时使用。
- “保持只读”：read model 过期但仍可展示最近可信证据时使用。

## 中文文案总规范

### 命名

- 一级导航使用 2 到 4 个中文字：`首页`、`运行监控`、`项目`、`Agent`、`Runner`、`验收`、`审批/权限`、`恢复`。
- 页面标题使用业务名，不用内部英文 key。
- 内部 ID 只在证据 chip、详情抽屉或复制引用中出现。

### 句式

- 卡片下一步用短句：`查看取消原因；Owner 批准后可重试。`
- 状态说明先说事实，再说动作：`租约已过期。查看 Runner 心跳和任务证据。`
- 避免泛词：不用“处理一下”“有问题”“异常状态”，改成“待授权”“租约过期”“证据缺失”。

### 中英混排

- Agent、Runner、TaskResult、read model、Central API 保留英文，因为它们是系统对象名。
- 状态和动作一律中文。
- 文件路径、命令、ID 保持原样。

### 空态

- 无数据：`暂无可显示数据。`
- 无任务：`暂无未关闭任务。`
- 无租约：`暂无活跃租约。`
- 无审批：`暂无待审批动作。`
- read model 未加载：`安全只读：未加载到真实 read model，状态变更动作已禁用。`

## 视觉与交互系统

### 布局

- 维持左侧 rail + 内容区，不做营销式 hero。
- 内容最大宽度 1120 到 1280px，面向长时间工作。
- 卡片半径控制在 8px；当前 CSS 10px 可在后续实现中收敛。
- 页面 section 不放进大卡片，只有列表项、指标和详情抽屉用卡片。

### 颜色

- 保持低饱和浅色背景。
- 状态色只服务语义：红色风险、黄色等待、蓝色权限/降级、绿色正常、灰色只读。
- 避免大面积单一蓝灰或紫色渐变。

### 可访问性

- 导航保留 `aria-current="page"`。
- 主内容区切换后 focus 到 `#workbench-root`。
- 状态不能只靠颜色表达，必须有中文标签。
- 证据 chip 要保留 title 或详情入口，便于读屏和复制。

## 详情抽屉建议

V1 后续实现可以为任意卡片提供右侧详情抽屉。抽屉不改变数据，只展开证据。

详情结构：

1. 标题和状态。
2. Owner / Agent / Runner。
3. 下一步。
4. 原始字段摘要。
5. 证据引用。
6. 允许动作或权限门。
7. 审计引用。

## 研发交接清单

本任务不实现代码，仅给后续研发交接建议：

- 补齐中文 role 映射，至少包含设计、运维、查知识。
- 把 `review-center` 命名为“审批/权限”，或拆为审批队列和权限门两个 section。
- 在 `result-center` 文案中将 `submitted` 显示为“已提交结果”，避免误读为验收通过。
- 对 `offline` 增加按上下文解释：设备页为“离线”，项目任务页为“已取消/不活跃”。
- 把权限动作固定在页面底部或右侧，不混在普通状态列表里。
- 为 recovery 单独汇总 stale/failed/offline/cancelled/rejected，而不是只展示 `recovery` 数组的一条 safe fallback。

## 设计自检

- 覆盖首页、运行监控、项目、Agent、Runner、验收、审批/权限、异常恢复。
- 明确全局信息层级、卡片层级、状态优先级。
- 明确中文文案原则和关键文案示例。
- 基于当前 Slice0 read model，不要求新增产品范围。
- 不实现研发代码，不替产品或测试写结论。
- 后续应由产品 Agent 评审范围，由研发 Agent 决定实现方案，由测试 Agent 验证结果。

## 交接结论

设计产物已达到 PM review 的交付形态。建议下一步由项目经理 Agent 路由给产品经理 Agent 做范围确认，再释放研发实现任务；如只做 UI 文案替换，可由研发 Agent 直接基于本设计拆轻量实现任务。
