---
type: TaskResult
title: Result for agent-runtime-rules-layering
description: Result of task agent-runtime-rules-layering.
timestamp: "2026-06-21T02:50:38Z"
resultId: TR-agent-runtime-rules-layering
taskId: agent-runtime-rules-layering
projectId: company-knowledge-core
assignee: agent.company.development
taskRuntime: {"version":"task-runtime.v1","taskType":"engineering_action","category":"engineering","qualityGate":"engineering","acceptancePath":"pm_review","requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
runnerId: ""
executorAgent: ""
status: done
summary: 已落地分层 Agent 行为规范：公司宪法、任务运行契约、人类验收策略、公共制度索引；task pull/start 会注入规则引用，TaskResult 会记录 operatingRuleRefs 并纳入 commonRulesEvaluation；同时修复 macOS 大小写不敏感导致不存在项目规则文件被误引用的问题。
outputRefs:
  - zhenzhi_knowledge/core.py
  - templates/task-result.md
  - AGENTS.md
  - docs/agent-team/company-agent-constitution.md
  - docs/agent-team/agent-task-runtime-contract.md
  - docs/agent-team/human-acceptance-policy.md
  - docs/agent-team/common-agent-operating-rules.md
  - docs/schemas/core-objects.md
knowledgeRefs: []
sourceMaterialRefs:
  - docs/agent-team/common-agent-operating-rules.md
evidenceRefs:
  - tests/test_cli.py
testsOrChecks:
  - python3 -m unittest tests.test_cli (133 tests OK)
  - python3 -m zhenzhi_knowledge.cli validate (valid)
nextActions: []
operatingRuleRefs: {"companyConstitution":"docs/agent-team/company-agent-constitution.md","taskRuntimeContract":"docs/agent-team/agent-task-runtime-contract.md","humanAcceptancePolicy":"docs/agent-team/human-acceptance-policy.md","commonRules":"docs/agent-team/common-agent-operating-rules.md","agentTeamGuide":"docs/agent-team/company-agent-team-operating-guide.md","roleOperatingSpec":"docs/agent-team/role-operating-specs.json","roleRules":"agents/agent.company.development.md","projectRules":"projects/company-knowledge-core/project.md"}
handoffContract: {"fromAgent":"agent.company.development","handoffTo":"agent.company.project-manager","handoffSummary":"请项目经理 Agent 复核分层规则是否足够短、是否已落到任务上下文、TaskResult 门禁和大小写精确路径检查。","requiredArtifacts":["technical plan","change summary","self-test result","risk notes"],"artifactRefs":["zhenzhi_knowledge/core.py","templates/task-result.md","AGENTS.md","docs/agent-team/company-agent-constitution.md","docs/agent-team/agent-task-runtime-contract.md","docs/agent-team/human-acceptance-policy.md","docs/agent-team/common-agent-operating-rules.md","docs/schemas/core-objects.md","tests/test_cli.py"],"openRisks":[],"nextSuggestedTask":"","terminalReason":""}
commonRulesEvaluation: {"version":"common-agent-rules.v1","status":"passed","passed":true,"rulesRef":"docs/agent-team/common-agent-operating-rules.md","guideRef":"docs/agent-team/company-agent-team-operating-guide.md","checkedRules":["summary","operating_rule_refs","evidence_or_artifacts","quality_evaluation","handoff_or_terminal_reason","engineering_tests_or_checks"],"reasons":[],"ruleIssueRequired":false}
qualityEvaluation: {"type":"AgentResultEvaluation","status":"passed","passed":true,"decision":"handoff_ready","score":95,"attemptNumber":1,"maxAttempts":3,"retryable":false,"reasons":[],"nextOwnerAgent":"agent.company.project-manager"}
acceptancePolicy: {"version":"acceptance.v1","acceptanceStatus":"waiting_acceptance","humanAcceptanceRequired":true,"acceptanceRequiredByDefault":true,"projectManager":"agent.company.project-manager","humanReviewer":"meimei","decidedBy":"","decisionReason":"default policy requires project manager notification and human acceptance before next role task","acceptedBy":"","acceptedAt":"","rejectedBy":"","rejectedAt":"","requiresNextTaskCreation":true}
improvementRefs: []
evalCaseRefs: []
followupTaskRefs: []
guideUpdateRequired: false
guideUpdated: false
guideRef: ""
guideFeishuUrl: ""
guideRevision: ""
guideAuditRefs: []
completedAt: "2026-06-21T02:50:38Z"
---

## Summary

已落地分层 Agent 行为规范：公司宪法、任务运行契约、人类验收策略、公共制度索引；task pull/start 会注入规则引用，TaskResult 会记录 operatingRuleRefs 并纳入 commonRulesEvaluation；同时修复 macOS 大小写不敏感导致不存在项目规则文件被误引用的问题。

## Evidence

- tests/test_cli.py

## Outputs

- zhenzhi_knowledge/core.py
- templates/task-result.md
- AGENTS.md
- docs/agent-team/company-agent-constitution.md
- docs/agent-team/agent-task-runtime-contract.md
- docs/agent-team/human-acceptance-policy.md
- docs/agent-team/common-agent-operating-rules.md
- docs/schemas/core-objects.md

## Next Actions

- none

## Handoff

- fromAgent: agent.company.development
- handoffTo: agent.company.project-manager
- summary: 请项目经理 Agent 复核分层规则是否足够短、是否已落到任务上下文、TaskResult 门禁和大小写精确路径检查。
- nextSuggestedTask: none
- terminalReason: none
- artifactRefs:
  - zhenzhi_knowledge/core.py
  - templates/task-result.md
  - AGENTS.md
  - docs/agent-team/company-agent-constitution.md
  - docs/agent-team/agent-task-runtime-contract.md
  - docs/agent-team/human-acceptance-policy.md
  - docs/agent-team/common-agent-operating-rules.md
  - docs/schemas/core-objects.md
  - tests/test_cli.py
- openRisks:
  - none

## Quality Evaluation

- status: passed
- decision: handoff_ready
- score: 95
- attempt: 1/3
- reasons: none

## Common Operating Rules

- status: passed
- rulesRef: docs/agent-team/common-agent-operating-rules.md
- guideRef: docs/agent-team/company-agent-team-operating-guide.md
- reasons: none
- operatingRuleRefs:
  - companyConstitution: docs/agent-team/company-agent-constitution.md
  - taskRuntimeContract: docs/agent-team/agent-task-runtime-contract.md
  - humanAcceptancePolicy: docs/agent-team/human-acceptance-policy.md
  - commonRules: docs/agent-team/common-agent-operating-rules.md
  - agentTeamGuide: docs/agent-team/company-agent-team-operating-guide.md
  - roleOperatingSpec: docs/agent-team/role-operating-specs.json
  - roleRules: agents/agent.company.development.md
  - projectRules: projects/company-knowledge-core/project.md

## Acceptance

- status: waiting_acceptance
- humanAcceptanceRequired: True
- projectManager: agent.company.project-manager
- humanReviewer: meimei
- reason: none

## Agent Improvement

- improvementRefs: none
- evalCaseRefs: none

## Tests Or Checks

- python3 -m unittest tests.test_cli (133 tests OK)
- python3 -m zhenzhi_knowledge.cli validate (valid)

## Agent Team Guide Gate

- guideUpdateRequired: False
- guideUpdated: False
- guideRef: none
- guideFeishuUrl: none
- guideRevision: none
- guideAuditRefs: none
