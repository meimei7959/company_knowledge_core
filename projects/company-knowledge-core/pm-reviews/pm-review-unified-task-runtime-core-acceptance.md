---
type: ProjectManagerReview
title: 统一任务运行内核 PM 验收
timestamp: "2026-06-21T00:00:00Z"
projectId: company-knowledge-core
taskId: unified-task-runtime-core
resultRef: task-results/tr-unified-task-runtime-core.md
reviewerAgent: agent.company.project-manager
decision: ready_for_human_acceptance
status: done
humanAcceptanceRequired: true
---

## 验收结论

项目经理 Agent 复核通过，建议进入人类验收。

这次交付不是继续叠加流程，而是把任务运行收敛到统一 runtime profile：

- 任务创建时写入 `taskRuntime`。
- 任务类型决定默认负责 Agent、质量门、验收路径和必要交付物。
- 工程任务不再被知识沉淀质量门要求 KnowledgeItem draft。
- 知识任务仍要求 SourceMaterial、KnowledgeItem draft 和 Review。
- 工程类任务必须有测试或检查。
- TaskResult 会记录 `taskRuntime`，供项目经理 Agent、通知、验收和后续 Agent 读取。

## 证据

- 代码：`zhenzhi_knowledge/core.py`
- 测试：`tests/test_cli.py`
- 指南：`docs/agent-team/company-agent-team-operating-guide.md`
- 公共制度：`docs/agent-team/common-agent-operating-rules.md`
- 调度模型：`docs/scheduler/task-dispatch-model.md`
- 任务结果：`task-results/tr-unified-task-runtime-core.md`

## 测试

- `python3 -m unittest tests.test_cli`
- `python3 -m zhenzhi_knowledge.cli validate`

## 风险

- 这是公共运行内核变更，影响任务创建和结果评价，因此保留人类验收门。
- 当前尚未部署到线上飞书机器人；部署前建议再跑一次灰度项目创建和知识记录。

## 下一步

人类 Owner 确认后，可以部署，并用飞书创建灰度项目与记录知识入口各跑一次线上验证。
