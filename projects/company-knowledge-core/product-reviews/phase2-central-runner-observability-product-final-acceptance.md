---
type: ReviewRecord
title: Phase 2 方案二中枢 Runner 观测与登记入口产品最终验收
projectId: company-knowledge-core
reviewerAgent: agent.company.product-manager
status: blocked
businessConclusion: blocked_for_production_launch
timestamp: "2026-06-23T02:47:58Z"
sourceRefs:
  - docs/product/ai-native-os/phase-2-central-runner-observability-prd.md
  - projects/company-knowledge-core/design/phase2-central-runner-observability-workbench-design.md
  - task-results/tr-kt-v2-central-runner-observability-development.md
  - task-results/tr-kt-v2-central-runner-observability-permission-gate-rework.md
  - task-results/tr-kt-v2-central-runner-observability-test-regression.md
---

# Phase 2 方案二中枢 Runner 观测与登记入口产品最终验收

## 结论

产品验收结论：不批准生产上线，批准进入真实部署验收补跑。

本地实现、设计口径和测试回归已经证明：工作台定位为“登记入口可操作，执行监管只读”基本成立；创建项目、电脑注册/邀请、工具注册/申请、只读监管、中文可读信息结构、权限门禁、幂等和审计边界在本地/API/CLI/静态工作台范围内符合 Phase 2 方案二产品要求。

但 PRD 把真实双机验收列为本期必须有；开发、返工和回归 TaskResult 均明确真实双机、真实 API Gateway 权限系统、真实 Tool Owner 审批回调未验证。因此本次不能作为生产上线最终通过，只能作为本地功能与产品语义验收通过，真实部署前置验收阻塞未关闭。

## 验收矩阵

| 验收项 | 结论 | 产品判断 |
| --- | --- | --- |
| 工作台承担创建项目入口 | 条件通过 | PRD 要求 Owner 可登记新项目，设计要求提交申请/确认/审计、不直接派单；开发结果说明登记入口可操作、幂等、权限/审批状态清晰、写入边界有 AuditLog。 |
| 工作台承担电脑注册/邀请入口 | 条件通过 | PRD 要求 Owner 邀请同事电脑、Runner 管理员提交注册申请、授权后才可调度；设计覆盖邀请/注册流程、审批和确认；本地回归覆盖旧 Runner 注册兼容和只读 read model。真实双机邀请/注册链路未补跑。 |
| 工作台承担工具注册/申请入口 | 条件通过 | PRD 要求工具 Owner 或 Runner 管理员登记工具、审批后才能用于任务；设计覆盖工具状态和审批边界；返工回归覆盖低风险工具登记、高风险工具申请的权限拒绝与审计。真实 Tool Owner 审批回调未接。 |
| 执行监管只读 | 通过 | 设计明确运行监管区不提供派单、改状态、禁用电脑、验收通过、重试执行、释放占用等按钮；开发结果说明未新增直接派单、修复、篡改结果接口；回归结果确认 read model 仍只读。 |
| 用户看懂几台电脑、几个项目、任务与风险 | 通过 | PRD 和设计要求总览展示可见电脑数、项目数、任务数、风险数、最近更新时间；项目列表/详情使用中文名称、负责人、任务标题、需求标题、业务状态。 |
| 用户看懂项目任务明细 | 通过 | 设计按“需求 -> 任务 -> 执行记录”组织，任务明细列包含任务、对应需求、进展、Agent、电脑、模型、token、工具、最后更新、验收状态；满足 Owner 回答“谁在做、做到哪、下一步是什么”。 |
| 用户看懂每台电脑明细 | 通过 | PRD 要求电脑详情展示身份、授权、运行能力、当前工作、进展资源、历史摘要；设计电脑列表用于回答“哪台电脑在线、正在做什么、是否异常”。 |
| Agent / 工具 / Codex / Claude / 模型 / token 可理解 | 条件通过 | PRD 要求模型与 token 按 AgentRun 和任务累计展示，缺失标 unknown；设计要求主文案显示 Codex / Claude / local model、工具名称和 token 消耗。产品语义满足，但真实 Runner 上报中的模型/token 数据未在双机环境验证。 |
| 权限边界 | 条件通过 | 返工后 API/CLI 四类写入口缺 permissions 或权限不足均拒绝写入，且写 workbench.permission.denied AuditLog。缺真实 API Gateway 权限系统联调。 |
| 审批边界 | 条件通过 | 设计要求创建项目、电脑注册、工具注册均进入审批/确认/审计；实现证据覆盖本地状态流和审计边界。真实审批系统与 Tool Owner 回调未接。 |
| 幂等边界 | 条件通过 | PRD 要求创建请求必须带幂等键，重复提交不得重复创建；开发结果说明登记入口幂等，回归覆盖登记语义正常。并发缺权限/幂等压测未做。 |
| 审计边界 | 通过 | 开发和返工结果均说明写入口有 AuditLog；权限拒绝审计包含 actor、targetRef、before/after、policyResult 和缺失权限详情。 |
| 真实双机验收 | 阻塞 | PRD 明确要求至少两台不同电脑同时接入同一中枢，分别领取或执行不同任务，中枢准确展示状态、隔离和异常恢复；三份 TaskResult 均声明该项未执行。 |

## 产品可用性判断

用户主路径可理解：

- Owner 能从总览知道当前可见几台电脑、几个项目、任务量、风险量和最近更新时间。
- Owner 能从项目详情按需求、任务、执行记录理解工作归属，而不是被 Runner 平铺视图困住。
- Owner 能从电脑详情看出设备 Owner、授权范围、Codex / Claude / local model 能力、可用工具、当前任务、token、运行时长、错误摘要和历史摘要。
- 工具、模型、token 使用中文业务文案承载；内部 ID 只应放在默认收起的技术详情并脱敏。

仍需上线前实证：

- 两台真实电脑的机器指纹摘要必须不同，不能只靠进程名区分。
- 同一中枢下两台电脑分别接任务或执行任务后，总览、项目详情、电脑详情、任务详情必须同步显示真实心跳、租约、AgentRun、模型、token、工具和异常恢复证据。
- 未授权项目不应泄漏任务内容、Runner 明细或 token 汇总。

## 阻塞项

1. 真实双机验收未完成。
   - PRD 将真实双机列为本期必须有。
   - 开发结果、权限返工结果、测试回归结果均把该项列为未覆盖缺口。
   - 产品判定：生产上线前阻塞。

2. 真实 API Gateway 权限系统未联调。
   - 当前证据为本地 payload permissions 语义门禁。
   - 产品判定：若目标是生产中枢，必须补真实 Gateway 鉴权、权限拒绝、审计落盘和至少一次 smoke。

3. 真实 Tool Owner 审批回调未接。
   - 当前只覆盖本地状态流和审计边界。
   - 产品判定：高风险工具、写权限工具、外部 API 工具上线前必须走真实审批闭环。

4. 并发缺权限/幂等压测未做。
   - 产品判定：不阻塞本地 slice 验收，阻塞生产级登记入口开放。

## 阶段性放行范围

可以放行：

- 本地产品语义验收。
- 静态工作台/本地 API/CLI 演示。
- 测试 Agent 或部署 Agent 继续补跑真实双机、真实 Gateway、真实审批回调。

不能放行：

- 宣布 Phase 2 方案二生产上线完成。
- 对真实团队开放可执行调度入口。
- 把模拟权限、模拟审批或单机回归当作真实多设备验收证据。

## 上线前补验要求

1. 两台不同真实电脑或真实独立 host 接入同一中枢。
2. 分别完成邀请、注册申请、审批、心跳、授权进入可调度状态。
3. 两台电脑领取或执行不同任务；中枢展示项目、需求、任务、Runner、Agent、模型、token、工具、租约和进展。
4. 验证未授权项目隔离，不泄漏任务内容、Runner 明细、token 汇总。
5. 验证权限不足的创建项目、邀请电脑、工具登记/申请不会写入业务对象，只写权限拒绝审计。
6. 验证重复提交不会创建重复项目、重复邀请或重复工具申请。
7. 验证真实审批结果回写后，项目/电脑/工具状态、审计记录、通知记录一致。
8. 输出部署验收报告和 TaskResult 后，交产品经理复验。

## 最终判定

产品最终验收状态：blocked_for_production_launch。

本地产品语义：passed_with_remote_gap。

下一步：由测试 Agent 或部署 Agent 补跑真实双机、真实 Gateway 权限、真实审批回调和并发幂等 smoke；完成后再提交产品最终复验。
