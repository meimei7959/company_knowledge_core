---
type: AuditLog
title: audit.20260619T144500Z
timestamp: 2026-06-19T14:45:00Z
auditId: audit.20260619T144500Z
actor: agent.company-knowledge-core.knowledge-engineering
action: agent_team.closed_loop_rules.updated
targetRef: docs/agent-team/company-agent-team-operating-guide.md
before: role flow documented but project intake, handoff contract, all-role evaluation, operations feedback, and state machine were not systematized
after: closed-loop rules documented and implemented
policyResult: guide_updated
---

## Details

用户要求把红队发现的缺口系统化补齐，避免过度设计，同时确保 Agent Team 能高效闭环运行。

本次更新：

- 增加立项评估 Gate：`ProjectIntake -> ProjectDraft -> ProjectLaunchChecklist -> project_initialization task`。
- 增加岗位交接 Contract：TaskResult 必须携带 handoff 字段、产物、风险、下一任务或终态原因。
- 增加全岗位质量评价：ProjectTask 和 KnowledgeTask 都生成 `qualityEvaluation`。
- 增加返工和升级机制：失败自动重试，阻塞或连续失败升级给项目经理 Agent。
- 增加运营反馈回流：`OperationsFeedback` 自动分类并创建后续任务。
- 增加调度器状态机：关闭状态不能倒退，继续工作必须创建新任务。
- 更新本地指南和知识库摘要。

## Verification

- `python3 -m unittest tests.test_cli` 通过，102 个测试 OK。

