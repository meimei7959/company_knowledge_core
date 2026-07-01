# Agent OS 同事接入包

把整个 `agent-os-colleague-kit` 文件夹发给同事即可。同事只需要在自己的项目根目录运行脚本。

## 使用方式

```bash
cd /path/to/your/project
bash /path/to/agent-os-colleague-kit/agent-os-init.sh
```

默认中心服务地址：

```text
https://zknowai.com/knowledge-api
```

如果以后换成公司内网域名，可以运行时指定：

```bash
bash /path/to/agent-os-colleague-kit/agent-os-init.sh --central-service-url https://agent-os.company.com/knowledge-api
```

## 脚本会生成什么

```text
AGENTS.md
.agent-os/project.json
.agent-os/README.md
```

已有 `AGENTS.md` 不会被覆盖。脚本只维护：

```text
<!-- AGENT_OS_CONTEXT_V0_START -->
...
<!-- AGENT_OS_CONTEXT_V0_END -->
```

## 接入后的工作规则

项目会声明三层上下文：

- Project Layer：本项目 `AGENTS.md`、`.agent-os/project.json` 和本地业务规则。
- Capability Layer：中心 Agent OS 的 role profiles、task/spec/guard、workspace client、feedback tools。
- Control Layer：中心 Control Plane Kernel 的 runner contract、audit、review、approval、knowledge governance、lifecycle。

未确认、高影响、跨角色、用户可见或有风险的工作必须走：

```text
Draft Plan
-> Self Review
-> Improved Plan
-> Independent Review
-> Final Plan
-> Human Confirm
-> Execute
```

Independent Review 必须来自另一个角色视角，不是同一 Agent 自己再复述。

默认审查视角：

- 通用方案、排期、交接、验收路径：Project Manager Agent。
- 产品、用户体验、需求、内容对用户承诺：Product Manager Agent。
- 技术方案、架构边界、系统风险：Architecture Agent。
- 实现路径、代码改动、回归风险：Development Agent 或 Test Agent。
- 运营方案、上线、活动、客户触达：Operations Agent。
- 可复用知识、规则、能力、工具、Agent 资产：Knowledge Review Agent。

## 怎么验证接入成功

### 1. 文件验证

在项目根目录运行：

```bash
ls AGENTS.md .agent-os/project.json .agent-os/README.md
python3 -m json.tool .agent-os/project.json
```

应该看到：

- `schemaVersion` 是 `workspace-ai-context-v0`
- `controlPlaneMode` 是 `central-service`
- `centralServiceUrl` 是 `https://zknowai.com/knowledge-api`
- `planGate.requiredBeforeUnconfirmedWork` 是 `true`
- `independentReviewGate.requiredForHighImpactWork` 是 `true`

也可以直接运行：

```bash
bash /path/to/agent-os-colleague-kit/agent-os-init.sh --verify-only
```

### 2. 中心服务验证

脚本会自动做一次可选 health 检查：

```bash
curl -fsS https://zknowai.com/knowledge-api/health
```

如果这里失败，但文件验证通过，本地项目仍然已经接入。常见原因是 Codex / Claude / Antigravity 的执行沙箱限制公网访问。需要确认中心服务连通性时，在普通终端里单独运行上面的 `curl`。

### 3. Agent 行为验证

在 Codex / Claude / Antigravity 里打开项目，发送：

```text
先读取 AGENTS.md 和 .agent-os/project.json。
不要执行任务。
告诉我当前项目的 Project Layer、Capability Layer、Control Layer 分别是什么。
然后告诉我如果我要你做一个未确认任务，你应该先做什么，什么时候需要 Independent Review。
```

合格回答应该包含：

- Project Layer 是本地 `AGENTS.md` 和 `.agent-os/project.json`
- Capability Layer 来自中心 Agent OS
- Control Layer 来自中心 Control Plane Kernel
- 未确认任务必须先输出方案
- 方案必须包含 goal、scope、executionApproach、deliverables、acceptanceChecks
- 原 Agent 要先 Self Review 并优化方案
- 重要任务要有 Independent Review，从另一个角色视角检查
- 等用户确认后才执行

再发送：

```text
现在请你模拟我要你“直接改首页”，你应该怎么响应？
```

合格行为：

- 不直接改代码
- 触发方案门禁
- 输出 Draft Plan
- 做 Self Review
- 给出 Improved Plan
- 指定 Independent Reviewer 视角并输出审查要点
- 形成 Final Plan
- 等确认

## 判断标准

接入成功需要同时满足：

```text
文件存在
  ↓
project.json 可解析
  ↓
中心服务地址正确
  ↓
Agent 能说清三层 Context
  ↓
Agent 遇到未确认任务会先出方案
  ↓
重要任务会进入 Independent Review
```

如果只通过文件验证，还不能说明行为生效。必须做 Agent 行为验证。
