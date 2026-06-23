---
type: AuditLog
title: V1 workbench Agent boundary guard
timestamp: "2026-06-22T04:35:10Z"
projectId: company-knowledge-core
actor: agent.company.project-manager
status: observed
riskLevel: L1
sourceRefs:
  - docs/agent-team/common-agent-operating-rules.md
  - agents/agent.company.project-manager.md
  - projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-design.md
  - projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-product-review.md
  - projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-dev.md
  - projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-test.md
  - projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-product-final-acceptance.md
  - projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-pm-final-acceptance.md
---

## Summary

The main thread directly edited the V1 workbench draft before the formal Design/Product/Development/Test Agent chain completed. This is treated as a process defect, not completed product evidence.

## Correction

- Added the main-thread substitute-work isolation rule to the common Agent operating rules.
- Added the Project Manager Agent operating note that direct main-thread edits remain unaccepted drafts until role TaskResults exist.
- Created the V1 workbench Agent task chain: Design, Product review, Development, Test, Product final acceptance, and PM final acceptance.
- Added validator and unit-test coverage requiring the Agent task chain before desktop workbench slice0 validation passes.

## Operating Decision

Future workbench, scheduler, Agent Ring, approval, requirement-tree, API, or data-model changes must be routed through the owning role Agents. PM may coordinate and close based on evidence, but must not replace Product, Design, Development, or Test conclusions.
