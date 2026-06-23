# AI 使用与人工最终化合规门

## 1. 为什么分成 collect 和 finalize-human

当前公开转载的新版申请表声明使用了宽泛措辞，涉及 AI 编写代码、撰写文档和生成登记申请材料。为了避免 Agent 在未确认事实、未核对最新表单时直接输出“可提交材料”，Skill 实行两阶段流程。

### collect

可由 Agent 调用，只生成内部工作成果：

- Git 快照；
- 源码清单、排除原因和哈希；
- 构建/测试结果；
- 敏感信息和第三方依赖检查；
- 原始截图归档；
- 缺件清单；
- 申报项映射；
- 工作资料包。

`collect` 不生成正式上报 ZIP，也不表示申请人可以作出任何官网声明。

### finalize-human

只允许申请负责人在终端手动调用。调用前应：

1. 打开提交当日的官方申请表；
2. 阅读当前声明和经办人要求；
3. 核对拟申报软件代码、说明书、功能说明和登记材料的真实形成过程；
4. 对存在疑问的事项向登记机构或专业人员核实；
5. 根据事实填写 `authorship-attestation.toml`；
6. 确认所有拟申报叙述内容由人独立完成且与真实软件一致。

## 2. 配置字段

```toml
[attestation]
reviewed_current_official_form = true
code_ai_used = "no"
document_ai_used = "no"
registration_material_ai_used = "no"
manual_human_authored = true
feature_evidence_human_authored = true
application_text_human_authored = true
confirmed_by = "申请负责人姓名"
confirmed_on = "YYYY-MM-DD"
notes = ""
```

字段值必须忠实反映事实。Agent 不得替人填写，也不得把 `yes` 或 `unknown` 改为 `no`。

## 3. 判定

- 任一 AI 使用字段为 `yes`：`INTERNAL_ONLY_AI_USE`；正式技术件不复制到上报区，不生成正式 ZIP。
- 任一 AI 使用字段为 `unknown`、未核对当前表单或缺人工确认：`READY_FOR_HUMAN_COMPLETION`。
- 三项均为 `no`，且全部人工确认完成：AI 门通过；仍需满足材料、构建和一致性条件。

该判定是 Skill 的保守工作流，不是对申请表或著作权法的法律意见。
