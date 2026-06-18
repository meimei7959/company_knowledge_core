# Core Tool Contract Draft

The first tool surface is the `zhenzhi-knowledge` local connector.

Do not implement a large platform first. Implement local commands that operate on the OKF-compatible Git bundle and later switch to `backend: api`.

## init / status

- `zhenzhi-knowledge init`
- `zhenzhi-knowledge status`
- `zhenzhi-knowledge profile use <local|staging|production>`

Responsibilities:

- Locate knowledge repository.
- Create local profile.
- Validate config.
- Never store secrets in knowledge files.

## sync

- `zhenzhi-knowledge sync pull`
- `zhenzhi-knowledge sync push`

Responsibilities:

- Pull latest team knowledge.
- Push reviewed updates.
- Detect conflicts.
- Never let Agent auto-overwrite conflicts.

## register

- `zhenzhi-knowledge agent register`
- `zhenzhi-knowledge project register`
- `zhenzhi-knowledge tool register`

Responsibilities:

- Generate OKF-compatible Markdown files.
- Generate Agent, Project, or ToolAsset records.
- Update `index.md`.
- Append `log.md`.
- Preserve unknown frontmatter fields.

## chat thread / interaction

- `zhenzhi-knowledge chat-thread bind`
- `zhenzhi-knowledge chat-thread list`
- `zhenzhi-knowledge interaction create`
- `zhenzhi-knowledge interaction search`

Responsibilities:

- Bind external communication channels such as Feishu/Lark groups to projects.
- Record customer messages, file uploads, and confirmations as Interaction records.
- Link Interaction records to SourceMaterial and KnowledgeItem records.
- Preserve external message IDs for traceability.

## missing facts

- `zhenzhi-knowledge missing-fact create`
- `zhenzhi-knowledge missing-fact list`
- `zhenzhi-knowledge missing-fact update`

Responsibilities:

- Track missing customer/project information.
- Link missing facts to source materials and interactions.
- Support status transitions: open -> asked -> answered -> confirmed -> closed.
- Keep business-domain-specific reasoning in the domain project, not core.

## task lifecycle

- `zhenzhi-knowledge start`
- `zhenzhi-knowledge finish`

Responsibilities:

- `start` validates projectId, agentId, policy, and tool permissions.
- `start` generates `.zhenzhi/context/current.md`.
- `finish` generates AgentRun, ProjectUpdate draft, KnowledgeDraft, and ToolUpdate draft.
- Agent/CLI push content must be recorded as AgentRun, SourceMaterial, ToolUpdate, or ProjectUpdate input before extraction.
- CLI-pushed content must go through Knowledge Extraction Agent before Knowledge Review Agent classification.

## review

- `zhenzhi-knowledge review list`
- `zhenzhi-knowledge review update`
- `zhenzhi-knowledge review bulk`
- `zhenzhi-knowledge review agent-check`

Responsibilities:

- Run the Knowledge Review Agent gate before indexing, human approval, or status promotion.
- Classify each candidate as auto observed, human approval required, clarification required, conflict required, or rejected.
- Directly store passed low-risk lessons, pitfalls, issue reviews, integration notes, and debugging conclusions as `observed/draft`.
- Create ReviewRecord for machine review results.
- Create IssueRecord for missing fields, unclear source, sensitivity risk, duplicate risk, conflict risk, or unreadable approval material.
- Generate reviewer-facing approval documents only for candidates classified as requiring human approval.
- Promote draft -> verified.
- Promote testing -> approved.
- Promote stale_candidate -> stale or verified.
- Write AuditLog.
- Require human action for verified knowledge, approved tools, policy changes, and high-risk actions.
- Block approved promotion when target has a failing EvalRun.

## policy

- `zhenzhi-knowledge policy register`

Responsibilities:

- Create Policy objects.
- Express Agent read/write/tool risk permissions.
- Support later Gateway enforcement.

## eval

- `zhenzhi-knowledge eval case create`
- `zhenzhi-knowledge eval run`

Responsibilities:

- Create EvalCase objects.
- Record EvalRun results.
- Write failure cases back as draft KnowledgeItem issues.

## conflict / stale / metrics

- `zhenzhi-knowledge conflict create`
- `zhenzhi-knowledge conflict resolve`
- `zhenzhi-knowledge audit search`
- `zhenzhi-knowledge stale scan`
- `zhenzhi-knowledge metrics report`

Responsibilities:

- Record conflicts as ConflictRecord.
- Resolve conflicts with AuditLog evidence.
- Query AuditLog by project, Agent, ToolAsset, or target reference.
- Detect stale knowledge candidates.
- Leave stale detection in stale_candidate until reviewer confirmation.
- Create operational MetricsReport.

## backup

- `zhenzhi-knowledge backup create`
- `zhenzhi-knowledge backup restore`

Responsibilities:

- Create local zip backups.
- Restore a backup with explicit overwrite.
- Exclude local runtime state such as `.zhenzhi/`.

## API / Gateway prototype

- `zhenzhi-knowledge api export`
- `zhenzhi-knowledge api serve`
- `zhenzhi-knowledge gateway context`

Responsibilities:

- Export a local `KnowledgeSnapshot v0.1`.
- Serve local HTTP endpoints for health, objects, retrieval, audit, gateway context, review, and tool invocation.
- Generate local `GatewayContext v0.1`.
- Preserve a future path from local Git backend to API backend.

## index / search

- `zhenzhi-knowledge index rebuild`
- `zhenzhi-knowledge index search`
- `zhenzhi-knowledge rag rebuild`
- `zhenzhi-knowledge rag search`

Responsibilities:

- Scan frontmatter.
- Build local SQLite metadata index.
- Build local chunk retrieval index.
- Exclude secrets and customer-confidential content from retrieval.
- Provide metadata search and local RAG retrieval with sourceRefs.
- Keep RAG as context recall, not source of truth.

## tool invocation

- `zhenzhi-knowledge tool invoke`

Responsibilities:

- Block unregistered tools.
- Check Project, Agent, Policy, ToolAsset risk, allowedProjects, and allowedAgents.
- Default to dry-run; local safe execution supports only explicitly safe entrypoints.
- Write AuditLog for allowed and denied invocation attempts.
- Generate default invocationPolicy from riskLevel during tool registration.
