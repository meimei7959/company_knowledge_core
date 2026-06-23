---
type: Project
title: 统一付费轻服务
description: Internal Billing Lite project for shared product billing, payment verification, device entitlement, and purchase restore across apps and platforms.
timestamp: "2026-06-23T11:55:53Z"
projectId: billing-lite
owner: meimei
humanOwner: 梅晓华
status: draft
scope: project
members:
  - meimei
relatedRepos: []
workspaceRef: /Users/meimei/Documents/统一付费轻服务
workspaceStructure:
  - /Users/meimei/Documents/统一付费轻服务/00_原始资料
  - /Users/meimei/Documents/统一付费轻服务/01_产品需求
  - /Users/meimei/Documents/统一付费轻服务/02_架构方案
  - /Users/meimei/Documents/统一付费轻服务/03_研发实现
  - /Users/meimei/Documents/统一付费轻服务/04_测试验收
  - /Users/meimei/Documents/统一付费轻服务/05_运营上线
  - /Users/meimei/Documents/统一付费轻服务/99_项目管理
relatedAgents:
  - agent.codex.local
  - agent.company.project-manager
  - agent.company.product-manager
  - agent.company.architecture
  - agent.company.development
  - agent.company.test
  - agent.company.operations
relatedTools:
  - tool.zhenzhi-knowledge
sourceMaterialRefs:
  - projects/billing-lite/sources/sm-billing-lite-prd-v1.md
updatedAt: "2026-06-23T12:32:54Z"
health: needs_decision
lastProjectManagerReviewRef: projects/billing-lite/pm-reviews/pm-review.20260623T123254353410Z.md
---

## Goal

Build a lightweight reusable billing service for multiple internal apps. The service provides a unified product catalog, price management, payment verification, device entitlement, purchase restore, external payment order handling, and basic operations support without creating a consumer account system.

## Scope

P0 scope follows the PRD:

- Multi-app and multi-channel product configuration.
- One-time lifetime purchase SKU, initially `pro_lifetime`.
- Apple IAP and Google Play Billing verification.
- External payment order, webhook, and License activation path for independent distribution channels.
- Anonymous installation identity and device-level entitlement.
- Purchase restore for Apple / Google channels.
- Minimal configuration and operations page.
- Transaction, entitlement, license, callback, audit, and monitoring records needed for support and risk control.

## Non-Goals

- Consumer registration, login, phone, email, password, profile, or social account system.
- Cross-app or cross-platform unified membership in P0.
- Subscription, consumable, usage pack, coupon, distributor, points, or marketing automation in P0.
- Payment aggregation, card acquiring, tax, invoice, revenue recognition, or finance ledger.
- Strong DRM guarantees beyond reasonable entitlement validation and risk controls.

## Current Focus

1. Product Manager validates and freezes the PRD scope, acceptance criteria, and unresolved decisions.
2. Architecture Agent designs the minimal V0 service model, payment adapter boundary, security controls, and rollout gates.
3. Development Agent implements the foundation only after product and architecture acceptance.
4. Test Agent verifies Apple, Google, PSP, idempotency, refund/revoke, restore, and no-login entitlement flows.
5. Operations Agent prepares launch checklist, monitoring, alerting, support SOP, and channel readiness.

Active task list: [projects/billing-lite/tasks/index.md](tasks/index.md).

## Workspace

实体项目目录在 `/Users/meimei/Documents/统一付费轻服务`。知识中枢里的 `projects/billing-lite/` 只保存项目管理、任务、来源材料、审计和交接记录。
