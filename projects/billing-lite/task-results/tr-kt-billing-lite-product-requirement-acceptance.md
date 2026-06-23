---
type: TaskResult
projectId: billing-lite
taskId: kt-billing-lite-product-requirement-acceptance
taskType: product_review
assignee: agent.company.product-manager
executorAgent: agent.company.product-manager
runner: runner.billing-lite-local-pm-codex
pmLeaseRef: pmlease.billing-lite.20260623T123333794462Z
pmActionRef: projects/billing-lite/pm-actions/pm-action.20260623T123511285417Z.md
leaseProof: pmlease.billing-lite.20260623T123333794462Z
status: submitted
conclusion: accepted_with_assumptions
summary: "PRD V1.0 accepted for architecture with Gate 0 assumptions; development must not pass Gate 0 until first app, first SKU, PSP, Windows P0, device limit, and credential/webhook ownership decisions close."
outputRefs:
  - projects/billing-lite/task-results/tr-kt-billing-lite-product-requirement-acceptance.md
evidenceRefs:
  - projects/billing-lite/tasks/kt-billing-lite-product-requirement-acceptance.md
  - projects/billing-lite/sources/sm-billing-lite-prd-v1.md
  - /Users/meimei/Documents/统一付费轻服务/00_原始资料/多端统一付费轻服务_PRD_V1.0.docx
  - /Users/meimei/Documents/统一付费轻服务/01_产品需求/billing-lite-product-requirement-acceptance.md
  - projects/billing-lite/project.md
  - projects/billing-lite/AGENTS.md
risks:
  - Windows P0 inclusion may change platform test/release scope.
  - PSP choice may affect adapter details, webhook verification, and operations runbook.
  - Device limit/reset policy affects License model, support SOP, abuse controls, and customer copy.
  - Credential/webhook/incident ownership must be explicit before production integration.
blockers: []
nextAction: "PM main thread should route this TaskResult to human/project acceptance and only then decide whether to release architecture; Gate 0 decisions must close before development crosses Gate 0."
checks:
  - "Checked task runtime: product_review, product_requirement_acceptance, human_review, productEvidenceRequired true, requiresTests false."
  - "Checked PRD source material and original docx extraction evidence."
  - "Checked PM draft as non-authoritative input and reissued Product Manager conclusion."
  - "Checked P0/P1/P2 scope, AC-01 through AC-13, technical acceptance dimensions, and Gate 0 open decisions."
testsOrChecks:
  - "No executable tests required for product acceptance."
  - "Schema validation run after write; initial failure corrected by moving required TaskResult fields into frontmatter."
approvalRequest:
  required: true
  requiredDecisionOwner: "PM main thread / human product owner"
  reason: "Product result is accepted_with_assumptions and requires Gate 0 decision closure before development implementation."
qualityEvaluation:
  decision: handoff_ready
  productConclusion: accepted_with_assumptions
  confidence: medium-high
  rationale: "P0 scope is coherent and testable; unresolved items are bounded as Gate 0 decisions rather than blockers."
acceptancePolicy:
  acceptanceStatus: waiting_acceptance
  path: human_review
  productResult: accepted_with_assumptions
  notes: "Architecture may start only after PM routing; development must not pass Gate 0 until open decisions close."
operatingRuleRefs:
  - docs/agent-team/company-agent-constitution.md
  - docs/agent-team/agent-task-runtime-contract.md
  - docs/agent-team/human-acceptance-policy.md
  - docs/agent-team/common-agent-operating-rules.md
  - agents/agent.company.product-manager.md
  - projects/billing-lite/AGENTS.md
  - projects/billing-lite/project.md
  - projects/billing-lite/tasks/kt-billing-lite-product-requirement-acceptance.md
commonRulesEvaluation:
  traceability: pass
  draftIsolation: pass
  roleIsolation: pass
  evidenceSufficiency: pass_with_assumptions
  permissionBoundary: pass
handoffContract:
  receiver: "PM main thread for acceptance routing; architecture role only after PM routing."
  architectureReady: true
  developmentGate: "Do not implement beyond Gate 0 until open decisions close."
createdAt: "2026-06-23T12:46:00+08:00"
---

# Billing Lite Product Requirement Acceptance

## summary

PRD V1.0 can be accepted for architecture with Gate 0 assumptions. Billing Lite is a lightweight shared billing service, not a full payment middle platform. P0 is sufficiently clear for architecture to start on product catalog, channel mapping, payment verification, device entitlement, restore purchase, callback handling, offline credential, audit, and minimal operations workflows.

Architecture may start after PM routing and required acceptance review. Development implementation must not pass Gate 0 until the open decisions below are closed by the appropriate human/project owners. In particular, production SKU creation, PSP SDK/channel commitment, Windows P0 commitment, device-limit policy, and production credential ownership are not released by this TaskResult.

Conclusion: `accepted_with_assumptions`.

## outputRefs

- `projects/billing-lite/task-results/tr-kt-billing-lite-product-requirement-acceptance.md`: formal Product Manager TaskResult.

## evidenceRefs

- `projects/billing-lite/tasks/kt-billing-lite-product-requirement-acceptance.md`: task definition, expected output, runtime, and current `processing` state.
- `projects/billing-lite/sources/sm-billing-lite-prd-v1.md`: extracted PRD source material, `BILLING-LITE-PRD-V1`.
- `/Users/meimei/Documents/统一付费轻服务/00_原始资料/多端统一付费轻服务_PRD_V1.0.docx`: original PRD copy, document version V1.0, document date 2026-06-22.
- `/Users/meimei/Documents/统一付费轻服务/01_产品需求/billing-lite-product-requirement-acceptance.md`: PM-thread draft reference only; used as input, not accepted blindly as formal conclusion.
- `projects/billing-lite/project.md`: project scope and non-goals.
- `projects/billing-lite/AGENTS.md`: Billing Lite gate and boundary rules.

## P0/P1/P2 Scope Matrix

| Capability | Level | Product acceptance position |
| --- | --- | --- |
| App, distribution channel, internal SKU, and channel product mapping | P0 | Accept. Operations must be able to create App, channel, `pro_lifetime`, and Apple/Google/external mappings. |
| Product catalog API | P0 | Accept. Must return sellable products by `app_id`, platform, channel, region, app version, and effective time. |
| Price management | P0 | Accept. Apple/Google client display uses store-returned price; external payment uses server price and effective-time snapshot. |
| Apple StoreKit verification | P0 | Accept. Server verifies transactions, grants entitlement idempotently by `transactionId`, supports notifications and restore. |
| Google Play Billing verification | P0 | Accept. Server verifies `purchaseToken`, grants entitlement idempotently, supports RTDN and restore. |
| External PSP / Apple Pay order path | P0 with assumption | Accept for architecture as adapter-based external payment path. Exact PSP and channel owner must close at Gate 0 before SDK/channel implementation. |
| Entitlement query and offline credential | P0 | Accept. Query by installation/license subject and return current entitlement plus signed offline credential and grace policy. |
| Restore purchase | P0 | Accept. Apple/Google restore after reinstall; external payment restore through License Code and device activation. |
| Refund / revoke handling | P0 | Accept. Platform notification or backend state change must revoke/freeze entitlement; next online query returns revoked state. |
| Order lookup | P0 | Accept. Operations/support must query by internal order number, channel transaction ID, and License identifier. |
| Manual entitlement handling | P0 | Accept. Operations/support may grant, revoke, or reset activation with reason and audit record. |
| Audit log | P0 | Accept. Product, price, entitlement, callback, and manual operations must be audit-visible. |
| Apple Offer Code redemption | P0 | Accept. Free Offer Code maps to the same Apple product and entitlement, not a separate entitlement type. |
| Apple/Google price auto-sync | P1 | Defer. Manual configuration/verification is enough for P0. |
| Device self-service unbind | P1 | Defer. P0 can use support reset; self-service can follow after launch evidence. |
| External payment enhancement | P1 | Defer. Add richer methods/regions/failure flows after PSP is chosen and first launch proves demand. |
| Lightweight account / identity binding | P2 | Defer. P0 must work without consumer account; future binding may attach to `license_subject`. |
| Cross-platform unified membership | P2 | Defer. Explicitly not P0; reassess only after business request for universal entitlement. |
| Subscriptions, consumables, marketing, finance settlement, invoice, tax, strong DRM | Out of scope | Reject from this release scope. Keep outside P0/P1 unless a new task changes product scope. |

## AC-01 through AC-13 Acceptance Matrix

| AC | Requirement acceptance | Status | Architecture / test expectation |
| --- | --- | --- | --- |
| AC-01 | Operations can create App, distribution channel, and `pro_lifetime` SKU. | Accepted | Configuration model and minimal operations page required. |
| AC-02 | Apple product ID does not include price; target price can change from 98 to 68 without new product ID. | Accepted | Product ID rule must be frozen at Gate 0. |
| AC-03 | External payment price change returns accurate effective price and keeps old order price snapshot. | Accepted | Order must persist amount, currency, price version, and creation-time snapshot. |
| AC-04 | iOS/Mac App Store purchase page displays StoreKit-returned price, not backend target price. | Accepted | Catalog returns channel product ID and business copy, not store display price override. |
| AC-05 | Repeating the same Apple `transactionId` 10 times creates one transaction and one entitlement. | Accepted | Unique key, idempotent transaction, and duplicate-submit test required. |
| AC-06 | Repeating the same Google `purchaseToken` does not duplicate entitlement. | Accepted | Unique key, idempotent transaction, and acknowledge strategy required. |
| AC-07 | PSP callback amount mismatch cannot mark order `PAID` and must raise alert. | Accepted | Adapter must verify signature, amount, currency, product, order status, and alert path. |
| AC-08 | User can purchase, query entitlement, and unlock professional feature without consumer login. | Accepted | `installation_id` / `license_subject` cannot depend on consumer account. |
| AC-09 | Apple/Google restore purchase regains entitlement after reinstall. | Accepted | StoreKit current entitlements, Google purchase state query, and backend restore required. |
| AC-10 | External License activates on one device and clearly rejects the second device when over limit. | Accepted with assumption | P0 default assumption: one active device; final limit/reset policy must close at Gate 0. |
| AC-11 | Free Offer Code redemption grants the same entitlement as the corresponding Apple product. | Accepted | Verify as normal Apple transaction; no separate entitlement type. |
| AC-12 | Refund/revoke notification causes next online query to return `REVOKED`. | Accepted | Notification verification, state pull, entitlement revoke, and client copy required. |
| AC-13 | During API outage, valid offline credential works within configured grace period. | Accepted with assumption | Grace length, signing algorithm, key ownership, and rotation must close at Gate 0. |

## Technical Acceptance Matrix

| Dimension | Required coverage before release |
| --- | --- |
| Channel environments | Apple StoreKit local test, Apple Sandbox, Apple production readiness; Google test track; PSP sandbox and production readiness. |
| Payment states | Success, cancel, failure, pending, duplicate submission, refund, revoke, callback retry, and callback out of order. |
| Network exceptions | Offline before purchase, delayed callback after payment, API timeout, client retry, server retry, and idempotent replay. |
| Restore scenarios | Same-device reinstall, device replacement, no purchase found, License device over limit, and support reset of old activation. |
| Risk controls | Tampered SKU, forged amount, forged callback, repeated `transactionId`, repeated `purchaseToken`, sandbox/production mix, and revoked entitlement reuse. |
| Data integrity | Immutable order price snapshot, entitlement state history, callback raw record, manual operation reason, and audit log. |
| Launch gates | Gate 0 model freeze; Gate 1 base service; Gate 2 Apple; Gate 3 Google; Gate 4 external payment/License; Gate 5 first app launch; Gate 6 second app reuse without core model change. |

## Open Decisions Required at Gate 0

| Decision | Required owner | Current assumption for architecture | Must not happen before closure |
| --- | --- | --- | --- |
| First app | Human product owner / PM routing | Use placeholder `app_a` for model shape only. | No production App record, launch test matrix, or release claim. |
| First SKU list | Human product owner / PM routing | Use `pro_lifetime` as first SKU and keep multi-SKU extensibility. | No production SKU creation or store product submission. |
| PSP choice and Apple Pay channel owner | Human product owner + architecture input | Design replaceable PSP adapter and channel boundary. | No SDK lock-in, PSP-specific data model lock, or production PSP integration. |
| Windows P0 | Human product owner / PM routing | Keep `windows` as platform enum and external payment-compatible model. | No Windows P0 build/test/release commitment. |
| Device limit and reset policy | Human product owner + support/operations input | Assume one active device and support reset for P0. | No final License enforcement constants or customer-facing promise. |
| Credential, webhook, and incident ownership | PM routing + operations owner | Architecture defines secret/webhook boundaries and operational responsibilities. | No production credential use, webhook go-live, or incident-response handoff. |

## testsOrChecks

- Checked task runtime: product review, `qualityGate: product_requirement_acceptance`, `acceptancePath: human_review`, `productEvidenceRequired: true`, `requiresTests: false`.
- Checked required source material and original docx extraction evidence against the PRD source record.
- Checked PM draft as non-authoritative input and reissued formal product conclusion in this TaskResult.
- Checked P0/P1/P2 scope, AC-01 through AC-13, technical acceptance dimensions, and Gate 0 open decisions.
- No executable product tests were required or run for this product acceptance task.

## operatingRuleRefs

- `docs/agent-team/company-agent-constitution.md`
- `docs/agent-team/agent-task-runtime-contract.md`
- `docs/agent-team/human-acceptance-policy.md`
- `docs/agent-team/common-agent-operating-rules.md`
- `agents/agent.company.product-manager.md`
- `projects/billing-lite/AGENTS.md`
- `projects/billing-lite/project.md`
- `projects/billing-lite/tasks/kt-billing-lite-product-requirement-acceptance.md`

## commonRulesEvaluation

- Traceability: Pass. Conclusion is tied to PRD source, original docx copy, project scope, task runtime, and draft reference.
- Draft isolation: Pass. The PM-thread draft was treated as input only; formal conclusion is issued by `agent.company.product-manager`.
- Role isolation: Pass. This result does not perform PM scheduling, architecture release, implementation, or test execution.
- Evidence sufficiency: Pass with assumptions. Product evidence is sufficient for architecture start; human decisions remain required before implementation crosses Gate 0.
- Permission and boundary: Pass. No architecture or engineering files were changed.
- Recovery rule: Pass. Task has a concrete TaskResult and no unrecoverable blocker.

## qualityEvaluation

- decision: `accepted_with_assumptions`
- rationale: P0 scope is coherent and testable, acceptance criteria are complete enough for architecture, and unresolved items are bounded as Gate 0 decisions rather than task blockers.
- confidence: medium-high
- residualRisks:
  - Product launch scope can shift if Windows is confirmed in or out of P0.
  - PSP choice may affect adapter details, webhook verification, settlement-facing fields, and operational runbook.
  - Device limit and reset policy affect License model, support SOP, abuse controls, and customer copy.
  - Credential ownership must be explicit before production integration.
- requiredBeforeDevelopmentBeyondGate0:
  - First app confirmed.
  - First SKU list confirmed.
  - PSP and Apple Pay ownership confirmed.
  - Windows P0 decision confirmed.
  - Device limit/reset policy confirmed.
  - Credential/webhook/incident owner confirmed.

## acceptancePolicy

- path: `human_review`
- productResult: `accepted_with_assumptions`
- PM routing needed: yes
- Architecture can start only after PM/human acceptance routing records this Product Manager result.
- Development implementation must not proceed beyond Gate 0 until the open decisions are closed.
- This TaskResult does not release downstream architecture task by itself; release remains PM main-thread responsibility.

## handoffContract

- Receiver: PM main thread for acceptance routing; architecture role may receive the result only after PM routing.
- Architecture-ready inputs:
  - P0/P1/P2 scope matrix above.
  - AC-01 through AC-13 acceptance matrix above.
  - Technical acceptance matrix above.
  - Gate 0 open decision table above.
- Architecture constraints:
  - Design for multi-app and multi-channel reuse, but keep first app/SKU as placeholders until confirmed.
  - Keep PSP implementation adapter-based until PSP choice is confirmed.
  - Preserve Windows platform compatibility in model unless PM/human explicitly removes Windows from P0.
  - Keep consumer accounts, subscriptions, consumables, cross-platform membership, finance settlement, invoice, tax, and strong DRM out of P0.
  - Treat License device limit, reset policy, offline credential signing, key rotation, webhook ownership, and incident response as Gate 0 closure items.
- Stop condition:
  - If PM/human cannot close any required Gate 0 decision, downstream implementation must pause and request a decision instead of silently choosing.
