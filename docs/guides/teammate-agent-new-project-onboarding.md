# 新电脑 Agent 接入与新项目初始化操作规程

这份文档给正在接入的新电脑上的 Agent 读取。

本文里的“你”“本机”“这台电脑”，都指当前正在阅读本文、准备接入桢知体系的这台新电脑，不是项目负责人电脑。

本文分两部分：

1. 第一部分：接入电脑成功。只把当前电脑注册成可用本机设备 / Runner，不需要任何新项目字段。
2. 第二部分：新项目成功。只有真的要在这台电脑上启动新项目时，才需要项目 ID、项目中文名、项目 owner、项目目标、业务仓库路径和 PRD。

如果当前任务只是“接入电脑”，不要向用户索要新项目 ID、项目中文名、owner、项目目标、本地业务仓库路径或 PRD 路径。

## 第一部分：接入电脑成功

### 当前是否可以接入

可以接入，但必须满足三个条件：

1. 这台电脑拿到了桢知本地 Agent 工具包。方式可以是 GitHub clone，也可以是项目负责人打包发送。
2. 这台电脑拿到了项目负责人通过安全渠道发放的 `ZHENZHI_KNOWLEDGE_API_TOKEN_PROD`。
3. 这台电脑安装了 `git`、`python3 >= 3.11` 和本地 AI 工具，例如 Codex、Claude 或 Antigravity。

当前电脑可以先只注册成可用 Runner。没有新项目时，不需要项目 ID、项目中文名、项目 owner、项目目标、本地业务仓库路径或 PRD 路径。

线上中枢地址：

```txt
http://124.221.138.151/knowledge-api
```

不要把 token 写入文档、Git、聊天记录、截图、任务描述或审计正文。

### 为什么已经部署了服务器，还需要本地工具包

服务器已经部署，说明线上中枢 API 可以访问。它负责保存项目、任务、Runner、TaskResult、审计和知识索引。

但当前这台新电脑要真正工作，还需要本地 Agent 工具包：

```txt
zhenzhi-knowledge CLI
setup-teammate.sh 接入脚本
Agent 岗位规则
Skill 包
项目模板
本地 start / finish / task result 写回命令
```

所以“访问仓库”不是为了访问线上服务，而是为了把本地 Agent 工具包拿到当前电脑。

如果当前电脑不能访问 GitHub，或者现场网络不允许访问 GitHub，可以让项目负责人从已部署版本打一个只读工具包发给当前电脑。这样当前电脑不需要访问 GitHub，也能接入线上中枢。

### 接入电脑需要的信息

第一阶段只接入电脑时，项目负责人必须通过安全渠道给当前电脑的使用者这些信息：

```txt
本地 Agent 工具包获取方式: 默认从公开 GitHub 仓库 clone
ZHENZHI_KNOWLEDGE_API_TOKEN_PROD: <只私聊发送，不写入文档>
同事 ID: <英文或拼音，例如 lisi>
AI 工具: codex / claude / antigravity / other
Runner ID: <建议 runner.<同事ID>-<电脑名>-<ai-tool>，例如 runner.lisi-mac-codex>
Runner 名称: <给人看的电脑名称，例如 李四 Mac Codex Runner>
```

不要猜这些值。缺任何一个，都先停下来向项目负责人要，不要自己编。

第一阶段禁止要求这些新项目字段：

```txt
新项目 ID
新项目中文名
项目 owner
项目目标
本地业务项目仓库绝对路径
source-file / PRD 路径
```

第二阶段真的要在这台电脑上启动新项目时，再向项目负责人要新项目信息包：

```txt
新项目 ID: <小写英文数字短横线，例如 customer-service-bot>
新项目中文名: <给人看的项目名>
项目 owner: <负责人ID或同事ID>
项目目标: <一句话目标>
本地业务项目仓库绝对路径: <例如 /Users/lisi/Documents/projects/customer-service-bot>
可选 source-file/PRD 路径: <例如 /Users/lisi/Downloads/prd.md>
```

### 如果无法从 GitHub clone

当前仓库已经是公开仓库，正常情况下不需要 GitHub 账号权限，直接 clone 即可：

```bash
git clone https://github.com/meimei7959/company_knowledge_core.git
```

如果当前电脑因为网络、防火墙、GitHub 访问异常等原因不能 clone，再让项目负责人提供本地 Agent 工具包 zip。

项目负责人在自己电脑上执行：

```bash
cd /Users/meimei/Documents/company_knowledge_core
git archive --format=zip --output /tmp/zhenzhi-agent-kit.zip HEAD
```

项目负责人把 `/tmp/zhenzhi-agent-kit.zip` 通过安全文件传输方式发给当前电脑的使用者。

当前新电脑收到 zip 后执行：

```bash
mkdir -p ~/Documents/company_knowledge_core
unzip /path/to/zhenzhi-agent-kit.zip -d ~/Documents/company_knowledge_core
cd ~/Documents/company_knowledge_core

export ZHENZHI_KNOWLEDGE_API_TOKEN_PROD='<项目负责人发给你的token>'
bash scripts/setup-teammate.sh --user-id <同事英文或拼音ID> --ai-tool codex
```

如果本机还没安装 `unzip`，先安装系统自带解压工具，或让负责人直接发送解压后的文件夹。

注意：zip 里不能包含 `.env`、`.git`、token、私钥、cookie 或任何 secret。

zip 方式适合先让当前电脑接入线上中枢并开始使用 Agent 团队规则。如果后续要把这台电脑生成的 Agent 注册记录、Runner 记录、任务结果文件提交回 Git，项目负责人需要代提交，或者让当前电脑使用自己的 GitHub 账号提交 PR。

### 你的角色边界

你不是主线程，也不是人类项目负责人。

你是当前电脑上的本地执行 Agent / Runner。你的职责是：

- 拉取桢知中枢仓库，读取 Agent 团队规则、Skill 和项目上下文。
- 注册自己的本机 Agent 身份和本机 Runner。
- 在新项目中使用同一套项目经理、产品、架构、设计、研发、测试 Agent 规则。
- 执行被分配的任务，写回 `TaskResult`、证据、运行记录和阻塞原因。
- 发现流程、Skill、工具、任务拆分、验收、上下文传递问题时，记录为任务结果、缺陷或改进建议。

你不能做的事：

- 不要绕过项目经理 Agent 自己关闭项目。
- 不要替产品、架构、测试、PM 直接下最终结论。
- 不要在没有任务来源的情况下随意创建实现任务。
- 不要把 token、密码、私钥、cookie 写进仓库。

正式 PM 动作必须由项目经理 Agent 通过：

```bash
python3 -m zhenzhi_knowledge.cli project pm-action ...
```

### 第一次接入当前电脑

你不需要去项目负责人电脑上取 token。项目负责人会通过安全渠道把 token 明文发给当前电脑的使用者。

拿到 token 和接入信息后，在当前这台要接入的新电脑上执行。把 `<项目负责人发给你的token>` 替换成负责人私聊发来的完整 token，把 `<同事英文或拼音ID>` 替换成信息包里的同事 ID。

```bash
git clone https://github.com/meimei7959/company_knowledge_core.git
cd company_knowledge_core

export ZHENZHI_KNOWLEDGE_API_TOKEN_PROD='<项目负责人发给你的token>'
bash scripts/setup-teammate.sh --user-id <同事英文或拼音ID> --ai-tool codex
```

如果使用 Claude：

```bash
export ZHENZHI_KNOWLEDGE_API_TOKEN_PROD='<项目负责人发给你的token>'
bash scripts/setup-teammate.sh --user-id <同事英文或拼音ID> --ai-tool claude
```

注意：

- token 只在当前终端会话里作为环境变量使用。
- 不要把真实 token 写入本文档、Git、任务描述、截图、聊天记录或审计正文。
- 如果终端关闭后需要重新执行接入命令，让负责人重新通过安全渠道提供 token，或者由使用者在自己的安全密码管理器中取出。

脚本会生成本机连接器文件：

```txt
.zhenzhi/config.json
.zhenzhi/agent-entrypoint.md
.zhenzhi/codex-start.md
.zhenzhi/claude-start.md
.zhenzhi/antigravity-start.md
agents/agent.<同事ID>.<ai-tool>.md
```

本地 AI 工具启动前必须先读：

```txt
.zhenzhi/agent-entrypoint.md
```

接入后检查：

```bash
python3 -m zhenzhi_knowledge.cli status
python3 -m zhenzhi_knowledge.cli api export >/dev/null
```

这两个命令通过后，说明你能读到线上中枢。

### 注册这台电脑为 Runner

为这台电脑取一个稳定的 runner id。格式建议：

```txt
runner.<同事ID>-<电脑名>-<ai-tool>
```

示例：

```bash
python3 -m zhenzhi_knowledge.cli runner register \
  --runner-id runner.lisi-mac-codex \
  --name "李四 Mac Codex Runner" \
  --host-type mac \
  --mode local \
  --agent agent.lisi.codex \
  --agent agent.company.project-manager \
  --agent agent.company.product-manager \
  --agent agent.company.architecture \
  --agent agent.company.design \
  --agent agent.company.development \
  --agent agent.company.test \
  --capability project_management \
  --capability requirement_clarification \
  --capability technical_solution \
  --capability ui_ux_design \
  --capability development \
  --capability testing \
  --capability task_result_writeback \
  --capability agent_team_growth \
  --data-scope local_repo \
  --ring-version single-machine-v1
```

只接入电脑时，不要填写 `--project` 和 `--repo`。因为当前还没有新项目，也没有业务代码仓库路径。

注册后发送心跳：

```bash
python3 -m zhenzhi_knowledge.cli runner heartbeat \
  --runner-id runner.lisi-mac-codex \
  --status online \
  --load 0 \
  --capability development \
  --capability testing
```

查看已注册 Runner：

```bash
python3 -m zhenzhi_knowledge.cli runner list
```

以后有新项目时，再把这台 Runner 绑定到项目：

```bash
python3 -m zhenzhi_knowledge.cli runner register \
  --runner-id runner.lisi-mac-codex \
  --name "李四 Mac Codex Runner" \
  --host-type mac \
  --mode local \
  --agent agent.lisi.codex \
  --capability development \
  --capability testing \
  --capability task_result_writeback \
  --project <新项目ID> \
  --repo <新项目本地仓库绝对路径> \
  --data-scope local_repo \
  --ring-version single-machine-v1
```

## 第二部分：新项目成功

### 在新项目上使用这套 Agent 团队

新业务项目应该有自己的项目目录或代码仓库，不要把业务代码直接放进 `company_knowledge_core`。

推荐目录：

```txt
~/Documents/projects/<新项目代码仓库>
~/Documents/company_knowledge_core
```

`company_knowledge_core` 是中枢和 Agent 团队规则仓库；新项目工作区是用户日常进入工作的目录。代码仓库不一定等于项目工作区：做软著、运营、素材、说明书时，代码只是参考源，必须放进工作区的源码镜像目录，和材料目录分开。

#### 新项目初始化脚本

创建新项目时，必须先分清两个目录，不能只创建中枢记录：

- 实体工作目录：用户能在 Finder 或本地文件系统里看到的真实项目目录。它是当前电脑自己的路径，不能从负责人电脑或其他 Runner 电脑复制。
- 源码镜像目录：当代码只是参考源时，Git 仓库放在实体工作目录下的源码镜像目录，后续 `git pull` 只影响源码镜像，不影响软著、运营、截图、说明书等材料。
- 中枢记录目录：知识中枢里的项目管理记录，例如 `projects/<project-id>/`。
- 禁止把实体工作目录建在 `company_knowledge_core` 里面。`company_knowledge_core` 只放中枢、Agent 规则、脚本、任务记录和审计，不放业务项目产物。

路径确认规则：

- 用户给出明确绝对路径时，按用户路径创建或登记。
- 用户只说“文稿”“本地”“Finder 里”“新建文件夹”，或发了本地文件夹截图时，先根据当前电脑推断候选路径，再向用户确认。
- 自动化或无人值守流程不能确认路径时，`workspaceRef` 写 `pending_confirmation`，不得声称实体工作目录已创建完成。
- 多电脑 Runner 场景中，每台电脑的本地 workspace 可以不同；中枢记录只能保存已确认的当前电脑路径，或保存可移植引用，例如 Git URL、`workspace://` 引用、项目相对路径。

新项目初始化必须优先使用脚本，不要手写整套项目 Markdown，也不要直接调用底层 `project register` 当作完成初始化。

```bash
python3 scripts/init_project.py \
  --project-id <新项目ID> \
  --name "<新项目中文名>" \
  --owner <负责人ID或姓名> \
  --goal "<项目目标>" \
  --workspace-profile development \
  --workspace-ref "<用户确认后的本机绝对路径>" \
  --source-file "<可选：PRD/原始资料路径>"
```

`--workspace-profile` 决定实体工作目录结构：

```txt
development 新开发项目：产品、设计、架构、研发工程、services、skills、测试、发布目录
delivery    普通交付项目：产品、架构、研发、测试、上线目录
operations 运营/素材/内容项目：资料来源、运营素材、内容生产、发布、复盘目录
copyright  软著/材料项目：源码镜像、软著材料、运营素材、过程记录、交付归档目录
```

项目经理 Agent 必须先判断项目类型：

```txt
用户要开始开发一个新产品/服务/工具 -> development
用户要围绕已有产品做运营、素材、官网、发布说明 -> operations
用户要基于已有代码做软著、说明书、截图、源代码整理 -> copyright
用户要做普通阶段性交付，但不是长期代码工程 -> delivery
用户只是接入电脑，还没有项目 -> 不初始化项目，只注册 Runner
```

如果是软著、运营素材、说明书这类项目，代码只是参考源，必须使用源码镜像参数：

```bash
python3 scripts/init_project.py \
  --project-id <新项目ID> \
  --name "<新项目中文名>" \
  --owner <负责人ID或姓名> \
  --goal "<项目目标>" \
  --workspace-profile copyright \
  --workspace-ref "<用户确认后的项目工作区>" \
  --source-repo-url "<Git 地址>" \
  --source-repo-path "<项目工作区里的源码镜像路径>" \
  --source-file "<可选：PRD/软著说明/原始资料路径>"
```

这个脚本会一次性完成：

```txt
创建实体项目目录和标准子目录
创建中枢 Project 记录
写入 workspaceRef
写入 workspaceProfile
登记 sourceRepoUrl/sourceRepoRef
登记 SourceMaterial
生成项目初始化任务
运行 bundle 校验
```

如果暂时无法确认本机实体目录，只允许显式使用：

```bash
python3 scripts/init_project.py \
  --project-id <新项目ID> \
  --name "<新项目中文名>" \
  --owner <负责人ID或姓名> \
  --allow-pending-workspace
```

这种情况下项目只能停在待确认状态，`workspaceRef` 会写成 `pending_confirmation`。后续初始化任务必须补齐真实路径；项目进入激活或完成状态前，不能还停在 `pending_confirmation`。

项目初始化完成前必须检查：

- `projects/<project-id>/project.md` 记录已确认的 `workspaceRef`，或明确记录 `workspaceRef: pending_confirmation`。
- 原始 PRD、截图、文档等本地资料复制或登记到实体工作目录的资料目录；不同 `workspaceProfile` 会使用不同目录。
- 如果项目使用源码镜像，源码镜像只允许读取和按需 `git pull`，不得写入软著、运营、截图、说明书或过程材料。
- 如果项目是新开发工程，`services`、`skills`、`apps`、`packages` 等只是本项目工作区的工程目录。它们不会从中枢自动复制；中枢只提供 Agent 规则、PM 调度、任务和证据写回能力。
- 项目工作区通过 `AGENTS.md` 和 `START_HERE.md` 接入桢知体系；本地 Agent 读取这两个入口后，再回到 `company_knowledge_core/projects/<project-id>/` 获取项目经理调度和任务上下文。
- `SourceMaterial.storageRef` 指向实体工作目录里的存储副本；`sourceRef` 可以保留原始来源。
- TaskResult 只写摘要、结论、风险、检查结果和证据引用；长日志、截图、PRD 全文、测试原始输出、研发产物不能写入中枢正文。
- TaskResult 的 `outputRefs` / `evidenceRefs` 同时覆盖实体工作目录或外部存储引用，以及中枢记录。
- 给人的回复先说实体工作目录，再说中枢记录路径。

项目 ID 使用小写英文、数字和短横线，例如：

```txt
customer-service-bot
sales-dashboard
internal-ops-tool
```

#### 项目初始化必须由项目经理 Agent 接管

初始化脚本只是创建项目实体、记录和初始化任务，不等于项目已经完成初始化。

项目经理 Agent 必须继续确认：

- 项目目标是什么。
- 是新建项目还是已有 Git 项目迁移。
- 项目 Owner 是谁。
- 是否需要产品经理 Agent 澄清需求。
- 是否需要设计 Agent 输出 UI/交互方案。
- 是否需要架构 Agent 输出技术方案。
- 研发 Agent 和测试 Agent 怎么接收任务。
- Runner 是哪台电脑。
- 验收标准、证据、上线条件是什么。

项目经理 Agent 的正式调度动作必须写 `pm-action`。

示例：

```bash
python3 -m zhenzhi_knowledge.cli project pm-action \
  --project <新项目ID> \
  --actor agent.company.project-manager \
  --intent dispatch \
  --current-state project_registered \
  --allowed-transition initialize_project_agent_team \
  --exit-state dispatched \
  --summary "接管新项目初始化，组建项目 Agent 团队并创建首批产品澄清任务。" \
  --task-id project-init-<新项目ID> \
  --requirement-ref PROJECT-INIT \
  --delegated-owner agent.company.product-manager \
  --delegated-owner agent.company.architecture \
  --delegated-owner agent.company.development \
  --delegated-owner agent.company.test \
  --next-action "Product Manager Agent clarifies product scope; Architecture Agent waits for accepted product package."
```

### 新项目动态流转

不要把项目流程写死。项目经理 Agent 必须根据项目类型、需求清晰度、界面复杂度、技术风险、测试风险和上线要求动态编排 Agent 队列。

默认参考链路是：

```txt
项目经理 Agent 接管
-> 产品经理 Agent 结构化需求和范围
-> 设计 Agent 输出 UI / 交互方案（有页面、工作台、用户操作、品牌体验时必须进入）
-> 架构 Agent 做技术方案（涉及系统边界、接口、数据、权限、安全、性能、长期演进时必须进入）
-> 产品经理 Agent 复核技术方案
-> 研发 Agent 接收审查并实现
-> 测试 Agent 接收审查并测试
-> 产品经理 Agent 产品验收
-> 项目经理 Agent 最终收口
```

项目经理 Agent 可以调整顺序，但必须写清原因：

- 需求已经非常清晰、范围已锁定：可以跳过产品澄清，但要记录依据。
- 没有用户界面、没有交互变化：可以跳过设计 Agent，但要记录依据。
- 只是低风险文档、配置、知识整理：可以跳过架构 Agent，但要记录依据。
- 有页面、工作台、表单、审批流、可视化、用户操作路径：必须加入设计 Agent。
- 有新接口、数据模型、权限、部署、跨系统集成、性能或安全风险：必须加入架构 Agent。
- 测试不通过：必须回到研发 Agent 修复，再由测试 Agent 回归，不能由 PM 或主线程代修。
- 产品验收不通过：必须回到产品指定的责任 Agent 返工。

无论怎么调整，项目经理 Agent 都必须通过 `pm-action` 写明本轮编排：

```txt
为什么需要这些 Agent
为什么跳过某些 Agent
每个下游 Agent 接收什么输入
每个阶段的验收证据是什么
失败后回到哪个 Agent
```

下游 Agent 接收上游交付物前，必须创建 `ReceiverReview`：

```txt
accepted_for_work              可以继续
accepted_with_assumptions      带明确假设继续
needs_rework                   打回返工
human_decision_required        需要人类决策
```

任务来源必须写清：

```txt
feature       必须关联 requirementRefs
bugfix        必须关联 defectRefs，可以没有 requirementRefs
project_setup 项目初始化
research      研究任务
knowledge_ingest 资料入库
maintenance   维护任务
```

### 日常工作命令

开始前同步：

```bash
python3 -m zhenzhi_knowledge.cli sync pull
```

开始一个任务：

```bash
python3 -m zhenzhi_knowledge.cli start \
  --project <新项目ID> \
  --agent agent.<同事ID>.<ai-tool> \
  --task "<本次任务描述>"
```

然后让本地 AI 工具读取：

```txt
.zhenzhi/context/current.md
```

如果执行的是已有任务卡：

```bash
python3 -m zhenzhi_knowledge.cli task pull <taskId>
python3 -m zhenzhi_knowledge.cli task start <taskId> \
  --actor agent.<同事ID>.<ai-tool>
```

完成任务后写回：

```bash
python3 -m zhenzhi_knowledge.cli task finish <taskId> \
  --result done \
  --summary "<完成内容、关键证据、剩余风险>" \
  --runner-id runner.<同事ID>-<电脑名>-<ai-tool> \
  --executor-agent agent.<实际岗位Agent> \
  --evidence-ref "<证据文件或测试报告>" \
  --test-or-check "<跑过的测试或检查>"
```

如果只是一次非任务卡的本地工作：

```bash
python3 -m zhenzhi_knowledge.cli finish \
  --project <新项目ID> \
  --agent agent.<同事ID>.<ai-tool> \
  --summary "<完成了什么、写回了什么、是否有阻塞>" \
  --result done
```

结束后同步：

```bash
python3 -m zhenzhi_knowledge.cli sync push
```

### 遇到问题怎么写回

如果任务做不了，不要静默停止。写回阻塞：

```bash
python3 -m zhenzhi_knowledge.cli task finish <taskId> \
  --result blocked \
  --summary "<为什么阻塞、缺什么输入、建议谁处理>" \
  --runner-id runner.<同事ID>-<电脑名>-<ai-tool> \
  --executor-agent agent.<实际岗位Agent> \
  --blocker "<阻塞原因>" \
  --next-action "<下一步 owner 和动作>"
```

如果发现 Bug，创建 Defect，再让 PM 路由 bugfix：

```bash
python3 -m zhenzhi_knowledge.cli defect create --help
python3 -m zhenzhi_knowledge.cli defect create-fix-task --help
```

如果发现的是 Agent 体系本身的问题，比如：

- 项目经理 Agent 不知道“同步到中枢”是什么意思。
- 项目初始化目录不清楚。
- 源码镜像和材料目录边界不清楚。
- Skill、上下文、权限、工具、调度、任务流转不顺。
- 用户在业务项目里发现了会影响其他项目复用的问题。

不要只写在当前业务项目的聊天里。项目经理 Agent 必须执行“上报体系问题”：

```bash
cd <company_knowledge_core 本机目录>
python3 scripts/agent_feedback.py system-issue \
  --source-project <当前业务项目ID> \
  --title "<问题标题>" \
  --actual "<实际发生了什么>" \
  --expected "<期望应该怎么工作>" \
  --evidence-ref "<可选：截图路径、任务ID、对话摘要或文件路径>"
```

这条命令会在中枢 `company-knowledge-core` 项目下创建：

- `Defect`：记录体系问题。
- PM 分诊任务：让中枢项目经理决定是改流程、改 Skill、改脚本、改工作台，还是交给研发修。

用户可以直接对业务项目里的 Codex 说：

```txt
把这个体系问题上报到中枢。来源项目是 <项目ID>，标题是 <问题标题>，实际发生了 <实际情况>，期望应该是 <期望行为>。
```

项目经理 Agent 不需要理解中枢内部目录，只需要执行上面的命令。目的不是抱怨，而是让 Agent 团队沉淀经验，后续能自动改进。

### Skill 不够用时怎么沉淀复用

如果某个岗位 Agent 在业务项目里发现原 Skill 不够用，例如知识工程 Agent 做软著时缺少“软著材料整理/源码清单/截图证据”能力：

- 当前项目可以先用临时方案完成交付。
- 临时方案只能服务当前项目，不能自动变成所有项目可复用能力。
- 想让其他项目复用，必须同步到中枢 Skill 注册表。
- `skill-gap` 必须在中枢仓库的 `feedback/*` 或 `codex/*` 分支写入，不能直接写 `main`。

执行：

```bash
cd <company_knowledge_core 本机目录>
git switch -c feedback/<当前业务项目ID>-<稳定英文ID>
python3 scripts/agent_feedback.py skill-gap \
  --source-project <当前业务项目ID> \
  --skill-id "<稳定英文ID，例如 softcopyright-submission-pack>" \
  --name "<Skill 中文名>" \
  --purpose "<这个 Skill 要解决什么复用能力>" \
  --gap "<当前 Skill 缺什么>" \
  --proposed-use "<未来哪些项目/岗位会复用>" \
  --source-ref "<可选：截图路径、任务ID、对话摘要或文件路径>"
```

如果已经在合适的 `feedback/*` 或 `codex/*` 分支上，可以沿用现有分支，不必重复创建。写完后推送该分支，请知识工程/PM 评审；不要把 skill-gap 直接提交到 `main`。

这条命令会在中枢创建：

- `SkillAsset`：状态是 `draft`，不是立即全公司默认启用。
- 知识工程评审任务：补输入输出契约、案例、测试、适用范围和推广策略。

推广规则：

- `scope=project`：只给当前项目用。
- `scope=company`：进入公司级复用候选，但必须评审和测试通过后再推广。
- 没有中枢 `SkillAsset`、没有评审任务、没有测试证据的 Skill，不算可复用 Skill。

兼容说明：旧脚本 `scripts/report_system_issue.py` 和 `scripts/report_skill_gap.py` 仍可运行，但只是统一入口的兼容 wrapper。新项目、新文档和 Agent 教学都应使用 `scripts/agent_feedback.py`。

## 验收标准

### 第一阶段：什么时候算电脑接入成功

同时满足这些条件，才算这台电脑接入成功：

- `status` 可以访问线上 API。
- `setup-teammate.sh` 已完成，本地生成 `.zhenzhi/agent-entrypoint.md`。
- `runner register` 生成了 Runner 记录。
- `runner heartbeat` 能把本机状态写回中枢。
- `runner list` 能看到这台 Runner。
- `python3 -m zhenzhi_knowledge.cli validate` 通过。
- 没有 token 或 secret 出现在 Git diff 中。

第一阶段不要求：

```txt
新项目 ID
项目中文名
项目 owner
项目目标
业务仓库路径
PRD / source-file
项目任务 start / finish
```

### 第二阶段：什么时候算新项目成功

有明确新项目后，同时满足这些条件，才算新项目初始化成功：

- 新项目已通过 `python3 scripts/init_project.py ...` 初始化。
- `Project.workspaceRef` 是已确认路径、Git URL、`workspace://`、相对路径，或明确的 `pending_confirmation`。
- 如果有 PRD、截图、文档等原始资料，已登记为 `SourceMaterial`。
- 项目初始化任务已生成。
- 项目经理 Agent 已用 `pm-action` 接管初始化。
- 项目经理 Agent 已按项目实际情况动态决定是否需要产品、设计、架构、研发、测试 Agent。
- 至少一个正式任务能从 `start` 到 `finish` 写回 TaskResult。
- `python3 -m zhenzhi_knowledge.cli validate` 通过。
- 没有 token 或 secret 出现在 Git diff 中。

## 给本机 Agent 的启动提示

把下面这段作为当前电脑上的本机 Agent 启动提示：

```txt
你是接入桢知 Agent 团队的本机 Agent。

先读取：
1. .zhenzhi/agent-entrypoint.md
2. docs/guides/teammate-agent-new-project-onboarding.md
3. docs/agent-team/company-agent-constitution.md
4. docs/agent-team/agent-task-runtime-contract.md
5. docs/agent-team/role-operating-specs.json

先判断当前任务模式：

A. 如果只是接入电脑：
- 只确认 token、同事 ID、AI 工具、runnerId、Runner 名称。
- 注册 Runner 并发送 heartbeat。
- 不要要求 projectId、项目中文名、项目 owner、项目目标、业务仓库路径或 PRD。
- 电脑接入成功后写清：这台电脑已可作为 Runner 使用，后续有新项目再进入项目初始化。

B. 如果是启动新项目：
- 再确认 projectId、项目中文名、项目 owner、项目目标、业务仓库路径、可选 PRD / source-file。
- 新项目不在 company_knowledge_core 里直接写业务代码。
- 新项目必须先用 python3 scripts/init_project.py 初始化。
- 没有确认 workspaceRef 时只能显式 pending_confirmation，不能声称实体工作目录已完成。

正式 PM 动作必须走 project pm-action。
下游 Agent 接收上游交付前必须写 ReceiverReview。
完成任务必须写 TaskResult、证据和测试/检查。
遇到阻塞必须写 blocked 结果并给 nextAction，不要停在本地。
```
