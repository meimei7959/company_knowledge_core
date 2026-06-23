---
type: Workflow
title: 阶段二多设备 Runner 协作 IA/UI addendum 后产品复核
description: Product Manager Agent review after Product IA, UI/interaction revision, and architecture addendum for Phase 2 multi-device Runner collaboration.
timestamp: "2026-06-22T12:54:41Z"
reviewId: review.phase2.multi-device-runner.ia-ui-addendum.product
projectId: company-knowledge-core
ownerAgent: agent.company.product-manager
taskId: kt-v2-colleague-runner-product-architecture-review-after-ia-ui
status: accepted
decision: handoff_to_development
sourceMaterialRefs:
  - docs/product/ai-native-os/phase-2-multi-device-runner-collaboration-prd.md
  - projects/company-knowledge-core/product-information-architecture/phase2-colleague-runner-workbench-information-architecture.md
  - projects/company-knowledge-core/design/phase2-multi-device-runner-workbench-ui-interaction-revision.md
  - projects/company-knowledge-core/technical-solutions/phase2-multi-device-runner-collaboration-technical-solution.md
  - projects/company-knowledge-core/technical-solutions/phase2-multi-device-runner-collaboration-ia-ui-impact-revision.md
operatingRuleRefs:
  - projects/company-knowledge-core/workflows/phase2-multi-device-collaboration-orchestrator.md
  - docs/agent-team/company-agent-constitution.md
  - docs/agent-team/agent-task-runtime-contract.md
  - docs/agent-team/human-acceptance-policy.md
  - docs/agent-team/common-agent-operating-rules.md
  - docs/agent-team/role-operating-specs.json
  - agents/agent.company.product-manager.md
  - projects/company-knowledge-core/project.md
  - projects/company-knowledge-core/AGENTS.md
---

# 阶段二多设备 Runner 协作 IA/UI addendum 后产品复核

Review date: 2026-06-22
Reviewer: agent.company.product-manager
Task: kt-v2-colleague-runner-product-architecture-review-after-ia-ui

## 复核结论

产品结论：通过。

可以交 `agent.company.development` 进入受控实现。研发输入必须同时包含原技术方案、架构 addendum、产品 IA、UI/交互返工稿和 PRD；不要求先把 addendum 合并回原技术方案正文后再启动研发。

必须修正项：无。

本次通过不是最终阶段二验收。真实双 host、多设备路由、权限隔离、TaskResult/AgentRun 写回、通知审计、用户可读工作台仍必须在研发后由 Test Agent 和 PM gate 验证。本地双 Runner 模拟只能作为研发自测，除非产品经理另行明确接受为阶段性替代证据。

## 复核依据

- PM Workflow：`projects/company-knowledge-core/workflows/phase2-multi-device-collaboration-orchestrator.md`。
- PRD：`docs/product/ai-native-os/phase-2-multi-device-runner-collaboration-prd.md`。
- 产品 IA：`projects/company-knowledge-core/product-information-architecture/phase2-colleague-runner-workbench-information-architecture.md`。
- UI/交互：`projects/company-knowledge-core/design/phase2-multi-device-runner-workbench-ui-interaction-revision.md`。
- 原技术方案：`projects/company-knowledge-core/technical-solutions/phase2-multi-device-runner-collaboration-technical-solution.md`。
- 架构 addendum：`projects/company-knowledge-core/technical-solutions/phase2-multi-device-runner-collaboration-ia-ui-impact-revision.md`。

阶段二多设备协作按 PM Workflow 执行，不作为共享 Skill 使用；本次产品经理使用 requirement/PRD scope 能力完成产品复核。

## 重点检查

| 检查项 | 产品判断 | 证据和约束 |
| --- | --- | --- |
| 同事接入 | 通过 | PRD、IA、UI 和技术方案均覆盖邀请、配对申请、项目侧确认、授权范围、有效期、撤销和只读设备。addendum 补清写 API/action contract，足够研发执行。 |
| PM Workflow 门禁 | 通过 | 研发准入所需 PRD、IA、UI/交互、原技术方案、架构 addendum 和产品通过结论已齐。本文件即产品通过结论。 |
| 产品 IA | 通过 | IA 将“协作设备”置于项目中枢下，覆盖项目、设备、Runner、授权、路由、恢复、结果、证据、审计和技术详情；主次层级和禁曝字段明确。 |
| UI/交互可理解性 | 通过 | UI 返工稿覆盖首屏、邀请弹窗、授权抽屉、设备/执行器状态、任务路由、异常/权限/空/加载/只读、中文文案和窄屏布局。 |
| 权限/配对 | 通过 | 架构保持“配对证明加入项目，授权决定可执行范围”；addendum 要求服务端 gate、危险动作二次确认、可读影响摘要、AuditLog 和 displayMessage。 |
| 任务路由 | 通过 | 原方案覆盖 Scheduler 硬过滤、排序、无候选原因、租约、心跳、离线/超时恢复；addendum 补充撤销、禁用、转交、返工重分配时必须重新过滤。 |
| 双设备验收 | 通过作为研发准入；最终验收仍有风险 | 原方案和 workflow 均要求至少两台设备或真实设备加明确模拟设备；最终真实双 host 不得由本机双 Runner 默认替代。 |
| 禁止主界面内部字段 | 通过 | IA 列出主界面禁曝字段；UI 和技术方案要求主界面用中文 label/display 字段，raw enum、id、endpoint、路径、错误栈只进脱敏技术详情。 |

## Addendum 接受判断

接受“原方案主干不变 + addendum 补强”的路径。

不要求返工原因：

- addendum 未改变 Core/Agent Ring 边界、身份模型、租约一致性、调度核心或 Context Pack 裁剪主模型。
- addendum 补齐的是研发可执行性：`collaborationSummary`、`staleStatePolicy`、危险动作契约、恢复不变量、审计通知可读摘要、验收检查。
- 这些补充可作为研发任务硬输入，不需要先重写原技术方案正文。

## 研发交付硬约束

1. 研发任务输入必须列入原技术方案和 addendum，不能只实现原技术方案。
2. 工作台主界面只渲染中文业务含义和 label/display 字段；内部 id、raw status、capability code、路径、sessionId、runnerId、deviceId、token、secret、endpoint、错误栈不得作为主信息展示。
3. 邀请、确认授权、撤销授权、暂停/恢复接单、禁用/启用电脑、释放租约、取消任务、转交执行中任务必须服务端校验权限，返回 `displayMessage`，写 AuditLog，并提供可读影响摘要。
4. 任务路由必须能解释为什么派给某个 Runner，以及为什么拒绝其他 Runner；撤销授权、禁用电脑、心跳过期、数据范围不足、只读/过期状态均必须重新过滤。
5. 加载失败、只读、数据过期必须保留最近安全可显示数据，并禁用不安全写操作。
6. 结果写回必须包含 TaskResult、AgentRun 或等价运行记录、NotificationRecord、AuditLog 和证据引用。
7. 验收必须覆盖真实双 host 或 PM 明确接受的阶段性替代证据；本地双 Runner 模拟不能直接关闭阶段二。

## 风险与处理

| 风险 | 产品处理 |
| --- | --- |
| 真实双 host 资源未准备 | 不阻塞研发启动；阻塞最终阶段二验收。PM/test 前必须确认真实 host 或批准阶段性替代证据。 |
| Addendum 与原方案分文件存在 | 不阻塞研发启动；Development Agent 的任务卡必须同时引用两份技术方案文件。 |
| UI 复杂度上升 | 接受。主界面保持摘要，授权细项和技术值放抽屉/折叠详情。 |
| 权限动作影响活跃租约 | 接受 addendum 的处理：进入 recovery/transfer flow，不静默失败。 |

## 最终决定

Decision: accepted.

Handoff: 可交 `agent.company.development`。

Architecture rework required: no.

Required fixes before development: none.

