# Agent Hub Feishu Menu

## Purpose

The Feishu bot should help employees who do not understand the knowledge engineering system yet.

Menus are shortcuts into guided workflows. They do not grant permission by themselves. Every menu action still goes through Agent Gateway, risk classification, project ownership, review, approval, and audit rules.

The same bot has two runtime modes:

- Private chat: Company Agent Hub mode.
- Project group chat: Project Assistant mode.

Feishu custom menus are bot-level configuration and cannot be split by private chat vs group chat. Configure one unified menu. The backend uses `chatType`, `chatId`, project binding, user identity, and message content to route the same menu text to the right guidance.

## Unified Menu

Recommended menu items:

| Level 1 | Menu | Sends Text | Purpose |
| --- | --- | --- | --- |
| 开始 | 新手引导 | 新手引导 | Explain what Agent Hub can do |
| 开始 | 查知识 | 查知识 | Show knowledge lookup guidance |
| 项目 | 创建项目 | 创建项目 | Start project creation guidance |
| 项目 | 绑定项目群 | 绑定项目群 | Start project group binding guidance |
| 项目 | 项目交接 | 项目交接 | Start handoff draft guidance |
| Agent | 组建 Agent 团队 | 组建 Agent 团队 | Route to Project Manager Agent guidance |
| Agent | 召唤 Agent | 召唤 Agent | Ask for target, project, phase, and expected output |
| 知识 | 记录资料 | 资料：项目 <项目名称>\n<内容> | Register project material and create a processing task |
| 知识 | 会议纪要 | 会议纪要：项目 <项目名称>\n<内容> | Register meeting notes and create a knowledge task |
| 知识 | 待审核 | 待审核 | Show review queue |
| 权限 | 申请工具/技能 | 申请工具/技能 | Start ToolAsset or SkillAsset draft intake |

Access credential requests are intentionally not a top-level menu item. They are advanced setup flows for Agent Ring, local tools, model APIs, or service integration. Employees should describe the access need in natural language or enter through `申请工具/技能`; the bot can still route real credential needs into the private approval flow.

## Newcomer Guide

The human-facing guide for employees is:

```txt
docs/guides/agent-hub-user-guide.md
```

The bot's `新手引导` reply should stay short. Long explanations, diagrams, menu map, examples, and safety boundaries belong in the guide.

Product workflow and future interactive card spec:

```txt
docs/agent-team/agent-hub-product-workflows.md
```

## Safety Rules

- Menu clicks never bypass permission checks.
- Destructive requests are blocked and converted into approval guidance.
- Access credential requests must stay in private chat when any secret value or personal setup instruction is involved.
- The bot records approval and `secretRef`; plaintext secret values must not enter project files, knowledge files, group chats, or audit details.
- Tool use and tool result storage are separate decisions.
- Project writeback requires project membership or owner approval.
- Knowledge publication requires Knowledge Engineering Agent review sub-agent gate and human approval when status becomes verified, approved, active, high-risk, or cross-team.

## Implementation Notes

The first implementation can use Feishu menu items that send fixed text messages. The bot recognizes these texts and returns text cards with guided next steps.

Later versions should replace text cards with Feishu interactive cards. The same intake fields, confirmation steps, safety checks, approval gates, and audit rules must remain.
