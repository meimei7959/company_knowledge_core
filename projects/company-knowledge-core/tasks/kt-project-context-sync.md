---
type: ProjectTask
title: Project context portability and sync design
description: Define how project work moves between Agent Ring runners without losing context.
timestamp: "2026-06-18T00:00:00Z"
taskId: KT-PROJECT-CONTEXT-SYNC
taskType: engineering_action
projectId: company-knowledge-core
requester: zhenzhi-central-processor
assignee: zhenzhi-knowledge-core
requiredCapabilities:
  - project_context_bundle
  - environment_manifest
  - task_handoff
  - runner_reassignment
  - knowledge_sync
requiredAgents:
  - knowledge-architecture-agent
  - scheduler-agent
  - agent-ring-integration-agent
preferredRunner: []
assignedRunner: []
executorAgent: []
leaseOwner: []
leaseExpiresAt: []
status: done
priority: high
dueAt: []
sourceMaterialRefs:
  - docs/protocols/project-context-sync-protocol.md
  - docs/protocols/agent-ring-communication-protocol.md
  - docs/architecture/central-processor-and-agent-ring.md
expectedOutput:
  - ProjectContextBundle schema
  - Environment manifest schema
  - Runner handoff contract
  - Reassignment and conflict rules
  - Tests or harness checks for cross-runner continuation
resultRef: task-results/tr-kt-project-context-sync.md
notificationRefs: []
auditRefs: []
completedAt: "2026-06-18T11:29:43Z"
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"engineering_action","category":"engineering","stage":"","requiredCapabilities":["engineering_action","project_context_bundle","environment_manifest","task_handoff","runner_reassignment","knowledge_sync"],"requiredTools":[],"sourceRefs":["docs/protocols/project-context-sync-protocol.md","docs/protocols/agent-ring-communication-protocol.md","docs/architecture/central-processor-and-agent-ring.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"engineering","acceptancePath":"pm_review","reviewPath":"engineering_test","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
updatedAt: "2026-06-21T07:18:05Z"
---

## Request

Make project work portable across computers.

When one Agent Ring runner starts a project or task and another runner continues it, the second runner should not need the user to explain project history again. It should pull the same structured project state, task state, knowledge, evidence, environment requirements, repository refs, and handoff notes from the central processor.

## Why This Matters

If project context lives only on one computer, every computer becomes an isolated Agent island. That creates repeated setup, lost decisions, unclear task progress, and inconsistent knowledge.

The central processor should make each computer replaceable. Agent Ring provides execution; the central processor provides memory, state, policy, and continuity.

## Expected Output

- Define `ProjectContextBundle`.
- Define project environment manifest.
- Define handoff note shape.
- Define how a task can move from one runner to another.
- Define conflict handling when local state diverges from central state.
- Add harness checks proving a second runner can continue from the first runner's output.

## Definition of Done

- ProjectContextBundle schema includes project state, task state, SourceMaterial refs, evidence refs, KnowledgeItem refs, decisions, conflicts, risks, recent TaskResults, AgentRuns, environment manifest refs, repository refs, secret refs, and handoff notes.
- Environment manifest describes repositories, setup commands, validation commands, tools, model requirements, data scopes, and secret refs without local-only absolute paths as canonical state.
- Handoff note contract records what was done, current state, next step, blockers, workspace refs, artifact refs, evidence refs, and logsRef.
- Scheduler can reassign a task from one runner to another without losing required context.
- Conflict rules detect stale source material, divergent commit refs, missing tool/secret refs, and contradictory knowledge.

## Test Plan

- Unit test context bundle generation for a project with tasks, sources, knowledge, decisions, and results.
- Unit test environment manifest rejects plaintext secrets and unstable local-only paths.
- E2E StubRunner test: runner A claims and writes handoff; runner B pulls updated context and completes task.
- Conflict test for source material updated after context pull.
- Conflict test for missing required secretRef or tool capability.
- Regression test ensures bundle excludes large raw logs/binaries and uses refs.
- Run `python3 -m zhenzhi_knowledge --root /Users/meimei/Documents/company_knowledge_core validate`.
- Run `python3 -m unittest tests.test_cli`.

## Self-Verification Checklist

- Confirm a new computer can understand project state without chat history.
- Confirm bundle is sufficient but not a raw dump.
- Confirm handoff and AgentRun records make previous runner work auditable.
- Confirm reassignment behavior is tested before real Agent Ring exists.
