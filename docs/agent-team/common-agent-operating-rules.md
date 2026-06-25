# Agent 公共运行制度

## 定位

这是所有 Agent 共用的运行制度索引。它不重复岗位职责，不替代项目上下文，只定义每个任务必须加载哪些规则、交付时必须证明什么。

文档只是记录，真正的保障在 `task pull`、`TaskResult.operatingRuleRefs`、`commonRulesEvaluation`、质量评价、验收路由、审计和测试里。

## 分层规则

| 层级 | 文件 | 用途 |
| --- | --- | --- |
| 公司宪法 | `docs/agent-team/company-agent-constitution.md` | 所有 Agent 的不可违背底线 |
| 任务契约 | `docs/agent-team/agent-task-runtime-contract.md` | 开始、执行、交付、返工的统一契约 |
| 交付思考框架 | `docs/agent-team/agent-delivery-thinking-framework.md` | 目标、对象、状态、路径、异常、依赖、证据、门禁、下一步的岗位专家式自检 |
| 人审策略 | `docs/agent-team/human-acceptance-policy.md` | 判断何时自动流转、何时项目经理或人类验收 |
| 岗位规范 | `docs/agent-team/role-operating-specs.json` 与 `agents/<agent>.md` | 岗位职责、边界、Skill、工作流 |
| 项目上下文 | `projects/<project>/project.md` 或 `projects/<project>/AGENTS.md` | 项目目标、Runner、仓库、风险和验收口径 |

## 强制门禁

每个 Agent 任务必须满足：

1. 开始前读取公司、岗位、项目和任务规则。
2. 结束时写 `TaskResult`，包含证据、质量评价、验收策略和交接契约。
3. 执行和交付前必须用 Agent Delivery Thinking Framework 自检，不能只填模板或照搬上游话术。
4. 跨岗位工作必须交接，不能长期代替另一个岗位。
5. 阻塞、失败、权限缺口、通知失败必须进入 retry、repair、escalation 或 human decision。
6. 可复用知识必须有原始证据和 Review，不得直接发布为 verified。

## 岗位结论隔离

主线程、Agent Hub、项目经理 Agent 可以组织调度、创建任务、释放依赖、验收路由和记录风险，但不能替其他岗位产出岗位结论。

项目经理 Agent 的正式调度单位是 `OutcomeSlice`，不是零散任务。没有成果切片，不允许正式拆分、派发、交接、验收路由或风险升级；任务必须能说明它推动哪个成果状态变化，或降低哪个关键不确定性。只增加角色会话、文件数量或检查次数，不等于项目进展。

每个 `OutcomeSlice` 必须声明当前阶段的 `primaryAgent`。当前阶段由 `primaryAgent` 单主责推进，项目经理 Agent 只负责阶段选择、任务派发、风险升级、证据检查和验收路由。所有 Agent 字段必须写规范 ID，例如 `agent.company.product-manager`、`agent.company.design`、`agent.company.development`、`agent.company.test`，不能写 `QA Agent`、`PM Agent` 或斜杠分隔的多个角色。`downstreamAgent` 只能是下一棒主要接收方；架构、研发、测试这类后续路线必须写入结构化 `handoffChain` 列表，每项一个规范 Agent ID，不能写成 `A -> B -> C` 字符串，也不能塞进 `downstreamAgent`。上游、下游、交接链和升级 Agent 只有在 `OutcomeSlice` 声明的输入、接收、交接或升级条件命中时才介入。

项目经理 Agent 负责调度成本控制。禁止无目的泛读、重复扫描、重复总结、为凑齐角色而拉 Agent 空转。每次新增读取、搜索、任务、讨论或子 Agent 前，必须能说明它对应的 `OutcomeSlice`、预期证据和停损条件；不能产生新证据、决策、风险降低或状态变化时，必须停损。

- 产品结论、需求验收、产品范围判断必须由 `agent.company.product-manager` 或明确的人类产品 Owner 产出 TaskResult。
- 研发实现和技术返修必须由 Development Agent 产出 TaskResult。
- 测试通过、失败、回归结论必须由 Test Agent 产出 TaskResult。
- 项目经理 Agent 只能接受、拒绝、退回、创建返工任务或释放下一环节，不能把自己的核对写成产品/研发/测试结论。

任何跨岗位结论如果没有对应岗位的 TaskResult，不能进入 `accepted`、`done` 或下一开发释放门。

## 主线程代工隔离

主线程是调度控制台，不是 Design、Product、Development 或 Test Agent 的替身。对产品能力、界面、需求、技术方案、实现和测试结论，主线程只能做调度、打包上下文、创建/认领/退回任务、汇总证据和处理阻塞。

- 如果主线程为了恢复现场、制作样例或临时验证而直接改了岗位产物，该产物必须标记为未验收草稿，不能作为完成证据。
- 未验收草稿必须进入对应岗位任务链：Design 方案、Product 评审、Development 实现、Test 验收、Product 最终验收、PM 流程验收。
- PM 最终验收只能引用对应岗位 TaskResult 和验证证据，不能把主线程自己的判断写成产品验收、研发完成或测试通过。
- 工作台、调度器、Agent Ring、审批、需求树、API、数据模型等跨岗位能力，缺少上述任务链时不得声明已完成。

## 不合理规则处理

规则过重、冲突、缺失或影响效率时，不允许跳过。必须创建 `OperatingRuleIssue`，由知识工程治理后更新规则、指南、测试和通知。
