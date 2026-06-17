from __future__ import annotations

import json
import hashlib
import math
import os
import re
import shutil
import sqlite3
import subprocess
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATUS_VALUES = {
    "draft",
    "testing",
    "verified",
    "approved",
    "stale_candidate",
    "stale",
    "deprecated",
    "blocked",
    "rejected",
    "active",
    "open",
    "resolved",
}

TYPE_VALUES = {
    "Project",
    "Agent",
    "ToolAsset",
    "KnowledgeItem",
    "SourceMaterial",
    "AgentRun",
    "Decision",
    "Workflow",
    "Prompt",
    "AuditLog",
    "Policy",
    "ConflictRecord",
    "EvalCase",
    "EvalRun",
    "MetricsReport",
}

SECRET_KEYS = ("token", "secret", "password", "passwd", "credential", "api_key", "apikey", "key")
COLLECTION_NAMES = {"index.md", "log.md", "decisions.md", "lessons.md", "agents.md", "tools.md"}
RETRIEVAL_VECTOR_DIMS = 64
KNOWLEDGE_SYSTEM_CATEGORIES = {"policies", "audit", "evals", "eval-runs", "conflicts", "metrics"}
KNOWLEDGE_CONTENT_CATEGORIES = {"company", "engineering", "product", "business", "operations", "research", "customer"}
KNOWLEDGE_ALLOWED_CATEGORIES = KNOWLEDGE_SYSTEM_CATEGORIES | KNOWLEDGE_CONTENT_CATEGORIES
KNOWLEDGE_ITEM_REQUIRED_FIELDS = {"type", "title", "timestamp", "owner", "status", "scope", "sourceRef", "confidence"}


class KnowledgeError(RuntimeError):
    pass


@dataclass(frozen=True)
class Bundle:
    root: Path

    @property
    def zz_dir(self) -> Path:
        return self.root / ".zhenzhi"

    @property
    def config_path(self) -> Path:
        return self.zz_dir / "config.json"

    @property
    def context_path(self) -> Path:
        return self.zz_dir / "context" / "current.md"

    @property
    def db_path(self) -> Path:
        return self.zz_dir / "index.sqlite3"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def unique_time_id(prefix: str) -> str:
    return prefix + "." + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def slug(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9._-]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    if not value:
        raise KnowledgeError("id cannot be empty")
    return value


def find_bundle_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    for parent in [current, *current.parents]:
        if (parent / "index.md").exists() and (parent / "AGENTS.md").exists():
            return parent
    return current


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8")


def append_text(path: Path, content: str) -> None:
    ensure_dir(path.parent)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(content)


def load_config(bundle: Bundle) -> dict[str, Any]:
    if not bundle.config_path.exists():
        raise KnowledgeError("missing .zhenzhi/config.json; run zhenzhi-knowledge init")
    return json.loads(read_text(bundle.config_path))


def save_config(bundle: Bundle, config: dict[str, Any]) -> None:
    ensure_dir(bundle.zz_dir)
    write_text(bundle.config_path, json.dumps(config, indent=2, ensure_ascii=False) + "\n")


def default_config(bundle: Bundle, user_id: str, ai_tool: str, agent_id: str, remote: str | None) -> dict[str, Any]:
    return {
        "schemaVersion": "v0.1",
        "userId": user_id,
        "defaultAiTool": ai_tool,
        "defaultAgentId": agent_id,
        "defaultProjectId": "",
        "entrypointPath": ".zhenzhi/agent-entrypoint.md",
        "activeProfile": "local",
        "profiles": {
            "local": {
                "backend": "git",
                "knowledgeRepo": str(bundle.root),
                "remote": remote or "",
            },
            "staging": {
                "backend": "api",
                "apiBaseUrl": "${ZHENZHI_KNOWLEDGE_API_STAGING}",
            },
            "production": {
                "backend": "api",
                "apiBaseUrl": "${ZHENZHI_KNOWLEDGE_API_PROD}",
            },
        },
    }


def render_local_start_prompt(ai_tool: str, project_id: str, agent_id: str) -> str:
    tool_name = "Codex" if ai_tool == "codex" else "Antigravity" if ai_tool == "antigravity" else ai_tool
    return f"""# {tool_name} Knowledge Start

Use this file before formal work in this repository.

```txt
projectId: {project_id or "<project-id>"}
agentId: {agent_id}
task: <task>

Before work:
1. Run `zhenzhi-knowledge sync pull`.
2. Run `zhenzhi-knowledge start --project {project_id or "<project-id>"} --agent {agent_id} --task "<task>"`.
3. Read `.zhenzhi/context/current.md`.

During work:
- Use only registered ToolAsset records.
- Respect Policy Result, allowed scopes, and allowed tool risk levels.
- Preserve sourceRef for knowledge used.

After work:
1. Run `zhenzhi-knowledge finish --project {project_id or "<project-id>"} --agent {agent_id} --summary "<summary>"`.
2. State knowledge refs used.
3. State drafts or ToolAsset updates written.
```
"""


def render_agent_entrypoint(bundle: Bundle, config: dict[str, Any]) -> str:
    active_name = config.get("activeProfile", "local")
    active_profile = config.get("profiles", {}).get(active_name, {})
    agent_id = config.get("defaultAgentId", "")
    project_id = config.get("defaultProjectId", "")
    remote = active_profile.get("remote", "")
    api_base = active_profile.get("apiBaseUrl", "")
    return f"""# Zhenzhi Knowledge Agent Entrypoint

This file connects local AI tools to the company knowledge bundle.

## Identity

- userId: {config.get("userId", "")}
- defaultAiTool: {config.get("defaultAiTool", "")}
- defaultAgentId: {agent_id}
- defaultProjectId: {project_id or "unset"}

## Repository

- knowledgeRepo: {bundle.root}
- remote: {remote or "unset"}
- activeProfile: {active_name}
- backend: {active_profile.get("backend", "")}
- apiBaseUrl: {api_base or "unset"}

## Required Workflow

Before work:

```bash
zhenzhi-knowledge sync pull
zhenzhi-knowledge start --project {project_id or "<project-id>"} --agent {agent_id} --task "<task>"
```

Then read:

```bash
.zhenzhi/context/current.md
```

During work:

- Search knowledge with `zhenzhi-knowledge rag search --query "<query>"`.
- Use only registered tools from the context pack or `zhenzhi-knowledge index search --type ToolAsset`.
- Register reusable tools with `zhenzhi-knowledge tool register`.
- Write only structured draft knowledge. Do not use this repository as a raw file dump.
- Put KnowledgeItem files under `knowledge/<category>/` with sourceRef, confidence, status, owner, and scope.
- Keep raw documents, screenshots, transcripts, exports, and temporary notes outside the knowledge bundle until they are summarized and reviewed.
- Do not store secrets in knowledge files, prompts, logs, or audit details.
- Do not promote facts or tools directly to verified/approved without review.

After work:

```bash
zhenzhi-knowledge finish --project {project_id or "<project-id>"} --agent {agent_id} --summary "<summary>"
zhenzhi-knowledge sync push
```

## Useful Commands

```bash
zhenzhi-knowledge status
zhenzhi-knowledge index rebuild
zhenzhi-knowledge rag rebuild
zhenzhi-knowledge review list
zhenzhi-knowledge audit search --agent-id {agent_id}
```
"""


def install_connector(
    bundle: Bundle,
    user_id: str,
    ai_tool: str,
    agent_id: str,
    remote: str,
    default_project: str,
    register_agent: bool = False,
    agent_name: str = "",
    purpose: str = "local AI development",
    rebuild_indexes: bool = True,
) -> list[Path]:
    config = default_config(bundle, user_id, ai_tool, agent_id, remote)
    config["defaultProjectId"] = slug(default_project) if default_project else ""
    save_config(bundle, config)

    written: list[Path] = [bundle.config_path]
    write_text(bundle.zz_dir / "agent-entrypoint.md", render_agent_entrypoint(bundle, config))
    written.append(bundle.zz_dir / "agent-entrypoint.md")
    write_text(bundle.zz_dir / "codex-start.md", render_local_start_prompt("codex", config["defaultProjectId"], agent_id))
    written.append(bundle.zz_dir / "codex-start.md")
    write_text(bundle.zz_dir / "antigravity-start.md", render_local_start_prompt("antigravity", config["defaultProjectId"], agent_id))
    written.append(bundle.zz_dir / "antigravity-start.md")

    if register_agent:
        agent_path = bundle.root / "agents" / f"{slug(agent_id)}.md"
        if not agent_path.exists():
            written.append(make_agent(bundle, agent_id, agent_name or agent_id, user_id, ai_tool, purpose))

    if rebuild_indexes:
        rebuild_index(bundle)
        rebuild_retrieval_index(bundle)
        written.append(bundle.db_path)

    return written


def scan_for_secret_values(path: Path) -> list[str]:
    problems: list[str] = []
    if not path.exists() or not path.is_file():
        return problems
    text = read_text(path)
    for line_no, line in enumerate(text.splitlines(), 1):
        lower = line.lower()
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        if any(term in key.lower() for term in SECRET_KEYS) and value.strip() not in {"", "[]", "null", "false"}:
            problems.append(f"{path}:{line_no}: possible secret value in {key.strip()}")
    return problems


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    raw = text[4:end]
    body = text[end + 5 :]
    return parse_simple_yaml(raw), body


def parse_simple_yaml(raw: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
    current_key: str | None = None
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith("  - ") and current_key:
            data.setdefault(current_key, []).append(line[4:].strip().strip('"'))
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        current_key = key
        if value == "":
            data[key] = []
        elif value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            data[key] = [] if not inner else [part.strip().strip('"') for part in inner.split(",")]
        elif value in {"true", "false"}:
            data[key] = value == "true"
        else:
            data[key] = value.strip('"')
    return data


def yaml_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, list):
        if not value:
            return "[]"
        return "\n" + "\n".join(f"  - {item}" for item in value)
    if value is None:
        return ""
    text = str(value)
    if text == "" or any(ch in text for ch in [":", "#", "[", "]", "{", "}", "\n"]):
        return json.dumps(text, ensure_ascii=False)
    return text


def render_doc(frontmatter: dict[str, Any], body: str) -> str:
    lines = ["---"]
    for key, value in frontmatter.items():
        rendered = yaml_value(value)
        if rendered.startswith("\n"):
            lines.append(f"{key}:{rendered}")
        else:
            lines.append(f"{key}: {rendered}")
    lines.append("---")
    lines.append("")
    lines.append(body.strip() + "\n")
    return "\n".join(lines)


def update_index(index_path: Path, title: str, ref: str) -> None:
    ensure_dir(index_path.parent)
    if not index_path.exists():
        write_text(index_path, f"# {index_path.parent.name.title()} Index\n\n")
    text = read_text(index_path)
    entry = f"- [{title}]({ref})"
    if entry not in text:
        append_text(index_path, entry + "\n")


def append_log(bundle: Bundle, message: str, log_path: Path | None = None) -> None:
    path = log_path or bundle.root / "log.md"
    if not path.exists():
        write_text(path, "# Log\n\n")
    append_text(path, f"- {utc_now()} {message}\n")


def create_audit_log(
    bundle: Bundle,
    actor: str,
    action: str,
    target_ref: str,
    before: str = "",
    after: str = "",
    policy_result: str = "",
    details: str = "",
) -> Path:
    audit_dir = bundle.root / "knowledge" / "audit"
    ensure_dir(audit_dir)
    audit_id = unique_time_id("audit")
    audit_path = audit_dir / f"{audit_id}.md"
    audit_fm = {
        "type": "AuditLog",
        "title": audit_id,
        "timestamp": utc_now(),
        "auditId": audit_id,
        "actor": actor,
        "action": action,
        "targetRef": target_ref,
        "before": before,
        "after": after,
        "policyResult": policy_result,
    }
    body = f"## Details\n\n{details or 'n/a'}\n"
    write_text(audit_path, render_doc(audit_fm, body))
    append_log(bundle, f"audit {action} {target_ref} {policy_result}")
    return audit_path


def make_project(bundle: Bundle, project_id: str, name: str, owner: str) -> Path:
    pid = slug(project_id)
    project_dir = bundle.root / "projects" / pid
    ensure_dir(project_dir)
    write_text(project_dir / "index.md", f"# {name}\n\n- [Project](project.md)\n- [Decisions](decisions.md)\n- [Lessons](lessons.md)\n- [Agents](agents.md)\n- [Tools](tools.md)\n")
    write_text(project_dir / "log.md", f"# {name} Log\n\n")
    frontmatter = {
        "type": "Project",
        "title": name,
        "description": f"Project context for {name}.",
        "timestamp": utc_now(),
        "projectId": pid,
        "owner": owner,
        "status": "draft",
        "scope": "project",
        "members": [],
        "relatedRepos": [],
        "relatedAgents": [],
        "relatedTools": [],
    }
    body = "## Goal\n\nTBD.\n\n## Scope\n\nTBD.\n\n## Current Focus\n\nTBD.\n"
    write_text(project_dir / "project.md", render_doc(frontmatter, body))
    for name_file, heading in [("decisions.md", "Decisions"), ("lessons.md", "Lessons"), ("agents.md", "Agents"), ("tools.md", "Tools")]:
        write_text(project_dir / name_file, f"# {heading}\n\n")
    update_index(bundle.root / "projects" / "index.md", name, f"{pid}/project.md")
    append_log(bundle, f"registered Project {pid}")
    append_log(bundle, f"registered Project {pid}", project_dir / "log.md")
    return project_dir / "project.md"


def make_agent(bundle: Bundle, agent_id: str, name: str, owner: str, ai_tool: str, purpose: str) -> Path:
    aid = slug(agent_id)
    path = bundle.root / "agents" / f"{aid}.md"
    frontmatter = {
        "type": "Agent",
        "title": name,
        "description": purpose,
        "timestamp": utc_now(),
        "agentId": aid,
        "owner": owner,
        "aiTool": ai_tool,
        "status": "draft",
        "riskLevel": "L1",
        "allowedProjects": [],
        "allowedTools": [],
        "allowedKnowledgeScopes": ["company", "engineering"],
        "humanApprovalRequired": True,
    }
    body = "## Purpose\n\n" + purpose + "\n\n## Operating Notes\n\n- Must run start before formal work.\n- Must run finish after formal work.\n"
    write_text(path, render_doc(frontmatter, body))
    update_index(bundle.root / "agents" / "index.md", name, f"{aid}.md")
    append_log(bundle, f"registered Agent {aid}")
    return path


def make_tool(bundle: Bundle, tool_id: str, name: str, owner: str, repo: str, entrypoint: str, risk: str) -> Path:
    tid = slug(tool_id)
    normalized_risk = risk.upper()
    if normalized_risk not in {"L1", "L2", "L3", "L4", "L5"}:
        raise KnowledgeError(f"unknown tool risk level: {risk}")
    approval_required = normalized_risk in {"L3", "L4", "L5"}
    path = bundle.root / "tools" / f"{tid}.md"
    frontmatter = {
        "type": "ToolAsset",
        "title": name,
        "description": f"Reusable tool asset: {name}.",
        "resource": repo,
        "timestamp": utc_now(),
        "toolId": tid,
        "owner": owner,
        "repoRef": repo,
        "entrypoint": entrypoint,
        "version": "0.1.0",
        "status": "testing",
        "scope": "company",
        "riskLevel": normalized_risk,
        "invocationPolicy": "approval_required" if approval_required else "agent_policy_allowed",
        "requiresApproval": ["call_high_risk_tool"] if approval_required else [],
        "executionMode": "dry_run_default",
        "allowedAgents": [],
        "allowedProjects": [],
        "secretsRequired": [],
        "knownIssues": [],
        "lastVerifiedAt": "",
    }
    body = "## Usage\n\nTBD.\n\n## Input Schema\n\nTBD.\n\n## Output Schema\n\nTBD.\n\n## Notes\n\nTBD.\n"
    write_text(path, render_doc(frontmatter, body))
    update_index(bundle.root / "tools" / "index.md", name, f"{tid}.md")
    append_log(bundle, f"registered ToolAsset {tid}")
    return path


def make_policy(
    bundle: Bundle,
    policy_id: str,
    title: str,
    agent_id: str,
    owner: str,
    allowed_projects: list[str],
    allowed_scopes: list[str],
    allowed_risks: list[str],
) -> Path:
    pid = slug(policy_id)
    path = bundle.root / "knowledge" / "policies" / f"{pid}.md"
    frontmatter = {
        "type": "Policy",
        "title": title,
        "description": f"Policy for {agent_id}.",
        "timestamp": utc_now(),
        "policyId": pid,
        "agentId": slug(agent_id),
        "owner": owner,
        "status": "draft",
        "scope": "company",
        "allowedProjects": [slug(item) for item in allowed_projects],
        "allowedKnowledgeScopes": allowed_scopes,
        "allowedToolRiskLevels": allowed_risks,
        "writePermissions": ["knowledge:draft", "toolAsset:draft"],
        "requiresApproval": ["publish_verified", "call_L3_tool", "access_customer_confidential"],
    }
    body = "## Notes\n\nPolicy changes require review before active use.\n"
    write_text(path, render_doc(frontmatter, body))
    update_index(bundle.root / "knowledge" / "index.md", title, f"policies/{pid}.md")
    append_log(bundle, f"registered Policy {pid}")
    return path


def load_object(path: Path) -> dict[str, Any]:
    fm, _ = parse_frontmatter(read_text(path))
    return fm


def find_project(bundle: Bundle, project_id: str) -> Path:
    path = bundle.root / "projects" / slug(project_id) / "project.md"
    if not path.exists():
        raise KnowledgeError(f"project not found: {project_id}")
    return path


def find_agent(bundle: Bundle, agent_id: str) -> Path:
    path = bundle.root / "agents" / f"{slug(agent_id)}.md"
    if not path.exists():
        raise KnowledgeError(f"agent not found: {agent_id}")
    return path


def find_tool(bundle: Bundle, tool_id: str) -> Path:
    path = bundle.root / "tools" / f"{slug(tool_id)}.md"
    if not path.exists():
        raise KnowledgeError(f"tool not found: {tool_id}")
    return path


def active_policies_for_agent(bundle: Bundle, agent_id: str) -> list[dict[str, Any]]:
    policies: list[dict[str, Any]] = []
    policy_root = bundle.root / "knowledge" / "policies"
    if not policy_root.exists():
        return policies
    for path in policy_root.glob("*.md"):
        fm = load_object(path)
        if fm.get("type") == "Policy" and fm.get("agentId") == slug(agent_id) and fm.get("status") in {"active", "verified", "approved"}:
            policies.append(fm)
    return policies


def merged_agent_permissions(agent: dict[str, Any], policies: list[dict[str, Any]]) -> dict[str, Any]:
    allowed_projects = set(agent.get("allowedProjects", []) or [])
    allowed_scopes = set(agent.get("allowedKnowledgeScopes", []) or [])
    allowed_risks = set(agent.get("allowedToolRiskLevels", []) or [])
    requires_approval = set(agent.get("requiresApproval", []) or [])
    write_permissions = set(agent.get("writePermissions", []) or [])
    for policy in policies:
        p_projects = set(policy.get("allowedProjects", []) or [])
        p_scopes = set(policy.get("allowedKnowledgeScopes", []) or [])
        p_risks = set(policy.get("allowedToolRiskLevels", []) or [])
        allowed_projects = p_projects if not allowed_projects else (allowed_projects & p_projects if p_projects else allowed_projects)
        allowed_scopes = p_scopes if not allowed_scopes else (allowed_scopes & p_scopes if p_scopes else allowed_scopes)
        allowed_risks = p_risks if not allowed_risks else (allowed_risks & p_risks if p_risks else allowed_risks)
        requires_approval |= set(policy.get("requiresApproval", []) or [])
        write_permissions |= set(policy.get("writePermissions", []) or [])
    return {
        "allowedProjects": sorted(allowed_projects),
        "allowedKnowledgeScopes": sorted(allowed_scopes),
        "allowedToolRiskLevels": sorted(allowed_risks or {"L1"}),
        "requiresApproval": sorted(requires_approval),
        "writePermissions": sorted(write_permissions),
        "policyCount": len(policies),
    }


def project_tools(bundle: Bundle, project_id: str) -> list[dict[str, Any]]:
    tools: list[dict[str, Any]] = []
    for path in (bundle.root / "tools").glob("*.md"):
        fm = load_object(path)
        if fm.get("type") != "ToolAsset":
            continue
        allowed_projects = fm.get("allowedProjects", []) or []
        if not allowed_projects or slug(project_id) in allowed_projects:
            tools.append({"path": rel(path, bundle.root), **fm})
    return tools


def start_task(bundle: Bundle, project_id: str, agent_id: str, task: str, retrieval_limit: int = 5) -> Path:
    project_path = find_project(bundle, project_id)
    agent_path = find_agent(bundle, agent_id)
    project = load_object(project_path)
    agent = load_object(agent_path)
    policies = active_policies_for_agent(bundle, agent_id)
    permissions = merged_agent_permissions(agent, policies)
    allowed = permissions.get("allowedProjects", [])
    if allowed and slug(project_id) not in allowed:
        raise KnowledgeError(f"agent {agent_id} is not allowed for project {project_id}")
    allowed_risks = set(permissions.get("allowedToolRiskLevels", []) or ["L1"])
    visible_tools = [tool for tool in project_tools(bundle, project_id) if not allowed_risks or tool.get("riskLevel", "") in allowed_risks]
    retrieved = search_retrieval(bundle, task, project_id=slug(project_id), scopes=permissions.get("allowedKnowledgeScopes", []) or [], limit=retrieval_limit)
    project_dir = project_path.parent
    context = [
        "# Current Context Pack",
        "",
        f"- generatedAt: {utc_now()}",
        f"- projectId: {slug(project_id)}",
        f"- agentId: {slug(agent_id)}",
        f"- task: {task}",
        "",
        "## Required Reading",
        "",
        f"- Project: {rel(project_path, bundle.root)}",
        f"- Agent: {rel(agent_path, bundle.root)}",
        f"- Decisions: {rel(project_dir / 'decisions.md', bundle.root)}",
        f"- Lessons: {rel(project_dir / 'lessons.md', bundle.root)}",
        f"- Project Agents: {rel(project_dir / 'agents.md', bundle.root)}",
        f"- Project Tools: {rel(project_dir / 'tools.md', bundle.root)}",
        "",
        "## Policy Result",
        "",
        "```json",
        json.dumps(permissions, indent=2, ensure_ascii=False),
        "```",
        "",
        "## Allowed ToolAssets",
        "",
        *[f"- {tool.get('toolId', '')}: {tool.get('title', '')} ({tool.get('riskLevel', '')}) -> {tool.get('path', '')}" for tool in visible_tools],
        "",
        "## Retrieved Context",
        "",
        *[
            "\n".join(
                [
                    f"### {item['path']}#{item['chunkId']}",
                    "",
                    f"- sourceRef: {item['path']}",
                    f"- score: {item['score']}",
                    "",
                    item["text"],
                    "",
                ]
            )
            for item in retrieved
        ],
        "" if retrieved else "No retrieved context.",
        "",
        "## Constraints",
        "",
        "- Read this context pack before work.",
        "- Code changes must go through Git.",
        "- Write AgentRun and draft updates with finish.",
        "- Do not dump raw files or arbitrary notes into knowledge directories.",
        "- New KnowledgeItem content must be structured, categorized, sourced, and reviewable.",
        "- Do not store secrets in knowledge files.",
        "- Do not call unregistered tools.",
        "- Do not call ToolAsset risk levels outside Policy Result.",
        "",
        "## Project Frontmatter",
        "",
        "```json",
        json.dumps(project, indent=2, ensure_ascii=False),
        "```",
        "",
        "## Agent Frontmatter",
        "",
        "```json",
        json.dumps(agent, indent=2, ensure_ascii=False),
        "```",
        "",
    ]
    write_text(bundle.context_path, "\n".join(context))
    append_log(bundle, f"started AgentRun draft for project={slug(project_id)} agent={slug(agent_id)}")
    return bundle.context_path


def finish_task(
    bundle: Bundle,
    project_id: str,
    agent_id: str,
    summary: str,
    result: str = "completed",
    no_reusable_lesson: bool = False,
    tool_update: bool = True,
) -> Path:
    find_project(bundle, project_id)
    agent_path = find_agent(bundle, agent_id)
    agent = load_object(agent_path)
    permissions = merged_agent_permissions(agent, active_policies_for_agent(bundle, agent_id))
    write_permissions = set(permissions.get("writePermissions", []) or [])
    if "knowledge:draft" not in write_permissions:
        raise KnowledgeError(f"agent {agent_id} lacks write permission: knowledge:draft")
    if tool_update and "toolAsset:draft" not in write_permissions:
        raise KnowledgeError(f"agent {agent_id} lacks write permission: toolAsset:draft")
    run_id = unique_time_id("run")
    run_dir = bundle.root / "runs" / slug(project_id)
    ensure_dir(run_dir)
    run_path = run_dir / f"{run_id}.md"
    knowledge_used = extract_source_refs(read_text(bundle.context_path)) if bundle.context_path.exists() else []
    frontmatter = {
        "type": "AgentRun",
        "title": f"{run_id} {slug(project_id)}",
        "description": summary,
        "timestamp": utc_now(),
        "runId": run_id,
        "projectId": slug(project_id),
        "agentId": slug(agent_id),
        "status": "draft",
        "result": result,
        "contextRefs": [".zhenzhi/context/current.md"],
        "toolsUsed": [],
        "knowledgeUsed": knowledge_used,
        "outputRefs": [],
        "codeRefs": [],
        "humanReview": "required",
    }
    body = f"## Summary\n\n{summary}\n\n## Lessons\n\n"
    body += "no reusable lesson\n" if no_reusable_lesson else "- TBD\n"
    body += "\n## Knowledge Gaps\n\n- TBD\n"
    write_text(run_path, render_doc(frontmatter, body))
    draft_dir = bundle.root / "projects" / slug(project_id)
    append_text(draft_dir / "lessons.draft.md", f"\n## {run_id}\n\n{summary}\n\n")
    append_text(draft_dir / "project.update.draft.md", f"\n## {run_id}\n\n{summary}\n\n")
    if tool_update:
        append_text(draft_dir / "tools.update.draft.md", f"\n## {run_id}\n\nNo specific ToolAsset update captured.\n\n")
    update_index(bundle.root / "runs" / "index.md", run_id, f"{slug(project_id)}/{run_id}.md")
    append_log(bundle, f"finished AgentRun {run_id}")
    return run_path


def failed_evals_for_target(bundle: Bundle, target_ref: str) -> list[Path]:
    failed: list[Path] = []
    eval_root = bundle.root / "knowledge" / "eval-runs"
    if not eval_root.exists():
        return failed
    for path in eval_root.glob("*.md"):
        fm = load_object(path)
        if fm.get("type") != "EvalRun":
            continue
        if fm.get("targetRef") == target_ref and fm.get("result") == "fail":
            failed.append(path)
    return failed


def review_path(bundle: Bundle, target: Path, status: str, reviewer: str) -> Path:
    if status not in STATUS_VALUES:
        raise KnowledgeError(f"unknown status: {status}")
    path = target if target.is_absolute() else bundle.root / target
    if not path.exists():
        raise KnowledgeError(f"target not found: {target}")
    text = read_text(path)
    fm, body = parse_frontmatter(text)
    if not fm:
        raise KnowledgeError("target has no frontmatter")
    if status == "approved" and failed_evals_for_target(bundle, rel(path, bundle.root)):
        raise KnowledgeError(f"target has failing EvalRun and cannot be approved: {rel(path, bundle.root)}")
    before = fm.get("status", "")
    fm["status"] = status
    fm["reviewer"] = reviewer
    fm["reviewedAt"] = utc_now()
    write_text(path, render_doc(fm, body))
    audit_dir = bundle.root / "knowledge" / "audit"
    ensure_dir(audit_dir)
    audit_id = unique_time_id("audit")
    audit_path = audit_dir / f"{audit_id}.md"
    audit_fm = {
        "type": "AuditLog",
        "title": audit_id,
        "timestamp": utc_now(),
        "auditId": audit_id,
        "actor": reviewer,
        "action": "review.updateStatus",
        "targetRef": rel(path, bundle.root),
        "before": before,
        "after": status,
        "policyResult": "human_review",
    }
    write_text(audit_path, render_doc(audit_fm, "## Review\n\nStatus changed by human review.\n"))
    append_log(bundle, f"reviewed {rel(path, bundle.root)} {before}->{status}")
    return audit_path


def bulk_review(bundle: Bundle, object_type: str, from_status: str, to_status: str, reviewer: str, limit: int | None = None) -> list[Path]:
    reviewed: list[Path] = []
    queue = list_review_queue(bundle)
    for item in queue:
        if object_type and item["type"] != object_type:
            continue
        if from_status and item["status"] != from_status:
            continue
        audit_path = review_path(bundle, Path(item["path"]), to_status, reviewer)
        reviewed.append(audit_path)
        if limit and len(reviewed) >= limit:
            break
    return reviewed


def list_review_queue(bundle: Bundle) -> list[dict[str, str]]:
    queue: list[dict[str, str]] = []
    object_roots = [bundle.root / name for name in ["projects", "agents", "tools", "knowledge", "runs"]]
    collection_names = {"index.md", "log.md", "decisions.md", "lessons.md", "agents.md", "tools.md"}
    for object_root in object_roots:
        if not object_root.exists():
            continue
        for path in object_root.rglob("*.md"):
            if path.name in collection_names or path.name.endswith(".draft.md"):
                continue
            fm = load_object(path)
            if fm.get("status") in {"draft", "testing", "open", "stale_candidate"}:
                queue.append(
                    {
                        "path": rel(path, bundle.root),
                        "type": fm.get("type", ""),
                        "status": fm.get("status", ""),
                        "title": fm.get("title", ""),
                        "owner": fm.get("owner", ""),
                    }
                )
    return sorted(queue, key=lambda item: item["path"])


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def validate_bundle(bundle: Bundle) -> list[str]:
    problems: list[str] = []
    required = [
        "index.md",
        "log.md",
        "projects/index.md",
        "agents/index.md",
        "tools/index.md",
        "knowledge/index.md",
        "runs/index.md",
    ]
    for item in required:
        if not (bundle.root / item).exists():
            problems.append(f"missing required file: {item}")
    object_roots = [bundle.root / name for name in ["projects", "agents", "tools", "knowledge", "runs"]]
    object_files: list[Path] = []
    for object_root in object_roots:
        if object_root.exists():
            object_files.extend(object_root.rglob("*.md"))
    collection_names = {"index.md", "log.md", "decisions.md", "lessons.md", "agents.md", "tools.md"}
    for path in object_files:
        rel_path = rel(path, bundle.root)
        if ".zhenzhi" in path.parts:
            continue
        if path.name in collection_names or path.name.endswith(".draft.md"):
            problems.extend(scan_for_secret_values(path))
            continue
        text = read_text(path)
        fm, _ = parse_frontmatter(text)
        if not fm:
            problems.append(f"{rel_path}: missing frontmatter")
            continue
        if "type" not in fm:
            problems.append(f"{rel_path}: missing type")
        elif fm["type"] not in TYPE_VALUES:
            problems.append(f"{rel_path}: unknown type {fm['type']}")
        if "status" in fm and fm["status"] not in STATUS_VALUES:
            problems.append(f"{rel_path}: unknown status {fm['status']}")
        if rel_path.startswith("knowledge/"):
            parts = rel_path.split("/")
            category = parts[1] if len(parts) > 1 else ""
            if len(parts) < 3:
                problems.append(f"{rel_path}: knowledge files must live under knowledge/<category>/")
            elif category not in KNOWLEDGE_ALLOWED_CATEGORIES:
                problems.append(f"{rel_path}: unknown knowledge category {category}")
            if fm.get("type") == "KnowledgeItem":
                if category in KNOWLEDGE_SYSTEM_CATEGORIES:
                    problems.append(f"{rel_path}: KnowledgeItem must live under a content category, not {category}")
                for field in sorted(KNOWLEDGE_ITEM_REQUIRED_FIELDS):
                    if not fm.get(field):
                        problems.append(f"{rel_path}: KnowledgeItem missing required field {field}")
        problems.extend(scan_for_secret_values(path))
    return problems


def rebuild_index(bundle: Bundle) -> int:
    ensure_dir(bundle.zz_dir)
    conn = sqlite3.connect(bundle.db_path)
    conn.execute("drop table if exists objects")
    conn.execute(
        "create table objects (path text primary key, type text, title text, status text, owner text, scope text, projectId text, agentId text, toolId text, riskLevel text, updatedAt text)"
    )
    count = 0
    object_roots = [bundle.root / name for name in ["projects", "agents", "tools", "knowledge", "runs"]]
    collection_names = {"index.md", "log.md", "decisions.md", "lessons.md", "agents.md", "tools.md"}
    object_files: list[Path] = []
    for object_root in object_roots:
        if object_root.exists():
            object_files.extend(object_root.rglob("*.md"))
    for path in object_files:
        if ".zhenzhi" in path.parts or path.name in collection_names or path.name.endswith(".draft.md"):
            continue
        fm, _ = parse_frontmatter(read_text(path))
        if not fm or "type" not in fm:
            continue
        conn.execute(
            "insert into objects values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                rel(path, bundle.root),
                fm.get("type", ""),
                fm.get("title", ""),
                fm.get("status", ""),
                fm.get("owner", ""),
                fm.get("scope", ""),
                fm.get("projectId", ""),
                fm.get("agentId", ""),
                fm.get("toolId", ""),
                fm.get("riskLevel", ""),
                fm.get("updatedAt", fm.get("timestamp", "")),
            ),
        )
        count += 1
    conn.commit()
    conn.close()
    return count


def search_index(bundle: Bundle, filters: dict[str, str]) -> list[dict[str, str]]:
    if not bundle.db_path.exists():
        rebuild_index(bundle)
    clauses: list[str] = []
    values: list[str] = []
    for key, value in filters.items():
        if not value:
            continue
        if key == "text":
            clauses.append("(path like ? or title like ?)")
            values.extend([f"%{value}%", f"%{value}%"])
        else:
            clauses.append(f"{key} = ?")
            values.append(value)
    where = " where " + " and ".join(clauses) if clauses else ""
    conn = sqlite3.connect(bundle.db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "select path, type, title, status, owner, scope, projectId, agentId, toolId, riskLevel from objects" + where + " order by path",
        values,
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def object_files(bundle: Bundle) -> list[Path]:
    files: list[Path] = []
    for root_name in ["projects", "agents", "tools", "knowledge", "runs"]:
        root = bundle.root / root_name
        if root.exists():
            files.extend(root.rglob("*.md"))
    return sorted(files)


def is_retrieval_allowed(path: Path, fm: dict[str, Any]) -> bool:
    if path.name in COLLECTION_NAMES or path.name.endswith(".draft.md"):
        return False
    if fm.get("type") == "AuditLog":
        return False
    confidentiality = str(fm.get("confidentiality", fm.get("classification", ""))).lower()
    scope = str(fm.get("scope", "")).lower()
    if "customer_confidential" in {confidentiality, scope}:
        return False
    if fm.get("customerConfidential") is True:
        return False
    return True


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9_\-.]+|[\u4e00-\u9fff]", text.lower())


def vectorize(text: str) -> list[float]:
    vector = [0.0] * RETRIEVAL_VECTOR_DIMS
    for token in tokenize(text):
        bucket = int(hashlib.sha256(token.encode("utf-8")).hexdigest()[:8], 16) % RETRIEVAL_VECTOR_DIMS
        vector[bucket] += 1.0
    length = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / length for value in vector]


def cosine(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right))


def chunk_text(text: str, max_chars: int = 900) -> list[str]:
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        if current and len(current) + len(paragraph) + 2 > max_chars:
            chunks.append(current)
            current = paragraph
        elif current:
            current += "\n\n" + paragraph
        else:
            current = paragraph
    if current:
        chunks.append(current)
    return chunks


def extract_source_refs(text: str) -> list[str]:
    refs: list[str] = []
    for match in re.finditer(r"sourceRef:\s*([^\n]+)", text):
        ref_value = match.group(1).strip()
        if ref_value and ref_value not in refs:
            refs.append(ref_value)
    return refs


def rebuild_retrieval_index(bundle: Bundle) -> int:
    ensure_dir(bundle.zz_dir)
    if not bundle.db_path.exists():
        rebuild_index(bundle)
    conn = sqlite3.connect(bundle.db_path)
    conn.execute("drop table if exists chunks")
    conn.execute(
        "create table chunks (path text, chunkId text, type text, title text, status text, owner text, scope text, projectId text, agentId text, toolId text, text text, vector text, sourceRef text, primary key(path, chunkId))"
    )
    count = 0
    for path in object_files(bundle):
        if ".zhenzhi" in path.parts:
            continue
        full_text = read_text(path)
        fm, body = parse_frontmatter(full_text)
        if not fm or "type" not in fm or not is_retrieval_allowed(path, fm):
            continue
        if scan_for_secret_values(path):
            continue
        for idx, chunk in enumerate(chunk_text(body), 1):
            chunk_id = f"chunk-{idx}"
            conn.execute(
                "insert into chunks values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    rel(path, bundle.root),
                    chunk_id,
                    fm.get("type", ""),
                    fm.get("title", ""),
                    fm.get("status", ""),
                    fm.get("owner", ""),
                    fm.get("scope", ""),
                    fm.get("projectId", ""),
                    fm.get("agentId", ""),
                    fm.get("toolId", ""),
                    chunk,
                    json.dumps(vectorize(chunk)),
                    rel(path, bundle.root),
                ),
            )
            count += 1
    conn.commit()
    conn.close()
    return count


def search_retrieval(bundle: Bundle, query: str, project_id: str = "", scopes: list[str] | None = None, limit: int = 5) -> list[dict[str, Any]]:
    if limit <= 0:
        return []
    if not bundle.db_path.exists():
        rebuild_index(bundle)
    conn = sqlite3.connect(bundle.db_path)
    conn.row_factory = sqlite3.Row
    table_exists = conn.execute("select name from sqlite_master where type='table' and name='chunks'").fetchone()
    conn.close()
    if not table_exists:
        rebuild_retrieval_index(bundle)
    query_vector = vectorize(query)
    query_tokens = set(tokenize(query))
    conn = sqlite3.connect(bundle.db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("select * from chunks").fetchall()
    conn.close()
    allowed_scopes = set(scopes or [])
    scored: list[dict[str, Any]] = []
    for row in rows:
        row_scope = row["scope"]
        row_project = row["projectId"]
        if allowed_scopes and row_scope and row_scope not in allowed_scopes:
            continue
        if project_id and row_project and row_project != project_id:
            continue
        text = row["text"]
        lexical = len(query_tokens & set(tokenize(text))) / max(len(query_tokens), 1)
        semantic = cosine(query_vector, json.loads(row["vector"]))
        score = round((semantic * 0.7) + (lexical * 0.3), 4)
        if score <= 0:
            continue
        item = dict(row)
        item.pop("vector", None)
        item["score"] = score
        scored.append(item)
    scored.sort(key=lambda item: (-item["score"], item["path"], item["chunkId"]))
    return scored[:limit]


def create_conflict(bundle: Bundle, conflict_type: str, owner: str, summary: str, affected: list[str]) -> Path:
    conflict_id = unique_time_id("conflict")
    path = bundle.root / "knowledge" / "conflicts" / f"{conflict_id}.md"
    frontmatter = {
        "type": "ConflictRecord",
        "title": conflict_id,
        "description": summary,
        "timestamp": utc_now(),
        "conflictId": conflict_id,
        "conflictType": conflict_type,
        "owner": owner,
        "status": "open",
        "affectedRefs": affected,
    }
    body = f"## Summary\n\n{summary}\n\n## Resolution\n\nTBD.\n"
    write_text(path, render_doc(frontmatter, body))
    update_index(bundle.root / "knowledge" / "index.md", conflict_id, f"conflicts/{conflict_id}.md")
    append_log(bundle, f"created ConflictRecord {conflict_id}")
    return path


def resolve_conflict(bundle: Bundle, target: Path, owner: str, resolution: str) -> Path:
    path = target if target.is_absolute() else bundle.root / target
    if not path.exists():
        raise KnowledgeError(f"conflict not found: {target}")
    text = read_text(path)
    fm, body = parse_frontmatter(text)
    if fm.get("type") != "ConflictRecord":
        raise KnowledgeError("target is not a ConflictRecord")
    before = fm.get("status", "")
    fm["status"] = "resolved"
    fm["reviewer"] = owner
    fm["resolvedAt"] = utc_now()
    body = body.rstrip() + f"\n\n## Resolution Note\n\n{resolution}\n"
    write_text(path, render_doc(fm, body))
    return create_audit_log(
        bundle,
        owner,
        "conflict.resolve",
        rel(path, bundle.root),
        before=before,
        after="resolved",
        policy_result="human_resolution",
        details=resolution,
    )


def search_audit_logs(bundle: Bundle, project_id: str = "", agent_id: str = "", tool_id: str = "", target: str = "") -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    audit_root = bundle.root / "knowledge" / "audit"
    if not audit_root.exists():
        return rows
    terms = [value for value in [slug(project_id) if project_id else "", slug(agent_id) if agent_id else "", slug(tool_id) if tool_id else "", target] if value]
    for path in sorted(audit_root.glob("*.md")):
        text = read_text(path)
        fm, _ = parse_frontmatter(text)
        if fm.get("type") != "AuditLog":
            continue
        searchable = "\n".join([text, str(fm.get("targetRef", "")), str(fm.get("actor", "")), str(fm.get("action", ""))])
        if terms and not all(term in searchable for term in terms):
            continue
        rows.append(
            {
                "path": rel(path, bundle.root),
                "action": fm.get("action", ""),
                "actor": fm.get("actor", ""),
                "targetRef": fm.get("targetRef", ""),
                "policyResult": fm.get("policyResult", ""),
            }
        )
    return rows


def create_metrics_report(bundle: Bundle, owner: str = "system") -> Path:
    rebuild_index(bundle)
    rows = search_index(bundle, {})
    draft_backlog = sum(1 for row in rows if row.get("status") in {"draft", "testing"})
    stale_count = sum(1 for row in rows if row.get("status") == "stale")
    stale_candidate_count = sum(1 for row in rows if row.get("status") == "stale_candidate")
    testing_tools = sum(1 for row in rows if row.get("type") == "ToolAsset" and row.get("status") == "testing")
    approved_tools = sum(1 for row in rows if row.get("type") == "ToolAsset" and row.get("status") == "approved")
    agent_runs = [row for row in rows if row.get("type") == "AgentRun"]
    unfinished = sum(1 for row in agent_runs if row.get("status") in {"draft", "open"})
    denied_tool_invocations = 0
    approved_tool_invocations = 0
    audit_root = bundle.root / "knowledge" / "audit"
    if audit_root.exists():
        for audit_path in audit_root.glob("*.md"):
            fm = load_object(audit_path)
            if fm.get("action") == "tool.invoke.denied":
                denied_tool_invocations += 1
            elif fm.get("action") == "tool.invoke.allowed":
                approved_tool_invocations += 1
    start_count = 0
    if (bundle.root / "log.md").exists():
        start_count = read_text(bundle.root / "log.md").count("started AgentRun")
    run_success = 0
    run_failure = 0
    for run_path in (bundle.root / "runs").rglob("*.md"):
        if run_path.name == "index.md":
            continue
        fm = load_object(run_path)
        if fm.get("type") != "AgentRun":
            continue
        result = str(fm.get("result", "")).lower()
        if result in {"completed", "success", "passed", "pass"}:
            run_success += 1
        elif result in {"failed", "failure", "error", "blocked"}:
            run_failure += 1
    report_id = unique_time_id("metrics")
    path = bundle.root / "knowledge" / "metrics" / f"{report_id}.md"
    frontmatter = {
        "type": "MetricsReport",
        "title": report_id,
        "description": "Knowledge core operational metrics.",
        "timestamp": utc_now(),
        "reportId": report_id,
        "owner": owner,
        "status": "verified",
        "startCount": start_count,
        "finishCount": len(agent_runs),
        "unfinishedTasks": unfinished,
        "draftBacklog": draft_backlog,
        "staleCount": stale_count,
        "staleCandidateCount": stale_candidate_count,
        "testingTools": testing_tools,
        "approvedTools": approved_tools,
        "deniedToolInvocations": denied_tool_invocations,
        "approvedToolInvocations": approved_tool_invocations,
        "agentRunSuccessCount": run_success,
        "agentRunFailureCount": run_failure,
    }
    body = "\n".join(
        [
            "## Summary",
            "",
            f"- indexed objects: {len(rows)}",
            f"- AgentRun count: {len(agent_runs)}",
            f"- start count: {start_count}",
            f"- unfinished tasks: {unfinished}",
            f"- draft/testing backlog: {draft_backlog}",
            f"- stale knowledge: {stale_count}",
            f"- stale candidates: {stale_candidate_count}",
            f"- testing tools: {testing_tools}",
            f"- approved tools: {approved_tools}",
            f"- approved tool invocations: {approved_tool_invocations}",
            f"- denied tool invocations: {denied_tool_invocations}",
            f"- AgentRun success count: {run_success}",
            f"- AgentRun failure count: {run_failure}",
            "",
        ]
    )
    write_text(path, render_doc(frontmatter, body))
    update_index(bundle.root / "knowledge" / "index.md", report_id, f"metrics/{report_id}.md")
    append_log(bundle, f"created MetricsReport {report_id}")
    return path


def create_backup(bundle: Bundle, output: Path | None = None) -> Path:
    backup_dir = bundle.root / "backups"
    ensure_dir(backup_dir)
    out = output or backup_dir / f"knowledge-backup-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}.zip"
    skip_parts = {".zhenzhi", "__pycache__", ".git"}
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in bundle.root.rglob("*"):
            if not path.is_file():
                continue
            rel_path = path.relative_to(bundle.root)
            if any(part in skip_parts for part in rel_path.parts):
                continue
            if rel_path.parts and rel_path.parts[0] == "backups":
                continue
            archive.write(path, rel_path)
    append_log(bundle, f"created backup {rel(out, bundle.root)}")
    return out


def restore_backup(bundle: Bundle, archive_path: Path, overwrite: bool = False) -> list[Path]:
    archive = archive_path if archive_path.is_absolute() else bundle.root / archive_path
    if not archive.exists():
        raise KnowledgeError(f"backup not found: {archive_path}")
    restored: list[Path] = []
    with zipfile.ZipFile(archive, "r") as zip_file:
        for member in zip_file.infolist():
            target = bundle.root / member.filename
            if target.exists() and not overwrite:
                raise KnowledgeError(f"restore target exists: {member.filename}; pass overwrite")
        for member in zip_file.infolist():
            target = bundle.root / member.filename
            ensure_dir(target.parent)
            with zip_file.open(member) as src, target.open("wb") as dst:
                shutil.copyfileobj(src, dst)
            restored.append(target)
    append_log(bundle, f"restored backup {archive_path}")
    return restored


def create_eval_case(
    bundle: Bundle,
    eval_id: str,
    title: str,
    owner: str,
    target_ref: str,
    input_text: str,
    expected: str,
) -> Path:
    eid = slug(eval_id)
    path = bundle.root / "knowledge" / "evals" / f"{eid}.md"
    frontmatter = {
        "type": "EvalCase",
        "title": title,
        "description": f"Evaluation case for {target_ref}.",
        "timestamp": utc_now(),
        "evalId": eid,
        "owner": owner,
        "status": "verified",
        "targetRef": target_ref,
        "expected": expected,
    }
    body = f"## Input\n\n{input_text}\n\n## Expected\n\n{expected}\n"
    write_text(path, render_doc(frontmatter, body))
    update_index(bundle.root / "knowledge" / "index.md", title, f"evals/{eid}.md")
    append_log(bundle, f"created EvalCase {eid}")
    return path


def run_eval_case(bundle: Bundle, eval_id: str, actual: str, runner: str) -> Path:
    eval_path = bundle.root / "knowledge" / "evals" / f"{slug(eval_id)}.md"
    if not eval_path.exists():
        raise KnowledgeError(f"EvalCase not found: {eval_id}")
    case = load_object(eval_path)
    expected = str(case.get("expected", ""))
    target_ref = str(case.get("targetRef", ""))
    target_version = ""
    target_path = bundle.root / target_ref if target_ref else None
    if target_path and target_path.exists():
        target_fm = load_object(target_path)
        target_version = str(target_fm.get("version", target_fm.get("promptVersion", "")))
    passed = expected in actual if expected else bool(actual)
    run_id = unique_time_id("evalrun")
    path = bundle.root / "knowledge" / "eval-runs" / f"{run_id}.md"
    frontmatter = {
        "type": "EvalRun",
        "title": run_id,
        "description": f"EvalRun for {eval_id}.",
        "timestamp": utc_now(),
        "evalRunId": run_id,
        "evalId": slug(eval_id),
        "targetRef": target_ref,
        "targetVersion": target_version,
        "owner": runner,
        "status": "verified" if passed else "draft",
        "result": "pass" if passed else "fail",
        "score": 1 if passed else 0,
    }
    body = f"## Expected\n\n{expected}\n\n## Actual\n\n{actual}\n"
    write_text(path, render_doc(frontmatter, body))
    update_index(bundle.root / "knowledge" / "index.md", run_id, f"eval-runs/{run_id}.md")
    append_log(bundle, f"created EvalRun {run_id} result={'pass' if passed else 'fail'}")
    if not passed:
        gap_path = bundle.root / "knowledge" / "engineering" / f"eval-failure-{run_id}.md"
        gap_fm = {
            "type": "KnowledgeItem",
            "title": f"Eval failure {run_id}",
            "description": f"Failure case from {eval_id}.",
            "timestamp": utc_now(),
            "owner": runner,
            "status": "draft",
            "scope": "engineering",
            "sourceRef": rel(path, bundle.root),
            "confidence": "high",
            "knowledgeType": "issue",
        }
        write_text(gap_path, render_doc(gap_fm, f"## Failure\n\nExpected `{expected}` but actual was:\n\n{actual}\n"))
    return path


def detect_stale(bundle: Bundle, owner: str = "system") -> list[Path]:
    candidates: list[Path] = []
    tool_versions: dict[str, str] = {}
    for path in (bundle.root / "tools").glob("*.md"):
        fm = load_object(path)
        if fm.get("type") == "ToolAsset":
            tool_versions[fm.get("toolId", path.stem)] = fm.get("version", "")
    for root_name in ["knowledge", "projects"]:
        root = bundle.root / root_name
        if not root.exists():
            continue
        for path in root.rglob("*.md"):
            if path.name in {"index.md", "log.md", "decisions.md", "lessons.md", "agents.md", "tools.md"} or path.name.endswith(".draft.md"):
                continue
            text = read_text(path)
            fm, body = parse_frontmatter(text)
            if not fm or fm.get("status") != "verified":
                continue
            linked_tool = fm.get("toolId") or fm.get("relatedTool")
            known_version = fm.get("toolVersion")
            should_mark = False
            reason = ""
            if linked_tool and known_version and tool_versions.get(linked_tool) and tool_versions[linked_tool] != known_version:
                should_mark = True
                reason = f"tool version changed: {linked_tool} {known_version}->{tool_versions[linked_tool]}"
            if should_mark:
                fm["status"] = "stale_candidate"
                fm["staleReason"] = reason
                fm["staleDetectedAt"] = utc_now()
                fm["reviewer"] = owner
                write_text(path, render_doc(fm, body))
                candidates.append(path)
                audit_dir = bundle.root / "knowledge" / "audit"
                ensure_dir(audit_dir)
                audit_id = unique_time_id("audit") + f".{len(candidates)}"
                audit_path = audit_dir / f"{audit_id}.md"
                audit_fm = {
                    "type": "AuditLog",
                    "title": audit_id,
                    "timestamp": utc_now(),
                    "auditId": audit_id,
                    "actor": owner,
                    "action": "stale.detect",
                    "targetRef": rel(path, bundle.root),
                    "before": "verified",
                    "after": "stale_candidate",
                    "policyResult": "auto_candidate",
                }
                write_text(audit_path, render_doc(audit_fm, f"## Reason\n\n{reason}\n"))
    if candidates:
        append_log(bundle, f"detected stale candidates: {len(candidates)}")
    return candidates


def invoke_tool(
    bundle: Bundle,
    tool_id: str,
    project_id: str,
    agent_id: str,
    input_text: str,
    execute: bool = False,
) -> dict[str, Any]:
    project_path = find_project(bundle, project_id)
    agent_path = find_agent(bundle, agent_id)
    actor = slug(agent_id)
    target_ref = f"tools/{slug(tool_id)}.md"
    try:
        tool_path = find_tool(bundle, tool_id)
    except KnowledgeError as exc:
        create_audit_log(bundle, actor, "tool.invoke.denied", target_ref, after="denied", policy_result="unregistered_tool", details=str(exc))
        raise
    project = load_object(project_path)
    agent = load_object(agent_path)
    tool = load_object(tool_path)
    permissions = merged_agent_permissions(agent, active_policies_for_agent(bundle, agent_id))
    allowed_projects = permissions.get("allowedProjects", []) or []
    allowed_risks = permissions.get("allowedToolRiskLevels", []) or ["L1"]
    allowed_agents = tool.get("allowedAgents", []) or []
    tool_projects = tool.get("allowedProjects", []) or []
    risk = tool.get("riskLevel", "")
    deny_reason = ""
    if allowed_projects and slug(project_id) not in allowed_projects:
        deny_reason = "agent_project_not_allowed"
    elif tool_projects and slug(project_id) not in tool_projects:
        deny_reason = "tool_project_not_allowed"
    elif allowed_agents and slug(agent_id) not in allowed_agents:
        deny_reason = "tool_agent_not_allowed"
    elif risk not in allowed_risks:
        deny_reason = "tool_risk_not_allowed"
    elif execute and tool.get("status") != "approved":
        deny_reason = "tool_not_approved_for_execution"
    if deny_reason:
        create_audit_log(bundle, actor, "tool.invoke.denied", rel(tool_path, bundle.root), after="denied", policy_result=deny_reason, details=input_text)
        raise KnowledgeError(f"tool invocation denied: {deny_reason}")
    output = ""
    mode = "dry_run"
    entrypoint = str(tool.get("entrypoint", ""))
    if execute:
        if entrypoint.startswith("echo://"):
            output = entrypoint[len("echo://") :]
            mode = "executed"
        else:
            create_audit_log(
                bundle,
                actor,
                "tool.invoke.denied",
                rel(tool_path, bundle.root),
                after="denied",
                policy_result="unsupported_entrypoint_execution",
                details=entrypoint,
            )
            raise KnowledgeError("only echo:// ToolAsset execution is supported by the local safe runtime")
    audit_path = create_audit_log(
        bundle,
        actor,
        "tool.invoke.allowed",
        rel(tool_path, bundle.root),
        after=mode,
        policy_result="allowed",
        details=f"project={project.get('projectId', slug(project_id))}\ninput={input_text}",
    )
    return {
        "apiVersion": "v0.1",
        "kind": "ToolInvocationResult",
        "generatedAt": utc_now(),
        "projectId": slug(project_id),
        "agentId": slug(agent_id),
        "toolId": slug(tool_id),
        "mode": mode,
        "entrypoint": entrypoint,
        "auditRef": rel(audit_path, bundle.root),
        "output": output,
    }


def export_api_snapshot(bundle: Bundle) -> dict[str, Any]:
    rebuild_index(bundle)
    objects = search_index(bundle, {})
    return {
        "apiVersion": "v0.1",
        "kind": "KnowledgeSnapshot",
        "generatedAt": utc_now(),
        "root": str(bundle.root),
        "objects": objects,
    }


def gateway_context(bundle: Bundle, project_id: str, agent_id: str, task: str) -> dict[str, Any]:
    context_path = start_task(bundle, project_id, agent_id, task)
    text = read_text(context_path)
    agent = load_object(find_agent(bundle, agent_id))
    policies = active_policies_for_agent(bundle, agent_id)
    permissions = merged_agent_permissions(agent, policies)
    return {
        "apiVersion": "v0.1",
        "kind": "GatewayContext",
        "generatedAt": utc_now(),
        "contextPath": rel(context_path, bundle.root),
        "projectId": slug(project_id),
        "agentId": slug(agent_id),
        "task": task,
        "policyResult": permissions,
        "context": text,
    }



def git(bundle: Bundle, args: list[str]) -> str:
    if shutil.which("git") is None:
        raise KnowledgeError("git not found")
    proc = subprocess.run(["git", *args], cwd=bundle.root, text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        raise KnowledgeError(proc.stderr.strip() or proc.stdout.strip())
    return proc.stdout.strip()
