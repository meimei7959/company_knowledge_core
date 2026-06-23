# Engineering Extension Model

## Purpose

The project must stay extensible as it grows from an OKF-compatible bundle into a central scheduler and knowledge platform.

Extensions should add capability without deleting existing objects, breaking old records, or coupling the central processor to a specific Agent Ring implementation.

## Extension Principles

- Preserve existing records and fields.
- Add new fields as optional before making them required.
- Keep object contracts human-readable and machine-readable.
- Keep runtime implementation behind protocol boundaries.
- Use references for large files, binaries, logs, and secrets.
- Add validation and tests for every new lifecycle rule.
- Make every write auditable.

## Extension Surfaces

### New Object Type

Use this path when the system needs a new durable concept.

Required changes:

- define object in `docs/schemas/core-objects.md`;
- add a template under `templates/`;
- add directory/index if it has its own collection;
- add validation rules when risk is high;
- update docs/workflows if it changes lifecycle;
- add CLI/API support only when humans or Agents must create it repeatedly;
- add tests for required fields and invalid placement.

Examples:

- `AgentRunner`
- `SourceMaterial`
- `TaskResult`
- future `ProjectContextBundle`
- future `EnvironmentManifest`

### New Task Type

Use this path when the scheduler needs to route a new kind of work.

Required changes:

- add task type meaning in object model docs;
- define requiredCapabilities and expectedOutput;
- document which runner capabilities can execute it;
- define result writeback shape;
- add notification and review rules;
- add tests for lifecycle.

Examples:

- `project_init`
- `knowledge_capture`
- `engineering_action`
- `tool_request`
- `handoff`

### New Runner Capability

Use this path when Agent Ring can do a new kind of local work.

Required changes:

- add capability name and meaning to protocol docs;
- add permission/risk boundary;
- define health check expectation if critical;
- define output/evidence requirements;
- ensure scheduler can match on it.

Examples:

- `codex_cli`
- `claude_cli`
- `long_context_summary`
- `browser_automation`
- `repo_bootstrap`
- `feishu_doc_read`

### New External Connector

Use this path for systems outside the central processor.

Required changes:

- add protocol doc under `docs/protocols/`;
- define ownership boundary;
- define auth, idempotency, retry, and audit;
- define writeback objects;
- define failure and conflict behavior;
- keep connector runtime outside this repository unless explicitly accepted.

Examples:

- Agent Ring
- Feishu/Lark channel adapter
- future Git hosting adapter
- future artifact storage adapter

### New Knowledge Domain

Use this path when a business area needs reusable knowledge.

Required changes:

- create category under `knowledge/<category>/` only when it is a core category;
- otherwise keep domain-specific schemas outside core and store refs/summaries here;
- define source evidence and review owner;
- define sensitivity and access rules.

Core should not absorb every business-domain object model.

### New Storage Backend

Use this path when Markdown files are no longer enough for hot state.

Required changes:

- keep export/import compatibility with the OKF bundle;
- define canonical object IDs;
- keep AuditLog append-only;
- keep references stable across storage moves;
- update validation/harness to compare exported records.

## Versioning

Contracts should carry explicit versions once external systems depend on them.

Recommended fields:

```yaml
apiVersion: v0.1
schemaVersion: 0.1.0
protocolVersion: 0.1.0
compatibility:
  minCentralProcessor: 0.1.0
  minAgentRing: 0.1.0
```

Breaking changes require:

- migration notes;
- backward-compatible read path when possible;
- tests for old and new records;
- clear deprecation window.

## Engineering Gates

Before a new architecture extension is considered done:

- docs explain the product reason and boundary;
- schema/template exists if a durable record is introduced;
- workflow explains lifecycle and review;
- validation catches dangerous invalid states;
- tests cover the lifecycle path;
- examples avoid raw secrets and local-only paths;
- Agent Ring dependency is expressed as a protocol contract, not an in-repo runtime assumption.

## Migration Rule

Do not rewrite the project by replacement.

Upgrade in layers:

```txt
existing record
-> optional new fields
-> template/docs update
-> validation warning
-> lifecycle tests
-> runtime support
-> stricter validation only after records are migrated
```

This keeps old knowledge usable while the product architecture becomes more capable.
