---
type: AuditLog
auditId: audit.20260623T000000-software-copyright-skill-integration
title: 软著材料 Skill 融入项目技能体系
timestamp: "2026-06-23T00:00:00Z"
createdAt: "2026-06-23T00:00:00Z"
projectId: company-knowledge-core
actor: agent.company-knowledge-core.knowledge-engineering
action: software-copyright-skill.integrate
target: skills/china-software-copyright-submission-pack/SKILL.md
---

# AuditLog: 软著材料 Skill 融入项目技能体系

## Summary

将下载目录中的 `china-software-copyright-submission-pack` 融入当前项目生产 Skill 体系。

## Decision

软著材料准备不由项目经理 Agent 单独负责。项目经理 Agent 负责上线节点、任务创建、风险和状态追踪；知识工程 Agent 负责软著材料包整理、证据映射、缺件清单、内部归档和合规检查；申请负责人或法务/行政负责人负责最终申请表、权属事实、AI 使用声明和提交。

## Changes

- 新增 `skills/china-software-copyright-submission-pack/`。
- 保留下载包核心脚本 `softcopyright.py`、`submission_pack.py`、参考资料和模板资产。
- 新增项目生产 Skill 入口 `SKILL.md`、交付卡、输出模板和质量示例。
- 更新 `docs/agent-team/company-skill-registry.json`，将 Skill 注册给知识工程 Agent。
- 更新 `docs/agent-team/role-operating-specs.json`，让知识工程 Agent 持有该 Skill，项目经理 Agent 只负责触发和追踪。
- 更新项目经理、知识工程岗位说明和团队指南。
- 更新 AI Native OS 测试用例，覆盖软著任务触发、材料包产出和错误归属阻断。

## Safety

- 不新增公司级 Agent。
- 不把软著材料生产职责放到项目经理 Agent。
- Agent 不代写源代码、说明书正文、权属事实、申请表声明或签章材料。
- `finalize-human` 只能由申请负责人在核对当前官方表单和真实 AI 使用事实后手动执行。
