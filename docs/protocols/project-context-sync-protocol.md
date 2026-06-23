# Project Context Sync Protocol

## Purpose

Project work must be portable across computers.

If one Agent Ring runner starts work on computer A and another runner continues on computer B, the second runner should recover the same project context, task state, source evidence, tool expectations, repository links, and operating constraints without asking the user to explain everything again.

This is a knowledge engineering synchronization problem, not only a file sync problem.

## Principle

Central Processor is the source of truth.

Agent Ring runners are execution caches. A local computer may hold working files, model caches, logs, browser state, and tool installations, but project memory, task state, decisions, evidence, and reusable knowledge must be synchronized through the central processor.

```txt
Computer A Agent Ring
-> writes TaskResult / AgentRun / artifacts / knowledge drafts
-> Central Processor stores structured project state
-> Computer B Agent Ring pulls Project Context Bundle
-> work continues with no context loss
```

## Context Bundle

The central processor must be able to generate a `ProjectContextBundle` for a project, task, or handoff.

Minimum contents:

- Project record and current status.
- ProjectTask / KnowledgeTask queue and latest task states.
- Current task context pack.
- SourceMaterial refs and evidence refs.
- Relevant KnowledgeItem records, including confidence, scope, and review status.
- Decisions, conflicts, known risks, and open questions.
- ToolAsset and SkillAsset requirements.
- Agent role descriptions and expected collaboration model.
- Repository refs, branch refs, commit refs, and setup commands.
- Environment manifest refs.
- Secret refs, never secret values.
- Recent TaskResult and AgentRun summaries.
- Handoff notes from previous runner.
- Audit trail and review requirements.

The bundle should contain structured refs and concise summaries. Large raw files, logs, binaries, meeting recordings, and screenshots stay as storage refs.

Current central API exposure:

```txt
POST /v0/tasks/pull
```

The response contains:

- `contextRef`: the generated markdown context pack for local agents.
- `context`: readable task context with source material snapshots.
- `projectContextBundle`: structured project, task, knowledge, execution history, and handoff refs.

Agent Ring should use `projectContextBundle` as the machine-readable handoff layer and `context` as the local model reading pack.

## Environment Manifest

Portable work requires a machine-readable environment description.

Each project should maintain an environment manifest:

```yaml
projectId: company-knowledge-core
repositories:
  - name: company_knowledge_core
    remote: git@github.com:zhenzhi/company_knowledge_core.git
    defaultBranch: main
    requiredBranches: []
commands:
  setup:
    - python3 -m unittest tests.test_cli
  validate:
    - python3 -m zhenzhi_knowledge --root . validate
tools:
  - codex_cli
  - git
  - python3
models: []
secrets:
  - ref: secret://lark/bot-token
    requiredFor: feishu_bot
dataScopes:
  - company_internal
```

The manifest tells a new runner how to recreate the project workspace. It does not store credentials.

## Sync Directions

### Pull

Agent Ring pulls context before claiming or continuing work:

```txt
GET /v0/projects/<projectId>/context
GET /v0/tasks/<taskId>/context
GET /v0/projects/<projectId>/environment
```

### Push

Agent Ring pushes structured results after work:

```txt
POST /v0/tasks/<taskId>/result
POST /v0/runs
POST /v0/source-materials/<sourceId>/extractions
POST /v0/knowledge/drafts
POST /v0/projects/<projectId>/handoffs
```

Push must be idempotent. Every write should include runnerId, executorAgent, taskId, source refs, and evidence refs.

## Handoff Contract

When a task moves from one runner to another, the previous runner should write a handoff note:

```yaml
handoffId: handoff.KT-20260618-001.001
taskId: KT-20260618-001
fromRunner: runner.mac-mini-01
toRunner:
status: ready_for_reassignment
summary: what was done
currentState: what is true now
nextStep: what the next runner should do
blockedOn: []
workspaceRefs:
  - git://repo@commit
artifactRefs: []
evidenceRefs: []
logsRef:
```

The next runner should not depend on hidden local state from the previous computer.

## Conflict Rules

Context sync must detect and surface conflicts:

- two runners claim the same task;
- local workspace commit differs from central recorded commit;
- a KnowledgeItem draft contradicts verified knowledge;
- environment manifest is missing a required tool;
- source material was updated after a runner pulled context;
- result writeback references unknown evidence.

ConflictRecord should be created when automatic merge is unsafe.

## What Must Not Be Synced As Plain Knowledge

- secret values;
- raw long logs;
- private local browser cookies;
- local absolute paths as canonical references;
- unreviewed summaries as verified facts;
- binary artifacts without storageRef, hash, source, and license.

## MVP

The first version can be simple:

1. Central processor generates task context pack from Project, Task, SourceMaterial, KnowledgeItem, Decisions, ToolAsset, and recent TaskResult.
2. Agent Ring pulls the context pack before claim.
3. Agent Ring writes TaskResult, AgentRun, and optional handoff note.
4. Scheduler can reassign expired or blocked tasks to another runner.
5. New runner pulls the same context pack plus latest handoff note and continues.

## Success Standard

A project is portable when:

- a second computer can pull the project and task context without asking the user to restate history;
- required setup, repository, tool, and secret refs are discoverable;
- previous work has structured TaskResult and AgentRun records;
- all AI summaries cite original SourceMaterial or evidence;
- local-only state is either unnecessary or represented by an artifact/storage ref;
- a runner can safely stop and another runner can continue.
