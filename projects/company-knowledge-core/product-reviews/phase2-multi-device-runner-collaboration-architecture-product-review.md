---
type: Workflow
title: 阶段二多设备 Runner 协作技术方案产品复核
description: Product Manager Agent review of the Phase 2 multi-device Runner collaboration technical solution against PRD and workbench design.
timestamp: "2026-06-22T12:13:43Z"
reviewId: review.phase2.multi-device-runner.architecture.product
projectId: company-knowledge-core
ownerAgent: agent.company.product-manager
taskId: kt-v2-colleague-runner-product-architecture-review
status: accepted
decision: handoff_to_development
sourceMaterialRefs:
  - docs/product/ai-native-os/phase-2-multi-device-runner-collaboration-prd.md
  - projects/company-knowledge-core/design/phase2-multi-device-runner-workbench-design.md
  - projects/company-knowledge-core/technical-solutions/phase2-multi-device-runner-collaboration-technical-solution.md
operatingRuleRefs:
  - projects/company-knowledge-core/workflows/phase2-multi-device-collaboration-orchestrator-orchestrator.md
  - docs/agent-team/company-agent-constitution.md
  - docs/agent-team/agent-task-runtime-contract.md
  - docs/agent-team/human-acceptance-policy.md
  - docs/agent-team/common-agent-operating-rules.md
  - agents/agent.company.product-manager.md
  - projects/company-knowledge-core/project.md
---

# 阶段二多设备 Runner 协作技术方案产品复核

Review date: 2026-06-22
Reviewer: agent.company.product-manager
Task: kt-v2-colleague-runner-product-architecture-review

## 复核结论

产品结论：通过。

架构师输出的技术方案满足阶段二 PRD 与工作台设计规范，可交 `agent.company.development` 进入受控实现。不退回架构师。

本次通过不是最终上线验收。研发实现后仍必须由 Test Agent 验证真实双设备/双 host 协作、权限隔离、用户可读中文工作台、TaskResult/AgentRun 写回、通知和审计证据。真实阶段二验收不能只用本机双 Runner 模拟替代。

## 复核依据

- 已加载并按 `projects/company-knowledge-core/workflows/phase2-multi-device-collaboration-orchestrator-orchestrator.md` 执行：产品、设计、架构、研发、测试、PM 结论分离；开发必须在产品接受架构方案后开始；工作台必须用户可读；TaskResult 必须记录规则引用。
- PRD 输入：`docs/product/ai-native-os/phase-2-multi-device-runner-collaboration-prd.md`。
- 设计输入：`projects/company-knowledge-core/design/phase2-multi-device-runner-workbench-design.md`。
- 复核对象：`projects/company-knowledge-core/technical-solutions/phase2-multi-device-runner-collaboration-technical-solution.md`。

## 重点检查

| 检查项 | 产品判断 | 证据 |
| --- | --- | --- |
| 用户友好中文工作台 | 通过 | 技术方案第 12、13 节定义 `CollaborationWorkbenchReadModel`、中文业务状态、中文按钮、折叠技术详情，并禁止主 UI 暴露 `runnerId`、`deviceId`、raw status、路径、token。匹配设计规范的中文命名、不可暴露字段、空/加载/失败/只读状态要求。 |
| 同事接入流程 | 通过 | 技术方案第 5、7、14 节覆盖邀请、同事接受、设备注册、项目侧确认、授权生效、撤销/过期；流程与设计规范“邀请同事 -> 配对授权 -> 设备可接任务”一致。 |
| 权限与配对 | 通过 | 技术方案明确配对只证明设备加入项目，授权才决定可执行工作；`RunnerAuthorization` 按项目、任务类型、Agent、仓库、工具、数据范围 gate；secret 不进入 Runner、TaskResult、AgentRun、ContextPack 或工作台。满足 PRD 最小权限与越权拒绝要求。 |
| 路由状态与解释 | 通过 | 技术方案第 8、9、11、12 节覆盖硬过滤、排序、无候选原因、租约、心跳、状态映射、恢复动作和 routeBoard；能说明分配给谁、为什么分配、下一步谁处理。 |
| 双设备验收 | 通过 | 技术方案第 15.2、15.4 节要求两个 Runner 注册、两个任务分配给不同 Runner、双 claim 拒绝、离线重领、越权拒绝、写回失败重试；并明确真实验收需要两个不同真实 host 或受控真实虚拟 host，本地模拟只能研发自测。 |
| 边界与非目标 | 通过 | 技术方案第 3、16 节保持 Core 只负责中枢契约、调度、记录和读模型；Agent Ring 内部执行网络、公网穿透、MDM、远程桌面、大规模集群调度不纳入阶段二；同时保留 V1 单机 Runner 能力。 |

## PRD 验收覆盖

| PRD 验收 | 复核结果 | 说明 |
| --- | --- | --- |
| P2-AC-001 两台 Runner 注册同项目 | 覆盖 | Device + Runner registry、heartbeat、runner list/read model 均在方案中定义。 |
| P2-AC-002 两任务分给不同 Runner | 覆盖 | Scheduler 排序与 RoutingDecision 记录支持可追溯分配。 |
| P2-AC-003 同任务不可双执行 | 覆盖 | 单有效租约、lease token hash、expectedVersion 校验。 |
| P2-AC-004 离线/超时可恢复 | 覆盖 | stale lease、runner offline、恢复队列、转派/取消、通知和审计。 |
| P2-AC-005 越权不能拉资料/工具 | 覆盖 | Authorization gate + Context Pack 裁剪 + 拒绝审计。 |
| P2-AC-006 TaskResult 完整 | 覆盖 | finish 校验 Result Center 所需字段。 |
| P2-AC-007 AgentRun 写回 | 覆盖 | finish 要求 AgentRun ref 或等价运行记录，且列为研发强化切片。 |
| P2-AC-008 多设备状态可见 | 覆盖 | CollaborationWorkbenchReadModel 覆盖 devices、routeBoard、permissionGatedActions、recoveryItems。 |
| P2-AC-009 暂停/禁用/转派有审计通知 | 覆盖 | 写 API 统一服务端权限校验、AuditLog、NotificationRecord 和 displayMessage。 |
| P2-AC-010 不破坏 V1 单机闭环 | 覆盖 | 兼容现有 AgentRunner/lease API；旧 Runner 无 deviceId 时作为 V1/manual Runner，不作为同事接入唯一验收证据。 |

## 研发交付约束

以下不是架构退回项，但进入 Development Agent 的硬性交付约束：

1. 主 UI 必须默认中文业务表达；内部 ID、raw status、路径、token、secret、接口栈只能在脱敏技术详情或证据层出现。
2. 邀请、配对、授权、撤销、过期必须服务端 gate，不允许前端只读模型代替权限判断。
3. Context Pack 必须按项目、仓库、工具、资料、数据范围裁剪；越权拒绝必须有用户可读原因和 AuditLog。
4. `TaskResult` 与 `AgentRun` 写回必须可被 Result Center 校验，不能只依赖同事电脑本地文件。
5. 工作台 validator 必须检查中文按钮/状态、空/加载/失败/只读/禁用原因、主界面无内部字段。
6. 真实阶段二验收必须提交两个不同真实 host 或受控真实虚拟 host 的证据；本地双 Runner 模拟只能作为研发自测。

## 风险与处理

| 风险 | 产品处理 |
| --- | --- |
| 第二台真实 Runner host 不可用 | 不阻塞研发启动；阻塞最终阶段二验收。PM 需在测试前确认真实 host 或批准受控真实虚拟 host。 |
| AgentRun 当前可能只作为 evidenceRef | 不退回架构；研发第 6 切片必须补强 finish 契约或验证器。 |
| 授权模型细导致 UI 复杂 | 接受方案处理：主 UI 只显示业务摘要，细项放授权详情和技术证据。 |
| 网络抖动误判离线 | 接受方案处理：区分降级/离线/过期，保留最近同步状态和恢复动作。 |

## 最终决定

Decision: accepted.

Handoff: 可交 `agent.company.development`。

No architecture rework required.
