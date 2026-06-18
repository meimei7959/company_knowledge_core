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

## 2. Draft Extraction

Knowledge Extraction Agent or human creates draft knowledge:

- KnowledgeDraft.
- ToolUpdate draft.
- ProjectUpdate draft.
- Decision draft.

Draft must preserve sourceRef, confidence, owner, and status.

The Knowledge Extraction Agent only converts source material into structured candidates. It must not decide final storage route or publish the draft.

Supported intake paths:

- Feishu/Lark path: message, meeting note, file, or thread -> Interaction / SourceMaterial -> Knowledge Extraction Agent.
- Agent/CLI path: Codex, Claude, Antigravity, cloud Agent, or another local Agent pushes content through `zhenzhi-knowledge` -> AgentRun / SourceMaterial / ToolUpdate / ProjectUpdate reference -> Knowledge Extraction Agent.
- Learning material path: URL, public account article, video/audio, document, screenshot, package, model file, or dataset -> SourceMaterial with materialType, sourceRef/storageRef, contentHash, license/sensitivity, and extraction metadata -> material-specific extractor -> Knowledge Extraction Agent.

Both paths must produce structured drafts before the Knowledge Review Agent sees them.

Material extraction rules:

- Web and public articles produce concise summaries, key claims, skill steps, source metadata, and citation links. Do not store copyrighted full text as reusable knowledge.
- Video and audio produce transcriptRef, chapter summary, key steps, tools, terms, and unresolved questions before knowledge extraction.
- Image and screenshot material must run OCR or be summarized with clear source location.
- PDF and Office documents must preserve page or section references.
- Package, binary, model, and dataset material must not be chunked into RAG by default. Store storageRef, contentHash, version, license, owner, allowed use, risk, and install/validation notes.
- Repo material extraction is limited to README, API docs, CHANGELOG, commit/PR summary, and lessons. Full source code remains in Git.

## 3. Knowledge Review Agent Gate

Every candidate must pass the Knowledge Review Agent before direct storage, indexing for reuse, human approval, or promotion.

The Knowledge Review Agent checks:

- object type and category;
- required fields and sourceRef;
- confidence and evidence;
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

The Knowledge Review Agent writes ReviewRecord, IssueRecord, and AuditLog where needed. It may directly store `auto_observed` knowledge after passing the gate. It may draft the human approval document, but it cannot publish `verified`, `approved`, `active`, policy, permission, security, or cross-team standard changes.

## 4. Human Review

Human reviewer checks:

- source validity;
- applicability;
- sensitivity;
- conflict with existing knowledge;
- whether knowledge should remain project-scoped or become company-scoped.

Missing information should become `MissingFact` records and can be asked through a bound communication channel such as a Feishu/Lark group.

## 5. Publication

After review:

- KnowledgeItem: draft -> verified.
- ToolAsset: testing -> approved.
- ConflictRecord: open -> resolved.
- Policy: draft -> active.

All publication must write AuditLog.

## 6. Usage

Agent uses knowledge through context pack:

```txt
zhenzhi-knowledge start -> context pack -> Agent work
```

Agent must record used knowledge and tools in AgentRun.

## 7. Writeback

After work:

```txt
Agent work -> zhenzhi-knowledge finish -> AgentRun + draft updates
```

No significant Agent task is complete without writeback.

## 8. Staleness

Knowledge becomes stale when:

- linked tool version changes;
- linked Git commit or implementation changes;
- project status changes;
- source material changes;
- newer decision replaces older knowledge;
- review interval expires.

Stale candidate requires reviewer confirmation before state changes.
