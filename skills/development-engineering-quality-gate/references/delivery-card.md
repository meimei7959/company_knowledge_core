# 研发工程质量门 Delivery Card

## Skill ID

`development-engineering-quality-gate`

## Owner Role

研发 Agent (`development`)

## Allowed Roles

研发 Agent, 架构师 Agent, 测试 Agent, 项目经理 Agent

## Job To Be Done

Prevent low-quality implementation handoff by forcing scoped changes, high-risk-file review, test evidence, and TaskResult quality evidence.

## Execution Contract

1. Load this skill before Development Agent implementation.
2. Run the project quality toolkit before handoff.
3. Attach command, verdict, findings, tests, and next action to TaskResult.
4. Route failures to repair, Architecture Agent, Test Agent, or PM Agent.

## Done Means

- Quality gate verdict is recorded.
- Required tests/checks are recorded.
- High-risk changes have review evidence or blocker routing.
- Handoff target can continue without reconstructing context.
