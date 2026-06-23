---
type: Workflow
title: AI Native OS Cross-Platform Desktop Client Design Solution
description: UX, information architecture, state model, handoff, and acceptance criteria for the complete Mac/Windows desktop client.
timestamp: "2026-06-21T12:55:00Z"
projectId: company-knowledge-core
taskId: kt-ai-native-os-gap-design-desktop-client
authorAgent: agent.company.design
runnerId: runner.meimei-mac-local-design-rt
status: draft
sensitivity: internal
requirementRefs:
  - AI-NATIVE-OS-PROD-GAP-001
  - AI-NATIVE-OS-PROD-GAP-002
  - UREQ-007
  - UREQ-008
  - UREQ-013
  - UREQ-014
  - ANOS-REQ-060
  - ANOS-REQ-061
  - ANOS-REQ-062
  - ANOS-REQ-063
sourceRefs:
  - .zhenzhi/context/task.kt-ai-native-os-gap-design-desktop-client.md
  - projects/company-knowledge-core/tasks/kt-ai-native-os-gap-design-desktop-client.md
  - projects/company-knowledge-core/product-reviews/ai-native-os-requirement-tree-final-product-acceptance.md
  - projects/company-knowledge-core/coordination/ai-native-os-full-product-gap-execution-plan.md
  - docs/product/ai-native-os/requirement-tree.md
reviewPath:
  - Product Manager Agent product review
  - Project Manager Agent delivery acceptance
  - Development Agent feasibility review
  - Test Agent launch acceptance matrix
---

# AI Native OS Desktop Client Design Solution

## Decision

Design recommends a complete Mac/Windows desktop client with one operational console, not separate pages for each subsystem. The desktop app should make central state visible, guide local runner pairing, route approvals and permissions back to the main window, and make failure recovery explicit enough for non-technical users and Runner Admins.

Development remains blocked until Product Manager Agent and Project Manager Agent accept this design solution.

## Problem Framing

The final product acceptance rejected the current state as full product implementation because Desktop Slice 0 and the workbench read model do not prove a full desktop client. Missing product evidence includes complete IA, packaged desktop runtime, secure storage, deep link handling, runner pairing, enterprise network states, offline/recovery states, and Agent Ring Console productization.

This design closes the UX/IA part of that gap. It does not implement production code.

## Target Users

| User | Primary need | Desktop support |
| --- | --- | --- |
| Project Owner | Know whether work is moving, blocked, or awaiting review. | Console home, project progress, acceptance state, readable blockers. |
| Project Manager Agent / human operator | Coordinate task queue, handoffs, runner health, and review gates. | Project progress, Agent current work, runner lease/history, acceptance gate view. |
| Agent Ring Runner Admin | Keep distributed computers authorized, scoped, live, and recoverable. | Runner registry, pairing, lease, heartbeat, stale lease, cancellation, retry, history. |
| Human Reviewer | Approve high-impact decisions without losing task context. | Approval modal, callback recovery, evidence preview, return to main window. |
| System Admin | Understand permission and storage risk before enabling local capabilities. | Secure storage prompts, permission dialogs, audit-ready copy, settings. |

## Product Principles

- Central API is source of truth. Desktop may cache display metadata, but must show when data is stale.
- Human labels come first. Raw IDs appear only in secondary detail drawers.
- Every status must expose next action, owner, and evidence or reason.
- Local runner state must never look authoritative when central heartbeat or lease is stale.
- Approval and permission flows must always return to the main window with a visible result.
- Secure storage prompts must explain what is stored, where, why, and how to revoke.
- Mac and Windows must use native platform conventions without changing information architecture.

## Information Architecture

Primary navigation uses a persistent left rail:

1. `Home`
2. `Current Work`
3. `Projects`
4. `Runners`
5. `Approvals`
6. `Knowledge & Evidence`
7. `Activity`
8. `Settings`

Global top bar:

- Environment selector: production, staging, local dev when allowed.
- Sync status: online, reconnecting, offline, stale, degraded.
- Active project switcher.
- Search command: task, project, runner, approval, source, knowledge.
- Notification center.
- User and organization menu.

Global bottom status strip:

- Runner connection summary.
- Last successful sync time.
- Pending write count.
- Active deep link or callback state when present.
- Product acceptance status for current release scope.

## Console Home

Purpose: answer "What needs attention now?"

Required panels:

- `Work Health`: counts for active tasks, blocked tasks, waiting acceptance, failed runner jobs, stale leases.
- `My Next Actions`: approvals, permission grants, human decisions, retry prompts, reviewer assignments.
- `Active Agent Work`: current Agent tasks grouped by role with status, owner, next checkpoint, and evidence freshness.
- `Runner Health`: registered, online, degraded, stale, disabled, unauthorized.
- `Project Progress`: current release readiness, gap status, acceptance gate status.
- `Incident & Recovery`: latest failed sync, callback failure, stale lease, offline mode, permission denial.

Home empty state:

- No active project: show project connection and recent projects.
- No assigned work: show healthy state plus recent completed tasks.
- No runner paired: show runner pairing call to action only to authorized users.

Home must not expose raw internal IDs as primary labels. ID details live in expandable metadata.

## Agent Current Work

Purpose: make current Agent execution readable and auditable.

View structure:

- Left list: task cards filtered by Agent role, priority, status, acceptance gate, runner.
- Main detail: task objective, context pack status, source refs, current step, evidence refs, tests/checks, open risks.
- Timeline: created, claimed, context prepared, started, heartbeat, result written, quality gate, acceptance, notification.
- Action area: pause/resume view-only state, request review, create follow-up, copy evidence package. Mutating actions require server authorization.

Task card fields:

- Human title.
- Role and executor Agent.
- Route status: pending, waiting runner, processing, waiting acceptance, changes requested, blocked, done, rejected.
- Result status when present: submitted, done, blocked, rejected.
- Quality decision: handoff ready, review required, retry required, repair required, auto accepted.
- Lease/runner badge when assigned.
- Acceptance badge: not needed, waiting PM, waiting human, accepted, rejected.

Agent work error states:

- Missing context pack: block action, show required source list.
- Rule evaluation failed: show failing rule and repair owner.
- Result lacks evidence: show evidence requirement before acceptance.
- Task completed but not accepted: show acceptance owner and review route.

## Project Progress

Purpose: show release readiness, not just task completion.

Progress model:

- Requirement coverage: total, complete, partial, blocked.
- Product gaps: AI-NATIVE-OS-PROD-GAP-001 to 006 with owner, current stage, evidence status.
- Acceptance gates: product, PM, design, development, test, operations, human.
- Launch evidence: task result refs, test refs, review refs, live integration refs.

Project progress view:

- `Release Readiness Bar`: design accepted, implementation ready, live verification ready, launch accepted.
- `Gap Board`: columns planned, in design, in technical solution, in implementation, in test, waiting acceptance, blocked, done.
- `Requirement Trace`: UREQ and ANOS refs with current evidence and reason when partial/blocked.
- `Decision Log`: major product and PM decisions with reviewer and date.

Required desktop client gap status copy:

- "Desktop implementation blocked until Product Manager Agent and Project Manager Agent accept this design solution."
- After review acceptance: "Desktop implementation may enter Development Agent technical execution."

## Runner, Lease, And History

Purpose: productize Agent Ring Console for Runner Admin and PM visibility.

Runners IA:

- `Registry`: all runners, owner, computer label, OS, capabilities, scopes, last seen, approval state.
- `Pairing`: pair new runner, re-pair existing runner, revoke pairing, rotate local credential reference.
- `Lease Monitor`: active leases, task, project, executor, lease owner, expiry, heartbeat, retry/cancel eligibility.
- `History`: claims, heartbeats, stale lease recovery, cancellations, retries, finishes, failures, audit refs.
- `Scope & Audit`: allowed projects, allowed tools, data scopes, denied attempts, admin changes.

Runner states:

| State | Visual treatment | Required next action |
| --- | --- | --- |
| Not paired | Neutral setup state | Pair runner or dismiss if user lacks permission. |
| Pending approval | Waiting badge | Show approver and expected route. |
| Online | Healthy badge | Show heartbeat and active leases. |
| Busy | Active badge | Show current task and lease expiry. |
| Degraded | Warning badge | Show cause: high latency, stale local bridge, partial permissions. |
| Stale lease | Critical badge | Offer admin retry, cancel, or handoff per policy. |
| Offline | Muted warning | Show last seen, cached state, recovery steps. |
| Disabled | Locked badge | Show disabling authority and audit ref. |
| Unauthorized | Critical locked badge | Do not show sensitive task details. |

Lease detail must include:

- Task title and project.
- Runner label, not just runner ID.
- Lease owner and expiry.
- Last heartbeat.
- Allowed actions and disabled-action reasons.
- Audit trail and TaskResult/AgentRun writeback status.

## Approvals And Permission Dialogs

Purpose: keep approval work inside the main mental model even when OS/browser callbacks occur.

Approval surfaces:

- Global `Approvals` view for all pending decisions.
- Inline task/project approval panel.
- Modal for urgent approval or permission request.
- Callback result banner after external approval, deep link, or browser return.

Approval modal content:

- Plain-language decision title.
- Requesting Agent or human.
- Scope of impact.
- Evidence summary and source refs.
- Risk statement.
- Recommended action and alternatives.
- Buttons: approve, reject, request changes, open full evidence.

Permission modal content:

- Capability requested: notifications, local file picker, runner pairing, deep link registration, secure storage, local logs.
- Why needed now.
- What will be stored or accessed.
- Revocation path.
- Audit statement.
- Buttons: allow once when feasible, allow, deny, open settings.

Return-to-main-window rules:

- Any external approval, OAuth, OS permission, or deep link callback must focus or reopen the main window.
- Main window shows a result banner: success, denied, expired, duplicate callback, unsupported link, no permission.
- If callback cannot resolve task context, show safe fallback with search and recent approval list.
- Never leave user on a blank callback window.

## Offline, Failure, And Recovery States

Global states:

- `Online`: live stream connected, latest central state visible.
- `Reconnecting`: show retry countdown and keep last known data.
- `Offline`: read-only cached metadata; block sensitive writes and runner claims.
- `Degraded`: connected but one subsystem failed, for example notifications or runner stream.
- `Stale`: no successful sync beyond configured freshness threshold.

Write behavior:

- Low-risk local preferences may save locally.
- Server writes queue only when action is explicitly supported and idempotent.
- Approval, permission, runner lease, task finish, and acceptance actions require central confirmation before showing success.

Recovery UX:

- One recovery center lists failed syncs, queued writes, stale leases, duplicate callbacks, notification failures.
- Each item shows owner, retry eligibility, safe retry button, and audit state.
- Successful recovery replaces warnings with a timestamped success entry.
- Failed recovery never hides original failure reason.

Failure copy rules:

- Say what failed, why if known, what is safe to retry, who owns next action.
- Show internal IDs only in expandable "Technical details".
- For permission failures, show required role or scope and request route.

## Deep Link Design

Desktop deep link scheme:

- `zhenzhi://task/<taskId>`
- `zhenzhi://project/<projectId>`
- `zhenzhi://runner/<runnerId>`
- `zhenzhi://approval/<approvalId>`
- `zhenzhi://callback/<provider>/<state>`

Deep link behavior:

- If authenticated and authorized: open target in main window.
- If unauthenticated: route through sign-in, then open target.
- If unauthorized: show permission state without sensitive content.
- If target missing: show not found with safe search.
- If app already open: focus existing main window and navigate.
- If callback is duplicate: show "already processed" with previous result.
- If callback state mismatches: show security warning and do not process.

Deep link visual feedback:

- Temporary top banner names the link outcome.
- Activity log records accepted, rejected, expired, duplicate, unsupported.
- Settings exposes registered scheme status for Mac and Windows.

## Secure Storage Prompts

Secure storage settings:

- macOS: Keychain-backed credential reference.
- Windows: Credential Manager or platform-backed encrypted store.
- Local files: only non-secret preferences and redacted display cache.

Prompt must show:

- Stored item category: session reference, runner pairing reference, integration callback state, local preference.
- Non-storage statement: raw secret values, raw tokens, and raw source material are not stored in local files.
- Revocation path: sign out, remove runner pairing, clear local cache.
- Audit impact: server records security-sensitive changes where applicable.

Security states:

- Secure storage available.
- Secure storage locked by OS.
- Secure storage unavailable.
- Credential expired.
- Credential revoked remotely.
- Local cache cleared.

When secure storage is unavailable, desktop must degrade to session-only behavior and explain limitations before continuing.

## Mac And Windows Constraints

Shared IA:

- Same navigation, status naming, acceptance states, and evidence structure on both platforms.

macOS:

- Use native menu items for About, Settings, Quit, Hide, Services.
- Support Dock badge for pending approval count only when user enables notifications.
- Use Keychain language in secure storage prompts.
- Deep link registration appears in Settings with "registered on this Mac".

Windows:

- Use system tray for background runner status only when user enables background operation.
- Use Windows Credential Manager language in secure storage prompts.
- Use notification permission and startup behavior compatible with enterprise policy.
- Deep link registration appears in Settings with "registered on this PC".

Both:

- Keyboard navigation for all primary actions.
- Minimum window width must preserve rail, main content, and detail drawer without overlap.
- High contrast readable status colors with text labels.
- Enterprise proxy/offline states must appear before retry loops.

## Visual And Interaction System

Status colors must never be the only carrier of meaning. Every status uses label, icon, and detail text.

Core components:

- Status badge.
- Evidence chip.
- Requirement trace row.
- Task card.
- Runner card.
- Lease timeline.
- Approval modal.
- Permission modal.
- Recovery item.
- Acceptance gate row.
- Detail drawer.

Layout:

- Dense operational UI, no marketing hero.
- Tables for registry/history and traceability.
- Cards only for repeated operational items.
- Detail drawer for metadata and audit trail.
- Modal only for decisions requiring focused action.

## Acceptance Status UX

Acceptance states shown in Project Progress and task detail:

- `Not required`
- `Waiting Product Manager review`
- `Waiting Project Manager review`
- `Waiting human decision`
- `Changes requested`
- `Accepted`
- `Rejected`
- `Blocked by missing evidence`

For this task, the desktop design solution status is:

- Design solution: submitted.
- Product Manager review: required.
- Project Manager review: required.
- Development implementation: blocked until both reviews accept.

## Development Handoff

Development Agent receives these implementable surfaces:

- App shell: left rail, top bar, bottom status strip, notification center, settings.
- Home dashboard with required panels and empty/error states.
- Current Work task list/detail/timeline.
- Project Progress release/gap/requirement/acceptance views.
- Runner Registry, Pairing, Lease Monitor, History, Scope & Audit.
- Approval and permission modals with callback return banner.
- Recovery center for offline, failed sync, stale lease, duplicate callback, permission denial.
- Deep link handling states and user-visible result banners.
- Secure storage prompt and settings states.
- Mac/Windows platform copy variants.

Implementation requirements for handoff:

- Use central API read models for project, task, runner, lease, approval, notification, audit, and acceptance state.
- Keep mutating actions permission-gated by server response.
- Do not present cached state as current when sync is stale.
- Add idempotency for callback, retry, approval, and status-changing actions.
- Log user-visible failure reason and audit ref where available.
- Keep raw IDs secondary and copyable in technical detail only.

Non-goals:

- This design does not choose final frontend framework.
- This design does not implement production code.
- This design does not approve launch readiness.
- This design does not replace Product Manager acceptance criteria or Test Agent evidence matrix.

## Test Acceptance Points

Test Agent should verify:

1. Console Home shows work health, next actions, active Agent work, runner health, project progress, recovery signals.
2. Agent Current Work shows task route status, result status, quality decision, lease badge, acceptance badge, evidence refs, and timeline.
3. Project Progress maps gaps, requirement status, acceptance gates, and launch evidence without claiming partial items as complete.
4. Runner Registry supports paired, pending approval, online, busy, degraded, stale lease, offline, disabled, unauthorized states.
5. Lease detail shows task, project, runner label, owner, expiry, heartbeat, allowed actions, disabled reasons, audit trail.
6. Approval modal includes decision, evidence, risk, recommendation, and approve/reject/request-changes actions.
7. Permission modal explains capability, need, storage/access, revocation, audit impact, and denial state.
8. External approval, OAuth, OS permission, and deep link callbacks return to the main window with a result banner.
9. Offline mode is read-only for sensitive writes and does not show queued approval/lease/task finish success before central confirmation.
10. Recovery center exposes failed sync, stale lease, duplicate callback, notification failure, retry eligibility, and final result.
11. Deep links open target, sign-in route, unauthorized state, missing target, duplicate callback, and state mismatch safely.
12. Secure storage prompts use macOS Keychain and Windows Credential Manager wording, and session-only fallback is visible.
13. Acceptance status for this release stays waiting Product Manager and Project Manager review until accepted.
14. UI remains usable with keyboard, high contrast, narrow desktop width, long project names, and long human-readable task titles.

## Review Checklist

Product Manager Agent:

- Confirms UX covers AI-NATIVE-OS-PROD-GAP-002.
- Confirms Runner Admin needs from UREQ-008 are represented.
- Confirms acceptance state copy does not overstate implementation readiness.
- Confirms approval and permission flows are understandable to human reviewers.

Project Manager Agent:

- Confirms design can hand off to Development Agent and Test Agent.
- Confirms implementation remains blocked until review acceptance.
- Confirms evidence refs and task result are sufficient for routing.
- Confirms no production code was changed.

Development Agent:

- Confirms central state, permission, deep link, secure storage, and runner lease needs are implementable.
- Raises feasibility risks before implementation.

Test Agent:

- Converts the test acceptance points into launch evidence matrix rows.
- Verifies Mac/Windows state coverage independently.

## Open Risks

- Product still needs final PM acceptance criteria for each desktop capability before implementation acceptance.
- Technical solution must confirm exact desktop shell, update, signing, and secure storage implementation.
- Live distributed Agent Ring execution evidence remains outside this design task and must be verified separately.
- Feishu/API callback behavior must be reconciled with the desktop callback UX before launch.

## Conclusion

This design solution is complete for Product Manager Agent and Project Manager Agent review. It is ready to enter review, not implementation.
