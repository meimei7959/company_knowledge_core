---
type: ProjectTask
title: AI Native OS Skill Registry lifecycle hardening
description: Register, version, evaluate, publish, reuse, and retire Agent skills across company and project scopes.
timestamp: "2026-06-20T02:40:00Z"
taskId: KT-OS-SKILL-REGISTRY-LIFECYCLE
taskType: os_maturity_hardening
projectId: company-knowledge-core
requester: meimei
assignee: agent.company-knowledge-core.knowledge-engineering
requiredCapabilities:
  - skill_registry
  - skill_versioning
  - eval_gate
  - reuse_scope
requiredAgents:
  - agent.company-knowledge-core.knowledge-engineering
  - agent.company-knowledge-core.project-manager
preferredRunner: []
assignedRunner: runner.meimei-mac-local-codex
executorAgent: []
leaseOwner: []
leaseExpiresAt: []
status: waiting_runner
priority: high
dueAt: []
sourceMaterialRefs:
  - docs/agent-team/company-agent-team-operating-guide.md
  - docs/agent-team/knowledge-engineering-agent-skill-pack.md
expectedOutput:
  - SkillAsset contract
  - skill promotion workflow
  - eval requirement for skill updates
  - public versus project-private reuse policy
resultRef: []
notificationRefs:
  - notifications/notification.20260621T052918746881Z.md
  - notifications/notification.20260621T053349653698Z.md
  - notifications/notification.20260621T053430466779Z.md
  - notifications/notification.20260621T055524586518Z.md
  - notifications/notification.20260621T055554631415Z.md
  - notifications/notification.20260621T055613444759Z.md
  - notifications/notification.20260621T061855458443Z.md
  - notifications/notification.20260621T062940776684Z.md
auditRefs: []
updatedAt: "2026-06-21T07:18:05Z"
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"os_maturity_hardening","category":"project","stage":"","requiredCapabilities":["os_maturity_hardening","skill_registry","skill_versioning","eval_gate","reuse_scope"],"requiredTools":[],"sourceRefs":["docs/agent-team/company-agent-team-operating-guide.md","docs/agent-team/knowledge-engineering-agent-skill-pack.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
---

## Goal

Make Agent capabilities improve through governed skills instead of informal prompt changes.

## Supports Mature OS Capability

Skill Registry.

## Requirements

- Skill records include owner Agent, scope, version, trigger, input/output, dependencies, eval cases, and rollback path.
- Skill changes require evaluation before company-wide reuse.
- Project-private skills cannot silently become company standards.

## Completion Standard

- Skill update produces version bump, changelog, eval result, and guide update when published.
- Failed skill eval blocks promotion and creates repair task.

## Test Method

- Skill registration validation.
- Skill promotion happy path and failed eval path.
- Query/list behavior for public and private skills.
