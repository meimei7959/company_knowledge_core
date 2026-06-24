# Company Knowledge Core Tasks

Project-scoped task cards for the Agent Hub and knowledge engineering central processor project.

Tasks that require distributed execution should be matched to Agent Ring runners through the scheduler protocol.

## Current Initialization

- [Company Knowledge Core project initialization](project-init-company-knowledge-core.md) - done
- [Project initialization closeout](kt-project-initialization-closeout.md) - done

## Next Phase Acceptance Tasks

These four tasks define the next user acceptance scope. They should be completed before the next phase is presented for human验收.

- [Production closed-loop acceptance](kt-production-closed-loop-acceptance.md) - pending
- [Agent Workbench integration package](kt-agent-workbench-integration-package.md) - pending
- [Universal material ingest pipeline](kt-universal-material-ingest.md) - pending
- [Knowledge graph phase one](kt-knowledge-graph-phase-one.md) - pending

## Mature AI Native OS Master Tasks

These six master tasks upgrade the project from a working Agent Hub / scheduler / knowledge core into a mature AI-native operating system. Each master task must land in executable workflow, protocol, validation, notification, evaluation, audit, or harness behavior, not only documentation.

Roadmap: [Mature AI Native Operating System Roadmap](../../../docs/strategy/mature-ai-native-operating-system-roadmap.md)

- [Execution spine](kt-os-execution-spine.md) - done
- [Digital worker and capability registry](kt-os-digital-worker-capability-registry.md) - done
- [Runner distributed execution network](kt-os-runner-execution-network.md) - done
- [Policy and quality gates](kt-os-policy-quality-gates.md) - done
- [Knowledge governance loop](kt-os-knowledge-governance-loop.md) - done
- [Collaboration and self-improvement loop](kt-os-collaboration-self-improvement.md) - done

### OS Capability Coverage Items

The earlier twelve hardening cards are retained as subsystem coverage items under the six master tasks. Do not execute them as separate parallel initiatives unless a master task explicitly splits one out.

- [Workflow State Machine hardening](kt-os-workflow-state-machine.md) - covered by [Execution spine](kt-os-execution-spine.md)
- [Event Bus and Notification hardening](kt-os-event-notification-bus.md) - covered by [Execution spine](kt-os-execution-spine.md)
- [Agent Directory hardening](kt-os-agent-directory.md) - covered by [Digital worker and capability registry](kt-os-digital-worker-capability-registry.md)
- [Skill Registry lifecycle hardening](kt-os-skill-registry-lifecycle.md) - covered by [Digital worker and capability registry](kt-os-digital-worker-capability-registry.md)
- [Tool Registry and persistence policy hardening](kt-os-tool-registry-policy.md) - covered by [Digital worker and capability registry](kt-os-digital-worker-capability-registry.md)
- [Runner Fabric hardening](kt-os-runner-fabric.md) - covered by [Runner distributed execution network](kt-os-runner-execution-network.md)
- [Context Pack Engine hardening](kt-os-context-pack-engine.md) - covered by [Runner distributed execution network](kt-os-runner-execution-network.md)
- [Policy Engine hardening](kt-os-policy-engine.md) - covered by [Policy and quality gates](kt-os-policy-quality-gates.md)
- [Evaluation Engine hardening](kt-os-evaluation-engine.md) - covered by [Policy and quality gates](kt-os-policy-quality-gates.md)
- [Knowledge Core governance hardening](kt-os-knowledge-core-governance.md) - covered by [Knowledge governance loop](kt-os-knowledge-governance-loop.md)
- [Agent Collaboration Protocol hardening](kt-os-agent-collaboration-protocol.md) - covered by [Collaboration and self-improvement loop](kt-os-collaboration-self-improvement.md)
- [Self-Improvement Pipeline hardening](kt-os-self-improvement-pipeline.md) - covered by [Collaboration and self-improvement loop](kt-os-collaboration-self-improvement.md)

## Next Central Processor Tasks

- [PostgreSQL operational store migration](kt-postgresql-operational-store.md) - done
- [Documentation entry alignment](kt-doc-entry-alignment.md) - done
- [Project status dashboard and Feishu project detail card](kt-project-status-dashboard.md) - done
- [Runner and project Agent registry hardening](kt-runner-agent-registry-hardening.md) - done
- [Task lifecycle notification loop](kt-task-notification-loop.md) - done
- [Knowledge capture to review pipeline](kt-knowledge-capture-review-pipeline.md) - done
- [Knowledge ingest orchestration with evaluation and retry](kt-knowledge-ingest-orchestration-eval-retry.md) - done
- [Review outcome to publisher/indexer closure](kt-review-outcome-publisher-closure.md) - done
- [Agent Workbench central contract tests](kt-agent-workbench-contract-tests.md) - done
- [Deployment and observability operations](kt-deployment-observability-ops.md) - done

## Coverage Review

- [Task Coverage Review](task-coverage-review.md) - draft

## AI Native OS Execution Queue

Project Manager Agent accepted the complete product package and split it into execution tasks.

- [PM handoff execution](kt-ai-native-os-project-manager-handoff.md) - done
- [Requirement and PRD domain implementation](kt-ai-native-os-dev-requirement-prd-domain.md) - pending
- [Product console surfaces](kt-ai-native-os-dev-console-surfaces.md) - pending
- [Scheduler, runner, and result execution spine](kt-ai-native-os-dev-scheduler-runner-result.md) - pending
- [Governance, quality, notification, admin, and API implementation](kt-ai-native-os-dev-governance-quality-ops.md) - pending
- [Console experience design](kt-ai-native-os-design-console-experience.md) - pending
- [Test and acceptance suite](kt-ai-native-os-test-acceptance-suite.md) - pending
- [Knowledge governance mapping](kt-ai-native-os-knowledge-governance-mapping.md) - pending
- [Review and approval routing](kt-ai-native-os-review-approval-routing.md) - pending
- [Operations launch readiness](kt-ai-native-os-ops-launch-readiness.md) - pending

## Completed Foundation Tasks

Core architecture and protocol:

- [Agent Ring protocol integration handoff](kt-agent-ring-protocol-integration.md)
- [Project context portability and sync design](kt-project-context-sync.md)

Feishu, DeepSeek, and routing:

- [Feishu DeepSeek intent router](kt-feishu-deepseek-router.md)
- [Feishu routing safety gate](kt-feishu-routing-safety-gate.md)
- [Feishu card workflow closure](kt-feishu-card-workflow-closure.md)
- [Feishu to Agent Ring task dispatch](kt-feishu-agent-ring-dispatch.md)
- [DeepSeek routing observability and evals](kt-deepseek-observability-evals.md)

Testing and access control:

- [Agent Ring stub runner tests](kt-agent-ring-stub-runner-tests.md)
- [Access credential and secretRef flow](kt-access-credential-secret-flow.md)
- [落地分层 Agent 行为规范和运行时校验](agent-runtime-rules-layering.md)
- [PM review implementation evidence.](kt-autoexec-dev-pm-autopilot-runtime-handoff.md)
- [PM review worker runtime evidence.](kt-autoexec-dev-agent-worker-runtime-handoff.md)
- [PM review state flow evidence.](kt-autoexec-dev-state-result-flow-handoff.md)
- [PM review workbench data evidence.](kt-autoexec-dev-workbench-data-api-handoff.md)
- [Retry task output for kt-ai-native-os-tech-solution-desktop-workbench-console](kt-ai-native-os-tech-solution-desktop-workbench-console-retry.md)
- [Retry task output for kt-ai-native-os-impl-requirement-prd-domain](kt-ai-native-os-impl-requirement-prd-domain-retry.md)
- [Retry task output for kt-ai-native-os-impl-scheduler-runner-result](kt-ai-native-os-impl-scheduler-runner-result-retry.md)
- [Retry task output for kt-ai-native-os-impl-governance-quality-ops-api](kt-ai-native-os-impl-governance-quality-ops-api-retry.md)
- [Retry task output for kt-ai-native-os-impl-desktop-workbench-slice0](kt-ai-native-os-impl-desktop-workbench-slice0-retry.md)
- [ready for PM review](kt-ai-native-os-repair-taskresult-metadata-migration-handoff.md)
- [Resolve blocked task handoff for kt-ai-native-os-dev-automation-hub-hard-capabilities](kt-ai-native-os-dev-automation-hub-hard-capabilities-blocker.md)
- [RT-TECH-001 Requirement Tree Technical Solution](kt-ai-native-os-rt-pm-coverage-matrix-handoff.md)
- [Retry task output for kt-ai-native-os-rt-product-review-technical-solution](kt-ai-native-os-rt-product-review-technical-solution-retry.md)
- [RT-PROD-REVIEW-001 Technical Solution Product Review](kt-ai-native-os-rt-tech-solution-requirement-tree-handoff.md)
- [Resolve blocked task handoff for kt-ai-native-os-rt-test-object-model-slice](kt-ai-native-os-rt-test-object-model-slice-blocker.md)
- [AI Native OS RT development repair - object model slice](kt-ai-native-os-rt-dev-object-model-slice-repair.md)
- [AI Native OS RT test regression - object model repair](kt-ai-native-os-rt-test-object-model-slice-regression.md)
- [Test Agent should run independent acceptance tests for RT object model validation and CLI shape.](kt-ai-native-os-rt-dev-object-model-slice-handoff.md)
- [Test Agent should rerun object model regression and confirm both prior blockers are closed.](kt-ai-native-os-rt-dev-object-model-slice-repair-handoff.md)
- [Project Manager Agent may proceed to PM acceptance for the Requirement Tree object model slice.](kt-ai-native-os-rt-test-object-model-slice-regression-handoff.md)
- [agent.company.test should execute kt-ai-native-os-rt-test-import-validation-slice regression and acceptance checks.](kt-ai-native-os-rt-dev-import-validation-slice-handoff.md)
- [Project Manager Agent may proceed to PM acceptance for Requirement Tree import and validation slice.](kt-ai-native-os-rt-test-import-validation-slice-handoff.md)
- [Hand off to agent.company.test for kt-ai-native-os-rt-test-task-queue-compiler-slice regression.](kt-ai-native-os-rt-dev-task-queue-compiler-slice-handoff.md)
- [Project Manager Agent may proceed to PM acceptance for Requirement Tree task queue compiler slice.](kt-ai-native-os-rt-test-task-queue-compiler-slice-handoff.md)
- [Hand off to agent.company.test for kt-ai-native-os-rt-test-context-pack-slice regression.](kt-ai-native-os-rt-dev-context-pack-slice-handoff.md)
- [Project Manager Agent may proceed to PM acceptance for Requirement Tree context pack slice.](kt-ai-native-os-rt-test-context-pack-slice-handoff.md)
- [Hand off to agent.company.test for kt-ai-native-os-rt-test-workbench-slice regression.](kt-ai-native-os-rt-dev-workbench-slice-handoff.md)
- [Project Manager Agent may proceed to PM acceptance for Requirement Tree workbench slice.](kt-ai-native-os-rt-test-workbench-slice-handoff.md)
- [kt-ai-native-os-rt-test-existing-work-backfill](kt-ai-native-os-rt-dev-existing-work-backfill-handoff.md)
- [Project Manager Agent may proceed to final PM acceptance for the Requirement Tree systemized traceability chain.](kt-ai-native-os-rt-test-existing-work-backfill-handoff.md)
- [AI Native OS Requirement Tree final product acceptance](kt-ai-native-os-rt-product-final-acceptance.md)
- [Run Product Manager scope review and then release Development technical solution tasks.](kt-ai-native-agent-v1-product-requirement-structure-handoff.md)
- [Retry task output for kt-ai-native-agent-v1-product-review-technical-solutions](kt-ai-native-agent-v1-product-review-technical-solutions-retry.md)
- [Release Development technical solution tasks for V1 runtime slices.](kt-ai-native-agent-v1-product-scope-review-handoff.md)
- [Review technical solution and release implementation task.](kt-ai-native-agent-v1-tech-profile-skill-registry-handoff.md)
- [Review technical solution and release implementation task.](kt-ai-native-agent-v1-tech-local-router-session-registry-handoff.md)
- [Review technical solution and release implementation task.](kt-ai-native-agent-v1-tech-agent-runtime-orchestrator-handoff.md)
- [Review technical solution and release implementation task.](kt-ai-native-agent-v1-tech-worktree-console-harness-handoff.md)
- [Release Development technical solution tasks for V1 runtime slices.](kt-ai-native-agent-v1-product-review-technical-solutions-retry-handoff.md)
- [V1 acceptance development task - Local Router runtime proof](kt-v1-local-router-runtime-acceptance-dev.md)
- [V1 acceptance test task - Local Router runtime proof](kt-v1-local-router-runtime-acceptance-test.md)
- [Run next V1 acceptance stage.](kt-ai-native-agent-v1-dev-implementation-handoff.md)
- [Run next V1 acceptance stage.](kt-ai-native-agent-v1-test-closed-loop-acceptance-handoff.md)
- [Run next V1 acceptance stage.](kt-ai-native-agent-v1-pm-product-final-acceptance-handoff.md)
- [AI Native Agent V1 Product Final Acceptance](kt-ai-native-agent-v1-product-final-acceptance.md)
- [Run next V1 acceptance stage.](kt-ai-native-agent-v1-product-final-acceptance-handoff.md)
- [Plan V2 multi-device Hub and desktop packaging work.](kt-ai-native-agent-v1-product-final-acceptance-handoff-02.md)
- [Run next V1 acceptance stage.](kt-v1-local-router-runtime-acceptance-dev-handoff.md)
- [Run next V1 acceptance stage.](kt-v1-local-router-runtime-acceptance-test-handoff.md)
- [V1 工作台 Codex 风格中文设计方案](kt-v1-workbench-codex-style-design.md)
- [研发实现 V1 工作台 Codex 风格中文界面](kt-v1-workbench-codex-style-dev.md)
- [产品评审 V1 工作台 Codex 风格设计](kt-v1-workbench-codex-style-product-review.md)
- [测试验收 V1 工作台 Codex 风格中文界面](kt-v1-workbench-codex-style-test.md)
- [产品最终验收 V1 工作台 Codex 风格中文界面](kt-v1-workbench-codex-style-product-final-acceptance.md)
- [项目经理最终验收 V1 工作台 Agent 体系执行链路](kt-v1-workbench-codex-style-pm-final-acceptance.md)
- [Retry task output for kt-v1-workbench-codex-style-product-final-acceptance](kt-v1-workbench-codex-style-product-final-acceptance-retry.md)
- [Retry task output for kt-v1-workbench-codex-style-pm-final-acceptance](kt-v1-workbench-codex-style-pm-final-acceptance-retry.md)
- [修复 V1 工作台用户可读中文文案](kt-v1-workbench-user-copy-polish.md)
- [测试验收 V1 工作台用户可读中文文案](kt-v1-workbench-user-copy-polish-test.md)
- [产品复验 V1 工作台用户可读中文文案](kt-v1-workbench-user-copy-polish-product-review.md)
- [Retry task output for kt-v1-workbench-user-copy-polish-test](kt-v1-workbench-user-copy-polish-test-retry.md)
- [修复 V1 工作台回归阻断的审计日志空白](kt-v1-workbench-user-copy-polish-log-whitespace-repair.md)
- [系统性修复审计日志尾随空格](kt-audit-log-trailing-whitespace-systemic-fix.md)
- [测试验收审计日志尾随空格系统修复](kt-audit-log-trailing-whitespace-systemic-fix-test.md)
- [实现工作台新建项目入口](kt-v1-workbench-project-create-entry.md)
- [阶段二：同事电脑接入同一项目中枢产品需求包](kt-v2-colleague-runner-product-requirements.md)
- [阶段二：同事接入工作台页面设计规范](kt-v2-colleague-runner-design-spec.md)
- [阶段二：多设备 Runner 接入技术方案](kt-v2-colleague-runner-architecture-solution.md)
- [阶段二：产品经理复核架构方案](kt-v2-colleague-runner-product-architecture-review.md)
- [阶段二：同事接入与多设备路由研发实现](kt-v2-colleague-runner-development.md)
- [阶段二：同事接入多设备闭环测试](kt-v2-colleague-runner-test.md)
- [阶段二：同事接入工作台 UI 与交互设计返工](kt-v2-colleague-runner-ui-interaction-design-revision.md)
- [阶段二：同事接入工作台产品信息架构](kt-v2-colleague-runner-product-information-architecture.md)
- [阶段二：产品 IA 与 UI/交互设计对技术方案影响复核](kt-v2-colleague-runner-architecture-ia-design-impact-review.md)
- [阶段二：产品经理复核 IA/UI 后技术方案](kt-v2-colleague-runner-product-architecture-review-after-ia-ui.md)
- [阶段二回归：主界面路径脱敏与多设备闭环复测](kt-v2-colleague-runner-test-regression-visible-path.md)
- [阶段二：同事接入多设备协作产品验收](kt-v2-colleague-runner-product-final-acceptance.md)
- [阶段二：真实同事电脑双 host 验收](kt-v2-colleague-runner-real-dual-host-acceptance.md)
- [修复 maintenance 任务来源追溯校验缺失](kt-20260623-001.md)
- [修复岗位 Agent 规则对任务来源与 ReceiverReview 机制的直接绑定](kt-20260623-002.md)
- [知识工程评审并沉淀可复用 Skill：软著材料执行与提交包生成](kt-20260624-001.md)
- [项目经理分诊体系问题：billing-lite project entry references missing central project path](kt-20260624-002.md)
