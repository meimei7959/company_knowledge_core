# Access Credential Request Flow

## Purpose

After Agent Ring exists, token handling must be split by responsibility.

The central processor should not become a place that stores or broadcasts every token. It should own the request, approval, policy, authorization scope, reference record, audit, and notification. Secret values must live in a Secret Manager, server runtime environment, or Agent Ring local secure store.

## Terminology

Use `access credential` in product language.

`token` is only one kind of credential. Other credential types include API keys, OAuth tokens, runner registration tokens, project-specific service tokens, and local tool credentials.

## Ownership Matrix

| Credential Type | Central Processor Owns | Secret Value Lives In |
| --- | --- | --- |
| Central processor API token | request, approval, issuance policy, audit | server secret store / env / identity service |
| Agent Ring runner registration token | request, approval, runner identity, revocation, audit | Agent Ring secure store after issuance |
| Local Codex / Claude / Git / browser credential | request record, policy, scope, audit | Agent Ring local secure store |
| DeepSeek API key for Feishu bot | config reference, owner, rotation record, audit | bot service secret store |
| Project-private third-party token | owner, approval, scope, secretRef, audit | Secret Manager or project-approved Agent Ring store |

## Flow

```txt
User asks Feishu bot for access credential
-> DeepSeek/router classifies credential type and risk
-> central processor creates AccessCredentialRequest
-> safety gate checks chat type, requester identity, project scope, risk
-> approval owner reviews
-> if central API/runner token: central processor or identity service issues credential
-> if local/project tool token: Secret Owner or Agent Ring configures secret locally
-> central processor stores secretRef, scope, expiry, owner, audit
-> requester gets setup instructions, never group-visible secret value
```

## Direct Bot Behavior

The bot may:

- accept request in private chat;
- explain what information is missing;
- create an AccessCredentialRequest;
- show request status;
- send setup instructions after approval;
- notify Secret Owner or Agent Ring that local configuration is required.

The bot must not:

- send credential values in group chat;
- store secret values in Markdown, knowledge, task descriptions, logs, screenshots, or audit details;
- grant credentials without approval when policy requires approval;
- reveal credentials from Secret Manager;
- ask users to paste secret values into chat unless an approved secure channel exists.

## Required Request Fields

```yaml
requestId: credential.20260618T000000Z
credentialType: central_api | runner_registration | local_tool | project_service | model_api
requester:
projectId:
runnerId:
toolOrService:
purpose:
credentialScope:
credentialRisk:
expiry:
secretRef: secretref://zhenzhi/<credentialType>/<owner-or-runner>
status: pending
approver:
notificationRefs: []
auditRefs: []
```

## Agent Ring Integration

When the credential is for a distributed computer:

1. Central processor approves the request and records allowed scope.
2. Agent Ring receives configuration instruction or pulls pending credential setup tasks.
3. Agent Ring stores secret locally or references an approved Secret Manager.
4. Agent Ring reports only `secretRef`, readiness, and health check result.
5. Central processor never stores the plaintext value.

## Stub Runner Testing

Before Agent Ring exists, the stub runner should simulate secret readiness without using real secret values.

Test data should use fake refs:

```yaml
secretRef: secretref://stub/deepseek
secretRef: secretref://stub/runner-registration
secretRef: secretref://stub/project-tool
```

Tests should assert:

- group chat token requests are redirected to private chat;
- AccessCredentialRequest is created;
- secret value is not written into files;
- approved request stores `secretRef`, not plaintext;
- StubRunner can continue when required secretRef is present;
- StubRunner blocks with a clear status when required secretRef is missing.

## Review Rules

Human or governance approval is required for:

- new central API token;
- runner registration token;
- model API key;
- project service token;
- any credential with write/delete/customer-facing capability;
- any credential crossing project, customer, or data-scope boundary.

Low-risk read-only project credentials may still require owner approval depending on project policy.
