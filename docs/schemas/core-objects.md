# Core Object Model Draft

This object model supports the first-stage OKF-compatible knowledge bundle and later migration to API/database storage.

Every object is represented as Markdown with YAML frontmatter. `type` is required.

First-stage object creation and updates are performed through `zhenzhi-knowledge` commands or equivalent reviewed Markdown changes.

The current core positioning is central processor: scheduler plus knowledge operations. A SourceMaterial should normally become reusable knowledge only through a task:

```txt
SourceMaterial -> ProjectTask / KnowledgeTask -> Agent Ring Runner execution -> TaskResult -> KnowledgeItem draft -> Review
```

Relationship management is part of the same lifecycle. Important references should be parseable so the local index, API layer, and future graph view can derive managed edges:

```txt
managed object fields -> KnowledgeGraphEdge index -> impact analysis / stale checks / context pack reasons / GraphSnapshot export
```

Graph edges help navigation and governance, but they do not replace the source objects. Truth still comes from the reviewed Project, TaskResult, SourceMaterial, KnowledgeItem, Decision, Policy, ReviewRecord, and AuditLog records.

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
- parseable relationship fields such as `projectId`, `taskId`, `agentId`, `runnerId`, `toolId`, `sourceMaterialRefs`, `knowledgeRefs`, `evidenceRefs`, `codeRefs`, `affectedRefs`, or `auditRefs`

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
- `pending`
- `processing`
- `submitted`
- `reviewing`
- `done`
- `resolved`

## Project

Temporary project source of truth until the project management product is ready. Project owns context and status, but not full source code or every execution detail.

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

## ProjectTask / KnowledgeTask

Track work that must be handled by a distributed Agent Ring runner. `KnowledgeTask` is a specialized task for processing SourceMaterial into structured knowledge.

Key fields:

- taskId
- taskType
- projectId
- requester
- requiredCapabilities
- requiredAgents
- preferredRunner
- assignedRunner
- executorAgent
- leaseOwner
- leaseExpiresAt
- sourceMaterialRefs
- status
- priority
- dueAt
- expectedOutput
- resultRef
- notificationRefs
- auditRefs

Supported task types:

- `project_init`
- `knowledge_capture`
- `engineering_action`
- `tool_request`
- `handoff`

Supported task statuses:

- `pending`
- `processing`
- `submitted`
- `reviewing`
- `done`
- `blocked`
- `rejected`

Rules:

- A Feishu/Lark material intake should create SourceMaterial first, then create a task for scheduler assignment.
- Server-side lightweight models may classify intent and extract fields; heavy parsing and structuring should be performed by an Agent Ring runner using local Codex, Claude, local models, IDE automation, browser automation, or approved local tools.
- Task status changes must be auditable.
- User-facing notifications should reference human-readable title, requester, assigned runner or executor Agent, and taskId.

## AgentRunner

Central registry record for an external Agent Ring runner.

Agent Ring itself is not implemented here. AgentRunner is the central processor's view of a distributed computer.

Key fields:

- runnerId
- ringVersion
- hostName
- hostType
- status
- mode
- agents
- capabilities
- availableProjects
- repoAccess
- dataScopes
- resource
- load
- lastHeartbeatAt

Rules:

- Runner registration is self-reported and should be verified by health checks for critical capabilities.
- Capability and permission are separate.
- Secrets must not be stored in AgentRunner records.
- Runner status and heartbeat are scheduler inputs.

## TaskResult

Track what an Agent Ring runner and executor Agent produced for a task.

Key fields:

- resultId
- taskId
- projectId
- runnerId
- executorAgent
- status
- summary
- outputRefs
- knowledgeRefs
- sourceMaterialRefs
- evidenceRefs
- testsOrChecks
- nextActions
- operatingRuleRefs
- commonRulesEvaluation
- qualityEvaluation
- acceptancePolicy
- completedAt

Rules:

- TaskResult must link back to the task and runner lease.
- Knowledge results must cite SourceMaterial or other evidence.
- Every TaskResult must include `operatingRuleRefs`, `commonRulesEvaluation`, and `qualityEvaluation`. Common rule failures must feed back into `qualityEvaluation` and route to retry, repair, escalation, or human acceptance.
- Finishing a task should not automatically mark KnowledgeItem as verified.
- The robot can notify the requester after the task reaches `done`, `blocked`, or `rejected`.

## ProjectManagerReview

Executable project health check produced by the project-scoped Project Manager Agent.

It is not a meeting note or chat summary. It is the system record that proves the Project Manager Agent inspected project state, risks, decisions, notifications, runners, and next actions.

Key fields:

- reviewId
- projectId
- projectManagerAgent
- actor
- status
- taskCount
- openTaskCount
- runnerCount
- riskCount
- decisionCount
- notificationRefs
- followupTaskRefs

Rules:

- Every active project should have recurring `ProjectManagerReview` records.
- A review with `blocked`, `needs_decision`, or `at_risk` status must create notification records for the responsible Project Manager Agent and, when human confirmation is required, the human Owner/reviewer.
- `--create-followup` creates an executable ProjectTask for the Project Manager Agent instead of leaving the risk in a report.
- Project status questions should prefer the latest ProjectManagerReview and project records over chat memory.
- ProjectManagerReview does not replace Product, Design, Development, Test, Operations, Knowledge Engineering, or Knowledge Query output.

## RoleOperatingReview

Executable role operating-system readiness check.

It verifies that a role has a machine-readable spec, role card, local Codex skill, skill pack, input/output contract, workflow, acceptance checks, output quality evaluation template, handoff targets, boundaries, common-rule inheritance, and command templates.

Key fields:

- reviewId
- roleId
- roleName
- projectId
- actor
- defaultAgentId
- status
- gapCount
- warningCount
- taskCount
- openTaskCount
- roleProfileRef
- skillRegistryRef
- skillRefs
- capabilityTags
- guideRef
- commonRulesRef
- qualityEvaluationTemplate
- followupTaskRefs
- notificationRefs

Rules:

- Role specs live in `docs/agent-team/role-operating-specs.json`.
- Project Manager Agent or Scheduler can run `zhenzhi-knowledge agent role-check --role <role-id>`.
- A failed role check should create a repair `ProjectTask` when `--create-followup` is used.
- Role-specific docs inherit common operating rules; they must not duplicate common rules.
- A role system is ready only when docs, local skill, machine-readable spec, workflow, handoff, acceptance, output quality evaluation, audit, and tests/evals are aligned.

## OperatingRuleIssue

Track a problem, conflict, excessive cost, missing guardrail, or improvement proposal in the common Agent operating rules.

It prevents rule changes from happening only in chat or as unreviewed document edits.

Key fields:

- issueId
- ruleId
- reporter
- owner
- status
- scope
- projectId
- sourceRef
- reviewTaskRef

Rules:

- Common operating rules are recorded in `docs/agent-team/common-agent-operating-rules.md`.
- If a rule is unreasonable or harmful, create an `OperatingRuleIssue` with `zhenzhi-knowledge agent-rules issue`.
- Creating an issue must also create a governance `ProjectTask` assigned to the knowledge steward / knowledge engineering owner.
- A rule change is complete only after rules docs, Agent Team guide, audit records, test/eval coverage, and affected-Agent notifications are updated.
- Role-specific docs should reference common rules instead of copying them.

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

## ActorContext

Runtime context for any actor that interacts with the AI-native OS.

Actor can be a human employee, company-level Agent, project-scoped Agent, Agent Ring Runner, Feishu/Lark bot, local Codex / Claude workbench, or another approved execution surface.

Key fields:

- actorId
- actorType
- displayName
- defaultProject
- currentProject
- allowedProjects
- allowedKnowledgeScopes
- notificationPreferences
- outputPreference
- preferredTools
- capabilities
- source
- memoryPolicy
- lastSeenAt

Rules:

- ActorContext is runtime context, not reusable truth.
- It tells the scheduler who is acting, what they can access, how they prefer output, and which memory layers should be loaded into a Context Pack.
- ActorContext must not store secrets.
- ActorContext may be derived from Agent or AgentRunner records when an explicit actor file does not exist.
- Context Packs should include ActorContext for the assignee or lease owner when available.

## ActorFeedback

Feedback from an actor about an Agent output, task result, workflow, answer, or operating experience.

Key fields:

- feedbackId
- actorId
- actorContextRef
- targetAgent
- projectId
- taskId
- resultRef
- rating
- feedbackType
- impact
- source
- status
- evidenceRefs
- linkedTask
- improvementRefs
- evalCaseRefs
- memoryPolicy

Rules:

- ActorFeedback is not reusable knowledge by itself.
- Negative or improvement feedback against a TaskResult should trigger AgentImprovementProposal and EvalCase generation.
- Feedback without a TaskResult should create a follow-up ProjectTask when it belongs to a project.
- Reusable conclusions must be promoted through KnowledgeItem, Skill, EvalCase, workflow, or guide review before becoming project or company memory.

## MemoryPromotionRule

Operating rule for moving information between memory layers.

Layer model:

- company memory: reviewed reusable knowledge, shared Skills, shared EvalCases, and operating guide updates.
- project memory: project goals, tasks, decisions, source materials, task results, and project-scoped lessons.
- task memory: current task input, evidence, output, quality evaluation, and handoff state.
- actor context: identity, permission, preference, current work context, and feedback.

Rules:

- Actor context does not automatically become project or company knowledge.
- Project memory can be promoted to company memory only when it is reusable beyond the project and has passed review.
- Actor feedback can trigger improvement proposals, but the reusable conclusion must be reviewed separately.
- Personal preferences can influence output formatting and notification choices, but must not override security, permission, evidence, or review gates.

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

## SkillAsset

Reusable Agent capability asset. A SkillAsset describes a repeatable role capability, prompt workflow, operating checklist, local skill package, or Agent Workbench skill that can be assigned to Agents and evaluated over time.

SkillAsset is different from ToolAsset:

- ToolAsset describes an executable tool or integration.
- SkillAsset describes how an Agent should perform a capability.
- A SkillAsset may depend on ToolAssets, but tool invocation and skill reuse are governed separately.

Key fields:

- skillId
- owner
- description
- version
- status
- scope
- projectId
- riskLevel
- inputContract
- outputContract
- evalCaseRefs
- allowedAgents
- allowedProjects
- rolloutState
- reusePolicy
- sourceRef
- lastEvaluatedAt
- lastPromotedAt
- rollbackRef

Rules:

- Draft skills are not company-wide defaults.
- Company-wide reuse requires review, eval evidence, owner approval, and versioned rollout.
- Project-private skills may be used inside a project but must not silently become company standards.
- Skill changes that affect role behavior must update the company Agent Team guide.

## KnowledgeItem

Reusable business or engineering knowledge.

Types:

- fact
- decision
- lesson
- learning_note
- skill_note
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

Reference to original input. The original may live in Git, cloud drive, chat, meeting notes, customer folders, public websites, public account articles, video/audio platforms, package storage, or object storage.

Key fields:

- sourceId
- sourceType
- materialType
- sourceRef
- storageRef
- originUrl
- title
- author
- publisher
- publishedAt
- contentHash
- mimeType
- size
- license
- extractionTool
- extractionStatus
- transcriptRef
- owner
- sensitivity
- projectId
- summary
- extractedKnowledge

Supported materialType values:

- `meeting_note`
- `chat_message`
- `customer_document`
- `project_document`
- `web_page`
- `public_account_article`
- `video`
- `audio`
- `pdf`
- `office_document`
- `image`
- `screenshot`
- `package`
- `binary`
- `model_file`
- `dataset`
- `repo_document`
- `agent_run`

SourceMaterial is not reusable knowledge by itself. Searchable KnowledgeItem records must be extracted from it, reviewed, and linked back by `sourceRef`.

SourceMaterial handling:

- Raw meeting notes, documents, chat messages, and files are registered here first.
- Store original URL, storage reference, content hash, permission scope, and extraction status when available.
- For Feishu meeting notes, preserve the Feishu URL/token, title, submitter, project, and snapshot/export path if the API can read it.
- Summaries are allowed as metadata, but reusable conclusions belong in KnowledgeItem and must cite this SourceMaterial.

## NotificationRecord

Track important bot notifications.

Key fields:

- notificationId
- taskId
- projectId
- recipient
- channel
- messageType
- status
- sentAt
- failureReason
- deliveredBy
- deliveryRef
- sourceMessageRef

Delivery rules:

- New notifications start as `pending`.
- Bot, Agent Ring, or temporary runner pulls pending notifications via CLI/API.
- Successful delivery changes status to `sent` and records `sentAt`, `deliveredBy`, and `deliveryRef`.
- Failed delivery changes status to `failed` and records `failureReason`.
- Every delivery status change creates AuditLog.

Examples:

- submitter was told material was accepted and assigned.
- assignee was sent a task card.
- requester was told task is done or blocked.

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
- requirementRef
- prdRef
- owner
- status
- impactLevel
- impactAreas
- context
- options
- tradeoffs
- recommendation
- deadline
- decision
- rationale
- affectedObjects

## Requirement

Durable product or business need.

Key fields:

- requirementId
- projectRef
- title
- summary
- submitter
- owner
- decisionOwner
- sourceRefs
- status
- sensitivity
- requirementStateRef
- prdRefs
- currentPrdRef
- decisionRefs
- acceptanceCriteriaRefs
- taskRefs
- impactReviewRefs
- auditRefs

## RequirementState

Field-level clarity snapshot for a Requirement.

Key fields:

- requirementStateId
- requirementRef
- version
- fields
- missingFields
- needsApprovalFields
- evidenceClaims
- inferenceClaims
- assumptionClaims
- decisionNeededClaims
- clarificationRounds
- qualityGate

## ClarificationRound

Product Manager Agent Socratic clarification record.

Key fields:

- roundId
- requirementRef
- agentRef
- questionRefs
- triggerFields
- recipient
- status
- answerRefs
- statePatchSummary
- auditRefs

## PRDDocument

Versioned product requirement document generated from RequirementState.

Key fields:

- prdId
- requirementRef
- projectRef
- version
- status
- authorAgent
- reviewer
- owner
- sourceRefs
- requirementStateSnapshotRef
- positioning
- marketPositioning
- businessModel
- workflows
- requirements
- scope
- nonGoals
- metrics
- risks
- openDecisions
- acceptanceCriteriaRefs
- evidenceSection
- inferenceSection
- assumptionSection
- decisionNeededSection
- qualityGate
- supersedesPrdRef
- supersededByPrdRef
- auditRefs

## AcceptanceCriteria

Observable acceptance unit linked to Requirement, PRD, task, and tests.

Key fields:

- criteriaId
- requirementRef
- prdRef
- taskRef
- criteriaType
- description
- observableSignal
- verificationMethod
- testCaseRefs
- owner
- status
- sourceRefs
- auditRefs

## ImpactReview

Trace record for PRD or criteria changes after downstream work exists.

Key fields:

- impactReviewId
- requirementRef
- fromPrdRef
- toPrdRef
- changedFields
- affectedTaskRefs
- affectedDesignRefs
- affectedTestRefs
- affectedResultRefs
- affectedDecisionRefs
- riskSummary
- recommendedActions
- owner
- status
- notificationRefs
- auditRefs

## DiscussionSession

Round-based Agent discussion session controlled by the central scheduler.

Key fields:

- discussionId
- projectId
- requester
- facilitatorAgent
- participantAgents
- relatedTaskId
- topic
- status
- currentRound
- maxRounds
- humanVisible
- turnRefs
- summaryRef
- decisionRefs
- followupTaskRefs
- notificationRefs

## DiscussionTurn

One Agent's role-specific contribution to a discussion.

Key fields:

- turnId
- discussionId
- projectId
- agentId
- role
- status
- stance
- concerns
- recommendations
- evidenceRefs

## DiscussionSummary

Project Manager Agent summary for a discussion session.

Key fields:

- summaryId
- discussionId
- projectId
- facilitatorAgent
- status
- consensus
- decision
- openQuestions
- turnRefs

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

## AgentImprovementProposal

Draft improvement record generated when an Agent delivery fails quality evaluation, is blocked, or is rejected by human / project-manager acceptance.

Key fields:

- proposalId
- agentId
- projectId
- taskId
- resultRef
- trigger
- failureReasons
- reuseScope
- evalCaseRefs
- recommendedActions
- reviewOwner

Rules:

- This object is not reusable truth. It is a repair and learning work item.
- `reuseScope: company` can become a shared Skill, EvalCase, workflow rule, or guide update after review.
- `reuseScope: project` stays inside the project unless Knowledge Engineering Agent extracts a company-level pattern.
- Every proposal must point to a TaskResult and at least one source reason.
- If it changes Agent roles, Skills, workflows, Scheduler, Agent Ring, or knowledge policy, the Agent Team operating guide update gate applies.

## AgentCapabilityReport

Capability metrics generated from TaskResult quality evaluations and Agent improvement proposals.

Key fields:

- reportId
- agentId
- projectId
- period
- taskResultCount
- passedCount
- failedCount
- firstPassRate
- averageScore
- topFailureReasons
- improvementRefs

Rules:

- Reports are management/index artifacts, not independent truth.
- Agent Ring, Project Manager Agent, and role Agents use them to prioritize Skill, EvalCase, and workflow improvements.
- Reports must be regenerated from TaskResult and AgentImprovementProposal evidence.

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

## KnowledgeGraphEdge

Normalized relationship record derived from frontmatter, body fields, index records, TaskResult evidence, AgentRun usage, Policy rules, ReviewRecord output, ConflictRecord impact, and AuditLog changes.

Key fields:

- edgeId
- fromRef
- relation
- toRef
- sourceRef
- evidenceRefs
- confidence
- status
- owner
- generatedBy
- observedAt
- updatedAt
- sensitivity
- auditRefs

Supported relation examples:

- `hasTask`
- `usesSource`
- `assignedTo`
- `resolves`
- `produced`
- `derivedFrom`
- `supportedBy`
- `used`
- `implementedIn`
- `referencesCode`
- `affects`
- `governs`
- `requiresApprovalFor`
- `evaluates`
- `recordsChangeTo`

Rules:

- Edges are derived from managed records or explicitly declared by reviewed records.
- Edges are not standalone truth and must point back to sourceRef or evidenceRefs when they carry operational meaning.
- Sensitive edges inherit the strictest sensitivity of either endpoint or evidence.
- Edges involving secret values are prohibited.
- Automated extraction may create `draft` or `observed` edges; verified operational meaning follows linked object review status.
- Edge creation, deletion, or material impact changes must be auditable.

## GraphSnapshot

Regenerated export artifact for visualization, API sync, impact review, or offline audit.

Key fields:

- snapshotId
- generatedAt
- generator
- scope
- includedTypes
- nodeCount
- edgeCount
- sourceIndexRef
- outputRef
- sensitivity
- auditRef

Rules:

- Snapshot files are read-only exports, not durable truth.
- Snapshots must not contain secret values.
- Customer-confidential snapshots require project or customer scope.
- Source records and AuditLog remain the durable record.
