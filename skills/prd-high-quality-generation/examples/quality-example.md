# PRD 高质量生成协议 Quality Example

## Request

- Project: company-knowledge-core
- Task ID: example
- Requested by: human.owner
- Skill: `prd-high-quality-generation`

## Result

产品经理 Agent 已完成内部六工序协议，并输出 PRD、测试用例、验收清单和开发交付包。

## PRD Quality Protocol

- requiredProtocolLevel: full
- requirementClarifier:
  - firstPrinciples: 已明确目标用户、真实问题、产品价值、成功指标。
  - socraticQuestions: 已记录用于暴露关键前提的澄清问题。
  - summary: 已明确目标用户、场景、问题、商业目标、成功指标。
- evidencePackGenerator: 已区分事实、推断、假设、待决策事项。
- productPlanGenerator: 已按完整上线范围输出产品方案。
- adversarialReviewer: 已挑战问题真实性、商业闭环、边界异常和可测性。
- prdQualityChecker: 已确认需求不是技术任务，验收标准可观察。
- deliveryPackGenerator: 已输出测试方向、验收清单和开发 Agent 交付包。

## Quality Gate

- Completeness: 通过。
- Evidence: 通过。
- Testability: 通过。
- Development handoff: 通过。
- Agent boundary: 未新增公司级 Controller 或 Reviewer。
