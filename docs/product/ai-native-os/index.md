# AI Native OS Product Package

This package defines the complete launch product for Zhenzhi AI Native OS.

It is not an MVP plan and does not split scope into P0/P1. It defines the complete product that must be delivered for formal launch.

## Documents

- [Complete Launch PRD](prd.md)
- [Requirement Tree](requirement-tree.md)
- [Functional Requirements](requirements.md)
- [Product Architecture From Agent Mode Docs](product-architecture-from-agent-mode-docs.md)
- [Agent Collaboration Contract](agent-collaboration-contract.md)
- [Development Handoff](development-handoff.md)
- [Test Cases](test-cases.md)
- [Acceptance Checklist](acceptance-checklist.md)
- [ANOS-REQ-160 Task Execution Productization PRD](task-execution-productization-prd.md)
- [ANOS-REQ-160 V0 Acceptance Matrix](task-execution-productization-acceptance-matrix.md)
- [ANOS-REQ-161 Execution Telemetry Retention PRD](execution-telemetry-retention-prd.md)
- [ANOS-REQ-161 Acceptance Matrix](execution-telemetry-retention-acceptance-matrix.md)

## Product Goal

Zhenzhi AI Native OS is the operating system for an AI-native organization.

It connects:

```txt
human request
-> requirement clarification
-> product plan
-> project and task orchestration
-> Agent team collaboration
-> distributed Agent Ring execution
-> result writeback
-> review and approval
-> reusable knowledge
-> metrics and operational improvement
```

## Non-Negotiable Launch Standard

Formal launch means the system supports complete daily operation:

- human users can submit, track, approve, and accept work;
- eight business Agents can collaborate with clear input/output contracts;
- governance Agents can review, audit, and protect quality;
- Agent Ring runners can claim, execute, heartbeat, and write back results;
- every durable output has source, owner, status, evidence, and audit trail;
- requirements, tasks, tests, and acceptance criteria are traceable.

## Current Foundation To Preserve

Do not rebuild the foundation unless a specific implementation defect proves it necessary.

Preserve:

- Project / ProjectTask / KnowledgeTask / TaskResult lifecycle.
- SourceMaterial-first intake.
- AgentRunner registry, capability matching, claim, lease, heartbeat, finish.
- Knowledge Review before reusable knowledge promotion.
- AuditLog and NotificationRecord.
- Feishu Agent Hub as a primary entry.
- Agent Ring as external execution layer.
- Git as code source of truth.
