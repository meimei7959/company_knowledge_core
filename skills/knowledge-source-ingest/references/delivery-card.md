# 知识来源接收与解析 Delivery Card

## Skill ID

`knowledge-source-ingest`

## Owner Role

知识工程 Agent (`knowledge-engineering`)

## Allowed Roles

知识工程 Agent

## Source References

- Company standard: `docs/agent-team/skill-delivery-standard.md`
- Shared contract: `skills/_shared/skill-output-contract.md`
- Mature package reference: `skills/_shared/references/mature-skill-package.md`
- External references registry: `docs/agent-team/skill-quality-sources.json`

## Job To Be Done

Use this skill when the Agent must perform `知识来源接收与解析` as a repeatable production capability, not as a generic role discussion.

## Trigger Aliases

- `source-classification`
- `source-reader`
- `evidence-packet`

## Execution Contract

1. Confirm the task input matches this skill.
2. Load the shared output contract.
3. Produce the skill output using `templates/output-template.md`.
4. Attach evidence and quality gate result.
5. If blocked, return the failure route with owner and next action.

## Done Means

- Output matches this skill's `SKILL.md`.
- Output follows the shared contract.
- Quality gate is explicit.
- Result can be handed to the next Agent without re-explaining context.
