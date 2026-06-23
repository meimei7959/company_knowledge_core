---
type: Workflow
title: AI Native OS Requirement Tree Coverage Matrix
description: BR to UREQ to ProductRequirement to ANOS to task/result to test to acceptance coverage baseline.
timestamp: "2026-06-21T09:58:00Z"
projectId: company-knowledge-core
taskId: kt-ai-native-os-rt-pm-coverage-matrix
owner: agent.company.project-manager
status: active
sensitivity: internal
sourceRefs:
  - docs/agent-team/project-manager-task-decomposition-skill.md
  - docs/product/ai-native-os/requirement-tree.md
  - docs/product/ai-native-os/requirements.md
  - docs/product/ai-native-os/test-cases.md
  - docs/product/ai-native-os/acceptance-checklist.md
  - projects/company-knowledge-core/coordination/ai-native-os-requirement-tree-resplit-plan.md
---

# AI Native OS Requirement Tree Coverage Matrix

This is the PM-MATRIX baseline for `kt-ai-native-os-rt-pm-coverage-matrix`.

It prevents any Requirement Tree implementation release from treating existing ANOS implementation slices as full BR/UREQ/ProductRequirement traceability.

## Status Rules

| Status | Meaning |
| --- | --- |
| complete | Requirement row has BR, UREQ, ProductRequirement, ANOS refs, done implementation TaskResult, independent test TaskResult, mapped test cases, mapped acceptance gates, and no open external/runtime blocker. |
| partial | Requirement row has source mapping and some done evidence, but one or more of BR/UREQ/ProductRequirement backfill, launch gate evidence, live integration evidence, or full runtime proof is missing. |
| uncovered | Requirement row exists in product docs but has no matching done task/result evidence. |
| blocked | Requirement row cannot be completed until external environment, human owner, runtime proof, or prerequisite model/backfill task exists. |

## Coverage Summary

| Layer | Count | Coverage conclusion |
| --- | ---: | --- |
| BusinessRequirement | 5 | All 5 are present in `requirement-tree.md`; all remain partial because existing TaskResults mostly cite ANOS refs, not BR refs. |
| UserRequirement | 15 | All 15 are present and mapped to ProductRequirement text plus ANOS ranges; all remain partial pending Requirement Tree object/backfill tasks. |
| ProductRequirement | 15 text rows | Present as the Product Requirement column in the UREQ table; no independent ProductRequirement IDs exist yet. |
| ANOS functional requirements | 74 | All 74 are mapped into four implementation/test packages; launch readiness remains partial where external/runtime proof is missing. |
| Test cases | 84 | All ANOS refs have designed test cases in `test-cases.md`; executed evidence is package-level, not one TaskResult per TC. |
| Acceptance gates | 44 | Gates are defined in `acceptance-checklist.md`; several launch gates remain partial due Desktop Slice 0, external Agent Ring PostgreSQL contract, live Feishu/API delivery, and traceability backfill. |

## Business Requirement Coverage

| BR | Covered UREQs | Primary ANOS ranges | Current status | Gap |
| --- | --- | --- | --- | --- |
| BR-001 | UREQ-001, UREQ-004, UREQ-005, UREQ-008, UREQ-012 | Agent Hub; Project Console; Scheduler; Agent Ring; Result; Notification; Metrics | partial | Traceable production loop exists in slices, but no single BR-to-result launch proof and no Requirement Tree backfill. |
| BR-002 | UREQ-002, UREQ-003, UREQ-006, UREQ-010, UREQ-014 | Requirement Center; PRD; Decision; Review; Quality | partial | Quality gates exist, but BR/UREQ/ProductRequirement references are not yet first-class in completed TaskResults. |
| BR-003 | UREQ-005, UREQ-008, UREQ-013 | Scheduler; Agent Ring; Result; Admin; API | partial/blocked | Local runner flow is tested; live Agent Ring PostgreSQL contract remains environment-blocked. |
| BR-004 | UREQ-009, UREQ-010, UREQ-011, UREQ-015 | Knowledge Core; Review; Notification | partial | Knowledge pipeline evidence exists, but reusable knowledge launch still depends on reviewed status and traceability backfill. |
| BR-005 | UREQ-004, UREQ-005, UREQ-006, UREQ-007, UREQ-012, UREQ-013 | Agent Team; Project Console; Scheduler; Quality; Admin; Ops | partial | Role contracts exist; full desktop/workbench runtime and launch gates remain partial. |

## UREQ To ProductRequirement Matrix

| UREQ | BR | ProductRequirement | ANOS mapping | Existing done task/result evidence | Tests | Acceptance gates | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| UREQ-001 | BR-001 | Classify intent, create SourceMaterial/Requirement, ask focused questions, notify next action. | ANOS-REQ-001..006, 120..122 | `tr-kt-ai-native-os-impl-desktop-workbench-slice0.md`; `tr-kt-ai-native-os-test-desktop-workbench-slice0.md`; Feishu routing/card results | TC-HUB-001..007; TC-NOT-001..003; TC-E2E-001/002 | AC-PROD-003; AC-REQ-001/002; AC-OPS-003 | partial |
| UREQ-002 | BR-002 | Store business, user, product, functional, non-functional, test, and acceptance mapping. | ANOS-REQ-010..016, 020..024 | `tr-kt-ai-native-os-impl-requirement-prd-domain.md`; `tr-kt-ai-native-os-test-requirement-prd-domain.md` | TC-REQ-001..007; TC-PRD-001..005; TC-E2E-003 | AC-REQ-001..005; AC-TEST-001 | partial |
| UREQ-003 | BR-002 | Expose PRD versions, Decision records, evidence, and approval state. | ANOS-REQ-020..024, 090..093 | Requirement/PRD domain result; governance/review result | TC-PRD-001..005; TC-REV-001..004 | AC-REQ-003/004/005; AC-GOV-001/002 | partial |
| UREQ-004 | BR-001, BR-005 | Link requirements to ProjectTasks, Agent roles, dependencies, and launch gates. | ANOS-REQ-030..034, 050..056 | Desktop Slice 0 result; scheduler/runner/result result | TC-PROJ-001..005; TC-SCH-001..007 | AC-PROD-003; AC-EXE-001/002; AC-UI-002 | partial |
| UREQ-005 | BR-001, BR-003 | Generate taskRuntime and handoff package from approved functional requirements. | ANOS-REQ-050..056, 070..073 | Scheduler/runner/result result; automation hub result; TaskResult metadata repair | TC-SCH-001..007; TC-RES-001..004; TC-E2E-004 | AC-EXE-001..005; AC-AGENT-003 | partial |
| UREQ-006 | BR-002 | Map each functional requirement to test cases and acceptance gates. | ANOS-REQ-023, 110..114 | Requirement/PRD test result; governance/quality test result | TC-PRD-004; TC-MET-001..005; TC-E2E-001 | AC-TEST-001..005; AC-OPS-004 | partial |
| UREQ-007 | BR-005 | Expose product requirements and scenario context to design tasks. | ANOS-REQ-020..024, 040..045 | Desktop Slice 0 result; Product review accepted limited desktop scope | TC-PRD-001..005; TC-AGENT-001..007 | AC-AGENT-001..003; AC-UI-003 | partial |
| UREQ-008 | BR-003 | Provide Agent Ring Console and enforce runner authorization. | ANOS-REQ-060..063 | Scheduler/runner/result result; Agent Ring protocol/stub runner results | TC-RUN-001..004; TC-E2E-004 | AC-EXE-002/003; AC-UI-004 | blocked |
| UREQ-009 | BR-004 | Require SourceMaterial and TaskResult links for knowledge drafts. | ANOS-REQ-080..084 | Governance/quality/ops/API result; knowledge capture/review pipeline result | TC-KNO-001..005; TC-E2E-005 | AC-KNO-001..004; AC-REQ-005 | partial |
| UREQ-010 | BR-002, BR-004 | Route KnowledgeItem through Review Center before promotion. | ANOS-REQ-090..093 | Governance/quality/ops/API result; policy quality gates result | TC-REV-001..004; TC-E2E-005 | AC-GOV-001..004; AC-KNO-002 | partial |
| UREQ-011 | BR-004 | Search reviewed knowledge and expose citation/gap state. | ANOS-REQ-083, 080..084 | Knowledge governance loop result; governance/quality/ops/API result | TC-KNO-004 plus TC-KNO-001..005 | AC-KNO-003/004 | partial |
| UREQ-012 | BR-001, BR-005 | Provide Operations and Quality Dashboard metrics. | ANOS-REQ-110..114, 140..142 | Governance/quality/ops/API result | TC-MET-001..005; TC-OPS-001..003; TC-E2E-007 | AC-OPS-001/003/004; AC-UI-006 | partial |
| UREQ-013 | BR-003, BR-005 | Provide Admin and Governance Console with audit-backed write controls. | ANOS-REQ-100..102, 130..133, 150..152 | Governance/quality/ops/API result; digital worker capability registry result | TC-REG-001..003; TC-ADM-001..004; TC-API-001..004 | AC-AGENT-004/005; AC-GOV-003/004; AC-UI-007 | partial |
| UREQ-014 | BR-002, BR-004 | Route high-impact decisions to human approval. | ANOS-REQ-021, 090..093 | Requirement/PRD result; governance/review result | TC-PRD-002; TC-REV-001..004 | AC-REQ-004; AC-GOV-001/002 | partial |
| UREQ-015 | BR-004 | Provide Knowledge Query with citations, permissions, and follow-up KnowledgeTask creation. | ANOS-REQ-083, 120..122 | Knowledge governance loop result; notification loop result | TC-KNO-004; TC-NOT-001..003 | AC-KNO-003; AC-OPS-003 | partial |

## ANOS Functional Range Matrix

| Functional range | ANOS refs | UREQs | Existing done task/result evidence | Test cases | Acceptance gates | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Agent Hub | ANOS-REQ-001..006 | UREQ-001 | Desktop Slice 0 implementation/test; Feishu card/routing results | TC-HUB-001..007; TC-E2E-001/002 | AC-PROD-003; AC-REQ-001/002; AC-OPS-003 | partial |
| Requirement Center | ANOS-REQ-010..016 | UREQ-002 | Requirement/PRD domain implementation/test | TC-REQ-001..007; TC-E2E-003 | AC-REQ-001/002/005; AC-UI-001 | partial |
| PRD And Decision Center | ANOS-REQ-020..024 | UREQ-002, UREQ-003, UREQ-006, UREQ-007, UREQ-014 | Requirement/PRD domain implementation/test; product review | TC-PRD-001..005; TC-E2E-003 | AC-REQ-003/004/005 | partial |
| Project Console | ANOS-REQ-030..034 | UREQ-004 | Desktop Slice 0 implementation/test | TC-PROJ-001..005 | AC-UI-002; AC-PROD-003 | partial |
| Agent Team Manager | ANOS-REQ-040..045 | UREQ-007 | Desktop Slice 0 implementation/test; role operating specs/results | TC-AGENT-001..007 | AC-AGENT-001..003; AC-UI-003 | partial |
| Scheduler And Task Center | ANOS-REQ-050..056 | UREQ-004, UREQ-005 | Scheduler/runner/result implementation/test; automation hub result | TC-SCH-001..007; TC-E2E-004 | AC-EXE-001/002/003 | partial |
| Agent Ring Console | ANOS-REQ-060..063 | UREQ-008 | Scheduler/runner/result implementation/test; Agent Ring protocol/stub runner results | TC-RUN-001..004; TC-E2E-004 | AC-EXE-002/003; AC-UI-004 | blocked |
| Result Center | ANOS-REQ-070..073 | UREQ-005 | Scheduler/runner/result implementation/test; metadata migration repair | TC-RES-001..004; TC-E2E-004 | AC-EXE-004/005 | partial |
| Knowledge Core | ANOS-REQ-080..084 | UREQ-009, UREQ-011 | Governance/quality/ops/API implementation/test; knowledge governance loop | TC-KNO-001..005; TC-E2E-005 | AC-KNO-001..004 | partial |
| Review Center | ANOS-REQ-090..093 | UREQ-003, UREQ-010, UREQ-014 | Governance/quality/ops/API implementation/test; policy gates result | TC-REV-001..004; TC-E2E-005 | AC-GOV-001/002; AC-KNO-002 | partial |
| Tool And Skill Registry | ANOS-REQ-100..102 | UREQ-013 | Governance/quality/ops/API implementation/test; digital worker registry result | TC-REG-001..003; TC-E2E-006 | AC-AGENT-004/005; AC-GOV-003 | partial |
| Quality And Evaluation Dashboard | ANOS-REQ-110..114 | UREQ-006, UREQ-012 | Governance/quality/ops/API implementation/test | TC-MET-001..005; TC-E2E-006 | AC-TEST-001..005; AC-OPS-004; AC-UI-006 | partial |
| Notification Center | ANOS-REQ-120..122 | UREQ-001, UREQ-015 | Governance/quality/ops/API implementation/test; notification loop result | TC-NOT-001..003; TC-E2E-007 | AC-OPS-003; AC-PROD-003 | partial |
| Admin And Governance Console | ANOS-REQ-130..133 | UREQ-013 | Governance/quality/ops/API implementation/test | TC-ADM-001..004 | AC-GOV-003/004; AC-UI-007 | partial |
| Operations And Feedback Center | ANOS-REQ-140..142 | UREQ-012 | Governance/quality/ops/API implementation/test | TC-OPS-001..003; TC-E2E-007 | AC-OPS-001/003/004 | partial |
| API And Integration Gateway | ANOS-REQ-150..152 | UREQ-013 | Governance/quality/ops/API implementation/test | TC-API-001..004 | AC-GOV-004; AC-OPS-001; AC-PROD-003 | partial |

## Existing Evidence Packages

| Package | Covers | Status note |
| --- | --- | --- |
| `tr-kt-ai-native-os-impl-requirement-prd-domain.md` and `tr-kt-ai-native-os-test-requirement-prd-domain.md` | ANOS-REQ-010..016, 020..024 | Implementation/test done, but Requirement Tree object/backfill not yet complete. |
| `tr-kt-ai-native-os-impl-desktop-workbench-slice0.md` and `tr-kt-ai-native-os-test-desktop-workbench-slice0.md` | ANOS-REQ-001..006, 030..034, 040..045 | Desktop Slice 0 is partial only. Full desktop runtime is not proven. |
| `tr-kt-ai-native-os-impl-scheduler-runner-result.md` and `tr-kt-ai-native-os-test-scheduler-runner-result.md` | ANOS-REQ-050..056, 060..063, 070..073 | Core tests pass; live Agent Ring PostgreSQL contract remains environment-blocked. |
| `tr-kt-ai-native-os-impl-governance-quality-ops-api.md` and `tr-kt-ai-native-os-test-governance-quality-ops-api.md` | ANOS-REQ-080..084, 090..093, 100..102, 110..114, 120..122, 130..133, 140..142, 150..152 | Unit/regression evidence exists; live external Feishu/API delivery remains explicit integration risk. |
| `tr-kt-ai-native-os-product-review-technical-solutions.md` | 74 ANOS technical solution coverage | Product accepted three packages; Desktop required Slice 0 before full implementation. |
| `tr-kt-agent-ring-protocol.md` and `tr-kt-agent-ring-stub-runner-tests.md` | Runner register, heartbeat, claim, context pull, finish writeback | Supports BR-003 evidence, but does not replace live external contract proof. |
| `tr-kt-os-knowledge-governance-loop.md`, `tr-task-knowledge-capture-review-pipeline.md`, `tr-task-universal-material-ingest.md` | Knowledge capture, review, query, material intake | Supports BR-004 evidence, but reviewed/verified promotion is still gate-controlled. |
| `tr-task-production-closed-loop-acceptance.md`, `tr-task-project-initialization-closeout.md` | Earlier central processor closed loop | Useful supporting evidence, but older results do not provide full BR/UREQ/ProductRequirement backfill. |

## Required Follow-Up Before Complete Status

| Gap | Required owner | Blocking rows |
| --- | --- | --- |
| First-class Requirement Tree model for BR, UREQ, ProductRequirement, mapping, test, and acceptance refs. | Development Agent after accepted technical solution | All BR/UREQ rows |
| Import and validation of `requirement-tree.md` proving 5 BR, 15 UREQ, 74 ANOS mappings, 84 tests, and 44 acceptance gates. | Development Agent + Test Agent | All BR/UREQ rows |
| Backfill existing TaskResults with BR/UREQ/ProductRequirement/test/acceptance refs without promoting partial work. | Development Agent + Test Agent | All rows with existing ANOS-only evidence |
| Desktop full runtime proof: macOS/Windows packaging, signing, updater, enterprise proxy/CA, secure local storage, deep link, runner pairing. | Development Agent + Test Agent + PM/Product acceptance | UREQ-001, UREQ-004, UREQ-007; Agent Hub, Project Console, Agent Team Manager |
| Live Agent Ring PostgreSQL contract check. | Development Agent/Test Agent with environment setup | UREQ-008; Agent Ring Console; Scheduler/Result launch gates |
| Live external Feishu/API delivery verification. | Development Agent/Test Agent/Ops as applicable | UREQ-001, UREQ-013, UREQ-015; API, Notification, Ops gates |

## PM Conclusion

The requirement corpus is enumerable and internally mapped: 5 BR, 15 UREQ, 15 ProductRequirement text rows, 74 ANOS functional requirements, 84 designed tests, and 44 launch acceptance gates.

Existing work gives strong ANOS-level implementation/test evidence, but it is not a complete Requirement Tree traceability system. The current baseline is therefore partial overall.

Desktop Slice 0 remains partial. It must not be interpreted as completed desktop client delivery.
