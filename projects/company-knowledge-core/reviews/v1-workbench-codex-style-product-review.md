---
type: ReviewRecord
title: V1 工作台 Codex 风格设计产品评审
projectId: company-knowledge-core
taskId: kt-v1-workbench-codex-style-product-review
reviewAgent: agent.company.product-manager
decision: approved
status: submitted
createdAt: "2026-06-22"
sourceRefs:
  - projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-product-review.md
  - projects/company-knowledge-core/design/v1-workbench-codex-style-design.md
  - task-results/tr-kt-v1-workbench-codex-style-design.md
operatingRuleRefs:
  companyConstitution: docs/agent-team/company-agent-constitution.md
  commonRules: docs/agent-team/common-agent-operating-rules.md
  taskRuntimeContract: docs/agent-team/agent-task-runtime-contract.md
  humanAcceptancePolicy: docs/agent-team/human-acceptance-policy.md
  roleRules: agents/agent.company.product-manager.md
  projectRules: projects/company-knowledge-core/project.md
---

# V1 工作台 Codex 风格设计产品评审

## Decision

approved。

产品评审认为：当前设计已满足“在现有体系基础上整体升级，达成 V1 版本单机闭环”的研发放行条件。它覆盖本地工作台必须让项目 Owner、项目经理 Agent 和岗位 Agent 看懂的核心事实：设备、Runner、Agent 会话、任务流、TaskResult、审批/权限门、异常恢复和证据来源。

本结论只批准设计进入研发实现任务，不代表研发已完成，不代表测试已通过，也不替 PM 最终验收或人类验收下结论。

## Review Scope

- 评审对象：`projects/company-knowledge-core/design/v1-workbench-codex-style-design.md`。
- 设计 TaskResult：`task-results/tr-kt-v1-workbench-codex-style-design.md`。
- 评审任务：`projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-product-review.md`。
- 评审口径：不是逐条开发昨天 74 个功能需求，而是确认 V1 单机闭环的工作台设计是否可指导研发。

## Coverage Review

| 评审项 | 产品判断 | 说明 |
| --- | --- | --- |
| 单机设备路由 | pass | 运行监控页展示 `devices`、`agentSessions`、`agentMessages`，首页展示最近路由和目标设备，Runner 页展示能力、租约、心跳和范围审计。 |
| Agent 团队状态 | pass | Agent 页覆盖岗位 Agent、在线状态、所在设备、当前任务、最近证据和交接提示，并明确缺岗位 TaskResult 时不可由 PM 或主线程代签。 |
| 任务流转 | pass | 项目页、运行监控页和验收页都以 ProjectTask/TaskResult/交接为主线，能回答当前推进到哪里、下一步谁负责、证据是否完整。 |
| 权限/审批阻塞 | pass | 审批/权限页覆盖 `approvals`、`permissionGatedActions`、serverGate、auditRef 和安全设置，符合默认只读和授权优先原则。 |
| 异常恢复 | pass | 异常恢复页单独覆盖 stale lease、failed runner、offline heartbeat、cancelled/rejected/blocked、retry condition、通知异常和只读 fallback。 |
| 证据可追溯 | pass | 设计要求每张状态卡有证据入口，验收页展示 output/evidence/tests/rule refs 完整性提醒，详情抽屉保留完整引用。 |
| 中文 Codex 风格可读性 | pass | 文案以短句、状态、下一步、证据为中心；内部 ID 降为次级信息；`submitted`、`safe_fallback`、`offline` 等有中文映射建议。 |

## Product Requirements For Development

研发实现必须满足以下产品要求，作为后续研发任务的验收输入：

1. 真实状态来源必须是 Central API read model 或其本地只读缓存；不能用静态 mock 冒充运行事实。
2. 首页首屏必须优先显示未关闭任务、在线设备、在线 Agent、带目标设备的消息、产品/PM/测试验收证据。
3. `submitted` 必须显示为“已提交结果”，不得显示成“已验收”或“已完成验收”。
4. `offline` 必须按上下文解释：设备/Runner 为“离线”，任务上下文不得误导为执行失败。
5. 权限动作必须集中在审批/权限区域或固定操作区，不能混进普通状态列表造成误点。
6. 所有破坏性、权限、审批、外发、密钥相关动作默认只读，必须展示所需权限、server gate 和 auditRef。
7. 异常恢复必须汇总 stale、failed、offline、cancelled、rejected、blocked 和 safe fallback，不能只展示单条 recovery 数据。
8. 缺 outputRef、evidenceRef、testsOrChecks、operatingRuleRefs 或 commonRulesEvaluation 时，验收页必须显式提示“证据不完整”。
9. Agent 页必须显示岗位责任边界；缺岗位 TaskResult 时不得允许主线程、PM 或其他岗位代签结论。
10. Runner 页必须显示 capability、scope、lease、heartbeat、stale/failed 状态和最近审计证据。
11. read model 过期或缺失时，整页进入“安全只读”，保留最近可信证据，不允许状态变更。
12. 中文文案必须优先业务含义，再展示内部引用；内部 ID 只作为证据 chip、hover 或详情信息。

## Non-Blocking Notes

- 设计 TaskResult 的真实路径为 `task-results/tr-kt-v1-workbench-codex-style-design.md`，不是项目目录下的 `projects/company-knowledge-core/task-results/...`。后续证据引用应使用真实路径。
- 设计里的研发交接清单已足够作为首个研发实现任务输入；研发可按页面 surface 拆 slice，但必须先保证读模型、证据、只读降级和恢复路径可见。

## Release To Development

允许进入研发实现任务。

建议下一步由项目经理 Agent 创建或释放研发任务，范围限定为 V1 工作台 Codex 风格中文升级和单机闭环可视化，不扩展到 74 个功能需求逐条开发。
