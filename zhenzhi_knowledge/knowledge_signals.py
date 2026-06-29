from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .core import (
    Bundle,
    KnowledgeError,
    create_audit_log,
    ensure_dir,
    parse_simple_yaml,
    read_text,
    rel,
    render_doc,
    safe_slug,
    utc_now,
    write_text,
)


KNOWLEDGE_DOMAINS = {
    "engineering",
    "business",
    "operations",
    "tooling",
    "agent-capability",
    "policy-candidate",
    "general",
}
KNOWLEDGE_TYPES = {
    "troubleshooting",
    "checklist",
    "decision",
    "process",
    "pitfall",
    "integration-note",
    "security-note",
    "business-note",
    "tool-note",
    "agent-capability-note",
    "general-note",
}
CONFIDENCE_VALUES = {"low", "medium", "high"}
RISK_VALUES = {"low", "medium", "high"}
DOMAIN_TO_CATEGORY = {
    "engineering": "engineering",
    "business": "business",
    "operations": "operations",
    "tooling": "tooling",
    "agent-capability": "agent-capability",
    "policy-candidate": "policy-candidates",
    "general": "general",
}
REVIEW_TERMS = {
    "客户承诺",
    "公司制度",
    "权限规则",
    "安全策略",
    "法律",
    "财务",
    "税务",
    "合规",
    "tool 权限",
    "agent 行为",
}
SENSITIVE_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"\btoken\b",
        r"\bsecret\b",
        r"\bpassword\b",
        r"\bcredential\b",
        r"\bapi[_-]?key\b",
        r"\baccess[_-]?token\b",
        r"\brefresh[_-]?token\b",
        r"Authorization\s*:",
        r"\bBearer\b",
        r"\bAKIA[0-9A-Z]{8,}\b",
        r"私钥",
        r"密钥",
        r"账号密码",
        r"客户承诺",
        r"合同承诺",
        r"法律意见",
        r"税务结论",
        r"财务结论",
    ]
]


@dataclass
class DistillStats:
    scanned: int = 0
    valid: int = 0
    invalid: int = 0
    distilled: int = 0
    duplicate: int = 0
    already_processed: int = 0
    review_required: int = 0
    generated_paths: list[str] = field(default_factory=list)
    updated_paths: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "scanned": self.scanned,
            "valid": self.valid,
            "invalid": self.invalid,
            "distilled": self.distilled,
            "duplicate": self.duplicate,
            "alreadyProcessed": self.already_processed,
            "reviewRequired": self.review_required,
            "generatedPaths": self.generated_paths,
            "updatedPaths": self.updated_paths,
            "errors": self.errors,
            "warnings": self.warnings,
        }


def distill_signals(bundle: Bundle) -> dict[str, Any]:
    stats = DistillStats()
    state_by_fingerprint = load_state_by_fingerprint(bundle)
    existing_records = load_index_records(bundle)
    existing_search = build_existing_search_records(bundle, existing_records)
    write_audit_jsonl(bundle, "knowledge_signal.scan.started", {"status": "started"})

    for path in discover_signal_paths(bundle):
        stats.scanned += 1
        try:
            raw, body = load_signal(path)
            signal, warnings = normalize_signal(raw, body)
            stats.warnings.extend(f"{rel(path, bundle.root)}: {warning}" for warning in warnings)
            errors = validate_signal(signal)
            if errors:
                stats.invalid += 1
                write_state(bundle, signal_identity(raw, path), path, "invalid", errors=errors, warnings=warnings)
                write_audit_jsonl(bundle, "knowledge_signal.invalid", {"path": rel(path, bundle.root), "errors": errors})
                continue
            stats.valid += 1
            identity = str(signal["signalId"] or signal["candidateId"])
            state_path = signal_state_path(bundle, identity)
            fingerprint = compute_fingerprint(signal)
            if state_path.exists():
                previous = json.loads(read_text(state_path))
                if previous.get("fingerprint") == fingerprint and previous.get("status") in {"distilled", "duplicate", "review_required"}:
                    stats.already_processed += 1
                    write_state(bundle, identity, path, "already_processed", signal=signal, fingerprint=fingerprint, knowledge_id=str(previous.get("knowledgeId") or ""), knowledge_path=str(previous.get("knowledgePath") or ""), duplicate_of=previous.get("duplicateOf"))
                    continue
            if fingerprint in state_by_fingerprint:
                previous = state_by_fingerprint[fingerprint]
                stats.duplicate += 1
                duplicate_of = str(previous.get("knowledgeId") or previous.get("duplicateOf") or "")
                write_state(bundle, identity, path, "duplicate", signal=signal, fingerprint=fingerprint, duplicate_of=duplicate_of, warnings=warnings)
                write_audit_jsonl(bundle, "knowledge_signal.duplicate", {"signalId": identity, "duplicateOf": duplicate_of})
                continue
            similar = find_similar_existing(signal, existing_search)
            if similar:
                stats.duplicate += 1
                write_state(bundle, identity, path, "duplicate", signal=signal, fingerprint=fingerprint, duplicate_of=similar["knowledgeId"], warnings=warnings)
                write_audit_jsonl(bundle, "knowledge_signal.duplicate", {"signalId": identity, "duplicateOf": similar["knowledgeId"]})
                continue

            safety = detect_safety(signal, body)
            if safety["warnings"]:
                warnings.extend(safety["warnings"])
            knowledge_path, knowledge_id = write_knowledge_item(bundle, signal, body, fingerprint, safety)
            stats.distilled += 1
            stats.generated_paths.append(rel(knowledge_path, bundle.root))
            review_required = bool(safety["reviewRequired"])
            if review_required:
                stats.review_required += 1
                review_path = write_review_marker(bundle, signal, knowledge_id, knowledge_path, safety)
                stats.generated_paths.append(rel(review_path, bundle.root))
            gap_paths = write_gap_drafts(bundle, signal, knowledge_id)
            for gap_path in gap_paths:
                stats.generated_paths.append(rel(gap_path, bundle.root))
            update_indexes(bundle, knowledge_path, knowledge_id, signal, fingerprint, safety)
            stats.updated_paths.extend(["knowledge/index.md", "knowledge/index.jsonl"])
            status = "review_required" if review_required else "distilled"
            write_state(bundle, identity, path, status, signal=signal, fingerprint=fingerprint, knowledge_id=knowledge_id, knowledge_path=rel(knowledge_path, bundle.root), warnings=warnings)
            state_by_fingerprint[fingerprint] = {"knowledgeId": knowledge_id, "fingerprint": fingerprint}
            existing_records = load_index_records(bundle)
            existing_search = build_existing_search_records(bundle, existing_records)
            write_audit_jsonl(bundle, "knowledge_signal.distilled", {"signalId": identity, "knowledgeId": knowledge_id, "status": status})
            if review_required:
                write_audit_jsonl(bundle, "knowledge_signal.review_required", {"signalId": identity, "knowledgeId": knowledge_id, "reasons": safety["reasons"]})
        except Exception as exc:  # keep processing other signals
            stats.invalid += 1
            identity = path.stem
            write_state(bundle, identity, path, "invalid", errors=[str(exc)])
            write_audit_jsonl(bundle, "knowledge_signal.invalid", {"path": rel(path, bundle.root), "errors": [str(exc)]})

    if stats.distilled or stats.duplicate or stats.invalid or stats.already_processed:
        try:
            create_audit_log(
                bundle,
                "agent.company-knowledge-core.knowledge-engineering",
                "knowledge_signal.distill_signals",
                "knowledge/.state/distilled-signals",
                after=json.dumps(stats.to_dict(), ensure_ascii=False),
                policy_result="generated",
            )
        except Exception as exc:
            stats.warnings.append(f"audit log skipped: {exc}")
    return stats.to_dict()


def discover_signal_paths(bundle: Bundle) -> list[Path]:
    projects_root = bundle.root / "projects"
    if not projects_root.exists():
        return []
    paths: list[Path] = []
    for project_dir in sorted(path for path in projects_root.iterdir() if path.is_dir()):
        for directory in [".zhenzhi/knowledge-signals", ".zhenzhi/knowledge-candidates"]:
            signal_dir = project_dir / directory
            if signal_dir.exists():
                paths.extend(sorted(signal_dir.glob("*.md")))
    return paths


def load_signal(path: Path) -> tuple[dict[str, Any], str]:
    text = read_text(path)
    if not text.startswith("---\n"):
        raise KnowledgeError("missing YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise KnowledgeError("unterminated YAML frontmatter")
    raw = normalize_block_scalars(text[4:end])
    return parse_simple_yaml(raw), text[end + 5 :]


def normalize_block_scalars(raw: str) -> str:
    lines = raw.splitlines()
    output: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        match = re.match(r"^(\s*)([A-Za-z0-9_-]+):\s*([>|])\s*$", line)
        if not match:
            output.append(line)
            index += 1
            continue
        indent = len(match.group(1))
        key = match.group(2)
        folded = match.group(3) == ">"
        index += 1
        block: list[str] = []
        while index < len(lines):
            nested = lines[index]
            nested_indent = len(nested) - len(nested.lstrip(" "))
            if nested.strip() and nested_indent <= indent:
                break
            block.append(nested[indent + 2 :] if len(nested) >= indent + 2 else "")
            index += 1
        text = " ".join(part.strip() for part in block if part.strip()) if folded else "\n".join(block).strip()
        output.append(f"{' ' * indent}{key}: {json.dumps(text, ensure_ascii=False)}")
    return "\n".join(output)


def normalize_signal(raw: dict[str, Any], body: str) -> tuple[dict[str, Any], list[str]]:
    warnings: list[str] = []
    signal = dict(raw)
    raw_missing = [field for field in ["skillImpact", "toolImpact", "humanOwnerConfirmationRequired"] if field not in raw]
    signal.setdefault("signalId", "")
    signal.setdefault("candidateId", "")
    signal["knowledgeDomain"] = normalize_enum(str(signal.get("knowledgeDomain") or ""), KNOWLEDGE_DOMAINS, "general", warnings, "knowledgeDomain")
    signal["knowledgeType"] = normalize_enum(str(signal.get("knowledgeType") or ""), KNOWLEDGE_TYPES, "general-note", warnings, "knowledgeType")
    signal["confidence"] = normalize_enum(str(signal.get("confidence") or ""), CONFIDENCE_VALUES, "medium", warnings, "confidence")
    risk = str(signal.get("riskLevel") or "").strip().lower()
    if not risk:
        risk = "medium" if bool(signal.get("humanOwnerConfirmationRequired")) else "low"
    signal["riskLevel"] = normalize_enum(risk, RISK_VALUES, "medium", warnings, "riskLevel")
    signal["appliesWhen"] = list_value(signal.get("appliesWhen"))
    signal["doesNotApplyWhen"] = list_value(signal.get("doesNotApplyWhen"))
    signal["sourceRefs"] = list_value(signal.get("sourceRefs"))
    signal["evidenceRefs"] = list_value(signal.get("evidenceRefs"))
    signal["keywords"] = list_value(signal.get("keywords"))
    signal["skillImpact"] = normalize_impact(signal.get("skillImpact"))
    signal["toolImpact"] = normalize_impact(signal.get("toolImpact"))
    signal["humanOwnerConfirmationRequired"] = bool(signal.get("humanOwnerConfirmationRequired"))
    signal["_rawMissing"] = raw_missing
    signal["_body"] = body.strip()
    return signal, warnings


def normalize_enum(value: str, allowed: set[str], fallback: str, warnings: list[str], field_name: str) -> str:
    normalized = value.strip().lower().replace("_", "-")
    aliases = {
        "policy": "policy-candidate",
        "agent": "agent-capability",
        "tool": "tooling",
        "tools": "tooling",
        "note": "general-note",
        "general": "general-note" if field_name == "knowledgeType" else "general",
    }
    normalized = aliases.get(normalized, normalized)
    if normalized in allowed:
        return normalized
    warnings.append(f"{field_name} normalized from {value or '<empty>'} to {fallback}")
    return fallback


def normalize_impact(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {"hasImpact": False, "suggestedImpact": "", "autoApplyAllowed": False}
    return {
        "hasImpact": bool(value.get("hasImpact")),
        "suggestedImpact": str(value.get("suggestedImpact") or ""),
        "autoApplyAllowed": False,
    }


def list_value(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if value is None or value == "":
        return []
    return [str(value).strip()]


def validate_signal(signal: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not (signal.get("signalId") or signal.get("candidateId")):
        errors.append("missing signalId or candidateId")
    for field_name in ["sourceProjectId", "title", "knowledgeDomain", "candidateConclusion", "confidence"]:
        if not str(signal.get(field_name) or "").strip():
            errors.append(f"missing {field_name}")
    for field_name in ["appliesWhen", "sourceRefs", "evidenceRefs"]:
        if not signal.get(field_name):
            errors.append(f"missing {field_name}")
    for field_name in ["skillImpact", "toolImpact"]:
        if field_name in signal.get("_rawMissing", []):
            errors.append(f"missing {field_name}")
    if "humanOwnerConfirmationRequired" in signal.get("_rawMissing", []):
        errors.append("missing humanOwnerConfirmationRequired")
    return errors


def signal_identity(raw: dict[str, Any], path: Path) -> str:
    return str(raw.get("signalId") or raw.get("candidateId") or path.stem)


def compute_fingerprint(signal: dict[str, Any]) -> str:
    canonical = "\n".join(
        [
            str(signal.get("knowledgeDomain") or ""),
            normalize_text(str(signal.get("title") or "")),
            normalize_text(str(signal.get("candidateConclusion") or "")),
            normalize_text(" ".join(signal.get("appliesWhen") or [])),
            normalize_text(" ".join(sorted(signal.get("keywords") or []))),
        ]
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def signal_state_path(bundle: Bundle, identity: str) -> Path:
    return bundle.root / "knowledge" / ".state" / "distilled-signals" / f"{safe_slug(identity, 'signal')}.json"


def write_state(
    bundle: Bundle,
    identity: str,
    source_path: Path,
    status: str,
    *,
    signal: dict[str, Any] | None = None,
    fingerprint: str = "",
    knowledge_id: str = "",
    knowledge_path: str = "",
    duplicate_of: str | None = None,
    errors: list[str] | None = None,
    warnings: list[str] | None = None,
) -> Path:
    payload = {
        "signalId": identity if str(identity).startswith("ks-") else (signal or {}).get("signalId", ""),
        "candidateId": (signal or {}).get("candidateId", "") if signal else "",
        "sourceProjectId": (signal or {}).get("sourceProjectId", "") if signal else "",
        "status": status,
        "knowledgeId": knowledge_id,
        "knowledgePath": knowledge_path,
        "sourcePath": rel(source_path, bundle.root),
        "fingerprint": fingerprint,
        "duplicateOf": duplicate_of,
        "errors": errors or [],
        "warnings": warnings or [],
        "processedAt": utc_now(),
    }
    path = signal_state_path(bundle, identity)
    write_text(path, json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    return path


def load_state_by_fingerprint(bundle: Bundle) -> dict[str, dict[str, Any]]:
    state_dir = bundle.root / "knowledge" / ".state" / "distilled-signals"
    result: dict[str, dict[str, Any]] = {}
    if not state_dir.exists():
        return result
    for path in sorted(state_dir.glob("*.json")):
        try:
            record = json.loads(read_text(path))
        except json.JSONDecodeError:
            continue
        fingerprint = str(record.get("fingerprint") or "")
        if fingerprint and record.get("status") in {"distilled", "review_required", "duplicate"}:
            result[fingerprint] = record
    return result


def detect_safety(signal: dict[str, Any], body: str) -> dict[str, Any]:
    haystack = "\n".join(
        [
            str(signal.get("candidateConclusion") or ""),
            "\n".join(signal.get("evidenceRefs") or []),
            body,
        ]
    )
    reasons: list[str] = []
    warnings: list[str] = []
    for pattern in SENSITIVE_PATTERNS:
        if pattern.search(haystack):
            reasons.append("sensitive_content_pattern")
            warnings.append("sensitive content pattern detected")
            break
    for term in REVIEW_TERMS:
        if term.lower() in haystack.lower():
            reasons.append(f"review_term:{term}")
    if signal.get("humanOwnerConfirmationRequired"):
        reasons.append("humanOwnerConfirmationRequired")
    if signal["riskLevel"] == "high":
        reasons.append("riskLevel=high")
    for impact_name in ["skillImpact", "toolImpact"]:
        impact = dict(signal.get(impact_name) or {})
        if impact.get("hasImpact"):
            reasons.append(f"{impact_name}.hasImpact")
        if impact.get("autoApplyAllowed"):
            reasons.append(f"{impact_name}.autoApplyAllowed_input_ignored")
            warnings.append(f"{impact_name}.autoApplyAllowed input ignored")
    review_required = bool(reasons)
    restricted = signal["riskLevel"] == "high" or "sensitive_content_pattern" in reasons
    risk = signal["riskLevel"]
    if "sensitive_content_pattern" in reasons:
        risk = "high"
    elif review_required and risk == "low":
        risk = "medium"
    return {"reviewRequired": review_required, "restricted": restricted, "riskLevel": risk, "reasons": sorted(set(reasons)), "warnings": warnings}


def knowledge_slug(signal: dict[str, Any]) -> str:
    title = str(signal.get("title") or "")
    keywords = " ".join(signal.get("keywords") or [])
    base = safe_slug(f"{title} {keywords}", "knowledge")
    return base[:90].strip("-") or "knowledge-signal"


def write_knowledge_item(bundle: Bundle, signal: dict[str, Any], body: str, fingerprint: str, safety: dict[str, Any]) -> tuple[Path, str]:
    now = utc_now()
    date_suffix = now[:10].replace("-", "")
    base_slug = knowledge_slug(signal)
    knowledge_id = f"ki-{base_slug}-{date_suffix}"
    category = DOMAIN_TO_CATEGORY.get(str(signal.get("knowledgeDomain") or "general"), "general")
    path = bundle.root / "knowledge" / category / f"{base_slug}-{date_suffix}.md"
    suffix = fingerprint[:8]
    if path.exists():
        path = bundle.root / "knowledge" / category / f"{base_slug}-{date_suffix}-{suffix}.md"
        knowledge_id = f"{knowledge_id}-{suffix}"
    signal_id = str(signal.get("signalId") or "")
    candidate_id = str(signal.get("candidateId") or "")
    fm = {
        "type": "KnowledgeItem",
        "knowledgeId": knowledge_id,
        "title": signal["title"],
        "timestamp": now,
        "createdAt": now,
        "updatedAt": now,
        "owner": "agent.company-knowledge-core.knowledge-engineering",
        "status": "draft",
        "scope": "company",
        "sourceRef": signal["sourceRefs"][0],
        "sourceRefs": signal["sourceRefs"],
        "evidenceRefs": signal["evidenceRefs"],
        "confidence": signal["confidence"],
        "knowledgeDomain": signal["knowledgeDomain"],
        "knowledgeType": signal["knowledgeType"],
        "sourceProjectId": signal["sourceProjectId"],
        "sourceTaskId": str(signal.get("sourceTaskId") or ""),
        "sourceSignalId": signal_id,
        "sourceCandidateId": candidate_id,
        "riskLevel": safety["riskLevel"],
        "reviewRequired": safety["reviewRequired"],
        "restricted": safety["restricted"],
        "fingerprint": fingerprint,
        "keywords": signal["keywords"],
        "appliesWhen": signal["appliesWhen"],
        "doesNotApplyWhen": signal["doesNotApplyWhen"],
        "skillImpact": signal["skillImpact"],
        "toolImpact": signal["toolImpact"],
        "relatedSignals": [],
    }
    write_text(path, render_doc(fm, render_knowledge_body(signal, safety)))
    return path, knowledge_id


def render_knowledge_body(signal: dict[str, Any], safety: dict[str, Any]) -> str:
    lines = [
        "# 结论",
        "",
        str(signal.get("candidateConclusion") or "").strip(),
        "",
        "# 适用场景",
        "",
        *[f"- {item}" for item in signal.get("appliesWhen") or []],
        "",
        "# 不适用场景",
        "",
        *([f"- {item}" for item in signal.get("doesNotApplyWhen") or []] or ["- 未记录。"]),
        "",
        "# 排查/使用方法",
        "",
        "1. 先确认本条知识的适用场景是否命中。",
        "2. 按来源证据复核关键事实。",
        "3. 如涉及 Skill 或 Tool, 只作为改进候选, 不自动变更能力。",
        "",
        "# 证据",
        "",
        f"- 来源项目: {signal.get('sourceProjectId')}",
        *[f"- 来源记录: {item}" for item in signal.get("sourceRefs") or []],
        *[f"- 关键证据: {item}" for item in signal.get("evidenceRefs") or []],
        "",
        "# 后续建议",
        "",
    ]
    if signal["skillImpact"]["hasImpact"]:
        lines.append("可生成人类 owner 审查的 AgentCapabilityGap draft, 但不得由自动蒸馏流程直接修改 Skill。")
    if signal["toolImpact"]["hasImpact"]:
        lines.append("可生成人类 owner 审查的 ToolCapabilityGap draft, 但不得由自动蒸馏流程直接修改 Tool。")
    if safety["reviewRequired"]:
        lines.append(f"需要审查: {', '.join(safety['reasons'])}。")
    if not lines[-1]:
        lines.append("暂无。")
    return "\n".join(lines) + "\n"


def write_review_marker(bundle: Bundle, signal: dict[str, Any], knowledge_id: str, knowledge_path: Path, safety: dict[str, Any]) -> Path:
    path = bundle.root / "knowledge" / "review" / f"{knowledge_id}.md"
    fm = {
        "type": "ReviewRecord",
        "title": f"Review {knowledge_id}",
        "reviewId": f"review-{knowledge_id}",
        "projectId": signal.get("sourceProjectId", ""),
        "upstreamRef": rel(knowledge_path, bundle.root),
        "receiverAgent": "agent.company-knowledge-core.knowledge-engineering",
        "reviewerAgent": "agent.core.knowledge-review",
        "status": "human_decision_required",
        "decision": "human_decision_required",
        "issues": safety["reasons"],
        "evidenceRefs": signal.get("evidenceRefs") or [],
        "sourceRefs": signal.get("sourceRefs") or [],
        "createdAt": utc_now(),
    }
    body = "\n".join([
        "# Review Required",
        "",
        f"- knowledgeId: {knowledge_id}",
        f"- sourceSignalId: {signal.get('signalId') or signal.get('candidateId')}",
        f"- riskLevel: {safety['riskLevel']}",
        f"- reasons: {', '.join(safety['reasons'])}",
    ])
    write_text(path, render_doc(fm, body))
    return path


def write_gap_drafts(bundle: Bundle, signal: dict[str, Any], knowledge_id: str) -> list[Path]:
    paths: list[Path] = []
    now = utc_now()
    if signal["skillImpact"]["hasImpact"]:
        gap_id = f"acg-{knowledge_slug(signal)}-{now[:10].replace('-', '')}"
        path = bundle.root / "knowledge" / "gaps" / "agent-capability" / f"{gap_id}.md"
        fm = {
            "type": "AgentCapabilityGap",
            "gapId": gap_id,
            "title": f"{signal['title']} Agent 能力缺口",
            "status": "draft",
            "riskLevel": signal["riskLevel"],
            "sourceKnowledgeId": knowledge_id,
            "sourceSignalId": signal.get("signalId") or signal.get("candidateId"),
            "ownerRequired": True,
            "autoApplyAllowed": False,
            "createdAt": now,
        }
        write_text(path, render_doc(fm, f"# 能力缺口\n\n{signal['skillImpact'].get('suggestedImpact') or signal['title']}\n\n# 禁止事项\n\n不得由自动蒸馏流程直接修改 Skill 或下发能力包。\n"))
        write_audit_jsonl(bundle, "knowledge_gap.agent_capability.created", {"path": rel(path, bundle.root), "knowledgeId": knowledge_id})
        paths.append(path)
    if signal["toolImpact"]["hasImpact"]:
        gap_id = f"tcg-{knowledge_slug(signal)}-{now[:10].replace('-', '')}"
        path = bundle.root / "knowledge" / "gaps" / "tool-capability" / f"{gap_id}.md"
        fm = {
            "type": "ToolCapabilityGap",
            "gapId": gap_id,
            "title": f"{signal['title']} Tool 能力缺口",
            "status": "draft",
            "riskLevel": signal["riskLevel"],
            "sourceKnowledgeId": knowledge_id,
            "sourceSignalId": signal.get("signalId") or signal.get("candidateId"),
            "ownerRequired": True,
            "autoApplyAllowed": False,
            "createdAt": now,
        }
        write_text(path, render_doc(fm, f"# 工具缺口\n\n{signal['toolImpact'].get('suggestedImpact') or signal['title']}\n\n# 禁止事项\n\n不得由自动蒸馏流程直接修改工具实现、权限或风险等级。\n"))
        write_audit_jsonl(bundle, "knowledge_gap.tool_capability.created", {"path": rel(path, bundle.root), "knowledgeId": knowledge_id})
        paths.append(path)
    return paths


def update_indexes(bundle: Bundle, knowledge_path: Path, knowledge_id: str, signal: dict[str, Any], fingerprint: str, safety: dict[str, Any]) -> None:
    update_markdown_index(bundle, knowledge_path, knowledge_id, signal, safety)
    update_jsonl_index(bundle, knowledge_path, knowledge_id, signal, fingerprint, safety)
    write_audit_jsonl(bundle, "knowledge_index.updated", {"knowledgeId": knowledge_id, "paths": ["knowledge/index.md", "knowledge/index.jsonl"]})


def update_markdown_index(bundle: Bundle, knowledge_path: Path, knowledge_id: str, signal: dict[str, Any], safety: dict[str, Any]) -> None:
    index_path = bundle.root / "knowledge" / "index.md"
    ensure_dir(index_path.parent)
    existing = read_text(index_path) if index_path.exists() else "# Knowledge Index\n\n"
    if knowledge_id in existing:
        return
    heading = DOMAIN_TO_CATEGORY.get(signal["knowledgeDomain"], "general").replace("-", " ").title()
    if f"## {heading}" not in existing:
        if not existing.endswith("\n"):
            existing += "\n"
        existing += f"\n## {heading}\n\n"
    entry = "\n".join(
        [
            f"- [{signal['title']}]({rel(knowledge_path, index_path.parent)})",
            f"  - knowledgeId: {knowledge_id}",
            f"  - status: draft",
            f"  - confidence: {signal['confidence']}",
            f"  - risk: {safety['riskLevel']}",
            f"  - reviewRequired: {str(safety['reviewRequired']).lower()}",
            f"  - tags - {', '.join(signal.get('keywords') or [])}",
            "",
        ]
    )
    existing += entry
    write_text(index_path, existing)


def load_index_records(bundle: Bundle) -> list[dict[str, Any]]:
    path = bundle.root / "knowledge" / "index.jsonl"
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    for line in read_text(path).splitlines():
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            records.append(value)
    return records


def update_jsonl_index(bundle: Bundle, knowledge_path: Path, knowledge_id: str, signal: dict[str, Any], fingerprint: str, safety: dict[str, Any]) -> None:
    path = bundle.root / "knowledge" / "index.jsonl"
    records = [record for record in load_index_records(bundle) if record.get("knowledgeId") != knowledge_id]
    record = {
        "knowledgeId": knowledge_id,
        "title": signal["title"],
        "status": "draft",
        "knowledgeDomain": signal["knowledgeDomain"],
        "knowledgeType": signal["knowledgeType"],
        "confidence": signal["confidence"],
        "riskLevel": safety["riskLevel"],
        "reviewRequired": safety["reviewRequired"],
        "restricted": safety["restricted"],
        "keywords": signal.get("keywords") or [],
        "path": rel(knowledge_path, bundle.root),
        "sourceProjectId": signal["sourceProjectId"],
        "sourceSignalId": signal.get("signalId") or "",
        "sourceCandidateId": signal.get("candidateId") or "",
        "fingerprint": fingerprint,
        "updatedAt": utc_now(),
        "searchText": " ".join(
            [
                signal["title"],
                str(signal.get("candidateConclusion") or ""),
                " ".join(signal.get("keywords") or []),
                " ".join(signal.get("appliesWhen") or []),
            ]
        ),
    }
    records.append(record)
    ensure_dir(path.parent)
    write_text(path, "".join(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n" for record in sorted(records, key=lambda item: str(item.get("knowledgeId") or ""))))


def build_existing_search_records(bundle: Bundle, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results = list(records)
    for category in ["engineering", "business", "operations", "tooling", "agent-capability", "policy-candidates", "general"]:
        root = bundle.root / "knowledge" / category
        if not root.exists():
            continue
        for path in sorted(root.glob("*.md")):
            try:
                from .core import parse_frontmatter

                fm, body = parse_frontmatter(read_text(path))
            except Exception:
                continue
            if fm.get("type") != "KnowledgeItem":
                continue
            results.append(
                {
                    "knowledgeId": str(fm.get("knowledgeId") or fm.get("title") or rel(path, bundle.root)),
                    "title": str(fm.get("title") or ""),
                    "keywords": list_value(fm.get("keywords")),
                    "searchText": " ".join([str(fm.get("title") or ""), body, " ".join(list_value(fm.get("keywords")))]),
                    "path": rel(path, bundle.root),
                    "fingerprint": str(fm.get("fingerprint") or ""),
                }
            )
    return results


def find_similar_existing(signal: dict[str, Any], records: list[dict[str, Any]]) -> dict[str, Any] | None:
    signal_tokens = token_set(" ".join([signal["title"], signal.get("candidateConclusion", ""), " ".join(signal.get("keywords") or []), " ".join(signal.get("appliesWhen") or [])]))
    signal_keywords = {normalize_text(item) for item in signal.get("keywords") or []}
    if not signal_tokens:
        return None
    for record in records:
        record_tokens = token_set(" ".join([str(record.get("title") or ""), str(record.get("searchText") or ""), " ".join(list_value(record.get("keywords")))]))
        if not record_tokens:
            continue
        token_overlap = len(signal_tokens & record_tokens) / max(1, min(len(signal_tokens), len(record_tokens)))
        keyword_overlap = len(signal_keywords & {normalize_text(item) for item in list_value(record.get("keywords"))})
        if token_overlap >= 0.75 or keyword_overlap >= 2:
            return record
    return None


def token_set(value: str) -> set[str]:
    ascii_tokens = set(re.findall(r"[a-z0-9_]{3,}", value.lower()))
    cjk_terms = {term for term in ["飞书", "工作台", "外链", "白名单", "企业管理后台", "开放平台", "能力缺口", "工具缺口"] if term in value}
    return ascii_tokens | cjk_terms


def search_knowledge_index(bundle: Bundle, query: str, *, include_restricted: bool = False, limit: int = 10) -> list[dict[str, Any]]:
    terms = token_set(query) or {query.strip().lower()}
    rows: list[tuple[int, dict[str, Any]]] = []
    for record in load_index_records(bundle):
        if record.get("restricted") and not include_restricted:
            continue
        text = " ".join(
            [
                str(record.get("title") or ""),
                str(record.get("searchText") or ""),
                " ".join(list_value(record.get("keywords"))),
                str(record.get("path") or ""),
            ]
        ).lower()
        score = sum(1 for term in terms if term and term.lower() in text)
        if score:
            rows.append((score, record))
    rows.sort(key=lambda item: (-item[0], str(item[1].get("updatedAt") or ""), str(item[1].get("knowledgeId") or "")))
    return [record | {"score": score} for score, record in rows[:limit]]


def write_audit_jsonl(bundle: Bundle, event_type: str, payload: dict[str, Any]) -> None:
    path = bundle.root / "knowledge" / ".state" / "audit.jsonl"
    ensure_dir(path.parent)
    safe_payload = redact_payload(payload)
    safe_payload.update({"eventType": event_type, "timestamp": utc_now()})
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(safe_payload, ensure_ascii=False, sort_keys=True) + "\n")


def redact_payload(payload: dict[str, Any]) -> dict[str, Any]:
    redacted: dict[str, Any] = {}
    for key, value in payload.items():
        if re.search(r"token|secret|password|credential|api[_-]?key", str(key), re.IGNORECASE):
            redacted[key] = "[redacted]"
        else:
            redacted[key] = value
    return redacted
