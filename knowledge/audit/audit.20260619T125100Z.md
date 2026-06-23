---
type: AuditLog
event: update_company_agent_team_operating_guide
actor: agent.company-knowledge-core.knowledge-engineering
timestamp: 2026-06-19T12:51:00Z
relatedKnowledge:
  - knowledge/company/company-agent-team-operating-guide.md
relatedSource:
  - docs/agent-team/company-agent-team-operating-guide.md
feishuDocUrl: https://xcn68awb7dsi.feishu.cn/docx/YnHudAQfVowx6vxnDfUc5C7onve
requiresReview: true
requiresHumanApproval: true
---

# Audit Log: Update Company Agent Team Operating Guide

Updated the company Agent Team operating guide to use Chinese as the primary language and added explicit update governance.

Reason:

- The guide is the working manual for all Agents and human collaborators.
- The user required the document to be clear in Chinese.
- The user required a mechanism to keep the document always current.
- The user required revision history that records why a change happened and who changed it.

Changes:

- Rewrote `docs/agent-team/company-agent-team-operating-guide.md` in Chinese.
- Added the update mechanism: local source update, Feishu sync, revision entry, AuditLog, Knowledge Engineering review, and human approval when cross-team standards are affected.
- Added ownership and routing rules for Agent role, Skill, workflow, scheduler, Agent Ring, and knowledge rule changes.
- Added revision record requirements and initial revision rows.
- Updated `knowledge/company/company-agent-team-operating-guide.md` to reference the Chinese source guide and Feishu document.
- Recreated the Feishu document under the Agent Hub production app and switched the source-of-truth link to the new document.

Review note:

This change affects company-level Agent operating standards and should remain draft until Knowledge Engineering review and human approval complete.
