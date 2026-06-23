---
type: Workflow
title: 阶段二同事接入多设备闭环测试报告
timestamp: "2026-06-22T13:18:45Z"
projectId: company-knowledge-core
taskId: kt-v2-colleague-runner-test
executorAgent: agent.company.test
status: changes_requested
resultRef: task-results/tr-kt-v2-colleague-runner-test.md
evidenceRef: projects/company-knowledge-core/test-reports/artifacts/phase2-colleague-runner-test-evidence.20260622T131845Z.jsonl
followupTaskRef: projects/company-knowledge-core/tasks/kt-v2-colleague-runner-development-fix-visible-path.md
---

# 阶段二同事接入多设备闭环测试报告

## Conclusion

测试未通过，需交回 `agent.company.development` 返修。

核心闭环能力通过自动验证：validator、targeted unittest、全量 unittest、项目 validate、模拟双 Runner 证据、git diff whitespace check 均通过。

阻断缺陷：主界面渲染后的 `runtime-monitor` 可见文本包含本机绝对路径 `/Users/meimei/Documents/company_knowledge_core`。这违反任务要求“主界面不得出现文件路径等内部字段”。

## Evidence

- 渲染 DOM 扫描：`agent-ring-console` 可读中文内容完整，未发现 `runtimeMetrics`、`sessionId`、`runnerId`、`deviceId`、`capabilityCode`、`scopeCode`、raw status、项目内路径或本机绝对路径。
- 渲染 DOM 扫描：`runtime-monitor` 发现文件路径泄露 `/Users/meimei/Documents/company_knowledge_core`。
- 源头定位：
  - `projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js:738` 把 `device.workspace` 渲染为可见 meta。
  - `projects/company-knowledge-core/desktop-workbench-slice0/workbench-live-read-model.js:861` 存在本机绝对路径 `workspace`。
  - `projects/company-knowledge-core/desktop-workbench-slice0/workbench-live-read-model.js` 多处 `repositoryRefs` / `repositoryScopes` 含同一本机绝对路径。
- 模拟证据：`projects/company-knowledge-core/test-reports/artifacts/phase2-colleague-runner-test-evidence.20260622T131845Z.jsonl`
  - events: 18
  - runners: `runner.phase2.local-dev-a`, `runner.phase2.local-test-b`
  - hosts: `host-a`, `host-b`
  - task_finish result refs: `task-results/simulated-dev-a.md`, `task-results/simulated-test-b.md`

## Commands

- `python3 scripts/validate_desktop_workbench_slice0.py` -> passed, `desktop workbench slice0 artifacts: passed`
- `python3 -m unittest tests.test_desktop_workbench_slice0 tests.test_distributed_runner_proof_harness` -> passed, 13 tests
- `python3 scripts/distributed_runner_proof_harness.py --evidence-file projects/company-knowledge-core/test-reports/artifacts/phase2-colleague-runner-test-evidence.20260622T131845Z.jsonl simulate-phase2` -> passed
- `python3 scripts/distributed_runner_proof_harness.py verify --evidence projects/company-knowledge-core/test-reports/artifacts/phase2-colleague-runner-test-evidence.20260622T131845Z.jsonl` -> passed, 18 events / 2 runners / 2 hosts
- `boost python3 -m unittest discover -s tests` -> passed, 213 tests, 1 skipped
- `python3 -m zhenzhi_knowledge.cli validate` -> passed, `valid`
- `git diff --check` -> passed

## User-Readable Coverage

- 当前项目、同事接入状态、任务路由去向、卡住原因、下一步操作：`agent-ring-console` 渲染文本覆盖。
- 设备/执行器列表、配对授权、任务路由、只读降级、异常恢复、审计摘要：`agent-ring-console` 渲染文本覆盖。
- 技术详情脱敏：协作设备页未暴露内部 ID；运行监控页仍暴露本机文件路径，需返修。

## Defect

`DEV-FIX-20260622-phase2-visible-path`

主界面运行监控页展示本机绝对路径。应把 workspace/repository path/repository scope 从主界面可见 meta 中移除，或只显示脱敏标签，例如“当前项目仓库”“已授权仓库范围”，并补充 DOM 可见文本测试覆盖 `/Users/`、项目内路径、`repositoryRefs`、`repositoryScopes`、`workspace` 原始值。

## Remaining Risk

真实双 host 风险仍未关闭。本地 `simulate-phase2` + `verify` 只能证明证据契约、2 runners、2 hosts、任务写回引用和异常路径模拟，不等同于真实同事电脑、真实网络、真实权限、真实 Agent Ring 执行验收。除非产品/PM明确接受替代证据，否则最终阶段二仍需真实双 host 验收。
