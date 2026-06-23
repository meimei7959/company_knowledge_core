---
name: china-software-copyright-submission-pack
description: 知识工程 Agent 在项目版本冻结、上线验收或用户要求申请中国软件著作权时使用；用于整理软著工作资料包、正式申报项映射、源程序鉴别材料、文档鉴别材料、截图和权属材料缺件清单。项目经理 Agent 只负责触发和追踪，不负责代写或最终确认材料。
---

# 中国软件著作权申报资料包

## Purpose

把冻结版本的软件或 Agent 产品整理为软著申请工作资料包，建立正式申报项、内部佐证项、缺件项和责任人的映射。

本 Skill 的主责是知识工程 Agent。项目经理 Agent 在上线计划中创建和追踪软著材料任务；产品、研发、测试、运营提供各自证据；申请负责人或法务/行政负责人做最终权属、申请表和 AI 使用声明确认。

## Triggers

- 用户提到软著、软件著作权、软件版权、著作权登记、源程序前后各 30 页、用户手册、操作说明书、设计说明书、申请表、营业执照、权属证明、上架权属证明。
- 项目进入 Release Candidate、版本冻结、上线验收或完整上线关闭节点。
- 某个 Agent、工具、平台模块要作为独立软件产品申请软著。
- 项目经理 Agent 的上线门禁发现缺少知识产权/软著材料包。

## Inputs

- 项目 ID、软件全称、简称、版本号、申请负责人、软件边界。
- 冻结 Git commit、源码范围、构建/测试命令、运行截图。
- 产品经理 Agent 提供的软件定位、功能边界和主要功能清单。
- 研发 Agent 提供源码路径、构建信息、第三方依赖说明。
- 测试 Agent 提供验收记录、测试报告、截图来源说明。
- 申请负责人提供的申请表、主体证明、权属证明、AI 使用事实确认。
- `.softcopyright/` 下的配置、说明书、功能证据和公司材料映射。

## Workflow

1. 项目经理 Agent 在 PRD 定稿、项目计划或 Release Candidate 节点判断是否需要软著任务。
2. 若需要，项目经理 Agent 创建 `software_copyright_material_pack` 任务，主责为知识工程 Agent。
3. 知识工程 Agent 初始化 `.softcopyright/` 模板，只创建结构，不填写法律事实或实质性说明书正文。
4. 产品、研发、测试、申请负责人补齐各自材料。
5. 知识工程 Agent 运行 `collect`，只做路径检查、源码清单、哈希、敏感信息扫描、截图归档、缺件识别和内部工作包整理。
6. 知识工程 Agent 输出工作资料包、申报材料一一对应表、缺件清单、AI 使用与人工最终化提示。
7. 申请负责人核对提交当日官方申请表、权属事实、AI 使用声明和签章材料。
8. 只有申请负责人确认后，才可手动运行 `finalize-human` 生成正式上报候选包。

可用脚本：

```bash
python3 skills/china-software-copyright-submission-pack/scripts/submission_pack.py init --repo <repo>
python3 skills/china-software-copyright-submission-pack/scripts/submission_pack.py collect --repo <repo>
python3 skills/china-software-copyright-submission-pack/scripts/submission_pack.py finalize-human --repo <repo>
```

Agent 默认只允许执行 `init` 和 `collect`。`finalize-human` 必须由申请负责人在人工核对后执行。

## Outputs

- 软著工作资料包。
- 申报材料一一对应表。
- 正式申报项缺件清单。
- 源程序鉴别材料候选件。
- 文档鉴别材料候选件。
- 截图、功能、代码映射表。
- AI 使用与人工最终化检查记录。
- 项目经理 Agent 可读取的上线门禁状态。

## Quality Gate

- 软件名称、版本、源码范围、说明书、截图和申请表字段必须一致。
- 源程序材料只能来自真实第一方冻结源码，不能由 Agent 生成或补写。
- 用户手册、功能说明、操作步骤、权属事实和申请表声明必须由人确认。
- 公司证照、合同、授权、代理材料只能由申请人提供，Agent 只能归档和检查路径。
- 存在 secret、真实隐私数据、路径错误、构建失败、截图缺失或 AI 声明未确认时，不得生成可提交正式包。
- 正式 ZIP 不得混入内部复核材料、构建日志、字段交接单或未要求上传的截图册。

## Failure Routes

- 缺产品边界或功能清单：退回产品经理 Agent。
- 缺源码范围、构建或依赖说明：退回研发 Agent。
- 缺测试报告或真实截图：退回测试 Agent。
- 缺申请表、主体证明、权属材料或 AI 使用事实确认：交申请负责人/法务/行政。
- 发现敏感信息或第三方代码边界不清：阻塞并通知项目经理 Agent 与申请负责人。
- 任务进入上线关闭但材料包未完成：项目经理 Agent 创建阻塞项或延期决策。

## References

- `references/official-requirements.md`
- `references/submission-material-map.md`
- `references/input-contract.md`
- `references/output-contract.md`
- `references/ai-compliance-gate.md`
- `references/source-material-spec.md`
- `references/manual-spec.md`
- `references/applicant-materials-spec.md`
