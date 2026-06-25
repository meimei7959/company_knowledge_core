# Agent 任务运行契约

## 开始任务

Agent 开始任务前必须拿到：

- 任务目标和完成标准；
- 如果任务来自项目经理调度，必须拿到 `outcomeSliceRef`，并理解它的阶段目标、主交付物、当前状态、目标状态、证据和停止条件；
- 输入资料和证据入口；
- 公司宪法、公共制度、岗位规则、项目规则；
- Agent Delivery Thinking Framework，用于先形成岗位判断，再选择表达形式；
- 当前任务是否需要测试、知识草稿、项目经理复核或人类验收。

## 执行任务

执行中必须保持：

- 不越权调用工具；
- 不跨岗位长期代工；
- 不替其他岗位产出最终岗位结论；产品验收必须由产品经理 Agent，测试结论必须由测试 Agent，研发实现必须由研发 Agent 写入 TaskResult；
- 先按 Agent Delivery Thinking Framework 思考目标、对象、状态、路径、异常、依赖、证据、门禁和下一步；输出形式由 Agent 自主选择，但必须让下游能接住；
- 任务执行要服务于 `OutcomeSlice` 的状态变化或不确定性降低；如果发现任务无法推动成果，应写阻塞/返工/停止理由，而不是继续消耗。
- 执行前先做成本-价值检查：本次工具调用、文件读取、搜索或 Agent 调度将产生什么证据、决策、风险降低或状态变化；如果只是重复确认、泛读或补一份不会改变结论的总结，必须停止。
- 发现缺资料、缺权限、规则冲突时立刻记录阻塞原因；
- 重要决策写入任务结果或决策记录。
- 遇到上下文窗口或 token 预算达到上限、会话被压缩、子 Agent 暂停、工具等待恢复、或执行线程临时不可继续时，必须记录断点、当前任务、已完成证据、下一步动作和恢复条件；恢复后必须继续工作，不能把暂停当成完成、失败或无人接管。
- Agent 反馈入口必须区分工作状态 intake 和可复用能力草稿：`system-issue` 可在 `main` 写入 Defect 和 PM 分诊任务；`skill-gap` 必须基于 `--central-root` 所在 Git 仓库确认当前分支为 `feedback/*` 或 `codex/*`，否则在写入任何文件前失败。

## 中断和恢复

以下情况属于可恢复暂停，不属于任务终止：

- context/token 预算耗尽；
- 自动压缩或会话恢复；
- 子 Agent 等待调度恢复；
- 工具调用排队或等待授权回到主窗口；
- 本地执行线程短暂不可用。

恢复规则：

- Project Manager Agent 必须继续等待或重新调度，直到任务有 `TaskResult`、`blocked`、`changes_requested`、`rejected`、`done` 或明确人类取消。
- 执行 Agent 必须从最后一个可证据化断点继续，不得重新开始导致重复提交或漏掉已完成工作。
- 如果恢复后发现上下文丢失，必须先读取任务、TaskResult、AuditLog、NotificationRecord、AgentRun 或项目协调文档恢复状态，再继续。
- 如果同一任务连续三次因同一资源限制无法恢复，才允许标记 `blocked`，并必须写清恢复所需条件。

## 完成任务

交付必须写 `TaskResult`，至少包含：

- `summary`
- `outputRefs` / `knowledgeRefs` / `evidenceRefs`
- `testsOrChecks`
- `operatingRuleRefs`
- `commonRulesEvaluation`
- `qualityEvaluation`
- `acceptancePolicy`
- `handoffContract` 或 `terminalReason`
- 如果任务带 `outcomeSliceRef`，必须继承该字段，并在 summary、evidence 或 qualityEvaluation 中说明对成果切片的贡献、未贡献原因或停损建议。

其中 `commonRulesEvaluation` 或 `qualityEvaluation` 必须能看出 Agent 已自检 Agent Delivery Thinking Framework。自检可以是自然语言，不要求逐项填表。

缺少这些字段，任务不能算完成。

## 流转结果

任务完成后，`ProjectTask.status` 只能进入以下路由状态之一：

- `done`：已完成并关闭；如有下一步，必须写入 `followupTaskRefs`。
- `waiting_acceptance`：TaskResult 通过机器检查，等待项目经理或人类验收。
- `changes_requested`：质量不达标或需要修改，可重试。
- `blocked`：缺资料、缺权限或外部状态阻塞。
- `rejected`：不可恢复、不可执行或验收驳回。

`handoff_ready`、`retry_required`、`review_required` 等只能作为 `qualityEvaluation.decision` 或验收策略字段，不允许写入 `ProjectTask.status`。
