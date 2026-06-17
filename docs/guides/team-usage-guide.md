# 桢知知识工程团队使用指南

这份文档给团队成员使用。目标是让 Codex、Claude、Antigravity 等本地 Agent 都能连接同一套知识工程，按统一流程读取知识、执行任务、写回经验和工具资产。

## 1. 你需要准备什么

项目负责人给同事三样东西：

```txt
GitHub 私有仓库:
https://github.com/meimei7959/company_knowledge_core.git

线上知识 API:
http://124.221.138.151/knowledge-api

团队 API Token:
单独通过安全渠道发送，不写进 Git、文档、聊天记录或截图。
```

### 1.1 API Token 从哪里来

API Token 由项目负责人维护，不由同事自己生成。当前 token 存在两个地方：

```txt
本地负责人机器:
deploy/lighthouse/.env

线上服务器:
/opt/projects/company_knowledge_core/repo/deploy/lighthouse/.env
```

负责人在本地查看 token：

```bash
grep '^ZHENZHI_KNOWLEDGE_API_TOKEN=' deploy/lighthouse/.env
```

给同事配置时，只发送 token 值，不发送 `.env` 文件。同事在自己的终端里设置：

```bash
export ZHENZHI_KNOWLEDGE_API_TOKEN_PROD=<团队 token>
```

然后再运行初始化脚本：

```bash
bash scripts/setup-teammate.sh --user-id <同事名> --ai-tool codex
```

安全规则：

```txt
不要提交 token。
不要写进 README、知识文件、项目文档、截图、聊天记录。
不要把 deploy/lighthouse/.env 发给同事。
不要把 token 填进 Agent 任务描述。
只通过安全渠道发给需要接入知识工程的成员。
```

如果怀疑 token 泄露，负责人应立即轮换：

```bash
python3 -c "import secrets; print('ZHENZHI_KNOWLEDGE_API_TOKEN=' + secrets.token_urlsafe(32))"
```

把生成的新值写入本地 `deploy/lighthouse/.env`，然后重新部署：

```bash
bash deploy/lighthouse/deploy.sh
```

轮换后，通知同事重新设置：

```bash
export ZHENZHI_KNOWLEDGE_API_TOKEN_PROD=<新的团队 token>
```

同事本地需要：

```txt
git
python3 >= 3.11
本地 AI 工具：Codex / Claude / Antigravity 任意一种
```

## 2. 新同事初始化

同事第一次使用时执行：

```bash
git clone https://github.com/meimei7959/company_knowledge_core.git
cd company_knowledge_core

export ZHENZHI_KNOWLEDGE_API_TOKEN_PROD=<团队 token>
bash scripts/setup-teammate.sh --user-id <同事名> --ai-tool codex
```

Claude 用户：

```bash
export ZHENZHI_KNOWLEDGE_API_TOKEN_PROD=<团队 token>
bash scripts/setup-teammate.sh --user-id <同事名> --ai-tool claude
```

Antigravity 用户：

```bash
export ZHENZHI_KNOWLEDGE_API_TOKEN_PROD=<团队 token>
bash scripts/setup-teammate.sh --user-id <同事名> --ai-tool antigravity
```

脚本位置：

```txt
scripts/setup-teammate.sh
```

脚本会生成：

```txt
.zhenzhi/config.json
.zhenzhi/agent-entrypoint.md
.zhenzhi/codex-start.md
.zhenzhi/claude-start.md
.zhenzhi/antigravity-start.md
.zhenzhi/index.sqlite3
agents/agent.<同事名>.<ai-tool>.md
```

这些文件的含义：

| 文件 | 用途 | 是否提交 |
| --- | --- | --- |
| `.zhenzhi/config.json` | 本地配置、默认 Agent、线上 API profile | 不提交 |
| `.zhenzhi/agent-entrypoint.md` | 给本地 Agent 读的统一入口 | 不提交 |
| `.zhenzhi/*-start.md` | 各 AI 工具启动提示 | 不提交 |
| `.zhenzhi/context/current.md` | 每次 `start` 后生成的任务上下文 | 不提交 |
| `.zhenzhi/index.sqlite3` | 本地索引和检索缓存 | 不提交 |
| `agents/agent.<同事名>.<ai-tool>.md` | 团队可见的 Agent 注册记录 | 需要提交 |

## 3. 每天怎么用

开始任务前：

```bash
zhenzhi-knowledge sync pull
zhenzhi-knowledge start \
  --project company-knowledge-core \
  --agent agent.<同事名>.<ai-tool> \
  --task "<今天要做的任务>"
```

然后让本地 AI 工具读取：

```txt
.zhenzhi/context/current.md
```

任务完成后：

```bash
zhenzhi-knowledge finish \
  --project company-knowledge-core \
  --agent agent.<同事名>.<ai-tool> \
  --summary "<完成了什么、产生了什么经验、是否有工具变化>"

zhenzhi-knowledge sync push
```

`start` 会生成：

```txt
.zhenzhi/context/current.md
```

里面包含：

```txt
项目资料
Agent 身份
权限策略
可用 ToolAsset
RAG 召回的相关知识
执行约束
```

`finish` 会生成：

```txt
runs/company-knowledge-core/run.<time>.md
projects/company-knowledge-core/lessons.draft.md
projects/company-knowledge-core/project.update.draft.md
projects/company-knowledge-core/tools.update.draft.md
log.md
```

这些 draft 不是最终知识，后续需要人工 review。

## 4. Codex / Claude / Antigravity 怎么接入

初始化后，本地 AI 工具应该先读：

```txt
.zhenzhi/agent-entrypoint.md
```

如果要给不同工具专门提示：

```txt
Codex:       .zhenzhi/codex-start.md
Claude:      .zhenzhi/claude-start.md
Antigravity: .zhenzhi/antigravity-start.md
```

给 Agent 的任务提示建议这样写：

```txt
你正在使用桢知知识工程。

先读取 .zhenzhi/agent-entrypoint.md。
正式工作前必须运行 start。
工作时必须遵守 .zhenzhi/context/current.md 里的权限、工具和知识约束。
完成后必须运行 finish，并说明写回了哪些 draft。

本次任务：
<任务描述>
```

## 5. zhenzhi-knowledge 命令说明

### 5.1 `install`

用途：初始化本地连接器。

常用命令：

```bash
zhenzhi-knowledge install \
  --user-id <同事名> \
  --ai-tool claude \
  --agent-id agent.<同事名>.claude \
  --default-project company-knowledge-core \
  --remote https://github.com/meimei7959/company_knowledge_core.git \
  --register-agent \
  --agent-name "<同事名> Claude"
```

生成：

```txt
.zhenzhi/config.json
.zhenzhi/agent-entrypoint.md
.zhenzhi/codex-start.md
.zhenzhi/claude-start.md
.zhenzhi/antigravity-start.md
agents/agent.<同事名>.<ai-tool>.md
```

通常不直接给同事用，优先用：

```bash
bash scripts/setup-teammate.sh
```

### 5.2 `status`

用途：检查本地配置和知识工程是否有效。

```bash
zhenzhi-knowledge status
```

输出：

```txt
root
profile
backend
valid
```

### 5.3 `profile use`

用途：切换本地使用 Git 模式还是线上 API 模式。

```bash
zhenzhi-knowledge profile use production
```

production profile 使用：

```txt
ZHENZHI_KNOWLEDGE_API_PROD=http://124.221.138.151/knowledge-api
ZHENZHI_KNOWLEDGE_API_TOKEN_PROD=<团队 token>
```

### 5.4 `sync pull / sync push`

用途：同步 Git 仓库。

```bash
zhenzhi-knowledge sync pull
zhenzhi-knowledge sync push
```

冲突时会生成：

```txt
knowledge/conflicts/conflict.<time>.md
```

### 5.5 `start`

用途：让 Agent 开始任务前读取统一上下文。

```bash
zhenzhi-knowledge start \
  --project company-knowledge-core \
  --agent agent.<同事名>.<ai-tool> \
  --task "<任务>"
```

生成：

```txt
.zhenzhi/context/current.md
log.md
```

Agent 必须先读 `.zhenzhi/context/current.md` 再工作。

### 5.6 `finish`

用途：任务完成后写回运行记录、经验草稿和工具更新草稿。

```bash
zhenzhi-knowledge finish \
  --project company-knowledge-core \
  --agent agent.<同事名>.<ai-tool> \
  --summary "<总结>"
```

生成：

```txt
runs/company-knowledge-core/run.<time>.md
projects/company-knowledge-core/lessons.draft.md
projects/company-knowledge-core/project.update.draft.md
projects/company-knowledge-core/tools.update.draft.md
```

注意：这些是 draft，需要审核，不是最终知识。

### 5.7 `rag rebuild / rag search`

用途：重建和查询语义检索索引。

```bash
zhenzhi-knowledge rag rebuild
zhenzhi-knowledge rag search --query "<问题>" --scope engineering
```

查询结果包含：

```txt
score
path
chunkId
sourceRef
```

### 5.8 `index rebuild / index search`

用途：重建对象索引，按类型、状态、项目、Agent、工具查询。

```bash
zhenzhi-knowledge index rebuild
zhenzhi-knowledge index search --type ToolAsset
zhenzhi-knowledge index search --type KnowledgeItem --status draft
```

### 5.9 `tool register`

用途：登记一个团队可复用工具。

```bash
zhenzhi-knowledge tool register \
  --tool-id tool.<name> \
  --name "<工具名>" \
  --owner <负责人> \
  --repo <代码仓库地址> \
  --entrypoint "<调用入口>" \
  --risk L1
```

生成：

```txt
tools/tool.<name>.md
tools/index.md
log.md
```

字段说明：

| 字段 | 说明 |
| --- | --- |
| `tool-id` | 工具唯一 ID |
| `repo` | 工具代码仓库，不要把源码复制进知识库 |
| `entrypoint` | 调用入口，例如 CLI 命令、HTTP 地址、MCP 名称 |
| `risk` | L1-L5，L3 以上需要审批 |

### 5.10 `tool invoke`

用途：按权限调用已注册工具。默认 dry-run。

```bash
zhenzhi-knowledge tool invoke \
  --tool-id tool.<name> \
  --project company-knowledge-core \
  --agent agent.<同事名>.<ai-tool> \
  --input "<输入>"
```

生成：

```txt
knowledge/audit/audit.<time>.md
```

### 5.11 `review list / review update`

用途：人工审核 draft、testing、stale_candidate。

```bash
zhenzhi-knowledge review list
zhenzhi-knowledge review update \
  --target <文件路径> \
  --status verified \
  --reviewer <审核人>
```

生成：

```txt
knowledge/audit/audit.<time>.md
```

审核规则：

```txt
draft -> verified
testing -> approved
stale_candidate -> stale 或 verified
```

### 5.12 `audit search`

用途：查询审计记录。

```bash
zhenzhi-knowledge audit search --agent-id agent.<同事名>.<ai-tool>
zhenzhi-knowledge audit search --target tools/tool.<name>.md
```

### 5.13 `metrics report`

用途：生成运营指标报告。

```bash
zhenzhi-knowledge metrics report --owner <负责人>
```

生成：

```txt
knowledge/metrics/metrics.<time>.md
```

### 5.14 `stale scan`

用途：检查受工具版本、项目状态影响的旧知识。

```bash
zhenzhi-knowledge stale scan --owner <负责人>
```

会把相关知识标记为：

```txt
stale_candidate
```

之后必须人工 review。

### 5.15 `eval case / eval run`

用途：为工具或 Agent 建评测用例并记录运行结果。

```bash
zhenzhi-knowledge eval case create \
  --eval-id eval.<name> \
  --title "<评测名>" \
  --owner <负责人> \
  --target-ref tools/tool.<name>.md \
  --input "<输入>" \
  --expected "<期望输出>"

zhenzhi-knowledge eval run \
  --eval-id eval.<name> \
  --actual "<实际输出>" \
  --runner <执行人>
```

生成：

```txt
knowledge/evals/eval.<name>.md
knowledge/eval-runs/evalrun.<time>.md
```

### 5.16 `backup create`

用途：备份知识工程。

```bash
zhenzhi-knowledge backup create
```

生成：

```txt
backups/knowledge-backup-<time>.zip
```

备份目录不提交 Git。

### 5.17 `api serve`

用途：启动线上或本地 HTTP API。

```bash
zhenzhi-knowledge api serve --host 0.0.0.0 --port 8765
```

线上已经部署在：

```txt
http://124.221.138.151/knowledge-api
```

### 5.18 `validate`

用途：检查知识工程结构是否合规。

```bash
zhenzhi-knowledge validate
```

会拦截：

```txt
缺 frontmatter 的文件
未知 type/status
疑似 secret 字段
乱放在 knowledge/ 根目录的文件
缺 sourceRef/confidence/status/owner/scope 的 KnowledgeItem
```

## 6. 知识应该写到哪里

不要把所有东西都丢进知识库。

| 内容 | 写到哪里 | 状态 |
| --- | --- | --- |
| 项目目标、范围、当前重点 | `projects/<project-id>/project.md` | draft/verified |
| 项目决策 | `projects/<project-id>/decisions.md` 或 `knowledge/company/` | draft/verified |
| 可复用经验 | `knowledge/engineering/` 或 `projects/<project-id>/lessons.draft.md` | draft |
| 工具登记 | `tools/tool.<name>.md` | testing/approved |
| Agent 运行记录 | `runs/<project-id>/run.<time>.md` | draft/verified |
| 冲突记录 | `knowledge/conflicts/` | open/resolved |
| 审计记录 | `knowledge/audit/` | 自动生成 |
| 评测用例 | `knowledge/evals/` | verified |
| 评测结果 | `knowledge/eval-runs/` | draft/verified |

不应该直接放入知识库：

```txt
原始聊天记录
截图
会议录音或全文转录
临时笔记
未整理的导出文件
源码副本
密钥、token、密码
```

这些内容要先整理成结构化 Markdown/YAML 对象，再进入对应目录。

## 7. 给我或 Agent 填什么信息

启动一个新同事：

```txt
同事名:
使用工具: codex / claude / antigravity
是否已有 GitHub 仓库访问权限:
是否已拿到团队 API token:
默认项目: company-knowledge-core 或其他 projectId
```

开始一个新项目：

```txt
projectId:
项目名称:
负责人:
关联代码仓库:
参与 Agent:
核心目标:
当前范围:
不做什么:
```

登记一个工具：

```txt
toolId:
工具名称:
负责人:
代码仓库地址:
调用入口:
输入格式:
输出格式:
风险等级: L1-L5
适用项目:
是否需要人工审批:
```

写入一条知识：

```txt
标题:
类别: company / engineering / product / business / operations / research / customer
来源 sourceRef:
置信度 confidence: low / medium / high
适用范围 scope:
正文:
是否可复用:
是否涉及客户敏感信息:
```

完成一次 Agent 任务：

```txt
projectId:
agentId:
任务:
结果:
使用了哪些知识:
使用了哪些工具:
产出了哪些文件:
要沉淀的经验:
需要人工 review 的事项:
```

## 8. 推荐团队流程

每天：

```txt
sync pull
start
Agent 工作
finish
sync push
```

每周：

```txt
review list
审核 draft / testing / stale_candidate
metrics report
stale scan
```

每次新增工具：

```txt
tool register
eval case create
eval run
review update -> approved
```

## 9. 当前线上状态

```txt
Knowledge API:
http://124.221.138.151/knowledge-api

Health:
http://124.221.138.151/knowledge-api/health

服务器端口:
127.0.0.1:8765

Docker container:
zhenzhi-knowledge-api

Compose project:
zhenzhi_knowledge
```

Agent Work 和知识工程部署在同一台服务器，但端口、容器、路径、Compose project 都是分开的。
