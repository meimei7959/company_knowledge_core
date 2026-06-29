# Agent Control Plane Gray Release Plan

## Goal

Release enterprise Agent capability control plane v0.1 with conservative governance:

- no automatic capability publishing;
- no automatic Runner pull;
- every release requires human approval;
- all side effects must be traceable through AuditLog and trace CLI.

## Feature Flags

Use these defaults for gray release:

```txt
CAPABILITY_GOVERNANCE_ENABLED=true
CAPABILITY_RELEASE_ENABLED=true
CAPABILITY_RELEASE_REQUIRE_APPROVAL=true
CAPABILITY_AUTO_PUBLISH_ENABLED=false
CAPABILITY_RUNNER_AUTO_PULL_ENABLED=false
CAPABILITY_USAGE_FEEDBACK_ENABLED=true

FEISHU_CAPABILITY_ACTIONS_ENABLED=true
FEISHU_INLINE_PROCESSING_ENABLED=false
FEISHU_REQUIRE_TASK_ID_FOR_PROCESSING_REPLY=true

KNOWLEDGE_DISTILL_SIGNALS_ENABLED=true
KNOWLEDGE_DRAFT_VISIBLE_TO_AGENTS=true
KNOWLEDGE_VERIFIED_REQUIRED_FOR_POLICY=true
```

## Day 1: Owner Self-Test Only

- Allowed users: owner only.
- Allowed channels: local CLI and one controlled Feishu chat.
- Allowed actions:
  - create SourceMaterial;
  - create Task;
  - finish Task with draft CapabilityCandidate;
  - run capability review;
  - create draft CapabilityRelease;
  - approve one low-risk release manually;
  - run manual Runner pull.
- Disabled actions:
  - automatic release;
  - automatic Runner pull;
  - high-risk tool activation;
  - direct Skill/Tool mutation from Feishu material.

Daily checks:

```bash
zhenzhi-knowledge capability list
zhenzhi-knowledge trace feishu-message <message-id>
zhenzhi-knowledge trace runner <runner-id>
```

Inspect:

- `knowledge/audit/`
- failed `NotificationRecord`
- pending `capability_review`
- pending `capability_approval`
- failed or blocked runner task

## Stage 2: One Engineering Colleague

- Add exactly one engineering colleague.
- Scope: engineering knowledge and low-risk skill/workflow candidates.
- Requirement: every candidate must have evidence refs and a task result.
- Release rule: owner approves before any Runner pull.
- Review daily:
  - rejected candidates;
  - changes requested;
  - failed notification attempts;
  - Runner pull audit records;
  - usage events.

Exit criteria:

- No untraceable capability candidate.
- No release without approval.
- No duplicate Feishu callback side effect.
- At least one usage event links release/task/result.

## Stage 3: One Operations Colleague

- Add exactly one operations colleague.
- Scope: workflow/playbook feedback and operational material intake.
- Do not allow tool activation.
- Keep `CAPABILITY_RUNNER_AUTO_PULL_ENABLED=false`.
- Use Feishu only for intake and status; no automatic capability release.

Exit criteria:

- Operations material classified correctly as knowledge draft or capability candidate.
- Business/market material does not create CapabilityCandidate.
- Feedback links to task/result/release when applicable.

## Daily Gray-Release Checklist

1. Review AuditLog count and unexpected actions.
2. Review failed NotificationRecord and delivery attempts.
3. Review pending capability review tasks.
4. Review pending capability approval tasks.
5. Review failed, blocked or stale runner tasks.
6. Run trace on at least one Feishu message, one task, one release and one runner.
7. Confirm no `CapabilityRelease` has `released` status without `approvedBy`.
8. Confirm no high-risk material is visible in ordinary retrieval.

## Rollback

Immediate feature rollback:

```txt
CAPABILITY_RELEASE_ENABLED=false
CAPABILITY_AUTO_PUBLISH_ENABLED=false
CAPABILITY_RUNNER_AUTO_PULL_ENABLED=false
FEISHU_CAPABILITY_ACTIONS_ENABLED=false
```

Operational rollback:

1. Stop approving `capability_approval` tasks.
2. Mark suspect releases `disabled` or `rejected`.
3. Ask runners to pull again manually.
4. Leave SourceMaterial, TaskResult, NotificationRecord and AuditLog intact.
5. File a repair task for each failed or ambiguous side effect.
6. If code rollback is required, revert only the release commit.

## Do Not Do During Gray Release

- Do not enable `CAPABILITY_AUTO_PUBLISH_ENABLED`.
- Do not enable `CAPABILITY_RUNNER_AUTO_PULL_ENABLED`.
- Do not publish tool or policy capabilities from Feishu intake.
- Do not delete audit records while investigating failures.
- Do not mix unrelated repository cleanup into the release commit.
