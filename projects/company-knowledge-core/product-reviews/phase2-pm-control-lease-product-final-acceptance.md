---
type: ReviewRecord
title: Phase 2 PM 主控租约产品最终验收
projectId: company-knowledge-core
taskId: kt-v2-pm-control-lease-product-final-acceptance
reviewAgent: agent.company.product-manager
status: blocked
decision: accepted_for_local_scope_blocked_for_production_launch
businessConclusion: local_scope_accepted_production_blocked
createdAt: "2026-06-23T05:49:38Z"
sourceRefs:
  - docs/product/ai-native-os/phase-2-pm-control-lease-prd.md
  - projects/company-knowledge-core/technical-solutions/phase2-pm-control-lease-technical-solution.md
  - projects/company-knowledge-core/product-reviews/phase2-pm-control-lease-architecture-product-review.md
  - task-results/tr-kt-v2-pm-control-lease-development.md
  - projects/company-knowledge-core/test-reports/phase2-pm-control-lease-test-report.md
  - task-results/tr-kt-v2-pm-control-lease-test.md
  - zhenzhi_knowledge/core.py
  - zhenzhi_knowledge/server.py
  - zhenzhi_knowledge/cli.py
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-read-model.js
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-live-read-model.js
  - tests/test_cli.py
  - tests/test_desktop_workbench_slice0.py
outputForTask: kt-v2-pm-control-lease-product-final-acceptance
---

# Phase 2 PM 主控租约产品最终验收

## 结论

本地可验证产品范围通过。

该机制已经满足本期产品目标：同一项目同一时间只能一个主控项目经理 Agent 持有调度租约；协同项目经理和备用项目经理不能绕过主控直接写项目调度；无租约、过期租约、非主控、项目不匹配、旧租约代际写入会被中枢拒绝并留下审计；工作台能展示主控项目经理、协同/备用项目经理、租约健康和接管记录。

上线发布仍阻塞。

阻塞原因不是当前本地产品语义失败，而是缺少上线级证据：HTTP socket/API 路由需要在非沙箱或部署验收环境补跑；真实多电脑共享中枢、真实并发 PM 接管、真实心跳过期与接管链路还没有双机部署证据。没有这些证据前，不能把它声明为生产级多电脑防冲突闭环。

## 验收范围

本次验收覆盖：

- 产品需求：`phase-2-pm-control-lease-prd.md` 中的主控租约、协同/备用边界、写操作保护、拒绝审计、工作台展示、接管记录。
- 架构方案：`PMControlLease`、`ProjectPmParticipant`、`PmLeaseTakeoverRecord`、写前校验、拒绝语义、API/CLI/工作台读模型。
- 研发交付：core 守卫、租约生命周期、CLI/API 入口、工作台展示、测试覆盖。
- 测试证据：本地 core/CLI/workbench 回归、过期租约、备用无租约、项目不匹配、旧租约代际、审计存在、目标 task 不写入。

本次验收不替代：

- 非沙箱 HTTP socket/API 实跑验收。
- 真实两台电脑或两台 host 接入同一中枢后的并发 PM 调度冲突验收。
- 生产部署、权限、监控和运维接管演练。

## 产品需求对齐

| 产品要求 | 验收判断 | 证据 |
| --- | --- | --- |
| 同一项目同一时间只有一个主控 PM | 通过 | core 租约读模型、acquire/takeover 测试、工作台主控展示 |
| 协同 PM 只能查看或提交建议，不能写调度 | 通过 | `pm_control_lease_not_primary` 拒绝测试和审计展示 |
| 备用 PM 只能在失联/过期/确认接管后成为主控 | 通过 | takeover 逻辑、健康主控接管确认、接管记录 |
| 所有 PM 调度写操作必须带租约 | 通过 | `guard_pm_control_write` / protected write guard 及调度写测试 |
| 中枢拒绝无租约写入并审计 | 通过 | `pm_control_lease.denied` 审计、目标 task 不写入测试 |
| 工作台展示主控、协同、备用、租约健康、接管记录 | 通过 | `pmControl` read model、中文工作台 DOM 测试 |
| 真实多电脑共享中枢生产闭环 | 阻塞 | 仅有本地/模拟证据，缺真实双机并发部署证据 |
| HTTP/API 路由实跑 | 阻塞 | 测试报告明确 socket bind 在当前沙箱无法实跑 |

## 用户视角判断

用户能在工作台理解“现在谁是主控项目经理、哪些项目经理只能协同或备用、租约是否健康、发生过哪些接管、为什么某次写入被拒绝”。这满足用户要求的“不要多个项目经理 Agent 同时抢调度权、工作台能看到主控和接管状态”。

但用户还不能据此确认真实多电脑生产环境绝对安全，因为真实同事电脑/第二 host 尚未接入同一共享中枢做并发验证。产品验收不把本地模拟证据等同为生产证据。

## 返工判断

不创建研发返工任务。

当前证据没有显示本地产品范围缺失；测试 Agent 已接受本地可验证范围。需要创建的是上线前补验任务，而不是研发返工任务：

- 非沙箱 HTTP/API PM 主控租约路由验收。
- 真实多电脑共享中枢 PM 主控租约并发验收。
- 工作台连接真实中枢后的主控、协同、备用、租约健康、接管记录展示复验。

## 最终判定

产品经理 Agent 接受本地可验证范围。

产品经理 Agent 不接受上线发布完成声明。上线前必须补齐真实 HTTP/API 与真实多电脑共享中枢并发证据。
