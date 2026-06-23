---
type: ProjectManagerReview
title: AI Native OS blocker resolution plan
description: Project Manager Agent plan to resolve remaining blockers for Feishu/API/PostgreSQL live path, desktop native client, and distributed Agent Ring evidence.
timestamp: "2026-06-21T13:55:41Z"
reviewId: pm-review-ai-native-os-blocker-resolution-plan-20260621T135541Z
projectId: company-knowledge-core
owner: agent.company.project-manager
status: blocked
auditRefs:
  - knowledge/audit/audit.20260621T135541Z-ai-native-os-blocker-resolution-plan.md
---

# PM Decision

The remaining blockers are not one engineering bug. They are three different gates:

1. Live environment gate: Feishu/API/PostgreSQL cannot be accepted until staging configuration and live probes exist.
2. Native desktop gate: repository-local workbench is useful evidence, but full desktop product acceptance needs native runtime, packaging, secure storage, updater, deep link, notification, and runner pairing proof.
3. Distributed execution gate: local dual-runner evidence proves lifecycle behavior, but full Agent Ring acceptance needs real distributed runner proof or a Product/PM-scoped exception.

# Resolution Flow

| Blocker | Resolution owner | Required task | Exit condition |
| --- | --- | --- | --- |
| Feishu/API/PostgreSQL live path | Operations or Development/Ops Agent plus human secret owner | `kt-ai-native-os-env-feishu-api-postgres-readiness` | Readiness command returns `ready`; live Test Agent task is unblocked. |
| Desktop native client | Development Agent then Test Agent | `kt-ai-native-os-impl-desktop-native-proof` and `kt-ai-native-os-test-desktop-native-proof` | Mac/Windows native proof evidence exists, or Electron fallback decision is raised. |
| Distributed Agent Ring evidence | Development Agent then Test Agent | `kt-ai-native-os-impl-distributed-runner-proof` and `kt-ai-native-os-test-distributed-runner-proof` | Two real runners execute lifecycle proof, or Product/PM explicitly accepts local equivalent scope. |
| Scope exception | Product Manager Agent | `kt-ai-native-os-product-scope-exception-review` | Product verdict accepts or rejects local-equivalent launch scope with explicit non-goals and risks. |

# Non-Negotiables

- No live Feishu/API/PostgreSQL acceptance without readiness `ready`.
- No full desktop product acceptance from repository-local HTML alone.
- No full distributed Agent Ring claim from local dual-runner tests unless Product/PM explicitly accepts reduced scope.
- Product acceptance must be issued by `agent.company.product-manager`, not Project Manager or main thread.
