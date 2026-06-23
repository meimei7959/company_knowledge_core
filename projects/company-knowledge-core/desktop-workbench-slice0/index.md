---
type: Workflow
title: AI Native OS Desktop Workbench Slice 0 Local Shell
description: Shell-independent proof artifacts plus a runnable local desktop workbench path for cross-platform desktop client validation.
timestamp: "2026-06-21T07:08:00Z"
projectId: company-knowledge-core
taskId: kt-ai-native-os-impl-desktop-workbench-slice0
status: draft
requirementRefs:
  - ANOS-REQ-001
  - ANOS-REQ-002
  - ANOS-REQ-003
  - ANOS-REQ-004
  - ANOS-REQ-005
  - ANOS-REQ-006
  - ANOS-REQ-030
  - ANOS-REQ-031
  - ANOS-REQ-032
  - ANOS-REQ-033
  - ANOS-REQ-034
  - ANOS-REQ-040
  - ANOS-REQ-041
  - ANOS-REQ-042
  - ANOS-REQ-043
  - ANOS-REQ-044
  - ANOS-REQ-045
sourceMaterialRefs:
  - projects/company-knowledge-core/technical-solutions/ai-native-os-desktop-workbench-console.md
  - projects/company-knowledge-core/product-reviews/ai-native-os-desktop-workbench-revision-review.md
---

# AI Native OS Desktop Workbench Slice 0 Local Shell

## Minimal Landing Point

The repository has no existing Node, Vite, React, Electron, Tauri, Rust, signing, updater, or OS package scaffold. The smallest viable implementation landing point is therefore a shell-independent local workbench under this project directory, plus a Python validator that can run inside the existing repository test stack.

This creates a runnable `file://` desktop workbench path without pretending signed Mac or Windows packaging exists.

## Artifacts

- `shared-frontend-foundation.ts`: shell-neutral TypeScript boundary for future React/Vite UI code. It contains no Tauri or Electron imports and requires shell features through dependency injection.
- `native-bridge-manifest.json`: explicit native bridge command boundary, permission shape, central-governance constraints, and forbidden local mutations.
- `slice0-proof-checklist.json`: executable proof checklist for packaging, signing/notarization, update channels, enterprise network/proxy, secure storage, native bridge, deep links, notification permission, environment/release ownership, and local Runner pairing.
- `workbench-shell.html`: local static workbench shell that can be opened from disk without a package manager or native runtime.
- `workbench-shell.css`: responsive desktop workbench layout with readable status labels and fallback states.
- `workbench-shell.js`: renderer for navigation, core state panels, permission-gated actions, and safe fallback handling.
- `workbench-read-model.js`: central API-shaped read model fixture covering project progress, Agent current work, runner lease/history, approvals, notifications, recovery, settings, and security warnings.
- `scripts/validate_desktop_workbench_slice0.py`: repository-local validator for the artifacts.
- `tests/test_desktop_workbench_slice0.py`: unittest coverage for the validator.

## Slice 0 Position

This slice implements the broad desktop shell states as a local static workbench, not only a document. It does not claim production native bridge UX or real packaging. The next packaging boundary is explicit:

- choose Tauri v2 or Electron owner;
- add signed Mac and Windows package projects;
- wire live central API transport and OS secure storage plugins;
- run install, update, deep link, notification, enterprise proxy, and runner pairing smoke tests on both platforms.

## Current Proof Status

Static proof passes when `python3 scripts/validate_desktop_workbench_slice0.py` succeeds.

The local shell covers project progress, Agent current work, runner registry/lease/history, approval callback, notifications, failure recovery, and settings/security prompts with readable labels before raw ids.

Real macOS signing/notarization, Windows installer signing, updater manifest signing, enterprise proxy/custom CA checks, secure storage plugin proof, and cross-platform install/uninstall smoke tests remain blocked until the Project Manager Agent confirms target environments, accounts, certificates, distribution owner, and Windows runner availability.

## Local Run

Open `projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.html` in a browser or desktop wrapper. No build step is required for this repository-local slice.
