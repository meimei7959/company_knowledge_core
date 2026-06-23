---
type: AuditLog
title: audit.20260623T124500Z-central-record-size-guard
timestamp: "2026-06-23T12:45:00Z"
auditId: audit.20260623T124500Z-central-record-size-guard
actor: agent.company.project-manager
action: process.guardrail.implement
targetRef: zhenzhi_knowledge/core.py
before: central_repository_could_accept_large_project_records
after: central_record_size_and_bulky_source_material_guards_added
policyResult: data_growth_guardrail_added
---

## Details

intent=prevent_online_central_server_data_explosion
implemented=Lowered inline SourceMaterial raw text limit, added central record size validation for non-core project records, required storageRef for bulky SourceMaterial types, updated project workspace entrypoints and onboarding guidance.
updatedRefs=zhenzhi_knowledge/core.py, tests/test_cli.py, scripts/init_project.py, docs/guides/teammate-agent-new-project-onboarding.md, projects/billing-lite/lessons.md
