# PRD 高质量生成协议 Delivery Card

## 使用者

产品经理 Agent。

## 适用任务

- 产品方案。
- PRD。
- 测试用例。
- 验收标准。
- 开发 Agent 交付包。

## 必交付证据

默认 `light`：

- `prdQualityProtocol.requiredProtocolLevel = light`
- `prdQualityProtocol.requirementClarifier.firstPrinciples`
- `prdQualityProtocol.requirementClarifier.socraticQuestions`
- `prdQualityProtocol.prdQualityChecker`
- `prdQualityProtocol.deliveryPackGenerator`

复杂完整 PRD 使用 `full`，除 light 三项外还需要：

- `prdQualityProtocol.evidencePackGenerator`
- `prdQualityProtocol.productPlanGenerator`
- `prdQualityProtocol.adversarialReviewer`

缺少任一项时，PRD 质量门禁必须失败。

小改动可使用 `none`，但必须提供 `rationale`。

## 禁止事项

- 不新增 Controller、Reviewer 或其他公司级 Agent。
- 不用技术方案替代产品需求。
- 不把没有来源的市场/竞品判断写成事实。
