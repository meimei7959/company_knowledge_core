# AI Native OS Development Handoff

This handoff tells Development Agent what to build so the complete product goal can be reached.

Development Agent must treat [Requirement Tree](requirement-tree.md) as the product requirement source and [Functional Requirements](requirements.md) as the implementation requirement source. Do not treat module names or task lists as product requirements unless they trace back to a user scenario and business requirement.

## Engineering Position

Do not rebuild the current core. Build product layers on top of the existing central processor.

Preserve:

- current ProjectTask / KnowledgeTask / TaskResult lifecycle;
- AgentRunner registry and lease model;
- Feishu Agent Hub entry;
- SourceMaterial-first rule;
- Knowledge Review and approval rules;
- AuditLog and NotificationRecord;
- Agent Ring external boundary.

## New Product Capabilities To Implement

### DEV-001 Requirement Domain

Implement durable objects and APIs for:

- Requirement.
- RequirementState.
- PRDDocument.
- AcceptanceCriteria.
- RequirementDecision.

Required behaviors:

- create from Feishu/API/Project Console;
- update field-level clarity states;
- link SourceMaterial, Project, PRD, ProjectTasks, Decisions;
- prevent approval without owner and acceptance criteria;
- record audit on writes.

Mapped requirements:

- ANOS-REQ-010 to ANOS-REQ-016.
- ANOS-REQ-020 to ANOS-REQ-024.

### DEV-002 Product Manager Agent Workflow

Implement workflow support for Product Manager Agent:

- load Product Manager Agent `skillRefs`: `requirement-clarification` and `prd-scope-definition`;
- produce clarification rounds;
- store questions and answers;
- update RequirementState;
- generate PRDDocument;
- generate ProjectTask proposals;
- create Decision request when required.

Mapped requirements:

- ANOS-REQ-011 to ANOS-REQ-016.
- ANOS-REQ-020 to ANOS-REQ-023.
- ANOS-REQ-056.

### DEV-003 Web Product Console

Implement console surfaces:

- Requirement Center.
- PRD and Decision Center.
- Project Console.
- Agent Team Manager.
- Scheduler and Task Center.
- Agent Ring Console.
- Result Center.
- Knowledge Core.
- Review Center.
- Tool and Skill Registry.
- Quality Dashboard.
- Notification Center.
- Admin and Governance Console.
- Operations and Feedback Center.

Mapped requirements:

- ANOS-REQ-030 to ANOS-REQ-034.
- ANOS-REQ-040 to ANOS-REQ-045.
- ANOS-REQ-060 to ANOS-REQ-063.
- ANOS-REQ-110 to ANOS-REQ-142.

### DEV-004 Agent Role Runtime Contracts

Implement durable input/output contracts for:

- Project Manager Agent.
- Product Manager Agent.
- Knowledge Query Agent.
- Knowledge Engineering Agent.
- Design Agent.
- Development Agent.
- Test Agent.
- Operations Agent.
- Knowledge Steward Agent.
- Knowledge Review Agent.
- Knowledge Ops Agent.

Required behaviors:

- role profile validation;
- required skill validation;
- allowed tool/scope validation;
- handoff contract validation;
- role health check;
- capability report.

Mapped requirements:

- ANOS-REQ-040 to ANOS-REQ-045.
- ANOS-REQ-070 to ANOS-REQ-073.

### DEV-005 Scheduler Productization

Extend existing scheduler to support:

- requirement/product discovery taskRuntime;
- design taskRuntime;
- test taskRuntime;
- operations taskRuntime;
- acceptance path by task type;
- stale lease dashboard;
- retry/cancel/escalation UI;
- owner-visible blocked state.

Mapped requirements:

- ANOS-REQ-050 to ANOS-REQ-056.

### DEV-006 Agent Ring Console And Runner Safety

Implement runner UI/API for:

- runner registration;
- heartbeat and load;
- current leases;
- task history;
- tool/repo/data scopes;
- manual handoff;
- stale lease repair.

Mapped requirements:

- ANOS-REQ-060 to ANOS-REQ-063.

### DEV-007 Review Center

Implement unified Review Center for:

- knowledge review;
- product decision review;
- requirement approval;
- tool approval;
- skill approval;
- permission approval;
- release gate review.

Mapped requirements:

- ANOS-REQ-090 to ANOS-REQ-093.
- ANOS-REQ-100 to ANOS-REQ-102.

### DEV-008 Skill Registry

Implement SkillAsset lifecycle:

- register skill package;
- version skill;
- attach tests;
- approval route;
- allowed Agents;
- rollout status;
- rollback path;
- usage history.

Mapped requirements:

- ANOS-REQ-045.
- ANOS-REQ-101.
- ANOS-REQ-102.

### DEV-009 Quality And Evaluation

Implement metrics and eval:

- task throughput;
- completion time;
- acceptance pass rate;
- retry rate;
- blocked/stale rate;
- Agent quality;
- requirement quality;
- knowledge quality;
- EvalCase / EvalRun release gates.

Mapped requirements:

- ANOS-REQ-110 to ANOS-REQ-114.

### DEV-010 Notification And Operations

Implement:

- readable notifications;
- delivery tracking;
- failure repair;
- user feedback;
- operations metrics;
- launch operations record;
- improvement task creation.

Mapped requirements:

- ANOS-REQ-120 to ANOS-REQ-122.
- ANOS-REQ-140 to ANOS-REQ-142.

### DEV-011 Admin And Governance

Implement:

- organization settings;
- user and role permissions;
- Agent enable/disable;
- runner enable/disable;
- tool/skill enable/disable;
- integration settings;
- secretRef policy;
- retention, backup, restore status;
- audit search.

Mapped requirements:

- ANOS-REQ-130 to ANOS-REQ-133.

### DEV-012 API And Gateway

Implement validated API contracts for:

- Requirement.
- PRDDocument.
- Project.
- ProjectTask.
- Agent.
- Runner.
- TaskResult.
- Review.
- Knowledge query.
- Notification.
- Metrics.
- Admin.

Mapped requirements:

- ANOS-REQ-150 to ANOS-REQ-152.

## Data Model Additions

### Requirement

Required fields:

- requirementId.
- title.
- projectRef.
- submitter.
- owner.
- sourceRefs.
- status.
- sensitivity.
- requirementStateRef.
- prdRefs.
- taskRefs.
- decisionRefs.
- acceptanceCriteriaRefs.
- createdAt / updatedAt.
- auditRefs.

### RequirementState

Required fields:

- requirementStateId.
- requirementRef.
- targetUser.
- userProblem.
- usageScenario.
- currentAlternative.
- valueProposition.
- marketPosition.
- businessModel.
- scope.
- nonGoals.
- constraints.
- successMetric.
- acceptanceCriteriaSummary.
- evidenceRefs.
- assumptions.
- missingFields.
- needsApprovalFields.

### PRDDocument

Required fields:

- prdId.
- requirementRef.
- version.
- status.
- authorAgent.
- owner.
- sourceRefs.
- problem.
- targetUsers.
- scenarios.
- goals.
- nonGoals.
- positioning.
- marketPositioning.
- businessModel.
- workflows.
- requirements.
- metrics.
- risks.
- openDecisions.
- acceptanceCriteriaRefs.
- taskProposalRefs.

### AcceptanceCriteria

Required fields:

- criteriaId.
- requirementRef.
- prdRef.
- taskRef optional.
- type.
- description.
- observableSignal.
- testCaseRefs.
- owner.
- status.

### SkillAsset

Required fields:

- skillId.
- name.
- version.
- owner.
- sourcePath.
- allowedAgents.
- allowedProjects.
- riskLevel.
- tests.
- status.
- rolloutState.
- rollbackPath.
- auditRefs.

## API Contract Principles

- Writes require actor, permission, object type, and audit.
- Responses use human-readable labels before raw ids.
- Every state transition validates allowed previous state.
- Every object can return related source, task, result, decision, review, notification, audit.
- Errors include user-facing reason and developer-facing code.

## Engineering Completion Definition

Development is complete only when:

- all mapped requirements have implementation;
- all tests in `test-cases.md` pass or have accepted documented exception;
- all launch gates in `acceptance-checklist.md` pass;
- no critical object can bypass owner, source, evidence, review, permission, or audit rules;
- web/API/Feishu/CLI use same state contracts;
- release notes list migrations, permissions, rollout, rollback, and known risks.
