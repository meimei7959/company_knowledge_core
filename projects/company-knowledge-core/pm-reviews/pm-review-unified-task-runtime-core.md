---
type: ProjectManagerReview
title: 统一任务运行内核 PM 分诊
timestamp: "2026-06-21T00:00:00Z"
projectId: company-knowledge-core
taskId: unified-task-runtime-core
reviewerAgent: agent.company.project-manager
decision: assign_to_development
status: done
nextAgent: agent.company.development
humanAcceptanceRequired: false
humanAcceptanceReason: 这是内部运行内核改造；研发与测试通过后由项目经理 Agent 验收，涉及生产部署或高风险规则变更时再转人工验收。
---

## 分诊结论

这是一个工程运行内核任务，不是知识沉淀任务，也不是单个飞书入口修复。

任务目标是把现有散落的项目创建、知识沉淀、工程修复、验收、通知流程收敛到一个统一任务生命周期里，让任务状态成为下一步流转的驱动力。

## 负责岗位

- 主责：研发 Agent。
- 协作：项目经理 Agent、测试 Agent、知识工程 Agent。
- 验收：项目经理 Agent。
- 人类验收：默认不需要；只有生产部署、高风险策略变更、权限/安全/审批规则变化时需要。

## 研发输入

- 当前任务卡：`tasks/unified-task-runtime-core.md`。
- 当前策略：`docs/strategy/zhenzhi-ai-native-knowledge-system.md`。
- 当前 Agent 团队规则：`docs/agent-team/company-agent-team-operating-guide.md`。
- 当前通用规则：`docs/agent-team/common-agent-operating-rules.md`。
- 当前调度模型：`docs/scheduler/task-dispatch-model.md`。

## 必须解决的问题

1. 任务类型分诊必须先于质量门判断，避免工程任务被知识沉淀质量门误杀。
2. TaskResult 必须有统一交付契约，避免每个流程自由拼结果。
3. 状态流转必须能驱动通知、验收、重试和交接。
4. 项目经理 Agent 必须能基于状态和结果决定是否进入下一节点。
5. 不能靠新增更多独立流程解决问题；实现要收敛已有流程。

## 验收标准

- 至少覆盖工程修复、知识沉淀、项目初始化三类任务。
- 任务创建后可以生成正确的负责 Agent、质量门、验收路径和通知策略。
- 工程任务不要求 KnowledgeItem draft。
- 知识沉淀任务必须要求 SourceMaterial、KnowledgeItem draft 和 Review 路径。
- 任务结果缺少证据、测试、自检或 terminal/handoff reason 时不能进入 done。
- 通知发送成功和失败都必须可追踪。
- 测试通过，且 `python3 -m zhenzhi_knowledge.cli validate` 通过。

## 下一步

交给研发 Agent 实现统一任务运行内核的最小可运行版本。
