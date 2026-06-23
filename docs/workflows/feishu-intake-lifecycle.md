# Feishu Intake Lifecycle

## Purpose

Feishu/Lark groups can be used as customer communication channels, team source-material intake channels, and learning-material intake channels.

Core stores communication artifacts, source references, task cards, task results, and reviewable knowledge drafts. Business domains decide how to interpret and use domain material. Learning material is extracted into reusable learning notes, skill notes, patterns, or issue notes before Agent use.

## Lifecycle

```txt
Feishu message, URL, article, video, audio, image, document, package, or file
-> Interaction
-> SourceMaterial
-> ProjectTask / KnowledgeTask
-> scheduler assigns an Agent Ring runner
-> Agent Ring executes through local Codex / Claude / approved model/tool
-> TaskResult + KnowledgeDraft candidates
-> Knowledge Engineering Agent review sub-agent
-> auto observed / clarification / conflict / human approval / reject
-> requester notification
-> stored KnowledgeItem or approved publication
```

## Core Responsibilities

- Bind chat thread to project/customer.
- Preserve message/file source references.
- Preserve URL, file token, storageRef, contentHash, materialType, license, and sensitivity metadata.
- Store materials and interactions.
- Create ProjectTask / KnowledgeTask for materials that require processing.
- Assign or expose the task to Agent Ring runners through scheduler matching.
- Notify submitter that the material was accepted and assigned.
- Provide task context to the selected Agent Ring runner.
- Run Knowledge Engineering Agent review sub-agent to classify the draft route.
- Notify requester when the task is done, blocked, rejected, or needs clarification.
- Store auto-approved observed/draft knowledge after machine review passes.
- Store missing fact records when clarification is required.
- Track confirmations.
- Audit durable writes.

## Agent Responsibilities

Knowledge Engineering Agent extraction sub-agent:

- runs through Agent Ring on a distributed computer when source material is long, sensitive, or project-specific;
- reads the ProjectTask / KnowledgeTask context and linked SourceMaterial;
- uses material-specific extraction output when available instead of treating raw files as knowledge;
- extracts structured KnowledgeDraft candidates;
- preserves project, submitter, sourceRef, confidence, sensitivity, and evidence;
- does not decide whether the draft can be published.

Knowledge Engineering Agent review sub-agent:

- reviews the extracted draft, not the raw chat as the primary object;
- checks classification, required fields, source evidence, duplicate/conflict risk, sensitivity, and readability;
- decides whether the draft is `auto_observed`, `clarification_required`, `conflict_required`, `human_approval_required`, or `reject`;
- writes ReviewRecord and AuditLog;
- creates the approval document only when human approval is required.

## Domain Responsibilities

- Decide what information is missing.
- Prepare customer-facing questions.
- Generate domain deliverables after enough context exists.

## Meeting Note Intake

Default meeting note flow:

```txt
User sends Feishu minutes/doc/card
-> Agent Hub detects material intake
-> Agent Hub registers SourceMaterial with original link, submitter, project, permission, and snapshot/export when possible
-> Agent Hub creates KnowledgeTask
-> submitter receives taskId and current status
-> scheduler matches an Agent Ring runner by capability and permission
-> Agent Ring claims task and receives context
-> local Codex / Claude / model summarizes, structures, cites evidence, and writes KnowledgeItem draft
-> Agent Ring finishes task with TaskResult
-> Knowledge Engineering Agent review sub-agent gates the draft
-> submitter is notified with done/blocked/rejected/needs clarification result
```

The server-side bot should not attempt deep parsing of long meeting notes with a small router model. It should preserve source, create a task, let the scheduler choose a Runner, and make the work traceable.

## Learning Material Intake

Supported examples:

- `学习资料：<URL 或文章内容>`
- `公众号文章：<链接、转发正文、截图或 PDF>`
- `视频资料：<链接或上传文件>`
- `安装包：项目 <项目名称或通用用途>\n<文件、版本、来源、许可、安装说明>`

Default behavior:

- The robot stores the original reference as SourceMaterial.
- The robot creates a KnowledgeTask when the material needs non-trivial parsing or judgment.
- The scheduler assigns an Agent Ring runner with matching capabilities and permissions.
- Agent Ring uses local tools to create a human-readable summary, key points, applicable skills, risk/limitations, and source metadata.
- The local Knowledge Engineering Agent extraction sub-agent turns useful parts into `learning_note`, `skill_note`, `pattern`, or `issue` drafts.
- Low-risk learning notes can be machine-reviewed into `observed/draft` directly.
- Policy changes, verified knowledge, customer commitments, sensitive material, unclear license, high-risk package use, or cross-team rules require human approval.

The robot should not reply with long explanations. It should tell the submitter only: material recognized, missing fields if any, draft route, and whether approval is needed.

## Current SourceMaterial CLI

The central processor now has a generic material intake command. Feishu robot handlers, temporary runners, and Agent Ring can all use the same contract.

Document or meeting note:

```bash
python3 -m zhenzhi_knowledge \
  --root /knowledge \
  material ingest \
  --title "AI Agent 会议纪要" \
  --project agent-hub \
  --submitter ou_xxx \
  --source-ref "https://xcn68awb7dsi.feishu.cn/minutes/xxx" \
  --content-file /tmp/minutes-export.md \
  --create-task
```

Package, model, binary file, or bulky dataset:

```bash
python3 -m zhenzhi_knowledge \
  --root /knowledge \
  material ingest \
  --title "本地模型安装包" \
  --submitter ou_xxx \
  --source-ref "feishu://file/xxx" \
  --storage-ref "workspace://agent-hub/materials/local-model.dmg" \
  --material-type package \
  --create-task
```

The command writes a `SourceMaterial` object and returns:

```json
{
  "sourceRef": "projects/agent-hub/sources/source.xxx.md",
  "sourceId": "source.xxx",
  "taskRef": "projects/agent-hub/tasks/kt-xxx.md"
}
```

HTTP API:

Agent Ring, Feishu bot callbacks, or temporary runners can use the same intake path through the central processor API:

```http
POST /v0/materials/ingest
```

Required fields:

- `sourceRef`: Feishu message URL, minutes URL, file token, Git/blob URL, or other retrievable source reference.
- `submitter`: requester or submitting Agent/Runner.

Common optional fields:

- `title`
- `projectId`
- `materialType`
- `storageRef`
- `content`
- `license`
- `sensitivity`
- `extractionTool`
- `extractionStatus`
- `createTask`
- `assignee`

The API and CLI share the same safety gate:

- obvious secret-like content is rejected before write;
- very large inline text is rejected unless `storageRef` is provided;
- binary/package/model/dataset material stores reference, hash, metadata, and review task, not raw payload text.

Rules:

- Text-like material may include original text in the `SourceMaterial` body.
- Binary, package, model, and bulky dataset material keeps only source reference, storage reference, type, sensitivity, and content hash in markdown.
- Every derived KnowledgeItem must cite the `SourceMaterial` and keep the original source path available.
- `--create-task` creates a `KnowledgeTask` for local Agent Ring processing.
- Task result should include summary, structured draft knowledge, source refs, evidence refs, tests/checks, and next actions.
- The bot should notify submitter of task creation, not pretend the material is already reusable knowledge.

Completion standard for intake:

- SourceMaterial exists and has `sourceRef`, `storageRef` or original text, `contentHash`, `materialType`, `sensitivity`, `extractionTool`, and `extractionStatus`.
- A non-trivial material has a linked KnowledgeTask.
- TaskResult links evidence and any KnowledgeItem draft.
- Knowledge draft includes source, confidence, scope, limits, and original source path.
- Requester receives done, blocked, rejected, or clarification notification after processing.
