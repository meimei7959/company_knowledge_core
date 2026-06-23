---
type: ToolAsset
title: Development Engineering Quality Toolkit
description: Project-specific static quality gate toolkit for Development Agent code changes in company_knowledge_core.
resource: local-python-script-and-agent-skill
timestamp: "2026-06-23T08:35:00Z"
toolId: tool.development-engineering-quality-toolkit
owner: development
repoRef: projects/company-knowledge-core/tools.md
entrypoint: python3 scripts/quality/development_quality_gate.py --root .
version: 0.1.0
status: testing
scope: company
riskLevel: L2
invocationPolicy: agent_policy_allowed
requiresApproval: []
executionMode: read_only_scan
allowedAgents:
  - agent.company.development
  - agent.company.project-manager
  - agent.company.architecture
  - agent.company.test
allowedProjects:
  - company-knowledge-core
secretsRequired: []
capabilities:
  - changed_file_scan
  - large_file_guard
  - high_risk_core_file_guard
  - python_symbol_length_guard
  - required_test_evidence_guard
  - architecture_review_required_guard
  - task_result_quality_gate_evidence
inputSchemaRef: skills/development-engineering-quality-gate/SKILL.md
outputSchemaRef: skills/development-engineering-quality-gate/SKILL.md#output-contract
knownIssues:
  - Static heuristics can produce false positives and must be interpreted by Development, Architecture, or Test Agent.
  - The script checks local Git changes; remote branch or CI-only changes require separate evidence.
  - Thresholds are intentionally conservative and should be tuned from real TaskResult evidence.
lastVerifiedAt: ""
---

# Development Engineering Quality Toolkit

## Purpose

This ToolAsset gives Development Agent and PM/Test/Architecture reviewers a repeatable static gate for code quality in the AI-native OS repository.

## Default Command

```bash
python3 scripts/quality/development_quality_gate.py --root .
```

When high-risk files are intentionally touched:

```bash
python3 scripts/quality/development_quality_gate.py --root . --architecture-review-ref <architecture-review-ref>
```

When tests cannot be added or run:

```bash
python3 scripts/quality/development_quality_gate.py --root . --allow-missing-tests "<blocker reason>"
```

## Gate Behavior

The toolkit reports:

- changed files, including untracked files;
- high-risk core files requiring Architecture Agent review;
- large file and file-growth violations;
- long Python functions/classes;
- code changes without test updates;
- pass/warn/fail verdict for TaskResult evidence.

## Boundaries

- This toolkit does not replace Test Agent, Architecture Agent, CI, security review, or human approval.
- A passing static gate does not mean product acceptance.
- A failing static gate blocks Development Agent handoff unless PM/Architecture records an explicit blocker or exception.
