# 项目任务拆解 Quality Example

## Acceptable Result Shape

The Agent uses `project-task-decomposition` only for tasks matching its triggers, names the input, produces a concrete artifact, includes evidence, runs the quality gate, and states the next handoff.

## Rejection Example

Reject or reroute when the task lacks required input, asks this skill to exceed its role boundary, contains secrets, or needs a different Agent.
