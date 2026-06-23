---
type: ReviewRecord
title: 任务来源模型与接收审查机制测试计划
description: 覆盖 workSourceType、Defect、ReceiverReview、TaskResult 追溯继承、健康检查、CLI/API、模板和岗位 Skill 的验收矩阵。
timestamp: 2026-06-23T06:52:24Z
projectId: company-knowledge-core
taskId: task-source-receiver-review-test-plan
status: submitted
ownerAgent: agent.company.test
reviewerAgent: agent.company.test
sourceRefs:
  - zhenzhi_knowledge/core.py
  - zhenzhi_knowledge/cli.py
  - zhenzhi_knowledge/server.py
  - templates/project-task.md
  - templates/task-result.md
  - docs/agent-team/role-operating-specs.json
  - agents/agent.company.project-manager.md
  - tests/test_cli.py
scope:
  - task_source_model
  - defect_model
  - receiver_review_gate
  - task_result_traceability
  - project_health_check
  - cli_api_lifecycle
  - templates_and_skills
---

# 任务来源模型与接收审查机制测试计划

## 测试结论口径

这份文件是测试 Agent 先行输出的验收计划，不代表功能已经通过。研发完成后，测试 Agent 必须按本矩阵执行；任一 P0/P1 用例失败，机制不得宣布闭环。

## 当前输入观察

- `zhenzhi_knowledge/core.py` 已有 `workSourceType`、`Defect`、`ReceiverReview` 的部分核心函数。
- `validate_task_source_traceability()` 已定义来源规则，但需要接入 `validate_bundle` 才能成为仓库级硬门禁。
- `finish_project_task()` 当前已继承 `requirementRefs`，还需要验证并补齐 `workSourceType`、`defectRefs`、`acceptanceCriteriaRefs`、`receiverReviewRefs` 继承。
- CLI/API/模板/岗位规则检索结果显示尚未完整暴露新增对象和字段，应作为实现与验收重点。

## 验收矩阵

| ID | 优先级 | 场景 | 输入 | 期望结果 | 建议测试层 |
| --- | --- | --- | --- | --- | --- |
| TSRR-001 | P0 | Feature 任务必须绑定需求 | `workSourceType=feature` 且 `requirementRefs=[]` | `validate` 失败，错误包含 `feature task requires requirementRefs` | core + validate |
| TSRR-002 | P0 | Feature 任务绑定需求可通过来源校验 | `workSourceType=feature` 且 `requirementRefs=["REQ-001"]` | 来源校验通过；任务前置字段落盘 | core |
| TSRR-003 | P0 | Bugfix 任务必须绑定缺陷 | `workSourceType=bugfix` 且 `defectRefs=[]` | `validate` 失败，错误包含 `bugfix task requires defectRefs` | core + validate |
| TSRR-004 | P0 | Bugfix 可无需求但必须有 Defect | 先创建 `Defect`，再创建 bugfix 任务，`requirementRefs=[]` | 任务创建成功，`defectRefs/defectObjectRefs` 存在，`requirementRefs` 可为空 | core + CLI |
| TSRR-005 | P1 | Research 任务来源校验 | `workSourceType=research` 且无研究问题、资料、预期输出 | `validate` 失败并提示 research 缺输入 | core + validate |
| TSRR-006 | P1 | Knowledge ingest 来源校验 | `workSourceType=knowledge_ingest` 且无资料/知识任务 | `validate` 失败并提示缺资料来源 | core + validate |
| TSRR-007 | P1 | Maintenance 来源校验 | `workSourceType=maintenance` 且无原因、资料、预期输出 | `validate` 失败并提示缺维护原因 | core + validate |
| TSRR-008 | P0 | ReceiverReview 接受继续 | `decision=accepted_for_work` | 创建成功，状态和决策均为 `accepted_for_work`，审计存在 | core + CLI |
| TSRR-009 | P0 | ReceiverReview 带假设接受 | `decision=accepted_with_assumptions` 且有 `assumptions` | 创建成功，假设落盘；下游可继续但需在 TaskResult 带回假设影响 | core + CLI |
| TSRR-010 | P0 | ReceiverReview 带假设接受但无假设 | `decision=accepted_with_assumptions` 且 `assumptions=[]` | 创建失败，错误说明必须写 assumptions | core |
| TSRR-011 | P0 | ReceiverReview 打回返工 | `decision=needs_rework` 且有 `issues` | 创建成功；下游不得继续执行；PM 应路由返工 | core + health |
| TSRR-012 | P0 | ReceiverReview 打回但无问题 | `decision=needs_rework` 且 `issues=[]` | 创建失败，错误说明必须写 issues | core |
| TSRR-013 | P0 | ReceiverReview 需要人类决策 | `decision=human_decision_required` 且有 `issues` | 创建成功；健康检查暴露决策风险 | core + health |
| TSRR-014 | P0 | ReceiverReview 需要人类决策但无问题 | `decision=human_decision_required` 且 `issues=[]` | 创建失败，错误说明必须写 issues | core |
| TSRR-015 | P0 | TaskResult 追溯字段继承 | 完成带 `workSourceType/requirementRefs/defectRefs/acceptanceCriteriaRefs/receiverReviewRefs` 的任务 | TaskResult 同步写入全部追溯字段，不丢链路 | core + CLI |
| TSRR-016 | P0 | CLI 创建 Feature 任务 | `task create --work-source-type feature --requirement-ref REQ-001` | 任务落盘字段正确，`validate` 通过 | CLI |
| TSRR-017 | P0 | CLI 创建 Bugfix 任务 | `defect create` 后 `defect create-fix-task` | Defect 与修复任务双向关联，bugfix 无需求也可通过 | CLI |
| TSRR-018 | P0 | CLI 创建 ReceiverReview | `receiver-review create --decision accepted_for_work` | 生成 ReceiverReview，审计存在 | CLI |
| TSRR-019 | P0 | API 创建任务支持来源字段 | `POST /v0/tasks/create` 带来源字段 | API 返回任务，字段落盘；错误输入返回可读 4xx | API |
| TSRR-020 | P0 | API 创建缺陷 | `POST /v0/defects` | 返回 Defect 路径/对象，审计存在 | API |
| TSRR-021 | P0 | API 创建接收审查 | `POST /v0/receiver-reviews` | 返回 ReceiverReview，状态规则与 core 一致 | API |
| TSRR-022 | P0 | 项目健康检查识别 Feature 无需求 | 仓库中存在无 `requirementRefs` 的 feature 任务 | 健康检查暴露风险，包含任务路径和修复建议 | health |
| TSRR-023 | P0 | 项目健康检查识别 Bugfix 无缺陷 | 仓库中存在无 `defectRefs` 的 bugfix 任务 | 健康检查暴露风险，包含任务路径和修复建议 | health |
| TSRR-024 | P0 | 项目健康检查识别接收审查阻断 | 存在 `needs_rework` 或 `human_decision_required` ReceiverReview | 健康检查展示阻断，不允许下游误判为可执行 | health |
| TSRR-025 | P1 | Fixed Defect 必须有回归证据 | `Defect.status=fixed` 且 `regressionEvidenceRefs=[]` | 健康检查暴露“已修复但未回归”风险 | health |
| TSRR-026 | P1 | 模板字段完整 | `templates/project-task.md`、`task-result.md`、`defect.md`、`receiver-review.md` | 面向人可读，字段与校验一致，无内部黑话作为主说明 | template |
| TSRR-027 | P1 | 岗位规则接收审查 | 产品、架构、设计、研发、测试岗位规则 | 下游岗位开工前必须创建 ReceiverReview，打回/决策时不得继续执行 | skill |
| TSRR-028 | P1 | 测试 Agent 缺陷流转规则 | 测试失败创建 Defect，而不是硬绑 Requirement | Bugfix 任务追缺陷，缺陷可选追需求 | skill + lifecycle |
| TSRR-029 | P0 | 全生命周期正向闭环 | Requirement -> Feature Task -> ReceiverReview -> TaskResult -> Test -> Acceptance | 每一跳可追溯，CLI/API/read model 均能查到来源 | lifecycle |
| TSRR-030 | P0 | 全生命周期返工闭环 | Upstream artifact -> ReceiverReview `needs_rework` -> rework task -> fixed TaskResult -> new ReceiverReview | 返工链路有审计、任务来源和结果追溯 | lifecycle |

## 必须新增或更新的自动化测试

建议在 `tests/test_cli.py` 或拆分新文件 `tests/test_task_source_receiver_review.py` 中覆盖：

- `test_validate_bundle_rejects_feature_task_without_requirement_refs`
- `test_validate_bundle_rejects_bugfix_task_without_defect_refs`
- `test_bugfix_task_with_defect_does_not_require_requirement`
- `test_receiver_review_accepts_all_valid_decisions`
- `test_receiver_review_rejects_missing_issues_for_rework_or_human_decision`
- `test_receiver_review_rejects_missing_assumptions`
- `test_finish_project_task_inherits_traceability_fields`
- `test_project_health_reports_task_source_and_receiver_review_risks`
- `test_cli_task_create_supports_work_source_and_refs`
- `test_cli_defect_create_and_fix_task_lifecycle`
- `test_cli_receiver_review_create_lifecycle`
- `test_api_task_defect_receiver_review_lifecycle`
- `test_templates_include_traceability_and_receiver_review_fields`
- `test_role_specs_require_receiver_review_before_downstream_work`

## CLI/API 验收入口

CLI 必须可验：

- `zhenzhi-knowledge task create --work-source-type feature --requirement-ref REQ-001`
- `zhenzhi-knowledge task create --work-source-type bugfix --defect-ref DEF-001`
- `zhenzhi-knowledge defect create ...`
- `zhenzhi-knowledge defect create-fix-task ...`
- `zhenzhi-knowledge receiver-review create --decision accepted_for_work ...`
- `zhenzhi-knowledge receiver-review create --decision needs_rework --issue ...`

API 必须可验：

- `POST /v0/tasks/create`
- `POST /v0/defects`
- `POST /v0/defects/create-fix-task`
- `POST /v0/receiver-reviews`
- `GET /v0/tasks` 或任务详情能返回来源字段
- 健康/工作台 read model 能展示来源风险和 ReceiverReview 阻断

## 通过标准

- P0 用例全部通过。
- `python3 -m zhenzhi_knowledge.cli validate` 通过。
- 相关单测通过；API 生命周期至少有 fake server 或真实 HTTP server 路由级测试。
- 模板与岗位规则不是只写文档，必须有测试检查字段和规则存在。
- 失败路径必须产生可读错误、审计或健康风险，不允许静默继续。

## 发布阻断条件

- `validate_bundle` 未接入任务来源校验。
- TaskResult 未继承来源追溯字段。
- ReceiverReview 打回/人类决策后，下游仍能被标成可继续。
- Bugfix 被强制要求 Requirement，或无 Defect 也能创建/通过。
- CLI/API/模板/岗位规则任一主链路缺失且无测试覆盖。
