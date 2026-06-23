---
type: AuditLog
title: AI Native OS requirement tree re-split plan
description: Project Manager Agent re-split of Requirement Tree work after reviewing the initial task decomposition quality.
timestamp: "2026-06-21T09:08:00Z"
auditId: audit.20260621T090800-ai-native-os-requirement-tree-resplit-plan
actor: agent.company.project-manager
action: pm.task_decomposition.resplit
target: docs/product/ai-native-os/requirement-tree.md
status: observed
sensitivity: internal
sourceRefs:
  - docs/agent-team/project-manager-task-decomposition-skill.md
  - docs/product/ai-native-os/requirement-tree.md
  - projects/company-knowledge-core/coordination/ai-native-os-requirement-tree-delta-task-list.md
---

# PM Re-Split Conclusion

The previous Requirement Tree task split was directionally correct but operationally unsafe. It placed too much model, validation, import, compiler, context, workbench, and migration work into one Development Agent task.

This plan replaces the initial broad tasks with a task ladder:

1. PM coverage matrix.
2. Development technical solution.
3. Product Manager review.
4. Small development/test slices.
5. Historical backfill.
6. Persona clarification.

# Reasonable Task Queue

## RT-PM-001 Coverage Matrix

Owner: Project Manager Agent  
Purpose: produce the exact BR -> UREQ -> ProductRequirement -> ANOS -> existing task/result -> test -> acceptance matrix.

Exit:

- Matrix has 5 BR and 15 UREQ.
- Every ANOS range maps to at least one UREQ.
- Existing completed work is classified as complete, partial, or uncovered.
- Desktop Slice 0 remains partial where full runtime is not proven.

## RT-TECH-001 Requirement Tree Technical Solution

Owner: Development Agent  
Purpose: propose architecture before implementation.

Exit:

- Defines object model, import strategy, validation strategy, migration/backfill approach, tests, and rollback.
- Explicitly states what will not be implemented in the first slice.

## RT-PROD-REVIEW-001 Technical Solution Product Review

Owner: Product Manager Agent  
Purpose: confirm engineering model preserves product semantics.

Exit:

- Product accepts or requests changes.
- No implementation task is released until accepted.

## RT-DEV-001 Object Model Slice

Owner: Development Agent  
Purpose: implement BR, UREQ, scenario, product requirement, mapping, and tree snapshot records.

Exit:

- Object model exists.
- New records validate.
- No importer/compiler/workbench work hidden in this slice.

## RT-TEST-001 Object Model Slice

Owner: Test Agent  
Purpose: independently verify RT-DEV-001.

Exit:

- Positive object model tests pass.
- Orphan/invalid record tests fail correctly.

## RT-DEV-002 Import And Validation Slice

Owner: Development Agent  
Purpose: import and validate `requirement-tree.md`.

Exit:

- Import proves 5 BR, 15 UREQ, 74 ANOS mappings.
- Validator reports orphan, missing test, missing acceptance, and missing owner cases.

## RT-TEST-002 Import And Validation Slice

Owner: Test Agent  
Purpose: verify importer and validator.

Exit:

- Valid tree passes.
- Broken tree fixtures fail with readable diagnostics.

## RT-DEV-003 Product Package To Task Queue Compiler

Owner: Development Agent  
Purpose: compile full requirement tree into role-specific ProjectTasks.

Exit:

- Tasks include BR/UREQ/ProductRequirement/ANOS/test/acceptance refs.
- Missing owner/evidence/test/gate creates blocker instead of executable task.

## RT-TEST-003 Compiler Slice

Owner: Test Agent  
Purpose: verify task compiler behavior.

Exit:

- Development/Test/Design/Ops/Review tasks are generated with correct role context.
- Incomplete tree blocks compilation.

## RT-DEV-004 Agent Context Pack Traceability

Owner: Development Agent  
Purpose: inject BR/UREQ/scenario/product requirement/test/acceptance context into Agent task packs.

Exit:

- Development Agent sees why and what to build.
- Test Agent sees observable criteria.
- Design Agent sees scenario and constraints.

## RT-TEST-004 Context Pack Slice

Owner: Test Agent  
Purpose: verify context packs by role.

Exit:

- Context includes traceability without leaking unrelated personas or raw dumps.

## RT-DEV-005 Requirement Tree Workbench View

Owner: Development Agent  
Purpose: expose requirement tree traceability in workbench data model.

Exit:

- Workbench can answer which BR/UREQ each task serves.
- Unmapped/untested/blocked items are visible.

## RT-TEST-005 Workbench Slice

Owner: Test Agent  
Purpose: verify workbench traceability and risk display.

Exit:

- Workbench read model shows BR -> UREQ -> ANOS -> Task -> Result -> Test -> Acceptance.

## RT-DEV-006 Existing 74 Work Item Backfill

Owner: Development Agent  
Purpose: backfill existing TaskResults and completed tasks with BR/UREQ refs after model/importer exists.

Exit:

- Completed work maps to UREQ/BR or is marked partial/uncovered.
- No previously partial work is silently promoted to complete.

## RT-TEST-006 Backfill Verification

Owner: Test Agent  
Purpose: verify backfill accuracy and launch readiness.

Exit:

- 74 functional requirements still have zero functional leakage.
- UREQ coverage matrix is complete or explicitly blocked.

# Release Rule

Only RT-PM-001 and RT-TECH-001 may start immediately. Every later task remains blocked until its predecessor TaskResult is accepted.
