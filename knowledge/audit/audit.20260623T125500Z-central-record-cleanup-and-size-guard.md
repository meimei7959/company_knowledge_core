---
type: AuditLog
title: audit.20260623T125500Z-central-record-cleanup-and-size-guard
timestamp: "2026-06-23T12:55:00Z"
auditId: audit.20260623T125500Z-central-record-cleanup-and-size-guard
actor: agent.company.project-manager
action: repository.cleanup_and_validation_guard
targetRef: zhenzhi_knowledge/core.py
before: oversized_records_not_blocked
after: oversized_records_blocked_and_erroneous_project_records_removed
policyResult: valid
---

## Details

summary=Removed erroneous project management records after owner correction, cleared associated global references, and added validation guards that keep central records compact while requiring bulky source materials to use storageRef.
updatedRefs=zhenzhi_knowledge/core.py, tests/test_cli.py, scripts/init_project.py, docs/guides/teammate-agent-new-project-onboarding.md
validation=python3 -m zhenzhi_knowledge.cli status -> valid
