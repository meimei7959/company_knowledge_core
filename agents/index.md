# Agents Index

Agents represent local or hosted AI workers registered to the knowledge core.

Each Agent file must be OKF-compatible and include:

- `type: Agent`
- `agentId`
- `owner`
- `aiTool`
- `allowedProjects`
- `allowedTools`
- `allowedKnowledgeScopes`
- `status`

- [Codex Local Builder](agent.codex.local.md)
- [Antigravity Local Builder](agent.antigravity.local.md)

Project creation generates project-scoped Agents such as `agent.<project>.project-manager`, `agent.<project>.product-manager`, `agent.<project>.knowledge-engineering`, and `agent.<project>.executor`. The project manager Agent owns project initialization closure for that project. The product manager Agent owns product discovery, requirement clarification, PRD, and acceptance criteria.

## Core Maintenance Agent And Sub-Agent Roles

Knowledge Engineering Agent is the umbrella owner. The linked steward, review, and ops files define internal sub-agent roles used by that workflow.

- [Company Knowledge Core Knowledge Engineering Agent](agent.company-knowledge-core.knowledge-engineering.md)
- [Knowledge Engineering Agent steward sub-agent](core/agent.knowledge-steward.md)
- [Knowledge Engineering Agent review sub-agent](core/agent.knowledge-review.md)
- [Knowledge Engineering Agent ops sub-agent](core/agent.knowledge-ops.md)
- [公司项目经理 Agent](agent.company.project-manager.md)
- [查知识 Agent](agent.company.knowledge-query.md)
- [产品经理 Agent](agent.company.product-manager.md)
- [设计 Agent](agent.company.design.md)
- [研发 Agent](agent.company.development.md)
- [测试 Agent](agent.company.test.md)
- [运营 Agent](agent.company.operations.md)
- [PicPeek 项目经理 Agent](agent.picpeek.project-manager.md)
- [PicPeek 知识工程 Agent](agent.picpeek.knowledge-engineering.md)
- [PicPeek 执行 Agent](agent.picpeek.executor.md)
- [PicPeek 产品经理 Agent](agent.picpeek.product-manager.md)
- [蜡笔投屏 项目经理 Agent](agent.labi-touping.project-manager.md)
- [蜡笔投屏 知识工程 Agent](agent.labi-touping.knowledge-engineering.md)
- [蜡笔投屏 执行 Agent](agent.labi-touping.executor.md)
- [蜡笔投屏 产品经理 Agent](agent.labi-touping.product-manager.md)
- [统一付费轻服务 项目经理 Agent](agent.billing-lite.project-manager.md)
- [统一付费轻服务 知识工程 Agent](agent.billing-lite.knowledge-engineering.md)
- [统一付费轻服务 执行 Agent](agent.billing-lite.executor.md)
- [统一付费轻服务 产品经理 Agent](agent.billing-lite.product-manager.md)
