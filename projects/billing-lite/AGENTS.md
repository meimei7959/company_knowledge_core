---
type: Policy
title: Billing Lite Agent Rules
policyId: policy-billing-lite-agent-rules
projectId: billing-lite
timestamp: "2026-06-23T11:55:53Z"
updatedAt: "2026-06-23T11:55:53Z"
---

# Billing Lite Agent Rules

This project is an internal payment and entitlement module. Agents must preserve the PRD boundary: lightweight shared service, unified API, no consumer account system, no complex billing platform in P0.

## Required Rule Layers

Formal tasks must load:

- [Company Agent Constitution](../../docs/agent-team/company-agent-constitution.md)
- [Agent Task Runtime Contract](../../docs/agent-team/agent-task-runtime-contract.md)
- [Human Acceptance Policy](../../docs/agent-team/human-acceptance-policy.md)
- [Common Agent Operating Rules](../../docs/agent-team/common-agent-operating-rules.md)
- role rules from `agents/<agent>.md`
- this project file

Every TaskResult must record `operatingRuleRefs` and `commonRulesEvaluation`.

## Project Boundaries

- Do not introduce consumer login, phone, email, password, or account recovery into P0.
- Do not implement cross-app or cross-platform membership by default.
- Do not treat client-reported amount or client-reported payment success as trusted.
- Do not create new Apple / Google product IDs for ordinary price changes.
- Do not persist secret values, private keys, webhook secrets, API tokens, or payment credentials in project knowledge files.
- Do not make this service a finance ledger, invoice system, tax system, or revenue recognition system.
- Keep Apple, Google, and external PSP differences behind adapter boundaries; product-facing APIs should stay stable.

## Acceptance Bias

Favor small verifiable release gates:

- Gate 0: model freeze.
- Gate 1: base service.
- Gate 2: Apple.
- Gate 3: Google.
- Gate 4: external payment and License.
- Gate 5: first app launch.
- Gate 6: second app reuse without core model changes.
