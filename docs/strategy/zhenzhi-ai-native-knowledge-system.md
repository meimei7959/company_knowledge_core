# 桢知科技 AI 原生知识工程建设方案

## 1. 当前判断

桢知现在不需要先建设一个很大的知识平台。当前最重要的问题是：

- 每个人都在本地开发，工具散落在个人电脑。
- 经验留在个人脑子、聊天记录、本地笔记里，团队无法复用。
- 多个项目并行，但项目上下文、决策、进展、工具、经验没有统一沉淀。
- 未来项目开发主要由 Agent 完成，但现在缺少 Agent 管理、权限、复盘、知识写回机制。

所以第一阶段的知识工程，不是“系统工程”，而是“AI 原生团队工作方式工程”。

一句话：

```txt
先把项目、Agent、工具、经验、业务知识的沉淀流程跑起来，再逐步产品化。
```

## 2. 知识工程的定位

知识工程不是代码仓，不是项目管理软件，也不是大而全的数据平台。

它在当前阶段承担 4 件事：

1. 管项目上下文：每个项目做什么、为什么做、当前状态、关键决策。
2. 管 Agent：哪个 Agent 做什么、能访问什么、能调用什么工具、结果如何。
3. 管工具资产：谁开发了什么工具、在哪里、怎么用、什么风险、谁维护。
4. 管经验知识：做项目、调 Agent、写代码、交付客户过程中形成的可复用经验。
5. 管知识质量：所有落库内容先过知识审核 Agent，避免知识库变成低质量资料堆。

## 3. 真源边界

不要把所有东西都复制进知识工程。每类资产要有清晰真源。

| 资产 | 真源 | 知识工程保存 |
| --- | --- | --- |
| 代码 | Git 仓库 | repoRef、commitRef、变更摘要、关联项目、经验复盘 |
| 项目需求 | 当前先用知识工程项目卡；以后迁移到自研项目管理系统 | projectRef、需求摘要、状态、决策、约束 |
| 工具代码 | Git 仓库或本地临时仓，成熟后必须上 Git | ToolAsset、入口、权限、风险、使用说明、失败案例 |
| Agent 配置 | 知识工程 Agent 卡；以后可接入 Agent 管理系统 | AgentIdentity、能力、权限、工具白名单、运行记录 |
| 业务知识 | 知识工程 | 来源、置信度、状态、版本、适用项目 |
| 原始资料 | 云盘、文档、聊天、会议、客户资料 | sourceRef、摘要、抽取事实、权限、引用链 |

原则：

- Git 是代码真源，知识工程不保存完整代码。
- 项目管理系统上线前，知识工程临时承担项目真源。
- 工具必须先登记，再允许团队复用或 Agent 调用。
- Agent 不能直接绕过知识工程访问工具和项目资料。

## 4. 第一阶段目标

第一阶段只做轻量闭环，不做复杂平台。

目标：

- 团队知道每个项目当前在做什么。
- 团队知道有哪些工具可用、怎么用、谁维护。
- 团队知道有哪些 Agent、能做什么、有哪些权限。
- 项目经验能从个人电脑沉淀到团队知识库。
- 代码变更能和项目、需求、工具、经验关联起来。
- 知识有更新机制，不会写完就过期。

## 5. 核心对象

第一版只保留 7 个核心对象。

### 5.1 Project

项目是当前工作的组织单位。

每个项目必须有项目卡：

- projectId
- name
- owner
- members
- status
- goal
- scope
- currentFocus
- keyDecisions
- relatedRepos
- relatedAgents
- relatedTools
- latestUpdate

项目卡解决：

- 多个项目并行时，团队知道每个项目状态。
- Agent 进入项目前，先读取项目卡。
- 后续自研项目管理系统上线后，项目卡可迁移为项目系统数据。

### 5.2 Agent

Agent 是团队成员的一类执行者。

每个 Agent 必须有 Agent 卡：

- agentId
- name
- purpose
- owner
- allowedProjects
- allowedTools
- allowedKnowledgeScopes
- riskLevel
- humanApprovalRequired
- runLogRef
- status

Agent 卡解决：

- 哪些 Agent 能参与哪些项目。
- 哪些 Agent 能调用哪些工具。
- 哪些 Agent 只能读，哪些 Agent 可以写。
- 出问题时知道谁负责、如何复盘。

### 5.3 ToolAsset

工具是公司能力资产，不是个人电脑里的私有脚本。

每个可复用工具必须有 ToolAsset 卡：

- toolId
- name
- owner
- repoRef
- entrypoint
- version
- status
- riskLevel
- inputSchema
- outputSchema
- allowedAgents
- allowedProjects
- secretsRequired
- usageNotes
- knownIssues
- lastVerifiedAt

工具状态：

- draft：个人开发中，不推荐团队使用。
- testing：可试用，但结果要人工检查。
- approved：团队可复用，Agent 可按权限调用。
- deprecated：不推荐新项目使用。
- blocked：有安全或质量问题，禁止调用。

### 5.4 KnowledgeItem

知识项保存可复用经验和业务事实。

类型：

- fact：明确事实。
- decision：已做决策。
- lesson：项目经验。
- pattern：可复用做法。
- constraint：约束。
- issue：问题和坑。
- prompt：可复用提示词。
- workflow：工作流程。

每条知识必须有：

- sourceRef
- confidence
- status
- scope
- owner
- updatedAt
- reviewAgentResult

状态：

- draft：未确认。
- observed：Agent 从真实问题、提交、测试、审批、回调、会议或运行记录中总结出的经验线索，可检索、可引用为参考，但不能作为强制规则。
- verified：已确认，可复用。
- stale：可能过期。
- rejected：不采用。

审核分级：

- 经验线索：`lesson`、`issue`、`pattern` 可以由 Agent 自动生成 `draft/observed`，前提是先通过知识审核 Agent，并写清楚根因、适用范围、证据、风险和不适用场景。这类知识先进入可检索经验库，不触发人工审批。
- 可复用经验：当经验被多个项目复用，或已有提交、测试、线上验证支撑时，可以申请升级为 `verified`。审核人只判断结论是否可复用、范围是否清楚、风险是否可接受。
- 强规则：凡是升级为政策、流程、铁律、安全要求、权限策略、审批规则，或修改已有 `verified` 知识，必须走人工审批。
- 项目专属经验由项目负责人审核；通用工程经验由知识工程负责人或对应领域负责人审核；跨权限、安全、审批、身份、通知的规则由通用负责人审核。

这套分级的目的，是让踩坑经验先被团队和 Agent 搜得到，同时避免每条 AI 总结都变成人工审批负担。

知识审核 Agent：

- 定位：它是知识质检员、治理分类器和审批材料整理员，不是最终审批人。
- 输入：知识提取 Agent 生成的结构化草稿，以及其引用的 SourceMaterial、AgentRun、聊天消息、会议纪要、Git/PR 摘要、工具说明、人工提交材料。
- 输出：结构化 KnowledgeItem/Project/ToolAsset/Decision/Policy 候选稿、ReviewRecord、IssueRecord、审批说明文档。
- 必检项：是否有来源、分类是否正确、字段是否完整、是否重复、是否冲突、是否含敏感信息、是否把原始资料误当知识、是否能被 Agent 准确检索、是否给人看得懂、是否需要人工审批。
- 治理分类：
  - `auto_observed`：踩坑经验、问题复盘、集成注意事项、调试结论、低风险工程模式。机审通过后直接落库为 `observed/draft`，不触发人工审批。
  - `human_approval_required`：项目立项、Token 申请、工具 approved、知识 verified、Policy/Workflow/铁律、权限/安全/审批/身份/通知规则、客户承诺、跨团队标准。
  - `clarification_required`：缺少项目、负责人、来源、证据、适用范围、敏感级别或关键字段。
  - `conflict_required`：与已有 verified/active/approved 内容冲突，先建 ConflictRecord，不直接覆盖。
  - `reject`：原始资料乱丢、无来源、不可复用、含禁止保存信息、明显错误或无法结构化。
- 结果：`pass_as_observed`、`needs_clarification`、`needs_human_approval`、`reject`、`conflict_detected`。
- 约束：它不能把自己生成或审核的内容直接改成 `verified`、`approved`、`active`，也不能绕过人工审批发布政策、流程、权限、安全或跨团队规则。
- 自动落库：分类为 `auto_observed` 且机审通过的内容，由审核 Agent 直接写入对应知识分类目录，并创建 ReviewRecord 和 AuditLog。
- 审批前置：分类为 `human_approval_required` 的内容，必须先由知识审核 Agent 生成审批说明文档；人工审批人只看整理后的结论、影响范围、风险、冲突和建议。

飞书资料入库链路：

```txt
飞书机器人收到资料
-> 记录 Interaction / SourceMaterial
-> 知识提取 Agent 生成结构化草稿
-> 知识审核 Agent 审核草稿并治理分类
-> 直接 observed/draft 落库 或 补资料/冲突/拒绝 或 发起人工审批
```

Agent/CLI 推送入库链路：

```txt
本地或云端 Agent 通过 zhenzhi-knowledge CLI 推送内容
-> 记录 AgentRun / SourceMaterial / ToolUpdate / ProjectUpdate 引用
-> 知识提取 Agent 根据推送内容生成结构化草稿
-> 知识审核 Agent 审核草稿并治理分类
-> 直接 observed/draft 落库 或 补资料/冲突/拒绝 或 发起人工审批
```

这两条入口共用同一个后半段治理管线。无论内容来自飞书、Codex、Claude、Antigravity、云端 Agent，还是其他本地 Agent，都不能直接写成正式知识。

### 5.5 SourceMaterial

原始资料不直接等于知识。

来源包括：

- 会议纪要。
- 聊天记录。
- 客户资料。
- 项目文档。
- 工具 README。
- Git commit / PR。
- Agent 运行记录。

知识工程保存 sourceRef、摘要、权限、抽取结果，不替代原始资料存储。

### 5.6 AgentRun

每次重要 Agent 执行都要记录。

记录：

- runId
- agentId
- projectId
- task
- toolsUsed
- knowledgeUsed
- outputRef
- humanReview
- result
- lessons

AgentRun 解决：

- Agent 做过什么可追溯。
- 好结果能复用。
- 坏结果能复盘。
- 工具调用和知识引用有证据链。

### 5.7 AuditLog

所有关键写入都要有审计。

包括：

- 创建项目卡。
- 知识审核 Agent 通过或驳回落库候选。
- 更新 Agent 权限。
- 发布工具。
- 修改 verified 知识。
- 将 `draft/observed` 经验升级为 verified。
- 将经验提升为政策、流程、铁律或跨团队标准。
- Agent 调用高风险工具。
- 废弃工具或知识。

## 6. 当前最小目录方式

项目还没开始做系统，先用一个知识工程仓库管理 Markdown/YAML。

底层文件格式建议兼容 OKF（Open Knowledge Format）：

- 每个知识对象是一个 Markdown 文件。
- 文件顶部使用 YAML frontmatter。
- `type` 是必填字段。
- 文件路径就是稳定 ID。
- Markdown 链接表达对象关系。
- `index.md` 支持目录级导航。
- `log.md` 支持目录级更新记录。

OKF 适合作为“知识文件交换格式”，但不等于完整知识工程。桢知仍需在 OKF 之上定义 Project、Agent、ToolAsset、AgentRun、权限、审核、写回流程。

建议结构：

```txt
company_knowledge_core/
  README.md
  index.md
  log.md
  docs/
    strategy/
      zhenzhi-ai-native-knowledge-system.md
  projects/
    index.md
    <project-id>/
      index.md
      log.md
      project.md
      decisions.md
      lessons.md
      agents.md
      tools.md
  agents/
    index.md
    <agent-id>.md
  tools/
    index.md
    <tool-id>.md
  knowledge/
    index.md
    company/
    engineering/
    business/
    prompts/
    workflows/
  runs/
    index.md
    <project-id>/
      <run-id>.md
```

这不是最终平台，只是第一阶段的真源工作法。以后项目管理系统、Agent 管理系统、工具市场上线后，这些内容可迁移成数据库对象。

### 6.1 OKF 兼容字段

所有非 `index.md`、`log.md` 的知识文件都必须有 frontmatter。

最小字段：

```yaml
---
type: ToolAsset
title: 文档解析工具
description: 将 PDF、Word、PPT 转为可检索文本和结构化片段。
tags: [tool, document, parser]
timestamp: 2026-06-16T00:00:00Z
---
```

桢知扩展字段：

```yaml
---
type: ToolAsset
title: 文档解析工具
description: 将 PDF、Word、PPT 转为可检索文本和结构化片段。
resource: git@example.com:zhenzhi/doc-parser.git
tags: [tool, document, parser]
timestamp: 2026-06-16T00:00:00Z
owner: alice
status: testing
scope: company
riskLevel: L1
sourceRef: git@example.com:zhenzhi/doc-parser.git
confidence: high
allowedAgents:
  - agent.alice.builder
allowedProjects:
  - zhenzhi-core
---
```

规则：

- `type` 遵守 OKF，必须有。
- `title`、`description`、`resource`、`tags`、`timestamp` 尽量使用 OKF 推荐字段。
- `owner`、`status`、`scope`、`riskLevel`、`allowedAgents` 是桢知治理扩展。
- 消费端必须容忍未知字段。
- 写回工具必须保留未知字段，避免破坏人工或其他 Agent 写入的信息。

### 6.2 桢知 type 建议

第一阶段使用这些 `type`：

| type | 用途 |
| --- | --- |
| Project | 项目卡 |
| Agent | Agent 身份和权限 |
| ToolAsset | 工具资产 |
| KnowledgeItem | 业务事实、经验、模式、问题 |
| SourceMaterial | 原始资料引用 |
| AgentRun | Agent 执行记录 |
| Decision | 项目或公司决策 |
| Workflow | 可复用流程 |
| Prompt | 可复用提示词 |
| AuditLog | 审计记录 |

不需要等 OKF 官方注册这些类型。OKF 明确允许生产者自定义 type，消费者应容忍未知类型。

### 6.3 OKF 能解决什么，不能解决什么

能直接借鉴：

- Markdown + YAML frontmatter。
- 路径即 ID。
- Git 版本管理。
- `index.md` 渐进式导航。
- `log.md` 更新历史。
- Markdown 链接构建知识关系。
- 人、Agent、工具都能读写同一批文件。

不能直接解决：

- Agent 身份注册。
- 权限控制。
- 高风险工具审批。
- draft 到 verified 的审核流。
- 多人并发冲突处理。
- 线上 API 和认证。
- RAG 索引策略。
- 客户数据隔离。

所以结论是：采用 OKF 作为底层知识文件规范；不要把 OKF 当成完整平台。

## 7. 知识工程形态

知识工程不是单一 RAG，也不是只有向量库。它应该是几种形态的组合，各自解决不同问题。

### 7.1 第一阶段形态：OKF-compatible Git Bundle

当前最适合的起步形态：

```txt
Git 仓库 + OKF-compatible Markdown/YAML 文件 + 本地连接器
```

解决：

- 团队几个人可马上开始。
- 每次知识变更可追踪、可 review、可回滚。
- Codex / Antigravity 能直接读取本地文件。
- 不需要先部署大平台。

适合保存：

- 项目卡。
- Agent 卡。
- ToolAsset 卡。
- lessons。
- decisions。
- AgentRun。
- draft 知识。

不适合：

- 大规模语义搜索。
- 高频权限判断。
- 很多 Agent 并发读写。
- 复杂客户数据隔离。

### 7.2 第二阶段形态：结构化索引

当 Markdown/YAML 文件变多后，需要一层结构化索引。

```txt
Markdown/YAML 真源
-> indexer
-> SQLite/Postgres 元数据索引
```

结构化索引保存：

- projectId
- agentId
- toolId
- knowledgeId
- status
- owner
- scope
- updatedAt
- sourceRef
- repoRef
- commitRef
- riskLevel

解决：

- 快速查“某项目有哪些工具”。
- 快速查“某 Agent 能用什么”。
- 快速查“哪些知识 stale”。
- 快速查“哪些 draft 待审核”。

### 7.3 第三阶段形态：全文检索 + RAG

RAG 不是知识工程本体，只是 Agent 取上下文的一种方式。

```txt
Markdown/YAML + SourceMaterial
-> chunk
-> full-text search / vector search
-> context pack
```

全文检索适合：

- 精确词搜索。
- 项目名、工具名、错误码、函数名。
- 中文关键词。

向量检索适合：

- 语义相似经验。
- 相似项目案例。
- 相似问题和解决方案。
- Prompt 和 workflow 推荐。

RAG 返回的不是“答案”，而是“可引用上下文”。Agent 仍然要引用 sourceRef。

### 7.4 第四阶段形态：关系图谱

知识图谱不是第一天就做，但关系必须从第一天记录。

核心关系：

```txt
Project -> uses -> ToolAsset
Project -> has -> Agent
AgentRun -> used -> KnowledgeItem
AgentRun -> used -> ToolAsset
KnowledgeItem -> derivedFrom -> SourceMaterial
ToolAsset -> implementedIn -> Git repo / commit
Decision -> affects -> Project / ToolAsset / Agent
```

先用 Markdown/YAML 记录关系，后续再进入图数据库或关系表。

图谱解决：

- 一个工具影响哪些项目。
- 一个知识来自哪些原始资料。
- 一个 Agent 常犯哪些问题。
- 一次代码变更产生了哪些经验。
- 一个客户交付物引用了哪些事实。

### 7.5 第五阶段形态：Knowledge API / Agent Gateway

当团队开始多人、多项目、多 Agent 高频协作，就需要线上服务。

```txt
本地 AI 工具
-> zhenzhi-knowledge connector
-> Knowledge API
-> 权限 / 索引 / RAG / 图谱 / 审计
```

线上服务负责：

- 权限校验。
- context pack 生成。
- Agent 注册。
- 项目注册。
- 工具注册。
- 写回草稿。
- 审核流。
- 审计记录。

### 7.6 组合关系

最终组合不是二选一。

```txt
Git/Markdown/YAML = 早期真源和变更审计
结构化数据库 = 元数据、状态、权限、查询
全文检索 = 精确搜索
向量库 = 语义召回
关系图谱 = 影响分析和证据链
对象存储 = 原始资料和附件
Knowledge API = Agent 统一入口
Agent Gateway = 权限、上下文、工具调用治理
```

建设顺序：

1. OKF-compatible Git Bundle。
2. 本地连接器。
3. 结构化索引。
4. 全文检索。
5. 向量库/RAG。
6. Knowledge API。
7. Agent Gateway。
8. 图谱和影响分析。

## 8. 本地开发如何同步

每个人仍然本地开发，但必须把可复用资产同步出来。

### 8.1 代码同步

流程：

```txt
本地开发 -> Git commit -> Git push -> 更新项目卡/工具卡/经验卡
```

要求：

- 代码只进 Git。
- 知识工程只记录 repoRef、commitRef、变更摘要、经验。
- 重要变更必须关联 projectId。
- 工具类变更必须关联 toolId。

### 8.2 工具同步

当一个人做了工具：

1. 先在本地开发。
2. 达到可复用后，推到 Git。
3. 在知识工程创建或更新 ToolAsset 卡。
4. 写清楚怎么安装、怎么调用、输入输出、风险。
5. 标记状态为 testing。
6. 至少一个其他人或 Agent 试用后，记录问题。
7. 稳定后改为 approved。

没有 ToolAsset 卡的工具，默认是个人工具，不算团队资产。

### 8.3 经验同步

经验同步不要求写长文，只要求及时、结构化。

每次遇到下面情况，必须写入 lessons：

- 解决了一个卡了很久的问题。
- 写了一个别人可能复用的脚本或工具。
- Agent 生成结果明显好或明显差。
- 某个 Prompt 特别有效。
- 某个技术路线被证明不行。
- 项目中做了重要取舍。

最小格式：

```txt
问题：
场景：
做法：
结果：
适用条件：
关联项目：
关联工具：
关联代码：
```

## 9. 多项目如何体现

知识工程中，Project 是一级组织单位。

每个项目都有：

- 项目卡。
- 决策记录。
- 工具清单。
- Agent 清单。
- 经验沉淀。
- 关联 Git 仓库。
- 关联交付物。

跨项目复用规则：

- 项目内知识默认只属于项目。
- 被复用 2 次以上，提升为公司级知识候选。
- 经 owner 确认后，进入 company / engineering / business 知识区。
- 项目特有内容不能直接提升为公司级知识。

## 10. Agent 管理机制

Agent 必须被管理，不能谁想怎么跑就怎么跑。

### 10.1 Agent 进入项目

Agent 参与项目前必须明确：

- 它的任务是什么。
- 它能读哪些项目资料。
- 它能调用哪些工具。
- 它能不能写入知识。
- 哪些动作需要人工确认。

### 10.2 Agent 权限分层

| 类型 | 权限 | 例子 |
| --- | --- | --- |
| reader | 只读知识和项目上下文 | 项目问答 Agent |
| analyst | 可生成 draft 知识 | 资料分析 Agent |
| builder | 可改代码，但必须走 Git | 开发 Agent |
| reviewer | 可做检查和建议，不直接发布 | Code Review Agent |
| executor | 可调用工具 | 自动化 Agent |

默认策略：

- Agent 可以写 draft。
- Agent 不能直接发布 verified。
- Agent 不能直接删除知识。
- Agent 不能绕过 Git 改代码。
- Agent 调高风险工具必须人工确认。

### 10.3 Agent 复盘

每个重要 AgentRun 结束后，至少记录：

- 做成了什么。
- 用了哪些工具。
- 哪些 Prompt 有效。
- 哪些知识不够。
- 哪些结果需要人工修正。
- 是否产生新经验。

## 11. Agent 如何读写知识库

关键不是“知识库存在”，而是 Agent 工作前必须读，工作后必须写。

第一阶段先用流程和模板强制；第二阶段用脚本/CLI 强制；第三阶段再做 Agent Gateway。

### 11.1 Agent 启动协议

每个 Agent 开始任务前，必须先拿到任务上下文包。

上下文包包含：

- 项目卡：`projects/<project-id>/project.md`
- 项目决策：`projects/<project-id>/decisions.md`
- 项目经验：`projects/<project-id>/lessons.md`
- 项目 Agent 清单：`projects/<project-id>/agents.md`
- 项目工具清单：`projects/<project-id>/tools.md`
- Agent 卡：`agents/<agent-id>.md`
- 相关 ToolAsset：`tools/<tool-id>.md`
- 相关公司级知识：`knowledge/company`、`knowledge/engineering`、`knowledge/business`

启动顺序：

```txt
收到任务
-> 确认 projectId 和 agentId
-> 读取项目卡
-> 读取 Agent 卡
-> 读取项目工具清单
-> 读取相关知识
-> 输出任务计划
-> 执行任务
```

Agent 没有读取上下文包，不应该开始执行。

### 11.2 Agent 请求知识库信息

Agent 请求知识时，不直接问“给我所有资料”，而是按项目、任务、权限请求。

请求格式：

```yaml
projectId: zhenzhi-core
agentId: agent.builder.frontend
task: 实现 ToolAsset 卡片模板
need:
  - project_context
  - related_decisions
  - allowed_tools
  - engineering_patterns
  - known_issues
```

知识库返回上下文包：

```yaml
project:
  ref: projects/zhenzhi-core/project.md
decisions:
  - ref: projects/zhenzhi-core/decisions.md
tools:
  - ref: tools/tool.markdown-template.md
knowledge:
  - ref: knowledge/engineering/agent-run-record.md
constraints:
  - Agent 只能写 draft
  - 代码必须走 Git
  - secret 不进入 Prompt
```

第一阶段可以人工或脚本组装上下文包；后续由 Agent Gateway 自动组装。

### 11.3 Agent 写回知识库

Agent 完成任务后，必须提交知识更新建议，不直接把所有内容写成 verified。

写回分 4 类：

- AgentRun：本次执行记录。
- ProjectUpdate：项目卡状态更新。
- ToolUpdate：工具卡版本、用法、问题更新。
- KnowledgeDraft：经验、模式、问题、Prompt 草稿。

写回格式：

```yaml
runId: run.2026-06-16.001
projectId: zhenzhi-core
agentId: agent.builder.frontend
task: 实现 ToolAsset 卡片模板
codeRefs:
  - repo: company_knowledge_core
    commit: pending
toolsUsed:
  - tool.markdown-template
knowledgeUsed:
  - knowledge/engineering/tool-asset.md
outputs:
  - projects/zhenzhi-core/tools.md
lessons:
  - type: pattern
    text: 工具卡必须记录 owner、entrypoint、riskLevel、lastVerifiedAt，否则后续 Agent 无法判断能不能调用。
knowledgeGaps:
  - 缺少工具风险等级判定标准。
humanReviewRequired: true
```

写回规则：

- AgentRun 可以直接记录。
- KnowledgeDraft 可以直接写 draft。
- verified 知识必须人工确认。
- ToolAsset 从 testing 到 approved 必须 owner 确认。
- 高风险工具权限变更必须人工确认。

### 11.4 如何保证 Agent 先读知识库

分 3 个阶段保证。

第一阶段：流程强制。

- 每个任务 prompt 必须包含 projectId 和 agentId。
- `AGENTS.md` 写明：执行任务前先读项目卡、Agent 卡、工具卡。
- 每次交付必须说明读取了哪些知识。
- 没有上下文读取记录，交付不接受。

第二阶段：工具强制。

- 做一个轻量 `agent-start` 脚本。
- 输入 projectId、agentId、task。
- 脚本生成 context pack。
- Agent 只能基于 context pack 开始工作。
- 做一个 `agent-finish` 脚本。
- 任务结束生成 AgentRun 和知识更新建议。

流程：

```txt
agent-start -> 生成上下文包 -> Agent 执行 -> agent-finish -> 生成写回草稿 -> 人审核
```

第三阶段：Gateway 强制。

- Agent 只能通过 Agent Gateway 请求知识。
- Gateway 检查权限、项目范围、工具白名单。
- Gateway 自动记录 AgentRun。
- Gateway 阻止未登记工具调用。
- Gateway 阻止 secret 进入上下文。

### 11.5 每天 Agent 更新知识库

每天结束前，每个参与项目的 Agent 生成一份日更新草稿。

日更新包含：

- 今日完成了什么。
- 修改了哪些代码或文档。
- 调用了哪些工具。
- 新增了哪些经验。
- 发现了哪些知识缺口。
- 哪些工具需要更新说明。
- 哪些项目状态需要更新。

日更新不直接进入 verified，由项目 owner 或当天值班 reviewer 批量确认。

建议节奏：

```txt
白天：Agent 执行任务，记录 AgentRun
收工前：Agent 生成 Daily Knowledge Draft
第二天早上：人快速审核，确认可复用内容
每周：统一清理 stale / testing / draft
```

### 11.6 Agent 不更新知识库怎么办

把知识写回作为任务完成条件。

任务完成必须同时满足：

- 代码或交付物完成。
- AgentRun 已记录。
- 相关项目卡已更新。
- 工具变化已更新 ToolAsset。
- 可复用经验已写入 draft。
- 不产生经验也要写明 `no reusable lesson`。

没有写回，就不算完成。

## 12. 本地知识连接器

团队成员使用本地 Codex、Antigravity 或其他 AI 开发工具时，需要一个统一的小工具连接知识工程。

这个工具暂名：

```txt
zhenzhi-knowledge
```

它不是大平台，而是本地连接器，负责 5 件事：

1. 告诉本地 AI 工具知识库在哪里。
2. 注册本地 Agent 身份。
3. 注册项目、工具、运行记录。
4. 生成任务上下文包。
5. 把 Agent 产出的经验和更新写回知识库草稿。

### 12.1 本地安装后做什么

每个成员在自己电脑上安装后，先执行初始化。

```bash
zhenzhi-knowledge init
```

初始化生成本地配置：

```yaml
userId: zhenzhi.<name>
defaultAiTool: codex
defaultAgentId: agent.<name>.builder
activeProfile: local
profiles:
  local:
    backend: git
    knowledgeRepo: /Users/<user>/work/company_knowledge_core
    remote: git@example.com:zhenzhi/company_knowledge_core.git
  staging:
    backend: api
    apiBaseUrl: ${ZHENZHI_KNOWLEDGE_API_STAGING}
  production:
    backend: api
    apiBaseUrl: ${ZHENZHI_KNOWLEDGE_API_PROD}
```

配置原则：

- 地址不写死在代码里。
- 本地阶段使用 `knowledgeRepo` 和 Git remote。
- 线上阶段使用 `apiBaseUrl`。
- API 地址来自环境变量、团队配置文件或登录后的 discovery。
- 配置只保存路径、profile、身份，不保存密钥。
- token 存在系统钥匙串、环境变量或企业认证系统，不进知识库。

后续切换线上服务时，只改 profile：

```bash
zhenzhi-knowledge profile use production
```

本地 AI 工具不关心知识库是本地 Git 还是线上 API，只调用同一组命令。

### 12.2 Agent 注册

本地 AI 工具第一次接入时，先注册 Agent。

```bash
zhenzhi-knowledge agent register \
  --agent-id agent.alice.builder \
  --name "Alice Local Builder" \
  --tool codex \
  --purpose "本地开发、代码修改、工具开发"
```

注册后生成：

```txt
agents/agent.alice.builder.md
```

Agent 卡写清：

- 这个 Agent 属于谁。
- 运行在哪个本地 AI 工具里。
- 默认能参与哪些项目。
- 能调用哪些工具。
- 能不能写 draft。
- 哪些动作要人工确认。

### 12.3 项目注册

新项目开始时，项目负责人注册项目。

```bash
zhenzhi-knowledge project register \
  --project-id zhenzhi-core \
  --name "桢知知识工程" \
  --owner alice
```

生成：

```txt
projects/zhenzhi-core/project.md
projects/zhenzhi-core/decisions.md
projects/zhenzhi-core/lessons.md
projects/zhenzhi-core/agents.md
projects/zhenzhi-core/tools.md
```

后续每个 Agent 进入项目，都先读这些文件。

### 12.4 工具注册

一个人开发了可复用工具后，用连接器登记。

```bash
zhenzhi-knowledge tool register \
  --tool-id tool.doc-parser \
  --name "文档解析工具" \
  --repo git@example.com:zhenzhi/doc-parser.git \
  --entrypoint "mcp://doc-parser" \
  --risk L1 \
  --owner alice
```

生成：

```txt
tools/tool.doc-parser.md
```

工具未注册前：

- 不算团队资产。
- 不出现在项目工具清单。
- Agent 默认不能调用。

### 12.5 Agent 开始任务

Agent 每次任务前执行：

```bash
zhenzhi-knowledge start \
  --project zhenzhi-core \
  --agent agent.alice.builder \
  --task "实现 ToolAsset 模板"
```

连接器做 4 件事：

- 检查项目是否存在。
- 检查 Agent 是否注册。
- 检查 Agent 是否允许进入项目。
- 生成 context pack。

context pack 示例：

```txt
.zhenzhi/context/current.md
```

里面包含：

- 项目目标和当前状态。
- 当前任务相关决策。
- 可用工具清单。
- Agent 权限边界。
- 相关经验知识。
- 本次任务写回要求。

Codex / Antigravity 启动任务时，必须把这个 context pack 作为前置上下文。

### 12.6 Agent 完成任务

Agent 每次任务后执行：

```bash
zhenzhi-knowledge finish \
  --project zhenzhi-core \
  --agent agent.alice.builder
```

连接器生成：

```txt
runs/zhenzhi-core/run.<timestamp>.md
projects/zhenzhi-core/lessons.draft.md
projects/zhenzhi-core/project.update.draft.md
tools/<tool-id>.update.draft.md
```

finish 必须记录：

- 完成内容。
- 代码引用。
- 工具调用。
- 知识引用。
- 新经验。
- 知识缺口。
- 是否需要人工审核。

### 12.7 本地 AI 工具如何接入

不同 AI 工具接入方式不同，但核心都一样：启动前读 context pack，结束后写 draft。

Codex 接入：

- 工作区 `AGENTS.md` 写明必须使用 `zhenzhi-knowledge start/finish`。
- 任务 prompt 带上 projectId、agentId。
- Codex 先读 `.zhenzhi/context/current.md` 再执行。

Antigravity 接入：

- 在它的项目规则或启动提示里写同样协议。
- 每次任务前由用户或脚本生成 context pack。
- 任务结束后调用 finish 写回草稿。

其他 AI 工具接入：

- 只要能读本地文件，就读 context pack。
- 只要能调用命令，就用 start/finish。
- 不能调用命令的，也可以人工复制 context pack。

### 12.8 同步机制

第一阶段知识库本身可以是 Git 仓库。

同步流程：

```txt
zhenzhi-knowledge sync pull
-> 获取团队最新知识
zhenzhi-knowledge start
-> 生成本次上下文
Agent 工作
zhenzhi-knowledge finish
-> 生成写回草稿
人审核
zhenzhi-knowledge sync push
-> 推送团队知识更新
```

规则：

- 每天开始前先 pull。
- 每次任务前 start。
- 每次任务后 finish。
- 每天结束前 push 已审核更新。
- 冲突先人工处理，不让 Agent 自动覆盖。

### 12.9 连接器命令清单

第一版只需要这些命令：

```bash
zhenzhi-knowledge init
zhenzhi-knowledge status
zhenzhi-knowledge sync pull
zhenzhi-knowledge sync push
zhenzhi-knowledge agent register
zhenzhi-knowledge project register
zhenzhi-knowledge tool register
zhenzhi-knowledge start
zhenzhi-knowledge finish
zhenzhi-knowledge review
```

`review` 用来把 draft 提升为 verified，必须人工执行。

### 12.10 连接器和未来平台的关系

连接器是第一阶段最小系统。未来平台上线后，它仍然可以保留。

演进路径：

```txt
本地 Markdown/Git 知识库
-> zhenzhi-knowledge 本地连接器
-> 远程 Knowledge API
-> Agent Gateway
-> 完整知识工程平台
```

所以现在不是先做大平台，而是先做一个能把本地 AI 工具、团队流程、知识库连接起来的小工具。

## 13. 安全与权限

第一阶段不做复杂权限系统，但必须有基本规则。

数据分级：

- public：公开资料。
- internal：公司内部资料。
- project：项目资料。
- customer_confidential：客户敏感资料。
- secret：密钥、账号、合同敏感项。

规则：

- secret 不进入知识工程正文，只保存引用和负责人。
- 客户敏感资料默认只在项目范围使用。
- 工具卡可以写需要什么密钥，但不能写密钥值。
- Agent 只能读取 allowedKnowledgeScopes。
- 高风险工具必须人工确认。
- 所有工具发布和权限变更要有 AuditLog。

## 14. 知识如何保持最新

知识不会自动可靠更新，必须靠流程。

### 14.1 每日轻量更新

每个人每天结束前只做 3 件事：

- 更新自己负责项目的 currentFocus。
- 把当天可复用经验写到 lessons。
- 把新工具或工具变化更新到 ToolAsset。

### 14.2 每周知识整理

每周一次，团队做 30 分钟知识整理：

- 哪些 draft 可以变 verified。
- 哪些知识已经 stale。
- 哪些工具可以从 testing 变 approved。
- 哪些本地工具应该推到 Git。
- 哪些项目经验可以提升为公司级知识。

### 14.3 Git 触发更新

每次 Git 重要提交后，知识工程应记录：

- 关联 projectId。
- 关联 toolId。
- 变更解决了什么问题。
- 是否产生新经验。
- 是否影响 Agent 使用方式。

后续可以做自动化：

```txt
Git push / PR merged -> Agent 读取 commit diff -> 生成知识更新建议 -> 人审核 -> 写回知识工程
```

### 14.4 过期机制

知识项需要 lastReviewedAt。

触发 stale：

- 关联工具版本变化。
- 关联项目状态变化。
- 关联代码重构。
- 3 个月未复审。
- 被新的经验或决策替代。

## 15. 实施任务清单

按当前方案审查后，第一阶段任务应聚焦在“OKF-compatible 知识仓 + 本地连接器 + Agent 工作流强制”三件事。暂不做大平台。

### 15.1 P0：基础规范

- [x] 确认知识仓采用 OKF-compatible Markdown/YAML。
- [x] 确认所有知识文件必须有 `type` frontmatter。
- [x] 确认桢知扩展字段：`owner`、`status`、`scope`、`riskLevel`、`allowedAgents`、`allowedProjects`。
- [x] 确认第一批 `type`：Project、Agent、ToolAsset、KnowledgeItem、SourceMaterial、AgentRun、Decision、Workflow、Prompt、AuditLog。
- [x] 定义 `status` 枚举：draft、testing、verified、approved、stale_candidate、stale、deprecated、blocked、rejected。
- [x] 定义数据分级：public、internal、project、customer_confidential、secret。
- [x] 定义工具风险等级：L1-L5。

验收标准：

- 新增知识文件能被脚本验证 frontmatter。
- 未包含 `type` 的文件不能通过检查。
- unknown frontmatter 字段必须被保留，不能被工具删除。

### 15.2 P0：目录和模板

- [x] 创建根 `index.md` 和 `log.md`。
- [x] 创建 `projects/index.md`。
- [x] 创建 `agents/index.md`。
- [x] 创建 `tools/index.md`。
- [x] 创建 `knowledge/index.md`。
- [x] 创建 `runs/index.md`。
- [x] 创建 Project 模板。
- [x] 创建 Agent 模板。
- [x] 创建 ToolAsset 模板。
- [x] 创建 KnowledgeItem 模板。
- [x] 创建 AgentRun 模板。
- [x] 创建 Decision 模板。
- [x] 创建 lessons 模板。

验收标准：

- 新项目可通过模板生成完整项目目录。
- 新 Agent 可通过模板生成 Agent 卡。
- 新工具可通过模板生成 ToolAsset 卡。

### 15.3 P0：当前资产盘点

- [x] 登记当前所有并行项目。
- [x] 每个项目写清 owner、members、goal、scope、currentFocus、relatedRepos。
- [x] 登记当前每个人本地可复用工具。
- [x] 每个工具写清 owner、repoRef、本地路径、entrypoint、status、riskLevel。
- [x] 登记当前会使用的本地 AI 工具：Codex、Antigravity 等。
- [x] 为每个人创建至少一个本地 Agent 卡。
- [x] 把已有关键经验写入 lessons draft。

验收标准：

- 团队能回答：现在有哪些项目、有哪些工具、有哪些 Agent、谁负责。
- 本地工具未登记前，不视为团队资产。

### 15.4 P0：`zhenzhi-knowledge` 本地连接器骨架

- [x] 实现 `zhenzhi-knowledge init`。
- [x] 实现 `zhenzhi-knowledge status`。
- [x] 实现 profile 配置：local、staging、production。
- [x] 支持 `knowledgeRepo` 本地路径。
- [x] 支持 Git remote 配置。
- [x] 支持 API 地址从环境变量读取。
- [x] 禁止在配置和知识文件中保存 token、密钥、账号密码。

验收标准：

- 本地安装后能定位知识仓。
- 地址不写死在代码中。
- 切换线上服务只需要切 profile。

### 15.5 P0：注册命令

- [x] 实现 `agent register`。
- [x] 实现 `project register`。
- [x] 实现 `tool register`。
- [x] 注册时自动生成 OKF-compatible Markdown 文件。
- [x] 注册时自动更新相关 `index.md`。
- [x] 注册时自动追加 `log.md`。

验收标准：

- 一个新人能在本地注册自己的 Agent。
- 一个新项目能生成标准项目目录。
- 一个新工具能进入工具目录并被项目引用。

### 15.6 P0：Agent 启动和写回

- [x] 实现 `start`。
- [x] `start` 输入 projectId、agentId、task。
- [x] `start` 检查项目是否存在。
- [x] `start` 检查 Agent 是否存在。
- [x] `start` 检查 Agent 是否允许进入项目。
- [x] `start` 生成 `.zhenzhi/context/current.md`。
- [x] 实现 `finish`。
- [x] `finish` 生成 AgentRun。
- [x] `finish` 生成 ProjectUpdate draft。
- [x] `finish` 生成 KnowledgeDraft。
- [x] `finish` 生成 ToolUpdate draft。

验收标准：

- Codex / Antigravity 开始任务前能读取 context pack。
- 任务结束后必须产生 AgentRun。
- 无写回草稿的任务不算完成。

### 15.7 P1：同步和审核

- [x] 实现 `sync pull`。
- [x] 实现 `sync push`。
- [x] 实现冲突检测。
- [x] 冲突不允许 Agent 自动覆盖。
- [x] 实现 `review`。
- [x] `review` 支持 draft -> verified。
- [x] `review` 支持 testing -> approved。
- [x] `review` 写入 AuditLog。

验收标准：

- 每天开始可拉取团队最新知识。
- 每天结束可推送已审核知识。
- draft 提升为 verified 必须人工执行。

### 15.8 P1：本地 AI 工具接入

- [x] 在知识工程 `AGENTS.md` 写入 start/finish 强制规则。
- [x] 为 Codex 准备项目启动提示模板。
- [x] 为 Antigravity 准备项目启动提示模板。
- [x] 每次任务 prompt 必须包含 projectId、agentId。
- [x] 每次交付必须说明读取了哪些知识。
- [x] 每次交付必须说明写回了哪些草稿。

验收标准：

- Codex 不读 context pack 就不能进入正式任务流程。
- Antigravity 不读 context pack 就不能进入正式任务流程。
- 人审核交付时能看到知识引用和写回记录。

### 15.9 P1：索引和检索

- [x] 实现 frontmatter 扫描器。
- [x] 生成本地 SQLite 索引。
- [x] 支持按 projectId 查询。
- [x] 支持按 agentId 查询。
- [x] 支持按 toolId 查询。
- [x] 支持按 status 查询。
- [x] 支持按 riskLevel 查询。
- [x] 支持全文搜索。

验收标准：

- 能快速查询某项目相关 Agent、工具、知识、运行记录。
- 能快速查询待审核 draft 和过期 stale。

### 15.10 P2：RAG 和语义召回

- [x] 定义 chunk 策略。
- [x] 定义哪些内容可进入向量库。
- [x] secret 永不进入向量库。
- [x] customer_confidential 默认不进入公司级向量库。
- [x] 建立本地向量索引原型。
- [x] `start` 可从全文检索和向量检索生成 context pack。
- [x] Agent 输出必须保留 sourceRef。

验收标准：

- RAG 只负责召回上下文，不负责决定真相。
- Agent 生成内容可追溯到 sourceRef。

### 15.11 P2：线上化准备

- [x] 设计 Knowledge API。
- [x] 设计 Agent Gateway。
- [x] 设计认证和 token 管理。
- [x] 设计权限模型。
- [x] 设计审计表。
- [x] 设计对象存储方案。
- [x] 设计从 Git Bundle 到数据库的迁移策略。

验收标准：

- 本地连接器可从 `backend: git` 切到 `backend: api`。
- 线上化不破坏第一阶段知识文件。

### 15.12 P1：质量标准和角色责任

- [x] 定义 Project Owner 责任：项目卡、项目决策、项目经验、项目状态。
- [x] 定义 Tool Owner 责任：ToolAsset、版本、风险等级、使用说明、废弃策略。
- [x] 定义 Knowledge Reviewer 责任：draft 审核、verified 发布、stale 清理。
- [x] 定义 Security Reviewer 责任：secret、customer_confidential、高风险工具审批。
- [x] 定义 `verified` 知识审核标准。
- [x] 定义 ToolAsset 从 testing 到 approved 的审核标准。
- [x] 定义 AgentRun 是否合格的验收标准。
- [x] 定义每周知识整理会的固定议程。
- [x] 定义未写回、未审核、未同步的处理规则。

验收标准：

- 每条 verified 知识能追溯 reviewer。
- 每个 approved 工具能追溯 owner 和批准记录。
- 每个项目至少有一个明确 Project Owner。

### 15.13 P1：冲突处理机制

- [x] 定义 ConflictRecord 类型。
- [x] 定义 Git 文件冲突处理流程。
- [x] 定义事实冲突处理流程。
- [x] 定义决策冲突处理流程。
- [x] 定义经验冲突处理流程。
- [x] `sync pull` 发现冲突时生成 ConflictRecord。
- [x] 冲突解决必须写入 AuditLog。
- [x] 冲突解决后更新相关 KnowledgeItem 状态。

验收标准：

- Agent 不允许自动覆盖冲突。
- 每个冲突都有 owner、原因、处理结果。
- 被冲突影响的知识不能继续保持 verified 而无说明。

### 15.14 P1：策略文件和权限表达

- [x] 定义 Policy 文件格式。
- [x] 定义 Agent 读权限策略。
- [x] 定义 Agent 写权限策略。
- [x] 定义 ToolAsset 调用策略。
- [x] 定义 project / customer_confidential / secret 的访问规则。
- [x] `start` 根据 Policy 过滤 context pack。
- [x] `tool register` 根据风险等级生成默认策略。
- [x] `review` 支持策略变更审核。

示例：

```yaml
---
type: Policy
title: Frontend Builder Policy
agentId: agent.alice.builder
scope: project
allowedProjects:
  - zhenzhi-core
allowedKnowledgeScopes:
  - company
  - engineering
  - project:zhenzhi-core
allowedToolRiskLevels:
  - L1
  - L2
write:
  knowledge: draft
  toolAsset: draft
requiresApproval:
  - publish_verified
  - call_L3_tool
  - access_customer_confidential
---
```

验收标准：

- Agent 权限不是散落在描述文字里，而是有可解析 Policy。
- `start` 输出的 context pack 已经过权限过滤。
- 高风险动作能明确判断是否需要人工确认。

### 15.15 P1：可观测性和运营指标

- [x] 定义 MetricsReport 类型。
- [x] 统计每日 `start` 次数。
- [x] 统计每日 `finish` 次数。
- [x] 统计未 finish 的任务数。
- [x] 统计 draft 积压数。
- [x] 统计 stale 知识数。
- [x] 统计 testing 工具数。
- [x] 统计 approved 工具复用次数。
- [x] 统计 AgentRun 成功率和失败率。
- [x] 统计未登记工具调用尝试。
- [x] 每周生成知识工程运营报告。

验收标准：

- 能判断知识工程是否被实际使用。
- 能发现团队没有写回、没有审核、工具无人维护的问题。
- 能用数据判断哪些工具和知识真正有价值。

### 15.16 P2：Agent 评测体系

- [x] 定义 EvalCase 类型。
- [x] 定义 EvalRun 类型。
- [x] 为关键 Agent 建立最小评测集。
- [x] 为关键工具建立回归测试样例。
- [x] 记录 Agent 失败案例。
- [x] 记录 Prompt 版本和评测结果。
- [x] 记录 ToolAsset 版本和评测结果。
- [x] 每次 Agent/Prompt/Tool 重要变化后运行评测。
- [x] 评测失败阻止 approved 状态升级。

验收标准：

- Agent 能力变化有数据可比。
- Prompt 和工具升级不会只靠主观感觉。
- 失败案例能回流为 KnowledgeItem。

### 15.17 P2：自动 stale 检测

- [x] 解析 ToolAsset 版本变化。
- [x] 解析 Git commitRef 变化。
- [x] 解析 Project 状态变化。
- [x] 解析 SourceMaterial 更新时间变化。
- [x] 自动找出受影响 KnowledgeItem。
- [x] 自动标记 stale candidate。
- [x] reviewer 确认后变为 stale。
- [x] stale 处理结果写入 AuditLog。

验收标准：

- 工具升级后，相关使用说明和经验会被标记复查。
- 项目状态变化后，相关项目知识会被标记复查。
- 过期知识不会无声留在 verified。

### 15.18 P2：备份、恢复和审计查询

- [x] 定义 Git 仓库备份策略。
- [x] 定义线上数据库备份策略。
- [x] 定义对象存储备份策略。
- [x] 定义误删恢复流程。
- [x] 定义按 projectId 查询审计记录。
- [x] 定义按 agentId 查询审计记录。
- [x] 定义按 toolId 查询审计记录。
- [x] 定义按 KnowledgeItem 查询审计记录。
- [x] 定义审计记录保留周期。

验收标准：

- 误删知识可恢复。
- 工具误发布可回溯。
- Agent 越权或失败可追踪。
- 客户敏感资料访问可审计。

### 15.19 P3：扩展性和迁移

- [x] 定义 OKF 文件到数据库对象的映射。
- [x] 定义数据库对象回写 OKF 文件的策略。
- [x] 定义多团队命名空间。
- [x] 定义多客户隔离策略。
- [x] 定义 API 版本策略。
- [x] 定义连接器兼容旧版本服务的策略。
- [x] 定义插件式 ToolAsset 类型扩展。
- [x] 定义跨知识仓引用规则。

验收标准：

- 从 Git Bundle 迁移到线上平台时不重写知识。
- 多团队、多项目、多客户扩展时不破坏现有 ID。
- 本地连接器和线上 API 可以独立演进。

### 15.20 暂不做

- [x] 暂不做完整 Web 平台。
- [x] 暂不做复杂图数据库。
- [x] 暂不做自动发布 verified 知识。
- [x] 暂不做 Agent 自动处理 Git 冲突。
- [x] 暂不把 secret、token、客户敏感正文放进 RAG。
- [x] 暂不让 Agent 直接调用未登记工具。

## 16. 建设路线

### 16.0 运营治理细则

#### 角色责任

Project Owner 负责项目卡、项目状态、项目决策、项目经验和 relatedRepos 的准确性。项目状态变化后，Project Owner 必须触发 stale 检查，必要时更新 Project、Decision、KnowledgeItem。

Tool Owner 负责 ToolAsset 的 repoRef、entrypoint、version、riskLevel、使用说明、已知问题、评测记录和废弃策略。ToolAsset 从 testing 到 approved 前，必须没有失败 EvalRun，且必须有 Tool Owner 或 reviewer 的 AuditLog。

Knowledge Reviewer 负责 draft 到 verified、stale_candidate 到 stale 或 verified 的审核。verified 知识必须有 sourceRef、confidence、status、owner、reviewer、reviewedAt；没有证据链的内容只能保持 draft。

Security Reviewer 负责 secret、customer_confidential、高风险工具、跨项目访问和线上 token 策略。secret 不进入知识文件、RAG、日志、AuditLog 正文；customer_confidential 默认不得进入公司级检索索引。

#### 审核标准

verified KnowledgeItem 必须满足：有明确来源、可复查、非 secret、非未授权客户敏感正文、scope 合理、confidence 明确、没有被更新决策或 stale candidate 覆盖。

知识工程不是原始资料仓库。Agent 不允许把文档、聊天记录、截图、转录、导出文件或临时笔记直接丢进知识目录。可复用知识必须先整理为结构化 Markdown/YAML 对象，放入 `knowledge/<category>/`，并带 `type`、`status`、`owner`、`scope`、`sourceRef`、`confidence` 等字段。未审核内容只能保持 draft，不能进入 verified 或 approved。

approved ToolAsset 必须满足：owner 明确、repoRef 明确、entrypoint 明确、riskLevel 合法、使用说明存在、无阻断级 knownIssues、无失败 EvalRun。L3-L5 工具必须经过 Security Reviewer 或等效人工审批。

合格 AgentRun 必须满足：projectId、agentId、task/summary、contextRefs、knowledgeUsed/sourceRef、toolsUsed、result、humanReview 状态完整。没有 start context 或 finish 写回的任务不能视为正式完成。

#### 冲突流程

事实冲突：创建 ConflictRecord，affectedRefs 指向冲突 KnowledgeItem 或 SourceMaterial。解决后保留正确事实为 verified，错误或过时事实改为 stale 或 rejected，并写 AuditLog。

决策冲突：新 Decision 不覆盖旧 Decision；旧 Decision 标记 stale 或 deprecated，正文保留取代关系和原因。

经验冲突：经验类 KnowledgeItem 允许并存，但必须标注适用条件、sourceRef 和 confidence。不可泛化的经验保持 project scope，不上升为 company scope。

#### 访问规则

public 可进入公司级索引和 RAG。internal 默认仅公司成员和已注册 Agent 可读。project 只允许 allowedProjects 或匹配 projectId 的 Agent 读取。customer_confidential 默认只允许明确授权项目读取，不进入公司级 RAG。secret 不允许进入任何知识文件、索引、RAG、日志或审计正文。

ToolAsset 默认策略由 riskLevel 生成：L1-L2 为 agent_policy_allowed；L3-L5 为 approval_required。所有实际调用仍必须同时通过 Agent Policy、Project 范围、ToolAsset allowedAgents/allowedProjects 和 riskLevel 检查。

#### 评测门禁

EvalCase 指向 targetRef。EvalRun 记录 targetRef、targetVersion、result 和 score。Agent、Prompt、ToolAsset 的重要变化必须产生或复用 EvalCase；存在失败 EvalRun 的目标不得升级为 approved。

#### 运营节奏

每周生成 MetricsReport，检查 start/finish 数、unfinishedTasks、draftBacklog、stale/stale_candidate、testing/approved tools、tool invocation、AgentRun 成功失败。知识整理会固定处理 draft、testing、stale_candidate、open ConflictRecord 和失败 EvalRun。

未写回：AgentRun 缺失或没有 draft 更新，Project Owner 追补。未审核：draft/testing/stale_candidate 超过一周，Reviewer 必须处理。未同步：Git 或 API profile 同步失败，创建 ConflictRecord 或运维事项，不允许 Agent 自动覆盖。

#### 备份和保留

Git 仓库是第一阶段知识真源，必须至少每天远程备份。线上数据库未来只保存 OKF 元数据、权限、索引和审计查询副本，必须每日快照、保留 30 天。对象存储只保存大文件和原始附件引用，必须按 sourceRef 反查到知识对象。

AuditLog 最少保留 365 天；涉及客户敏感资料、高风险工具、权限变更、approved 发布的审计记录长期保留。审计正文不保存 secret。

#### 迁移和扩展

OKF 文件到数据库映射规则：文件路径是稳定 objectId；frontmatter 映射为结构化字段；Markdown body 作为正文版本；Git commitRef 作为变更证据。数据库回写 OKF 时必须保留未知字段和原路径。

多团队命名空间使用 `teamId/objectType/objectId`；多客户隔离使用 customerId、projectId、scope 和 Policy 共同判断。跨知识仓引用使用 `knowledge://<repo>/<path>#<anchor>`。

API 版本使用 `/v0/` 前缀；连接器必须兼容当前 minor 版本，不兼容时降级到 Git backend。ToolAsset 类型扩展通过 `toolType`、`capabilities`、`inputSchemaRef`、`outputSchemaRef` 字段表达，不改核心对象。

### 第 1 周：统一工作法

目标：先让团队资产不再散。

交付：

- `zhenzhi-knowledge` 命令骨架。
- `init` / `status` / `agent register` / `project register` / `tool register`。
- 项目卡模板。
- Agent 卡模板。
- ToolAsset 卡模板。
- lessons 模板。
- 当前所有项目登记。
- 当前所有可复用工具登记。

### 第 2-4 周：形成协作闭环

目标：项目、工具、经验能持续更新。

交付：

- `start` 生成 context pack。
- `finish` 生成 AgentRun 和知识更新草稿。
- `sync pull/push` 同步知识库。
- 每个项目有 weekly update。
- 每个工具有 owner 和状态。
- 每个 Agent 有权限说明。
- 每周知识整理会。
- 重要 Git 变更能回写知识。

### 第 2 个月：Agent 化

目标：让 Agent 参与知识沉淀。

交付：

- AgentRun 记录。
- Codex / Antigravity 接入本地连接器。
- Git diff 生成知识更新建议。
- 工具 README 自动生成 ToolAsset 草稿。
- 项目会议或聊天生成 lessons 草稿。
- 人工审核后发布 verified 知识。

### 第 3 个月：产品化准备

目标：把工作法沉淀成未来系统设计。

交付：

- 项目管理系统对象模型。
- Agent 管理对象模型。
- Tool Registry 对象模型。
- KnowledgeItem 状态机。
- 权限和审计最小模型。

## 17. 当前方案需要改进的点

原方案方向合理，但偏平台化、偏数据治理，离当前团队痛点有距离。

需要调整为：

- 从“大架构”改为“团队每日工作流”。
- 从“知识平台”改为“项目 + Agent + 工具 + 经验”四类资产治理。
- 从“未来系统对象”改为“现在 Markdown/YAML 可执行模板”。
- 从“所有数据统一入库”改为“真源系统引用 + 知识摘要 + 经验沉淀”。
- 从“Agent 能力描述”改为“Agent 权限、运行记录、复盘写回”。
- 从“工具知识”改为“ToolAsset 工具资产管理”。

## 18. 当前最小共识

第一阶段只坚持 6 条：

1. 每个项目必须有项目卡。
2. 每个可复用工具必须有 ToolAsset 卡。
3. 每个 Agent 必须有 Agent 卡。
4. 每次重要 Agent 执行必须有 AgentRun 记录。
5. 每周必须把个人经验提升为团队知识。
6. 代码进 Git，知识工程只保存引用、摘要、决策和经验。
7. Agent 开始任务前必须读取上下文包。
8. Agent 结束任务后必须提交知识更新建议。
9. 本地 AI 工具必须通过 `zhenzhi-knowledge` 连接知识工程。
