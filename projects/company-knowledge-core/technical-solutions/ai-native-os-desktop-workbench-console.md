---
type: Workflow
title: AI Native OS desktop workbench and console technical solution
description: Technical solution for Desktop Workbench, Agent Hub, Project Console, and Agent Team Manager.
timestamp: "2026-06-21T06:30:00Z"
projectId: company-knowledge-core
taskId: kt-ai-native-os-tech-solution-desktop-workbench-console
authorAgent: agent.company.development
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
  - docs/product/ai-native-os/requirements.md
  - docs/product/ai-native-os/prd.md
  - projects/company-knowledge-core/tasks/kt-ai-native-os-tech-solution-desktop-workbench-console.md
  - projects/company-knowledge-core/coordination/ai-native-os-agent-execution-governance.md
reviewPath:
  - Product Manager Agent product fit review
  - Project Manager Agent delivery acceptance
  - Test Agent requirement coverage review
---

# AI Native OS Desktop Workbench And Console Technical Solution

## Scope

This solution covers the desktop client surface for:

- Agent Hub intake and status handling.
- Project Console health, task, source, evidence, risk, and queue views.
- Agent Team Manager for business Agents, governance Agents, capability reports, tools, skills, and health checks.
- Cross-platform desktop workbench shell for macOS and Windows from one maintained codebase.

Out of scope:

- Agent Ring runtime implementation.
- Central API implementation details outside client-facing contracts.
- Feishu bot implementation beyond shared state and callback expectations.
- Code implementation in this delivery step.

## Recommendation

Use **Tauri v2 plus a shared web frontend** as the recommended desktop workbench architecture, gated by `Slice 0: Desktop Distribution And Native Bridge Proof`.

The workbench should be a desktop client, not a web page wrapped late in the release. It should still share most UI code with any future web console by keeping the product UI in a web frontend and placing native desktop capability behind a small, permission-gated Tauri bridge.

Recommended stack:

- Desktop shell: Tauri v2.
- Frontend: TypeScript web app, preferably React with a Vite-style build for desktop startup speed.
- Local bridge: Rust Tauri commands for file picking, OS notifications, deep links, local app settings, secure credential references, and optional local runner pairing.
- Central state: AI Native OS API and Integration Gateway remains source of truth.
- Realtime: WebSocket or server-sent event stream from central API for project, task, runner, review, and notification updates.
- Local runner connection: desktop pairs with Agent Ring Runner through central API first; optional loopback connector only for local status and launch handoff, never as private state authority.

Why this route:

- One maintainable codebase for Mac and Windows.
- Smaller install footprint and lower memory cost than Electron.
- Stronger default security model because privileged native actions must be explicitly exposed.
- Enough native reach for desktop workbench needs: file picker, notifications, deep links, secure local config, updater, and local process handoff.
- Keeps the workbench aligned with central API contracts, avoiding divergent local semantics.

Main risk:

- Tauri plugin, updater, packaging, signing/notarization, enterprise proxy, secure storage, deep link, notification permission, and local runner pairing maturity must be verified in Slice 0 before broad desktop implementation. If Tauri fails a launch-blocking proof and the failure cannot be fixed inside Slice 0, stop broad console UI work and return an Electron fallback decision request to Product Manager Agent and Project Manager Agent.

## Desktop Technology Comparison

| Option | Strengths | Weaknesses | Fit |
| --- | --- | --- | --- |
| Tauri v2 with web frontend | Small binary, lower memory, Rust native bridge, explicit permissions, good Mac/Windows packaging, shared UI code. | Less battle-tested than Electron for complex enterprise desktop edge cases; Rust bridge skill required; plugin gaps may need custom work. | Recommended for AI Native OS workbench because native needs are focused and central API owns state. |
| Electron with web frontend | Mature ecosystem, many desktop apps proven at scale, rich auto-update patterns, easier Node-based local integrations. | Larger install size, higher memory, wider attack surface, more risk of ungoverned local file/process access. | Fallback if Tauri updater, signing, proxy, or runner pairing fails acceptance tests. |
| Native split: Swift/AppKit plus Windows .NET/WinUI | Best OS-native polish, strongest platform-specific control, deep enterprise integration possible. | Two codebases, higher cost, slower feature delivery, harder to keep Agent Hub and Console semantics identical. | Not recommended for launch; reserve for future isolated native modules if OS-specific capability becomes product-critical. |

Decision: recommend Tauri v2, shared web frontend, and Rust bridge for launch, but make Slice 0 the decision gate. Keep frontend framework independent of Tauri APIs so the UI can be reused in Electron or web console if needed. If Slice 0 fails on any launch-blocking Tauri proof and no in-slice fix is viable, request an Electron fallback decision before building full desktop surfaces.

## Product Architecture

```txt
Desktop Workbench
  Web UI layer
    Agent Hub
    Project Console
    Agent Team Manager
    Notification Center entry points
  Client state layer
    API client
    realtime subscription client
    optimistic UI queue
    local cache of non-secret display state
  Desktop bridge
    file picker and reference registration
    OS notification permission
    deep link handler
    secure credential reference storage
    local runner pairing helper
  Central API and Integration Gateway
    validated writes
    audit records
    state contracts
    permission and sensitivity checks
  Agent Ring Runner
    registers capability
    claims leases
    writes AgentRun and TaskResult
```

The desktop client must never become a second scheduler. It presents state, submits validated user actions, receives realtime updates, and can help pair a local runner. Scheduler, review gates, leases, sensitivity checks, and write audit stay in central services.

## Central API Connection

All durable writes go through the central API:

- Agent Hub intake creates or updates SourceMaterial, Requirement, Project, KnowledgeTask, status query, or clarification record.
- Project Console reads Project, Requirement, ProjectTask, KnowledgeTask, TaskResult, ReviewRecord, NotificationRecord, AgentRun, Decision, SourceMaterial, and MetricsReport.
- Agent Team Manager reads and updates Agent, ToolAsset, SkillAsset, capability report, role health, allowed scopes, and rollout state.

Client rules:

- Use short-lived access tokens plus refresh flow; store only credential references in OS secure storage.
- Do not store secret values, raw tokens, or raw sensitive source material in local files.
- Use server-side permission checks for every write and sensitive read.
- Include idempotency key for intake submission, approval callbacks, retry, and status-changing actions.
- Render human labels first and raw internal IDs only in secondary/debug detail.

Realtime:

- Subscribe by project, assigned review, notification inbox, active work queue, and runner status.
- On reconnect, fetch changed state by cursor to avoid missed updates.
- Show stale-state banner when realtime disconnects and last sync is old.

## Agent Runner Connection

Agent Ring remains external to this repository and external to the desktop workbench.

Preferred connection model:

1. Runner registers with central API and advertises machine, owner, heartbeat, load, Agents, tools, repositories, and data scopes.
2. Desktop displays runner status from central API.
3. Desktop can start a local pairing flow by opening a loopback callback or deep link.
4. Runner receives a scoped pairing proof from central API, not from the desktop client.
5. Runner claims tasks and writes TaskResult/AgentRun through central API.
6. Desktop observes status and exposes manual handoff actions, but does not write private runner state.

Loopback/local bridge is allowed only for:

- detect installed local runner;
- open runner setup;
- show local heartbeat diagnostics;
- pass a central API-issued pairing proof to a runner process after user confirmation;
- open local workspace path after permission check.

Loopback/local bridge is not allowed for:

- direct task lease mutation;
- bypassing central permission checks;
- direct unregistered tool execution;
- local storage of task evidence without TaskResult writeback.

## Agent Hub Solution

Requirement coverage: ANOS-REQ-001 through ANOS-REQ-006.

Core UI:

- Request composer for natural language, document link, file reference, meeting note, or task instruction.
- Source picker that records source type, project binding, sensitivity hint, and submitter.
- Project binding step: match existing project, create new project, or ask disambiguation when names collide.
- Classification preview: project creation, requirement clarification, knowledge query, knowledge capture, task status, approval action, or admin request.
- Async work state: immediate confirmation, durable task/status link, and later notification.

Core behavior:

- Submit intake to central API with source metadata and idempotency key.
- API performs classification, sensitivity detection, and permission routing; desktop only displays result.
- Ambiguous intent or ambiguous project creates clarification state, not silent dispatch.
- Human-facing confirmation includes business label, status, next action, owner, and link/ref.
- Raw IDs remain copyable in technical detail but are not primary UI text.

Data contract expected by desktop:

```txt
IntakeSubmission
  submitterRef
  channel = desktop
  inputType = natural_language | document_link | file_reference | meeting_note | task_instruction
  bodyRef or bodyText
  projectBinding
  sourceMetadata
  clientSensitivityHint
  idempotencyKey

IntakeResult
  displayTitle
  classification
  sensitivityDecision
  createdObjectRefs
  status
  nextAction
  ownerRef
  notificationRef
  auditRef
  clarificationQuestionRefs
```

## Project Console Solution

Requirement coverage: ANOS-REQ-030 through ANOS-REQ-034.

Primary views:

- Project health overview: launch state, requirement readiness, task progress, review status, notification health, and open blockers.
- Active work queues: first queue and active queue, with task type, runtime, required capabilities, assignee/runner, status, lease, risk, and acceptance path.
- Agent roster: business Agents and governance Agents by status, scope, current work, tools, and health.
- Evidence chain: SourceMaterial -> Requirement/PRD -> ProjectTask/KnowledgeTask -> AgentRun -> TaskResult -> ReviewRecord/KnowledgeItem.
- Blockers and risks: owner, reason, next action, notification state, due date, escalation path.

Console behavior:

- Default to owner-oriented summary: what changed, who owns it, next action.
- Allow drilldown into source evidence and audit trail without making raw IDs the primary content.
- Show stale leases and waiting runners as operational states, not vague failure.
- Display acceptance path from task runtime so user knows whether product, test, knowledge review, or human approval is next.

Data contract expected by desktop:

```txt
ProjectConsoleSnapshot
  project
  health
  requirementCoverage
  activeQueues
  agentRoster
  runnerSummaries
  sourceEvidenceChain
  reviewState
  notifications
  risksAndBlockers
  metrics
  lastUpdatedCursor
```

## Agent Team Manager Solution

Requirement coverage: ANOS-REQ-040 through ANOS-REQ-045.

Primary views:

- Business Agent directory for the eight business roles.
- Governance Agent directory separated from business Agents.
- Agent detail: profile, owner, allowed projects, allowed tools, knowledge scopes, skill packages, risk level, status, current work.
- Capability report: supported task types, tools, repositories, runtime needs, output contracts, acceptance paths, and runner compatibility.
- Role health check: missing skill, scope, tool, output contract, owner, test evidence, or rollout state.
- Tool and skill lifecycle: registered owner, version, tests, rollout state, rollback path, allowed Agents, audit requirements.

Guardrails:

- Governance Agents must not be visually or operationally mixed with execution roles.
- Disabled Agent, tool, skill, or scope is visible and cannot be selected for dispatch.
- Unregistered tool calls are represented as blocked/audited events, not hidden runtime errors.
- Skill update UI must require owner, version, test evidence, rollout state, and rollback path before eligible approval.

Data contract expected by desktop:

```txt
AgentTeamSnapshot
  businessAgents
  governanceAgents
  capabilityReports
  roleHealthChecks
  toolAssets
  skillAssets
  blockedToolEvents
  rolloutStates
```

## Local Permissions And Security

Desktop permissions should be product-specific and least-privilege:

- File access: use OS file picker; store file reference and metadata, not broad folder access by default.
- Notifications: request OS notification permission only after first user-visible notification need.
- Deep links: register app protocol for object links and runner pairing.
- Clipboard: user-initiated copy only.
- Local network: limited to central API and optional loopback runner pairing.
- Auth material: use OS secure storage for refresh-token reference or encrypted access handle; central auth material remains in server-side protected storage.
- Logs: redact tokens, auth material, raw sensitive body text, and file contents.
- Offline cache: cache only display metadata needed for recent state; encrypted at rest where supported; clearable from settings.

Security model:

- Desktop enforces UI affordances, but central API is enforcement authority.
- Every write must produce AuditLog through central API.
- Sensitivity decision comes from server-side classification and permission policy.
- Local runner pairing must be revocable from Admin/Governance Console.

## Packaging, Signing, And Release

Packaging targets:

- macOS: universal app where feasible, signed and notarized; distribute DMG or PKG depending enterprise install needs.
- Windows: signed MSI or NSIS installer; support per-user install first, machine-wide install only after admin policy is defined.

Release channels:

- internal-dev;
- pilot;
- stable;
- emergency rollback channel.

Build artifacts:

- versioned desktop binary;
- frontend asset hash;
- Tauri bridge version;
- API compatibility version;
- release notes with requirementRefs and migration notes.

Release gates:

- package install/uninstall smoke test on Mac and Windows;
- code signing verification;
- auto-update verification by channel;
- rollback verification;
- permission prompt audit;
- central API compatibility check;
- local runner pairing smoke test;
- no secret leakage in local logs and app storage.

Pre-implementation proof gate:

- Slice 0 must verify these gates before full desktop implementation starts.
- Shell-independent shared web frontend work may proceed only when it does not assume Tauri-specific behavior.
- Broad Agent Hub, Project Console, Agent Team Manager, native bridge productionization, runner pairing UX, and rollout implementation wait until Slice 0 passes or PM/Project Manager approve Electron fallback.

## Automatic Updates

Use Tauri updater if it passes Slice 0 proof:

- signed update manifest;
- channel-aware update URL;
- staged rollout support through server-side release channel;
- mandatory update flag only for security or API-breaking changes;
- user-visible release status and restart prompt;
- rollback by serving previous signed version on rollback channel.

Fallback if Tauri updater fails enterprise constraints:

- package-level managed distribution for stable release;
- Electron fallback decision request if auto-update, enterprise install, signing/notarization, secure storage, deep link, notification, or local Runner pairing is launch-blocking and cannot be solved with Tauri inside Slice 0.

## Implementation Slices

Slice 0: Desktop Distribution And Native Bridge Proof.

- Build minimal Tauri v2 app using shared web frontend boundary and Rust bridge stubs.
- Verify macOS packaging path: universal app feasibility where needed, DMG or PKG packaging, code signing, notarization feasibility, install, launch, uninstall.
- Verify Windows packaging path: signed MSI or NSIS packaging, per-user install, launch, uninstall, and machine-wide install decision inputs.
- Verify update channels: internal-dev, pilot, stable, emergency rollback channel, signed manifest, channel-aware URL, rollback, and forced-update rule limited to security or API-breaking incompatibility.
- Verify enterprise network behavior: proxy/VPN, custom CA or certificate inspection handling, API reachability diagnostics, updater reachability, and readable failure messaging.
- Verify secure local storage and auth material handling: OS secure storage plugin viability, refresh-token reference or encrypted access handle, no raw token or secret persistence in files, logs, crash reports, or cache.
- Verify native bridge behaviors: file picker permission shape, deep link registration for object links and runner pairing, OS notification permission prompt timing, local settings storage, and redacted diagnostics.
- Verify local Runner pairing proof flow: central API issues scoped pairing proof; desktop only hands access proof to local runner after user confirmation; runner writes AgentRun/TaskResult through central API; desktop cannot mutate leases or private runner state.
- Acceptance: all launch-blocking Mac/Windows packaging, signing/notarization, update, enterprise proxy, secure storage, auth material, deep link, notification permission, and pairing proof checks pass with evidence. If Tauri fails any launch-blocking proof and no in-slice fix is viable, produce Electron fallback decision request before broad UI implementation.

Slice 1: Desktop shell foundation after Slice 0 pass.

- Tauri shell, shared web UI scaffold, app routing, auth placeholder, environment/channel config, secure storage wrapper.
- Acceptance: app starts on Mac/Windows, connects to configured API health endpoint, logs redacted.

Slice 2: Central API client and realtime state.

- Typed API client, idempotency key support, cursor refresh, realtime subscription, stale-state UI.
- Acceptance: reconnect restores project and notification state without duplicate writes.

Slice 3: Agent Hub intake.

- Request composer, source/file/link registration flow, project binding/disambiguation, classification result display, async confirmation.
- Acceptance: covers ANOS-REQ-001..006 with auditable created refs and readable confirmation.

Slice 4: Project Console.

- Health overview, active queues, agent roster, evidence chain, blockers/risks, acceptance path display.
- Acceptance: covers ANOS-REQ-030..034 with traceable source-to-result chain and owner next action.

Slice 5: Agent Team Manager.

- Business/governance Agent directories, capability reports, role health, tool/skill registry read paths, blocked unregistered tool events.
- Acceptance: covers ANOS-REQ-040..045 and separates governance roles from execution roles.

Slice 6: Desktop native bridge productionization.

- File picker, OS notifications, deep links, local settings, secure credential handle, local runner detection.
- Acceptance: Slice 0 proofed bridge behaviors are hardened for production; permissions are explicit, auditable where writes occur, and no broad file/process access is granted.

Slice 7: Runner pairing and manual handoff support.

- Central API-issued pairing proof flow, local runner diagnostics, manual handoff visibility.
- Acceptance: desktop cannot mutate lease directly; runner writes AgentRun/TaskResult through central API.

Slice 8: Packaging and update rollout hardening.

- Signed Mac/Windows builds, installer smoke tests, updater rollout, rollback channel, release gate checklist.
- Acceptance: Slice 0 proof remains valid in production build; install, update, rollback, and uninstall pass on both target platforms.

## Test Strategy

Requirement trace tests:

- ANOS-REQ-001..006: intake submission cases for text, link, file reference, meeting note, task instruction, ambiguous intent, sensitivity block, async callback, and project disambiguation.
- ANOS-REQ-030..034: console snapshot cases for healthy project, waiting runner, stale lease, blocker, missing evidence, and owner next action.
- ANOS-REQ-040..045: Agent roster separation, capability report, missing skill/tool/scope health check, unregistered tool blocked event, skill version/test/rollback fields.

Desktop tests:

- Slice 0 proof tests for Mac/Windows packaging, signing/notarization feasibility, update channels, enterprise proxy/network behavior, secure storage/auth material, deep links, OS notification permission, and local Runner pairing proof flow.
- Unit tests for typed API mappers, permission guards, label formatting, and stale-state handling.
- Component tests for Agent Hub, Project Console, Agent Team Manager, empty/error/loading states.
- End-to-end desktop smoke tests on Mac and Windows for login, intake, project console drilldown, Agent detail, notification, deep link, and runner pairing.
- Packaging tests for signing, install, update, rollback, uninstall, and log redaction.
- Security tests for secret non-persistence, sensitive source display blocking, local cache clearing, and disabled tool/Agent behavior.

Regression gates:

- No write action without idempotency key.
- No raw internal ID as primary human-facing label.
- No direct runner lease mutation from desktop.
- No unregistered tool execution path from workbench.
- No secret value in local storage, logs, crash report, or knowledge file.

## Product Manager Agent Decisions Integrated

1. Future web console mode is architecturally preserved from day one, but not launched as supported UI until desktop pilot succeeds.
2. Launch offline behavior is read-only recent state plus draft intake queue. No offline approval, lease mutation, or evidence publication.
3. Local Runner pairing roles are System Admin and Runner Admin by default. Project Owner may pair only project-scoped runners when Admin grants permission.
4. File references register references and metadata first. File bytes ingestion requires Knowledge/Ops workflow decision and permission check.
5. Visible confirmation is required before task creation for admin request, approval action, permission/integration change, tool/skill enablement, and sensitive or ambiguous classification.
6. Project Console health labels are `On track`, `Needs attention`, `Blocked`, `Waiting for decision`, `Waiting for runner`, `Reviewing`, `Done`; runtime internals stay secondary.
7. Skill update approval is displayed in Agent Team Manager, with approval action routed to Review Center.
8. Forced update is allowed only for security or API-breaking incompatibility. Emergency rollback owner is Project Manager Agent plus Ops owner.

## Risks And Rollback

| Risk | Impact | Mitigation | Rollback |
| --- | --- | --- | --- |
| Tauri updater fails enterprise proxy/signing requirements. | Blocks desktop release automation. | Run updater, packaging, proxy, signing, and notarization proof in Slice 0 before broad implementation lock-in. | Use managed package distribution only if acceptable; if launch-blocking, request Electron fallback decision before broad UI work. |
| Tauri plugin gap for secure storage, deep links, or notifications. | Extra native bridge work. | Prove plugin or custom Rust bridge viability in Slice 0 behind a frontend-independent interface. | Implement custom Rust bridge; if still launch-blocking, request Electron fallback decision without rewriting product UI. |
| Desktop local runner bridge bypasses central governance. | Security and audit violation. | Central API-issued pairing proof only; no direct lease mutation. | Disable local bridge remotely; keep central runner registry workflow active. |
| Local cache stores sensitive material. | Data leakage. | Cache display metadata only; redact logs; server-side sensitivity enforcement. | Clear cache on next start; disable offline cache by config. |
| Native split requested later for platform polish. | Delivery slowdown. | Keep UI and contracts shell-independent. | Add native module for isolated OS feature instead of splitting whole app. |
| Console overwhelms users with runtime internals. | Poor adoption and wrong decisions. | Human-readable labels first, raw IDs secondary, owner/next-action summary. | Hide advanced runtime detail behind diagnostics mode. |
| Agent Team Manager accidentally mixes governance and execution roles. | Wrong assignment or approval confusion. | Separate directories, filters, and role type constraints. | Disable write actions for Agent Team Manager until role model is corrected. |

## Requirement Coverage Summary

| Requirement refs | Solution area |
| --- | --- |
| ANOS-REQ-001..006 | Agent Hub intake, classification, sensitivity, readable confirmation, async state, project binding. |
| ANOS-REQ-030..034 | Project Console health, roster, evidence chain, active queues, risks and blockers. |
| ANOS-REQ-040..045 | Agent Team Manager role registry, governance separation, capability report, health checks, tool blocking, skill lifecycle. |

## TaskResult Draft

```txt
taskRef: kt-ai-native-os-tech-solution-desktop-workbench-console
executorAgent: agent.company.development
outputRefs:
  - projects/company-knowledge-core/technical-solutions/ai-native-os-desktop-workbench-console.md
evidenceRefs:
  - docs/product/ai-native-os/requirements.md
  - docs/product/ai-native-os/prd.md
  - projects/company-knowledge-core/tasks/kt-ai-native-os-tech-solution-desktop-workbench-console.md
  - projects/company-knowledge-core/tasks/kt-ai-native-os-tech-solution-desktop-workbench-console-revision.md
  - projects/company-knowledge-core/tasks/kt-ai-native-os-tech-solution-desktop-workbench-console-retry.md
  - projects/company-knowledge-core/product-reviews/ai-native-os-technical-solutions-product-review.md
  - projects/company-knowledge-core/coordination/ai-native-os-agent-execution-governance.md
requirementRefs:
  - ANOS-REQ-001..006
  - ANOS-REQ-030..034
  - ANOS-REQ-040..045
openRisks:
  - Tauri Slice 0 proof may trigger Electron fallback decision request if launch-blocking failures remain.
  - Local runner pairing must remain central-API governed.
  - Enterprise network/proxy and signing/notarization constraints need confirmed target environments.
nextActions:
  - Product Manager Agent reviews Slice 0 gate and fallback decision language.
  - Test Agent derives requirement coverage tests from this solution.
  - Development Agent proceeds to broad desktop implementation only after Slice 0 passes or fallback decision is approved.
```
