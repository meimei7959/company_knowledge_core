# Central Processor And Agent Ring

## Positioning

This project is the central processor for Zhenzhi's AI-native operating system.

It combines:

- scheduler state;
- project and task orchestration;
- knowledge engineering;
- runner registry;
- protocol contracts;
- review, audit, and notification.

Agent Ring is external. It is the Agent workstation installed on each distributed computer.

The central processor does not define Agent Ring's full product scope. Agent Ring may own its own subscriptions, local Agent configuration, Codex / Claude / local model integration, Skill and tool management, UI, local security, and automation. This architecture only defines how Agent Ring connects to the central processor as a registered runner that can claim tasks, pull context, execute locally, and write back auditable results.

## Mental Model

```txt
Agent Hub = entrance
Central Processor = scheduler + knowledge core
Agent Ring = Agent workstation on each computer
Distributed Computers = execution processors
Codex / Claude / local models / tools = execution engines
```

The central processor decides what should happen and records what happened. Agent Ring makes a distributed computer able to do work. Its internal product design remains owned by the Agent Ring project; the central processor only depends on the integration contract.

## Project Portability

The same project should be able to move from one computer to another without losing context.

This is possible only if the central processor keeps structured project memory:

- current Project and Task state;
- SourceMaterial and evidence refs;
- TaskResult and AgentRun history;
- decisions, risks, conflicts, and open questions;
- required Agent, ToolAsset, repository, environment, and secret refs;
- handoff notes from previous runners.

Agent Ring should treat local state as cache. Before work, it pulls a project or task context bundle from the central processor. After work, it writes structured results back. If a runner stops or another computer takes over, the new runner pulls the latest context bundle and continues.

Protocol: [Project Context Sync Protocol](../protocols/project-context-sync-protocol.md).

## End-To-End Flow

```txt
User or Agent asks Agent Hub to start work
-> Agent Hub creates Project / SourceMaterial / ProjectTask / KnowledgeTask
-> Scheduler determines required capabilities
-> Scheduler selects an online Agent Ring runner
-> Runner claims task with lease
-> Runner pulls project/task context bundle
-> Runner launches local Agent and execution engine
-> Runner writes TaskResult, AgentRun, evidence, artifacts, knowledge drafts
-> Knowledge Review gates reusable knowledge
-> Agent Hub notifies requester or project channel
```

## What Belongs Here

- Project records.
- Task records and state transitions.
- Source material records.
- TaskResult and AgentRun records.
- Agent and ToolAsset registry.
- AgentRunner registry and capability claims.
- Scheduler decisions and leases.
- KnowledgeItem, ReviewRecord, ConflictRecord, AuditLog.
- Protocol docs and compatibility contracts.

## What Does Not Belong Here

- Agent Ring desktop/service implementation.
- Agent Ring product scope, subscription model, local Agent configuration, Skill/tool management, model integration, or UI.
- Local process supervision on distributed computers.
- Local Codex / Claude installation.
- Local model runtime.
- Raw long logs or binary artifacts.
- Secrets stored as values.
- Business-domain implementation code.

## Why This Split Matters

Without Agent Ring, tasks become records that wait for someone or something to manually pick them up.

Without the central processor, every computer becomes an isolated Agent island with no shared project state, no review, no audit, and no reusable knowledge.

Together:

```txt
Central Processor gives direction, memory, policy, and state.
Agent Ring gives distributed execution.
```
