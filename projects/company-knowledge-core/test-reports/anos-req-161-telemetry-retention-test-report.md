---
type: EvalRun
title: ANOS-REQ-161 telemetry retention test report
description: Test validation report for execution telemetry retention, cleanup, protected refs, audit summary, learning signals, and metrics rollup.
timestamp: "2026-06-23T12:17:42Z"
reportId: test-report.anos-req-161-telemetry-retention
projectId: company-knowledge-core
requirementRefs:
  - ANOS-REQ-161
  - ANOS-REQ-160
taskRef: projects/company-knowledge-core/tasks/kt-anos-req-161-telemetry-retention-test.md
receiverReviewRef: projects/company-knowledge-core/receiver-reviews/receiver-review.anos-req-161.test.md
developmentResultRef: task-results/tr-kt-anos-req-161-telemetry-retention-development.md
status: done
verdict: pass
testedBy: agent.company.test
evidenceRefs:
  - docs/product/ai-native-os/execution-telemetry-retention-acceptance-matrix.md
  - docs/product/ai-native-os/execution-telemetry-retention-prd.md
  - projects/company-knowledge-core/technical-solutions/anos-req-161-telemetry-retention-technical-solution.md
  - task-results/tr-kt-anos-req-161-telemetry-retention-development.md
  - zhenzhi_knowledge/telemetry_retention.py
  - tests/test_telemetry_retention.py
---

## Conclusion

Pass. ANOS-REQ-161 telemetry retention V0 satisfies the tested acceptance path for classification, current-state upsert, task timeline closeout compaction, dry-run/apply cleanup, protected references, batch AuditLog summary, learning signal promotion, and metrics rollup.

No failed item needs Development回派.

## Command Results

- `python3 -m unittest tests.test_telemetry_retention`: pass, 6 tests, `OK`, exit 0.
- Supplemental acceptance probe: pass, 26 checks, dry-run counts `eventsScanned=8`, `deleteCandidates=2`, `protectedSkips=3`, `learningCandidates=1`, `compactTasks=1`; apply counts matched dry-run and wrote one batch audit summary.
- `python3 -m zhenzhi_knowledge.cli status`: pass, `valid: yes`, exit 0.

## Acceptance Coverage

| Item | Result | Evidence |
| --- | --- | --- |
| ANOS-REQ-161-001 classification | pass | Unit tests and supplemental probe verified heartbeat, progress_update, tool_usage, model_usage, result_writeback, and learning error classification/routes. |
| ANOS-REQ-161-002 current-state upsert | pass | Unit tests and supplemental probe verified repeated heartbeat keeps one logical current-state row and latest step wins. |
| ANOS-REQ-161-003 timeline closeout compaction | pass | Unit tests and supplemental probe verified terminal task timeline is selected for compaction and writes a task summary. |
| ANOS-REQ-161-004 dry-run | pass | Dry-run returned delete, compact, rollup, promote/learning candidate, and protected skip counts/reasons without mutating source events. |
| ANOS-REQ-161-005 apply | pass | Apply deleted expired unprotected ephemeral/hot raw events, wrote summary/metrics/promotions, and returned deleted refs. |
| ANOS-REQ-161-006 protected refs | pass | Apply preserved protected result refs, cited evidence refs, learning signals, and refs cited by TaskResult/Audit/verified knowledge/open blocker fixtures. |
| ANOS-REQ-161-007 batch AuditLog | pass | Apply wrote exactly one new AuditLog with `policyResult: batch_summary`; no per-row audit noise was created. |
| ANOS-REQ-161-008 learning signal and metrics rollup | pass | Learning signal was retained and promoted to `AgentImprovementProposal` plus `EvalCase`; metrics rollup was written under `knowledge/metrics/`. |

## Protected Ref Checks

Pass for tested protected classes:

- TaskResult/evidence refs.
- AuditLog/human acceptance refs.
- verified KnowledgeItem evidence refs.
- open blocker evidence refs.
- protected_result_ref events.
- promoted AgentImprovementProposal and EvalCase outputs.

Active lease/task progress protection is represented by the protected/core-result class and cited-ref skip mechanism in this V0 fixture set; no failure found.

## Dry-Run And Apply Report Shape

Dry-run/apply reports expose equivalent actionable counts:

- `deleteCandidates`
- `protectedSkips`
- `learningCandidates`
- `compactTasks`
- `rollup.willWriteMetricsReport`
- `deletedRefs`, `summaryRefs`, `rollupRef`, `promotionRefs`, `auditRef` in apply mode

The V0 report does not use literal top-level `archive` or `error` counters. No archive action is implemented in the repository-local V0; errors are not present for the passing fixture path. This is equivalent to the acceptance requirement for actionable delete/compact/rollup/promote/skip reporting.

## Residual Risk

- Coverage is repository-local/file-backed V0, matching the accepted technical solution. Production scheduling cadence and external API/database integration remain future work.
- Protected-ref scanning is conservative text/ref based, as noted by Development; current tests validate required V0 behavior.
