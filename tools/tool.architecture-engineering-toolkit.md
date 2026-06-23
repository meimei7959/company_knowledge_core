---
type: ToolAsset
title: Architecture Engineering Toolkit
description: Capability contract for architecture decision, diagram, dependency, API contract, and security guardrail tools used by Architecture Agent.
resource: local-agent-skills-and-approved-open-source-tools
timestamp: "2026-06-23T03:45:00Z"
toolId: tool.architecture-engineering-toolkit
owner: architecture
repoRef: projects/company-knowledge-core/tools.md
entrypoint: Agent Ring local runner resolves approved CLI or documentation tool per task
version: 0.1.0
status: testing
scope: company
riskLevel: L2
invocationPolicy: agent_policy_allowed
requiresApproval: []
executionMode: dry_run_default
allowedAgents:
  - agent.company.architecture
allowedProjects:
  - company-knowledge-core
secretsRequired: []
capabilities:
  - architecture_decision_record
  - c4_model_diagram
  - markdown_diagram
  - dependency_boundary_analysis
  - api_contract_lint
  - static_guardrail_scan
  - code_query_security_review
  - architecture_evidence_packet
inputSchemaRef: docs/agent-team/architecture-agent-role-and-skill-pack.md#input-contract
outputSchemaRef: docs/agent-team/architecture-agent-role-and-skill-pack.md#output-contract
knownIssues:
  - This is a registry contract; it does not prove every candidate CLI is installed on every runner.
  - External scanners must run in read-only or dry-run mode unless the task explicitly authorizes changes.
  - Generated diagrams and analysis reports are evidence, not verified reusable knowledge until review passes.
lastVerifiedAt: ""
---

# Architecture Engineering Toolkit

## Purpose

This ToolAsset gives the Architecture Agent an auditable tool belt for technical design and architecture review. It groups mature open-source tool families into one governed capability contract while keeping concrete execution local to Agent Ring or the manual Codex runner.

## Tool Families

| Family | Candidate tools | Use in Architecture Agent work |
| --- | --- | --- |
| Architecture decision records | `architecture-decision-record/architecture-decision-record`, `npryce/adr-tools` | Capture ArchitectureDecision context, options, status, and consequences. |
| Architecture diagrams as code | `structurizr/java` Structurizr DSL, `mermaid-js/mermaid`, `plantuml/plantuml`, `C4-PlantUML/C4-PlantUML` | Produce C4/context/container/component, sequence, state, and dependency views that stay reviewable in Git. |
| Dependency boundary checks | `sverweij/dependency-cruiser`, `madge/madge` | Detect cycles, forbidden imports, layer leaks, and module boundary violations. |
| API contract checks | `stoplightio/spectral`, `OpenAPITools/openapi-generator` | Lint OpenAPI/AsyncAPI style and detect contract drift before implementation or release. |
| Static guardrail scans | `semgrep/semgrep`, `github/codeql` | Support architecture review with policy, security, and code-query evidence. |

## Invocation Policy

- Default mode is read-only or dry-run.
- Architecture Agent may cite outputs in TechnicalArchitecturePlan, ArchitectureDecision, or CodeArchitectureReview.
- Any command that writes source code, changes dependencies, calls external services with secrets, or changes CI policy needs explicit task permission or Tool Owner approval.
- Runner must record concrete tool name, version when available, command or integration path, output reference, and limitations in TaskResult evidence.

## Evidence Standard

Architecture conclusions based on this toolkit must include:

- inspected repo path, API/schema path, or architecture document path;
- tool family and concrete candidate tool used;
- key finding with severity and affected boundary;
- false-positive or confidence note;
- next action: approve, repair, investigate, or route to another role.

## External Signals

Selected because they are common architecture-agent support tools on GitHub:

- `mermaid-js/mermaid`: high-adoption text diagrams in Markdown.
- `architecture-decision-record/architecture-decision-record` and `npryce/adr-tools`: ADR documentation and CLI workflow.
- `structurizr/java` / Structurizr DSL and C4-PlantUML: C4 and architecture-as-code modeling.
- `sverweij/dependency-cruiser`: dependency validation and visualization.
- `stoplightio/spectral` and `OpenAPITools/openapi-generator`: API contract linting and generation checks.
- `semgrep/semgrep` and `github/codeql`: static guardrail and code-query evidence for security and policy review.

## Boundaries

- This ToolAsset does not replace human architecture judgment.
- This ToolAsset does not approve verified knowledge, security policy, CI enforcement, or production dependency changes.
- Commercial, hosted, or secret-backed modes of candidate tools are outside this ToolAsset until separately approved.
