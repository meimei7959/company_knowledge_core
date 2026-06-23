---
type: SourceMaterial
title: 多端统一付费轻服务 PRD V1.0
description: PRD for Billing Lite, a lightweight shared billing, payment verification, and device entitlement service across iOS, macOS, Android, and Windows apps.
timestamp: "2026-06-23T11:55:53Z"
sourceId: sm-billing-lite-prd-v1
projectId: billing-lite
materialType: docx
sourceRef: /Users/meimei/Downloads/多端统一付费轻服务_PRD_V1.0.docx
storageRef: /Users/meimei/Documents/统一付费轻服务/00_原始资料/多端统一付费轻服务_PRD_V1.0.docx
originalRef: /Users/meimei/Downloads/多端统一付费轻服务_PRD_V1.0.docx
contentHash: sha256:b5f502fede86ba347140df5788210a04eb271d34b625e4aa956828a6f0677239
author: unknown
documentDate: "2026-06-22"
documentVersion: V1.0
documentStatus: 评审稿
sensitivity: internal
license: internal
extractionTool: docx_zip_xml_extract
extractionStatus: extracted_summary
extractionConfidence: high
createdBy: agent.company.project-manager
updatedAt: "2026-06-23T11:55:53Z"
---

## Extracted Summary

Entity workspace: `/Users/meimei/Documents/统一付费轻服务`.

Stored PRD copy: `/Users/meimei/Documents/统一付费轻服务/00_原始资料/多端统一付费轻服务_PRD_V1.0.docx`.

The PRD defines Billing Lite as a lightweight common billing service, not a full payment middle platform. It exposes a unified JSON API for product catalog, payment verification, device entitlement, callback handling, and restore purchase flows while each client continues to use the payment method required by its platform.

P0 intentionally excludes consumer accounts, cross-platform membership, subscriptions, consumables, complex marketing, finance settlement, invoice, tax, and strong DRM. Default commercial mode is per-app, per-platform one-time lifetime purchase.

## Key P0 Capabilities

- Configure apps, distribution channels, products, target price, availability, and mapping.
- Keep Apple / Google product IDs stable because IDs represent entitlement rather than price.
- Verify Apple StoreKit, Google Play Billing, and external PSP / Apple Pay order results on the server.
- Issue entitlement only after trusted server-side verification.
- Use anonymous `installation_id`, platform transactions, and external License to identify entitlement.
- Support Apple / Google purchase restore after reinstall.
- Handle refund, revoke, webhook, and duplicate callback idempotently.
- Provide minimal operations pages for configuration, query, abnormal order handling, and support.

## Acceptance Highlights

- Operations can create App, channel, and `pro_lifetime` SKU.
- Apple product ID does not include price, and target price changes do not require new product IDs.
- Direct payment price changes return according to effective time; old orders preserve price snapshot.
- Store payment pages display StoreKit / Play localized price, not backend target price.
- Repeated Apple `transactionId`, Google `purchaseToken`, and PSP callback submissions do not duplicate entitlement.
- PSP amount mismatch cannot mark an order as paid and must raise an alert.
- No-login purchase, entitlement query, and professional-feature unlock must work.
- Refund / revoke notification leads the next online entitlement query to return `REVOKED`.

## Launch Gates

- Gate 0: model freeze for product ID rules, SKU, platform matrix, and data model.
- Gate 1: base service for configuration, catalog, installation, entitlement, and audit.
- Gate 2: Apple StoreKit, verification, notifications, restore, and Offer Code.
- Gate 3: Google Play Billing, backend verification, RTDN, and restore.
- Gate 4: external order, PSP / Apple Pay, webhook, and License.
- Gate 5: first app launch with monitoring, alerting, support SOP, rollback, and SLO checks.
- Gate 6: second app reuse without backend core model change.

## Open Decision Areas

- First app and exact first SKU list.
- External PSP choice and Apple Pay channel owner.
- Default device activation limit and reset policy.
- Whether Windows enters P0 external payment or follows after first launch.
- Production channel credentials, webhook ownership, and incident response owner.
