---
type: AuditLog
title: audit.20260621T082956-requirement-definition-skill-update
timestamp: 2026-06-21T08:29:56Z
auditId: audit.20260621T082956-requirement-definition-skill-update
actor: agent.company.product-manager
action: skill.package.updated
targetRef: skills/product-manager-agent/SKILL.md
before: Product Manager Agent skill could treat functional requirements, modules, tasks, and tests as requirements without enforcing requirement hierarchy
after: Product Manager Agent skill defines valid requirements, requirement hierarchy, pseudo-requirement rejection, requirement tree output, and requirement-to-test/acceptance mapping
policyResult: skill documentation update only; approval of skill rollout still follows SkillAsset and review rules when used as registered reusable skill
---

## Details

Updated Product Manager Agent skill to preserve the distinction between business requirements, user requirements, product requirements, functional requirements, development tasks, test cases, and acceptance gates.

updatedRefs:
- skills/product-manager-agent/SKILL.md
- skills/product-manager-agent/references/output-contract.md
- skills/product-manager-agent/references/requirement-definition.md
