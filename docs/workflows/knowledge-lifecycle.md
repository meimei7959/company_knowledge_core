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
- Tool documentation.
- AgentRun.

## 2. Draft Extraction

Agent or human creates draft knowledge:

- KnowledgeDraft.
- ToolUpdate draft.
- ProjectUpdate draft.
- Decision draft.

Draft must preserve sourceRef, confidence, owner, and status.

## 3. Review

Human reviewer checks:

- source validity;
- applicability;
- sensitivity;
- conflict with existing knowledge;
- whether knowledge should remain project-scoped or become company-scoped.

Missing information should become `MissingFact` records and can be asked through a bound communication channel such as a Feishu/Lark group.

## 4. Publication

After review:

- KnowledgeItem: draft -> verified.
- ToolAsset: testing -> approved.
- ConflictRecord: open -> resolved.
- Policy: draft -> active.

All publication must write AuditLog.

## 5. Usage

Agent uses knowledge through context pack:

```txt
zhenzhi-knowledge start -> context pack -> Agent work
```

Agent must record used knowledge and tools in AgentRun.

## 6. Writeback

After work:

```txt
Agent work -> zhenzhi-knowledge finish -> AgentRun + draft updates
```

No significant Agent task is complete without writeback.

## 7. Staleness

Knowledge becomes stale when:

- linked tool version changes;
- linked Git commit or implementation changes;
- project status changes;
- source material changes;
- newer decision replaces older knowledge;
- review interval expires.

Stale candidate requires reviewer confirmation before state changes.
