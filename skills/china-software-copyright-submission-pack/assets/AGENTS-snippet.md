## 软件著作权材料整理

当用户明确要求整理软著材料，或发布冻结后存在 `.release/softcopyright-ready` 时，调用 `$china-software-copyright-submission-pack`。

Agent 仅允许：

1. 检查 `.softcopyright/` 输入是否完整；
2. 运行构建、测试、路径检查、敏感信息扫描和一致性检查；
3. 运行 `submission_pack.py collect --repo .`；
4. 报告 F-01 至 F-10 的当前状态和缺件；
5. 将工作资料包交给申请负责人。

Agent 严禁：

- 代写或补写拟申报代码、说明书正文、主要功能描述、功能说明或操作步骤；
- 推断权属、开发完成日期、发表日期、开发方式或权利取得方式；
- 代填 `authorship-attestation.toml`；
- 运行 `finalize-human`；
- 生成或修改签名、公章、证照、合同、授权书；
- 声称材料一定通过或已经完成登记。

申请负责人必须在核对提交当日官方申请表和真实 AI 使用情况后，手动运行 `finalize-human`。
