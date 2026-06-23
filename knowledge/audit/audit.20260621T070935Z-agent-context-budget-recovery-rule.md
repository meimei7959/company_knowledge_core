---
type: AuditLog
title: audit.20260621T070935Z-agent-context-budget-recovery-rule
timestamp: "2026-06-21T07:09:35Z"
auditId: audit.20260621T070935Z-agent-context-budget-recovery-rule
actor: agent.company.project-manager
action: agent.iron-rule.context-budget-recovery.created
targetRef: docs/agent-team/company-agent-constitution.md
projectId: company-knowledge-core
policyResult: "human owner requested iron rule; context budget exhaustion is recoverable pause and must not stop agent delivery"
---
# Agent Context Budget Recovery Rule Created

## Summary

Human owner instructed that when development reaches token or context limits, Agent work must wait for recovery and continue instead of stopping.

## Updated Rules

- Company Agent constitution now treats context/token exhaustion and resumable sub-agent pauses as recoverable pauses.
- Agent task runtime contract now requires checkpoint recording and state restoration before continuing.
- Human acceptance policy now distinguishes recoverable pause from task failure.
- Project AGENTS iron rules now require continuing until done, blocked, handed off, rejected, or human-cancelled.
- AI Native OS execution governance now applies the recovery rule to the 74-requirement delivery chain.

## Operational Impact

Project Manager Agent must monitor paused sub-agents, preserve task state, and continue work after recovery. A task can only become blocked after repeated unrecovered pauses with explicit blocker evidence.
