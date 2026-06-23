# Knowledge Graph Management

Knowledge graph capability is a management layer over the existing knowledge engineering objects. It is not a separate source of truth and does not replace Project, ProjectTask, TaskResult, SourceMaterial, KnowledgeItem, AgentRun, ToolAsset, Decision, Policy, AuditLog, or Review records.

The first-stage rule is relation-first: every important object should carry parseable references, and every automated relationship must be explainable from those references or from reviewed evidence.

## Purpose

The graph answers operational questions that plain search cannot answer well:

- Which projects, tasks, tools, agents, and knowledge items are affected by a changed ToolAsset, repo commit, SourceMaterial, Policy, or Decision?
- Which original material and task execution produced a reusable conclusion?
- Which AgentRun used which knowledge and tools, and what result or issue followed?
- Which stale candidates should be created after a project status, tool version, source material, or decision changes?
- Which facts, lessons, and customer deliverables depend on the same evidence chain?

## Graph Layers

### Object Graph

The object graph links managed records:

```txt
Project -> hasTask -> ProjectTask / KnowledgeTask
ProjectTask -> usesSource -> SourceMaterial
ProjectTask -> assignedTo -> AgentRunner
TaskResult -> resolves -> ProjectTask
TaskResult -> produced -> KnowledgeItem
KnowledgeItem -> derivedFrom -> SourceMaterial
KnowledgeItem -> supportedBy -> TaskResult / AgentRun
AgentRun -> used -> KnowledgeItem
AgentRun -> used -> ToolAsset
Decision -> affects -> Project / ToolAsset / Agent / KnowledgeItem
Policy -> governs -> Agent / ToolAsset / Project / data scope
ConflictRecord -> affects -> KnowledgeItem / Decision / SourceMaterial
EvalRun -> evaluates -> Agent / Prompt / ToolAsset
AuditLog -> recordsChangeTo -> any managed object
```

### Code Reference Graph

Full source code remains in Git repositories. The knowledge core stores only code references that matter to governance and evidence:

```txt
ToolAsset -> implementedIn -> repoRef / commitRef / entrypoint
KnowledgeItem -> referencesCode -> repoRef / path / commitRef / symbol
TaskResult -> changedCode -> repoRef / commitRef / pullRequestRef
AgentRun -> touchedCode -> codeRefs
```

Static code analysis tools may generate local visualizations, but their output becomes reusable team knowledge only when summarized into managed records with sourceRef, confidence, and review status.

### Process Graph

The process graph connects intake, execution, review, notification, and publication:

```txt
Interaction -> created -> SourceMaterial
SourceMaterial -> opened -> KnowledgeTask
KnowledgeTask -> claimedBy -> AgentRunner
AgentRunner -> executedBy -> Agent
Agent -> wrote -> TaskResult / AgentRun
TaskResult -> proposed -> KnowledgeItem draft
ReviewRecord -> reviewed -> KnowledgeItem / ToolAsset / Policy
NotificationRecord -> notified -> requester / assignee / owner
```

### Access Graph

The access graph makes permission filtering explainable:

```txt
Agent -> allowedIn -> Project
Agent -> allowedToUse -> ToolAsset
Agent -> allowedToRead -> Knowledge scope / SourceMaterial scope
Policy -> requiresApprovalFor -> high-risk tool / customer_confidential / verified publish
```

Context pack generation must use this graph to explain why a record was included, excluded, or requires approval.

## KnowledgeGraphEdge

`KnowledgeGraphEdge` is the normalized relation record used by indexes, API exports, graph views, impact analysis, stale checks, and audit queries. It may be materialized in PostgreSQL/API storage or exported from Markdown/YAML records.

Key fields:

- edgeId
- fromRef
- relation
- toRef
- sourceRef
- evidenceRefs
- confidence
- status
- owner
- generatedBy
- observedAt
- updatedAt
- sensitivity
- auditRefs

Rules:

- Edges are derived from managed objects or explicitly declared by reviewed records.
- Edges are not standalone truth. The source object and evidence decide truth.
- Sensitive edges inherit the strictest sensitivity of either endpoint or evidence.
- Edges involving secret values are prohibited because secret values must not enter knowledge files, indexes, graph exports, or AuditLog正文.
- Automated edge extraction may create `draft` or `observed` edges; verified operational meaning still follows the linked objects' review status.
- Deleting or changing an edge must be auditable.

## GraphSnapshot

`GraphSnapshot` is an export artifact for visualization, impact review, API sync, or offline audit. It is regenerated from source records and indexes.

Key fields:

- snapshotId
- generatedAt
- generator
- scope
- includedTypes
- nodeCount
- edgeCount
- sourceIndexRef
- outputRef
- sensitivity
- auditRef

Rules:

- A snapshot is read-only evidence of graph state at one time.
- Snapshots must not contain secret values.
- Customer-confidential snapshots require project or customer scope and must not be published to company-wide graph views.
- Snapshots are disposable; source records remain the durable truth.

## Lifecycle

1. Intake registers SourceMaterial, ProjectTask, Interaction, or other source records with parseable references.
2. Execution writes TaskResult and AgentRun with contextRefs, sourceMaterialRefs, evidenceRefs, knowledgeRefs, toolsUsed, and codeRefs.
3. Extraction creates KnowledgeItem drafts and candidate edges.
4. Knowledge Engineering Agent review sub-agent checks structure, evidence, sensitivity, duplicates, conflicts, and graph impact.
5. Human review is required when the graph relationship changes verified knowledge, approved tools, active policies, permissions, security rules, customer commitments, or cross-team standards.
6. Indexing materializes edges for search, impact analysis, stale detection, and context pack generation.
7. API or CLI export produces GraphSnapshot for visualization or downstream analysis.

## Minimum Implementation

The minimum useful graph capability is not a graph database. It is:

- consistent object references in frontmatter and body fields;
- a graph-edge extractor from Markdown/YAML plus PostgreSQL index records;
- `zhenzhi-knowledge graph export` to emit nodes and edges as JSON;
- `zhenzhi-knowledge graph impact <ref>` to show affected objects before review or publication;
- stale detection that uses graph edges before marking candidates;
- context pack explanations that include relation reasons.

Graph database storage can wait until API usage, multi-team scale, or query complexity justifies it.

## Current CLI Contract

The current implementation materializes graph edges from managed markdown object frontmatter. It does not require a graph database.

Export:

```bash
python3 -m zhenzhi_knowledge --root /knowledge graph export --actor agent.company-knowledge-core.knowledge-engineering
```

Result:

- rewrites generated edge objects under `graph/edges/`;
- writes one snapshot under `graph/snapshots/`;
- prints a JSON `GraphSnapshot`;
- stores the snapshot as `observed`, because it is generated evidence, not verified knowledge;
- creates AuditLog records for edge rebuild and snapshot export.

Impact:

```bash
python3 -m zhenzhi_knowledge --root /knowledge graph impact projects/agent-hub/sources/source.xxx.md --actor agent.company-knowledge-core.knowledge-engineering
```

Result:

- prints incoming edges, outgoing edges, and directly affected refs;
- reads current object references by default and does not rewrite `graph/edges/`;
- creates an AuditLog record for the impact inspection.

Use `--rebuild` only when the caller explicitly wants to refresh generated edge files before impact analysis:

```bash
python3 -m zhenzhi_knowledge --root /knowledge graph impact projects/agent-hub/sources/source.xxx.md --actor agent.company-knowledge-core.knowledge-engineering --rebuild
```

HTTP API:

```http
POST /v0/graph/export
POST /v0/graph/impact
```

`/v0/graph/export` rebuilds generated edge files and writes a `GraphSnapshot`.
`/v0/graph/impact` is read-only by default; pass `{"rebuild": true}` only for an intentional refresh.

Generated edges are stored as `KnowledgeGraphEdge` objects with:

- `fromRef`
- `relation`
- `toRef`
- `sourceRef`
- `evidenceRefs`
- `confidence`
- `status`
- `sensitivity`
- `auditRefs`

Currently extracted relations include project membership, task membership, source usage, evidence refs, output refs, knowledge refs, notification refs, runner assignment, tool usage, and access-reference requirements.

Context packs now include `inclusionReason` for retrieved items. When a graph relation explains inclusion, the reason uses this shape:

```txt
inclusionReason: graph:<relation>:<related-ref>
```

Fallback remains:

```txt
inclusionReason: retrieval_match
```

## Completion Standard

Graph phase one is considered complete when:

- `zhenzhi-knowledge graph export` produces `GraphSnapshot` JSON and markdown snapshot.
- `graph/edges/*.md` contains generated `KnowledgeGraphEdge` records.
- `zhenzhi-knowledge graph impact <ref>` returns incoming, outgoing, and affected refs without rewriting graph files unless `--rebuild` is used.
- Generated graph records contain no secret values.
- Context packs can show at least one graph-based `inclusionReason`.
- Tests cover export, impact, audit, and context reason generation.
