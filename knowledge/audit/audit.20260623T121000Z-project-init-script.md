---
type: AuditLog
title: audit.20260623T121000Z-project-init-script
timestamp: "2026-06-23T12:10:00Z"
auditId: audit.20260623T121000Z-project-init-script
actor: agent.company.project-manager
action: process.guardrail.implement
targetRef: scripts/init_project.py
before: new_project_initialization_relied_on_manual_markdown_and_docs
after: project_initialization_script_and_workspace_validation_added
policyResult: executable_guardrail_added
---

## Details

intent=avoid_manual_new_project_initialization_errors
implemented=Added scripts/init_project.py, workspaceRef defaults and validation, CLI workspace-ref support, and tests.
validation=Related unittest subset passed; git diff --check passed. Full bundle validation is currently blocked by unrelated ANOS-REQ-161 test artifact issues.
updatedRefs=scripts/init_project.py, zhenzhi_knowledge/core.py, zhenzhi_knowledge/cli.py, tests/test_cli.py, docs/guides/teammate-agent-new-project-onboarding.md, projects/billing-lite/lessons.md
