# Claude Start Prompt Template

Use this template before formal Claude work.

```txt
projectId: <project-id>
agentId: <agent-id>
task: <task>

Before work:
1. Run `zhenzhi-knowledge sync pull`.
2. Run `zhenzhi-knowledge start --project <project-id> --agent <agent-id> --task "<task>"`.
3. Read `.zhenzhi/context/current.md`.

During work:
- Use only registered ToolAsset records.
- Respect Policy Result, allowed scopes, and allowed tool risk levels.
- Preserve sourceRef for knowledge used.

After work:
1. Run `zhenzhi-knowledge finish --project <project-id> --agent <agent-id> --summary "<summary>"`.
2. State knowledge refs used.
3. State drafts or ToolAsset updates written.
```
