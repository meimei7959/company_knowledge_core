---
type: TaskResult
title: Result for KT-ACCESS-CREDENTIAL-SECRET-FLOW
description: Result of task KT-ACCESS-CREDENTIAL-SECRET-FLOW.
timestamp: "2026-06-18T11:07:57Z"
resultId: TR-KT-ACCESS-CREDENTIAL-SECRET-FLOW
taskId: KT-ACCESS-CREDENTIAL-SECRET-FLOW
projectId: company-knowledge-core
assignee: zhenzhi-knowledge-core
runnerId: []
executorAgent: ""
status: done
summary: "已将旧 token 发放流程升级为 access credential request：Feishu 私聊会创建 AccessCredentialRequest，按 central_api/runner_registration/local_tool/model_api/project_service 分类；审批通过和自动批准只返回 secretRef 与配置说明，不再发送真实 token/key；secret 扫描器允许 secretref:// 引用但继续拦截明文；Agent Ring claim 会检查 requiredSecretRefs，缺失则 blocked，ready 后可领取。"
outputRefs:
  - zhenzhi_knowledge/core.py
  - zhenzhi_knowledge/feishu.py
  - zhenzhi_knowledge/server.py
  - tests/test_cli.py
  - docs/protocols/access-credential-request-flow.md
knowledgeRefs: []
sourceMaterialRefs:
  - docs/protocols/access-credential-request-flow.md
  - docs/agent-team/deepseek-feishu-routing-plan.md
  - docs/harness/agent-ring-stub-test-strategy.md
evidenceRefs:
  - tests.test_cli.CliTests.test_feishu_private_credential_request_creates_secret_ref_record
  - tests.test_cli.CliTests.test_token_approval_sends_secret_ref_only_to_submitter_when_enabled
  - tests.test_cli.CliTests.test_agent_ring_http_task_lifecycle
testsOrChecks: []
nextActions:
  - 后续可把 Secret Manager 真实适配和凭证轮换策略拆入独立任务。
completedAt: "2026-06-18T11:07:57Z"
---

## Summary

已将旧 token 发放流程升级为 access credential request：Feishu 私聊会创建 AccessCredentialRequest，按 central_api/runner_registration/local_tool/model_api/project_service 分类；审批通过和自动批准只返回 secretRef 与配置说明，不再发送真实 token/key；secret 扫描器允许 secretref:// 引用但继续拦截明文；Agent Ring claim 会检查 requiredSecretRefs，缺失则 blocked，ready 后可领取。

## Evidence

- tests.test_cli.CliTests.test_feishu_private_credential_request_creates_secret_ref_record
- tests.test_cli.CliTests.test_token_approval_sends_secret_ref_only_to_submitter_when_enabled
- tests.test_cli.CliTests.test_agent_ring_http_task_lifecycle

## Outputs

- zhenzhi_knowledge/core.py
- zhenzhi_knowledge/feishu.py
- zhenzhi_knowledge/server.py
- tests/test_cli.py
- docs/protocols/access-credential-request-flow.md

## Next Actions

- 后续可把 Secret Manager 真实适配和凭证轮换策略拆入独立任务。

## Tests Or Checks

- none
