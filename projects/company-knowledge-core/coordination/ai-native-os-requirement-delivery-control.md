---
type: Workflow
title: AI Native OS Requirement Delivery Control
description: Project Manager Agent control baseline for delivering all AI Native OS requirements through development, test, and launch acceptance.
timestamp: "2026-06-21T05:39:54Z"
controlId: control.ai-native-os.requirement-delivery
projectId: company-knowledge-core
ownerAgent: agent.company.project-manager
runnerRef: runners/runner.meimei-mac-local-codex.md
sourceMaterialRefs:
  - docs/product/ai-native-os/requirements.md
  - docs/product/ai-native-os/test-cases.md
  - docs/product/ai-native-os/acceptance-checklist.md
  - projects/company-knowledge-core/coordination/ai-native-os-execution-plan.md
status: active
---
# AI Native OS Requirement Delivery Control

## Baseline

| Metric | Count | Control Meaning |
| --- | ---: | --- |
| Requirements | 74 | Every ANOS-REQ must have development evidence, test evidence, and launch acceptance evidence before release. |
| Requirement leakage | 0 | No requirement may be dropped, hidden, or left without an owner. |
| Test cases | 77 | Test Agent must preserve requirement-to-test traceability. |
| Launch acceptance gates | 44 | Project Manager Agent blocks launch when any required gate lacks evidence. |

## Closure Rule

Project initialization and execution are closed only when every requirement has:

- a development task owner;
- an accepted technical solution when the requirement touches product architecture, workflow, data model, scheduler, runner, governance, API, or console behavior;
- a test task owner;
- a TaskResult from the development owner with implemented `requirementRefs`;
- a TaskResult from the test owner with tested `requirementRefs`, result evidence, and blockers;
- launch acceptance evidence or an explicit launch blocker;
- Project Manager Agent status that reconciles requirement, test, risk, and approval state.

## Development Rhythm

The four development tasks are not direct-code tickets. They are controlled slices with a required technical solution stage:

1. Development Agent writes the technical solution for its assigned `requirementRefs`.
2. Project Manager Agent reviews sequence, dependency, risk, evidence, and launch-gate impact.
3. Test Agent reviews whether the solution can prove requirement coverage.
4. Project Manager Agent only then releases implementation work.
5. Development Agent implements and writes TaskResult evidence.
6. Test Agent executes requirement-mapped tests.
7. Project Manager Agent reconciles against the 74-requirement baseline and creates follow-up work if needed.

## Delivery Matrix

| Module | Requirement Refs | Development Task | Test Task | Launch Control |
| --- | --- | --- | --- | --- |
| Agent Hub | ANOS-REQ-001..006 | kt-ai-native-os-dev-console-surfaces | kt-ai-native-os-test-acceptance-suite | Product, console, and execution acceptance. |
| Requirement Center | ANOS-REQ-010..016 | kt-ai-native-os-dev-requirement-prd-domain | kt-ai-native-os-test-acceptance-suite | Requirement acceptance. |
| PRD And Decision Center | ANOS-REQ-020..024 | kt-ai-native-os-dev-requirement-prd-domain | kt-ai-native-os-test-acceptance-suite | Product and decision traceability acceptance. |
| Project Console | ANOS-REQ-030..034 | kt-ai-native-os-dev-console-surfaces | kt-ai-native-os-test-acceptance-suite | Console acceptance. |
| Agent Team Manager | ANOS-REQ-040..045 | kt-ai-native-os-dev-console-surfaces | kt-ai-native-os-test-acceptance-suite | Agent team acceptance. |
| Scheduler And Task Center | ANOS-REQ-050..056 | kt-ai-native-os-dev-scheduler-runner-result | kt-ai-native-os-test-acceptance-suite | Execution acceptance. |
| Agent Ring Console | ANOS-REQ-060..063 | kt-ai-native-os-dev-scheduler-runner-result | kt-ai-native-os-test-acceptance-suite | Agent Ring acceptance. |
| Result Center | ANOS-REQ-070..073 | kt-ai-native-os-dev-scheduler-runner-result | kt-ai-native-os-test-acceptance-suite | Result evidence acceptance. |
| Knowledge Core | ANOS-REQ-080..084 | kt-ai-native-os-dev-governance-quality-ops | kt-ai-native-os-test-acceptance-suite | Knowledge acceptance. |
| Review Center | ANOS-REQ-090..093 | kt-ai-native-os-dev-governance-quality-ops | kt-ai-native-os-test-acceptance-suite | Review and governance acceptance. |
| Tool And Skill Registry | ANOS-REQ-100..102 | kt-ai-native-os-dev-governance-quality-ops | kt-ai-native-os-test-acceptance-suite | Tool approval acceptance. |
| Quality And Evaluation Dashboard | ANOS-REQ-110..114 | kt-ai-native-os-dev-governance-quality-ops | kt-ai-native-os-test-acceptance-suite | Quality and EvalRun acceptance. |
| Notification Center | ANOS-REQ-120..122 | kt-ai-native-os-dev-governance-quality-ops | kt-ai-native-os-test-acceptance-suite | Notification acceptance. |
| Admin And Governance Console | ANOS-REQ-130..133 | kt-ai-native-os-dev-governance-quality-ops | kt-ai-native-os-test-acceptance-suite | Admin and permission acceptance. |
| Operations And Feedback Center | ANOS-REQ-140..142 | kt-ai-native-os-dev-governance-quality-ops | kt-ai-native-os-test-acceptance-suite | Operations readiness acceptance. |
| API And Integration Gateway | ANOS-REQ-150..152 | kt-ai-native-os-dev-governance-quality-ops | kt-ai-native-os-test-acceptance-suite | API and integration acceptance. |

## Agent Team Execution

| Role | Agent | Required Responsibility |
| --- | --- | --- |
| Project Manager | agent.company.project-manager | Own the delivery matrix, run scheduler ticks, reconcile TaskResult evidence, expose risks, and block release when evidence is missing. |
| Development | agent.company.development | Implement assigned `requirementRefs`, write code/evidence outputs, and return TaskResult with coverage. |
| Test | agent.company.test | Convert 77 test cases into executable or manually verifiable checks and report requirement leakage as zero or blocked. |
| Design | agent.company.design | Validate console experience for role-specific operational workflows. |
| Knowledge Ops | agent.core.knowledge-ops | Map knowledge, source material, audit, review, and graph impact requirements. |
| Knowledge Review | agent.core.knowledge-review | Verify review routes and human approval stop rules. |
| Operations | agent.company.operations | Verify deployment, monitoring, notification, backup, and rollback readiness. |

## Monitoring Loop

Project Manager Agent must run this loop after every TaskResult and at least once per project work session:

1. Run scheduler tick for `company-knowledge-core`.
2. Check each task state: `pending`, `waiting_runner`, `processing`, `blocked`, `waiting_acceptance`, `done`.
3. Reconcile delivered `requirementRefs` against the 74-requirement baseline.
4. Reconcile tested `requirementRefs` against the 77-test-case baseline.
5. Check launch gates against the 44 acceptance items.
6. Create or repair tasks for missing runner, stale lease, failed tests, missing evidence, open dependency, unapproved scope change, or launch blocker.
7. Notify owner and requester when work is blocked, stale, or ready for acceptance.

## Current Execution State

- Execution computer: `runner.meimei-mac-local-codex`.
- Current project queue state: waiting tasks have been assigned to this runner.
- Current control gap closed here: the 74 requirements are now explicitly distributed to development and test tasks.
- Next operating step: claim one high-priority task at a time, execute it, write TaskResult evidence, then run scheduler tick and PM status again.

## Release Blockers

Project Manager Agent must not mark AI Native OS launch-ready when any of these is true:

- a requirement lacks development evidence;
- a requirement lacks test evidence;
- a test case cannot map to a requirement or acceptance gate;
- an acceptance gate lacks pass/fail evidence;
- a TaskResult is missing outputRefs, evidenceRefs, blockers, or nextActions;
- required human approval is absent;
- scheduler or runner state hides stalled work.
