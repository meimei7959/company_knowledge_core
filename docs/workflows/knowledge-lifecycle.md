# Knowledge Lifecycle

## 1. Source Material In

Register original material by reference. Do not copy everything into the knowledge core.

All first-stage records are OKF-compatible Markdown/YAML files.

Examples:

- Git commit / PR.
- README.
- Meeting note.
- Chat summary.
- Customer document.
- Feishu/Lark group message or file.
- Website article or public account article.
- Video, audio, image, screenshot, PDF, Office document, package, binary, model file, or dataset.
- Tool documentation.
- AgentRun.

## 2. Task Dispatch

Most source material should not be parsed by the Feishu bot directly. If material needs judgment, long-context reading, project knowledge, or engineering work, create a task first and let the scheduler assign it to Agent Ring.

```txt
SourceMaterial
-> ProjectTask / KnowledgeTask
-> scheduler matching
-> Agent Ring runner execution
-> TaskResult
```

Task assignment rules:

- Project material is matched to a Runner with project access and required capabilities.
- Company knowledge material is matched to a Runner with knowledge-structuring capability.
- Engineering work is matched to a Runner with repo access, Codex/Claude/tool capability, and policy permission.
- Server-side models only classify intent, extract fields, and route workflow unless the task is explicitly low-risk and short.

## 3. Draft Extraction

Knowledge Engineering Agent extraction sub-agent or human creates draft knowledge:

- KnowledgeDraft.
- ToolUpdate draft.
- ProjectUpdate draft.
- Decision draft.

Draft must preserve sourceRef, confidence, owner, and status.

The Knowledge Engineering Agent extraction sub-agent only converts source material into structured candidates. It must not approve its own draft, decide final storage route alone, or publish reusable knowledge without the review and governance subflow.

Supported intake paths:

- Feishu/Lark path: message, meeting note, file, or thread -> Interaction / SourceMaterial -> KnowledgeTask -> Agent Ring extraction -> TaskResult.
- Agent Ring path: Codex, Claude, local model, browser, script, or another local Agent executes a claimed task through the protocol -> TaskResult / AgentRun / SourceMaterial / ToolUpdate / ProjectUpdate reference -> Knowledge Engineering Agent extraction sub-agent.
- Learning material path: URL, public account article, video/audio, document, screenshot, package, model file, or dataset -> SourceMaterial with materialType, sourceRef/storageRef, contentHash, license/sensitivity, and extraction metadata -> KnowledgeTask -> Agent Ring extraction -> Knowledge Engineering Agent extraction sub-agent.

All paths must produce structured drafts before the Knowledge Engineering Agent review sub-agent gate sees them.

Default execution Agent:

- `agent.company-knowledge-core.knowledge-engineering`
- Agent profile: `agents/agent.company-knowledge-core.knowledge-engineering.md`
- Skill pack: `docs/agent-team/knowledge-engineering-agent-skill-pack.md`
- Reader toolkit registry: `tools/tool.knowledge-material-readers.md`

When Agent Ring is not enabled, the manual Runner prompt must explicitly tell Codex or Claude to read the Agent profile and skill pack before extracting source material. When Agent Ring is enabled, the workbench must include those references in the context pack for tasks assigned to this Agent.

Material extraction rules:

- Web and public articles produce concise summaries, key claims, skill steps, source metadata, and citation links. Do not store copyrighted full text as reusable knowledge.
- Video and audio produce transcriptRef, chapter summary, key steps, tools, terms, and unresolved questions before knowledge extraction.
- Image and screenshot material must run OCR or be summarized with clear source location.
- PDF and Office documents must preserve page or section references.
- Package, binary, model, and dataset material must not be chunked into RAG by default. Store storageRef, contentHash, version, license, owner, allowed use, risk, and install/validation notes.
- Repo material extraction is limited to README, API docs, CHANGELOG, commit/PR summary, and lessons. Full source code remains in Git.

## 4. Knowledge Engineering Review Sub-Agent Gate

Do not use one broad meaning for "entering the knowledge base". The lifecycle has separate gates:

- raw registration: `SourceMaterial`, `KnowledgeTask`, `ProjectTask`, `TaskResult`, `AgentRun`, `AuditLog`, and `NotificationRecord` may be written automatically when required fields and safety checks pass;
- reviewable draft: `KnowledgeItem` / `Decision` / `Workflow` / `ToolAsset` / `Policy` candidates may be written as `draft`, `observed`, `testing`, or `open` only after structure, source, owner, sensitivity, and duplicate checks pass;
- reusable publication: `verified`, `approved`, `active`, cross-team standards, permission changes, customer commitments, and policy/workflow changes require human approval;
- retrieval use: formal answers use `verified` / `approved` / `active`; `draft` / `observed` may only be shown as clearly labeled reference material, not as official truth.

The Knowledge Engineering Agent review sub-agent gate applies to reviewable knowledge candidates and publication requests. It does not block raw material registration or task creation.

### What Does Not Need Human Review

These writes may happen automatically with validation and `AuditLog`:

- `SourceMaterial` registration with `sourceRef`, submitter, material type, sensitivity, and content hash.
- `KnowledgeTask` / `ProjectTask` creation for parsing, summarizing, engineering work, or follow-up.
- `TaskResult` / `AgentRun` writeback from an approved Runner or local workflow.
- `NotificationRecord` and callback/audit records.
- Low-risk extracted notes stored as `draft` or `observed` after the Knowledge Engineering Agent review sub-agent checks pass.

These records are not reusable truth. They are traceable work state or evidence.

### What Needs Review Sub-Agent Gate

These candidates must pass the Knowledge Engineering Agent review sub-agent gate before being indexed for reuse or shown beyond "reference only":

- extracted `KnowledgeItem` drafts;
- issue lessons, integration notes, runbooks, learning notes, and skill notes;
- proposed `Decision` or `Workflow` drafts;
- tool/skill metadata drafts;
- changes to existing draft or observed knowledge;
- knowledge generated from meeting notes, Feishu docs, chat, screenshots, files, repos, or Agent task results.

The gate may mark the candidate as:

- `pass_as_observed`;
- `needs_clarification`;
- `needs_human_approval`;
- `conflict_detected`;
- `reject`.

### What Needs Human Approval

Human approval is required before any of these transitions:

- `KnowledgeItem`: `draft` / `observed` -> `verified`.
- Existing `verified` knowledge is changed, superseded, or deprecated.
- `ToolAsset`: `testing` -> `approved`, or approved tool risk/scope/entrypoint changes.
- `Policy`: `draft` -> `active`, or any active policy change.
- `Workflow` / iron rule / cross-team standard becomes active.
- Project creation or project ownership/risk boundary changes.
- Permission, identity, token, approval, notification, security, or customer-commitment changes.
- Conflicts with existing `verified` / `approved` / `active` objects are resolved.

Human reviewers approve the reusable conclusion, scope, sensitivity, and operational impact. They are not expected to reconstruct raw debugging history.

The Knowledge Engineering Agent review sub-agent checks:

- object type and category;
- required fields and sourceRef;
- confidence and evidence;
- whether relationship edges are parseable, justified, and scoped correctly;
- whether graph impact creates stale candidates, conflicts, or approval requirements;
- sensitivity and permission scope;
- duplicate or conflict with existing knowledge;
- whether the item is raw material instead of reusable knowledge;
- whether the text is understandable by a human reviewer;
- whether the candidate should be auto-stored, clarified, rejected, conflict-routed, or sent to human approval.

Governance classification:

- `auto_observed`: lessons, pitfalls, issue reviews, integration notes, debugging conclusions, low-risk engineering patterns, and low-risk learning notes or skill notes. If the gate passes, store directly as `observed/draft` with ReviewRecord and AuditLog.
- `human_approval_required`: project creation, Agent token requests, approved tools, verified knowledge, policy/workflow/iron-rule changes, permission/security/approval/identity/notification rules, customer commitments, and cross-team standards.
- `clarification_required`: missing project, owner, source, evidence, applicability, sensitivity, or required fields.
- `conflict_required`: conflicts with existing verified/active/approved knowledge.
- `reject`: raw dump, no source, not reusable, prohibited secret/sensitive data, obviously wrong, or not structurally recoverable.

Possible results:

- `pass_as_observed`: store as searchable observed/draft knowledge, no human approval needed.
- `needs_clarification`: ask the submitter for missing facts.
- `needs_human_approval`: generate an approval document and submit to the right approval flow.
- `conflict_detected`: create ConflictRecord and route to owner.
- `reject`: do not enter the reusable knowledge set.

The Knowledge Engineering Agent review sub-agent writes ReviewRecord, IssueRecord, and AuditLog where needed. It may directly store `auto_observed` knowledge after passing the gate. It may draft the human approval document, but it cannot publish `verified`, `approved`, `active`, policy, permission, security, or cross-team standard changes.

## 5. Human Review

Human reviewer checks:

- source validity;
- applicability;
- sensitivity;
- conflict with existing knowledge;
- whether knowledge should remain project-scoped or become company-scoped.

Missing information should become `MissingFact` records and can be asked through a bound communication channel such as a Feishu/Lark group.

## 6. Publication

After review:

- KnowledgeItem: draft -> verified.
- ToolAsset: testing -> approved.
- ConflictRecord: open -> resolved.
- Policy: draft -> active.

All publication must write AuditLog.

## 7. Graph Index And Impact

After extraction, review, or publication, the local index should derive `KnowledgeGraphEdge` records from managed object references.

Graph extraction inputs:

- Project, ProjectTask, KnowledgeTask, AgentRunner, TaskResult, SourceMaterial, KnowledgeItem, AgentRun, ToolAsset, Decision, Policy, ConflictRecord, EvalRun, ReviewRecord, NotificationRecord, and AuditLog records.
- Parseable fields such as projectId, taskId, runnerId, agentId, sourceMaterialRefs, evidenceRefs, knowledgeRefs, toolsUsed, codeRefs, affectedRefs, allowedProjects, allowedTools, and targetRef.
- Reviewed body links that are supported by sourceRef or evidenceRefs.

Graph usage:

- context pack generation explains why each item is included, excluded, or approval-gated;
- stale detection follows edges from changed tools, source material, project status, code references, policies, and decisions;
- review shows affected objects before verified publication, approved tool changes, active policy changes, or conflict resolution;
- API/export can produce GraphSnapshot artifacts for visualization without turning snapshots into truth.

Graph governance rules:

- graph edges inherit sensitivity from their endpoints and evidence;
- secret values must not appear in graph edges or snapshots;
- customer-confidential graph views stay project/customer scoped;
- automated edges may support review, but cannot publish verified knowledge, approved tools, active policies, or cross-team standards without the required review path.

## 8. Usage

Agent uses knowledge through context pack:

```txt
zhenzhi-knowledge start -> context pack -> Agent work
```

Agent must record used knowledge and tools in AgentRun.

## 9. Writeback

After work:

```txt
Agent work -> zhenzhi-knowledge finish -> AgentRun + draft updates
Task work -> zhenzhi-knowledge task finish -> TaskResult + task status + draft updates
```

No significant Agent task is complete without writeback.

For knowledge intake, writeback is not the end of the workflow. `TaskResult` must pass deterministic evaluation and then route to review, retry, or repair according to [Knowledge Ingest Orchestration Workflow](knowledge-ingest-orchestration.md).

## 10. Notification

Task status changes drive bot notifications:

- `pending`: submitter is told material/task was accepted and assigned.
- `processing`: assignee has pulled or started the task.
- `submitted` / `reviewing`: requester can see work is waiting for review.
- `done`: requester is told what was saved, where, and what remains unverified.
- `blocked`: requester or project owner is asked for missing permission, source, or clarification.
- `rejected`: requester is told why it was not saved or processed.

Notifications must be represented as NotificationRecord or AuditLog before the online product stores them elsewhere.

## 11. Staleness

Knowledge becomes stale when:

- linked tool version changes;
- linked Git commit or implementation changes;
- project status changes;
- source material changes;
- newer decision replaces older knowledge;
- review interval expires.

Stale candidate requires reviewer confirmation before state changes.
