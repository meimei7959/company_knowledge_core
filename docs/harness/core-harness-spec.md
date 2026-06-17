# Core Harness Spec

Harness is the quality gate for the knowledge core. Implementation comes after the model and directory structure are confirmed.

The first implementation target is the `zhenzhi-knowledge` local connector operating on the OKF-compatible bundle.

## OKF Format Checks

- Every knowledge object file must have YAML frontmatter.
- Every knowledge object file must include `type`.
- Tools must preserve unknown frontmatter fields.
- `index.md` and `log.md` are allowed directory files.

## Directory Checks

Required first-stage directories:

- `projects/`
- `agents/`
- `tools/`
- `knowledge/`
- `runs/`

Required first-stage root files:

- `index.md`
- `log.md`
- `README.md`

## Connector Checks

The local connector must support:

- `init`
- `status`
- `profile`
- `sync pull`
- `sync push`
- `agent register`
- `project register`
- `tool register`
- `tool invoke`
- `policy register`
- `start`
- `finish`
- `review`
- `validate`
- `index rebuild`
- `index search`
- `rag rebuild`
- `rag search`
- `conflict create`
- `conflict resolve`
- `audit search`
- `stale scan`
- `metrics report`
- `eval case create`
- `eval run`
- `backup create`
- `backup restore`
- `api export`
- `api serve`
- `gateway context`

## Agent Workflow Checks

- Formal Agent tasks must have projectId and agentId.
- `start` must generate a context pack before work.
- `finish` must generate AgentRun after work.
- Agent output must include knowledge refs used.
- Agent output must include draft updates or explicitly state `no reusable lesson`.

## Governance Checks

- verified KnowledgeItem requires human review.
- approved ToolAsset requires Tool Owner approval.
- approved ToolAsset must be blocked when a failing EvalRun targets it.
- Policy changes require review.
- High-risk tools require approval.
- All status changes must create AuditLog.
- Customer confirmations from Feishu/Lark must be distinguishable from agent assumptions.
- MissingFact status changes must preserve the asking/answering Interaction reference when available.
- Failed EvalRun or ReviewRecord must create or reference IssueRecord when follow-up is needed.
- Approved deliverables must have review/evaluation evidence.

## Security Checks

- secret values must not appear in knowledge files.
- customer_confidential data must not enter company-level RAG by default.
- Agent context must be filtered by allowedKnowledgeScopes.
- Unregistered tools must not be callable by Agent workflow.

## Operational Checks

- stale knowledge must be detectable.
- stale_candidate must require reviewer confirmation before stale.
- draft backlog must be measurable.
- unfinished AgentRun must be measurable.
- tool reuse must be measurable.
- failed evaluation backlog must be measurable.
- unresolved IssueRecord count must be measurable.

## Communication Checks

- Feishu/Lark group messages used by a domain must be recorded as Interaction or SourceMaterial records.
- Group files must preserve external message/resource references.
- Missing facts asked in chat must link back to MissingFact records.
- Customer answers must be traceable to the source Interaction.
