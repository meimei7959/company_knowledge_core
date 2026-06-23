# Billing Lite Decisions

## D0 Project Naming

- Chinese name: 统一付费轻服务
- English name: Billing Lite
- Project ID: `billing-lite`

Reason: matches the PRD product code, keeps the project intentionally small, and avoids implying a full billing middle platform.

## D1 P0 Product Shape

Billing Lite is a lightweight shared service centered on unified APIs and minimal operations surfaces. It is not a consumer account system, payment aggregation platform, finance system, or marketing system.

## D2 P0 Entitlement Boundary

Default P0 entitlement is per App plus platform / distribution channel. Cross-app and cross-platform membership remains future scope unless explicitly accepted by product review.

## D3 Trust Boundary

Client amount, client price, and client-declared payment success are not trusted. Entitlement must be issued from server-side verification or validated PSP callback state.

