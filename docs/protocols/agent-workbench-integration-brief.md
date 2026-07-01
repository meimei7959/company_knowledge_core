# Agent 工作台对接说明

本文档给开发 Agent 工作台的同事使用。目标是先理解本项目的定位，再按当前可用协议把工作台接入中央处理器。

本文档不是 Agent 工作台的产品需求文档，不限定工作台内部要做成什么形态。它只定义中央处理器和工作台之间必须对齐的协作边界、数据对象、任务流转和写回协议。

飞书文档：

```txt
https://www.feishu.cn/docx/YaMudOEXjoHjMSxcEZdcnORYnKh
```

相关细节文档：

- 架构边界：[Central Processor And Agent Ring](../architecture/central-processor-and-agent-ring.md)
- 通信协议：[Agent Ring Communication Protocol](agent-ring-communication-protocol.md)
- 任务调度：[Task Dispatch Model](../scheduler/task-dispatch-model.md)
- 上下文同步：[Project Context Sync Protocol](project-context-sync-protocol.md)

## 1. 项目定位

本项目不是单纯的知识库，也不是 Agent 工作台本体。

本项目是桢知 AI-native 公司的中央处理器，包含两件事：

1. 中央调度器：接收飞书入口、项目创建、资料上传、会议纪要、工程请求，把它们变成可追踪任务。
2. 知识工程底座：保存项目、Agent、Runner、任务、原始材料、结构化知识、审批、审计和执行结果。

Agent 工作台，也就是 Agent Ring，不在本项目内实现。它是安装在每台电脑上的 Agent 产品和执行工作台。它可以有自己的订阅、Agent 配置、Codex / Claude / 本地模型接入、Skill 管理、工具管理、权限管理、日志、UI、自动化和其他本机能力，这些由工作台项目自行设计。

对中央处理器来说，关键不是工作台内部怎么做，而是每台电脑能通过工作台注册成一个可信 Runner，从中央处理器领取任务，驱动本机能力完成任务，最后把结果、证据、状态和后续动作写回中央处理器。

一句话理解：

```txt
飞书机器人 = 人机入口
中央处理器 = 调度器 + 知识工程
Agent 工作台 = 每台电脑上的 Agent 产品和执行工作台
电脑 = 分布式处理器
Codex / Claude / 本地模型 / 工具 = 本机执行引擎
```

## 2. 本项目负责什么

中央处理器负责：

- 项目创建与项目初始化任务。
- 项目 Agent 登记，包括项目经理 Agent、知识工程 Agent、执行 Agent。
- Runner 注册表，包括电脑、能力、可用 Agent、可访问项目、仓库、数据范围、心跳和负载。
- 任务路由状态机，包括 `pending`、`waiting_runner`、`processing`、`waiting_acceptance`、`changes_requested`、`blocked`、`done`、`rejected`。
- 任务租约，避免多个 Runner 同时处理同一个任务。
- 任务上下文包，给 Runner 提供项目、任务、来源资料、历史决策、相关知识和验收标准。
- 结果写回，包括 TaskResult、AgentRun、证据、产物引用、知识草稿、后续动作。
- 审批、Review、审计和通知。

中央处理器不负责：

- 在本地启动 Codex 或 Claude。
- 管理每台电脑的进程。
- 保存本地密钥、模型 API key、浏览器 cookie、IDE 状态。
- 决定 Agent 工作台是客户端、守护进程、菜单栏程序还是 CLI。
- 决定 Agent 工作台自己的订阅体系、Agent 配置体系、模型接入体系、Skill 管理方式或产品 UI。
- 规定工作台内部如何管理本机 Agent、Skill、工具、模型、任务队列、账户、订阅或权限。
- 替代 Git 仓库保存项目源码。

## 3. Agent 工作台自身范围和接入要求

Agent 工作台是独立产品，具体产品范围由 Agent 工作台开发同学决定。下面只是说明它可能包含的能力，不是中央处理器对工作台的功能清单，也不是验收边界。

它可以包括但不限于：

- 本机 Agent 的创建、配置、启停和能力管理。
- Codex、Claude、本地模型、浏览器、IDE、脚本和其他执行引擎的接入。
- Skill、工具、MCP、插件、私有能力包的安装、启用、升级和权限管理。
- 订阅、授权、账户、设备绑定和本地安全存储。
- 任务列表、执行日志、异常恢复、人工确认、无人值守模式和产品 UI。

本文档不规定这些内部产品设计。工作台可以比这里列得更多，也可以先只实现最小闭环。

中央处理器只关心一个核心目的：工作台把一台电脑变成可被中央调度、可审计、可迁移上下文的分布式执行节点。

也就是说，工作台内部可以围绕自己的产品目标继续扩展，例如订阅体系、Agent 市场、技能包管理、模型路由、工具授权、本机自动化、执行日志和人机协作界面。中央处理器不介入这些产品设计，只要求它们在执行中央任务时能够形成可追踪、可恢复、可审计的结果。

因此，当工作台要接入中央处理器时，必须满足下面这条对接链路。

中央处理器接入要求：

1. 注册 Runner。
2. 定期心跳。
3. 拉取可执行任务。
4. 领取任务并拿到租约。
5. 拉取任务上下文。
6. 在本机启动执行引擎，例如 Codex。
7. 按任务要求处理项目、代码、文档、会议纪要或知识沉淀。
8. 写回 TaskResult、证据、产物、状态和后续动作。
9. 任务失败时写回失败原因，而不是静默丢任务。

工作台可以有人值守，也可以无人值守；可以是客户端、守护进程、菜单栏程序、CLI 或组合形态。中央处理器不关心它内部如何实现，只关心 Runner 是否在线、是否具备能力、是否有权限、是否按协议写回。

## 4. 当前项目创建闭环

飞书机器人里创建项目成功后，中央处理器会自动做这些事情：

1. 创建 Project。
2. 创建 `launch.md` 项目启动清单。
3. 创建默认项目 Agent：
   - `agent.<projectId>.project-manager`
   - `agent.<projectId>.knowledge-engineering`
   - `agent.<projectId>.executor`
4. 创建项目初始化任务：
   - taskId: `project-init-<projectId>`
   - taskType: `project_initialization`
   - requiredCapabilities: `codex`, `git`, `knowledge_sync`, `project_initialization`
5. 如果 Agent Ring 未启用，任务状态为 `waiting_runner`。
6. 如果已登记默认 Runner，任务会写入 `assignedRunner`。

`waiting_runner` 的含义不是失败，而是：

- 中央处理器已把任务准备好；
- 目前没有自动工作台接管；
- 需要临时 Runner 或人工启动本地 Codex 接管；
- 接管后仍然要通过任务协议写回结果。

## 5. 短期接入方式：临时 Runner

在正式 Agent 工作台完成前，可以先用 CLI 登记当前电脑：

```bash
python -m zhenzhi_knowledge \
  --root /knowledge \
  runner register \
  --runner-id runner.meimei-mac-codex \
  --name "梅晓华 Mac 本地 Codex" \
  --host-type mac \
  --mode manual \
  --agent agent.agent-hub.executor \
  --capability codex \
  --capability git \
  --capability knowledge_sync \
  --capability project_initialization \
  --project agent-hub \
  --repo https://github.com/meimei7959/company_knowledge_core.git \
  --data-scope company
```

心跳：

```bash
python -m zhenzhi_knowledge \
  --root /knowledge \
  runner heartbeat \
  --runner-id runner.meimei-mac-codex \
  --status online
```

这个方式适合现在测试闭环。正式工作台上线后，应改为 HTTP API 接入。

## 6. 正式对接 API

线上服务地址：

```txt
https://zknowai.com/knowledge-api
```

除飞书事件入口外，API 需要鉴权。工作台不要把 token 写入知识库；token 应保存在本地安全存储或 Secret Manager。

### 6.1 健康检查

```http
GET /health
```

成功返回：

```json
{
  "ok": true,
  "problems": []
}
```

### 6.2 注册 Runner

```http
POST /v0/runners/register
```

请求：

```json
{
  "runnerId": "runner.meimei-mac-codex",
  "name": "梅晓华 Mac 本地 Codex",
  "hostType": "mac",
  "mode": "manual",
  "agents": ["agent.agent-hub.executor"],
  "capabilities": ["codex", "git", "knowledge_sync", "project_initialization"],
  "availableProjects": ["agent-hub"],
  "repoAccess": ["https://github.com/meimei7959/company_knowledge_core.git"],
  "dataScopes": ["company"],
  "ringVersion": "0.1.0"
}
```

返回：

```json
{
  "apiVersion": "v0.1",
  "kind": "Runner",
  "runnerRef": "runners/runner.meimei-mac-codex.md"
}
```

字段说明：

- `runnerId`：一台电脑或一个工作台实例的稳定 ID。
- `agents`：这台电脑可执行的 Agent。
- `capabilities`：调度能力标签，任务会按它匹配。
- `availableProjects`：允许处理的项目。
- `repoAccess`：这台电脑可访问的仓库。
- `dataScopes`：允许读取的数据范围。
- `mode`：`manual` 表示有人确认后执行；`unattended` 表示可无人值守。

### 6.3 Runner 心跳

```http
POST /v0/runners/heartbeat
```

请求：

```json
{
  "runnerId": "runner.meimei-mac-codex",
  "status": "online",
  "load": "0",
  "capabilities": ["codex", "git", "knowledge_sync", "project_initialization"],
  "availableProjects": ["agent-hub"]
}
```

`status` 可用值：

- `online`
- `busy`
- `offline`
- `degraded`

工作台建议每 30 到 60 秒心跳一次。执行任务时可上报 `busy`。

### 6.4 查询任务

```http
GET /v0/tasks?status=waiting_runner&assignee=agent.agent-hub.project-manager
GET /v0/tasks?status=pending
```

短期实现可以先轮询：

1. 查 `pending`。
2. 查 `waiting_runner`。
3. 过滤 `requiredCapabilities`、`availableProjects`、`assignedRunner`。
4. 只领取自己能处理的任务。

后续中央调度器成熟后，可以改成服务端分配或推送。

### 6.5 领取任务

```http
POST /v0/tasks/claim
```

请求：

```json
{
  "taskId": "project-init-agent-hub",
  "runnerId": "runner.meimei-mac-codex",
  "expectedVersion": 1,
  "leaseSeconds": 600
}
```

成功后中央处理器会：

- 校验 Runner 在线；
- 校验项目和能力是否满足任务要求；
- 校验 secretRef 是否就绪；
- 设置任务状态为 `processing`；
- 设置 `assignedRunner`、`leaseOwner`、`leaseExpiresAt`、`heartbeatAt`；
- 返回 `leaseToken`。

工作台必须保存 `leaseToken`，后续 pull、heartbeat、finish 都要带上。不要把 `leaseToken` 写进知识库文件。

### 6.6 任务心跳

```http
POST /v0/tasks/heartbeat
```

请求：

```json
{
  "taskId": "project-init-agent-hub",
  "runnerId": "runner.meimei-mac-codex",
  "leaseToken": "<leaseToken>",
  "leaseSeconds": 600
}
```

任务运行时间较长时必须续租。租约过期后，中央处理器可以把任务交给其他 Runner。

### 6.7 拉取任务上下文

```http
POST /v0/tasks/pull
```

请求：

```json
{
  "taskId": "project-init-agent-hub",
  "runnerId": "runner.meimei-mac-codex",
  "leaseToken": "<leaseToken>"
}
```

拉取时任务应已经是 `processing`。中央处理器会生成任务上下文包，包含：

- Project。
- ProjectTask 或 KnowledgeTask。
- SourceMaterial。
- expectedOutput。
- 相关项目文件和历史结果。
- 约束和 Review 要求。

工作台必须先让执行 Agent 读取上下文包，再开始执行。

### 6.8 完成任务

```http
POST /v0/tasks/finish
```

请求：

```json
{
  "taskId": "project-init-agent-hub",
  "runnerId": "runner.meimei-mac-codex",
  "leaseToken": "<leaseToken>",
  "executorAgent": "agent.agent-hub.executor",
  "result": "done",
  "summary": "已完成项目初始化检查，补齐 README/AGENTS 状态，记录待补事项。",
  "outputRefs": ["projects/agent-hub/launch.md"],
  "knowledgeRefs": ["knowledge/engineering/feishu-card-implementation-runbook-20260618.md"],
  "evidenceRefs": ["projects/agent-hub/tasks/project-init-agent-hub.md"],
  "nextActions": ["等待 Agent Ring 正式工作台接入后改为自动领取任务"],
  "testsOrChecks": ["python3 -m unittest tests.test_cli"]
}
```

中央处理器会创建 TaskResult，并根据质量评价和验收策略更新任务路由状态。

允许结果状态：

- `submitted`
- `done`
- `blocked`
- `rejected`

建议工作台正常完成时使用 `done`。如果只是提交了结果但还需要后续验收，也可以使用 `submitted`；中央处理器会根据质量评价和验收策略把任务转入 `waiting_acceptance`、`changes_requested`、`blocked` 或 `done`。

## 7. 任务状态机

当前关键状态：

```txt
pending
  -> waiting_runner
  -> processing
  -> waiting_acceptance
  -> done

waiting_runner
  -> processing
  -> waiting_acceptance
  -> done

processing
  -> changes_requested
  -> blocked
  -> rejected

changes_requested
  -> pending / waiting_runner / processing

blocked
  -> pending / waiting_runner / processing / rejected
```

工作台遇到异常不要直接丢弃任务：

- 本地能力不足：不要 claim；或 claim 后 finish 为 `blocked` 并写明缺什么。
- 仓库无法访问：finish 为 `blocked`，写入错误、仓库地址、重试建议。
- 执行中断：下次启动时检查本地任务缓存和中央任务租约。
- 租约过期：重新 claim；如果已被其他 Runner claim，停止本地写回。

分层规则：

- `ProjectTask.status` 只表达路由位置：谁该接、是否执行中、是否等验收、是否关闭。
- `TaskResult.result` 只表达本次执行结果：`submitted`、`done`、`blocked`、`rejected`。
- `TaskResult.qualityEvaluation.decision` 表达质量动作：例如 `retry_required`、`repair_required`、`review_required`、`auto_accepted`。
- `acceptancePolicy.acceptanceStatus` 表达人或项目经理是否需要验收：例如 `waiting_acceptance`。
- `assignedRunner`、`leaseOwner`、`leaseExpiresAt` 和 `heartbeatAt` 表达领取和租约，不再使用 `claimed` 作为任务状态。

验收不是默认全量人审。工作台写回 TaskResult 后，中央处理器按风险决定下一步：关键交付、高优先级、有开放风险或有下一岗位交接时进入 `waiting_acceptance`；低风险内部记录、通知、审计、资料登记、检索类任务，如果证据、产物和检查齐全，可以进入 `auto_accepted` 并关闭。工作台不得把 `accepted`、`rejected`、`manual-runner-required` 等验收或旧门禁词写入 `ProjectTask.status`。

## 8. 项目初始化任务应该做什么

对已有仓库项目，初始化任务应检查并补齐：

- 项目是否已登记在中央处理器。
- Git 仓库是否可访问。
- README 是否说明项目定位和启动方式。
- AGENTS 是否说明本项目 Agent 工作规则。
- 目录结构是否清晰。
- 项目 Agent 是否已登记并挂到项目。
- Runner 是否已登记。
- 是否需要项目群。
- 是否已有决策记录、经验沉淀、风险清单。
- 后续任务是否拆出来。

对从头创建的新项目，初始化任务应生成：

- 仓库创建申请或执行清单。
- 初始 README。
- 初始 AGENTS。
- 基础目录结构。
- 项目启动清单。
- 项目 Agent 清单。
- 第一批工程任务。

工作台不要绕过审批去创建高风险资源。仓库、权限、群、客户承诺、secret 等操作如果需要审批，应先写任务和申请。

## 8.1 资料入库任务应该怎么接

当飞书机器人或中央处理器收到会议纪要、文档、文件、链接、包、数据集或学习资料时，中央处理器会先登记 `SourceMaterial`，必要时创建 `KnowledgeTask`。

工作台接到这类任务时，处理顺序是：

1. claim 任务并拿租约。
2. pull 任务上下文。
3. 读取上下文里的 `sourceMaterialRefs`。
4. 找到 `SourceMaterial` 的 `sourceRef`、`storageRef`、`contentHash`、`materialType`、`sensitivity`。
5. 用本机 Codex、Claude、本地模型、OCR、文档解析器或其他工作台内部能力处理资料。
6. 生成 TaskResult。
7. 如果有可复用结论，写 `knowledgeDraft` 或 `knowledgeRefs`，但不要直接标记 verified。
8. finish 任务，附上 evidenceRefs、outputRefs、testsOrChecks、nextActions。

工作台需要注意：

- 文档和会议纪要可以深度摘要、结构化、提取行动项。
- 安装包、模型、数据集和二进制文件不要把原始内容写进知识 markdown；只写引用、哈希、元数据、安装/使用结论和风险。
- 所有总结必须保留证据路径，至少能回到 `SourceMaterial`。
- 如果资料权限不足、内容无法读取、格式不支持，finish 为 `blocked`，写明缺什么。

## 8.2 图谱能力和上下文解释

中央处理器会从对象引用生成 `KnowledgeGraphEdge`，并在需要时导出 `GraphSnapshot`。

工作台不需要内置图数据库。它只需要理解：

- 任务上下文里的 `inclusionReason` 表示为什么某条资料或知识被放进上下文；
- `graph:<relation>:<ref>` 表示来源于关系图；
- `retrieval_match` 表示主要来自检索命中；
- 工作台写回 TaskResult、KnowledgeDraft、AgentRun 时要填好 `projectId`、`taskId`、`sourceMaterialRefs`、`evidenceRefs`、`knowledgeRefs`、`outputRefs`、`toolId`、`runnerId` 等引用字段，这样中央处理器才能继续抽边。

调试命令：

```bash
python3 -m zhenzhi_knowledge --root /knowledge graph export
python3 -m zhenzhi_knowledge --root /knowledge graph impact <object-ref>
```

HTTP 接口：

```http
POST /v0/materials/ingest
POST /v0/graph/export
POST /v0/graph/impact
```

工作台优先使用 HTTP 接口和中央处理器通信；CLI 主要用于本地调试和临时 Runner。

- `/v0/materials/ingest` 用于登记会议纪要、文件、链接、安装包、模型、数据集或学习资料；可同时创建 `KnowledgeTask`。
- `/v0/graph/export` 用于主动导出 `GraphSnapshot`，会刷新生成的边文件。
- `/v0/graph/impact` 用于查询某个对象影响范围，默认只读；只有明确传入 `rebuild: true` 时才刷新边文件。

这两个命令用于排查“这个资料影响了哪些任务/知识/项目”，不是工作台的强依赖。

## 9. 知识同步和跨电脑迁移

这个项目有一个重要目标：同一个项目从一台电脑换到另一台电脑时，不丢上下文。

工作台必须做到：

1. 所有正式任务从中央处理器拉上下文。
2. 执行结果必须写回 TaskResult。
3. 可复用经验必须写成有来源、有证据、有适用范围的知识草稿。
4. 原始材料不要只存在本地。
5. 本地路径不要作为唯一真源；需要用 `workspace://`、Git URL、项目相对路径或中央对象引用。
6. 任务交接时要写 nextActions 或 handoff note。

这样另一个 Runner 接手时，可以通过中央处理器恢复：

- 项目目标；
- 仓库；
- Agent；
- 任务；
- 来源材料；
- 最近结论；
- 未完成事项；
- 风险和证据。

## 10. 中央对接 MVP 建议

这里说的 MVP 只指“接入中央处理器”的最小闭环，不代表 Agent 工作台产品的完整范围。工作台自己的订阅、Agent 配置、模型接入、Skill 管理、工具市场、产品 UI 等能力，由工作台团队按自己的产品设计推进。

### 对接中央处理器必须做

- 本地配置页或配置文件：
  - API base URL。
  - API token。
  - runnerId。
  - runner name。
  - hostType。
  - mode。
  - agents。
  - capabilities。
  - availableProjects。
  - repoAccess。
- 启动后自动注册 Runner。
- 定时心跳。
- 轮询任务。
- claim / heartbeat / pull / finish。
- 至少一种本地执行引擎适配层，例如 Codex、Claude、本地模型、脚本或其他工作台支持的 Agent 执行器。
- 本地任务日志。
- 崩溃恢复。

### 工作台产品可自行设计

- 可视化任务列表。
- 一键接管 `waiting_runner` 任务。
- 多 Agent 编排。
- 多模型路由。
- Codex、Claude、本地模型和云模型的接入与切换。
- Skill、工具、插件、MCP 的管理。
- 订阅、授权、设备管理和本地安全存储。
- 自动生成知识草稿。
- 浏览器、IDE、Git GUI 集成。
- 任务推送替代轮询。

## 11. Agent 讨论会对接

中央处理器第一阶段支持异步回合制 Agent 讨论会。工作台不需要实现实时聊天室，也不需要决定公司级流程；它只需要让本机注册的 Agent 能参与中央处理器创建的讨论，并把观点、证据、汇总结果按协议写回。

### 11.1 工作台在讨论会里的职责

工作台负责：

1. 发现分配给本机 Agent 的讨论发言请求。
2. 为本机 Agent 准备讨论上下文，包括项目、关联任务、历史决策、相关知识和其他 Agent 已提交观点。
3. 调用本地 Codex / Claude / 本地模型 / 工具，让对应 Agent 生成观点。
4. 写回 `DiscussionTurn`。
5. 如果本机 Agent 是项目经理 Agent，则在所有必要角色提交后写回 `DiscussionSummary`。
6. 如果形成共识，允许中央处理器生成 `Decision` 和后续 `ProjectTask`。
7. 如果仍有分歧或高风险，写回 `waiting_human_decision`，由机器人通知人类决策。

工作台不负责：

- 擅自跳过中央处理器创建的讨论状态。
- 绕过 `DiscussionSummary` 直接创建执行任务。
- 把本机聊天日志当成正式决策。
- 在没有中央对象引用的情况下让另一个 Agent 继续执行。

### 11.2 讨论会对象

| 对象 | 说明 |
| --- | --- |
| `DiscussionSession` | 讨论会主记录，包含主题、项目、参与 Agent、关联任务、状态和通知 |
| `DiscussionTurn` | 某个 Agent 的一轮观点，包含立场、建议、风险和证据 |
| `DiscussionSummary` | 项目经理 Agent 汇总，包含共识、待决问题、决策建议 |
| `Decision` | 讨论形成的正式决策 |
| `ProjectTask` | 讨论后拆出的后续任务 |
| `NotificationRecord` | 机器人通知记录，保证人类和 Agent 能看到讨论进度 |

### 11.3 API 协议

#### 创建讨论会

```http
POST /v0/discussions/create
```

请求：

```json
{
  "title": "需求实现方案讨论",
  "projectId": "agent-hub",
  "requester": "agent.company.project-manager",
  "topic": "这个需求如何实现、如何验收、是否存在风险。",
  "participantAgents": [
    "agent.company.product-manager",
    "agent.company.development",
    "agent.company.test"
  ],
  "relatedTaskId": "REQ-001",
  "facilitatorAgent": "agent.company.project-manager",
  "maxRounds": 1,
  "humanVisible": true
}
```

返回：

```json
{
  "apiVersion": "v0.1",
  "kind": "DiscussionSession",
  "discussionId": "DISC-20260619-001",
  "discussionRef": "projects/agent-hub/discussions/disc-20260619-001.md"
}
```

#### 写回角色观点

```http
POST /v0/discussions/turn
```

请求：

```json
{
  "discussionId": "DISC-20260619-001",
  "agentId": "agent.company.development",
  "role": "研发 Agent",
  "content": "建议先做异步回合制讨论，不做实时聊天室。",
  "stance": "support",
  "concerns": ["需要保证通知链路和后续任务创建"],
  "recommendations": ["补 CLI/API/飞书入口", "补端到端测试"],
  "evidenceRefs": ["docs/agent-team/company-agent-team-operating-guide.md"]
}
```

返回：

```json
{
  "apiVersion": "v0.1",
  "kind": "DiscussionTurn",
  "discussionId": "DISC-20260619-001",
  "turnRef": "projects/agent-hub/discussions/disc-20260619-001-turn-01.md",
  "sessionStatus": "waiting_agent_turns"
}
```

当所有必要参与 Agent 都写回后，`sessionStatus` 会变成 `pm_reviewing`。

#### 写回项目经理汇总

```http
POST /v0/discussions/finalize
```

请求：

```json
{
  "discussionId": "DISC-20260619-001",
  "facilitator": "agent.company.project-manager",
  "summary": "产品、研发、测试同意先做异步回合制讨论。",
  "consensus": "第一阶段不做实时聊天室，只做中央可追踪讨论对象和通知链路。",
  "decision": "采用 DiscussionSession / DiscussionTurn / DiscussionSummary 作为第一阶段模型。",
  "openQuestions": [],
  "humanDecisionRequired": false,
  "followupTaskTitle": "实现 Agent 讨论第一阶段闭环",
  "followupAssignee": "agent.company.development"
}
```

返回：

```json
{
  "apiVersion": "v0.1",
  "kind": "DiscussionSummary",
  "discussionId": "DISC-20260619-001",
  "discussionRef": "projects/agent-hub/discussions/disc-20260619-001.md",
  "summaryRef": "projects/agent-hub/discussions/disc-20260619-001-summary.md",
  "decisionRefs": ["projects/agent-hub/decision.disc-20260619-001.md"],
  "followupTaskRefs": ["projects/agent-hub/tasks/kt-20260619-001.md"],
  "status": "next_task_created"
}
```

#### 查询讨论会

```http
GET /v0/discussions/<discussionId>
```

### 11.4 通知语义

中央处理器会为讨论会每个关键节点创建 `NotificationRecord`。工作台可以轮询这些通知，也可以等后续推送能力接入。第一阶段必须支持轮询和投递确认，避免通知只停留在文件记录里。

| messageType | 含义 |
| --- | --- |
| `discussion_created` | 讨论会已创建 |
| `discussion_turn_requested` | 某个 Agent 需要提交观点 |
| `discussion_turn_submitted` | 某个 Agent 已提交观点 |
| `discussion_ready_for_summary` | 所有必要观点已提交，项目经理 Agent 可以汇总 |
| `discussion_summary_ready` | 汇总已生成 |
| `discussion_human_decision_required` | 需要人类决策 |
| `discussion_completed` | 讨论已闭环 |

#### 拉取待投递通知

```http
GET /v0/notifications?status=pending&recipient=agent.company.development
Authorization: Bearer <api-token>
```

返回：

```json
{
  "apiVersion": "v0.1",
  "kind": "NotificationList",
  "notifications": [
    {
      "notificationId": "notification.20260619T161946415374Z",
      "messageType": "discussion_turn_requested",
      "recipient": "agent.company.development",
      "channel": "feishu",
      "status": "pending",
      "discussionId": "DISC-20260619-001",
      "messageSummary": "请提交讨论观点：研发测试讨论。角色：agent.company.development。",
      "notificationRef": "notifications/notification.20260619t161946415374z.md"
    }
  ]
}
```

常用过滤参数：

- `status`: `pending` / `sent` / `failed`
- `recipient`: Agent ID、用户 open_id、项目群或 `project`
- `channel`: `feishu`、`agent-ring` 等
- `messageType`: 例如 `discussion_turn_requested`
- `projectId`
- `taskId`
- `discussionId`

#### 确认投递结果

```http
POST /v0/notifications/delivery
Authorization: Bearer <api-token>
Content-Type: application/json

{
  "notificationId": "notification.20260619T161946415374Z",
  "status": "sent",
  "actor": "agent-ring.runner.mac-mini",
  "deliveryRef": "feishu://message/om_xxx"
}
```

失败时：

```json
{
  "notificationId": "notification.20260619T161946415374Z",
  "status": "failed",
  "actor": "agent-ring.runner.mac-mini",
  "failureReason": "Feishu API timeout"
}
```

中央处理器会把状态写回 `NotificationRecord`，并创建 `notification.delivered` 或 `notification.failed` AuditLog。

### 11.5 工作台验收标准

工作台完成讨论会对接，至少要满足：

1. 能读取或接收 `discussion_turn_requested`。
2. 能让指定本机 Agent 生成观点。
3. 能调用 `/v0/discussions/turn` 写回 `DiscussionTurn`。
4. 项目经理 Agent 能在 `pm_reviewing` 后调用 `/v0/discussions/finalize`。
5. 能展示讨论状态、发言记录、汇总记录、Decision 和后续任务。
6. 能通过 `/v0/notifications` 拉取待投递通知。
7. 能通过 `/v0/notifications/delivery` 回写 `sent` / `failed`。
8. 任何失败都要写回错误或通知人类，不能静默丢失。

## 12. 安全边界

工作台必须遵守：

- 不把 secret、token、cookie、私钥写入知识库。
- 不绕过中央任务状态直接写 verified knowledge。
- 不执行未注册的高风险工具。
- 不用本地未审查结果覆盖中央已验证知识。
- 不把本地绝对路径当作项目真源。
- 不在没有租约或租约过期时写回任务结果。
- 不把用户私聊内容扩散到项目知识，除非它已成为明确的 SourceMaterial。

## 13. Agent 自净化对接

Agent 工作台不仅执行任务，也要把失败变成下一次更好的能力。中央处理器负责生成和保存自净化对象；工作台负责拉取、展示、执行、验证。

### 13.1 中央处理器会生成什么

当任务 `finish` 后质量评价不通过，或人类/项目经理验收打回时，中央处理器会自动生成：

- `AgentImprovementProposal`：记录哪个 Agent、哪个任务、为什么失败、建议改什么、是否公司级复用。
- `EvalCase` 草稿：把失败样例变成回归用例。
- `NotificationRecord`：通知项目经理 Agent 和责任 Agent。
- `AgentCapabilityReport`：按需汇总某个 Agent 的通过率、失败原因和改进项。

工作台不需要自己判断“要不要创建改进项”；它只需要正确写回 `TaskResult`、拉取通知、执行改进任务。

### 13.2 工作台需要支持的行为

1. 拉取通知：

```http
GET /v0/notifications?status=pending&recipient=<agentId>
```

2. 识别以下消息类型：

| messageType | 含义 | 工作台动作 |
| --- | --- | --- |
| `agent_improvement_proposal_created` | 项目经理 Agent 需要看改进提案 | 展示提案、失败原因、EvalCase、责任 Agent |
| `agent_improvement_action_required` | 某个角色 Agent 需要修复能力 | 让本机 Agent 拉取提案和相关 TaskResult，修 Skill / checklist / workflow |
| `task_result_changes_requested` | 人类或项目经理打回交付 | 重新拉取任务上下文，按打回原因返工 |

3. 生成能力报告：

```http
POST /v0/agents/report
Content-Type: application/json

{
  "agentId": "agent.company.development",
  "projectId": "agent-hub",
  "owner": "agent-ring.runner.mac-mini",
  "period": "2026-W25"
}
```

响应：

```json
{
  "apiVersion": "v0.1",
  "kind": "AgentCapabilityReport",
  "reportRef": "knowledge/metrics/agent-capability-agent.company.development.20260620T005000Z.md"
}
```

4. 本地 CLI 等价入口：

```txt
zhenzhi-knowledge agent report --agent-id <agentId> --project <projectId>
```

### 13.3 复用边界

工作台必须尊重 `AgentImprovementProposal.reuseScope`：

- `company`：可提示所有项目和所有员工使用，但成为正式 Skill / Eval / 指南前仍需 Review。
- `project`：只在项目上下文内使用，不自动扩散到公司级公共知识。

如果同一个项目级问题重复出现，工作台可以提醒知识工程 Agent 抽象为公司级改进，但不能直接越权发布。

### 13.4 验收标准

工作台完成自净化对接，至少要满足：

1. 能展示 `agent_improvement_proposal_created` 和 `agent_improvement_action_required`。
2. 能从通知跳到 TaskResult、AgentImprovementProposal、EvalCase。
3. 能让责任 Agent 基于失败原因修正 Skill / workflow / prompt / 工具使用。
4. 能重新执行任务或 EvalCase。
5. 能回写新的 TaskResult。
6. 能调用 `/v0/agents/report` 或 CLI 生成能力报告。
7. 对公司级改进，能提示需要更新公司 Agent Team 指南和飞书指南。
8. 对项目级改进，不能默认扩散到公司公共知识。

## 14. 对接验收脚本

工作台开发同学接入前，可以先跑中央处理器提供的 HTTP 合约脚本：

```bash
python3 scripts/agent_ring_contract.py
```

这个脚本会创建临时本地 bundle，启动中央处理器 HTTP API，并验证工作台必须遵守的协议边界：

- 健康检查；
- API token 保护；
- Runner 注册和心跳；
- 任务查询、领取、租约、上下文拉取、任务心跳、结果写回；
- Agent 讨论 create / turn / finalize；
- NotificationRecord 拉取和投递确认；
- Agent 自净化通知、能力报告和改进对象读取；
- stale version、错误 lease token、缺少能力、过期租约等失败路径。

脚本不会调用真实 Codex、Claude、本地模型、浏览器或外部工具，也不会使用真实 secret。它验证的是“中央处理器和工作台之间的通信契约”，不是工作台内部产品能力。

## 15. 当前已验证状态

截至 2026-06-18，中央处理器已经具备：

- 飞书项目创建入口。
- 创建项目后自动生成项目初始化任务。
- Agent Ring 未启用时，任务状态为 `waiting_runner`。
- 临时 Runner 登记。
- 项目 Agent 登记。
- Runner 注册与心跳 API。
- 任务 claim、heartbeat、pull、finish API。
- TaskResult 写回。
- Agent 讨论会第一阶段 API：create / turn / finalize / status。
- 通知出站 API：`GET /v0/notifications` 和 `POST /v0/notifications/delivery`。
- 讨论会 NotificationRecord 创建、拉取、投递确认链路。
- Agent 自净化对象：AgentImprovementProposal、EvalCase 草稿、AgentCapabilityReport。
- Agent 能力报告 CLI/API：`zhenzhi-knowledge agent report`、`POST /v0/agents/report`。
- 审批和审计基础能力。

当前 `agent-hub` 项目已经回补：

- 初始化任务：`project-init-agent-hub`
- 状态：`waiting_runner`
- 绑定 Runner：`runner.meimei-mac-codex`
- 负责人 Agent：`agent.agent-hub.project-manager`
- Runner 能力：`codex`, `git`, `knowledge_sync`, `project_initialization`

## 16. 中央对接验收标准

下面只验收“是否接入中央处理器”，不验收 Agent 工作台自身完整产品能力。

1. 能注册一台电脑为 Runner。
2. 能持续心跳，中央处理器看到 Runner 在线。
3. 能发现 `waiting_runner` 或 `pending` 任务。
4. 能按能力和项目范围过滤任务。
5. 能 claim 任务并拿到 leaseToken。
6. 能 pull 上下文包。
7. 能启动本地 Codex 或先用 mock executor 执行。
8. 能 finish 任务并写回 TaskResult。
9. 租约过期、任务被别人领取、Runner 能力不足时能正确失败并提示。
10. 能参与 Agent 讨论会，写回本机 Agent 的 DiscussionTurn。
11. 项目经理 Agent 能写回 DiscussionSummary，并触发 Decision 或后续 ProjectTask。
12. 能接收 Agent 自净化通知，读取改进提案和 EvalCase。
13. 能生成 AgentCapabilityReport，辅助判断哪个 Skill / workflow 要优先优化。
14. 中央处理器审计日志里能看到注册、心跳、claim、pull、finish、discussion create/turn/finalize、notification delivery、agent improvement 全链路。

这些条目跑通后，Agent 工作台就可以作为分布式电脑执行节点接入中央处理器，并支持多 Agent 异步协作讨论。
