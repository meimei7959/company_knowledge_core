---
type: Workflow
title: ANOS-REQ-160 V0 只读任务事实视图技术方案
description: Architecture Agent technical solution for a read-only task fact view over existing task, runner, result, review, notification, audit, and source material records.
timestamp: "2026-06-23T08:01:06Z"
projectId: company-knowledge-core
taskId: kt-anos-req-160-v0-task-fact-view-architecture
ownerAgent: agent.company.architecture
status: submitted
requirementRefs:
  - ANOS-REQ-160
prdRef: docs/product/ai-native-os/task-execution-productization-prd.md
acceptanceMatrixRef: docs/product/ai-native-os/task-execution-productization-acceptance-matrix.md
receiverReviewRef: projects/company-knowledge-core/receiver-reviews/receiver-review.anos-req-160.architecture.md
---

# ANOS-REQ-160 V0 只读任务事实视图技术方案

## 结论

V0 应实现为现有对象之上的只读 projection。仓库当前已出现 partial `build_task_fact_view`、`GET /v0/projects/{projectId}/tasks/{taskId}/fact-view`、以及 CLI `task fact` 源码入口；Architecture Agent 接受这些作为 V0 读面锚点，但要求 Development Agent 按验收矩阵补齐字段、缺口、权限和测试，不得把 projection 升级成新的核心对象。

该 projection 可以服务 central API read model、CLI read output、或桌面工作台详情页使用的数据结构，但不得持久化为核心对象、不得写回任务状态、不得改 Scheduler / Agent Ring / Runner claim/lease/heartbeat/finish / TaskResult 写回链路。

推荐落点：

```txt
existing records
-> read-only task fact projector / serializer
-> central API or CLI read output
-> desktop workbench task detail rendering
```

## 架构边界

| 层 | 允许 | 禁止 |
| --- | --- | --- |
| Core read layer | 新增纯函数式读取/组装逻辑，例如 `build_task_fact_view(bundle, project_id, task_id)` | 新增核心对象、修改状态机、修改调度/租约/写回行为 |
| API/CLI | 增加只读端点或只读命令输出 | POST/PUT 写任务、写结果、改验收、改 lease |
| Workbench | 复用现有 `central-api-read-model` 和 `technicalDetailsTemplate` 类模式展示事实、证据、缺口 | 通过桌面 bridge 写 TaskResult、AgentRun、lease 或私有 Runner 状态 |
| Tests | 用 fixture 覆盖状态、缺口、脱敏和旧任务兼容 | 用测试修改真实任务闭环作为通过条件 |

## 现有依据

1. `docs/architecture/core-architecture.md` 已定义 ProjectTask、TaskResult、AgentRunner、AuditLog 等是核心对象。
2. `projects/company-knowledge-core/desktop-workbench-slice0/workbench-read-model.js` 已采用 `sourceOfTruth: central-api-read-model`，并包含 status、owner、nextAction、fallbackState、evidenceRefs 等展示结构。
3. `projects/company-knowledge-core/desktop-workbench-slice0/native-bridge-manifest.json` 已禁止桌面端直接写 TaskResult、AgentRun、lease 和私有 Runner 状态。
4. `zhenzhi_knowledge/core.py` 已有 `build_task_fact_view(bundle, project_id, task_id)`，返回 `schemaVersion: task-fact-view.v0`、`sourceOfTruth: existing-records`、`readOnly: true`、facts、gaps、redactions、sourceRefs；这是实现锚点，不是新增核心对象。
5. `zhenzhi_knowledge/server.py` 已有 `GET /v0/projects/{projectId}/tasks/{taskId}/fact-view`，调用 `build_task_fact_view`；V0 开发应补齐/验证该只读路由，而不是另建写链路。
6. `zhenzhi_knowledge/cli.py` 已有 `task fact <taskId> --project <projectId> --format json|markdown` parser 和调用逻辑；当前 shell 中 `zhenzhi-knowledge` entrypoint 不在 PATH，研发验证可先使用 `python3 -m zhenzhi_knowledge.cli ...`。

## 字段映射

| 事实区块 | 读取来源 | 字段 |
| --- | --- | --- |
| 任务身份 | `ProjectTask` frontmatter | taskId、title、projectId、workSourceType、priority、status、createdAt/timestamp、updatedAt |
| 需求来源 | `ProjectTask` | requirementRefs、requirementObjectRefs、acceptanceCriteriaRefs、sourceMaterialRefs、receiverReviewRefs |
| 当前状态 | `ProjectTask` + 派生解释表 | raw status、statusLabel、statusExplanation、nextStepOwner、nextStepReason |
| 执行责任 | `ProjectTask` + `AgentRunner` | assignee、executorAgent、assignedRunner、leaseOwner、runnerId、heartbeatAt、leaseHeartbeatAt |
| 执行过程 | `ProjectTask` + `AgentRun` refs | startedAt、completedAt、currentPhase、agentRunRefs、lastHeartbeatAt |
| 结果证据 | `ProjectTask.resultRef` + `TaskResult` | resultId、result status、summary、outputRefs、evidenceRefs、testsOrChecks |
| 质量规则 | `TaskResult` | operatingRuleRefs、commonRulesEvaluation、qualityEvaluation |
| 验收 | `TaskResult.acceptancePolicy` + `ReviewRecord` | acceptanceStatus、acceptanceOwner、reviewRefs、humanAcceptanceRequired |
| 审计通知 | `ProjectTask.auditRefs` + `NotificationRecord` | auditRefs、notificationRefs、lastAuditAction、delivery status |

## 缺口分类

`build_task_fact_view` 应输出缺口数组，不改变源对象：

| gapType | 条件 | 示例 |
| --- | --- | --- |
| `current gap` | 新任务按当前契约应该具备但缺失 | feature task 缺 requirementRefs、done 缺 TaskResult |
| `legacy gap` | 历史任务缺少后引入字段 | 旧任务缺 commonRulesEvaluation |
| `not applicable` | 该状态或任务类型不需要该字段 | pending task 无 TaskResult |
| `dangling ref` | 引用字段存在但目标对象不存在 | resultRef 指向缺失文件 |
| `status/result mismatch` | task status 与 TaskResult 结果冲突 | done + result=blocked |
| `security redacted` | 有事实但当前 viewer 无权读内容 | 证据材料仅显示脱敏引用 |

## 状态解释规则

只读 projection 内置映射，不修改 `ProjectTask.status`：

| status | explanation | required next step |
| --- | --- | --- |
| pending | 任务已创建，还未执行。 | 补条件、分配 Runner、或人工确认。 |
| waiting_runner | 等待可用 Runner。 | 展示能力、权限、在线状态、租约或匹配条件缺口。 |
| processing | Agent/Runner 正在执行。 | 展示 executorAgent、runner、阶段、心跳。 |
| blocked | 任务无法继续。 | 展示 blocker、owner、恢复动作。 |
| waiting_acceptance | 结果待验收。 | 展示 acceptanceOwner、resultRef、验收标准和证据。 |
| done | 任务完成。 | 展示结果、证据、验收记录；缺证据时显示 gap。 |
| failed | 执行失败。 | 展示失败原因、可重试性和下一责任人。 |
| unknown | 未识别状态。 | 展示 raw status 和数据修复建议。 |

## API / CLI 方案

V0 推荐沿用并加固现有两个只读入口；若实现排期必须收敛，API 入口优先，CLI 保留为验证和运维读面：

1. API：`GET /v0/projects/{projectId}/tasks/{taskId}/fact-view`
2. CLI：`zhenzhi-knowledge task fact <taskId> --project company-knowledge-core --format json|markdown`；entrypoint 未安装时，用 `python3 -m zhenzhi_knowledge.cli task fact <taskId> --project company-knowledge-core --format json|markdown` 验证源码路径。

返回结构是 read model：

```json
{
  "schemaVersion": "task-fact-view.v0",
  "sourceOfTruth": "existing-records",
  "projectId": "company-knowledge-core",
  "taskId": "example",
  "readOnly": true,
  "facts": {},
  "statusExplanation": {},
  "gaps": [],
  "redactions": [],
  "sourceRefs": []
}
```

该结构不得持久化为核心对象；若缓存给工作台，也必须标记 generatedAt、sourceRefs 和 stale policy。

## Workbench 方案

在 `desktop-workbench-slice0` 中增加或复用任务详情渲染区：

1. 读取 `taskFactView` 数组或单个对象。
2. 用现有 `escapeHtml` 和 `technicalDetailsTemplate` 样式展示 evidenceRefs、auditRefs、notificationRefs。
3. 对 gap 用用户可读中文展示：`当前缺口`、`历史缺口`、`不适用`、`引用缺失`。
4. 对 redaction 只展示 label、objectType、objectRef、reason，不展示 secret 值或未授权正文。
5. 不接入任何写操作按钮；如有 action 区，只能链接到既有任务/结果/审计记录。

## 当前实现校准

现有 `build_task_fact_view` 已覆盖 identity、source、status、execution、result、auditRefs、notificationRefs、gaps、redactions、danglingRefs、sourceRefs 等基础结构，但仍应按验收矩阵补强：

1. `done` 缺 `resultRef` 和缺 evidence/tests 的展示文案必须清晰区分 `result evidence gap`、`current gap`、`legacy gap`。
2. `waiting_runner` 缺等待原因、`waiting_acceptance` 缺验收 owner、`blocked` 缺恢复路径、未知状态、dangling ref、status/result mismatch 必须有稳定可测试输出。
3. ReviewRecord、NotificationRecord、AuditLog 的详情可见性应以引用和最近动作/状态为主；无法解析时显示 gap，不伪造闭环。
4. 当前 projection 返回 `kind: TaskFactView` 仅是 API kind/read model 名称；不得在 docs/schemas/core-objects.md 或核心对象目录中注册为核心对象。

## 安全和权限

1. projector 必须对字段名和值做 secret-like 检查：token、password、secret、key、credential、leaseToken 等只显示 hash/ref。
2. 本地路径只显示仓库相对路径或脱敏标签，避免暴露个人目录作为主要解释。
3. 未授权 SourceMaterial 只显示存在、类型、标题、访问限制。
4. 桌面 native bridge 继续禁止 `writeTaskResult`、`writeAgentRun`、`mutate lease`。

## 实施切片

| 切片 | Owner | 输出 |
| --- | --- | --- |
| DEV-1 Core projector hardening | Development Agent | 加固现有 `build_task_fact_view` 或等价只读 serializer，补齐 gap/redaction/status/acceptance/audit 规则。 |
| DEV-2 CLI/API read surface | Development Agent | 稳定现有 GET fact-view 与 CLI `task fact` 只读入口，返回 json/markdown。 |
| DEV-3 Workbench display | Development Agent | 单任务事实视图 UI，显示字段、缺口、证据、验收、审计。 |
| TEST-1 Acceptance matrix validation | Test Agent | 覆盖 22 条验收矩阵，特别是 P0。 |
| PRODUCT-1 Technical solution review | Product Manager Agent | 确认技术方案未扩大范围且满足产品语义。 |

## 测试策略

1. 单元测试：构造 pending、waiting_runner、processing、blocked、waiting_acceptance、done、failed、unknown 任务 fixture。
2. 缺口测试：done 缺 resultRef、done 缺 evidenceRefs、waiting_acceptance 缺 owner、waiting_runner 缺原因、dangling ref、status/result mismatch。
3. 旧任务测试：缺 requirementRefs / commonRulesEvaluation / qualityEvaluation 不崩溃，显示 `legacy gap`。
4. 安全测试：secret-like 值、leaseToken、绝对用户路径、未授权材料正文不出现在输出。
5. Workbench 渲染测试：页面不显示裸状态码作为唯一解释，不出现未转义 HTML，不出现写操作按钮。
6. 回归测试：现有 scheduler、runner、TaskResult writeback、project health 行为不变。
7. CLI/API 冒烟测试：`python3 -m zhenzhi_knowledge.cli task fact ... --format json|markdown` 与 GET fact-view 读取同一任务时，关键字段和 gap 口径一致。

## 风险和回滚

| 风险 | 缓解 |
| --- | --- |
| 读模型被误用为新真源 | 文件名、schema 和文档明确 `readOnly`、`sourceOfTruth: existing-records`。 |
| V0 被顺手扩展为 PM Health 重构 | PM Health 消费事实视图留到 V1，不在 DEV-1/2/3 中实现。 |
| 证据/材料泄露 | 默认脱敏，未授权内容只显示引用和限制说明。 |
| 旧任务质量参差导致 UI 混乱 | gap 分类是 V0 核心能力，旧任务显示 `legacy gap`。 |

回滚方式：删除/关闭只读 CLI/API/workbench入口即可；不会影响任务执行状态、Runner lease、TaskResult 写回或验收记录。

## 产品复核关注点

Product Manager Agent 复核时重点看：

1. 是否仍是 V0 只读事实视图。
2. 是否覆盖 ANOS-REQ-160 验收矩阵 P0。
3. 是否未新增核心对象。
4. 是否未重写执行链路。
5. 用户是否能看懂任务、责任、结果、证据、验收和下一步。
