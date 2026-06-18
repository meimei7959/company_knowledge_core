# Core Object Model Draft

This object model supports the first-stage OKF-compatible knowledge bundle and later migration to API/database storage.

Every object is represented as Markdown with YAML frontmatter. `type` is required.

First-stage object creation and updates are performed through `zhenzhi-knowledge` commands or equivalent reviewed Markdown changes.

## Shared Frontmatter

Recommended shared fields:

- `type`
- `title`
- `description`
- `tags`
- `timestamp`
- `owner`
- `status`
- `scope`
- `sourceRef`
- `confidence`

Tools must preserve unknown fields.

Status values:

- `draft`
- `observed`
- `testing`
- `verified`
- `approved`
- `stale_candidate`
- `stale`
- `deprecated`
- `blocked`
- `rejected`
- `active`
- `open`
- `resolved`

## Project

Temporary project source of truth until the project management product is ready.

Key fields:

- projectId
- owner
- members
- status
- goal
- scope
- currentFocus
- relatedRepos
- relatedAgents
- relatedTools
- latestUpdate

## Agent

Registered local or hosted agent identity.

Key fields:

- agentId
- owner
- aiTool
- purpose
- allowedProjects
- allowedTools
- allowedKnowledgeScopes
- riskLevel
- humanApprovalRequired
- status

## ToolAsset

Reusable team tool asset. Tool code lives in Git or the tool runtime; core stores metadata, permissions, usage notes, and risk.

Key fields:

- toolId
- owner
- repoRef
- entrypoint
- version
- status
- riskLevel
- invocationPolicy
- requiresApproval
- executionMode
- inputSchema
- outputSchema
- allowedAgents
- allowedProjects
- secretsRequired
- usageNotes
- knownIssues
- lastVerifiedAt

## KnowledgeItem

Reusable business or engineering knowledge.

Types:

- fact
- decision
- lesson
- pattern
- constraint
- issue
- prompt
- workflow

Required governance:

- sourceRef
- confidence
- status
- scope
- owner
- updatedAt
- reviewAgentResult

## SourceMaterial

Reference to original input. The original may live in Git, cloud drive, chat, meeting notes, customer folders, or object storage.

Key fields:

- sourceId
- sourceType
- sourceRef
- owner
- sensitivity
- projectId
- summary
- extractedKnowledge

## ChatThread

Communication channel bound to a project.

Examples:

- Feishu/Lark customer group.
- Internal delivery group.
- Customer confirmation thread.

Key fields:

- chatThreadId
- projectId
- customerId
- provider
- externalChatId
- title
- participants
- status
- latestMessageAt

## Interaction

Individual communication event or summarized interaction.

Examples:

- Customer uploaded a file.
- Project manager agent asked missing questions.
- Customer confirmed a fact.

Key fields:

- interactionId
- projectId
- customerId
- chatThreadId
- providerMessageId
- sender
- messageType
- summary
- sourceMaterialRefs
- extractedKnowledgeRefs

## MissingFact

Structured missing information needed by a workflow or domain.

Key fields:

- missingFactId
- projectId
- customerId
- requestedByDomain
- question
- reason
- status
- relatedSourceRefs
- askedInInteractionId
- answeredByInteractionId

## AgentRun

Trace of one meaningful agent task.

Key fields:

- runId
- projectId
- agentId
- task
- contextRefs
- toolsUsed
- knowledgeUsed
- outputRefs
- codeRefs
- humanReview
- result
- lessons

## Decision

Project or company decision.

Key fields:

- decisionId
- projectId
- owner
- status
- context
- options
- decision
- rationale
- affectedObjects

## Policy

Machine-readable permission and approval rule.

Key fields:

- policyId
- agentId
- allowedProjects
- allowedKnowledgeScopes
- allowedToolRiskLevels
- writePermissions
- requiresApproval

## ConflictRecord

Record for Git conflicts, factual conflicts, decision conflicts, or experience conflicts.

Key fields:

- conflictId
- conflictType
- affectedRefs
- owner
- status
- resolution

## EvalCase / EvalRun

Evaluation cases and runs for Agent, Prompt, and ToolAsset quality.

Key fields:

- evalId
- targetRef
- input
- expected
- actual
- score
- result
- failureNotes

## ReviewRecord

Human or agent review of a knowledge object, deliverable, tool, workflow output, or domain output.

Key fields:

- reviewId
- targetRef
- reviewer
- reviewType
- result
- comments
- issueRefs
- approvedAt
- reviewAgentId
- gateResult
- requiredHumanApproval
- generatedApprovalDocRef

## IssueRecord

Structured issue found during evaluation, review, audit, or delivery.

Key fields:

- issueId
- targetRef
- severity
- problem
- evidence
- suggestedFix
- assignedTo
- status
- resolvedBy
- resolvedAt

## MetricsReport

Operational metrics for the knowledge system.

Key fields:

- reportId
- period
- startCount
- finishCount
- unfinishedTasks
- draftBacklog
- staleCount
- toolReuseCount
- agentFailureRate

## AuditLog

Record of important writes, status changes, approvals, and permission changes.

Key fields:

- auditId
- actor
- action
- targetRef
- before
- after
- policyResult
- timestamp
