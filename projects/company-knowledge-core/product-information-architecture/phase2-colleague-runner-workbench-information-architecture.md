---
type: Workflow
title: 阶段二同事接入工作台产品信息架构
description: Product information architecture for Phase 2 colleague computer and multi-device Runner collaboration workbench.
timestamp: "2026-06-22T12:34:15Z"
artifactId: pia.phase2.colleague-runner-workbench
projectId: company-knowledge-core
ownerAgent: agent.company.product-manager
taskId: kt-v2-colleague-runner-product-information-architecture
status: draft
sourceMaterialRefs:
  - projects/company-knowledge-core/workflows/phase2-multi-device-collaboration-orchestrator-orchestrator.md
  - docs/product/ai-native-os/phase-2-multi-device-runner-collaboration-prd.md
  - task-results/tr-kt-v2-colleague-runner-product-requirements.md
  - projects/company-knowledge-core/design/phase2-multi-device-runner-workbench-ui-interaction-revision.md
  - projects/company-knowledge-core/technical-solutions/phase2-multi-device-runner-collaboration-technical-solution.md
  - projects/company-knowledge-core/product-reviews/phase2-multi-device-runner-collaboration-architecture-product-review.md
operatingRuleRefs:
  - projects/company-knowledge-core/workflows/phase2-multi-device-collaboration-orchestrator-orchestrator.md
  - docs/agent-team/company-agent-constitution.md
  - docs/agent-team/agent-task-runtime-contract.md
  - docs/agent-team/human-acceptance-policy.md
  - agents/agent.company.product-manager.md
  - projects/company-knowledge-core/project.md
updatedAt: "2026-06-22T12:34:15Z"
---

# 阶段二同事接入工作台产品信息架构

## 边界结论

本文件引用并遵守 `projects/company-knowledge-core/workflows/phase2-multi-device-collaboration-orchestrator-orchestrator.md`。产品经理 Agent 负责产品信息架构：页面目标、导航模型、对象分组、用户可见命名、主次信息层级、任务路径和主界面禁曝字段。设计 Agent 消费本 IA 后负责 UI 设计、交互设计、视觉层级、中文文案、组件行为和状态表达。

本文件不做 UI 设计，不规定版式、视觉样式、组件造型、动效、断点或具体交互控件。

## 页面目标

阶段二工作台页面面向项目 Owner、项目经理 Agent、同事 Runner 管理员、岗位 Agent 执行者、测试 Agent 和系统管理员。页面目标是让用户在同一项目中枢里看懂并处理多设备执行：

1. 当前项目是否允许同事电脑加入，谁可以加入，加入后能做什么。
2. 哪些电脑在线、可接任务、等待授权、正在执行、异常或离线。
3. 哪些任务已被路由给哪台电脑，为什么这样分配，是否有租约冲突。
4. 执行结果、TaskResult、AgentRun、证据、检查结果和验收状态是否已写回。
5. 离线、超时、越权、工具缺失、上下文失败、写回失败和人工审批等待时，谁负责下一步。
6. 项目 Owner 可以邀请同事、确认授权、转派任务、暂停接单、禁用设备、释放租约或查看证据。

## 导航模型

主入口命名为“协作设备”。该入口属于项目中枢，不属于研发调试台。

导航结构建议给设计 Agent 作为 IA 输入：

| 层级 | 用户入口名 | 用户意图 | IA 边界 |
| --- | --- | --- | --- |
| 项目中枢 | 项目概览 | 了解项目总体任务、风险和验收 | 只显示协作设备摘要和待处理入口。 |
| 项目中枢 / 协作设备 | 协作设备 | 管理同事电脑接入、授权、路由和恢复 | 阶段二主页面。 |
| 协作设备 / 接入与授权 | 邀请同事、确认授权 | 完成同事电脑加入和范围授权 | 不直接暴露配对 token、设备 id、Runner id。 |
| 协作设备 / 任务路由 | 任务分配、执行中、待回传 | 看清任务由谁执行、为什么、卡在哪里 | 展示业务解释，不展示 raw route enum。 |
| 协作设备 / 证据与操作记录 | 结果证据、审计、通知 | 复核 TaskResult、AgentRun、AuditLog、NotificationRecord | 可进入证据层查看脱敏技术细节。 |
| 协作设备 / 技术详情 | 技术详情 | 给架构、研发、测试定位问题 | 默认不是主信息；必须折叠、脱敏、可审计。 |

## 页面和模块对象分组

### 1. 项目上下文

对象：项目、项目 Owner、当前访问者、项目接入策略、只读/可操作权限。

用户要回答的问题：

- 我现在看的哪个项目？
- 这个项目是否允许同事电脑加入？
- 我是否有邀请、授权、暂停、转派或验收权限？

主信息：项目名称、协作状态、当前权限、下一步主动作。

次信息：项目负责人、最近同步时间、只读原因、数据可能过期提示。

### 2. 协作总览

对象：设备数量、可接任务数量、异常数量、待授权数量、待验收数量。

用户要回答的问题：

- 现在有几台电脑能工作？
- 有没有需要我处理的授权、异常或验收？
- 是否有任务等待 Runner？

主信息：可接任务、执行中、待处理、风险。

次信息：最近心跳、最近写回、最近审计记录入口。

### 3. 接入与授权

对象：邀请、配对申请、授权范围、撤销/过期、审批等待。

用户要回答的问题：

- 怎么让同事电脑加入当前项目？
- 这台电脑是谁的、叫什么、能申请做什么？
- 是否允许它执行某类任务、访问某个仓库、使用某类工具或读取某类资料？

主信息：申请人、电脑名称、项目、申请能力、授权结论、风险提醒、下一步动作。

次信息：申请时间、过期状态、授权范围摘要、审批责任人。

### 4. 设备与执行器

对象：电脑、Runner、Owner、可执行 Agent、工作类型、负载、在线状态、当前任务。

用户要回答的问题：

- 这台电脑是谁的？
- 它现在能不能接任务？
- 它适合做什么工作？
- 它正在做什么，多久没响应？

主信息：电脑显示名、负责人、可用状态、可做工作、当前任务、下一步动作。

次信息：最近在线、负载摘要、风险标签、授权摘要。

### 5. 任务路由

对象：ProjectTask / KnowledgeTask、任务要求、候选 Runner、路由理由、租约、阻塞、下一责任人。

用户要回答的问题：

- 任务分给谁了？
- 为什么分给这台电脑？
- 是否已经领取？是否等待回传？
- 卡点是谁处理？

主信息：任务名称、业务状态、分配电脑、分配理由、卡点、下一步。

次信息：任务类型、所需角色、所需能力、租约状态摘要、等待时长。

### 6. 恢复与风险

对象：离线、租约过期、权限拒绝、工具缺失、仓库不可用、上下文失败、写回失败、人工审批等待。

用户要回答的问题：

- 发生了什么？
- 对项目有什么影响？
- 谁要做什么？
- 能等待、续租、转派、取消、补授权还是提交审批？

主信息：业务影响、可读原因、责任人、建议动作。

次信息：发生时间、影响任务、恢复尝试、相关审计。

### 7. 结果、证据和验收

对象：TaskResult、AgentRun、evidenceRefs、testsOrChecks、qualityEvaluation、acceptancePolicy、handoffContract、terminalReason。

用户要回答的问题：

- 同事电脑是否把结果写回了中枢？
- 结果是否完整，能否验收？
- 是否需要项目经理或人类验收？
- 下一步转给谁？

主信息：结果状态、验收状态、证据完整性、下一责任人。

次信息：输出文档、检查项、质量评价、交接摘要、审计入口。

### 8. 操作记录和技术详情

对象：AuditLog、NotificationRecord、read model 原始来源、脱敏内部字段。

用户要回答的问题：

- 谁做了邀请、授权、暂停、转派、释放租约或禁用？
- 什么时候发生，影响了什么？
- 需要研发/测试定位时，相关技术字段在哪里？

主信息：操作人、动作、对象中文名、影响、结果。

次信息：脱敏技术字段、内部枚举、路径、端点、错误栈、原始状态。

## 用户可见概念命名

| 内部/技术概念 | 主界面用户命名 | 使用规则 |
| --- | --- | --- |
| Shared Project Center | 项目中枢 | 表达统一任务、证据和验收事实。 |
| DeviceRegistration / Device | 同事电脑 / 电脑 | 优先用电脑显示名和负责人。 |
| AgentRunner / Runner | 执行器 | 解释为“这台电脑上可接任务的执行入口”。 |
| PairingRequest | 接入申请 | 表达“同事电脑申请加入项目”。 |
| RunnerAuthorization | 授权范围 | 表达项目、角色、任务类型、仓库、工具、资料范围。 |
| Capability code | 可做工作 | 映射为设计、开发、测试、资料整理、项目管理等中文标签。 |
| Lease | 任务占用 | 解释为“这项任务当前由谁执行，何时需要响应”。 |
| Heartbeat | 最近在线 | 展示“刚刚在线 / X 分钟前在线 / 已离线”。 |
| Route decision | 分配理由 | 说明“具备工作类型、项目授权、当前空闲”等业务原因。 |
| waiting_runner | 等待可用电脑 | 不渲染 raw enum。 |
| stale_lease | 响应超时 | 表达需要等待、续租、转派或取消。 |
| recovery_pending | 等待恢复 | 搭配责任人和下一步。 |
| Permission Gate | 权限检查 | 失败时说清缺少什么授权。 |
| Context Pack | 任务上下文 | 表达本次任务允许读取的资料和规则。 |
| Result Center | 结果验收 | 表达结果写回、证据检查和验收流转。 |
| TaskResult | 任务结果 | 作为证据层对象出现。 |
| AgentRun | 执行记录 | 作为证据层对象出现。 |
| AuditLog | 操作记录 | 面向用户说明谁做了什么。 |
| NotificationRecord | 通知记录 | 面向用户说明谁收到了什么提醒。 |

## 主次信息层级

### 首屏/主信息

主信息必须回答“现在能不能协作、谁在做什么、我下一步做什么”：

- 当前项目协作状态。
- 可接任务电脑数量。
- 等待授权数量。
- 执行中任务数量。
- 异常/需处理数量。
- 邀请同事、确认授权、转派任务、查看证据等主要动作。
- 每条任务的任务名称、分配给谁、为什么、卡点、下一责任人。

### 次级信息

次级信息帮助用户判断风险和优先级：

- 最近在线时间。
- 授权范围摘要。
- 可做工作标签。
- 当前负载摘要。
- 等待时长。
- 结果完整性。
- 审计/通知入口。

### 证据/技术详情

证据和技术详情用于复核和排障，不做主信息：

- TaskResult 完整字段。
- AgentRun 运行记录。
- AuditLog / NotificationRecord。
- 脱敏内部 id、raw enum、路径、endpoint、错误栈。
- read model schemaVersion、generatedAt、technicalDetails。

## 用户任务路径

### 路径 1：邀请同事电脑加入

1. 项目 Owner 进入“协作设备”。
2. 查看当前项目是否允许同事电脑加入。
3. 发起“邀请同事”。
4. 同事在自己电脑完成接入申请。
5. 项目中枢出现“待确认”的接入申请。
6. Owner 查看申请人、电脑名称、申请工作类型和风险。
7. Owner 进入授权路径。

成功信号：页面能说明“谁的电脑申请加入哪个项目、准备做什么、下一步谁确认”。

### 路径 2：确认配对并授予范围

1. Owner 查看接入申请。
2. 选择授权范围：项目、任务类型、Agent 角色、仓库、工具、资料范围。
3. 系统进行服务端权限检查。
4. 授权成功后，电脑变为“可接任务”或“等待任务”。
5. 授权失败时，显示缺少的授权、审批责任人和下一步。

成功信号：用户看到中文授权摘要，不需要理解 scope code。

### 路径 3：调度任务到同事电脑

1. 调度器根据任务要求匹配可用电脑。
2. 页面展示任务分配对象和分配理由。
3. 任务进入“执行中”或“等待回传”。
4. 其他电脑不能重复领取同一任务。
5. 如无合适电脑，任务进入“等待可用电脑”并给出原因。

成功信号：用户看懂“为什么是这台电脑做、如果没人能做要补什么”。

### 路径 4：结果写回与验收

1. Runner 执行任务。
2. Runner 写回 TaskResult、AgentRun、证据、检查、质量评价和验收策略。
3. 页面展示“结果已回传 / 证据缺失 / 待验收 / 需修改”。
4. 项目经理或人类验收人查看证据并决定接受、退回或转交。

成功信号：用户不登录同事电脑，也能在中枢复核完整结果。

### 路径 5：离线、超时或写回失败恢复

1. Runner 心跳断开、租约超时或写回失败。
2. 页面显示业务影响、可读原因、责任人和建议动作。
3. 用户可等待、续租、释放租约、转派、取消或要求补证据。
4. 操作写入 AuditLog 和 NotificationRecord。

成功信号：任务不永久停在“执行中”，恢复动作可追溯。

### 路径 6：越权或审批等待

1. Runner 尝试领取或读取越权任务资料。
2. 系统拒绝，并显示“缺少项目/仓库/工具/资料授权”。
3. 如需人工审批，任务进入“等待审批”。
4. 页面展示审批责任人、材料、截止时间和下一步。

成功信号：越权不产生任务结果；等待审批不被误认为失败或完成。

### 路径 7：暂停、禁用、转派和撤销授权

1. Owner 选择设备、任务或授权范围。
2. 页面说明动作影响：暂停接单、禁用电脑、转派任务、撤销授权。
3. 服务端 gate 校验权限。
4. 成功后更新协作状态、任务状态和操作记录。
5. 失败时展示可读原因。

成功信号：危险动作有明确影响说明和审计。

## 禁止主界面暴露的内部字段

以下字段或概念不得作为标题、主列、按钮、卡片核心文案、错误主文案或默认可见内容。需要排障时只能进入“证据/技术详情”，且必须脱敏：

| 禁曝对象 | 主界面替代 |
| --- | --- |
| `runnerId`、`deviceId`、`leaseId`、`claimId`、`sessionId`、`runId` | 电脑显示名、负责人、任务结果、执行记录。 |
| `leaseTokenHash`、`leaseProofHash`、`leaseOwner` 原始值 | 任务占用状态、当前执行电脑、响应截止。 |
| raw status / enum，如 `waiting_runner`、`stale_lease`、`recovery_pending` | 等待可用电脑、响应超时、等待恢复。 |
| capability code / role code / scope code | 可做工作、岗位角色、授权范围摘要。 |
| 本地文件路径、仓库绝对路径、上下文包路径 | 文档标题、仓库显示名、资料范围。 |
| endpoint、API 路径、schemaVersion、generatedAt 原始字段 | 最近同步、技术详情入口。 |
| token、secret、密码、密钥、cookie、认证头 | 永不展示；只显示“凭据已配置/缺少凭据”。 |
| 错误堆栈、stdout/stderr 原文、大段日志 | 可读错误摘要、影响、下一步；原文脱敏后进技术详情。 |
| 内部审核 id、通知 id、审计 id | 操作记录标题、时间、操作人、影响对象。 |
| 未脱敏的 owner id、open_id、邮箱、手机号 | 负责人显示名；敏感联系方式按权限显示。 |

## 给 Design Agent 的 IA 输入

Design Agent 后续应消费本 IA，并产出 UI/交互设计，不再把 IA 本身当作最终设计交付。

必须覆盖：

- 主入口名：“协作设备”。
- 用户第一眼要看懂：项目是否允许同事加入、可接任务电脑数、异常数、待授权数、当前任务路由和下一步。
- 信息对象：项目上下文、协作总览、接入与授权、设备与执行器、任务路由、恢复与风险、结果证据、操作记录、技术详情。
- 状态必须用户可读：可接任务、执行中、等待授权、离线、响应超时、等待回传、待验收、需人工处理、已完成。
- 空、加载、失败、无权限、只读、数据过期、等待审批、写回失败都必须说明“发生了什么、影响什么、谁处理、下一步是什么”。
- 主界面不得展示本文件列出的禁曝字段。

不得做：

- 把 `runnerId`、`deviceId`、raw status、路径、token、endpoint 作为主信息。
- 用技术表格替代用户任务路径。
- 只给信息架构而缺少 UI/交互设计交付。

## 给 Architecture Agent 的 IA 输入

架构方案应保证 read model 直接服务用户可读 IA，而不是让前端猜测内部状态：

- `CollaborationWorkbenchReadModel` 必须提供项目、协作摘要、设备、Runner、接入申请、授权、路由、恢复项、通知、证据、权限动作、技术详情。
- `devices[]` / `runners[]` 必须有可读字段：`displayName`、`ownerLabel`、`availabilityLabel`、`workTypeLabels`、`authorizationSummary`、`currentTaskLabel`、`lastSeenLabel`、`riskLabels`、`primaryAction`。
- `routeBoard[]` 必须有：`businessStatus`、`assignedDeviceLabel`、`routeReason`、`blockerLabel`、`nextOwnerLabel`、`nextAction`。
- `permissionGatedActions[]` 必须返回可读失败原因和服务端 gate 结果。
- `technicalDetails[]` 只能作为折叠、脱敏、证据层数据。
- 状态映射必须覆盖未知值；未知状态显示“需处理”，原始值进入技术详情。

## 给 Development Agent 的 IA 输入

研发实现必须遵守 IA 边界：

- 主模板只渲染用户可读字段，不直接渲染内部 id、raw status、token、secret、路径、endpoint、错误栈。
- 所有写操作必须走服务端 permission gate：邀请、确认授权、撤销授权、暂停接单、禁用电脑、释放租约、转派任务。
- API 失败必须返回 `displayMessage` 或等价可读字段。
- 技术详情默认非主信息，并对敏感字段脱敏。
- 空、加载、失败、只读、禁用按钮都必须有中文原因。
- 操作完成后必须能在操作记录或审计入口看到可读摘要。
- 不得破坏 V1 单机闭环。

## 给 Test Agent 的 IA 输入

测试验收应从用户可读 IA 出发：

- 双 Runner / 双 host 或受控真实虚拟 host 证据：能看到两台电脑在同一项目中枢。
- 路由解释：两个任务可分给不同 Runner；同一任务不能被两个 Runner 有效领取。
- 接入授权：邀请、配对、授权、撤销、过期都有中文状态和审计。
- 权限隔离：越权读取或领取被拒绝，并有可读原因和 AuditLog。
- 恢复状态：离线、租约超时、写回失败能进入可恢复状态，有责任人和下一步。
- 结果证据：TaskResult、AgentRun、evidenceRefs、testsOrChecks、qualityEvaluation、acceptancePolicy 可复核。
- 主 UI 禁曝：不得出现禁曝字段；若在技术详情出现，必须默认非主信息且脱敏。
- 兼容性：V1 单机闭环仍可用，或有明确非相关说明。

## IA 验收清单

- 页面目标覆盖同事接入、授权、路由、写回、恢复、验收。
- 导航模型将“协作设备”置于项目中枢下。
- 对象分组覆盖项目、设备、Runner、授权、路由、结果、证据、恢复、审计。
- 用户可见命名有中文映射。
- 主次信息层级清楚，技术详情不抢占主界面。
- 用户任务路径覆盖邀请、授权、路由、写回、恢复、越权、暂停/转派/撤销。
- 禁曝字段列表明确。
- 给设计、架构、研发、测试的 IA 输入明确且不越过岗位边界。
