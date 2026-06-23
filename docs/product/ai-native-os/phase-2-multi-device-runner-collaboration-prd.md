---
type: ProductRequirementPackage
title: 阶段二多设备 Runner 协作闭环产品需求包
description: 基于 V1 单机闭环后的同事电脑接入同一项目中枢、多设备 Runner 协作闭环需求。
timestamp: "2026-06-22T11:54:41Z"
projectId: company-knowledge-core
ownerAgent: agent.company.product-manager
status: draft
phase: phase-2
sourceBaseline:
  - docs/product/ai-native-os/requirement-tree.md
  - docs/product/ai-native-os/requirements.md
  - docs/product/ai-native-os/test-cases.md
  - docs/scheduler/task-dispatch-model.md
  - docs/harness/agent-ring-distributed-runner-proof-harness.md
  - projects/company-knowledge-core/coordination/ai-native-agent-v1-single-machine-upgrade-plan.md
relatedRequirements:
  - BR-001
  - BR-003
  - BR-005
  - UREQ-004
  - UREQ-005
  - UREQ-008
  - ANOS-REQ-050
  - ANOS-REQ-051
  - ANOS-REQ-052
  - ANOS-REQ-053
  - ANOS-REQ-060
  - ANOS-REQ-061
  - ANOS-REQ-062
  - ANOS-REQ-063
updatedAt: "2026-06-22T11:54:41Z"
---

# 阶段二多设备 Runner 协作闭环产品需求包

## 一句话目标

让同事把自己的电脑作为受控 Runner 接入同一个项目中枢后，可以被项目调度器安全分配任务、在本地执行、持续上报状态，并把 TaskResult、AgentRun、通知和审计写回同一项目事实链。

## 背景

V1 已证明单机闭环：项目中枢可以表达任务、Runner、本机执行、TaskResult、通知、审计和工作台可读状态。阶段二不再证明“本机能跑通”，而是验证组织级协作：多台同事电脑能在同一项目中枢下分工执行，且不会丢失权限、上下文、证据和验收边界。

## 业务目标

1. 项目 Owner 可以把同一项目的不同任务分配给不同同事电脑执行，不再依赖单台机器排队。
2. 每台同事电脑只看到、领取、执行自己被授权范围内的任务、仓库、工具和资料。
3. 调度器能根据 Runner 能力、在线状态、负载、项目范围和租约状态分配任务。
4. 项目中枢能实时看见“谁的电脑正在做什么、卡在哪里、证据是否写回、下一步谁验收”。
5. 任何离线、超时、权限不足、证据缺失、人工审批等待，都能形成可恢复的任务状态，而不是静默失败。

## 用户角色

| 角色 | 用户视角目标 |
| --- | --- |
| 项目 Owner | 看到所有设备、任务、风险和结果，能决定是否接入、暂停、验收或转派。 |
| 项目经理 Agent | 把产品包和任务队列分配给合适 Runner，处理阻塞和验收路由。 |
| 同事 Runner 管理员 | 在自己的电脑注册 Runner，知道自己被授权执行什么，能暂停、恢复、退出。 |
| 岗位 Agent 执行者 | 在本机拿到完整上下文、验收标准和允许工具，执行后写回标准结果。 |
| 测试 Agent | 验证多设备协作、租约、写回、异常恢复和权限隔离。 |
| 系统管理员 | 管理 Runner 准入、密钥、仓库范围、工具范围、审计和禁用。 |

## 用户场景

### 场景 1：同事电脑首次接入项目中枢

同事收到项目 Owner 邀请，在自己的电脑运行注册流程，选择项目、机器名称、可执行 Agent 角色、可用仓库和工具范围。注册完成后，项目中枢显示该 Runner 为“待授权”或“在线可调度”，并展示最近心跳。

验收信号：项目 Owner 能看懂这台电脑是谁的、能做什么、是否在线、被授权到哪个项目。

### 场景 2：调度器把任务分配给最合适的 Runner

项目中枢有多个待执行任务。调度器根据任务所需角色、能力、仓库范围、工具范围、负载和租约状态，给某台同事电脑发放租约。其他 Runner 看到任务已被占用，不能重复执行。

验收信号：同一任务同一时间只有一个有效租约；分配理由可解释；无合适 Runner 时任务进入 waiting_runner。

### 场景 3：Runner 在本地执行并写回统一结果

Runner 拉取上下文包，交给本地 Codex、Claude、模型或工具执行。完成后，必须写回 TaskResult、AgentRun、证据引用、检查结果、质量评价、验收策略和通知记录。

验收信号：项目 Owner 不需要登录同事电脑，也能在中枢看到完整结果与证据。

### 场景 4：Runner 离线或超时

Runner 失去心跳或租约超时。项目中枢标记任务为 stale_lease 或 runner_offline，并给项目经理 Agent 创建恢复动作：等待、续租、转派或取消。

验收信号：任务不会永久卡在 claimed；恢复动作有审计记录。

### 场景 5：权限边界拦截

Runner 尝试领取超出项目、仓库、工具或数据范围的任务。系统阻止领取或执行，并生成可读错误、通知和审计。

验收信号：越权不产生任务结果；审计能说明谁、何时、尝试访问什么、为什么被拒。

### 场景 6：人工审批等待

任务需要人审、工具 Owner 批准或高风险资料授权。Runner 不能绕过审批，只能写回 blocked/needs_approval 状态和审批请求。

验收信号：等待审批是可见状态，有责任人、材料、截止时间和下一步。

## 功能需求

| ID | 需求 | 验收要点 |
| --- | --- | --- |
| P2-RUN-001 | Runner 注册项目、设备、Owner、能力、可执行 Agent、工具、仓库和数据范围。 | 注册记录可在中枢查看；未授权 Runner 不可领取任务。 |
| P2-RUN-002 | Runner 心跳上报在线状态、当前负载、执行中任务、版本和最近错误。 | 工作台展示最后心跳时间；超时自动进入离线或异常。 |
| P2-RUN-003 | 调度器按任务要求匹配 Runner 能力、范围、状态和负载。 | 分配理由可追溯；无匹配时进入 waiting_runner。 |
| P2-RUN-004 | 任务领取采用租约机制，包含租约 Owner、过期时间、续租和释放。 | 同一任务不能双执行；超时可恢复。 |
| P2-RUN-005 | Runner 拉取上下文包时只包含授权范围内资料。 | 上下文包包含规则、任务、需求、验收、证据入口；不包含越权内容。 |
| P2-RUN-006 | Runner 完成后写回统一 TaskResult 和 AgentRun。 | 结果包含 summary、outputRefs、evidenceRefs、testsOrChecks、operatingRuleRefs、commonRulesEvaluation、qualityEvaluation、acceptancePolicy、handoffContract 或 terminalReason。 |
| P2-RUN-007 | 项目中枢显示多设备执行状态。 | 能按项目看到待领取、执行中、等待审批、超时、失败、待验收、完成。 |
| P2-RUN-008 | 支持人工转派、暂停 Runner、禁用 Runner、释放租约。 | 所有人工操作必须写 AuditLog 和 NotificationRecord。 |
| P2-RUN-009 | 权限拒绝、工具缺失、仓库不可用、上下文拉取失败、结果写回失败进入可恢复状态。 | 每种失败都有用户可读原因、下一步和责任人。 |
| P2-RUN-010 | 保留手工交接路径，直到完整 Agent Ring 产品可用。 | 手工交接仍必须写 AgentRun 或等价记录、TaskResult、NotificationRecord、AuditLog。 |

## 非功能需求

1. 可追溯：任何任务从创建、匹配、领取、执行、写回、验收到通知都能串成一条证据链。
2. 权限隔离：Runner 默认最小权限；项目、仓库、工具、数据范围、Agent 角色均需显式授权。
3. 可恢复：离线、超时、冲突、审批等待、写回失败不算完成，必须可重试、转派或人工处理。
4. 可解释：调度结果、拒绝原因、验收状态、阻塞原因面向项目 Owner 可读。
5. 一致性：TaskResult 和 AgentRun 是中心事实，不以同事电脑本地文件作为最终状态。
6. 安全：不把密钥、token、密码写入知识文件、任务结果或上下文包。
7. 兼容：阶段二必须保留 V1 单机闭环能力，不能要求所有任务都必须远程多设备执行。
8. 可测试：必须有最小双 Runner 或三 Runner 验收用例，覆盖成功、冲突、离线、越权和写回。

## 边界：不是 V1 单机闭环

阶段二要做：

- 多台同事电脑接入同一项目中枢。
- 中央调度器在多 Runner 间分配任务。
- Runner 能力、租约、心跳、权限、负载和失败状态可见。
- 本地执行结果写回同一 TaskResult/AgentRun 契约。
- 跨设备异常恢复、转派和审计。

阶段二不做：

- 不重做 V1 本机工作台文案和单机演示。
- 不把 Agent Ring 内部实现并入本仓库；本仓库定义中枢契约、调度和记录。
- 不支持无授权 Runner 自由读取项目资料。
- 不把本地聊天记录、截图、临时日志当作可复用知识直接发布。
- 不承诺跨公网复杂网络穿透、企业 MDM、远程桌面和大规模集群调度。
- 不要求阶段二一次覆盖所有业务 Agent 的完整生产效率指标。

## 验收标准

| ID | 验收项 | 可观察证据 |
| --- | --- | --- |
| P2-AC-001 | 至少两台 Runner 注册到同一项目中枢，其中一台可为当前本机，另一台可为同事电脑或受控模拟 Runner。 | Runner registry 记录含 owner、machine、scope、capabilities、heartbeat。 |
| P2-AC-002 | 调度器能把两个不同任务分配给不同 Runner。 | 两个任务的 assignedRunner、leaseOwner、leaseProof、AgentRun 不同且可追溯。 |
| P2-AC-003 | 同一任务不能被两个 Runner 同时有效领取。 | 第二个领取请求被拒绝或等待；AuditLog 记录原因。 |
| P2-AC-004 | Runner 离线或租约超时后，任务进入可恢复状态。 | 任务状态、通知、恢复动作和审计可见。 |
| P2-AC-005 | 越权 Runner 不能拉取不在范围内的项目资料或工具。 | 拒绝记录包含用户可读原因和审计。 |
| P2-AC-006 | 成功执行任务必须写回完整 TaskResult。 | TaskResult 字段满足任务运行契约。 |
| P2-AC-007 | 成功执行任务必须写回 AgentRun 或等价运行记录。 | 运行记录关联 taskId、runnerId、executorAgent、evidenceRefs、resultRef。 |
| P2-AC-008 | 工作台或中枢视图能让项目 Owner 看见多设备状态。 | 可读展示 Runner、任务、租约、阻塞、验收和下一步。 |
| P2-AC-009 | 人工暂停、禁用、转派 Runner 有审计和通知。 | AuditLog 与 NotificationRecord 引用操作人和影响对象。 |
| P2-AC-010 | 阶段二验收不破坏 V1 单机闭环。 | V1 单机验收检查仍通过或有明确非相关说明。 |

## 技术方案输入：交付给架构师

### 需要架构师决策

1. Runner 身份模型：设备、Owner、Agent 角色、项目授权和租约 Owner 的关系。
2. Runner 注册协议：本地 CLI、API/Gateway、Agent Ring stub 的最小一致接口。
3. 租约一致性：如何保证单任务单有效租约、续租、过期、释放和转派。
4. 上下文包裁剪：按项目、仓库、工具、数据范围生成最小上下文。
5. AgentRun 模型：Runner 本地执行与中心 TaskResult 的关联字段。
6. 多设备状态视图：中枢需要提供哪些查询模型给工作台和通知。
7. 失败恢复状态机：waiting_runner、claimed、running、needs_approval、stale_lease、runner_offline、writeback_failed、submitted、waiting_acceptance、done 的迁移规则。
8. 安全边界：Runner token、工具授权、仓库访问、日志脱敏、密钥禁止写回。

### 建议最小架构切片

1. Runner registry + heartbeat：支持注册、授权、心跳、暂停、禁用。
2. Scheduler lease：支持匹配、领取、续租、释放、超时恢复。
3. Context pull：生成带规则、任务、验收、允许资源的上下文包。
4. Result writeback：统一写回 TaskResult、AgentRun、NotificationRecord、AuditLog。
5. Multi-runner console read model：按项目展示 Runner 与任务状态。
6. Harness：至少双 Runner 成功执行、租约冲突、离线恢复、越权拒绝、写回失败。

### 必须保留的项目规则

- Core 只调度和记录，Agent Ring 执行仍是外部层。
- 知识写入必须先有 SourceMaterial/TaskResult 证据，不直接发布 verified knowledge。
- 所有写操作必须形成 AuditLog。
- TaskResult 必须记录 operatingRuleRefs 并通过 commonRulesEvaluation。
- 高影响权限、工具、安全、客户承诺和政策变更必须人审。

## 推荐后续任务

1. 架构师 Agent 输出阶段二多设备 Runner 协作技术方案。
2. 项目经理 Agent 拆分开发、测试、运维和文档任务。
3. 研发 Agent 实现 Runner registry、lease、context pull、result writeback 最小闭环。
4. 测试 Agent 建立多 Runner 验收 harness。
5. 运维 Agent 补充 Runner 接入、禁用、恢复和审计操作手册。
