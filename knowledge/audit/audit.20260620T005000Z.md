---
type: AuditLog
title: Agent self-improvement workflow implemented
timestamp: 2026-06-20T00:50:00Z
actor: agent.company-knowledge-core.knowledge-engineering
action: agent_team.self_improvement.workflow.update
targetRef: docs/agent-team/company-agent-team-operating-guide.md
before: task quality evaluation created retry or repair tasks, but did not persist reusable Agent improvement assets
after: failed or rejected TaskResult creates AgentImprovementProposal, EvalCase draft, notifications, and AgentCapabilityReport support
policyResult: guide_updated
---

## Summary

Implemented the Agent self-improvement loop so failed, blocked, or human-rejected Agent deliveries become reusable improvement evidence.

## Evidence

- `zhenzhi_knowledge/core.py`
- `zhenzhi_knowledge/cli.py`
- `zhenzhi_knowledge/server.py`
- `tests/test_cli.py`
- `docs/agent-team/company-agent-team-operating-guide.md`
- `knowledge/company/company-agent-team-operating-guide.md`
- `docs/protocols/agent-workbench-integration-brief.md`
- `docs/schemas/core-objects.md`

## Governance

- Company-level improvements must pass Review before becoming shared Skill, EvalCase, workflow rule, or guide content.
- Project-level improvements stay inside project context unless Knowledge Engineering Agent extracts a company-level pattern.
