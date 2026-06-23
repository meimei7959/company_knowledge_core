---
type: Workflow
title: Task Source Traceability and Receiver Review Technical Solution
description: Architecture solution for task source traceability, Defect, and ReceiverReview execution gates.
timestamp: "2026-06-23T06:51:58Z"
projectId: company-knowledge-core
status: draft
owner: agent.company.architecture
scope: ai-native-agent-runtime
sourceRefs:
  - zhenzhi_knowledge/core.py
  - zhenzhi_knowledge/cli.py
  - zhenzhi_knowledge/server.py
  - templates/project-task.md
  - templates/task-result.md
  - docs/agent-team/role-operating-specs.json
  - tests/test_cli.py
---

# 任务来源与接收审查技术方案

## 1. 结论

本方案不重新设计对象模型，直接承接当前 `zhenzhi_knowledge/core.py` 已经开始实现的 `workSourceType`、`Defect`、`ReceiverReview`、`validate_task_source_traceability()`、`create_defect()`、`create_bugfix_task()`、`create_receiver_review()` 等函数和常量。

研发下一步要做的是把这些半成品接入运行主链路：任务创建必须带来源，任务完成必须继承追溯字段，下游接活前必须形成 `ReceiverReview`，验证器和健康检查必须能拦截链路断点，CLI/API/模板/岗位规则/测试必须全部同步。

## 2. 当前实现判断

已经有的基础：

- `TYPE_VALUES` 已包含 `Defect`、`ReceiverReview`。
- 已有对象目录函数：`defect_storage_dir()`、`receiver_review_storage_dir()`。
- 已有来源类型：`WORK_SOURCE_TYPE_VALUES = feature | bugfix | project_setup | research | knowledge_ingest | maintenance`。
- 已有缺陷和接收审查状态集合：`DEFECT_STATUS_VALUES`、`RECEIVER_REVIEW_STATUS_VALUES`。
- `create_project_task()` 已接收 `work_source_type`、`requirement_refs`、`defect_refs`、`source_reason`、`receiverReviewRefs` 等字段，并写入 `## Work Source`。
- `validate_task_source_traceability()` 已经实现基础规则，但还没有接入 `validate_bundle()`。
- `create_requirement_task()` 当前先创建任务、再补需求字段，必须改成直接创建 `workSourceType=feature` 的需求任务。
- `finish_project_task()` 当前只继承了 `requirementRefs`，还没有完整继承任务来源、缺陷、接收审查等字段。
- CLI/API/模板/岗位规则/测试仍未闭环。

需要注意的兼容点：

- 当前 `DEFECT_STATUS_VALUES` 包含 `open`，但业务目标列出的缺陷初始状态是 `triaged`。为了兼容已有文件，可以保留 `open` 为迁移兼容值，但新建缺陷默认必须改为 `triaged`。
- `validate_bundle()` 当前对所有对象统一使用 `STATUS_VALUES` 检查 `status`。研发必须在该检查前按对象类型分流：`Defect.status` 用 `DEFECT_STATUS_VALUES`，`ReceiverReview.status` 或 `decision` 用 `RECEIVER_REVIEW_STATUS_VALUES`，避免新对象被通用状态误杀。

## 3. 数据模型补齐

### 3.1 ProjectTask / KnowledgeTask 来源字段

任务对象必须稳定写入以下字段：

- `workSourceType`
- `requirementRefs`
- `requirementObjectRefs`
- `acceptanceCriteriaRefs`
- `defectRefs`
- `defectObjectRefs`
- `incidentRefs`
- `operationRefs`
- `knowledgeTaskRefs`
- `researchQuestion`
- `sourceReason`
- `receiverReviewRefs`

规则：

- `feature` 必须有 `requirementRefs`。
- `bugfix` 必须有 `defectRefs`，允许没有 `requirementRefs`。
- `research` 至少有 `researchQuestion`、`sourceMaterialRefs` 或 `expectedOutput`。
- `knowledge_ingest` 至少有 `sourceMaterialRefs` 或 `knowledgeTaskRefs`。
- `maintenance` 至少有 `sourceReason`、`sourceMaterialRefs` 或 `expectedOutput`。

### 3.2 Defect

`Defect` 用于承接 bugfix 来源，不强制绑定需求。

字段：

- `defectId`
- `projectId`
- `reporter`
- `severity`
- `status`
- `requirementRefs`
- `sourceTaskRef`
- `sourceResultRef`
- `evidenceRefs`
- `expectedBehavior`
- `actualBehavior`
- `reproductionSteps`
- `fixTaskRefs`
- `regressionEvidenceRefs`

新建默认：

- `status: triaged`
- 如果由测试失败创建，必须写 `sourceTaskRef` 或 `sourceResultRef`。
- 如果是线上/人工反馈创建，必须写 `evidenceRefs` 或 `sourceReason`。

### 3.3 ReceiverReview

`ReceiverReview` 是下游 Agent 接收上游交付物前的输入门禁，不是最终验收。

字段：

- `reviewId`
- `projectId`
- `upstreamRef`
- `receiverAgent`
- `reviewerAgent`
- `decision`
- `status`
- `artifactRefs`
- `checklist`
- `issues`
- `assumptions`

判断值：

- `accepted_for_work`：可以继续。
- `accepted_with_assumptions`：带明确假设继续。
- `needs_rework`：打回返工。
- `human_decision_required`：需要人类决策。

规则：

- `needs_rework` 和 `human_decision_required` 必须写 `issues`。
- `accepted_with_assumptions` 必须写 `assumptions`。
- `accepted_for_work` 必须至少有 `checklist` 或 `artifactRefs`，避免空审查。
- `reviewerAgent` 默认等于 `receiverAgent`，除非是明确的人类或 PM 审查代理。

## 4. 核心函数改造清单

### 4.1 validate_bundle 接入

在 `validate_bundle()` 遍历对象时补以下分支：

1. 当 `fm.type in {"ProjectTask", "KnowledgeTask"}`：
   - 调用 `validate_task_source_traceability(rel_path, fm, require_explicit=True)`。
   - 迁移期可以允许 `legacyTraceabilityExempt: true`，但新任务禁止豁免。
   - 校验 `receiverReviewRefs` 中引用的对象必须存在，且类型为 `ReceiverReview`。

2. 当 `fm.type == "Defect"`：
   - `defectId`、`projectId`、`reporter`、`severity`、`status` 必填。
   - `status` 必须属于 `DEFECT_STATUS_VALUES`。
   - `fixed` 或 `closed` 必须有 `fixTaskRefs`。
   - `closed` 必须有 `regressionEvidenceRefs`。
   - 如果没有 `requirementRefs`，不报错。

3. 当 `fm.type == "ReceiverReview"`：
   - `reviewId`、`projectId`、`upstreamRef`、`receiverAgent`、`reviewerAgent`、`decision` 必填。
   - `decision` 必须属于 `RECEIVER_REVIEW_STATUS_VALUES`。
   - `status` 如存在，必须等于 `decision` 或属于同一集合。
   - `needs_rework` / `human_decision_required` 必须有 `issues`。
   - `accepted_with_assumptions` 必须有 `assumptions`。
   - `accepted_for_work` 必须有 `checklist` 或 `artifactRefs`。

### 4.2 TaskResult 继承追溯字段

在 `finish_project_task()` 写 `TaskResult.frontmatter` 时，从任务继承以下字段：

- `workSourceType`
- `requirementRefs`
- `requirementObjectRefs`
- `acceptanceCriteriaRefs`
- `defectRefs`
- `defectObjectRefs`
- `incidentRefs`
- `operationRefs`
- `knowledgeTaskRefs`
- `researchQuestion`
- `sourceReason`
- `receiverReviewRefs`

规则：

- `TaskResult.workSourceType` 必须等于任务有效来源类型。
- 如果任务为 `bugfix`，结果里必须保留 `defectRefs`。
- 如果任务为 `feature`，结果里必须保留 `requirementRefs` 和 `acceptanceCriteriaRefs`。
- `TaskResult` 不重新推断来源，以任务为准。

### 4.3 create_requirement_task

`create_requirement_task()` 必须直接调用：

- `work_source_type="feature"`
- `requirement_refs=[requirementId]`
- `requirement_object_refs=[requirement path]`
- `acceptance_criteria_refs=[...]`
- `source_reason="Feature work from requirement <id>"`

不要先创建 maintenance/knowledge_ingest 任务后再补字段。否则中途失败会留下错误来源类型任务。

### 4.4 create_bugfix_task

`create_bugfix_task()` 已经基本正确，但要补：

- 创建前确认 `Defect.status` 不是 `closed`。
- 创建后把 `Defect.status` 从 `triaged` 或 `reopened` 改为 `in_progress`。
- 任务写 `workSourceType=bugfix`、`defectRefs`、`defectObjectRefs`。
- 任务完成后由测试回归再把缺陷流转到 `fixed` 或 `closed`，研发不直接关闭缺陷。

### 4.5 create_receiver_review

保持现有函数，补以下能力：

- 同时写 `decision` 和 `status`，两者默认一致。
- 写 `upstreamAgent` 可选字段，便于工作台展示“谁交给谁”。
- 接收审查通过后，把生成的 review 路径追加到下游任务 `receiverReviewRefs`。
- `needs_rework` 自动返回上游返工任务建议，但不由架构函数直接创建返工任务。

## 5. CLI 改造

### 5.1 task create

`zhenzhi-knowledge task create` 增加：

- `--work-source-type`
- `--requirement-ref`，可重复。
- `--requirement-object-ref`，可重复。
- `--acceptance-criteria-ref`，可重复。
- `--defect-ref`，可重复。
- `--defect-object-ref`，可重复。
- `--incident-ref`，可重复。
- `--operation-ref`，可重复。
- `--knowledge-task-ref`，可重复。
- `--research-question`
- `--source-reason`
- `--receiver-review-ref`，可重复。

这些参数必须传入 `create_project_task()`，不是只写命令行表面。

### 5.2 defect create

新增：

```bash
zhenzhi-knowledge defect create \
  --title <title> \
  --project <projectId> \
  --reporter <agent-or-human> \
  --severity <low|medium|high|critical> \
  --requirement-ref <optional> \
  --source-task-ref <optional> \
  --source-result-ref <optional> \
  --evidence-ref <ref> \
  --expected <text> \
  --actual <text> \
  --step <text>
```

调用 `create_defect()`。

### 5.3 defect create-fix-task

新增：

```bash
zhenzhi-knowledge defect create-fix-task \
  --defect-id <defectId> \
  --requester agent.company.test \
  --assignee agent.company.development \
  --priority high
```

调用 `create_bugfix_task()`。

### 5.4 receiver-review create

新增：

```bash
zhenzhi-knowledge receiver-review create \
  --project <projectId> \
  --upstream-ref <artifact-or-task-result> \
  --receiver-agent agent.company.architecture \
  --reviewer-agent agent.company.architecture \
  --decision accepted_for_work \
  --artifact-ref <ref> \
  --check <checklist item> \
  --issue <issue> \
  --assumption <assumption>
```

调用 `create_receiver_review()`。

## 6. API 改造

### 6.1 /v0/tasks/create

扩展现有 `/v0/tasks/create`，支持与 CLI 相同的来源字段。服务端必须把 payload 映射到 `create_project_task()` 参数，不允许丢字段。

返回体增加：

- `workSourceType`
- `requirementRefs`
- `defectRefs`
- `receiverReviewRefs`

### 6.2 /v0/defects

新增：

- `POST /v0/defects`：创建缺陷。
- `GET /v0/defects?projectId=<projectId>`：列出项目缺陷。
- `POST /v0/defects/create-fix-task`：创建 bugfix 任务。

### 6.3 /v0/receiver-reviews

新增：

- `POST /v0/receiver-reviews`：创建接收审查。
- `GET /v0/receiver-reviews?projectId=<projectId>&upstreamRef=<ref>`：查询接收审查。

### 6.4 /v0/tasks/finish

保持入口不变，但结果必须自动继承任务追溯字段。API 不要求客户端重复提交来源字段，避免客户端和任务事实不一致。

## 7. 健康检查与读模型

### 7.1 项目健康检查

`run_project_manager_health_check()` 增加风险：

- `feature` 任务无 `requirementRefs`：高风险。
- `bugfix` 任务无 `defectRefs`：高风险。
- `research` / `knowledge_ingest` / `maintenance` 来源依据不足：中风险。
- `ReceiverReview.decision == needs_rework`：高风险，下一步返回上游返工。
- `ReceiverReview.decision == human_decision_required`：高风险，下一步找人类决策。
- `Defect.status == fixed` 但没有 `regressionEvidenceRefs`：高风险。
- `Defect.status == closed` 但没有回归证据：阻塞。

### 7.2 工作台读模型

`scheduler_workbench_read_model()`、`workbench_project_execution_read_model()`、`v1_workbench_read_model()` 至少暴露：

- 任务来源：功能需求、缺陷修复、项目初始化、研究、知识录入、维护。
- 来源引用：需求、缺陷、验收标准、资料、原因。
- 接收审查状态：可继续、带假设继续、打回返工、等待人类决策。
- 缺陷状态：待确认、处理中、已修复待回归、已关闭、重新打开。
- 风险提示：缺来源、缺审查、审查未通过、修复缺回归。

面向用户的主显示必须中文，不直接显示 `workSourceType`、`receiverReviewRefs`、`defectRefs` 作为主要信息。

## 8. 模板更新

### 8.1 templates/project-task.md

补字段：

- `workSourceType`
- `requirementRefs`
- `requirementObjectRefs`
- `acceptanceCriteriaRefs`
- `defectRefs`
- `defectObjectRefs`
- `incidentRefs`
- `operationRefs`
- `knowledgeTaskRefs`
- `researchQuestion`
- `sourceReason`
- `receiverReviewRefs`

正文新增 `## Work Source` 和 `## Receiver Reviews`。

### 8.2 templates/task-result.md

补同样的追溯字段，说明它们来自任务继承，执行 Agent 不手填改写。

### 8.3 templates/defect.md

新增 Defect 模板，包含 expected/actual/reproduction/fix/regression 四段。

### 8.4 templates/receiver-review.md

新增 ReceiverReview 模板，包含 checklist/issues/assumptions/decision 四段。

## 9. Skill 和岗位规则更新

### 9.1 项目经理 Agent

- 编排任务时必须声明 `workSourceType`。
- Feature 任务没有需求引用不得派发给研发。
- Bugfix 任务没有 Defect 不得派发给研发。
- 下游任务启动前必须检查是否已有对应 `ReceiverReview`。

### 9.2 产品经理 Agent

- 需求拆分输出必须可被 Feature 任务引用。
- 需求交给架构/设计/研发前，接收方必须做 `ReceiverReview`。
- 产品不直接创建 bugfix 任务，除非先创建 Defect 或引用已有 Defect。

### 9.3 架构师 Agent

- 接收 PRD/需求包前必须创建 `ReceiverReview`。
- 需求缺失、目标偏移、验收标准不足时，用 `needs_rework` 打回产品。
- 若可继续但有假设，用 `accepted_with_assumptions` 并明确假设。

### 9.4 设计 Agent

- 信息架构来自产品，设计只审查输入是否足够做 UI/交互设计。
- 缺用户路径、页面目标、关键状态时打回产品。

### 9.5 研发 Agent

- 接收技术方案前必须创建 `ReceiverReview`。
- 任务必须能追到需求或缺陷，否则不得开工。
- 测试打回的问题必须先形成 Defect，再创建 bugfix 任务。

### 9.6 测试 Agent

- 测试失败必须创建或更新 Defect。
- Bugfix 回归通过后写 `regressionEvidenceRefs`。
- 测试 TaskResult 必须保留需求/缺陷追溯字段。

## 10. 测试切面

新增或扩展测试：

- Feature 任务无 `requirementRefs`，`validate_bundle()` 失败。
- Bugfix 任务无 `defectRefs`，`validate_bundle()` 失败。
- Bugfix 任务有 `defectRefs` 且无 `requirementRefs`，校验通过。
- Research / knowledge_ingest / maintenance 来源依据不足时失败。
- `ReceiverReview.needs_rework` 无 `issues` 失败。
- `ReceiverReview.human_decision_required` 无 `issues` 失败。
- `ReceiverReview.accepted_with_assumptions` 无 `assumptions` 失败。
- `finish_project_task()` 生成的 TaskResult 自动继承来源字段。
- `create_requirement_task()` 直接生成 `workSourceType=feature` 的任务。
- CLI `task create` 来源字段写入成功。
- CLI `defect create` 和 `defect create-fix-task` 成功。
- CLI `receiver-review create` 成功。
- API `/v0/tasks/create` 来源字段写入成功。
- API `/v0/defects` 和 `/v0/receiver-reviews` 成功。
- 项目健康检查能看到缺来源、审查打回、人类决策、缺回归证据风险。
- 工作台读模型能展示用户可读的来源和接收审查状态。

## 11. 兼容和迁移策略

### 11.1 旧任务

旧任务分三类处理：

- 已完成且有 TaskResult 的历史任务：允许 `legacyTraceabilityExempt: true`，不阻塞当前发布。
- 未完成任务：必须补 `workSourceType` 和来源引用。
- 新建任务：禁止缺来源。

### 11.2 旧 bugfix

旧 bugfix 任务如果没有缺陷对象，迁移脚本应按任务结果或测试报告生成 Defect，并回填 `defectRefs`。

### 11.3 旧接收交接

已有“上游交给下游”的交接文件可以迁移为 `ReceiverReview`：

- 如果下游已经开工且无明显问题，迁移为 `accepted_with_assumptions`，假设写“历史交接已被执行，后续发现问题走 Defect”。
- 如果下游未开工，必须重新审查。

### 11.4 API 兼容

旧客户端不传来源字段时：

- 服务端可以用 `infer_work_source_type()` 推断。
- 但如果推断后不满足来源规则，必须拒绝新任务创建。
- 拒绝要写审计：`task_source_traceability.denied`。

## 12. 研发交付顺序

建议研发按以下顺序实现：

1. `validate_bundle()` 接入任务来源、Defect、ReceiverReview 校验。
2. `finish_project_task()` 继承追溯字段。
3. `create_requirement_task()` 改为直接创建 feature 任务。
4. 补 CLI 命令和参数。
5. 补 API 端点和 payload 映射。
6. 补项目健康检查和工作台读模型。
7. 补模板。
8. 补岗位规则和 Skill 引用。
9. 补单测和生命周期测试。
10. 跑 `python3 -m zhenzhi_knowledge.cli validate`、相关单测、必要的 API 路径测试。

## 13. 验收标准

研发完成后，测试 Agent 必须证明：

- 任务来源模型可被创建、校验、查询、展示。
- Feature 任务不能脱离需求。
- Bugfix 任务可以脱离需求，但不能脱离 Defect。
- 接收审查能阻断下游错误开工。
- TaskResult 可追溯到原始需求或缺陷。
- 健康检查能发现断链风险。
- CLI/API/模板/岗位规则都接入同一套机制。

只有这些全部通过，才算“任务为什么存在、来自哪里、下游是否可继续”机制闭环。
