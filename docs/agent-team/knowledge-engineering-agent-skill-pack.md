# Knowledge Engineering Agent Skill Pack

## Purpose

This document defines the default skill pack for `agent.company-knowledge-core.knowledge-engineering`.

It inherits `docs/agent-team/common-agent-operating-rules.md`. This file only defines Knowledge Engineering specific responsibility, skills, workflow, handoff, and acceptance.

The goal is not to make the Agent summarize anything it sees. The goal is to make the Knowledge Engineering Agent team convert source material into evidence-backed, reviewable, governed knowledge.

The top-level Knowledge Engineering Agent owns the whole workflow. Review, governance, approval routing, repair, indexing, notification, and operations are sub-agent roles inside the workflow, not unrelated standalone responsibilities.

Operating check:

```bash
zhenzhi-knowledge agent role-check --role knowledge-engineering --project <project-id> --actor agent.<project-id>.project-manager
```

## Operating Principle

```txt
source reference
-> material type
-> reader skill
-> raw snapshot / storageRef / contentHash
-> evidence packet
-> structured draft
-> TaskResult
-> Knowledge Review sub-agent
-> governance / human approval when required
-> observed or verified writeback
-> indexing and notification
```

No conclusion may enter a `KnowledgeItem` draft unless it has an evidence path back to the original material.

## Sub-Agent Roles Inside The Workflow

The Agent team must keep duties separated without breaking ownership of the full flow.

- Extraction sub-agent: reads SourceMaterial, builds evidence packets, writes TaskResult and KnowledgeItem draft.
- Review sub-agent: checks structure, evidence, sensitivity, duplicate risk, conflict risk, scope, and reviewer readability.
- Governance sub-agent: decides category, ownership, policy impact, public/project boundary, and human approval path.
- Ops sub-agent: handles tool access, connector failure, sync failure, audit integrity, notification, and indexing failures.
- Human approval actor: required for verified knowledge, policy/workflow/permission changes, security impact, customer commitments, or cross-team standards.

The extraction sub-agent must not approve its own output. The top-level Knowledge Engineering Agent is still responsible for driving the item through all sub-agent steps until it reaches `observed`, `verified`, `rejected`, `blocked`, or `changes_requested`.

## Required Skill Groups

### 1. Source Type Classifier

Classifies incoming material before extraction.

Inputs:

- `sourceRef`
- `storageRef`
- `materialType`
- file extension
- URL host/path
- task title/body

Outputs:

- normalized `materialType`;
- candidate reader skill;
- access requirements;
- sensitivity and copyright warning;
- fallback path when the source cannot be read.

Common material types:

- `feishu-doc`
- `feishu-minutes`
- `feishu-drive-file`
- `pdf`
- `office-document`
- `spreadsheet`
- `web-article`
- `public-account-article`
- `youtube-video`
- `image`
- `repo-doc`
- `chat-message`
- `package-or-binary`
- `dataset`

### 2. Source Reader Skills

Each reader must preserve source metadata and stable evidence locations.

| Material | Preferred reader | Fallback | Required evidence location |
| --- | --- | --- | --- |
| Feishu document | `lark-doc` | exported markdown / user pasted text | doc token, block id, heading, paragraph |
| Feishu minutes / meeting | `lark-minutes` / `lark-vc` | transcript export / user pasted minutes | minutes token, chapter, speaker, timestamp |
| Feishu drive file | `lark-drive` plus file-specific parser | downloaded file reference | file token, version, page/section |
| PDF | `pdf` parser | OCR / user-provided excerpt | page number, region or heading |
| Word / docx | `documents` parser | exported markdown | heading, paragraph, table index |
| Spreadsheet | `spreadsheets` parser | CSV export | sheet name, row/column range |
| Web article | web reader / browser snapshot | user pasted text / PDF export | URL, title, section, quote |
| Public account article | accessible URL reader | forwarded text, screenshot OCR, PDF export | original URL or capture ref, section |
| YouTube/video | transcript reader | user-provided transcript / downloaded audio task | video URL, timestamp range |
| Image/screenshot | OCR / visual inspection | human transcription | image ref, region |
| Repo document | Git / CodeGraph / repo doc reader | user-provided file path | repo URL, commit, file path, line/heading |
| Package/binary/model/dataset | registrar only | owner-provided manifest | storageRef, hash, version, license |

If the preferred reader is unavailable, the Agent must record the fallback used and lower confidence when appropriate.

### 3. Evidence Packet Builder

Every extraction must produce an internal evidence packet before writing knowledge.

Minimum structure:

```yaml
sourceMaterialRef: projects/<project>/sources/<source>.md
originalRef: <url/file/doc token/message ref>
contentHash: <sha256 or source hash>
extractedAt: <iso time>
extractor: <reader skill or tool name>
chunks:
  - chunkId: <stable id>
    location: <page/block/timestamp/url/heading/row>
    text: <short excerpt or normalized statement>
    sensitivity: internal
    confidence: high|medium|low
```

### 3A. Software Copyright Material Pack

Use [China Software Copyright Submission Pack](../../skills/china-software-copyright-submission-pack/SKILL.md) when a frozen project version, software module, tool, or Agent product needs Chinese software copyright application materials.

Knowledge Engineering Agent owns the material pack because the work is source-backed evidence collection, mapping, consistency checking, sensitivity scanning, and archival. Project Manager Agent owns the release node and task routing only.

Rules:

- Do not generate or rewrite applicant-owned source code.
- Do not write legal facts, ownership facts, signatures, application-form declarations, or manual body text for the applicant.
- Only run `init` and `collect` automatically.
- `finalize-human` is reserved for the applicant owner after checking the current official form and actual AI usage facts.
- Route missing product boundary to Product Manager Agent, missing source/build details to Development Agent, missing screenshots/test evidence to Test Agent, and missing applicant/legal materials to the human owner.

The evidence packet may live inside `TaskResult` initially. Later it can become a first-class object if needed.

### 4. Knowledge Extractor

Transforms evidence into structured knowledge.

Required sections for `KnowledgeItem` drafts:

- Context.
- Source / evidence.
- Summary.
- Structured knowledge.
- Applies when.
- Does not apply when.
- Risks or pitfalls.
- Open questions.
- Review notes.

Required frontmatter:

- `type: KnowledgeItem`
- `title`
- `owner: agent.company-knowledge-core.knowledge-engineering`
- `status: draft`
- `scope`
- `sourceRef`
- `confidence`
- `projectId` when project-scoped
- `tags`

### 5. Citation Builder

For each conclusion, include an evidence reference.

Acceptable evidence references:

- `SourceMaterial` path.
- Feishu doc block or heading.
- PDF page.
- Word heading/paragraph.
- video timestamp.
- web URL plus section.
- repo commit/file/line or heading.
- screenshot region.

If evidence cannot be cited, the statement must stay in `Open Questions` or `Limits`, not `Knowledge`.

### 6. Writeback Skill

Writes durable records:

- `TaskResult`;
- `KnowledgeItem draft`;
- optional `ConflictRecord` when extraction conflicts with existing verified knowledge;
- optional `MissingFact` / issue note when source or scope is incomplete;
- review record, repair task, approval request, notification, and index update when the review subflow requires them;
- `AuditLog` through the standard CLI/API path.

The Agent must update task state:

- `submitted` when draft/result is ready for review;
- `blocked` when source cannot be resolved or required tool access is missing;
- never `done` unless the owning workflow explicitly permits it after review.

## Stable Manual CLI Workflow

When the human provides content directly, use this local workflow unless Agent Ring has already supplied a task card.

1. Register the content as SourceMaterial and create a task:

```bash
python3 -m zhenzhi_knowledge.cli material ingest \
  --project company-knowledge-core \
  --submitter <submitter> \
  --title "<material title>" \
  --source-ref "<original source ref or manual://...>" \
  --material-type <materialType> \
  --content-file <path-to-local-snapshot> \
  --create-task \
  --assignee agent.company-knowledge-core.knowledge-engineering
```

2. Read the generated task card and every `sourceMaterialRefs` entry before extraction.

3. Build an evidence packet with `sourceMaterialRef`, `originalRef`, `contentHash`, `extractedAt`, `extractor`, and stable chunk/page/block/timestamp references.

4. Write the structured draft payload as JSON:

```json
{
  "title": "<knowledge title>",
  "summary": "<short summary>",
  "structured": "<evidence-backed structured knowledge>",
  "sourceRefs": ["projects/<project>/sources/<source>.md"],
  "confidence": "high|medium|low",
  "scope": "engineering",
  "limits": ["<applicability limit>"],
  "knowledgeType": "lesson"
}
```

5. Finish the task with the draft payload:

```bash
python3 -m zhenzhi_knowledge.cli task finish <taskId> \
  --result submitted \
  --summary "<what was extracted>" \
  --evidence-ref projects/<project>/sources/<source>.md \
  --executor-agent agent.company-knowledge-core.knowledge-engineering \
  --knowledge-draft-file <draft-json-file>
```

Expected writeback:

- `TaskResult` with `sourceMaterialRefs`, `evidenceRefs`, `knowledgeRefs`, and deterministic quality evaluation.
- `KnowledgeItem` draft under `knowledge/<category>/`.
- review follow-up task for the Knowledge Review sub-agent when review is required.
- `AuditLog` records for material ingest, task finish, and draft creation.
- notification record for task completion or blockage.

If the task card or SourceMaterial cannot be resolved, finish with `--result blocked`, cite the failed lookup, and do not create source-derived knowledge.

## Local Skill Names

When running inside Codex, the Agent should prefer installed local skills when relevant:

- `lark-doc`: Feishu documents.
- `lark-minutes`: Feishu minutes.
- `lark-vc`: Feishu meeting records.
- `lark-drive`: Feishu drive files and downloads.
- `pdf`: PDF extraction and rendering.
- `documents`: Word/docx processing.
- `spreadsheets`: Excel/CSV/sheet processing.
- `codegraph`: repository code/document structure.
- `context-mode`: large text/file analysis without flooding context.
- `browser` or web reader: web page inspection when permitted.

These local skills are execution capabilities. Reusable team capability must still be represented by a ToolAsset or skill-pack reference in the knowledge core.

## Tool Registry Relationship

The registered tool package is:

- `tools/tool.knowledge-material-readers.md`

The ToolAsset records capability and policy. It does not contain secret values, browser cookies, local credentials, or downloaded raw files.

Agent Ring / Agent Workbench should use the ToolAsset and this skill pack to decide whether a local Runner can claim a material extraction task.

## Failure Rules

Block the task when:

- task card cannot be resolved;
- SourceMaterial cannot be resolved;
- source requires login or permission not available to the Runner;
- source looks like it contains secrets;
- file type is unsupported and no fallback is supplied;
- copyright or confidentiality status is unclear for public reuse.

Blocked writeback must include:

- attempted reader;
- error;
- missing permission or missing source;
- what the submitter should provide next.

## Manual Runner Prompt

For short-term operation before Agent Ring is ready:

```txt
你是知识工程 Agent。请接管知识工程任务 <taskId>。
先读取 agents/agent.company-knowledge-core.knowledge-engineering.md。
再读取 docs/agent-team/knowledge-engineering-agent-skill-pack.md。
然后读取任务卡和 SourceMaterial。
按资料类型选择 reader skill，生成 EvidencePacket、TaskResult 和 KnowledgeItem draft。
如果任务或 SourceMaterial 不可解析，写 blocked TaskResult，不要编造知识。
```
