---
type: AcceptanceMatrix
requirementId: ANOS-REQ-160
title: ANOS-REQ-160 任务执行产品化与 Agent 成长闭环验收矩阵
description: 面向 ANOS-REQ-160 的分阶段验收标准；V0 验收只读任务事实视图，V1/V2 作为 PM-worker 调度和 Agent 成长闭环的后续验收口径。
timestamp: "2026-06-23T07:45:45Z"
projectId: company-knowledge-core
ownerAgent: agent.company.product-manager
status: draft
prdRef: docs/product/ai-native-os/task-execution-productization-prd.md
---

# ANOS-REQ-160 任务执行产品化与 Agent 成长闭环验收矩阵

## 验收口径

V0 验收只判断任务事实视图是否正确展示现有事实、缺口、权限和下一步。任何新增核心对象、重写执行链路、改变任务状态机、直接执行任务操作的实现都不通过本矩阵。

V1/V2 验收不扩大 V0 实现面。V1 验收 PM Agent 调度子 Agent worker 的记录、边界和收敛是否进入现有任务事实；V2 验收失败、返工、人工纠偏和阻塞恢复是否能沉淀为 AgentImprovementProposal、EvalCase 和能力更新路径。

## 矩阵

| ID | 优先级 | 需求 | 前置条件 | 验收方式 | 预期结果 |
| --- | --- | --- | --- | --- | --- |
| ANOS-160-AC-001 | P0 | 任一活跃 ProjectTask 可打开只读事实视图 | 存在 pending / waiting_runner / processing / blocked / waiting_acceptance / done / failed 至少一种任务样例 | UI/API/CLI 查看任务详情 | 视图打开成功，显示 taskId、title、projectId、status 和更新时间。 |
| ANOS-160-AC-002 | P0 | V0 不新增核心对象 | 完成技术方案或实现 diff | 架构/代码审查 | 未新增 `TaskFactView` 等核心对象类型；只新增读模型、projection、serializer 或 UI 展示层实现。 |
| ANOS-160-AC-003 | P0 | 不重写执行链路 | 完成技术方案或实现 diff | 架构/代码审查 + 回归检查 | Scheduler、Agent Ring、Runner claim/lease/heartbeat/finish、TaskResult 写回流程无行为性重写。 |
| ANOS-160-AC-004 | P0 | 视图只读 | 打开任一任务事实视图 | UI/API 检查 | 无编辑、领取、改派、重试、验收、拒绝、关闭、写回知识或修改证据的 V0 操作。 |
| ANOS-160-AC-005 | P0 | 需求来源可追溯 | feature task 带 requirementRefs/sourceMaterialRefs/acceptanceCriteriaRefs | 查看事实视图 | 展示需求、来源材料和验收标准引用；引用缺失时展示缺口类型。 |
| ANOS-160-AC-006 | P0 | done 缺结果不得显示为完整闭环 | done task 缺 resultRef 或 TaskResult | 查看事实视图 | 状态解释显示完成状态来源，同时标 `result evidence gap`，不得显示为证据完整。 |
| ANOS-160-AC-007 | P0 | done 缺证据必须暴露 | done task 有 TaskResult 但缺 evidenceRefs/testsOrChecks | 查看事实视图 | 展示 resultRef，并将缺 evidence 或 tests 标为 `current gap` 或 `legacy gap`。 |
| ANOS-160-AC-008 | P0 | waiting_runner 必须解释等待原因 | waiting_runner task 有或缺 Runner 匹配事实 | 查看事实视图 | 展示等待原因；无法判断时显示 `waiting reason unknown` 和缺失字段。 |
| ANOS-160-AC-009 | P0 | waiting_acceptance 必须显示验收路由 | waiting_acceptance task 有 TaskResult | 查看事实视图 | 展示 acceptanceOwner/acceptancePolicy/reviewRefs/resultRef；缺 owner 时标验收路由缺口。 |
| ANOS-160-AC-010 | P0 | blocked 必须显示恢复路径 | blocked task 有 blocker 或缺 blocker | 查看事实视图 | 展示阻塞原因、owner、下一步；缺信息时显示 `blocker detail missing`。 |
| ANOS-160-AC-011 | P1 | processing 显示执行责任和心跳 | processing task 有 assignedRunner/leaseOwner/AgentRun 或部分缺失 | 查看事实视图 | 展示 executorAgent、runner/host、currentPhase、lastHeartbeatAt；缺字段显性标记。 |
| ANOS-160-AC-012 | P1 | pending 显示下一步责任 | pending task | 查看事实视图 | 展示需要补条件、分配 Runner 或人工确认的下一步；无法判断时标 `next step unknown`。 |
| ANOS-160-AC-013 | P0 | 旧任务兼容 | 历史任务缺 requirementRefs、qualityEvaluation 或 commonRulesEvaluation | 查看事实视图 | 页面不崩溃，不白屏；已有事实正常显示，缺失项标 `legacy gap`。 |
| ANOS-160-AC-014 | P0 | 状态与结果不一致必须暴露 | task status 为 done 但 TaskResult result 为 blocked/rejected，或 status 非 done 但已有结果 | 查看事实视图 | 显示 `status/result mismatch`，并展示原始 status 与 resultRef。 |
| ANOS-160-AC-015 | P0 | 质量和规则评价不可默认通过 | TaskResult 缺 qualityEvaluation 或 commonRulesEvaluation | 查看事实视图 | 显示缺口，不显示 passed、accepted 或完整闭环。 |
| ANOS-160-AC-016 | P0 | 审计和通知引用可见 | task 有 AuditLog/NotificationRecord 引用或可关联记录 | 查看事实视图 | 展示最近审计动作和通知状态；缺审计时标 `audit gap`。 |
| ANOS-160-AC-017 | P0 | 敏感信息不泄露 | evidence/source/audit 含 secret-like 字段、token、密码或受限材料 | 安全检查 + 人工审查 | 只展示脱敏引用、标题、类型和权限说明；不展示 secret 值。 |
| ANOS-160-AC-018 | P1 | 未授权证据内容受限 | 当前用户/Agent 无权读某证据内容 | 权限场景检查 | 视图展示证据存在和访问限制，不展示正文。 |
| ANOS-160-AC-019 | P1 | 引用缺失可诊断 | 任务引用不存在的 TaskResult、SourceMaterial、Review 或 Audit | 查看事实视图 | 显示 `dangling ref`、引用字段和引用值，不抛内部异常。 |
| ANOS-160-AC-020 | P1 | 未知状态可诊断 | task status 为未识别值 | 查看事实视图 | 展示 raw status、来源对象、`unknown status` 和需要修复的数据契约。 |
| ANOS-160-AC-021 | P1 | 数据加载失败不改变任务 | 模拟事实视图加载局部失败 | UI/API 测试 | 展示加载失败来源和重试提示；不修改 ProjectTask 或 TaskResult。 |
| ANOS-160-AC-022 | P0 | 验收结果可复核 | 完成 V0 实现和测试 | 测试报告审查 | 每个 P0 验收项有测试证据、截图/API 输出或代码审查证据。 |
| ANOS-160-AC-023 | P1 | worker 参与记录可见 | 某任务由 PM Agent 调度 Architecture/Development/Test/Review worker 中至少一个完成 | 查看事实视图 | 展示 worker role、输入摘要、边界、输出摘要、证据引用和 PM 收敛结论；缺失项标 `worker trace gap`。 |
| ANOS-160-AC-024 | P1 | 未使用 worker 不误报 | 某任务未使用子 Agent worker | 查看事实视图 | worker 区块显示 `not applicable`，不把未使用 worker 误判为失败。 |
| ANOS-160-AC-025 | P1 | 成长信号可见 | 某任务存在验收拒绝、返工、人工纠偏或阻塞恢复记录 | 查看事实视图 | 展示成长信号；如果未生成改进候选，标 `learning loop gap`。 |

## V1 PM-worker 调度验收候选

| ID | 优先级 | 需求 | 前置条件 | 验收方式 | 预期结果 |
| --- | --- | --- | --- | --- | --- |
| ANOS-160-V1-AC-001 | P0 | PM 调度 worker 有明确契约 | PM Agent 调度一个 worker | 查看任务记录 / TaskResult / Audit | 能看到 worker role、输入、边界、允许动作、禁止动作、输出格式和证据要求。 |
| ANOS-160-V1-AC-002 | P0 | worker 输出必须由 PM 收敛 | worker 已产出架构/研发/测试/审查结果 | 查看 PM 收敛记录 | PM 明确接受、部分接受、拒绝、要求返工或转人工，worker 输出不直接等同最终任务结论。 |
| ANOS-160-V1-AC-003 | P0 | worker 权限边界被执行 | Test worker 与 Development worker 同时参与任务 | 审查输出和文件变更 | Test worker 不修改研发文件或宣布最终验收；Development worker 不自验收产品通过。 |
| ANOS-160-V1-AC-004 | P1 | worker 结果进入现有事实链 | worker 完成任务片段 | 查看 TaskResult / Review / Audit / evidenceRefs | worker 输出和证据能被任务事实视图追溯，不只停留在聊天上下文。 |
| ANOS-160-V1-AC-005 | P0 | Development worker 必须运行工程质量门 | Development worker 完成代码实现 | 查看 TaskResult / qualityEvaluation | TaskResult 包含 `development_quality_gate` 命令和 verdict；缺失时不能进入完整闭环。 |
| ANOS-160-V1-AC-006 | P0 | 高风险核心文件需要架构证据 | Development worker 修改 core/cli/server/feishu 或调度/Runner/TaskResult/Audit/Review/权限路径 | 运行质量工具 + 架构审查 | 没有 architecture review ref 时质量门 fail；有 ref 时记录审查证据。 |
| ANOS-160-V1-AC-007 | P0 | 缺测试不能静默通过 | Development worker 修改代码但没有测试更新 | 运行质量工具 | 质量门 fail，除非 TaskResult 记录明确环境 blocker 和 Test Agent 后续动作。 |
| ANOS-160-V1-AC-008 | P1 | 大文件增长被拦截 | Development worker 向超阈值 Python 文件继续加逻辑 | 运行质量工具 | 超阈值或大幅增长被标记 fail/warn，并要求拆分或架构说明。 |

## V2 Agent 成长闭环验收候选

| ID | 优先级 | 需求 | 前置条件 | 验收方式 | 预期结果 |
| --- | --- | --- | --- | --- | --- |
| ANOS-160-V2-AC-001 | P0 | 失败和纠偏生成改进候选 | 任务被拒绝、重复返工、人工纠偏或阻塞恢复 | 查看任务事实和改进记录 | 事件关联 taskId、role、worker output、PM 收敛结论和证据。 |
| ANOS-160-V2-AC-002 | P0 | 可复用问题生成 AgentImprovementProposal | 改进候选被判断可复用 | 查看 AgentImprovementProposal | 提案包含问题归因、影响角色、建议修改、复用范围、风险和验证方式。 |
| ANOS-160-V2-AC-003 | P0 | 能力更新必须有 eval | skill / role spec / workflow 准备更新 | 查看 EvalCase 和验证结果 | 关键改进先有 eval，再更新能力资产；失败 eval 不推广。 |
| ANOS-160-V2-AC-004 | P1 | 下次调度使用升级能力 | 能力更新已通过验证并发布 | 执行同类任务 | PM 调度同类 worker 时能引用新版 skill / role spec / workflow。 |

## 不通过条件

1. 实现新增核心对象类型或新执行状态机。
2. 实现直接写 ProjectTask、TaskResult、Review、Audit、KnowledgeItem 或 Runner lease。
3. done 缺证据仍展示为完整闭环。
4. waiting_acceptance 看不到验收 owner、resultRef 或缺口。
5. 历史任务缺字段导致页面崩溃、空白或误显示完整。
6. 视图暴露 secret、token、密码或未授权材料正文。
7. worker 输出没有 PM 收敛就被当成最终任务结论。
8. 失败、返工或人工纠偏只停留在对话里，没有进入任务事实或改进候选。

## 分阶段交付关系

1. V0：只读任务事实视图，包含 worker trace 和 learning signal 的显示口径。
2. V1：PM Agent 调度子 Agent worker 的契约、记录和收敛。
3. V2：AgentImprovementProposal、EvalCase、skill / role spec / workflow 更新和发布。
4. 后续：正式独立 Agent 在上述闭环稳定后逐步替代成熟 worker 角色。
