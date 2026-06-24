---
type: Defect
title: billing-lite project entry references missing central project path
description: Bug or quality issue that can create bugfix ProjectTasks without a product requirement.
timestamp: "2026-06-24T12:33:38Z"
defectId: defect.20260624T123338408097Z
projectId: company-knowledge-core
reporter: agent.company.project-manager
owner: ""
severity: medium
status: triaged
requirementRefs: []
sourceTaskRef: ""
sourceResultRef: ""
evidenceRefs:
  - "sourceProject:billing-lite"
  - /Users/meimei/Documents/统一付费轻服务/AGENTS.md
expectedBehavior: Central project refs declared by entity workspace should exist, or the entity AGENTS.md should reference the actual central project path so PM actions, TaskResults, ReceiverReview, and audits can be written to the correct project.
actualBehavior: Entity workspace AGENTS.md references /Users/meimei/Documents/company_knowledge_core/projects/billing-lite/project.md, tasks/index.md, sources/sm-billing-lite-prd-v1.md, and AGENTS.md, but these files are absent while central validate passes.
reproductionSteps:
  - Read /Users/meimei/Documents/统一付费轻服务/AGENTS.md, ran python3 -m zhenzhi_knowledge.cli validate in company_knowledge_core, then attempted to read projects/billing-lite/project.md and related files.
fixTaskRefs:
  - projects/company-knowledge-core/tasks/kt-20260624-002.md
regressionEvidenceRefs: []
auditRefs:
  - knowledge/audit/audit.20260624T123338410818Z.md
updatedAt: "2026-06-24T12:33:38Z"
---

## Expected Behavior

Central project refs declared by entity workspace should exist, or the entity AGENTS.md should reference the actual central project path so PM actions, TaskResults, ReceiverReview, and audits can be written to the correct project.

## Actual Behavior

Entity workspace AGENTS.md references /Users/meimei/Documents/company_knowledge_core/projects/billing-lite/project.md, tasks/index.md, sources/sm-billing-lite-prd-v1.md, and AGENTS.md, but these files are absent while central validate passes.

## Reproduction Steps

- Read /Users/meimei/Documents/统一付费轻服务/AGENTS.md, ran python3 -m zhenzhi_knowledge.cli validate in company_knowledge_core, then attempted to read projects/billing-lite/project.md and related files.

## Evidence

- sourceProject:billing-lite
- /Users/meimei/Documents/统一付费轻服务/AGENTS.md
