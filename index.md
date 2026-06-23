# Company Knowledge Core Index

This repository is the OKF-compatible central processor bundle for Zhenzhi's AI-native team.

Agent Hub, Scheduler, and external Agent Ring runners access this bundle through the central protocol/API/CLI. Formal Agent work must produce AgentRun records. Assigned project or knowledge work must produce ProjectTask/KnowledgeTask and TaskResult records. ToolAsset updates and reviewed status changes must write AuditLog entries.

## Main Strategy

- [桢知科技 AI 原生知识工程建设方案](docs/strategy/zhenzhi-ai-native-knowledge-system.md)
- [Architecture Index](docs/architecture/index.md)
- [Product System Architecture](docs/architecture/product-system-architecture.md)
- [Engineering Extension Model](docs/architecture/engineering-extension-model.md)
- [DeepSeek Feishu Routing Plan](docs/agent-team/deepseek-feishu-routing-plan.md)
- [Agent Ring Stub Test Strategy](docs/harness/agent-ring-stub-test-strategy.md)
- [Access Credential Request Flow](docs/protocols/access-credential-request-flow.md)

## Knowledge Areas

- [Projects](projects/index.md)
- [Tasks](tasks/index.md)
- [Source Materials](sources/index.md)
- [Task Results](task-results/index.md)
- [Agent Runners](runners/index.md)
- [Agents](agents/index.md)
- [Tools](tools/index.md)
- [Knowledge](knowledge/index.md)
- [Runs](runs/index.md)
- [Agent Ring Protocol](docs/protocols/agent-ring-communication-protocol.md)
- [Project Context Sync Protocol](docs/protocols/project-context-sync-protocol.md)
- [Scheduler](docs/scheduler/index.md)
