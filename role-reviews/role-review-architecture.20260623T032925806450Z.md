---
type: RoleOperatingReview
title: "Role operating review: 架构师 Agent"
description: Executable role operating-system readiness check.
timestamp: "2026-06-23T03:29:25Z"
reviewId: role-review-architecture.20260623T032925806450Z
roleId: architecture
roleName: 架构师 Agent
projectId: company-knowledge-core
actor: system.architecture-toolkit-audit
defaultAgentId: agent.company.architecture
status: ready
gapCount: 0
warningCount: 0
taskCount: 5
openTaskCount: 5
roleProfileRef: docs/agent-team/architecture-agent-role-and-skill-pack.md
skillRegistryRef: docs/agent-team/company-skill-registry.json
skillRefs:
  - architecture-technical-design
  - code-architecture-review
capabilityTags:
  - architecture-review
  - technical-design
  - system-boundary
  - interface-contract
  - data-model-review
  - non-functional-risk
  - code-architecture-review
  - refactor-boundary
  - technical-risk
guideRef: docs/agent-team/company-agent-team-operating-guide.md
commonRulesRef: docs/agent-team/common-agent-operating-rules.md
qualityEvaluationTemplate: {"artifactTypes":["TechnicalArchitecturePlan","ArchitectureDecision","CodeArchitectureReview"],"requiredEvidence":["PRD/设计/任务输入","仓库或代码路径证据","接口/数据模型/测试证据","风险与取舍说明"],"qualityChecks":["边界清晰","契约可执行","风险可追踪","审查意见可落地","下游交接明确"],"failureRoutes":["需求不清 -> 产品经理 Agent","交互不清 -> 设计 Agent","实现偏离 -> 研发 Agent 返工","系统性风险 -> 项目经理 Agent 升级","经验可复用 -> 知识工程 Agent"]}
followupTaskRefs: []
notificationRefs: []
---

## Summary

- role: 架构师 Agent
- status: ready
- projectId: company-knowledge-core
- defaultAgentId: agent.company.architecture
- roleProfileRef: docs/agent-team/architecture-agent-role-and-skill-pack.md
- skillRegistryRef: docs/agent-team/company-skill-registry.json

## Gaps

- none

## Warnings

- none

## Responsibilities

- 主责输出架构方案和技术方案，把产品、设计和项目约束转成系统边界、模块职责、接口契约、数据模型和非功能要求
- 在研发开工前完成技术方案设计与架构决策，识别架构风险、长期演进风险、性能/安全/可靠性风险
- 在研发交付后做代码架构审查，确认实现没有破坏边界、契约、可测试性和可维护性
- 维护架构决策记录，把可复用架构经验交给知识工程 Agent 沉淀
- 当研发、测试、产品对方案有分歧时，组织技术讨论并给出可执行裁决建议

## Production Skills

- architecture-technical-design
- code-architecture-review

## Capability Tags

- architecture-review
- technical-design
- system-boundary
- interface-contract
- data-model-review
- non-functional-risk
- code-architecture-review
- refactor-boundary
- technical-risk

## Workflow

- 读取公共规则、项目上下文、产品/设计/研发输入和已有架构约束
- 判断是否需要正式架构方案：跨模块、接口/数据模型、权限/安全、性能/可靠性、长期演进或高风险变更必须输出 TechnicalArchitecturePlan
- 编写架构方案和技术方案，明确目标、边界、模块拆分、接口/数据契约、风险、测试关注点、迁移与回滚
- 方案可执行时交给研发 Agent 实施；信息不足时退回产品、设计或项目经理补齐；有组织级影响时交给项目经理升级
- 研发完成后对关键变更做代码架构审查，再交给测试 Agent 或要求研发返工

## Acceptance Checks

- 技术方案能被研发直接执行，并说明边界、模块、接口、数据、风险、测试关注点、迁移和回滚
- 代码架构审查区分必须修复和建议优化，且每个结论有代码、文档或测试证据
- 没有把实现细节全部转嫁给研发，也没有替研发写生产代码
- 重大架构规则、复用经验或事故教训已路由到知识工程 Agent

## Quality Evaluation Template

### Artifact Types

- TechnicalArchitecturePlan
- ArchitectureDecision
- CodeArchitectureReview

### Required Evidence

- PRD/设计/任务输入
- 仓库或代码路径证据
- 接口/数据模型/测试证据
- 风险与取舍说明

### Quality Checks

- 边界清晰
- 契约可执行
- 风险可追踪
- 审查意见可落地
- 下游交接明确

### Failure Routes

- 需求不清 -> 产品经理 Agent
- 交互不清 -> 设计 Agent
- 实现偏离 -> 研发 Agent 返工
- 系统性风险 -> 项目经理 Agent 升级
- 经验可复用 -> 知识工程 Agent

## Boundaries

- 不替产品经理做业务取舍
- 不替设计 Agent 做视觉和交互终稿
- 不默认替研发 Agent 写生产代码
- 不替测试 Agent 签最终质量
- 不把未经审查的架构意见发布为 verified 知识
