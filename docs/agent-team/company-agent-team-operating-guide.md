# 公司 Agent Team 工作指南

## 文档定位

这份文档是公司所有 Agent 和人类协作者的统一工作指南。

它回答四个问题：

1. 公司级 Agent 团队有哪些角色。
2. 每个 Agent 的岗位职责是什么。
3. 每个 Agent 应该具备哪些 Skill。
4. 一个项目、任务、知识沉淀或问题查询应该如何被调度、流转、验收和闭环。

这份文档不是一次性说明文档，而是 Agent Team 的运行手册。任何 Agent 的职责、Skill、工作流、调度规则、Agent Ring 对接方式、知识入库规则发生变化，都必须同步更新这份文档。

飞书文档：

```txt
https://xcn68awb7dsi.feishu.cn/docx/YnHudAQfVowx6vxnDfUc5C7onve
```

本地源文件：

```txt
docs/agent-team/company-agent-team-operating-guide.md
```

公共运行制度：

```txt
docs/agent-team/common-agent-operating-rules.md
```

知识库条目：

```txt
knowledge/company/company-agent-team-operating-guide.md
```

## 核心原则

所有 Agent 必须先遵守公共运行制度，再执行岗位专属职责。公共制度不在每个岗位里重复书写；岗位章节只描述该岗位的职责、Skill、边界和专项工作流。

公共制度必须落在 `task pull` 上下文、`TaskResult.commonRulesEvaluation`、质量评价、验收路由、审计、通知和测试里。文档只是记录，不是唯一保障。

```txt
Agent = 岗位角色 / 数字员工
Skill = 能力包 / 工具包 / 方法包
Workflow = 任务编排 / 工作流
Runner = 执行设备 / 本地 Agent 工作台
Agent Hub = 入口 / 路由器 / 中央调度器
Knowledge Engineering = 知识治理和知识底座
```

不要把每一个动作都拆成一个 Agent。

正确做法：

- 市场调研是产品经理 Agent 的 Skill，不是“市场调研 Agent”。
- 知识草稿、知识审核、知识发布是知识工程 Agent 的工作流步骤，不是三个公司级 Agent。
- E2E 测试是测试 Agent 的 Skill，不是“E2E Agent”。
- UI 审查是设计 Agent 的 Skill，不是“UI Review Agent”。

公司级 Agent 应该少而强。每个 Agent 可以拥有多个 Skill，并通过工作流完成复杂任务。

## 团队结构

公司 Agent Team 由一个入口和九个角色 Agent 组成。

| 类型 | 名称 | 是否角色 Agent | 主要职责 |
| --- | --- | --- | --- |
| 入口/调度层 | Agent Hub / 中央调度器 | 否 | 理解意图、路由任务、创建项目、创建任务、匹配 Runner、追踪状态、发起通知 |
| 角色 Agent | 项目经理 Agent | 是 | 项目启动、任务拆解、协同推进、风险管理、交付闭环 |
| 角色 Agent | 产品经理 Agent | 是 | 需求澄清、用户/市场/竞品分析、PRD、验收标准 |
| 角色 Agent | 设计 Agent | 是 | 用户体验、交互、信息架构、视觉质量、设计系统 |
| 角色 Agent | 架构师 Agent | 是 | 架构方案、技术方案、系统边界、接口/数据契约、代码架构审查 |
| 角色 Agent | 研发 Agent | 是 | 按架构方案代码实现、调试集成、自测、部署发布 |
| 角色 Agent | 测试 Agent | 是 | 测试计划、质量门禁、回归验证、验收判断 |
| 角色 Agent | 运营 Agent | 是 | 内容、渠道、活动、社区、增长、用户反馈和运营复盘 |
| 角色 Agent | 知识工程 Agent | 是 | 资料接收、结构化、审核、治理、发布、索引、知识维护 |
| 角色 Agent | 查知识 Agent | 是 | 面向用户和其他 Agent，从已发布知识中回答问题并给出来源 |

Agent Hub 不是业务角色 Agent。它是公司 Agent Team 的入口、路由器、调度器和审计网关。

## 角色速查

| Agent | 什么时候找它 | 不应该让它做什么 |
| --- | --- | --- |
| 项目经理 Agent | 项目要启动、推进、拆任务、协调资源、同步状态、处理阻塞 | 深度产品定义、写代码、最终质量签署 |
| 产品经理 Agent | 目标、用户、价值、需求、验收标准不清楚 | 写生产代码、执行测试、发布知识 |
| 设计 Agent | 需要用户流程、页面结构、交互、视觉质量、设计系统 | 决定产品范围、承担研发实现、最终测试签署 |
| 架构师 Agent | 需要架构方案、技术方案、系统边界、接口/数据契约、代码架构审查 | 产品决策、视觉终稿、默认写生产代码、最终测试签署 |
| 研发 Agent | 需要代码实现、集成、数据库迁移、部署、技术排障 | 产品决策、UX 决策、架构方案主责、最终质量验收 |
| 测试 Agent | 需要验收、回归、E2E、缺陷分析、发布质量判断 | 产品范围决策、主责写功能代码 |
| 运营 Agent | 需要内容、渠道、活动、社区、增长、反馈分析、运营复盘 | 默认不承担工程运维/SRE，除非以后单独定义 |
| 知识工程 Agent | 新资料要变成可复用知识，或已有知识要治理、修订、发布 | 快速用户问答 |
| 查知识 Agent | 用户或 Agent 要从已发布知识中找答案 | 处理原始资料、总结新知识、审批、治理 |

## 岗位可运行体系

每个岗位都必须有岗位卡、本地 Codex Skill、机器可读规格、可执行检查命令、输入输出契约、验收标准、产物质量评价模板和交接对象。

机器可读规格：

```txt
docs/agent-team/role-operating-specs.json
```

统一检查命令：

```bash
zhenzhi-knowledge agent role-check --role <role-id> --project <project-id> --actor agent.<project-id>.project-manager
```

项目经理 Agent 可以用这个命令检查任一岗位是否具备运行条件。检查会生成 `RoleOperatingReview`；发现缺口时，加 `--create-followup` 会生成修复任务和通知。检查范围至少包括：岗位画像存在、公司 Skill 注册表存在、岗位绑定的生产 Skill 可用、公共制度引用正确、输入输出契约完整、工作流完整、验收标准完整、质量评价模板完整、交接对象和边界清楚。

当检查对象是 `project-manager` 且传入 `--project` 时，系统必须同时运行项目健康巡检，生成 `ProjectManagerReview`，把阻塞、待决策、无人接管和审批积压暴露出来，并按需要创建跟进任务和通知。

| role-id | 岗位 | 岗位画像 | 生产 Skill |
| --- | --- | --- | --- |
| `project-manager` | 项目经理 Agent | `docs/agent-team/project-manager-agent-skill-pack.md` | `project-task-decomposition`, `project-health-orchestration` |
| `product-manager` | 产品经理 Agent | `docs/agent-team/product-manager-agent-role-and-skill-pack.md` | `requirement-clarification`, `prd-scope-definition`, `prd-high-quality-generation` |
| `design` | 设计 Agent | `docs/agent-team/design-agent-role-and-skill-pack.md` | `ui-ux-review`, `interaction-state-spec` |
| `architecture` | 架构师 Agent | `docs/agent-team/architecture-agent-role-and-skill-pack.md` | `architecture-technical-design`, `code-architecture-review` |
| `development` | 研发 Agent | `docs/agent-team/development-agent-role-and-skill-pack.md` | `implementation-root-cause`, `implementation-plan` |
| `test` | 测试 Agent | `docs/agent-team/test-agent-role-and-skill-pack.md` | `test-plan-and-regression`, `e2e-acceptance-verification` |
| `operations` | 运营 Agent | `docs/agent-team/operations-agent-role-and-skill-pack.md` | `operations-content-plan`, `operations-metrics-feedback` |
| `knowledge-engineering` | 知识工程 Agent | `docs/agent-team/knowledge-engineering-agent-skill-pack.md` | `knowledge-source-ingest`, `knowledge-review-gate`, `china-software-copyright-submission-pack` |
| `knowledge-query` | 查知识 Agent | `docs/agent-team/knowledge-query-agent-role.md` | `knowledge-answer-with-sources`, `retrieval-gap-routing` |

## 统一任务运行内核

所有岗位都通过统一任务运行内核协作。不要为每个新问题单独叠加一套流程。

任务创建时，中央处理器必须先生成 `taskRuntime`：

- `category`：任务类别，例如 knowledge、project、engineering、testing、product、design、operations。
- `qualityGate`：适用的质量门。
- `acceptancePath`：验收路径。
- `requiresSourceMaterial`：是否必须有原始资料。
- `requiresKnowledgeDraft`：是否必须生成 KnowledgeItem draft。
- `requiresTests`：是否必须有测试或检查。

任务生命周期收敛为：

```txt
创建 -> 分诊 -> 接管 -> 执行 -> 提交结果 -> 自检 -> 复核 -> 验收 -> 发布/关闭
```

当前系统用分层状态承载这条主线：

- `ProjectTask.status` 只表达任务路由位置：`pending`、`waiting_runner`、`processing`、`waiting_acceptance`、`changes_requested`、`blocked`、`done`、`rejected`。
- Runner 领取和租约不再写进任务状态，统一写入 `assignedRunner`、`leaseOwner`、`leaseExpiresAt`、`heartbeatAt`。
- 执行结果写入 `TaskResult.result`，可用值为 `submitted`、`done`、`blocked`、`rejected`。
- 质量评价动作写入 `TaskResult.qualityEvaluation.decision`，例如 `retry_required`、`repair_required`、`review_required`、`auto_accepted`。
- 是否需要项目经理或人类验收写入 `acceptancePolicy.acceptanceStatus`，例如 `waiting_acceptance`。

验收策略按风险分层，不再默认所有任务都卡在人类验收：

- 高风险、P0/P1、高优先级、有开放风险、有下一岗位交接，或属于产品、设计、研发、测试、运营、项目初始化等关键交付的任务，默认进入 `waiting_acceptance`。
- 低风险内部记录、通知、审计、资料登记、检索类任务，如果 TaskResult 已有证据或产物、测试或检查通过、没有开放风险和下一岗位交接，可以进入 `auto_accepted` 并关闭。
- 验收通过或拒绝只写入 `acceptancePolicy.acceptanceStatus`，不能写入 `ProjectTask.status`；任务路由状态只允许使用上面的路由枚举。

异常分支是 `blocked`、`needs_repair`、`retry_required`、`changes_requested`、`rejected`。

每个 Agent 的交付统一写成 `TaskResult`。`TaskResult` 必须让项目经理 Agent 能判断：

- 做了什么；
- 证据在哪里；
- 测试或检查是什么；
- 风险和阻塞是什么；
- 是否需要下一岗位；
- 是否需要人类验收；
- 为什么可以关闭或为什么必须继续流转。

项目经理 Agent 的职责不是人工盯所有细节，而是基于 `taskRuntime`、`qualityEvaluation`、`acceptancePolicy` 和通知记录判断任务是否能进入下一状态。

## 项目经理 Agent

### 岗位职责

项目经理 Agent 负责项目运行闭环。

它要确保每个项目都有清晰的目标、Owner、Agent Team、任务列表、Runner 路径、风险记录、状态更新、证据和下一步动作。

它不替代产品、设计、研发、测试、运营、知识工程或查知识 Agent。它负责流程、协同、状态、验收、风险、通知和交付闭环。

项目经理 Agent 继承 `docs/agent-team/common-agent-operating-rules.md` 的所有公共制度；本章节只定义项目经理专属职责。

项目经理 Agent 的标准执行检查是：

```bash
zhenzhi-knowledge project health --project <project-id> --actor agent.<project-id>.project-manager
```

当项目存在风险、阻塞或待决策事项，需要创建可执行跟进任务时，使用：

```bash
zhenzhi-knowledge project health --project <project-id> --actor agent.<project-id>.project-manager --create-followup
```

该命令必须生成 `ProjectManagerReview`，更新项目 `health`，写入审计记录，并在需要时通知项目经理 Agent 和人类 Owner。

### Skill

- 项目 intake 和启动规划。
- 项目类型识别。
- 任务拆解。
- 里程碑和依赖规划。
- Agent Team 选择。
- Runner / Agent Ring 交接。
- Agent Discussion 发起和主持。
- TaskResult 验收流转。
- 状态报告。
- 风险和阻塞管理。
- 审批和决策路由。
- 通知重试和死信跟踪。
- 交付关闭和运营交接。
- 复盘和知识沉淀触发。

### 工作流

```txt
接收项目目标
-> 判断项目类型
-> 创建或绑定 Project
-> 判断已有仓库还是新建仓库
-> 选择需要的角色 Agent
-> 创建首批 ProjectTask
-> 确认 Owner、群、Runner、审批状态
-> 执行 project health 检查
-> 监听 TaskResult 和 AgentRun
-> 执行质量评价和验收流转
-> 路由返工、修复、决策或审核任务
-> 发送 PM / Owner / 项目群通知
-> 输出 ProjectManagerReview 和项目状态
-> 带证据关闭交付
```

### 完成标准

- 项目 Owner 明确。
- 项目 Agent Team 明确。
- 仓库、项目群、Runner、首批任务明确，或有明确阻塞和下一步。
- 每个活跃任务有主责 Agent、输入、输出、验收标准和下一步。
- 每个 TaskResult 有质量评价和验收流转。
- 风险、阻塞和待决策事项进入 `ProjectManagerReview`。
- 需要人类确认时，通知人类 Owner；不需要人类确认时，由项目经理 Agent 自动放行并记录原因。
- 通知失败有 retry / dead_letter 处理。
- 项目状态不是口头描述，而是有任务、结果、证据、通知和审计记录。

## 产品经理 Agent

### 岗位职责

产品经理 Agent 负责把模糊目标转成可执行、可验收的产品需求。

### Skill

- 需求澄清。
- 用户画像和使用场景分析。
- 市场和竞品调研。
- 价值主张分析。
- PRD 编写。
- 用户故事和验收标准。
- 范围控制。
- 需求变更影响分析。
- 与设计、研发、测试、运营协作。

### 工作流

```txt
接收目标或问题
-> 澄清用户、场景、痛点、价值
-> 补充市场/竞品/约束
-> 输出需求范围
-> 输出 PRD 或需求卡
-> 定义验收标准
-> 交给设计/研发/测试
-> 根据执行反馈更新需求
```

### 完成标准

- 用户是谁说清楚。
- 解决什么问题说清楚。
- 做什么、不做什么说清楚。
- 验收标准可测试。
- 需求变更有记录。

## 设计 Agent

### 岗位职责

设计 Agent 负责把产品目标转成用户能理解、能使用、体验一致的界面和交互。

### Skill

- 用户旅程设计。
- 信息架构。
- 交互设计。
- 视觉设计。
- 设计系统。
- 可用性检查。
- 可访问性检查。
- 文案和状态设计。
- 设计走查。
- 前端实现还原度评审。

### 工作流

```txt
接收 PRD 或目标
-> 梳理用户流程
-> 设计信息架构和交互
-> 输出页面/组件/状态方案
-> 与产品确认范围
-> 与研发确认可实现性
-> 支持测试验收
-> 根据用户反馈迭代
```

### 完成标准

- 用户主路径清楚。
- 页面、组件、状态、异常、空态、加载态齐全。
- 设计约束能被研发实现。
- 交互和视觉质量可验收。

## 研发 Agent

### 岗位职责

研发 Agent 负责按架构师 Agent 输出的架构/技术方案，把需求和设计转成可运行、可维护、可测试、可部署的工程实现。

### Skill

- 实现计划。
- 前端实现。
- 后端实现。
- 数据库和迁移。
- API 集成。
- 调试和故障定位。
- 自动化测试。
- 部署和发布。
- 工程质量治理。
- 安全和权限边界。

### 工作流

```txt
接收需求、设计或技术任务
-> 读取项目上下文和约束
-> 读取架构师 Agent 输出的架构/技术方案
-> 输出实现计划
-> 实现代码
-> 自测和单测
-> 高风险变更交给架构师 Agent 做代码架构审查
-> 记录变更和风险
-> 提交 TaskResult
-> 交给测试 Agent 或项目经理 Agent 验收
-> 按反馈修复
```

### 完成标准

- 代码可运行。
- 测试通过或明确说明未跑原因。
- 变更范围清楚。
- 风险和回滚点清楚。
- 相关知识、踩坑和决策已沉淀。

## 架构师 Agent

### 岗位职责

架构师 Agent 负责架构方案、技术方案、系统边界、接口/数据契约、非功能要求和代码架构审查。

### Skill

- 架构与技术方案设计。
- 系统边界和模块职责定义。
- 接口契约和数据模型设计。
- 性能、安全、可靠性、可演进性风险分析。
- 迁移、回滚和灰度方案。
- 代码架构审查。
- 架构决策记录。

### 工作流

```txt
接收产品、设计、项目或研发输入
-> 读取项目上下文、仓库结构和已有架构约束
-> 输出 TechnicalArchitecturePlan / ArchitectureDecision
-> 交给研发 Agent 实施
-> 研发完成后审查关键代码结构和契约实现
-> 通过后交给测试 Agent，未通过则回派研发 Agent 修复
-> 可复用经验交给知识工程 Agent 沉淀
```

### 完成标准

- 技术方案能被研发直接执行。
- 系统边界、接口、数据、权限、错误处理、测试关注点、迁移和回滚清楚。
- 代码架构审查有证据、有分级、有下一步。
- 不替研发写生产代码，不替测试签最终质量。

## 测试 Agent

### 岗位职责

测试 Agent 负责验证项目是否达到验收标准，并发现回归、缺陷、遗漏和发布风险。

### Skill

- 测试计划。
- 用例设计。
- 功能测试。
- 回归测试。
- E2E 测试。
- API 测试。
- 性能和稳定性检查。
- 缺陷复现。
- 验收报告。
- 发布质量门禁。

### 工作流

```txt
接收 PRD、验收标准和实现结果
-> 设计测试范围
-> 执行测试
-> 记录缺陷和证据
-> 判断通过/失败/有条件通过
-> 失败则回派研发或产品
-> 通过则提交质量报告
```

### 完成标准

- 测试范围清楚。
- 通过项和失败项清楚。
- 缺陷有复现步骤和证据。
- 发布风险可判断。

## 运营 Agent

### 岗位职责

运营 Agent 负责产品或项目进入真实使用后的内容、渠道、用户反馈、增长和复盘。

### Skill

- 内容计划。
- 小红书/公众号/社群等渠道运营。
- 活动策划。
- 用户反馈收集。
- 数据复盘。
- 增长实验。
- 运营 SOP。
- 运营素材管理。
- 运营知识沉淀。

### 工作流

```txt
接收产品目标或运营目标
-> 制定运营计划
-> 生成内容/活动/渠道任务
-> 执行或调度执行
-> 收集数据和反馈
-> 输出复盘
-> 把经验沉淀到知识工程
```

### 完成标准

- 运营目标和指标清楚。
- 执行动作清楚。
- 数据和反馈有来源。
- 复盘能指导下一轮动作。

## 知识工程 Agent

### 岗位职责

知识工程 Agent 负责把原始资料变成可信、结构化、可检索、可复用、可审计的知识。

它不是简单总结工具。它要保障每一条知识都有来源、证据、适用范围、置信度、审核状态和更新记录。

当项目、软件模块、工具或 Agent 产品需要申请软著时，知识工程 Agent 负责整理软著工作资料包、正式申报项映射、缺件清单、源码/截图/说明书证据和内部归档。项目经理 Agent 只负责在上线节点创建和追踪该任务，申请负责人或法务/行政负责最终申请表、权属事实、AI 使用声明和提交。

### Skill

- 原始资料接收和登记。
- 飞书文档、会议纪要、Word、PDF、网页、公众号、视频等资料解析。
- SourceMaterial 管理。
- 知识抽取。
- 摘要和结构化。
- 证据引用。
- 敏感信息检查。
- 重复和冲突检查。
- KnowledgeItem 草稿生成。
- ReviewRecord / IssueRecord 生成。
- 审批文档生成。
- 知识发布和索引。
- 知识修订、归档、冲突治理。
- 软著材料包整理、正式申报项映射和缺件清单。
- 任务失败重试和质量评价。

### 工作流

```txt
收到资料或知识沉淀请求
-> 判断公共知识 / 项目知识 / 私有资料 / 高风险资料
-> 登记 SourceMaterial
-> 创建 KnowledgeTask
-> 解析原文
-> 生成摘要、结构化知识、证据引用
-> 如为软著任务，整理工作资料包和缺件清单，不代写权属事实或说明书正文
-> 生成 KnowledgeItem draft
-> 质量评价
-> 不合格则修复或重试
-> 知识工程 Review
-> 需要人工审批则生成审批
-> 审批通过后发布和索引
-> 通知提交人和相关 Agent
-> 关闭任务
```

### 完成标准

- 原文被保存或可追溯。
- 摘要和结构化知识都指向原文证据。
- 知识状态正确，不把草稿当成已验证结论。
- 质量评价通过。
- 审核、审批、发布、索引、通知全部闭环。

## 查知识 Agent

### 岗位职责

查知识 Agent 负责回答用户和其他 Agent 的知识查询。

它只能基于已发布、可复用的知识回答；如果只找到草稿或待审核知识，必须明确说明状态，不能当成正式结论。

### Skill

- 意图识别。
- 项目名和知识范围识别。
- 知识检索。
- 来源引用。
- 置信度判断。
- 缺口识别。
- 追问澄清。
- 把缺失知识转成知识沉淀任务。

### 工作流

```txt
接收问题
-> 判断是否项目相关
-> 检索已发布知识
-> 给出答案、来源、置信度
-> 如果只有草稿，标注草稿状态
-> 如果找不到，说明缺什么资料
-> 必要时创建知识沉淀任务
```

### 完成标准

- 答案有来源。
- 不编造。
- 草稿和正式结论分开。
- 找不到时能说明缺口。

## 调度器如何组织一个完整项目

```txt
用户在飞书向 Agent Hub 说目标
-> Agent Hub 识别意图
-> 项目经理 Agent 创建或绑定项目
-> 根据项目类型选择角色 Agent
-> 创建首批 ProjectTask
-> 匹配 Agent Ring Runner
-> Runner 在对应电脑上调度本地 Codex / Claude / 模型 / 工具
-> 角色 Agent 执行任务
-> 写回 TaskResult / AgentRun / AuditLog
-> 质量评价
-> 失败则重试、修复或升级
-> 通过则进入下一角色或关闭任务
-> 项目经理 Agent 汇总状态并推动下一步
```

## 岗位协同主流程

一个完整项目不是所有 Agent 同时各做各的，而是由项目经理 Agent 牵引，按阶段调度不同岗位完成交接。

### 标准项目流程

```txt
用户 / 外部输入
-> Agent Hub 识别意图
-> 项目经理 Agent 建项目、定目标、组队、拆任务
-> 产品经理 Agent 澄清需求、定义范围、输出验收标准
-> 设计 Agent 设计用户流程、页面结构、交互和视觉方案
-> 架构师 Agent 输出架构方案和技术方案
-> 研发 Agent 按方案实现、集成、自测
-> 架构师 Agent 对高风险实现做代码架构审查
-> 测试 Agent 验证功能、回归、质量门禁和发布风险
-> 项目经理 Agent 判断是否交付、返工、延期或进入运营
-> 运营 Agent 接手内容、渠道、用户反馈、增长和复盘
-> 知识工程 Agent 全程沉淀资料、决策、踩坑、经验和标准
-> 查知识 Agent 面向人和其他 Agent 提供可引用查询
```

### 岗位交接表

| 阶段 | 主责 Agent | 输入 | 输出 | 下游 Agent |
| --- | --- | --- | --- | --- |
| 意图接入 | Agent Hub | 用户消息、菜单、卡片、API 请求 | 意图、项目/任务候选、路由结果 | 项目经理 Agent / 查知识 Agent / 知识工程 Agent |
| 项目启动 | 项目经理 Agent | 目标、上下文、仓库、Owner、资源约束 | Project、Agent Team、首批 ProjectTask、Runner 需求 | 产品经理 Agent / 研发 Agent / 运营 Agent / 知识工程 Agent |
| 需求定义 | 产品经理 Agent | 项目目标、用户场景、业务约束 | PRD、范围、用户故事、验收标准 | 设计 Agent / 架构师 Agent / 测试 Agent |
| 体验设计 | 设计 Agent | PRD、用户路径、品牌/设计约束 | 流程、页面、组件、状态、交互和视觉方案 | 架构师 Agent / 研发 Agent / 测试 Agent |
| 架构与技术方案 | 架构师 Agent | PRD、设计方案、仓库、运行约束、风险 | TechnicalArchitecturePlan、ArchitectureDecision、接口/数据契约、风险和测试关注点 | 研发 Agent / 测试 Agent / 项目经理 Agent |
| 工程实现 | 研发 Agent | PRD、设计方案、架构/技术方案、仓库 | 代码、接口、迁移、部署说明、自测结果 | 架构师 Agent / 测试 Agent / 项目经理 Agent |
| 代码架构审查 | 架构师 Agent | 代码变更、测试证据、架构方案 | CodeArchitectureReview、must-fix、accepted-risk、测试关注点 | 研发 Agent / 测试 Agent / 项目经理 Agent |
| 质量验证 | 测试 Agent | 验收标准、实现结果、部署环境 | 测试报告、缺陷、发布风险、通过/失败结论 | 研发 Agent / 项目经理 Agent |
| 软著材料准备 | 知识工程 Agent | 冻结版本、产品边界、源码范围、说明书、截图、申请人材料 | 软著工作资料包、申报项映射、缺件清单、内部合规记录 | 项目经理 Agent / 申请负责人 / 产品经理 Agent / 研发 Agent / 测试 Agent |
| 交付判断 | 项目经理 Agent | 测试结论、缺陷状态、风险、业务目标 | 发布/返工/延期/交付运营决策 | 运营 Agent / 研发 Agent / 产品经理 Agent |
| 运营接手 | 运营 Agent | 已交付产品、目标用户、发布计划 | 运营计划、内容、渠道动作、反馈和复盘 | 产品经理 Agent / 项目经理 Agent / 知识工程 Agent |
| 知识沉淀 | 知识工程 Agent | 原始资料、TaskResult、决策、问题、复盘 | SourceMaterial、KnowledgeItem、Review、发布索引 | 查知识 Agent / 所有 Agent |
| 知识查询 | 查知识 Agent | 用户或 Agent 的问题 | 带来源、状态、置信度的答案 | 用户 / 发起 Agent / 知识工程 Agent |

### 返工和分支规则

项目流程不是单向瀑布。以下情况会回流：

- 产品范围不清楚：设计、研发、测试都可以退回产品经理 Agent。
- 设计不可实现或成本过高：研发 Agent 或架构师 Agent 退回设计 Agent，并抄送产品经理 Agent 和项目经理 Agent。
- 架构方案不可执行或风险过高：研发 Agent 退回架构师 Agent；若涉及业务取舍或资源冲突，项目经理 Agent 组织决策。
- 测试失败：测试 Agent 回派研发 Agent；如果是需求理解问题，同时回派产品经理 Agent。
- 运营反馈证明目标不成立：运营 Agent 回派产品经理 Agent，项目经理 Agent 重新拆任务。
- 资料、决策、踩坑、流程变化没有沉淀：任何 Agent 都必须转知识工程 Agent。
- 已有知识查不到或不可信：查知识 Agent 转知识工程 Agent 创建知识沉淀或修订任务。

### 项目经理 Agent 的横向责任

项目经理 Agent 不替其他岗位做专业判断，但它负责保证流程不断链：

- 每个阶段必须有主责 Agent。
- 每次交接必须有输入、输出、证据和下一步。
- 任务失败必须进入重试、修复、返工、澄清或升级。
- 项目状态必须来自 TaskResult、AgentRun、Review、测试报告和审计记录。
- 项目结束时必须完成交付判断、运营交接和知识沉淀检查。

### 子 Agent 卡住时的恢复规则

当子 Agent、worker 或外部执行器长时间没有心跳、阶段进展或中间产物时，项目经理 Agent 必须恢复调度，但不能接手专业产物。

正确流程：

```txt
发现子 Agent 卡住
-> 终止或中断该子 Agent
-> 记录 blocker/audit：任务、岗位、耗时、最后进展、缺失产物
-> 缩小任务范围并重新派给同岗位 Agent
-> 等待同岗位 Agent 的 TaskResult
-> 依据 TaskResult 继续验收、返工或下一岗位流转
```

禁止行为：

- PM 不能因为产品经理 Agent 卡住就自己写 PRD。
- PM 不能因为设计 Agent 卡住就自己写设计稿或交互规范。
- PM 不能因为架构师 Agent 卡住就自己写正式技术方案。
- PM 不能因为研发 Agent 卡住就自己写代码。
- PM 不能因为测试 Agent 卡住就自己给测试通过结论。

如果没有可用替代 Agent，任务状态必须变为 `blocked` 或 `needs_decision`，并通知项目 Owner 或人类决策人。PM 写出的任何跨岗位内容只能是调度备注或待接收草稿，不能算交付物。

## 系统化闭环规则

这一节是调度器必须执行的规则，用来补齐红队发现的断点：项目不能无判断地创建，岗位不能无产物地交接，任务不能无评价地关闭，运营反馈不能停在聊天记录里。

### 立项评估 Gate

用户提出“做一个项目”时，Agent Hub 不能直接创建正式执行任务。调度器必须先生成项目启动草稿：

```txt
ProjectIntake
-> ProjectDraft
-> ProjectLaunchChecklist
-> project_initialization task
```

最少字段：

- 项目名称。
- 项目 Owner。
- 项目来源：已有仓库接入 / 从头新建 / 运营长期项目。
- 项目目标。
- 预期交付物。
- 优先级。
- 风险等级。
- 建议 Agent Team。
- 是否需要项目群。
- 是否需要代码仓库。
- 是否需要 Agent Ring Runner。

规则：

- 小问题不立项，交给查知识 Agent 或创建单任务。
- 目标不清楚时先澄清，不创建执行任务。
- 已有仓库接入只要求 Git 地址和 Owner；项目名、仓库名、README/AGENTS/目录结构由初始化任务检查后补齐。
- 从头新建项目不让用户填写仓库名；系统根据项目名称生成仓库候选名。
- 运营长期项目不强制代码仓库。
- Agent Ring 未启用时，初始化任务状态必须是 `waiting_runner`。

### 岗位交接 Contract

每个 TaskResult 都必须写清楚下游能不能接：

| 字段 | 含义 |
| --- | --- |
| `handoffTo` | 下一岗位 Agent；没有下一岗位时留空并写终态原因 |
| `handoffSummary` | 下游读完就能理解当前结果的摘要 |
| `requiredArtifacts` | 该岗位交接必须具备的产物 |
| `artifactRefs` | 实际产物路径 |
| `openRisks` | 未关闭风险 |
| `nextSuggestedTask` | 建议创建的下一任务 |
| `terminalReason` | 没有下一岗位时为什么可以关闭 |

缺少交接摘要、证据或产物时，任务不能被视为健康完成；调度器会进入返工、升级或项目经理判断。

### 全岗位质量评价

每个 TaskResult 都必须生成 `qualityEvaluation`：

| 字段 | 含义 |
| --- | --- |
| `status` | passed / failed / blocked |
| `passed` | 是否通过 |
| `decision` | close / handoff_ready / retry_required / escalate_to_project_manager / review_required |
| `score` | 0-100 |
| `reasons` | 失败原因 |
| `nextOwnerAgent` | 下一接管 Agent |
| `attemptNumber` / `maxAttempts` | 当前尝试次数和最大尝试次数 |

流转规则：

```txt
pass + 有 handoffTo -> 进入验收门，通知项目经理 Agent；默认等待人类验收，通过后才创建下一岗位任务
pass + 无 handoffTo -> 进入验收门或自动验收；由项目经理 Agent 判断关闭、运营、返工或补任务
retry_required -> 自动创建返工任务
blocked -> 升级给项目经理 Agent
连续失败 -> 项目经理 Agent 重新拆任务或请求人工决策
知识任务 pass -> 内部自动验收并进入 Knowledge Review；成为 verified/policy/权限类变更时仍需人类审批
```

### 交付验收门

每个岗位完成 TaskResult 后，都必须经过验收门，不能由 `finish` 直接把任务推给下一个岗位。

验收门的执行规则：

1. `finish` 只写入 TaskResult、`qualityEvaluation`、`acceptancePolicy`、通知记录和审计记录。
2. 质量不达标时，调度器立即创建返工或升级任务，不进入下一岗位。
3. 质量达标且需要岗位交接时，任务状态进入 `waiting_acceptance`，并通知项目经理 Agent 和默认人类验收人。
4. 项目经理 Agent 收到通知后，判断是否需要人类确认；默认需要，人类验收通过后才允许创建下一岗位任务。
5. 低风险记录类、查询类、通知类任务，或任务显式声明 `humanAcceptanceRequired: false` 时，可以 `auto_accepted`，但必须保留通知和审计。
6. 验收通过后，调度器创建下一岗位任务，写入 `followupTaskRefs`，原任务关闭为 `done`。
7. 验收拒绝或要求修改时，调度器创建返工任务，原任务状态写成 `rejected` 或 `changes_requested`。

验收门必须写入这些字段：

| 字段 | 含义 |
| --- | --- |
| `acceptancePolicy.acceptanceStatus` | not_required / waiting_acceptance / accepted / auto_accepted / rejected / changes_requested |
| `acceptancePolicy.humanAcceptanceRequired` | 是否需要人类验收 |
| `acceptancePolicy.projectManager` | 负责推进的项目经理 Agent |
| `acceptancePolicy.humanReviewer` | 默认人类验收人 |
| `acceptancePolicy.decisionReason` | 验收或自动验收理由 |
| `followupTaskRefs` | 验收通过或返工后创建的后续任务 |

### 运营反馈回流

运营 Agent 的反馈不是项目末尾备注，而是新的输入源。反馈必须记录为 `OperationsFeedback`，并按内容分流：

| 反馈类型 | 下游 |
| --- | --- |
| 产品反馈 | 产品经理 Agent |
| 工程反馈 | 研发 Agent |
| 知识反馈 | 知识工程 Agent |
| 无法分类或综合反馈 | 项目经理 Agent |

每条反馈必须保留：

- 来源项目。
- 提交者。
- 原始反馈。
- 证据路径。
- 影响范围。
- 建议下一步。
- 自动生成的后续任务。

### 调度器状态机

任务状态不能随意跳转。项目任务的典型路由主线：

```txt
pending
-> waiting_runner
-> processing
-> waiting_acceptance
-> done

processing
-> changes_requested / blocked / rejected

changes_requested / blocked
-> pending / waiting_runner / processing
```

`ProjectTask.status` 只使用 `pending`、`waiting_runner`、`processing`、`waiting_acceptance`、`changes_requested`、`blocked`、`done`、`rejected`。`done/rejected` 不能倒退回 `processing`。如果需要继续工作，必须创建新的返工、交接、反馈或阻塞处理任务。

## 默认组队规则

| 项目类型 | 默认 Agent Team |
| --- | --- |
| 新产品 / 新功能 | 项目经理 Agent、产品经理 Agent、设计 Agent、架构师 Agent、研发 Agent、测试 Agent、知识工程 Agent |
| 纯工程任务 | 项目经理 Agent、架构师 Agent、研发 Agent、测试 Agent、知识工程 Agent |
| 运营项目 | 项目经理 Agent、运营 Agent、产品经理 Agent、知识工程 Agent，必要时加入设计/架构师/研发/测试 |
| 知识沉淀 | 知识工程 Agent、查知识 Agent，必要时加入项目经理 Agent |
| 用户问题查询 | 查知识 Agent，必要时转知识工程 Agent 创建知识任务 |
| 设计专项 | 项目经理 Agent、产品经理 Agent、设计 Agent、架构师 Agent、研发 Agent、测试 Agent |

## 协作规则

1. 一个任务必须有主责 Agent。
2. 一个任务可以有多个协作 Agent。
3. Skill 不等于 Agent。新增能力优先作为已有 Agent 的 Skill。
4. Workflow 不等于 Agent。新增流程优先作为已有 Agent 的工作流。
5. Agent Hub 只负责入口、路由、调度和审计，不直接冒充角色 Agent。
6. Agent Ring 负责本地执行环境、工具注册、能力声明、任务领取和结果写回。
7. 任何可复用知识必须经过知识工程闭环。
8. 任何跨团队规则、权限、安全、客户承诺、流程标准变更，必须人工审批。

## Agent 讨论会机制

Agent 讨论会用于产品、研发、测试、设计、运营、知识工程等 Agent 围绕同一个需求、方案、风险或验收标准进行回合制讨论。它不是普通聊天，而是中央调度器管理的一类协作对象。

第一阶段采用异步回合制，不做实时聊天室：

```txt
项目任务 / 需求 / 风险进入
-> 项目经理 Agent 判断需要多角色讨论
-> 创建 DiscussionSession
-> 参与 Agent 分别提交 DiscussionTurn
-> 全部角色提交后进入 pm_reviewing
-> 项目经理 Agent 生成 DiscussionSummary
-> 形成 Decision / 后续 ProjectTask / 人类待决事项
-> 机器人通知相关角色和人类
```

### 什么时候发起讨论

- 需求目标不清楚，产品价值、用户场景或非目标范围存在不确定。
- 产品和研发对实现方式、技术风险、边界范围存在分歧。
- 研发和测试对验收标准、边界用例、发布风险没有形成一致。
- 设计、运营、知识工程等跨角色交付会影响后续团队。
- 当前任务风险高、影响跨项目，或需要人类做取舍。
- 人类明确要求“让这些 Agent 讨论一下”。

普通低风险小任务可以不发起讨论，直接走任务执行和验收门。

### 讨论对象

| 对象 | 作用 |
| --- | --- |
| `DiscussionSession` | 一次讨论会，记录主题、项目、关联任务、参与 Agent、状态和通知 |
| `DiscussionTurn` | 某个 Agent 的一轮观点，记录立场、担忧、建议和证据 |
| `DiscussionSummary` | 项目经理 Agent 的汇总，记录共识、待决问题、决策建议 |
| `Decision` | 讨论形成的正式项目或公司决策 |
| `ProjectTask` | 讨论后拆出的后续执行任务 |
| `NotificationRecord` | 讨论创建、发言、汇总、人类决策、闭环的机器人通知记录 |

### 角色分工

| 角色 | 在讨论中的职责 |
| --- | --- |
| 项目经理 Agent | 主持讨论、判断参与角色、汇总共识、识别分歧、决定是否需要人类决策 |
| 产品经理 Agent | 说明用户目标、业务价值、需求边界、优先级和非目标 |
| 设计 Agent | 说明用户流程、交互状态、信息架构和体验风险 |
| 架构师 Agent | 说明架构方案、技术方案、系统边界、接口/数据契约、技术风险和替代方案 |
| 研发 Agent | 说明实现计划、代码影响、依赖、复杂度和落地风险 |
| 测试 Agent | 说明验收标准、测试用例、边界条件、回归风险和发布建议 |
| 运营 Agent | 说明运营路径、交付后使用场景、反馈指标和持续优化动作 |
| 知识工程 Agent | 判断讨论结果是否需要沉淀为知识、规则、案例或经验 |
| 查知识 Agent | 在讨论中提供已审核知识、历史决策和来源引用 |

### 状态和退出条件

| 状态 | 含义 | 下一步 |
| --- | --- | --- |
| `waiting_agent_turns` | 等待参与 Agent 提交观点 | 参与 Agent 写回 `DiscussionTurn` |
| `pm_reviewing` | 参与 Agent 已提交完，等待项目经理 Agent 汇总 | 生成 `DiscussionSummary` |
| `waiting_human_decision` | 有分歧或高风险，需要人类取舍 | 机器人通知人类，等待决策 |
| `next_task_created` | 已形成后续任务 | 后续任务进入任务调度和验收门 |
| `done` | 讨论已闭环且没有后续任务 | 归档并可被查询 |

讨论必须有退出条件：

- 第一阶段默认 1 轮发言。
- 超过最大轮次仍没有共识，进入 `waiting_human_decision`。
- 高风险、安全、客户承诺、跨项目规则变化，必须进入人类决策。
- 讨论结果必须产出 `DiscussionSummary`，不能只停留在聊天内容。

### 通知链路

机器人通知是讨论会闭环的一部分，不是附加体验。

| 事件 | messageType | 通知对象 |
| --- | --- | --- |
| 讨论会创建 | `discussion_created` | 项目经理 Agent |
| 请求角色发言 | `discussion_turn_requested` | 每个参与 Agent |
| 角色已提交观点 | `discussion_turn_submitted` | 项目经理 Agent |
| 全部观点已提交 | `discussion_ready_for_summary` | 项目经理 Agent |
| 讨论汇总完成 | `discussion_summary_ready` | 请求人 / 项目经理 |
| 需要人类决策 | `discussion_human_decision_required` | 项目 Owner 或指定人类 |
| 讨论闭环 | `discussion_completed` | 项目经理 Agent / 项目群 |

飞书机器人应优先发送摘要卡，而不是把完整讨论刷屏：

- 当前主题。
- 参与 Agent。
- 已形成共识。
- 主要分歧。
- 是否需要人类决策。
- 讨论记录路径。
- 后续任务或 Decision 路径。

完整讨论过程保存在中央处理器对象和飞书文档中，人类可追溯查看。

通知必须走可确认投递链路：

1. 中央处理器创建 `NotificationRecord`，初始状态为 `pending`。
2. 飞书机器人、Agent Ring 或临时 Runner 通过 `notification list` / `/v0/notifications` 拉取待发通知。
3. 投递成功后调用 `notification mark --status sent` 或 `/v0/notifications/delivery`，写入 `sentAt`、`deliveredBy`、`deliveryRef`。
4. 投递失败后标记 `failed`，写入 `failureReason`，由项目经理 Agent 或通知 worker 重试 / 转人工。
5. 所有投递状态变化都写入 AuditLog，不能只依赖飞书客户端提示。

### 可执行入口

本地 CLI：

```txt
zhenzhi-knowledge discussion create --title "<标题>" --project <projectId> --requester <actor> --topic "<问题>"
zhenzhi-knowledge discussion turn --discussion-id <id> --agent-id <agentId> --content "<观点>"
zhenzhi-knowledge discussion finalize --discussion-id <id> --facilitator <agentId> --summary "<汇总>" --decision "<决策>" --followup-task-title "<后续任务>"
zhenzhi-knowledge discussion status --discussion-id <id>
zhenzhi-knowledge notification list --status pending --recipient <agentId-or-user>
zhenzhi-knowledge notification mark --notification-id <id> --status sent --actor <notifier> --delivery-ref <message-id>
```

HTTP API：

```txt
POST /v0/discussions/create
POST /v0/discussions/turn
POST /v0/discussions/finalize
GET  /v0/discussions/<discussionId>
GET  /v0/notifications?status=pending&recipient=<agentId-or-user>
POST /v0/notifications/delivery
```

飞书入口：

```txt
发送：组织讨论 / Agent 讨论 / 需求讨论 / 技术方案讨论
```

### 验收标准

一次讨论会只有满足以下条件，才算闭环：

1. 有 `DiscussionSession`。
2. 每个必要角色都有 `DiscussionTurn`，或者有明确缺席 / 跳过原因。
3. 有项目经理 Agent 生成的 `DiscussionSummary`。
4. 有 `Decision`、后续 `ProjectTask` 或 `waiting_human_decision`。
5. 每个关键节点都有 `NotificationRecord`。
6. 通知可以被机器人 / Agent Ring 拉取，并能被标记为 `sent` 或 `failed`。
7. 通知投递结果有 AuditLog。
8. 后续任务继续进入任务质量评价和交付验收门。
9. `zhenzhi-knowledge validate` 通过。

## Agent 自净化与能力成长闭环

Agent 不能只是“失败后重试”。每次失败、返工、阻塞、人类验收不通过，都必须变成下一次可复用的改进资产。这样公司 Agent Team 才会越做越稳，而不是每个项目从头踩坑。

### 触发条件

以下情况会自动进入自净化闭环：

- `TaskResult.qualityEvaluation.passed = false`。
- 任务结果状态为 `blocked`、`failed`、`rejected`。
- 人类或项目经理 Agent 在交付验收门选择 `changes_requested` 或 `rejected`。
- EvalRun 失败、Review 多次返工、通知投递失败、Runner 执行失败等被转成任务质量问题。
- 人类明确指出“这个流程/技能/角色不对，需要沉淀经验”。

### 可执行流转

```txt
Agent 完成任务
-> 写入 TaskResult
-> 调度器生成 qualityEvaluation
-> 如果通过：进入项目经理验收门 / 下一岗位 / 知识 Review
-> 如果不通过：创建 retry/repair/escalation 任务
-> 同时创建 AgentImprovementProposal
-> 同时创建 EvalCase 草稿作为回归用例
-> 通知项目经理 Agent 和对应角色 Agent
-> 对应角色 Agent 修 Skill / checklist / workflow
-> 必要时更新本指南和飞书指南
-> 重新跑 EvalCase 或任务
-> 通过后关闭改进项
```

这里的关键是：任务可以继续流转，Agent 的能力也必须沉淀。不能只创建返工任务，却不记录为什么失败、下次怎么避免。

### 新增对象

| 对象 | 用途 | 是否可复用 |
| --- | --- | --- |
| `AgentImprovementProposal` | 记录某个 Agent 因失败、阻塞、验收不通过而产生的改进提案 | 默认 draft，Review 后才可转为 Skill / Eval / 指南 |
| `EvalCase` | 把失败样例变成回归测试，防止以后再犯 | draft 起步，修正后可 verified |
| `AgentCapabilityReport` | 汇总某个 Agent 的通过率、失败原因、改进项 | 管理和调度参考，不是独立真相 |
| `ActorContext` | 记录人、Agent、Runner、机器人入口、本地工作台的运行上下文、权限和偏好 | 不作为知识复用，只进入 Context Pack |
| `ActorFeedback` | 记录人或数字员工对 Agent 输出、流程、任务结果的反馈 | 负面反馈可触发改进提案，结论仍需 Review |
| `NotificationRecord` | 通知项目经理 Agent、责任 Agent、人类验收人 | 可投递、可失败重试、可审计 |

### Actor Context 和分层记忆

不要给每个员工做一套重的个人知识库。成熟 OS 的记忆分四层：

| 层级 | 内容 | 作用 |
| --- | --- | --- |
| 公司记忆 | 已审核知识、公共 Skill、公共 EvalCase、Agent Team 指南、制度 | 所有员工、所有项目、所有公司级 Agent 可复用 |
| 项目记忆 | 项目目标、任务、决策、资料、TaskResult、项目经验 | 当前项目 Agent、Runner、成员可用 |
| 任务记忆 | 当前任务输入、证据、输出、质量评价、交接状态 | 保证任务执行不丢上下文 |
| Actor Context | 人、Agent、Runner、机器人入口、本地工作台是谁、能看什么、偏好什么、最近反馈 | 运行上下文，不直接成为知识 |

规则：

- Actor 可以是人类员工、公司级 Agent、项目级 Agent、Agent Ring Runner、飞书机器人、本地 Codex / Claude 工作台。
- 每次拉取任务时，Context Pack 必须包含 assignee 或 lease owner 的 Actor Context。
- Actor 偏好只能影响展示、通知和协作方式，不能覆盖权限、安全、证据、Review 或审批门。
- ActorFeedback 不直接进入知识库；负面反馈先生成 `AgentImprovementProposal` 和 `EvalCase`，再由 Review 决定是否晋级为项目或公司记忆。
- 项目经验重复出现两次以上，知识工程 Agent 应提出公司级抽象建议。

### 公共复用和项目私有边界

自净化结果分两类：

| 范围 | 进入哪里 | 谁可以用 | 示例 |
| --- | --- | --- | --- |
| 公司级 `reuseScope: company` | 公司 Agent Team 指南、公共 Skill、公共 EvalCase、公共知识库 | 所有员工、所有项目、所有 Agent Ring Runner、所有公司级 Agent | 飞书卡片开发坑、知识入库证据规则、项目交接标准 |
| 项目级 `reuseScope: project` | 项目目录、项目 Skill、项目 EvalCase、项目知识上下文 | 该项目 Agent、该项目 Runner、该项目成员 | 某客户特定口径、某仓库特殊部署流程 |

判断原则：

- 影响多个项目、多个员工、多个角色的，抽象成公司级。
- 只适用于某个项目、客户、仓库、环境的，留在项目级。
- 项目级经验如果重复出现两次以上，知识工程 Agent 应提出公司级抽象建议。
- 公司级经验必须经过 Review；涉及岗位、Skill、Workflow、调度规则、Agent Ring、知识政策时，必须同步更新本指南。

### 员工如何复用

普通员工不需要知道内部对象名。员工通过以下入口间接使用这套能力：

- 在 Agent Hub 问问题：查知识 Agent 会优先返回已审核知识、来源和适用范围。
- 创建项目：项目经理 Agent 会使用最新的公司级 Agent 配置、Skill、交接标准和 EvalCase。
- 提交资料：知识工程 Agent 会使用最新的资料解析、证据引用、Review 和发布规则。
- 发起讨论：项目经理 Agent 会按最新岗位职责组织产品、设计、研发、测试、运营、知识工程、查知识 Agent 参与。
- 查看任务通知：失败、返工、验收、改进项都会通过通知链路告诉对应角色或项目经理。

Agent Ring / 本地电脑通过以下入口复用：

```txt
GET  /v0/notifications?status=pending&recipient=<agentId>
POST /v0/tasks/pull
POST /v0/tasks/finish
POST /v0/agents/report
```

本地 CLI：

```txt
zhenzhi-knowledge notification list --status pending --recipient <agentId>
zhenzhi-knowledge task pull <taskId>
zhenzhi-knowledge task finish <taskId> --summary "<结果>" --evidence-ref <证据>
zhenzhi-knowledge agent report --agent-id <agentId> --project <projectId>
```

### 完成标准

一次 Agent 自净化闭环只有满足以下条件，才算完成：

1. 原始失败有 `TaskResult`。
2. `TaskResult` 有 `qualityEvaluation` 和失败原因。
3. 已创建 retry、repair、escalation 或 human acceptance 后续任务。
4. 已创建 `AgentImprovementProposal`。
5. 已创建草稿 `EvalCase`。
6. 已通知项目经理 Agent 和责任 Agent。
7. 若影响公司级角色、Skill、工作流或调度规则，已更新本指南和飞书指南。
8. 责任 Agent 已修复 Skill / checklist / workflow / prompt / tool usage。
9. 修复后重新跑任务或 EvalCase。
10. 通过后关闭改进项；未通过则继续 retry / repair / escalate。

## 文档实时更新机制

这份文档必须保持最新。这里的“实时更新”不是后台自动幻想式更新，而是工程化闭环：

```txt
发生 Agent/Skill/Workflow/调度规则变化
-> 变更任务不能关闭
-> 必须同步更新本地源文档
-> 必须同步更新飞书文档
-> 必须补充修订记录
-> 必须写入 AuditLog
-> 必须经过知识工程 Review
-> 影响跨团队标准时必须人工审批
-> 通过后才能关闭变更任务
```

### 谁负责更新

| 变化类型 | 主责 Agent | 协作 Agent | 是否需要人工审批 |
| --- | --- | --- | --- |
| 新增/删除公司级 Agent | 项目经理 Agent | 知识工程 Agent | 是 |
| 修改 Agent 岗位职责 | 对应角色 Agent | 项目经理 Agent、知识工程 Agent | 是 |
| 新增/删除 Skill | 对应角色 Agent | 知识工程 Agent | 视影响范围决定 |
| 修改核心工作流 | 对应角色 Agent | 项目经理 Agent、知识工程 Agent | 是 |
| 修改调度规则 | 项目经理 Agent | 架构师 Agent、研发 Agent、知识工程 Agent | 是 |
| 修改 Agent Ring 对接协议 | 架构师 Agent | 研发 Agent、项目经理 Agent、知识工程 Agent | 是 |
| 修改知识入库、审核、发布规则 | 知识工程 Agent | 查知识 Agent、项目经理 Agent | 是 |
| 修改查询答案口径 | 查知识 Agent | 知识工程 Agent | 视影响范围决定 |

### 更新门禁

任何涉及 Agent Team 的任务，在关闭前必须检查：

1. 是否影响 Agent 角色定义。
2. 是否影响 Skill 列表。
3. 是否影响工作流。
4. 是否影响 Agent Hub 调度规则。
5. 是否影响 Agent Ring 对接。
6. 是否影响知识入库、审核、发布、查询。
7. 是否需要更新这份指南。

如果答案有任意一个是“是”，任务结果必须包含：

- 已更新的本地源文档路径。
- 已同步的飞书文档链接。
- 修订记录条目。
- AuditLog 路径。
- 是否需要人工审批。
- 审批状态。

没有这些内容，任务不能标记为完成。

### 系统字段

中央调度器使用以下字段执行门禁：

| 字段 | 含义 |
| --- | --- |
| `guideUpdateRequired` | 这个任务是否影响 Agent、Skill、Workflow、Scheduler、Agent Ring 或知识规则 |
| `guideUpdated` | 是否已经更新本指南 |
| `guideRef` | 本地源文档路径，默认 `docs/agent-team/company-agent-team-operating-guide.md` |
| `guideFeishuUrl` | 已同步的飞书正式文档链接 |
| `guideRevision` | 修订记录说明 |
| `guideAuditRefs` | 对应 AuditLog 路径列表 |

任务创建时，如果标题、任务类型或期望输出命中 Agent/Skill/Workflow/Scheduler/Agent Ring/知识规则相关变化，调度器会自动标记 `guideUpdateRequired: true`。

任务完成时，如果 `guideUpdateRequired: true`，但没有 `guideUpdated: true`、`guideRevision` 和 `guideAuditRefs`，任务不能关闭。

CLI 完成任务时必须显式提交：

```txt
zhenzhi-knowledge task finish <taskId> \
  --summary "<总结>" \
  --guide-updated \
  --guide-revision "<为什么修改、改了什么>" \
  --guide-audit-ref knowledge/audit/<audit-id>.md
```

`zhenzhi-knowledge validate` 也会检查这组字段。即使绕过 CLI 手写任务文件，缺少指南更新证据也会导致校验失败。

## 修订记录

修订记录必须记录“谁、什么时候、为什么、改了什么、证据在哪里”。

每次修改必须新增一行，不能覆盖旧记录。

| 时间 | 修改人 / Agent | 变更原因 | 主要变更 | 证据 / 任务 / 审批 |
| --- | --- | --- | --- | --- |
| 2026-06-19 | 知识工程 Agent | 建立公司 Agent Team 统一工作指南 | 定义 Agent Team 结构、职责、Skill、工作流、调度规则、实时更新机制 | `knowledge/audit/audit.20260619T122906Z.md` |
| 2026-06-19 | Codex / 知识工程协作 | 用户要求文档中文化，并说明如何保证实时更新和修订记录 | 将指南改为中文，补充实时更新机制、更新门禁、修订记录规则 | 本次任务 |
| 2026-06-19 | Codex / 知识工程协作 | 用户要求把指南更新机制做成必须执行的系统规则 | 增加 `guideUpdateRequired/guideUpdated` 系统门禁字段，任务完成和 bundle 校验都会强制检查指南更新证据 | `knowledge/audit/audit.20260619T130500Z.md` |
| 2026-06-19 | Codex / 知识工程协作 | 用户要求把岗位和岗位之间的项目流程串起来 | 增加岗位协同主流程、交接表、返工规则和项目经理横向责任 | `knowledge/audit/audit.20260619T134500Z.md` |
| 2026-06-19 | Codex / 知识工程协作 | 红队发现立项、岗位交接、质量评价、运营反馈和状态机还没有系统化落地 | 增加立项评估 Gate、岗位交接 Contract、全岗位质量评价、运营反馈回流和调度器状态机规则 | `knowledge/audit/audit.20260619T144500Z.md` |
| 2026-06-19 | Codex / 知识工程协作 | 用户要求每个岗位交付后先通知项目经理并默认人类验收，不能自动进入下一环节 | 增加交付验收门：TaskResult -> PM 通知 -> 人类验收或自动验收 -> 创建下一岗位/返工任务 | `knowledge/audit/audit.20260619T153000Z.md` |
| 2026-06-19 | Codex / 知识工程协作 | 用户要求产品、研发、测试等 Agent 能像人一样讨论问题，并且讨论过程可见、可通知、可转任务 | 增加 Agent 讨论会机制：DiscussionSession / DiscussionTurn / DiscussionSummary / Decision / 后续任务 / 通知链路 / CLI/API/飞书入口 | `knowledge/audit/audit.20260619T160800Z.md` |
| 2026-06-19 | Codex / 知识工程协作 | 用户补充机器人通知链路也要完善，不能只写 NotificationRecord | 增加通知出站队列和投递确认协议：`notification list/mark`、`/v0/notifications`、`/v0/notifications/delivery`、投递 AuditLog | `knowledge/audit/audit.20260619T162000Z.md` |
| 2026-06-20 | Codex / 知识工程协作 | 用户要求各岗位 Agent 能自净化，越来越高效高质量，并让能力可被全公司复用 | 增加 Agent 自净化闭环：TaskResult 质量评价失败或验收打回后自动生成 AgentImprovementProposal、EvalCase、通知和 AgentCapabilityReport，区分公司级/项目级复用 | `knowledge/audit/audit.20260620T005000Z.md` |
| 2026-06-20 | Codex / 知识工程协作 | 红队发现岗位体系仍偏文档化：产品经理 Agent ID 不统一、role-check 不检查产物质量模板、除产品外缺本地 Skill | 统一公司级产品经理 Agent ID，补齐岗位运行检查，并把质量评价模板纳入 RoleOperatingReview 强制检查 | 本次任务 |
| 2026-06-22 | Codex / 知识工程协作 | 用户指出 `skills/*-agent` 本质是岗位定义，不是真正可执行 Skill | 拆分岗位画像与生产 Skill：删除伪 Skill 目录，新增公司 Skill 注册表、18 个可执行 Skill、`zhenzhi-knowledge skill validate` 与全局校验门禁 | 本次任务 |
| 2026-06-22 | Codex / 知识工程协作 | 用户要求把架构师 Agent 从研发 Agent 中拆出，主责架构方案、技术方案和代码架构审查 | Agent Team 扩展为九个角色；新增架构师岗位画像、`architecture-technical-design`、`code-architecture-review`，并更新岗位交接为设计/产品 -> 架构 -> 研发 -> 架构审查 -> 测试 | 本次任务 |
| 2026-06-20 | Codex / 知识工程协作 | 用户要求反思员工级进化和记忆体系，避免重个人知识库，支持所有员工和数字员工 | 增加 Actor Context、ActorFeedback、四层记忆和反馈晋级规则；任务 Context Pack 注入 Actor Context，负面反馈进入改进提案和 EvalCase | 本次任务 |

## 快速路由指南

| 遇到的问题 | 找谁 |
| --- | --- |
| 我要开始一个项目 | 项目经理 Agent |
| 我不知道需求怎么描述 | 产品经理 Agent |
| 页面不好用或不知道怎么设计 | 设计 Agent |
| 需要架构方案、技术方案、接口/数据契约、代码架构审查 | 架构师 Agent |
| 需要按方案写代码、部署、排障 | 研发 Agent |
| 需要验证能不能发布 | 测试 Agent |
| 要做内容、渠道、活动、复盘 | 运营 Agent |
| 有资料要沉淀成知识 | 知识工程 Agent |
| 想查一个已有答案 | 查知识 Agent |
| 不知道找谁 | Agent Hub |

## 相关源文档

- `docs/agent-team/knowledge-core-agent-team.md`
- `docs/agent-team/knowledge-engineering-agent-skill-pack.md`
- `docs/agent-team/knowledge-query-agent-role.md`
- `docs/agent-team/product-manager-agent-role-and-skill-pack.md`
- `docs/agent-team/project-manager-agent-skill-pack.md`
- `docs/agent-team/role-operating-specs.json`
- `skills/*-agent/SKILL.md`
- `docs/workflows/knowledge-ingest-orchestration.md`
- `docs/workflows/knowledge-lifecycle.md`
- `docs/protocols/agent-workbench-integration-brief.md`
