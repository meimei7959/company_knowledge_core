---
type: AuditLog
title: audit.20260624T040043608141Z
timestamp: "2026-06-24T04:00:43Z"
auditId: audit.20260624T040043608141Z
actor: agent.company.project-manager
action: pm.action.record
targetRef: projects/company-knowledge-core/pm-actions/pm-action.20260624T040043607612Z.md
before: unified_feedback_deployed
after: dispatched
policyResult: pm_action_runtime
---

## Details

intent=dispatch
transition=add_feedback_branch_governance
summary=项目经理调度 Git 分支治理：未审核 Skill/工作流反馈不得直接写入 main，需在 feedback/codex 分支完成架构、知识工程、测试、PM 审核后再合入 main。
