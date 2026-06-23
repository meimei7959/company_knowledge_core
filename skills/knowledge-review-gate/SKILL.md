---
name: knowledge-review-gate
description: Use when reviewing structured knowledge drafts for evidence, category, confidence, sensitivity, duplicate risk, and publish path.
---

# Knowledge Review Gate

## Purpose

Prevent low-quality or unsourced knowledge from becoming reusable truth.

## Triggers

- A KnowledgeItem draft is produced.
- A lesson, incident, or process rule is ready for reuse.
- A verified item may change.

## Inputs

- KnowledgeItem draft.
- SourceMaterial and evidence refs.
- Scope, confidence, and sensitivity.

## Workflow

1. Check structure, category, source evidence, confidence, and scope.
2. Check duplicate, conflict, and sensitivity risk.
3. Decide draft, observed, review required, or human approval required.
4. Create review record and publish/index only when allowed.
5. Route rejected or weak drafts back for repair.

## Outputs

- Review decision.
- Issue or repair route.
- Approval request when required.
- Publish/index instruction when allowed.

## Quality Gate

- Reusable conclusion is evidence-backed.
- Source path is available to future Agents.
- Verified or policy-level knowledge never bypasses human review.

## Failure Routes

- Missing evidence: return to source ingest or extraction.
- Conflict detected: create ConflictRecord.
- High-impact rule: require human approval.
