from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .core import (
    Bundle,
    KnowledgeError,
    PMControlLeaseError,
    accept_project_task_result,
    acquire_pm_control_lease,
    apply_knowledge_approval_result,
    apply_knowledge_review_result,
    default_config,
    find_bundle_root,
    finish_task,
    git,
    install_connector,
    load_config,
    make_agent,
    make_project,
    make_skill,
    make_tool,
    invoke_tool,
    list_notifications,
    rebuild_index,
    rebuild_retrieval_index,
    create_conflict,
    create_agent_capability_report,
    create_actor_feedback,
    create_acceptance_criteria,
    create_clarification_round,
    create_discussion_session,
    create_decision_request,
    create_defect,
    create_bugfix_task,
    create_metrics_report,
    create_eval_case,
    create_impact_review,
    create_ops_experiment,
    create_operating_rule_issue,
    create_outcome_slice,
    create_backup,
    disable_governed_asset,
    diagnose_project_task,
    detect_stale,
    discussion_session_status,
    bulk_review,
    cancel_project_task,
    create_project_task,
    create_project_manager_action,
    create_project_launch,
    create_runner_invitation,
    create_tool_registration_request,
    create_workbench_project,
    create_requirement,
    create_requirement_task,
    create_receiver_review,
    create_source_material,
    create_operations_feedback,
    export_api_snapshot,
    export_graph_snapshot,
    finish_project_task,
    finalize_discussion_session,
    generate_prd_document,
    gateway_context,
    graph_impact,
    heartbeat_pm_control_lease,
    list_review_queue,
    pm_control_lease_read_model,
    project_task_status,
    pull_project_task,
    approve_prd_document,
    approve_requirement,
    review_path,
    search_index,
    make_policy,
    publish_knowledge_bundle,
    register_agent_runner,
    register_workbench_tool,
    register_project_agent,
    attach_agent_to_project,
    heartbeat_agent_runner,
    manual_handoff_project_task,
    run_agent_role_operating_check,
    run_project_manager_health_check,
    run_eval_case,
    restore_backup,
    resolve_decision,
    resolve_conflict,
    run_agent_worker,
    run_v1_single_machine_acceptance,
    run_scheduler_autopilot,
    scheduler_workbench_read_model,
    schedule_project_tasks,
    search_audit_logs,
    search_retrieval,
    compile_v1_task_package,
    execute_v1_task_package,
    heartbeat_v1_agent_session,
    list_v1_devices,
    list_v1_agent_sessions,
    mark_notification_delivery,
    register_v1_agent_profile,
    register_v1_device,
    register_v1_agent_session,
    register_v1_skill,
    send_v1_agent_message,
    submit_discussion_turn,
    takeover_pm_control_lease,
    save_config,
    start_task,
    set_project_task_status,
    update_requirement_state,
    validate_bundle,
    validate_skill_registry,
    backfill_requirement_tree_existing_work,
    build_task_fact_view,
    compile_requirement_tree_task_queue,
    promote_requirement_tree_traceability,
    requirement_tree_import_records,
    requirement_tree_workbench_read_model,
    retry_project_task,
    release_pm_control_lease,
    runner_registry_for_workbench,
    submit_runner_registration,
    validate_requirement_tree_records,
    v1_workbench_read_model,
    workbench_project_execution_read_model,
    write_v1_workbench_read_model,
    upsert_actor_context,
)
from .server import serve


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="zhenzhi-knowledge")
    parser.add_argument("--root", default=None, help="knowledge bundle root")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init")
    p_init.add_argument("--user-id", default=os.environ.get("USER", "unknown"))
    p_init.add_argument("--ai-tool", default="codex")
    p_init.add_argument("--agent-id", default=None)
    p_init.add_argument("--remote", default="")

    p_install = sub.add_parser("install")
    p_install.add_argument("--user-id", default=os.environ.get("USER", "unknown"))
    p_install.add_argument("--ai-tool", default="codex")
    p_install.add_argument("--agent-id", default=None)
    p_install.add_argument("--remote", default="")
    p_install.add_argument("--default-project", default="")
    p_install.add_argument("--register-agent", action="store_true")
    p_install.add_argument("--agent-name", default="")
    p_install.add_argument("--purpose", default="local AI development")
    p_install.add_argument("--no-rebuild-index", action="store_true")

    sub.add_parser("status")
    p_profile = sub.add_parser("profile")
    p_profile_sub = p_profile.add_subparsers(dest="profile_command", required=True)
    p_profile_use = p_profile_sub.add_parser("use")
    p_profile_use.add_argument("name")

    p_sync = sub.add_parser("sync")
    p_sync_sub = p_sync.add_subparsers(dest="sync_command", required=True)
    p_sync_sub.add_parser("pull")
    p_sync_sub.add_parser("push")

    p_agent = sub.add_parser("agent")
    p_agent_sub = p_agent.add_subparsers(dest="agent_command", required=True)
    p_agent_register = p_agent_sub.add_parser("register")
    p_agent_register.add_argument("--agent-id", required=True)
    p_agent_register.add_argument("--name", required=True)
    p_agent_register.add_argument("--owner", required=True)
    p_agent_register.add_argument("--tool", default="codex")
    p_agent_register.add_argument("--purpose", required=True)
    p_agent_register.add_argument("--allow-project", action="append", default=[])
    p_agent_report = p_agent_sub.add_parser("report")
    p_agent_report.add_argument("--agent-id", required=True)
    p_agent_report.add_argument("--project", default="")
    p_agent_report.add_argument("--owner", default="system.scheduler")
    p_agent_report.add_argument("--period", default="")
    p_agent_role_check = p_agent_sub.add_parser("role-check")
    p_agent_role_check.add_argument("--role", required=True)
    p_agent_role_check.add_argument("--project", default="")
    p_agent_role_check.add_argument("--actor", default="system.project-manager")
    p_agent_role_check.add_argument("--create-followup", action="store_true")
    p_agent_role_check.add_argument("--no-notify", action="store_true")

    p_actor = sub.add_parser("actor")
    p_actor_sub = p_actor.add_subparsers(dest="actor_command", required=True)
    p_actor_context = p_actor_sub.add_parser("context")
    p_actor_context.add_argument("--actor-id", required=True)
    p_actor_context.add_argument("--type", default="")
    p_actor_context.add_argument("--name", default="")
    p_actor_context.add_argument("--default-project", default="")
    p_actor_context.add_argument("--allow-project", action="append", default=None)
    p_actor_context.add_argument("--scope", action="append", default=None)
    p_actor_context.add_argument("--notify", action="append", default=None)
    p_actor_context.add_argument("--output-preference", default="")
    p_actor_context.add_argument("--source", default="")
    p_actor_context.add_argument("--owner", default="system.scheduler")
    p_actor_feedback = p_actor_sub.add_parser("feedback")
    p_actor_feedback.add_argument("--actor-id", required=True)
    p_actor_feedback.add_argument("--content", required=True)
    p_actor_feedback.add_argument("--target-agent", default="")
    p_actor_feedback.add_argument("--project", default="")
    p_actor_feedback.add_argument("--task", default="")
    p_actor_feedback.add_argument("--result-ref", default="")
    p_actor_feedback.add_argument("--rating", default="")
    p_actor_feedback.add_argument("--type", default="")
    p_actor_feedback.add_argument("--impact", default="")
    p_actor_feedback.add_argument("--evidence-ref", action="append", default=[])
    p_actor_feedback.add_argument("--source", default="")
    p_actor_feedback.add_argument("--owner", default="system.scheduler")

    p_runner = sub.add_parser("runner")
    p_runner_sub = p_runner.add_subparsers(dest="runner_command", required=True)
    p_runner_register = p_runner_sub.add_parser("register")
    p_runner_register.add_argument("--runner-id", required=True)
    p_runner_register.add_argument("--name", required=True)
    p_runner_register.add_argument("--host-type", default="")
    p_runner_register.add_argument("--mode", default="manual")
    p_runner_register.add_argument("--agent", action="append", default=[])
    p_runner_register.add_argument("--capability", action="append", default=[])
    p_runner_register.add_argument("--project", action="append", default=[])
    p_runner_register.add_argument("--repo", action="append", default=[])
    p_runner_register.add_argument("--data-scope", action="append", default=[])
    p_runner_register.add_argument("--ring-version", default="manual-0.1")
    p_runner_heartbeat = p_runner_sub.add_parser("heartbeat")
    p_runner_heartbeat.add_argument("--runner-id", required=True)
    p_runner_heartbeat.add_argument("--status", default="online")
    p_runner_heartbeat.add_argument("--load", default="")
    p_runner_heartbeat.add_argument("--capability", action="append", default=None)
    p_runner_heartbeat.add_argument("--project", action="append", default=None)
    p_runner_list = p_runner_sub.add_parser("list")
    p_runner_list.add_argument("--project", default="")

    p_pm_lease = sub.add_parser("pm-lease")
    p_pm_lease_sub = p_pm_lease.add_subparsers(dest="pm_lease_command", required=True)
    p_pm_status = p_pm_lease_sub.add_parser("status")
    p_pm_status.add_argument("--project", required=True)
    p_pm_acquire = p_pm_lease_sub.add_parser("acquire")
    p_pm_acquire.add_argument("--project", required=True)
    p_pm_acquire.add_argument("--pm-agent", required=True)
    p_pm_acquire.add_argument("--runner-id", default="")
    p_pm_acquire.add_argument("--device-id", default="")
    p_pm_acquire.add_argument("--lease-seconds", type=int, default=900)
    p_pm_acquire.add_argument("--idempotency-key", default="")
    p_pm_heartbeat = p_pm_lease_sub.add_parser("heartbeat")
    p_pm_heartbeat.add_argument("--project", required=True)
    p_pm_heartbeat.add_argument("--pm-agent", required=True)
    p_pm_heartbeat.add_argument("--lease-id", required=True)
    p_pm_heartbeat.add_argument("--pm-lease-token", required=True)
    p_pm_heartbeat.add_argument("--lease-generation", dest="fencing_token", default="")
    p_pm_heartbeat.add_argument("--fencing-token", dest="fencing_token", default="")
    p_pm_heartbeat.add_argument("--lease-seconds", type=int, default=900)
    p_pm_release = p_pm_lease_sub.add_parser("release")
    p_pm_release.add_argument("--project", required=True)
    p_pm_release.add_argument("--pm-agent", required=True)
    p_pm_release.add_argument("--lease-id", required=True)
    p_pm_release.add_argument("--pm-lease-token", required=True)
    p_pm_release.add_argument("--lease-generation", dest="fencing_token", default="")
    p_pm_release.add_argument("--fencing-token", dest="fencing_token", default="")
    p_pm_release.add_argument("--reason", default="")
    p_pm_takeover = p_pm_lease_sub.add_parser("takeover")
    p_pm_takeover.add_argument("--project", required=True)
    p_pm_takeover.add_argument("--to-pm-agent", required=True)
    p_pm_takeover.add_argument("--operator", default="")
    p_pm_takeover.add_argument("--reason", required=True)
    p_pm_takeover.add_argument("--runner-id", default="")
    p_pm_takeover.add_argument("--device-id", default="")
    p_pm_takeover.add_argument("--lease-seconds", type=int, default=900)
    p_pm_takeover.add_argument("--confirm-healthy", action="store_true")

    p_workbench = sub.add_parser("workbench")
    p_workbench_sub = p_workbench.add_subparsers(dest="workbench_command", required=True)
    p_workbench_project = p_workbench_sub.add_parser("create-project")
    p_workbench_project.add_argument("--project-id", required=True)
    p_workbench_project.add_argument("--name", required=True)
    p_workbench_project.add_argument("--owner", required=True)
    p_workbench_project.add_argument("--source-mode", default="local_repo")
    p_workbench_project.add_argument("--repository-ref", action="append", default=[])
    p_workbench_project.add_argument("--default-assignee", action="append", default=[])
    p_workbench_project.add_argument("--visibility", action="append", default=[])
    p_workbench_project.add_argument("--sensitivity", default="internal")
    p_workbench_project.add_argument("--actor", default="")
    p_workbench_project.add_argument("--idempotency-key", required=True)
    p_workbench_project.add_argument("--permission", action="append", default=None)
    p_workbench_invite = p_workbench_sub.add_parser("invite-runner")
    p_workbench_invite.add_argument("--project", required=True)
    p_workbench_invite.add_argument("--runner-label", required=True)
    p_workbench_invite.add_argument("--capability", action="append", default=[])
    p_workbench_invite.add_argument("--data-scope", action="append", default=[])
    p_workbench_invite.add_argument("--expires-in-seconds", type=int, default=900)
    p_workbench_invite.add_argument("--runner-owner", default="")
    p_workbench_invite.add_argument("--actor", default="")
    p_workbench_invite.add_argument("--idempotency-key", required=True)
    p_workbench_invite.add_argument("--permission", action="append", default=None)
    p_workbench_runner_request = p_workbench_sub.add_parser("register-runner")
    p_workbench_runner_request.add_argument("--runner-id", required=True)
    p_workbench_runner_request.add_argument("--name", required=True)
    p_workbench_runner_request.add_argument("--pairing-code", default="")
    p_workbench_runner_request.add_argument("--host-type", default="")
    p_workbench_runner_request.add_argument("--mode", default="unattended")
    p_workbench_runner_request.add_argument("--agent", action="append", default=[])
    p_workbench_runner_request.add_argument("--capability", action="append", default=[])
    p_workbench_runner_request.add_argument("--project", action="append", default=[])
    p_workbench_runner_request.add_argument("--repo", action="append", default=[])
    p_workbench_runner_request.add_argument("--data-scope", action="append", default=[])
    p_workbench_runner_request.add_argument("--ring-version", default="0.1.0")
    p_workbench_runner_request.add_argument("--owner", default="")
    p_workbench_runner_request.add_argument("--idempotency-key", required=True)
    p_workbench_tool = p_workbench_sub.add_parser("register-tool")
    p_workbench_tool.add_argument("--project", required=True)
    p_workbench_tool.add_argument("--tool-name", required=True)
    p_workbench_tool.add_argument("--tool-type", required=True)
    p_workbench_tool.add_argument("--risk-level", default="low")
    p_workbench_tool.add_argument("--operation", action="append", default=[])
    p_workbench_tool.add_argument("--runner-scope", action="append", default=[])
    p_workbench_tool.add_argument("--owner", default="")
    p_workbench_tool.add_argument("--actor", default="")
    p_workbench_tool.add_argument("--idempotency-key", required=True)
    p_workbench_tool.add_argument("--permission", action="append", default=None)
    p_workbench_tool_request = p_workbench_sub.add_parser("request-tool")
    p_workbench_tool_request.add_argument("--project", required=True)
    p_workbench_tool_request.add_argument("--tool-name", required=True)
    p_workbench_tool_request.add_argument("--tool-type", required=True)
    p_workbench_tool_request.add_argument("--risk-level", default="high")
    p_workbench_tool_request.add_argument("--operation", action="append", default=[])
    p_workbench_tool_request.add_argument("--credential-policy", default="")
    p_workbench_tool_request.add_argument("--owner", default="")
    p_workbench_tool_request.add_argument("--justification", required=True)
    p_workbench_tool_request.add_argument("--data-scope", action="append", default=[])
    p_workbench_tool_request.add_argument("--runner-scope", action="append", default=[])
    p_workbench_tool_request.add_argument("--actor", default="")
    p_workbench_tool_request.add_argument("--idempotency-key", required=True)
    p_workbench_tool_request.add_argument("--permission", action="append", default=None)
    p_workbench_read = p_workbench_sub.add_parser("execution-read-model")
    p_workbench_read.add_argument("--project", required=True)
    p_workbench_read.add_argument("--task-id", default="")

    p_project = sub.add_parser("project")
    p_project_sub = p_project.add_subparsers(dest="project_command", required=True)
    p_project_register = p_project_sub.add_parser("register")
    p_project_register.add_argument("--project-id", required=True)
    p_project_register.add_argument("--name", required=True)
    p_project_register.add_argument("--owner", required=True)
    p_project_register.add_argument("--workspace-ref", default="")
    p_project_intake = p_project_sub.add_parser("intake")
    p_project_intake.add_argument("--name", required=True)
    p_project_intake.add_argument("--owner", required=True)
    p_project_intake.add_argument("--goal", required=True)
    p_project_intake.add_argument("--source", default="")
    p_project_intake.add_argument("--deliverable", default="")
    p_project_intake.add_argument("--priority", default="medium")
    p_project_intake.add_argument("--risk", default="low")
    p_project_intake.add_argument("--repo-url", default="")
    p_project_intake.add_argument("--requested-agent", action="append", default=[])
    p_project_intake.add_argument("--create-group", default="confirm")
    p_project_intake.add_argument("--requester", default="")
    p_project_intake.add_argument("--ring-enabled", action="store_true")
    p_project_intake.add_argument("--project-id", default="")
    p_project_intake.add_argument("--workspace-ref", default="")
    p_project_health = p_project_sub.add_parser("health")
    p_project_health.add_argument("--project", required=True)
    p_project_health.add_argument("--actor", default="system.project-manager")
    p_project_health.add_argument("--create-followup", action="store_true")
    p_project_health.add_argument("--no-notify", action="store_true")
    p_project_pm_action = p_project_sub.add_parser("pm-action")
    p_project_pm_action.add_argument("--project", required=True)
    p_project_pm_action.add_argument("--actor", default="agent.company.project-manager")
    p_project_pm_action.add_argument("--intent", required=True)
    p_project_pm_action.add_argument("--current-state", required=True)
    p_project_pm_action.add_argument("--allowed-transition", required=True)
    p_project_pm_action.add_argument("--exit-state", required=True)
    p_project_pm_action.add_argument("--summary", required=True)
    p_project_pm_action.add_argument("--task-id", default="")
    p_project_pm_action.add_argument("--requirement-ref", action="append", default=[])
    p_project_pm_action.add_argument("--record-written", action="append", default=[])
    p_project_pm_action.add_argument("--delegated-owner", action="append", default=[])
    p_project_pm_action.add_argument("--evidence-ref", action="append", default=[])
    p_project_pm_action.add_argument("--next-action", default="")
    p_project_pm_action.add_argument("--blocker", default="")
    p_project_pm_action.add_argument("--blocker-owner", default="")
    p_project_pm_action.add_argument("--terminal-decision", default="")
    p_project_pm_action.add_argument("--outcome-slice-ref", default="")
    p_project_pm_action.add_argument("--outcome-state-before", default="")
    p_project_pm_action.add_argument("--outcome-state-after", default="")
    p_project_pm_action.add_argument("--outcome-value-change", default="")
    p_project_pm_action.add_argument("--cost-summary", default="")
    p_project_pm_action.add_argument("--scope-change", default="")
    p_project_pm_action.add_argument("--guardrail-decision", default="")
    p_project_pm_action.add_argument("--guardrail-reason", default="")
    p_project_outcome = p_project_sub.add_parser("outcome-slice")
    p_project_outcome.add_argument("--project", required=True)
    p_project_outcome.add_argument("--title", required=True)
    p_project_outcome.add_argument("--owner", default="agent.company.project-manager")
    p_project_outcome.add_argument("--stage-goal", required=True)
    p_project_outcome.add_argument("--main-deliverable", required=True)
    p_project_outcome.add_argument("--current-state", required=True)
    p_project_outcome.add_argument("--target-state", required=True)
    p_project_outcome.add_argument("--outcome-slice-id", default="")
    p_project_outcome.add_argument("--status", default="active")
    p_project_outcome.add_argument("--summary", default="")
    p_project_outcome.add_argument("--evidence-ref", action="append", default=[])
    p_project_outcome.add_argument("--risk-ref", action="append", default=[])
    p_project_outcome.add_argument("--stop-condition", action="append", default=[])
    p_project_outcome.add_argument("--primary-agent", default="")
    p_project_outcome.add_argument("--upstream-agent", default="")
    p_project_outcome.add_argument("--downstream-agent", default="")
    p_project_outcome.add_argument("--handoff-agent", action="append", default=[])
    p_project_outcome.add_argument("--escalation-agent", action="append", default=[])
    p_project_outcome.add_argument("--escalation-rule", action="append", default=[])
    p_project_outcome.add_argument("--acceptance-signal", default="")
    p_project_outcome.add_argument("--time-budget", default="")
    p_project_outcome.add_argument("--token-budget", default="")
    p_project_outcome.add_argument("--wip-limit", type=int, default=3)

    p_task = sub.add_parser("task")
    p_task_sub = p_task.add_subparsers(dest="task_command", required=True)
    p_task_create = p_task_sub.add_parser("create")
    p_task_create.add_argument("--task-id", default="")
    p_task_create.add_argument("--title", required=True)
    p_task_create.add_argument("--project", default="")
    p_task_create.add_argument("--requester", required=True)
    p_task_create.add_argument("--assignee", required=True)
    p_task_create.add_argument("--type", dest="task_type", default="knowledge_capture")
    p_task_create.add_argument("--priority", default="normal")
    p_task_create.add_argument("--due-at", default="")
    p_task_create.add_argument("--source", action="append", default=[])
    p_task_create.add_argument("--expected", action="append", default=[])
    p_task_create.add_argument("--work-source-type", default="")
    p_task_create.add_argument("--requirement-ref", action="append", default=[])
    p_task_create.add_argument("--requirement-object-ref", action="append", default=[])
    p_task_create.add_argument("--acceptance-criteria-ref", action="append", default=[])
    p_task_create.add_argument("--defect-ref", action="append", default=[])
    p_task_create.add_argument("--defect-object-ref", action="append", default=[])
    p_task_create.add_argument("--incident-ref", action="append", default=[])
    p_task_create.add_argument("--operation-ref", action="append", default=[])
    p_task_create.add_argument("--knowledge-task-ref", action="append", default=[])
    p_task_create.add_argument("--research-question", default="")
    p_task_create.add_argument("--source-reason", default="")
    p_task_create.add_argument("--outcome-slice-ref", default="")
    p_task_create.add_argument("--pm-agent", default="")
    p_task_create.add_argument("--pm-lease-id", default="")
    p_task_create.add_argument("--pm-lease-generation", dest="pm_fencing_token", default="")
    p_task_create.add_argument("--pm-fencing-token", dest="pm_fencing_token", default="")
    p_task_create.add_argument("--pm-source", default="")
    p_task_pull = p_task_sub.add_parser("pull")
    p_task_pull.add_argument("task_id")
    p_task_start = p_task_sub.add_parser("start")
    p_task_start.add_argument("task_id")
    p_task_start.add_argument("--actor", default="system")
    p_task_start.add_argument("--pm-agent", default="")
    p_task_start.add_argument("--pm-lease-id", default="")
    p_task_start.add_argument("--pm-lease-generation", dest="pm_fencing_token", default="")
    p_task_start.add_argument("--pm-fencing-token", dest="pm_fencing_token", default="")
    p_task_start.add_argument("--pm-source", default="")
    p_task_fact = p_task_sub.add_parser("fact")
    p_task_fact.add_argument("task_id")
    p_task_fact.add_argument("--project", required=True)
    p_task_fact.add_argument("--format", choices=["json", "markdown"], default="json")
    p_task_finish = p_task_sub.add_parser("finish")
    p_task_finish.add_argument("task_id")
    p_task_finish.add_argument("--result", default="done")
    p_task_finish.add_argument("--summary", required=True)
    p_task_finish.add_argument("--output-ref", action="append", default=[])
    p_task_finish.add_argument("--knowledge-ref", action="append", default=[])
    p_task_finish.add_argument("--evidence-ref", action="append", default=[])
    p_task_finish.add_argument("--next-action", action="append", default=[])
    p_task_finish.add_argument("--runner-id", default="")
    p_task_finish.add_argument("--lease-token", default="")
    p_task_finish.add_argument("--executor-agent", default="")
    p_task_finish.add_argument("--test-or-check", action="append", default=[])
    p_task_finish.add_argument("--knowledge-draft-json", default="")
    p_task_finish.add_argument("--knowledge-draft-file", default="")
    p_task_finish.add_argument("--guide-updated", action="store_true")
    p_task_finish.add_argument("--guide-ref", default="")
    p_task_finish.add_argument("--guide-feishu-url", default="")
    p_task_finish.add_argument("--guide-revision", default="")
    p_task_finish.add_argument("--guide-audit-ref", action="append", default=[])
    p_task_finish.add_argument("--handoff-to", default="")
    p_task_finish.add_argument("--handoff-summary", default="")
    p_task_finish.add_argument("--artifact-ref", action="append", default=[])
    p_task_finish.add_argument("--open-risk", action="append", default=[])
    p_task_finish.add_argument("--next-suggested-task", default="")
    p_task_finish.add_argument("--blocker", action="append", default=[])
    p_task_finish.add_argument("--approval-request-json", default="")
    p_task_finish.add_argument("--approval-request-file", default="")
    p_task_status = p_task_sub.add_parser("status")
    p_task_status.add_argument("task_id")
    p_task_diagnose = p_task_sub.add_parser("diagnose")
    p_task_diagnose.add_argument("task_id")
    p_task_accept = p_task_sub.add_parser("accept")
    p_task_accept.add_argument("task_id")
    p_task_accept.add_argument("--decision", choices=["accepted", "auto_accepted", "rejected", "changes_requested"], default="accepted")
    p_task_accept.add_argument("--reviewer", required=True)
    p_task_accept.add_argument("--reason", default="")
    p_task_accept.add_argument("--human", action="store_true")
    p_task_cancel = p_task_sub.add_parser("cancel")
    p_task_cancel.add_argument("task_id")
    p_task_cancel.add_argument("--actor", required=True)
    p_task_cancel.add_argument("--reason", required=True)
    p_task_cancel.add_argument("--runner-id", default="")
    p_task_cancel.add_argument("--lease-token", default="")
    p_task_retry = p_task_sub.add_parser("retry")
    p_task_retry.add_argument("task_id")
    p_task_retry.add_argument("--actor", required=True)
    p_task_retry.add_argument("--reason", required=True)
    p_task_retry.add_argument("--runner-id", default="")
    p_task_retry.add_argument("--lease-token", default="")
    p_task_retry.add_argument("--preferred-runner", default="")
    p_task_handoff = p_task_sub.add_parser("handoff")
    p_task_handoff.add_argument("task_id")
    p_task_handoff.add_argument("--actor", required=True)
    p_task_handoff.add_argument("--to", dest="handoff_to", required=True)
    p_task_handoff.add_argument("--summary", required=True)
    p_task_handoff.add_argument("--runner-id", default="")
    p_task_handoff.add_argument("--lease-token", default="")
    p_task_handoff.add_argument("--evidence-ref", action="append", default=[])
    p_task_handoff.add_argument("--artifact-ref", action="append", default=[])
    p_task_handoff.add_argument("--next-action", default="")
    p_task_handoff.add_argument("--preferred-runner", default="")

    p_defect = sub.add_parser("defect")
    p_defect_sub = p_defect.add_subparsers(dest="defect_command", required=True)
    p_defect_create = p_defect_sub.add_parser("create")
    p_defect_create.add_argument("--title", required=True)
    p_defect_create.add_argument("--project", required=True)
    p_defect_create.add_argument("--reporter", required=True)
    p_defect_create.add_argument("--severity", default="medium")
    p_defect_create.add_argument("--defect-id", default="")
    p_defect_create.add_argument("--requirement-ref", action="append", default=[])
    p_defect_create.add_argument("--source-task-ref", default="")
    p_defect_create.add_argument("--source-result-ref", default="")
    p_defect_create.add_argument("--evidence-ref", action="append", default=[])
    p_defect_create.add_argument("--expected-behavior", default="")
    p_defect_create.add_argument("--actual-behavior", default="")
    p_defect_create.add_argument("--reproduction-step", action="append", default=[])
    p_defect_fix = p_defect_sub.add_parser("create-fix-task")
    p_defect_fix.add_argument("defect_id")
    p_defect_fix.add_argument("--title", default="")
    p_defect_fix.add_argument("--requester", required=True)
    p_defect_fix.add_argument("--assignee", required=True)
    p_defect_fix.add_argument("--type", dest="task_type", default="development")
    p_defect_fix.add_argument("--priority", default="high")

    p_receiver_review = sub.add_parser("receiver-review")
    p_receiver_review_sub = p_receiver_review.add_subparsers(dest="receiver_review_command", required=True)
    p_receiver_review_create = p_receiver_review_sub.add_parser("create")
    p_receiver_review_create.add_argument("--project", required=True)
    p_receiver_review_create.add_argument("--upstream-ref", required=True)
    p_receiver_review_create.add_argument("--receiver-agent", required=True)
    p_receiver_review_create.add_argument("--reviewer-agent", default="")
    p_receiver_review_create.add_argument("--decision", required=True)
    p_receiver_review_create.add_argument("--artifact-ref", action="append", default=[])
    p_receiver_review_create.add_argument("--check", action="append", default=[])
    p_receiver_review_create.add_argument("--issue", action="append", default=[])
    p_receiver_review_create.add_argument("--assumption", action="append", default=[])
    p_receiver_review_create.add_argument("--review-id", default="")

    p_requirement = sub.add_parser("requirement")
    p_requirement_sub = p_requirement.add_subparsers(dest="requirement_command", required=True)
    p_requirement_create = p_requirement_sub.add_parser("create")
    p_requirement_create.add_argument("--project", required=True)
    p_requirement_create.add_argument("--source", action="append", required=True)
    p_requirement_create.add_argument("--title", required=True)
    p_requirement_create.add_argument("--submitter", required=True)
    p_requirement_create.add_argument("--owner", default="")
    p_requirement_create.add_argument("--decision-owner", default="")
    p_requirement_create.add_argument("--sensitivity", default="internal")
    p_requirement_create.add_argument("--summary", default="")
    p_requirement_state = p_requirement_sub.add_parser("update-state")
    p_requirement_state.add_argument("requirement_id")
    p_requirement_state.add_argument("--patch", required=True, help="JSON object or path to JSON file")
    p_requirement_state.add_argument("--actor", default="agent.company.product-manager")
    p_requirement_state.add_argument("--source", action="append", default=[])
    p_requirement_clarify = p_requirement_sub.add_parser("clarify")
    p_requirement_clarify.add_argument("requirement_id")
    p_requirement_clarify.add_argument("--agent", default="agent.company.product-manager")
    p_requirement_clarify.add_argument("--recipient", default="")
    p_requirement_approve = p_requirement_sub.add_parser("approve")
    p_requirement_approve.add_argument("requirement_id")
    p_requirement_approve.add_argument("--owner", required=True)
    p_requirement_criteria = p_requirement_sub.add_parser("add-criteria")
    p_requirement_criteria.add_argument("requirement_id")
    p_requirement_criteria.add_argument("--description", required=True)
    p_requirement_criteria.add_argument("--observable-signal", required=True)
    p_requirement_criteria.add_argument("--verification-method", default="manual_review")
    p_requirement_criteria.add_argument("--owner", required=True)
    p_requirement_criteria.add_argument("--type", dest="criteria_type", default="product")
    p_requirement_criteria.add_argument("--status", default="draft")
    p_requirement_task = p_requirement_sub.add_parser("create-task")
    p_requirement_task.add_argument("requirement_id")
    p_requirement_task.add_argument("--title", required=True)
    p_requirement_task.add_argument("--assignee", required=True)
    p_requirement_task.add_argument("--requester", required=True)
    p_requirement_task.add_argument("--criteria-ref", action="append", default=[])
    p_requirement_task.add_argument("--type", dest="task_type", default="development")
    p_requirement_task.add_argument("--priority", default="normal")
    p_requirement_impact = p_requirement_sub.add_parser("impact-review")
    p_requirement_impact.add_argument("requirement_id")
    p_requirement_impact.add_argument("--from", dest="from_prd", required=True)
    p_requirement_impact.add_argument("--to", dest="to_prd", required=True)
    p_requirement_impact.add_argument("--owner", required=True)
    p_requirement_impact.add_argument("--status", default="draft")
    p_requirement_tree = p_requirement_sub.add_parser("tree")
    p_requirement_tree_sub = p_requirement_tree.add_subparsers(dest="requirement_tree_command", required=True)
    p_requirement_tree_import = p_requirement_tree_sub.add_parser("import")
    p_requirement_tree_import.add_argument("--project", required=True)
    p_requirement_tree_import.add_argument("--source", default="docs/product/ai-native-os/requirement-tree.md")
    p_requirement_tree_import.add_argument("--coverage-matrix", default="projects/company-knowledge-core/coordination/ai-native-os-requirement-tree-coverage-matrix.md")
    p_requirement_tree_import.add_argument("--actor", default="agent.company.development")
    p_requirement_tree_import.add_argument("--version", default="")
    p_requirement_tree_import.add_argument("--tree-slug", default="ai-native-os")
    p_requirement_tree_compile = p_requirement_tree_sub.add_parser("compile")
    p_requirement_tree_compile.add_argument("--project", default="")
    p_requirement_tree_compile.add_argument("--tree", default="")
    p_requirement_tree_compile.add_argument("--actor", default="agent.company.development")
    p_requirement_tree_workbench = p_requirement_tree_sub.add_parser("workbench")
    p_requirement_tree_workbench.add_argument("--project", default="")
    p_requirement_tree_workbench.add_argument("--tree", default="")
    p_requirement_tree_backfill = p_requirement_tree_sub.add_parser("backfill-existing-work")
    p_requirement_tree_backfill.add_argument("--project", required=True)
    p_requirement_tree_backfill.add_argument("--tree", default="")
    p_requirement_tree_backfill.add_argument("--source", default="docs/product/ai-native-os/requirement-tree.md")
    p_requirement_tree_backfill.add_argument("--coverage-matrix", default="projects/company-knowledge-core/coordination/ai-native-os-requirement-tree-coverage-matrix.md")
    p_requirement_tree_backfill.add_argument("--actor", default="agent.company.development")
    p_requirement_tree_backfill.add_argument("--version", default="")
    p_requirement_tree_backfill.add_argument("--tree-slug", default="ai-native-os")
    p_requirement_tree_promote = p_requirement_tree_sub.add_parser("promote")
    p_requirement_tree_promote.add_argument("--candidate", required=True, help="JSON file with promotion candidates")
    p_requirement_tree_promote.add_argument("--project", default="")
    p_requirement_tree_promote.add_argument("--tree", default="")
    p_requirement_tree_promote.add_argument("--actor", default="agent.company.development")
    p_requirement_tree_promote.add_argument("--write", action="store_true", help="write accepted promotions and AuditLog records")
    p_requirement_tree_promote.add_argument("--dry-run", action="store_true", help="preview validation and audit deltas without writing")
    p_requirement_tree_sub.add_parser("validate")

    p_prd = sub.add_parser("prd")
    p_prd_sub = p_prd.add_subparsers(dest="prd_command", required=True)
    p_prd_generate = p_prd_sub.add_parser("generate")
    p_prd_generate.add_argument("requirement_id")
    p_prd_generate.add_argument("--author-agent", default="agent.company.product-manager")
    p_prd_generate.add_argument("--reviewer", default="")
    p_prd_approve = p_prd_sub.add_parser("approve")
    p_prd_approve.add_argument("prd_id")
    p_prd_approve.add_argument("--reviewer", required=True)

    p_decision = sub.add_parser("decision")
    p_decision_sub = p_decision.add_subparsers(dest="decision_command", required=True)
    p_decision_create = p_decision_sub.add_parser("create")
    p_decision_create.add_argument("--requirement", required=True)
    p_decision_create.add_argument("--impact", default="medium")
    p_decision_create.add_argument("--owner", required=True)
    p_decision_create.add_argument("--area", action="append", default=[])
    p_decision_create.add_argument("--context", required=True)
    p_decision_create.add_argument("--prd-ref", default="")
    p_decision_create.add_argument("--option", action="append", default=[])
    p_decision_create.add_argument("--tradeoffs", default="")
    p_decision_create.add_argument("--recommendation", default="")
    p_decision_create.add_argument("--deadline", default="")
    p_decision_resolve = p_decision_sub.add_parser("resolve")
    p_decision_resolve.add_argument("decision_id")
    p_decision_resolve.add_argument("--selected-option", required=True)
    p_decision_resolve.add_argument("--rationale", required=True)
    p_decision_resolve.add_argument("--approver", default="")

    p_scheduler = sub.add_parser("scheduler")
    p_scheduler_sub = p_scheduler.add_subparsers(dest="scheduler_command", required=True)
    p_scheduler_tick = p_scheduler_sub.add_parser("tick")
    p_scheduler_tick.add_argument("--project", default="")
    p_scheduler_tick.add_argument("--actor", default="system.scheduler")
    p_scheduler_tick.add_argument("--claim", action="store_true")
    p_scheduler_tick.add_argument("--lease-seconds", type=int, default=600)
    p_scheduler_tick.add_argument("--limit", type=int, default=0)
    p_scheduler_autopilot = p_scheduler_sub.add_parser("autopilot")
    p_scheduler_autopilot.add_argument("--project", default="")
    p_scheduler_autopilot.add_argument("--actor", default="agent.company.project-manager")
    p_scheduler_autopilot.add_argument("--cycles", type=int, default=1)
    p_scheduler_autopilot.add_argument("--max-rounds", type=int, default=None)
    p_scheduler_autopilot.add_argument("--claim-limit", type=int, default=1)
    p_scheduler_autopilot.add_argument("--lease-seconds", type=int, default=600)
    p_scheduler_autopilot.add_argument("--claim", action="store_true")
    p_scheduler_workbench = p_scheduler_sub.add_parser("workbench")
    p_scheduler_workbench.add_argument("--project", default="")
    p_scheduler_workbench.add_argument("--task-id", default="")

    p_worker = sub.add_parser("worker")
    p_worker_sub = p_worker.add_subparsers(dest="worker_command", required=True)
    p_worker_run = p_worker_sub.add_parser("run")
    p_worker_run.add_argument("--project", default="")
    p_worker_run.add_argument("--agent", required=True)
    p_worker_run.add_argument("--runner-id", "--runner", default="")
    p_worker_run.add_argument("--stage", default="")
    p_worker_run.add_argument("--limit", type=int, default=1)
    p_worker_run.add_argument("--lease-seconds", type=int, default=600)

    p_v1 = sub.add_parser("v1")
    p_v1_sub = p_v1.add_subparsers(dest="v1_command", required=True)
    p_v1_device = p_v1_sub.add_parser("device")
    p_v1_device_sub = p_v1_device.add_subparsers(dest="v1_device_command", required=True)
    p_v1_device_register = p_v1_device_sub.add_parser("register")
    p_v1_device_register.add_argument("--device-id", default="device.local")
    p_v1_device_register.add_argument("--name", default="Local Machine")
    p_v1_device_register.add_argument("--host-type", default="local_mac")
    p_v1_device_register.add_argument("--capability", action="append", default=[])
    p_v1_device_register.add_argument("--workspace", default="")
    p_v1_device_list = p_v1_device_sub.add_parser("list")
    p_v1_profile = p_v1_sub.add_parser("profile")
    p_v1_profile_sub = p_v1_profile.add_subparsers(dest="v1_profile_command", required=True)
    p_v1_profile_register = p_v1_profile_sub.add_parser("register")
    p_v1_profile_register.add_argument("--agent", required=True)
    p_v1_profile_register.add_argument("--project", default="")
    p_v1_profile_register.add_argument("--skill", action="append", default=[])
    p_v1_skill = p_v1_sub.add_parser("skill")
    p_v1_skill_sub = p_v1_skill.add_subparsers(dest="v1_skill_command", required=True)
    p_v1_skill_register = p_v1_skill_sub.add_parser("register")
    p_v1_skill_register.add_argument("--skill-id", required=True)
    p_v1_skill_register.add_argument("--name", default="")
    p_v1_skill_register.add_argument("--allowed-agent", action="append", default=[])
    p_v1_skill_register.add_argument("--risk", default="low")
    p_v1_session = p_v1_sub.add_parser("session")
    p_v1_session_sub = p_v1_session.add_subparsers(dest="v1_session_command", required=True)
    p_v1_session_register = p_v1_session_sub.add_parser("register")
    p_v1_session_register.add_argument("--project", required=True)
    p_v1_session_register.add_argument("--agent", required=True)
    p_v1_session_register.add_argument("--session-id", default="")
    p_v1_session_register.add_argument("--device-id", default="device.local")
    p_v1_session_register.add_argument("--capability", action="append", default=[])
    p_v1_session_heartbeat = p_v1_session_sub.add_parser("heartbeat")
    p_v1_session_heartbeat.add_argument("--session-id", required=True)
    p_v1_session_heartbeat.add_argument("--status", default="online")
    p_v1_session_heartbeat.add_argument("--task-id", default="")
    p_v1_session_list = p_v1_session_sub.add_parser("list")
    p_v1_session_list.add_argument("--project", default="")
    p_v1_router = p_v1_sub.add_parser("router")
    p_v1_router_sub = p_v1_router.add_subparsers(dest="v1_router_command", required=True)
    p_v1_router_send = p_v1_router_sub.add_parser("send")
    p_v1_router_send.add_argument("--project", required=True)
    p_v1_router_send.add_argument("--from-agent", required=True)
    p_v1_router_send.add_argument("--to-agent", required=True)
    p_v1_router_send.add_argument("--type", required=True)
    p_v1_router_send.add_argument("--payload-json", default="{}")
    p_v1_router_send.add_argument("--context-ref", action="append", default=[])
    p_v1_package = p_v1_sub.add_parser("package")
    p_v1_package_sub = p_v1_package.add_subparsers(dest="v1_package_command", required=True)
    p_v1_package_compile = p_v1_package_sub.add_parser("compile")
    p_v1_package_compile.add_argument("--task-id", required=True)
    p_v1_package_compile.add_argument("--from-agent", default="agent.company.project-manager")
    p_v1_package_compile.add_argument("--to-agent", required=True)
    p_v1_package_compile.add_argument("--project", default="")
    p_v1_runtime = p_v1_sub.add_parser("runtime")
    p_v1_runtime_sub = p_v1_runtime.add_subparsers(dest="v1_runtime_command", required=True)
    p_v1_runtime_execute = p_v1_runtime_sub.add_parser("execute")
    p_v1_runtime_execute.add_argument("--package-id", required=True)
    p_v1_runtime_execute.add_argument("--runner", required=True)
    p_v1_runtime_execute.add_argument("--agent", default="")
    p_v1_acceptance = p_v1_sub.add_parser("acceptance")
    p_v1_acceptance_sub = p_v1_acceptance.add_subparsers(dest="v1_acceptance_command", required=True)
    p_v1_acceptance_run = p_v1_acceptance_sub.add_parser("run")
    p_v1_acceptance_run.add_argument("--project", default="company-knowledge-core")
    p_v1_acceptance_run.add_argument("--actor", default="agent.company.project-manager")
    p_v1_workbench = p_v1_sub.add_parser("workbench")
    p_v1_workbench_sub = p_v1_workbench.add_subparsers(dest="v1_workbench_command", required=True)
    p_v1_workbench_export = p_v1_workbench_sub.add_parser("export")
    p_v1_workbench_export.add_argument("--project", default="company-knowledge-core")
    p_v1_workbench_export.add_argument("--out", default="")
    p_v1_workbench_export.add_argument("--format", choices=["json", "js"], default="json")

    p_tool = sub.add_parser("tool")
    p_tool_sub = p_tool.add_subparsers(dest="tool_command", required=True)
    p_tool_register = p_tool_sub.add_parser("register")
    p_tool_register.add_argument("--tool-id", required=True)
    p_tool_register.add_argument("--name", required=True)
    p_tool_register.add_argument("--owner", required=True)
    p_tool_register.add_argument("--repo", required=True)
    p_tool_register.add_argument("--entrypoint", required=True)
    p_tool_register.add_argument("--risk", default="L1")
    p_tool_invoke = p_tool_sub.add_parser("invoke")
    p_tool_invoke.add_argument("--tool-id", required=True)
    p_tool_invoke.add_argument("--project", required=True)
    p_tool_invoke.add_argument("--agent", required=True)
    p_tool_invoke.add_argument("--input", required=True)
    p_tool_invoke.add_argument("--execute", action="store_true")

    p_skill = sub.add_parser("skill")
    p_skill_sub = p_skill.add_subparsers(dest="skill_command", required=True)
    p_skill_register = p_skill_sub.add_parser("register")
    p_skill_register.add_argument("--skill-id", required=True)
    p_skill_register.add_argument("--name", required=True)
    p_skill_register.add_argument("--owner", required=True)
    p_skill_register.add_argument("--purpose", default="")
    p_skill_register.add_argument("--scope", default="company", choices=["company", "project", "private"])
    p_skill_register.add_argument("--risk", default="L2")
    p_skill_register.add_argument("--project", default="")
    p_skill_register.add_argument("--source-ref", default="")
    p_skill_sub.add_parser("validate")

    p_policy = sub.add_parser("policy")
    p_policy_sub = p_policy.add_subparsers(dest="policy_command", required=True)
    p_policy_register = p_policy_sub.add_parser("register")
    p_policy_register.add_argument("--policy-id", required=True)
    p_policy_register.add_argument("--title", required=True)
    p_policy_register.add_argument("--agent-id", required=True)
    p_policy_register.add_argument("--owner", required=True)
    p_policy_register.add_argument("--allow-project", action="append", default=[])
    p_policy_register.add_argument("--allow-scope", action="append", default=[])
    p_policy_register.add_argument("--allow-risk", action="append", default=[])

    p_start = sub.add_parser("start")
    p_start.add_argument("--project", required=True)
    p_start.add_argument("--agent", required=True)
    p_start.add_argument("--task", required=True)
    p_start.add_argument("--retrieval-limit", type=int, default=5)

    p_finish = sub.add_parser("finish")
    p_finish.add_argument("--project", required=True)
    p_finish.add_argument("--agent", required=True)
    p_finish.add_argument("--summary", required=True)
    p_finish.add_argument("--result", default="completed")
    p_finish.add_argument("--no-reusable-lesson", action="store_true")
    p_finish.add_argument("--no-tool-update", action="store_true")

    p_review = sub.add_parser("review")
    p_review_sub = p_review.add_subparsers(dest="review_command", required=True)
    p_review_list = p_review_sub.add_parser("list")
    p_review_list.add_argument("--type", dest="object_type", default="")
    p_review_update = p_review_sub.add_parser("update")
    p_review_update.add_argument("--target", required=True)
    p_review_update.add_argument("--status", required=True)
    p_review_update.add_argument("--reviewer", required=True)
    p_review_apply = p_review_sub.add_parser("apply")
    p_review_apply.add_argument("--task-id", required=True)
    p_review_apply.add_argument("--outcome", required=True)
    p_review_apply.add_argument("--reviewer", required=True)
    p_review_apply.add_argument("--summary", required=True)
    p_review_apply.add_argument("--target-ref", action="append", default=[])
    p_review_approve = p_review_sub.add_parser("approve")
    p_review_approve.add_argument("--task-id", required=True)
    p_review_approve.add_argument("--outcome", choices=["approved", "rejected"], required=True)
    p_review_approve.add_argument("--approver", required=True)
    p_review_approve.add_argument("--summary", required=True)
    p_review_approve.add_argument("--target-ref", action="append", default=[])
    p_review_approve.add_argument("--publish-status", default="verified")
    p_review_bulk = p_review_sub.add_parser("bulk")
    p_review_bulk.add_argument("--type", dest="object_type", default="")
    p_review_bulk.add_argument("--from-status", default="")
    p_review_bulk.add_argument("--to-status", required=True)
    p_review_bulk.add_argument("--reviewer", required=True)
    p_review_bulk.add_argument("--limit", type=int, default=0)

    p_index = sub.add_parser("index")
    p_index_sub = p_index.add_subparsers(dest="index_command", required=True)
    p_index_sub.add_parser("rebuild")
    p_index_search = p_index_sub.add_parser("search")
    p_index_search.add_argument("--type", dest="object_type", default="")
    p_index_search.add_argument("--status", default="")
    p_index_search.add_argument("--project-id", default="")
    p_index_search.add_argument("--agent-id", default="")
    p_index_search.add_argument("--tool-id", default="")
    p_index_search.add_argument("--risk-level", default="")
    p_index_search.add_argument("--text", default="")

    p_rag = sub.add_parser("rag")
    p_rag_sub = p_rag.add_subparsers(dest="rag_command", required=True)
    p_rag_sub.add_parser("rebuild")
    p_rag_search = p_rag_sub.add_parser("search")
    p_rag_search.add_argument("--query", required=True)
    p_rag_search.add_argument("--project-id", default="")
    p_rag_search.add_argument("--scope", action="append", default=[])
    p_rag_search.add_argument("--limit", type=int, default=5)

    p_publish = sub.add_parser("publish")
    p_publish.add_argument("--actor", default="system.publisher")
    p_publish.add_argument("--reason", default="")
    p_publish.add_argument("--rebuild-graph", action="store_true")

    p_material = sub.add_parser("material")
    p_material_sub = p_material.add_subparsers(dest="material_command", required=True)
    p_material_ingest = p_material_sub.add_parser("ingest")
    p_material_ingest.add_argument("--title", default="")
    p_material_ingest.add_argument("--source-ref", default="")
    p_material_ingest.add_argument("--project", default="")
    p_material_ingest.add_argument("--submitter", required=True)
    p_material_ingest.add_argument("--material-type", default="")
    p_material_ingest.add_argument("--storage-ref", default="")
    p_material_ingest.add_argument("--content", default="")
    p_material_ingest.add_argument("--content-file", default="")
    p_material_ingest.add_argument("--license", dest="license_hint", default="")
    p_material_ingest.add_argument("--sensitivity", default="internal")
    p_material_ingest.add_argument("--extraction-tool", default="manual")
    p_material_ingest.add_argument("--extraction-status", default="registered")
    p_material_ingest.add_argument("--create-task", action="store_true")
    p_material_ingest.add_argument("--assignee", default="agent.company-knowledge-core.knowledge-engineering")

    p_discussion = sub.add_parser("discussion")
    p_discussion_sub = p_discussion.add_subparsers(dest="discussion_command", required=True)
    p_discussion_create = p_discussion_sub.add_parser("create")
    p_discussion_create.add_argument("--title", required=True)
    p_discussion_create.add_argument("--project", default="")
    p_discussion_create.add_argument("--requester", required=True)
    p_discussion_create.add_argument("--topic", required=True)
    p_discussion_create.add_argument("--participant-agent", action="append", default=[])
    p_discussion_create.add_argument("--related-task-id", default="")
    p_discussion_create.add_argument("--facilitator-agent", default="agent.company.project-manager")
    p_discussion_create.add_argument("--max-rounds", type=int, default=1)
    p_discussion_create.add_argument("--not-human-visible", action="store_true")
    p_discussion_turn = p_discussion_sub.add_parser("turn")
    p_discussion_turn.add_argument("--discussion-id", required=True)
    p_discussion_turn.add_argument("--agent-id", required=True)
    p_discussion_turn.add_argument("--role", default="")
    p_discussion_turn.add_argument("--content", required=True)
    p_discussion_turn.add_argument("--stance", default="")
    p_discussion_turn.add_argument("--concern", action="append", default=[])
    p_discussion_turn.add_argument("--recommendation", action="append", default=[])
    p_discussion_turn.add_argument("--evidence-ref", action="append", default=[])
    p_discussion_finalize = p_discussion_sub.add_parser("finalize")
    p_discussion_finalize.add_argument("--discussion-id", required=True)
    p_discussion_finalize.add_argument("--facilitator", required=True)
    p_discussion_finalize.add_argument("--summary", required=True)
    p_discussion_finalize.add_argument("--consensus", default="")
    p_discussion_finalize.add_argument("--decision", default="")
    p_discussion_finalize.add_argument("--open-question", action="append", default=[])
    p_discussion_finalize.add_argument("--human-decision-required", action="store_true")
    p_discussion_finalize.add_argument("--followup-task-title", default="")
    p_discussion_finalize.add_argument("--followup-assignee", default="")
    p_discussion_status = p_discussion_sub.add_parser("status")
    p_discussion_status.add_argument("--discussion-id", required=True)

    p_notification = sub.add_parser("notification")
    p_notification_sub = p_notification.add_subparsers(dest="notification_command", required=True)
    p_notification_list = p_notification_sub.add_parser("list")
    p_notification_list.add_argument("--status", default="")
    p_notification_list.add_argument("--recipient", default="")
    p_notification_list.add_argument("--channel", default="")
    p_notification_list.add_argument("--message-type", default="")
    p_notification_list.add_argument("--project-id", default="")
    p_notification_list.add_argument("--task-id", default="")
    p_notification_list.add_argument("--discussion-id", default="")
    p_notification_list.add_argument("--limit", type=int, default=50)
    p_notification_mark = p_notification_sub.add_parser("mark")
    p_notification_mark.add_argument("--notification-id", required=True)
    p_notification_mark.add_argument("--status", required=True, choices=["pending", "sent", "failed", "retrying", "dead_letter"])
    p_notification_mark.add_argument("--actor", required=True)
    p_notification_mark.add_argument("--failure-reason", default="")
    p_notification_mark.add_argument("--delivery-ref", default="")

    p_feedback = sub.add_parser("feedback")
    p_feedback.add_argument("--project", required=True)
    p_feedback.add_argument("--submitter", required=True)
    p_feedback.add_argument("--content", required=True)
    p_feedback.add_argument("--type", dest="feedback_type", default="")
    p_feedback.add_argument("--evidence-ref", action="append", default=[])
    p_feedback.add_argument("--impact", default="")
    p_feedback.add_argument("--suggested-next-action", default="")
    p_feedback.add_argument("--requirement-ref", default="")
    p_feedback.add_argument("--agent-ref", default="")
    p_feedback.add_argument("--result-ref", default="")
    p_feedback.add_argument("--score", default="")

    p_admin = sub.add_parser("admin")
    p_admin_sub = p_admin.add_subparsers(dest="admin_command", required=True)
    p_admin_disable = p_admin_sub.add_parser("disable")
    p_admin_disable.add_argument("--type", dest="object_type", required=True, choices=["agent", "tool", "skill", "runner", "integration", "policy"])
    p_admin_disable.add_argument("--id", dest="object_id", required=True)
    p_admin_disable.add_argument("--actor", required=True)
    p_admin_disable.add_argument("--reason", required=True)
    p_admin_disable.add_argument("--reassign", action="store_true")

    p_ops = sub.add_parser("ops")
    p_ops_sub = p_ops.add_subparsers(dest="ops_command", required=True)
    p_ops_experiment = p_ops_sub.add_parser("experiment")
    p_ops_experiment.add_argument("--project", required=True)
    p_ops_experiment.add_argument("--title", required=True)
    p_ops_experiment.add_argument("--owner", required=True)
    p_ops_experiment.add_argument("--hypothesis", required=True)
    p_ops_experiment.add_argument("--audience", required=True)
    p_ops_experiment.add_argument("--metric", required=True)
    p_ops_experiment.add_argument("--start-at", default="")
    p_ops_experiment.add_argument("--end-at", default="")
    p_ops_experiment.add_argument("--customer-facing", action="store_true")

    p_agent_rules = sub.add_parser("agent-rules")
    p_agent_rules_sub = p_agent_rules.add_subparsers(dest="agent_rules_command", required=True)
    p_agent_rules_issue = p_agent_rules_sub.add_parser("issue")
    p_agent_rules_issue.add_argument("--title", required=True)
    p_agent_rules_issue.add_argument("--rule-id", default="")
    p_agent_rules_issue.add_argument("--reporter", required=True)
    p_agent_rules_issue.add_argument("--reason", required=True)
    p_agent_rules_issue.add_argument("--scope", default="company")
    p_agent_rules_issue.add_argument("--proposal", default="")
    p_agent_rules_issue.add_argument("--source-ref", default="")
    p_agent_rules_issue.add_argument("--project", default="")

    p_graph = sub.add_parser("graph")
    p_graph_sub = p_graph.add_subparsers(dest="graph_command", required=True)
    p_graph_export = p_graph_sub.add_parser("export")
    p_graph_export.add_argument("--actor", default="system")
    p_graph_impact = p_graph_sub.add_parser("impact")
    p_graph_impact.add_argument("ref")
    p_graph_impact.add_argument("--actor", default="system")
    p_graph_impact.add_argument("--rebuild", action="store_true")

    p_conflict = sub.add_parser("conflict")
    p_conflict_sub = p_conflict.add_subparsers(dest="conflict_command", required=True)
    p_conflict_create = p_conflict_sub.add_parser("create")
    p_conflict_create.add_argument("--type", dest="conflict_type", required=True)
    p_conflict_create.add_argument("--owner", required=True)
    p_conflict_create.add_argument("--summary", required=True)
    p_conflict_create.add_argument("--affected", action="append", default=[])
    p_conflict_resolve = p_conflict_sub.add_parser("resolve")
    p_conflict_resolve.add_argument("--target", required=True)
    p_conflict_resolve.add_argument("--owner", required=True)
    p_conflict_resolve.add_argument("--resolution", required=True)

    p_audit = sub.add_parser("audit")
    p_audit_sub = p_audit.add_subparsers(dest="audit_command", required=True)
    p_audit_search = p_audit_sub.add_parser("search")
    p_audit_search.add_argument("--project-id", default="")
    p_audit_search.add_argument("--agent-id", default="")
    p_audit_search.add_argument("--tool-id", default="")
    p_audit_search.add_argument("--target", default="")

    p_metrics = sub.add_parser("metrics")
    p_metrics_sub = p_metrics.add_subparsers(dest="metrics_command", required=True)
    p_metrics_report = p_metrics_sub.add_parser("report")
    p_metrics_report.add_argument("--owner", default="system")

    p_stale = sub.add_parser("stale")
    p_stale_sub = p_stale.add_subparsers(dest="stale_command", required=True)
    p_stale_scan = p_stale_sub.add_parser("scan")
    p_stale_scan.add_argument("--owner", default="system")

    p_eval = sub.add_parser("eval")
    p_eval_sub = p_eval.add_subparsers(dest="eval_command", required=True)
    p_eval_case = p_eval_sub.add_parser("case")
    p_eval_case_sub = p_eval_case.add_subparsers(dest="eval_case_command", required=True)
    p_eval_case_create = p_eval_case_sub.add_parser("create")
    p_eval_case_create.add_argument("--eval-id", required=True)
    p_eval_case_create.add_argument("--title", required=True)
    p_eval_case_create.add_argument("--owner", required=True)
    p_eval_case_create.add_argument("--target-ref", required=True)
    p_eval_case_create.add_argument("--input", required=True)
    p_eval_case_create.add_argument("--expected", required=True)
    p_eval_run = p_eval_sub.add_parser("run")
    p_eval_run.add_argument("--eval-id", required=True)
    p_eval_run.add_argument("--actual", required=True)
    p_eval_run.add_argument("--runner", required=True)
    p_eval_run.add_argument("--severity", default="high", choices=["low", "medium", "high", "critical"])

    p_backup = sub.add_parser("backup")
    p_backup_sub = p_backup.add_subparsers(dest="backup_command", required=True)
    p_backup_create = p_backup_sub.add_parser("create")
    p_backup_create.add_argument("--output", default="")
    p_backup_restore = p_backup_sub.add_parser("restore")
    p_backup_restore.add_argument("--archive", required=True)
    p_backup_restore.add_argument("--overwrite", action="store_true")

    p_api = sub.add_parser("api")
    p_api_sub = p_api.add_subparsers(dest="api_command", required=True)
    p_api_sub.add_parser("export")
    p_api_serve = p_api_sub.add_parser("serve")
    p_api_serve.add_argument("--host", default="127.0.0.1")
    p_api_serve.add_argument("--port", type=int, default=8765)

    p_gateway = sub.add_parser("gateway")
    p_gateway_sub = p_gateway.add_subparsers(dest="gateway_command", required=True)
    p_gateway_context = p_gateway_sub.add_parser("context")
    p_gateway_context.add_argument("--project", required=True)
    p_gateway_context.add_argument("--agent", required=True)
    p_gateway_context.add_argument("--task", required=True)

    sub.add_parser("validate")
    return parser


def bundle_from_args(args: argparse.Namespace) -> Bundle:
    return Bundle(Path(args.root).resolve() if args.root else find_bundle_root())


def cmd_init(bundle: Bundle, args: argparse.Namespace) -> None:
    agent_id = args.agent_id or f"agent.{args.user_id}.builder"
    config = default_config(bundle, args.user_id, args.ai_tool, agent_id, args.remote)
    save_config(bundle, config)
    print(f"initialized {bundle.config_path}")


def cmd_status(bundle: Bundle) -> None:
    config = load_config(bundle)
    profile_name = config.get("activeProfile", "local")
    profile = config.get("profiles", {}).get(profile_name, {})
    problems = validate_bundle(bundle)
    print(f"root: {bundle.root}")
    print(f"profile: {profile_name}")
    print(f"backend: {profile.get('backend', '')}")
    print(f"valid: {'yes' if not problems else 'no'}")
    if problems:
        print("problems:")
        for problem in problems:
            print(f"- {problem}")


def active_profile(bundle: Bundle) -> dict:
    config = load_config(bundle)
    profile_name = config.get("activeProfile", "local")
    profile = dict(config.get("profiles", {}).get(profile_name, {}))
    profile["name"] = profile_name
    return profile


def resolve_api_base_url(profile: dict) -> str:
    raw = str(profile.get("apiBaseUrl", "")).strip()
    if raw.startswith("${") and raw.endswith("}"):
        env_name = raw[2:-1]
        raw = os.environ.get(env_name, "")
    if not raw:
        raise KnowledgeError("active api profile has no apiBaseUrl")
    return raw.rstrip("/")


def api_request(bundle: Bundle, method: str, path: str, payload: dict | None = None) -> dict:
    profile = active_profile(bundle)
    base = resolve_api_base_url(profile)
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"} if body else {}
    token_env = str(profile.get("apiTokenEnv", "")).strip()
    token = os.environ.get(token_env, "") if token_env else str(profile.get("apiToken", "")).strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(
        base + path,
        data=body,
        headers=headers,
        method=method,
    )
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def use_api_backend(bundle: Bundle) -> bool:
    return active_profile(bundle).get("backend") == "api"


def main(argv: list[str] | None = None) -> int:
    parser = make_parser()
    args = parser.parse_args(argv)
    bundle = bundle_from_args(args)
    try:
        if args.command == "init":
            cmd_init(bundle, args)
        elif args.command == "install":
            agent_id = args.agent_id or f"agent.{args.user_id}.builder"
            paths = install_connector(
                bundle,
                args.user_id,
                args.ai_tool,
                agent_id,
                args.remote,
                args.default_project,
                args.register_agent,
                args.agent_name,
                args.purpose,
                not args.no_rebuild_index,
            )
            for path in paths:
                print(path)
        elif args.command == "status":
            cmd_status(bundle)
        elif args.command == "profile":
            config = load_config(bundle)
            if args.name not in config.get("profiles", {}):
                raise KnowledgeError(f"unknown profile: {args.name}")
            config["activeProfile"] = args.name
            save_config(bundle, config)
            print(f"active profile: {args.name}")
        elif args.command == "sync":
            if args.sync_command == "pull":
                try:
                    print(git(bundle, ["pull", "--ff-only"]))
                except KnowledgeError as exc:
                    path = create_conflict(bundle, "git_pull", "system", str(exc), ["git:pull"])
                    print(f"created conflict: {path}", file=sys.stderr)
                    return 2
            elif args.sync_command == "push":
                try:
                    print(git(bundle, ["push"]))
                except KnowledgeError as exc:
                    path = create_conflict(bundle, "git_push", "system", str(exc), ["git:push"])
                    print(f"created conflict: {path}", file=sys.stderr)
                    return 2
        elif args.command == "agent":
            if args.agent_command == "register":
                if args.allow_project:
                    path = None
                    for project_id in args.allow_project:
                        path = register_project_agent(bundle, project_id, args.agent_id, args.name, args.owner, args.tool, args.purpose)
                    assert path is not None
                else:
                    path = make_agent(bundle, args.agent_id, args.name, args.owner, args.tool, args.purpose)
                print(path)
            elif args.agent_command == "report":
                path = create_agent_capability_report(bundle, args.agent_id, args.owner, args.project, args.period)
                print(path)
            elif args.agent_command == "role-check":
                result = run_agent_role_operating_check(
                    bundle,
                    args.role,
                    args.project,
                    args.actor,
                    args.create_followup,
                    not args.no_notify,
                )
                print(json.dumps(result, indent=2, ensure_ascii=False))
        elif args.command == "actor":
            if args.actor_command == "context":
                path = upsert_actor_context(
                    bundle,
                    args.actor_id,
                    args.type,
                    args.name,
                    args.default_project,
                    args.allow_project,
                    args.scope,
                    args.notify,
                    args.output_preference,
                    args.source,
                    args.owner,
                )
                print(path)
            elif args.actor_command == "feedback":
                result = create_actor_feedback(
                    bundle,
                    args.actor_id,
                    args.content,
                    args.target_agent,
                    args.project,
                    args.task,
                    args.result_ref,
                    args.rating,
                    args.type,
                    args.evidence_ref,
                    args.impact,
                    args.source,
                    args.owner,
                )
                print(json.dumps(result, indent=2, ensure_ascii=False))
        elif args.command == "runner":
            if args.runner_command == "register":
                path = register_agent_runner(
                    bundle,
                    args.runner_id,
                    args.name,
                    args.host_type,
                    args.mode,
                    args.agent,
                    args.capability,
                    args.project,
                    args.repo,
                    args.data_scope,
                    args.ring_version,
                )
                print(path)
            elif args.runner_command == "heartbeat":
                path = heartbeat_agent_runner(bundle, args.runner_id, args.status, args.load, args.capability, args.project)
                print(path)
            elif args.runner_command == "list":
                result = {"apiVersion": "v0.1", "kind": "RunnerRegistry", "runners": runner_registry_for_workbench(bundle, args.project)}
                print(json.dumps(result, indent=2, ensure_ascii=False))
        elif args.command == "pm-lease":
            if args.pm_lease_command == "status":
                result = {"apiVersion": "v0.1", "kind": "PMControlLeaseReadModel", "pmControl": pm_control_lease_read_model(bundle, args.project)}
                print(json.dumps(result, indent=2, ensure_ascii=False))
            elif args.pm_lease_command == "acquire":
                result = acquire_pm_control_lease(bundle, args.project, args.pm_agent, runner_id=args.runner_id, device_id=args.device_id, lease_seconds=args.lease_seconds, idempotency_key=args.idempotency_key, source_channel="cli")
                print(json.dumps(result, indent=2, ensure_ascii=False))
            elif args.pm_lease_command == "heartbeat":
                result = heartbeat_pm_control_lease(bundle, args.project, args.pm_agent, args.lease_id, args.pm_lease_token, args.fencing_token, args.lease_seconds, "cli")
                print(json.dumps(result, indent=2, ensure_ascii=False))
            elif args.pm_lease_command == "release":
                result = release_pm_control_lease(bundle, args.project, args.pm_agent, args.lease_id, args.pm_lease_token, args.fencing_token, args.reason, "cli")
                print(json.dumps(result, indent=2, ensure_ascii=False))
            elif args.pm_lease_command == "takeover":
                result = takeover_pm_control_lease(bundle, args.project, args.to_pm_agent, args.operator or args.to_pm_agent, args.reason, runner_id=args.runner_id, device_id=args.device_id, lease_seconds=args.lease_seconds, confirm_healthy=args.confirm_healthy, source_channel="cli")
                print(json.dumps(result, indent=2, ensure_ascii=False))
        elif args.command == "workbench":
            if args.workbench_command == "create-project":
                result = create_workbench_project(
                    bundle,
                    args.project_id,
                    args.name,
                    args.owner,
                    args.source_mode,
                    args.repository_ref,
                    args.default_assignee,
                    args.visibility,
                    args.sensitivity,
                    args.actor or args.owner,
                    args.idempotency_key,
                    args.permission,
                )
                print(json.dumps(result, indent=2, ensure_ascii=False))
            elif args.workbench_command == "invite-runner":
                result = create_runner_invitation(
                    bundle,
                    args.project,
                    args.runner_label,
                    args.capability,
                    args.expires_in_seconds,
                    args.runner_owner,
                    args.data_scope,
                    args.actor or args.runner_owner,
                    args.idempotency_key,
                    args.permission,
                )
                print(json.dumps(result, indent=2, ensure_ascii=False))
            elif args.workbench_command == "register-runner":
                result = submit_runner_registration(
                    bundle,
                    args.runner_id,
                    args.name,
                    args.pairing_code,
                    args.host_type,
                    args.mode,
                    args.agent,
                    args.capability,
                    args.project,
                    args.repo,
                    args.data_scope,
                    args.ring_version,
                    owner=args.owner,
                    idempotency_key=args.idempotency_key,
                )
                print(json.dumps(result, indent=2, ensure_ascii=False))
            elif args.workbench_command == "register-tool":
                result = register_workbench_tool(
                    bundle,
                    args.project,
                    args.tool_name,
                    args.tool_type,
                    args.risk_level,
                    args.operation,
                    args.runner_scope,
                    args.owner,
                    args.actor or args.owner,
                    args.idempotency_key,
                    args.permission,
                )
                print(json.dumps(result, indent=2, ensure_ascii=False))
            elif args.workbench_command == "request-tool":
                result = create_tool_registration_request(
                    bundle,
                    args.project,
                    args.tool_name,
                    args.tool_type,
                    args.risk_level,
                    args.operation,
                    args.credential_policy,
                    args.owner,
                    args.justification,
                    args.data_scope,
                    args.runner_scope,
                    args.actor or args.owner,
                    args.idempotency_key,
                    args.permission,
                )
                print(json.dumps(result, indent=2, ensure_ascii=False))
            elif args.workbench_command == "execution-read-model":
                result = workbench_project_execution_read_model(bundle, args.project, args.task_id)
                print(json.dumps(result, indent=2, ensure_ascii=False))
        elif args.command == "project":
            if args.project_command == "register":
                path = make_project(bundle, args.project_id, args.name, args.owner, args.workspace_ref)
                print(path)
            elif args.project_command == "intake":
                result = create_project_launch(
                    bundle,
                    args.name,
                    args.owner,
                    args.goal,
                    args.source,
                    args.deliverable,
                    args.priority,
                    args.risk,
                    args.repo_url,
                    ",".join(args.requested_agent),
                    args.create_group,
                    True,
                    args.ring_enabled,
                    args.requester or args.owner,
                    args.project_id,
                    args.workspace_ref,
                )
                print(json.dumps(result, indent=2, ensure_ascii=False))
            elif args.project_command == "health":
                result = run_project_manager_health_check(
                    bundle,
                    args.project,
                    args.actor,
                    args.create_followup,
                    not args.no_notify,
                )
                print(json.dumps(result, indent=2, ensure_ascii=False))
            elif args.project_command == "pm-action":
                result = create_project_manager_action(
                    bundle,
                    args.project,
                    args.actor,
                    args.intent,
                    args.current_state,
                    args.allowed_transition,
                    args.exit_state,
                    args.summary,
                    task_id=args.task_id,
                    requirement_refs=args.requirement_ref,
                    records_written=args.record_written,
                    delegated_owners=args.delegated_owner,
                    evidence_refs=args.evidence_ref,
                    next_action=args.next_action,
                    blocker=args.blocker,
                    blocker_owner=args.blocker_owner,
                    terminal_decision=args.terminal_decision,
                    outcome_slice_ref=args.outcome_slice_ref,
                    outcome_state_before=args.outcome_state_before,
                    outcome_state_after=args.outcome_state_after,
                    outcome_value_change=args.outcome_value_change,
                    cost_summary=args.cost_summary,
                    scope_change=args.scope_change,
                    guardrail_decision=args.guardrail_decision,
                    guardrail_reason=args.guardrail_reason,
                )
                print(json.dumps(result, indent=2, ensure_ascii=False))
            elif args.project_command == "outcome-slice":
                result = create_outcome_slice(
                    bundle,
                    args.project,
                    args.title,
                    args.owner,
                    args.stage_goal,
                    args.main_deliverable,
                    args.current_state,
                    args.target_state,
                    outcome_slice_id=args.outcome_slice_id,
                    status=args.status,
                    summary=args.summary,
                    evidence_refs=args.evidence_ref,
                    risk_refs=args.risk_ref,
                    stop_conditions=args.stop_condition,
                    primary_agent=args.primary_agent,
                    upstream_agent=args.upstream_agent,
                    downstream_agent=args.downstream_agent,
                    handoff_chain=args.handoff_agent,
                    escalation_agents=args.escalation_agent,
                    escalation_rules=args.escalation_rule,
                    acceptance_signal=args.acceptance_signal,
                    time_budget=args.time_budget,
                    token_budget=args.token_budget,
                    wip_limit=args.wip_limit,
                )
                print(json.dumps(result, indent=2, ensure_ascii=False))
        elif args.command == "task":
            if args.task_command == "create":
                path = create_project_task(
                    bundle,
                    args.title,
                    args.project,
                    args.requester,
                    args.assignee,
                    args.task_type,
                    args.task_id,
                    args.priority,
                    args.due_at,
                    args.source,
                    args.expected,
                    work_source_type=args.work_source_type,
                    requirement_refs=args.requirement_ref,
                    requirement_object_refs=args.requirement_object_ref,
                    acceptance_criteria_refs=args.acceptance_criteria_ref,
                    defect_refs=args.defect_ref,
                    defect_object_refs=args.defect_object_ref,
                    incident_refs=args.incident_ref,
                    operation_refs=args.operation_ref,
                    knowledge_task_refs=args.knowledge_task_ref,
                    research_question=args.research_question,
                    source_reason=args.source_reason,
                    outcome_slice_ref=args.outcome_slice_ref,
                    pm_agent_id=args.pm_agent,
                    pm_lease_id=args.pm_lease_id,
                    pm_fencing_token=args.pm_fencing_token,
                    pm_source_channel=args.pm_source,
                )
                print(path)
            elif args.task_command == "pull":
                path = pull_project_task(bundle, args.task_id)
                print(path)
            elif args.task_command == "start":
                path = set_project_task_status(
                    bundle,
                    args.task_id,
                    "processing",
                    args.actor,
                    pm_agent_id=args.pm_agent,
                    pm_lease_id=args.pm_lease_id,
                    pm_fencing_token=args.pm_fencing_token,
                    pm_source_channel=args.pm_source,
                )
                print(path)
            elif args.task_command == "fact":
                fact_view = build_task_fact_view(bundle, args.project, args.task_id)
                if args.format == "markdown":
                    status = fact_view["facts"]["status"]
                    print(f"# Task Fact View: {fact_view['taskId']}")
                    print()
                    print(f"- projectId: {fact_view['projectId']}")
                    print(f"- taskRef: {fact_view['taskRef']}")
                    print(f"- status: {status['raw']}")
                    print(f"- explanation: {status['explanation']}")
                    print(f"- nextStepOwner: {status['nextStepOwner']}")
                    print(f"- nextStep: {status['nextStep']}")
                    print()
                    print("## Gaps")
                    for gap in fact_view["gaps"]:
                        print(f"- {gap['type']} {gap['field']}: {gap['message']}")
                    if not fact_view["gaps"]:
                        print("- none")
                else:
                    print(json.dumps(fact_view, indent=2, ensure_ascii=False))
            elif args.task_command == "finish":
                knowledge_draft = None
                if args.knowledge_draft_json and args.knowledge_draft_file:
                    raise KnowledgeError("use either --knowledge-draft-json or --knowledge-draft-file, not both")
                if args.knowledge_draft_json:
                    knowledge_draft = json.loads(args.knowledge_draft_json)
                    if not isinstance(knowledge_draft, dict):
                        raise KnowledgeError("knowledge draft JSON must be an object")
                if args.knowledge_draft_file:
                    knowledge_draft = json.loads(Path(args.knowledge_draft_file).read_text(encoding="utf-8"))
                    if not isinstance(knowledge_draft, dict):
                        raise KnowledgeError("knowledge draft file must contain a JSON object")
                approval_request = None
                if args.approval_request_json and args.approval_request_file:
                    raise KnowledgeError("use either --approval-request-json or --approval-request-file, not both")
                if args.approval_request_json:
                    approval_request = json.loads(args.approval_request_json)
                    if not isinstance(approval_request, dict):
                        raise KnowledgeError("approval request JSON must be an object")
                if args.approval_request_file:
                    approval_request = json.loads(Path(args.approval_request_file).read_text(encoding="utf-8"))
                    if not isinstance(approval_request, dict):
                        raise KnowledgeError("approval request file must contain a JSON object")
                path = finish_project_task(
                    bundle,
                    args.task_id,
                    args.result,
                    args.summary,
                    args.output_ref,
                    args.knowledge_ref,
                    args.evidence_ref,
                    args.next_action,
                    runner_id=args.runner_id,
                    lease_token=args.lease_token,
                    executor_agent=args.executor_agent,
                    tests_or_checks=args.test_or_check,
                    knowledge_draft=knowledge_draft,
                    guide_updated=args.guide_updated,
                    guide_ref=args.guide_ref,
                    guide_feishu_url=args.guide_feishu_url,
                    guide_revision=args.guide_revision,
                    guide_audit_refs=args.guide_audit_ref,
                    handoff_to=args.handoff_to,
                    handoff_summary=args.handoff_summary,
                    artifact_refs=args.artifact_ref,
                    open_risks=args.open_risk,
                    next_suggested_task=args.next_suggested_task,
                    blockers=args.blocker,
                    approval_request=approval_request,
                )
                print(path)
            elif args.task_command == "status":
                print(json.dumps(project_task_status(bundle, args.task_id), indent=2, ensure_ascii=False))
            elif args.task_command == "diagnose":
                print(json.dumps(diagnose_project_task(bundle, args.task_id), indent=2, ensure_ascii=False))
            elif args.task_command == "accept":
                result = accept_project_task_result(
                    bundle,
                    args.task_id,
                    args.decision,
                    args.reviewer,
                    reason=args.reason,
                    human=args.human,
                )
                print(json.dumps(result, indent=2, ensure_ascii=False))
            elif args.task_command == "cancel":
                result = cancel_project_task(
                    bundle,
                    args.task_id,
                    args.actor,
                    args.reason,
                    runner_id=args.runner_id,
                    lease_token=args.lease_token,
                )
                print(json.dumps(result, indent=2, ensure_ascii=False))
            elif args.task_command == "retry":
                result = retry_project_task(
                    bundle,
                    args.task_id,
                    args.actor,
                    args.reason,
                    runner_id=args.runner_id,
                    lease_token=args.lease_token,
                    preferred_runner=args.preferred_runner,
                )
                print(json.dumps(result, indent=2, ensure_ascii=False))
            elif args.task_command == "handoff":
                result = manual_handoff_project_task(
                    bundle,
                    args.task_id,
                    args.actor,
                    args.handoff_to,
                    args.summary,
                    runner_id=args.runner_id,
                    lease_token=args.lease_token,
                    evidence_refs=args.evidence_ref,
                    artifact_refs=args.artifact_ref,
                    next_action=args.next_action,
                    preferred_runner=args.preferred_runner,
                )
                print(json.dumps(result, indent=2, ensure_ascii=False))
        elif args.command == "defect":
            if args.defect_command == "create":
                path = create_defect(
                    bundle,
                    args.title,
                    args.project,
                    args.reporter,
                    severity=args.severity,
                    defect_id=args.defect_id,
                    requirement_refs=args.requirement_ref,
                    source_task_ref=args.source_task_ref,
                    source_result_ref=args.source_result_ref,
                    evidence_refs=args.evidence_ref,
                    expected_behavior=args.expected_behavior,
                    actual_behavior=args.actual_behavior,
                    reproduction_steps=args.reproduction_step,
                )
                print(path)
            elif args.defect_command == "create-fix-task":
                path = create_bugfix_task(
                    bundle,
                    args.defect_id,
                    args.title,
                    args.requester,
                    args.assignee,
                    task_type=args.task_type,
                    priority=args.priority,
                )
                print(path)
        elif args.command == "receiver-review":
            if args.receiver_review_command == "create":
                path = create_receiver_review(
                    bundle,
                    args.project,
                    args.upstream_ref,
                    args.receiver_agent,
                    args.reviewer_agent,
                    args.decision,
                    artifact_refs=args.artifact_ref,
                    checklist=args.check,
                    issues=args.issue,
                    assumptions=args.assumption,
                    review_id=args.review_id,
                )
                print(path)
        elif args.command == "requirement":
            if args.requirement_command == "create":
                path = create_requirement(
                    bundle,
                    args.project,
                    args.source,
                    args.title,
                    args.submitter,
                    args.owner,
                    args.decision_owner,
                    args.sensitivity,
                    args.summary,
                )
                print(path)
            elif args.requirement_command == "update-state":
                raw_patch = args.patch.strip()
                if raw_patch.startswith("{"):
                    patch = json.loads(raw_patch)
                else:
                    patch_path = Path(args.patch)
                    patch = json.loads(patch_path.read_text(encoding="utf-8") if patch_path.exists() else args.patch)
                if not isinstance(patch, dict):
                    raise KnowledgeError("state patch must be a JSON object")
                path = update_requirement_state(bundle, args.requirement_id, patch, args.actor, args.source)
                print(path)
            elif args.requirement_command == "clarify":
                path = create_clarification_round(bundle, args.requirement_id, args.agent, args.recipient)
                print(path)
            elif args.requirement_command == "approve":
                path = approve_requirement(bundle, args.requirement_id, args.owner)
                print(path)
            elif args.requirement_command == "add-criteria":
                path = create_acceptance_criteria(
                    bundle,
                    args.requirement_id,
                    args.description,
                    args.observable_signal,
                    args.verification_method,
                    args.owner,
                    args.criteria_type,
                    status=args.status,
                )
                print(path)
            elif args.requirement_command == "create-task":
                path = create_requirement_task(
                    bundle,
                    args.requirement_id,
                    args.title,
                    args.assignee,
                    args.requester,
                    args.criteria_ref,
                    args.task_type,
                    args.priority,
                )
                print(path)
            elif args.requirement_command == "impact-review":
                path = create_impact_review(bundle, args.requirement_id, args.from_prd, args.to_prd, args.owner, args.status)
                print(path)
            elif args.requirement_command == "tree":
                if args.requirement_tree_command == "import":
                    source_path = Path(args.source)
                    if not source_path.is_absolute():
                        source_path = bundle.root / source_path
                    coverage_path = Path(args.coverage_matrix) if args.coverage_matrix else None
                    if coverage_path and not coverage_path.is_absolute():
                        coverage_path = bundle.root / coverage_path
                    result = requirement_tree_import_records(bundle, args.project, source_path, coverage_path, args.actor, args.version, args.tree_slug)
                    print(json.dumps(result, indent=2, ensure_ascii=False))
                elif args.requirement_tree_command == "validate":
                    problems = validate_requirement_tree_records(bundle)
                    if problems:
                        print("Requirement Tree validation failed:")
                        for problem in problems:
                            print(f"- {problem}")
                        return 2
                    print("Requirement Tree validation passed")
                elif args.requirement_tree_command == "compile":
                    result = compile_requirement_tree_task_queue(bundle, args.tree, args.project, args.actor)
                    print(json.dumps(result, indent=2, ensure_ascii=False))
                elif args.requirement_tree_command == "workbench":
                    if bundle.config_path.exists() and use_api_backend(bundle):
                        query = urlencode({key: value for key, value in {"projectId": args.project, "tree": args.tree}.items() if value})
                        result = api_request(bundle, "GET", "/v0/requirement-tree/workbench" + (f"?{query}" if query else ""))
                    else:
                        result = requirement_tree_workbench_read_model(bundle, args.project, args.tree)
                    print(json.dumps(result, indent=2, ensure_ascii=False))
                elif args.requirement_tree_command == "backfill-existing-work":
                    source_path = Path(args.source)
                    if not source_path.is_absolute():
                        source_path = bundle.root / source_path
                    coverage_path = Path(args.coverage_matrix)
                    if not coverage_path.is_absolute():
                        coverage_path = bundle.root / coverage_path
                    result = backfill_requirement_tree_existing_work(bundle, args.project, coverage_path, args.actor, args.tree, source_path, args.version, args.tree_slug)
                    print(json.dumps(result, indent=2, ensure_ascii=False))
                elif args.requirement_tree_command == "promote":
                    candidate_path = Path(args.candidate)
                    if not candidate_path.is_absolute():
                        candidate_path = bundle.root / candidate_path
                    payload = json.loads(candidate_path.read_text(encoding="utf-8"))
                    result = promote_requirement_tree_traceability(bundle, payload, args.project, args.tree, args.actor, dry_run=not args.write)
                    print(json.dumps(result, indent=2, ensure_ascii=False))
                    if result.get("status") == "rejected":
                        return 2
        elif args.command == "prd":
            if args.prd_command == "generate":
                path = generate_prd_document(bundle, args.requirement_id, args.author_agent, args.reviewer)
                print(path)
            elif args.prd_command == "approve":
                path = approve_prd_document(bundle, args.prd_id, args.reviewer)
                print(path)
        elif args.command == "decision":
            if args.decision_command == "create":
                path = create_decision_request(
                    bundle,
                    args.requirement,
                    args.impact,
                    args.owner,
                    args.context,
                    args.area,
                    args.prd_ref,
                    args.option,
                    args.tradeoffs,
                    args.recommendation,
                    args.deadline,
                )
                print(path)
            elif args.decision_command == "resolve":
                path = resolve_decision(bundle, args.decision_id, args.selected_option, args.rationale, args.approver)
                print(path)
        elif args.command == "scheduler":
            if args.scheduler_command == "tick":
                result = schedule_project_tasks(
                    bundle,
                    args.project,
                    args.actor,
                    args.claim,
                    args.lease_seconds,
                    args.limit,
                )
                print(json.dumps(result, indent=2, ensure_ascii=False))
            elif args.scheduler_command == "autopilot":
                result = run_scheduler_autopilot(
                    bundle,
                    args.project,
                    args.actor,
                    args.max_rounds if args.max_rounds is not None else args.cycles,
                    args.claim_limit,
                    args.lease_seconds,
                    args.claim,
                )
                print(json.dumps(result, indent=2, ensure_ascii=False))
            elif args.scheduler_command == "workbench":
                result = scheduler_workbench_read_model(bundle, args.project, args.task_id)
                print(json.dumps(result, indent=2, ensure_ascii=False))
        elif args.command == "worker":
            if args.worker_command == "run":
                result = run_agent_worker(
                    bundle,
                    args.project,
                    args.agent,
                    args.runner_id,
                    args.limit,
                    args.lease_seconds,
                    args.stage,
                )
                print(json.dumps(result, indent=2, ensure_ascii=False))
        elif args.command == "v1":
            if args.v1_command == "device":
                if args.v1_device_command == "register":
                    path = register_v1_device(bundle, args.device_id, args.name, args.host_type, args.capability, args.workspace)
                    print(path)
                elif args.v1_device_command == "list":
                    print(json.dumps({"apiVersion": "v1", "kind": "V1DeviceList", "devices": list_v1_devices(bundle)}, indent=2, ensure_ascii=False))
            elif args.v1_command == "profile":
                if args.v1_profile_command == "register":
                    path = register_v1_agent_profile(bundle, args.agent, args.project, args.skill)
                    print(path)
            elif args.v1_command == "skill":
                if args.v1_skill_command == "register":
                    path = register_v1_skill(bundle, args.skill_id, args.name, args.allowed_agent, args.risk)
                    print(path)
            elif args.v1_command == "session":
                if args.v1_session_command == "register":
                    path = register_v1_agent_session(bundle, args.project, args.agent, args.session_id, args.capability, device_id=args.device_id)
                    print(path)
                elif args.v1_session_command == "heartbeat":
                    path = heartbeat_v1_agent_session(bundle, args.session_id, args.status, args.task_id)
                    print(path)
                elif args.v1_session_command == "list":
                    print(json.dumps({"apiVersion": "v1", "kind": "V1SessionList", "sessions": list_v1_agent_sessions(bundle, args.project)}, indent=2, ensure_ascii=False))
            elif args.v1_command == "router":
                if args.v1_router_command == "send":
                    payload = json.loads(args.payload_json)
                    path = send_v1_agent_message(bundle, args.project, args.from_agent, args.to_agent, args.type, payload, args.context_ref)
                    print(path)
            elif args.v1_command == "package":
                if args.v1_package_command == "compile":
                    path = compile_v1_task_package(bundle, args.task_id, args.from_agent, args.to_agent, args.project)
                    print(path)
            elif args.v1_command == "runtime":
                if args.v1_runtime_command == "execute":
                    result = execute_v1_task_package(bundle, args.package_id, args.runner, args.agent)
                    print(json.dumps(result, indent=2, ensure_ascii=False))
            elif args.v1_command == "acceptance":
                if args.v1_acceptance_command == "run":
                    result = run_v1_single_machine_acceptance(bundle, args.project, args.actor)
                    print(json.dumps(result, indent=2, ensure_ascii=False))
            elif args.v1_command == "workbench":
                if args.v1_workbench_command == "export":
                    if args.out:
                        path = write_v1_workbench_read_model(bundle, args.project, args.out, args.format)
                        print(path)
                    else:
                        result = v1_workbench_read_model(bundle, args.project)
                        print(json.dumps(result, indent=2, ensure_ascii=False))
        elif args.command == "discussion":
            if args.discussion_command == "create":
                result = create_discussion_session(
                    bundle,
                    args.title,
                    args.project,
                    args.requester,
                    args.topic,
                    args.participant_agent or None,
                    args.related_task_id,
                    args.facilitator_agent,
                    args.max_rounds,
                    not args.not_human_visible,
                )
                print(json.dumps(result, indent=2, ensure_ascii=False))
            elif args.discussion_command == "turn":
                result = submit_discussion_turn(
                    bundle,
                    args.discussion_id,
                    args.agent_id,
                    args.role,
                    args.content,
                    args.stance,
                    args.concern,
                    args.recommendation,
                    args.evidence_ref,
                )
                print(json.dumps(result, indent=2, ensure_ascii=False))
            elif args.discussion_command == "finalize":
                result = finalize_discussion_session(
                    bundle,
                    args.discussion_id,
                    args.facilitator,
                    args.summary,
                    args.consensus,
                    args.decision,
                    args.open_question,
                    args.human_decision_required,
                    args.followup_task_title,
                    args.followup_assignee,
                )
                print(json.dumps(result, indent=2, ensure_ascii=False))
            elif args.discussion_command == "status":
                print(json.dumps(discussion_session_status(bundle, args.discussion_id), indent=2, ensure_ascii=False))
        elif args.command == "notification":
            if args.notification_command == "list":
                result = list_notifications(
                    bundle,
                    status=args.status,
                    recipient=args.recipient,
                    channel=args.channel,
                    message_type=args.message_type,
                    project_id=args.project_id,
                    task_id=args.task_id,
                    discussion_id=args.discussion_id,
                    limit=args.limit,
                )
                print(json.dumps({"apiVersion": "v0.1", "kind": "NotificationList", "notifications": result}, indent=2, ensure_ascii=False))
            elif args.notification_command == "mark":
                result = mark_notification_delivery(
                    bundle,
                    args.notification_id,
                    args.status,
                    args.actor,
                    args.failure_reason,
                    args.delivery_ref,
                )
                print(json.dumps({"apiVersion": "v0.1", "kind": "NotificationRecord", "notification": result}, indent=2, ensure_ascii=False))
        elif args.command == "feedback":
            result = create_operations_feedback(
                bundle,
                args.project,
                args.submitter,
                args.content,
                args.feedback_type,
                args.evidence_ref,
                args.impact,
                args.suggested_next_action,
                args.requirement_ref,
                args.agent_ref,
                args.result_ref,
                args.score,
            )
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif args.command == "admin":
            if args.admin_command == "disable":
                result = disable_governed_asset(
                    bundle,
                    args.object_type,
                    args.object_id,
                    args.actor,
                    args.reason,
                    args.reassign,
                )
                print(json.dumps(result, indent=2, ensure_ascii=False))
        elif args.command == "ops":
            if args.ops_command == "experiment":
                path = create_ops_experiment(
                    bundle,
                    args.project,
                    args.title,
                    args.owner,
                    args.hypothesis,
                    args.audience,
                    args.metric,
                    args.start_at,
                    args.end_at,
                    args.customer_facing,
                )
                print(path)
        elif args.command == "agent-rules":
            if args.agent_rules_command == "issue":
                result = create_operating_rule_issue(
                    bundle,
                    args.title,
                    args.rule_id,
                    args.reporter,
                    args.reason,
                    args.scope,
                    args.proposal,
                    args.source_ref,
                    args.project,
                )
                print(json.dumps(result, indent=2, ensure_ascii=False))
        elif args.command == "tool":
            if args.tool_command == "register":
                path = make_tool(bundle, args.tool_id, args.name, args.owner, args.repo, args.entrypoint, args.risk)
                print(path)
            elif args.tool_command == "invoke":
                if use_api_backend(bundle):
                    result = api_request(
                        bundle,
                        "POST",
                        "/v0/tool/invoke",
                        {
                            "toolId": args.tool_id,
                            "projectId": args.project,
                            "agentId": args.agent,
                            "input": args.input,
                            "execute": args.execute,
                        },
                    )
                else:
                    result = invoke_tool(bundle, args.tool_id, args.project, args.agent, args.input, args.execute)
                print(json.dumps(result, indent=2, ensure_ascii=False))
        elif args.command == "skill":
            if args.skill_command == "register":
                path = make_skill(
                    bundle,
                    args.skill_id,
                    args.name,
                    args.owner,
                    args.purpose,
                    args.scope,
                    args.risk,
                    args.project,
                    args.source_ref,
                )
                print(path)
            elif args.skill_command == "validate":
                problems = validate_skill_registry(bundle)
                if problems:
                    for problem in problems:
                        print(problem)
                    return 1
                print("valid")
        elif args.command == "policy":
            path = make_policy(
                bundle,
                args.policy_id,
                args.title,
                args.agent_id,
                args.owner,
                args.allow_project,
                args.allow_scope,
                args.allow_risk,
            )
            print(path)
        elif args.command == "start":
            path = start_task(bundle, args.project, args.agent, args.task, args.retrieval_limit)
            print(path)
        elif args.command == "finish":
            path = finish_task(bundle, args.project, args.agent, args.summary, args.result, args.no_reusable_lesson, not args.no_tool_update)
            print(path)
        elif args.command == "review":
            if args.review_command == "list":
                queue = list_review_queue(bundle)
                for item in queue:
                    if args.object_type and item["type"] != args.object_type:
                        continue
                    print(f"{item['path']}\t{item['type']}\t{item['status']}\t{item['owner']}\t{item['title']}")
            elif args.review_command == "update":
                if use_api_backend(bundle):
                    print(
                        json.dumps(
                            api_request(
                                bundle,
                                "POST",
                                "/v0/review/update",
                                {"target": args.target, "status": args.status, "reviewer": args.reviewer},
                            ),
                            indent=2,
                            ensure_ascii=False,
                        )
                    )
                else:
                    path = review_path(bundle, Path(args.target), args.status, args.reviewer)
                    print(path)
            elif args.review_command == "apply":
                result = apply_knowledge_review_result(
                    bundle,
                    args.task_id,
                    args.outcome,
                    args.reviewer,
                    args.summary,
                    args.target_ref or None,
                )
                print(json.dumps(result, indent=2, ensure_ascii=False))
            elif args.review_command == "approve":
                result = apply_knowledge_approval_result(
                    bundle,
                    args.task_id,
                    args.outcome,
                    args.approver,
                    args.summary,
                    args.target_ref or None,
                    args.publish_status,
                )
                print(json.dumps(result, indent=2, ensure_ascii=False))
            elif args.review_command == "bulk":
                paths = bulk_review(bundle, args.object_type, args.from_status, args.to_status, args.reviewer, args.limit or None)
                for path in paths:
                    print(path)
        elif args.command == "index":
            if args.index_command == "rebuild":
                count = rebuild_index(bundle)
                print(f"indexed {count} objects")
            elif args.index_command == "search":
                filters = {
                    "type": args.object_type,
                    "status": args.status,
                    "projectId": args.project_id,
                    "agentId": args.agent_id,
                    "toolId": args.tool_id,
                    "riskLevel": args.risk_level,
                    "text": args.text,
                }
                if use_api_backend(bundle):
                    query = urlencode({key: value for key, value in filters.items() if value})
                    rows = api_request(bundle, "GET", "/v0/objects" + (f"?{query}" if query else "")).get("objects", [])
                else:
                    rows = search_index(bundle, filters)
                for row in rows:
                    print(f"{row['path']}\t{row['type']}\t{row['status']}\t{row['title']}")
        elif args.command == "rag":
            if args.rag_command == "rebuild":
                count = rebuild_retrieval_index(bundle)
                print(f"indexed {count} chunks")
            elif args.rag_command == "search":
                if use_api_backend(bundle):
                    params: list[tuple[str, str]] = [("query", args.query), ("limit", str(args.limit))]
                    if args.project_id:
                        params.append(("projectId", args.project_id))
                    params.extend(("scope", scope) for scope in args.scope)
                    rows = api_request(bundle, "GET", f"/v0/rag/search?{urlencode(params)}").get("chunks", [])
                else:
                    rows = search_retrieval(bundle, args.query, project_id=args.project_id, scopes=args.scope, limit=args.limit)
                for row in rows:
                    print(f"{row['score']}\t{row['path']}#{row['chunkId']}\t{row['sourceRef']}")
        elif args.command == "publish":
            payload = {
                "actor": args.actor,
                "reason": args.reason,
                "rebuildGraph": args.rebuild_graph,
            }
            result = api_request(bundle, "POST", "/v0/publish/rebuild", payload) if use_api_backend(bundle) else publish_knowledge_bundle(bundle, args.actor, args.reason, args.rebuild_graph)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif args.command == "material":
            if args.material_command == "ingest":
                content = args.content
                if args.content_file:
                    content = Path(args.content_file).read_text(encoding="utf-8")
                result = create_source_material(
                    bundle,
                    args.title,
                    args.source_ref,
                    args.submitter,
                    args.project,
                    args.material_type,
                    args.storage_ref,
                    content,
                    args.license_hint,
                    args.sensitivity,
                    args.extraction_tool,
                    args.extraction_status,
                    args.create_task,
                    args.assignee,
                )
                print(json.dumps(result, indent=2, ensure_ascii=False))
        elif args.command == "graph":
            if args.graph_command == "export":
                print(json.dumps(export_graph_snapshot(bundle, args.actor), indent=2, ensure_ascii=False))
            elif args.graph_command == "impact":
                print(json.dumps(graph_impact(bundle, args.ref, args.actor, args.rebuild), indent=2, ensure_ascii=False))
        elif args.command == "conflict":
            if args.conflict_command == "create":
                path = create_conflict(bundle, args.conflict_type, args.owner, args.summary, args.affected)
                print(path)
            elif args.conflict_command == "resolve":
                path = resolve_conflict(bundle, Path(args.target), args.owner, args.resolution)
                print(path)
        elif args.command == "audit":
            if args.audit_command == "search":
                if use_api_backend(bundle):
                    query = urlencode(
                        {
                            key: value
                            for key, value in {
                                "projectId": args.project_id,
                                "agentId": args.agent_id,
                                "toolId": args.tool_id,
                                "target": args.target,
                            }.items()
                            if value
                        }
                    )
                    rows = api_request(bundle, "GET", "/v0/audit" + (f"?{query}" if query else "")).get("auditLogs", [])
                else:
                    rows = search_audit_logs(bundle, args.project_id, args.agent_id, args.tool_id, args.target)
                for row in rows:
                    print(f"{row['path']}\t{row['action']}\t{row['actor']}\t{row['targetRef']}\t{row['policyResult']}")
        elif args.command == "metrics":
            path = create_metrics_report(bundle, args.owner)
            print(path)
        elif args.command == "stale":
            paths = detect_stale(bundle, args.owner)
            for path in paths:
                print(path)
        elif args.command == "eval":
            if args.eval_command == "case":
                path = create_eval_case(bundle, args.eval_id, args.title, args.owner, args.target_ref, args.input, args.expected)
                print(path)
            elif args.eval_command == "run":
                path = run_eval_case(bundle, args.eval_id, args.actual, args.runner, args.severity)
                print(path)
        elif args.command == "backup":
            if args.backup_command == "create":
                path = create_backup(bundle, Path(args.output) if args.output else None)
                print(path)
            elif args.backup_command == "restore":
                paths = restore_backup(bundle, Path(args.archive), args.overwrite)
                for path in paths:
                    print(path)
        elif args.command == "api":
            if args.api_command == "export":
                result = api_request(bundle, "GET", "/v0/snapshot") if use_api_backend(bundle) else export_api_snapshot(bundle)
                print(json.dumps(result, indent=2, ensure_ascii=False))
            elif args.api_command == "serve":
                serve(bundle, args.host, args.port)
        elif args.command == "gateway":
            if args.gateway_command == "context":
                if use_api_backend(bundle):
                    result = api_request(bundle, "POST", "/v0/gateway/context", {"projectId": args.project, "agentId": args.agent, "task": args.task})
                else:
                    result = gateway_context(bundle, args.project, args.agent, args.task)
                print(json.dumps(result, indent=2, ensure_ascii=False))
        elif args.command == "validate":
            problems = validate_bundle(bundle)
            if problems:
                for problem in problems:
                    print(problem)
                return 1
            print("valid")
        return 0
    except PMControlLeaseError as exc:
        print(
            json.dumps(
                {
                    "apiVersion": "v0.1",
                    "kind": "Error",
                    "errorCode": exc.error_code,
                    "message": str(exc),
                    "auditRef": exc.audit_ref,
                    "nextAction": exc.next_action,
                },
                indent=2,
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return 2
    except KnowledgeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
