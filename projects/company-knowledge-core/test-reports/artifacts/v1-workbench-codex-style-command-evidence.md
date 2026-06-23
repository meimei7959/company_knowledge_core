---
type: Workflow
title: V1 Workbench Codex Style Test Command Evidence
timestamp: "2026-06-22T05:35:54Z"
taskId: kt-v1-workbench-codex-style-test
executorAgent: agent.company.test
---

# V1 Workbench Codex Style Test Command Evidence

## Required Commands

| Command | Result | Evidence |
|---|---:|---|
| `node --check projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js` | pass | `EXIT=0` |
| `python3 scripts/validate_desktop_workbench_slice0.py /Users/meimei/Documents/company_knowledge_core` | pass | `desktop workbench slice0 artifacts: passed`, `EXIT=0` |
| `python3 -m unittest tests.test_desktop_workbench_slice0` | pass | `Ran 8 tests in 0.014s`, `OK`, `EXIT=0` |
| `python3 -m zhenzhi_knowledge --root /Users/meimei/Documents/company_knowledge_core validate` | pass | `valid`, `EXIT=0` |
| `git diff --check -- projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.html projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.css projects/company-knowledge-core/desktop-workbench-slice0/workbench-read-model.js projects/company-knowledge-core/desktop-workbench-slice0/workbench-live-read-model.js` | pass | `EXIT=0` |

## Independent Read Model Checks

| Check | Result | Evidence |
|---|---:|---|
| live read model source | pass | `runtimeReadModelKind=real-v1-runtime-read-model`, `fixture=false`, `sourceOfTruth=central-api-read-model`, `staleStatePolicy=show-safe-fallback-not-current` |
| script load order | pass | `workbench-read-model.js` -> `workbench-live-read-model.js` -> `workbench-shell.js` |
| V1 local device route | pass | only `device.local`; rendered route text includes `targetDeviceId=device.local` |
| task/runner/read model breadth | pass | 11 surfaces, 4 home cards, 4 agent sessions, 28 task flow rows, 14 task results, 15 runner leases, 3 acceptance evidence cards |
| submitted label | pass | rendered as `已提交，待评审`; explanatory text says `不等于已验收` |
| evidence completeness prompt | pass | result center renders missing field prompts for `outputRefs`, `evidenceRefs`, `testsOrChecks`, `operatingRuleRefs`, `commonRulesEvaluation` |
| status Chinese mapping | fail | Runner history renders raw English `retried` and `escalated` |

## Browser / File Render Attempt

| Attempt | Result | Notes |
|---|---:|---|
| Playwright import | pass | Node can import `playwright` |
| Playwright bundled Chromium | skipped | browser executable missing at Playwright cache path; launch failed before page load |
| Playwright with system Chrome | failed | system Chrome launched then aborted under automation (`SIGABRT`) |
| Chrome headless CLI screenshot | failed | command timed out after 30s, no screenshot produced |
| DOM-level execution fallback | pass | executed `workbench-live-read-model.js` and `workbench-shell.js` in VM with DOM stub; rendered all primary surfaces to HTML strings for content inspection |

## Defect Evidence

Implementation location:

- `projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js:56` defines `statusText`.
- `projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js:73` maps `submitted` to `已提交，待评审`.
- `projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js:75` ends map without `retried` / `escalated`.
- `projects/company-knowledge-core/desktop-workbench-slice0/workbench-live-read-model.js:10262` uses `status: "retried"`.
- `projects/company-knowledge-core/desktop-workbench-slice0/workbench-live-read-model.js:10267` uses `status: "escalated"`.

Rendered Runner page text evidence:

```txt
Package retry retried Runner history Require idempotency
Permission escalation escalated Runner history Show approval owner
```
