---
type: ToolAsset
title: DESIGN.md Toolkit
description: Local CLI toolkit for validating, diffing, exporting, and describing project-level DESIGN.md files for Agent UI work.
resource: npm:@google/design.md
timestamp: "2026-07-01T07:05:43Z"
toolId: tool.design-md
owner: agent.company.design
repoRef: https://github.com/google-labs-code/design.md
entrypoint: design.md
packageName: "@google/design.md"
version: 0.3.0
status: approved
scope: company
riskLevel: L2
invocationPolicy: agent_policy_allowed
requiresApproval: []
executionMode: local_runner_required
installCommand: npm install @google/design.md --ignore-scripts --no-audit --no-fund
usageCommands:
  - npx --no-install design.md lint DESIGN.md
  - npx --no-install design.md diff DESIGN.md DESIGN-v2.md
  - npx --no-install design.md export --format json-tailwind DESIGN.md
  - npx --no-install design.md export --format css-tailwind DESIGN.md
  - npx --no-install design.md export --format dtcg DESIGN.md
  - npx --no-install design.md spec --rules
allowedAgents:
  - agent.company.design
  - agent.company.development
  - agent.company.test
allowedProjects: []
secretsRequired: []
capabilities:
  - design_md_lint
  - design_md_diff
  - design_md_export_tailwind
  - design_md_export_dtcg
  - design_md_spec_prompt_context
sourceRefs:
  - https://github.com/google-labs-code/design.md
  - https://github.com/voltagent/awesome-design-md
verifiedTrial:
  timestamp: "2026-07-01T07:13:27Z"
  workspace: /private/tmp/designmd-install-test
  packageVersion: 0.3.0
  checks:
    - npm view returned bin design.md/designmd and version 0.3.0
    - npm install @google/design.md --ignore-scripts --no-audit --no-fund completed in 13 seconds
    - local node_modules/.bin/design.md help, lint, and export commands succeeded
    - npx --no-install design.md and npm exec -- design.md succeeded after local install
knownIssues:
  - Direct npx design.md is wrong because npm treats design.md as a package name and returns 404.
  - Use local install first, then npx --no-install design.md, npm exec -- design.md, or ./node_modules/.bin/design.md.
  - The tool validates token structure and exports tokens; it does not judge full visual taste, layout quality, or product fit.
lastVerifiedAt: "2026-07-01T07:13:27Z"
---

# DESIGN.md Toolkit

## Purpose

This ToolAsset registers `@google/design.md` as an approved local tool for project-level design source files.

## Policy

- `allowedProjects: []` means company-wide visibility for approved project contexts.
- Design Agent owns creation and changes to project `DESIGN.md`.
- Development Agent may consume `DESIGN.md` and token exports for implementation.
- Test Agent may use `DESIGN.md` and lint/diff output as visual QA evidence.
- The tool must not fetch private design sources, store credentials, or replace rendered UI checks.
