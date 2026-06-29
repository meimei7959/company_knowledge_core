from __future__ import annotations

import html
import re
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from .core import (
    Bundle,
    KnowledgeError,
    as_list,
    claim_project_task,
    ensure_dir,
    find_project_task,
    finish_project_task,
    find_agent_runner,
    heartbeat_agent_runner,
    load_object,
    make_agent,
    publish_knowledge_bundle,
    read_text,
    register_agent_runner,
    rel,
    render_doc,
    slug,
    update_frontmatter_file,
    utc_now,
    write_text,
)
from . import feishu as feishu_module
from .feishu import FEISHU_API_BASE, notify_feishu_task_status


DEFAULT_FEISHU_DIRECT_RUNNER = "runner.feishu-direct-material-processor"
LOCAL_CONTROL_AGENT = "agent.company-knowledge-core.knowledge-engineering"
URL_RE = re.compile(r"https?://[^\s，,。；;）)】\\>]+")
MAX_EXTRACTED_TEXT_CHARS = 12000
FEISHU_RESULT_REQUIRED_SECTIONS = ("资料整理结果：", "建议：", "边界：")


class ReadableHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_ignored = False
        self.ignored_depth = 0
        self.parts: list[str] = []
        self.title_parts: list[str] = []
        self.in_title = False
        self.current_attrs: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        normalized = tag.lower()
        if normalized in {"script", "style", "noscript", "svg"}:
            self.ignored_depth += 1
            self.in_ignored = True
            return
        self.current_attrs = {key.lower(): value or "" for key, value in attrs}
        if normalized == "title":
            self.in_title = True
        if normalized in {"p", "div", "section", "article", "br", "h1", "h2", "h3", "li"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        normalized = tag.lower()
        if normalized in {"script", "style", "noscript", "svg"} and self.ignored_depth:
            self.ignored_depth -= 1
            self.in_ignored = self.ignored_depth > 0
            return
        if normalized == "title":
            self.in_title = False
        if normalized in {"p", "div", "section", "article", "h1", "h2", "h3", "li"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self.in_ignored:
            return
        text = data.strip()
        if not text:
            return
        if self.in_title:
            self.title_parts.append(text)
        self.parts.append(text)

    @property
    def title(self) -> str:
        return normalize_extracted_text(" ".join(self.title_parts), 200)

    @property
    def text(self) -> str:
        return normalize_extracted_text("\n".join(self.parts), MAX_EXTRACTED_TEXT_CHARS)


class ContainerTextHTMLParser(HTMLParser):
    def __init__(self, target_ids: set[str], target_classes: set[str]) -> None:
        super().__init__()
        self.target_ids = target_ids
        self.target_classes = target_classes
        self.capture_depth = 0
        self.ignored_depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        normalized = tag.lower()
        attrs_map = {key.lower(): value or "" for key, value in attrs}
        if normalized in {"script", "style", "noscript", "svg"}:
            self.ignored_depth += 1
            return
        if self.capture_depth == 0:
            class_tokens = set(attrs_map.get("class", "").split())
            if attrs_map.get("id") in self.target_ids or bool(class_tokens & self.target_classes):
                self.capture_depth = 1
                self.parts.append("\n")
            return
        self.capture_depth += 1
        if normalized in {"p", "div", "section", "article", "br", "h1", "h2", "h3", "li"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        normalized = tag.lower()
        if normalized in {"script", "style", "noscript", "svg"} and self.ignored_depth:
            self.ignored_depth -= 1
            return
        if self.capture_depth == 0:
            return
        if normalized in {"p", "div", "section", "article", "h1", "h2", "h3", "li"}:
            self.parts.append("\n")
        self.capture_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.capture_depth == 0 or self.ignored_depth:
            return
        text = data.strip()
        if text:
            self.parts.append(text)

    @property
    def text(self) -> str:
        return normalize_extracted_text("\n".join(self.parts), MAX_EXTRACTED_TEXT_CHARS)


def ensure_feishu_direct_material_runner(
    bundle: Bundle,
    runner_id: str = DEFAULT_FEISHU_DIRECT_RUNNER,
    project_id: str = "company-knowledge-core",
) -> str:
    rid = slug(runner_id)
    try:
        find_agent_runner(bundle, rid)
    except KnowledgeError:
        register_agent_runner(
            bundle,
            rid,
            "飞书资料直处理器",
            host_type="server",
            mode="inline",
            agents=[LOCAL_CONTROL_AGENT],
            capabilities=["knowledge_capture", "research_material_processing", "feishu_direct_reply"],
            available_projects=[project_id],
            repo_access=[project_id],
            data_scopes=["internal"],
        )
    heartbeat_agent_runner(
        bundle,
        rid,
        status="online",
        load="feishu-direct-material-processing",
        capabilities=["knowledge_capture", "research_material_processing", "feishu_direct_reply"],
        available_projects=[project_id],
    )
    return rid


def ensure_feishu_direct_material_agent(bundle: Bundle, project_id: str = "company-knowledge-core") -> str:
    agent_id = slug(LOCAL_CONTROL_AGENT)
    agent_path = bundle.root / "agents" / f"{agent_id}.md"
    if not agent_path.exists():
        make_agent(
            bundle,
            LOCAL_CONTROL_AGENT,
            "飞书资料整理 Agent",
            "knowledge-engineering",
            "codex",
            "处理飞书入口收到的研究资料，生成可读摘要、来源引用和 Agent 能力提升初筛。",
        )
    update_frontmatter_file(
        agent_path,
        {
            "allowedProjects": sorted(set(as_list(load_object(agent_path).get("allowedProjects")) + [slug(project_id)])),
            "writePermissions": ["knowledge:draft"],
            "updatedAt": utc_now(),
        },
    )
    policy_dir = bundle.root / "knowledge" / "policies"
    ensure_dir(policy_dir)
    policy_path = policy_dir / f"policy.{agent_id}.md"
    if not policy_path.exists():
        write_text(
            policy_path,
            render_doc(
                {
                    "type": "Policy",
                    "title": "飞书资料整理 Agent 最小权限",
                    "description": "Allows the Feishu direct material processor to write draft knowledge outputs.",
                    "timestamp": utc_now(),
                    "policyId": f"policy.{agent_id}",
                    "owner": "knowledge-engineering",
                    "agentId": agent_id,
                    "status": "active",
                    "allowedProjects": [slug(project_id)],
                    "allowedKnowledgeScopes": ["engineering"],
                    "allowedToolRiskLevels": ["L1"],
                    "writePermissions": ["knowledge:draft"],
                },
                "## Scope\n\nOnly for direct Feishu material processing and draft result writeback.\n",
            ),
        )
    return agent_id


def source_material_payload(bundle: Bundle, source_ref: str) -> dict[str, str]:
    if not source_ref.strip():
        return {"title": "资料", "sourceRef": "", "content": ""}
    path = bundle.root / source_ref
    if not path.exists():
        return {"title": "资料", "sourceRef": source_ref, "content": ""}
    fm = load_object(path)
    text = read_text(path)
    _, body = split_frontmatter_text(text)
    return {
        "title": str(fm.get("title") or path.stem),
        "sourceRef": str(fm.get("sourceRef") or source_ref),
        "storageRef": str(fm.get("storageRef") or ""),
        "content": compact_material_body(body),
        "materialRef": rel(path, bundle.root),
    }


def split_frontmatter_text(text: str) -> tuple[str, str]:
    if not text.startswith("---"):
        return "", text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return "", text
    return parts[1], parts[2].strip()


def compact_material_body(body: str, limit: int = 2000) -> str:
    lines = [line.rstrip() for line in body.splitlines()]
    useful = [line for line in lines if line.strip() and not line.strip().startswith("- summary: pending")]
    text = "\n".join(useful).strip()
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "\n..."


def infer_material_url(*values: str) -> str:
    for value in values:
        match = URL_RE.search(value or "")
        if match:
            return match.group(0)
    return ""


def normalize_extracted_text(value: str, limit: int = MAX_EXTRACTED_TEXT_CHARS) -> str:
    text = html.unescape(value or "")
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t\f\v]+", " ", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "\n..."


def compact_feishu_result_text(value: str, limit: int = 700) -> str:
    text = normalize_extracted_text(value or "", limit)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text


def compact_json_text(value: Any, limit: int = MAX_EXTRACTED_TEXT_CHARS) -> str:
    parts: list[str] = []

    def visit(item: Any) -> None:
        if len("\n".join(parts)) > limit:
            return
        if isinstance(item, dict):
            for key, child in item.items():
                if str(key).lower() in {"text", "content", "title", "name", "plain_text", "value"}:
                    visit(child)
                elif isinstance(child, (dict, list)):
                    visit(child)
        elif isinstance(item, list):
            for child in item:
                visit(child)
        elif isinstance(item, str):
            stripped = item.strip()
            if stripped and len(stripped) < 5000:
                parts.append(stripped)

    visit(value)
    return normalize_extracted_text("\n".join(parts), limit)


def parse_html_readable_text(raw_html: str) -> dict[str, str]:
    parser = ReadableHTMLParser()
    parser.feed(raw_html)
    text = parser.text
    title = parser.title
    wechat_match = re.search(r"<h1[^>]*(?:id=[\"']activity-name[\"']|class=[\"'][^\"']*rich_media_title)[^>]*>(.*?)</h1>", raw_html, re.I | re.S)
    if wechat_match:
        title = normalize_extracted_text(re.sub(r"<[^>]+>", "", wechat_match.group(1)), 200) or title
    content_parser = ContainerTextHTMLParser({"js_content"}, {"rich_media_content"})
    content_parser.feed(raw_html)
    content_text = content_parser.text
    if content_text:
        text = content_text
    return {"title": title, "text": text}


def fetch_general_webpage_text(url: str, timeout: float = 10.0) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 ZhenzhiKnowledgeBot/0.1 (+https://zknowai.com)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,text/plain;q=0.8,*/*;q=0.5",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        content_type = response.headers.get("Content-Type", "")
        raw = response.read(2_000_000)
    encoding = "utf-8"
    match = re.search(r"charset=([^;]+)", content_type, re.I)
    if match:
        encoding = match.group(1).strip()
    body = raw.decode(encoding, errors="replace")
    if "html" in content_type.lower() or "<html" in body[:500].lower():
        parsed = parse_html_readable_text(body)
        return {"ok": bool(parsed["text"]), "kind": "webpage", "title": parsed["title"], "text": parsed["text"], "error": ""}
    return {"ok": True, "kind": "text", "title": "", "text": normalize_extracted_text(body), "error": ""}


def feishu_doc_token_from_url(url: str) -> tuple[str, str]:
    parsed = urllib.parse.urlparse(url)
    parts = [part for part in parsed.path.split("/") if part]
    for kind in ["docx", "doc", "wiki"]:
        if kind in parts:
            index = parts.index(kind)
            if index + 1 < len(parts):
                return kind, parts[index + 1]
    return "", ""


def fetch_feishu_document_text(url: str) -> dict[str, Any]:
    kind, token = feishu_doc_token_from_url(url)
    if not token:
        return {"ok": False, "kind": "feishu", "title": "", "text": "", "error": "未识别飞书文档 token"}
    settings = feishu_module.load_feishu_settings()
    if not settings.app_id or not settings.app_secret:
        return {"ok": False, "kind": "feishu", "title": "", "text": "", "error": "缺少 FEISHU_APP_ID/FEISHU_APP_SECRET，无法读取飞书文档正文"}
    try:
        tenant_token = feishu_module.get_tenant_access_token(settings)
        document_id = token
        if kind == "wiki":
            node = feishu_module.feishu_json_request("GET", f"{FEISHU_API_BASE}/wiki/v2/spaces/get_node?token={urllib.parse.quote(token)}", tenant_token)
            data = node.get("data") if isinstance(node.get("data"), dict) else {}
            obj_token = str(data.get("obj_token") or data.get("node", {}).get("obj_token") or "")
            obj_type = str(data.get("obj_type") or data.get("node", {}).get("obj_type") or "")
            if obj_token and obj_type in {"docx", "doc"}:
                document_id = obj_token
        doc = feishu_module.feishu_json_request("GET", f"{FEISHU_API_BASE}/docx/v1/documents/{urllib.parse.quote(document_id)}", tenant_token)
        children = feishu_module.feishu_json_request("GET", f"{FEISHU_API_BASE}/docx/v1/documents/{urllib.parse.quote(document_id)}/blocks/{urllib.parse.quote(document_id)}/children?page_size=500", tenant_token)
        title = compact_json_text(doc, 200)
        text = compact_json_text(children)
        return {"ok": bool(text), "kind": "feishu", "title": title, "text": text, "error": "" if text else "飞书文档正文为空或无权限"}
    except Exception as exc:
        return {"ok": False, "kind": "feishu", "title": "", "text": "", "error": str(exc)}


def extract_external_material_text(url: str) -> dict[str, Any]:
    if not url:
        return {"ok": False, "kind": "none", "title": "", "text": "", "error": "无 URL"}
    host = urllib.parse.urlparse(url).netloc.lower()
    try:
        if "feishu.cn" in host or "larksuite.com" in host:
            return fetch_feishu_document_text(url)
        result = fetch_general_webpage_text(url)
        if "mp.weixin.qq.com" in host:
            result["kind"] = "wechat_article"
        return result
    except (urllib.error.URLError, TimeoutError, OSError, UnicodeError) as exc:
        return {"ok": False, "kind": "webpage", "title": "", "text": "", "error": str(exc)}


def build_feishu_research_done_detail(
    title: str,
    source_url: str,
    extraction: dict[str, Any],
    extracted_text: str,
    source_text: str = "",
) -> str:
    visible_text = extracted_text or (source_text if not source_url else "")
    extraction_ok = bool(extracted_text) or (bool(visible_text) and not source_url)
    one_line_summary = compact_feishu_result_text(visible_text, 220) if visible_text else ""
    lower_text = f"{title}\n{visible_text}".lower()
    agent_route_keywords = [
        "agent 团队",
        "agent团队",
        "agent 能力",
        "agent能力",
        "ai agent",
        "智能体",
        "workflow",
        "工作流",
        "skill",
        "tool",
        "工具能力",
        "runner",
        "codex",
        "claude",
        "draft",
        "任务编排",
        "路由",
        "能力候选",
        "知识工程",
        "检查点",
        "验收标准",
        "prompt",
        "提示词",
    ]
    business_route_keywords = [
        "用户",
        "需求",
        "评论",
        "市场",
        "竞品",
        "应用商店",
        "社交媒体",
        "产品",
        "运营",
        "增长",
        "投屏",
        "客户",
        "商业",
        "付费",
        "价格",
        "留存",
        "转化",
    ]
    strong_agent_route_keywords = [
        "agent 能力",
        "agent能力",
        "智能体",
        "workflow",
        "工作流",
        "skill",
        "tool",
        "工具能力",
    ]
    is_agent_capability_material = any(keyword in lower_text for keyword in agent_route_keywords)
    is_business_material = any(keyword in lower_text for keyword in business_route_keywords)
    has_strong_agent_signal = any(keyword in lower_text for keyword in strong_agent_route_keywords)
    should_route_to_business_knowledge = (not is_agent_capability_material) or (is_business_material and not has_strong_agent_signal)
    capability_keywords = {
        "任务判断": ["task", "任务", "优先级", "规划", "决策"],
        "执行步骤": ["workflow", "流程", "步骤", "pipeline", "落地"],
        "检查点": ["checklist", "gate", "检查", "验收", "质量"],
        "示例/反例": ["example", "case", "案例", "反例", "实践"],
        "工具使用": ["tool", "工具", "automation", "自动化", "api"],
        "验收标准": ["acceptance", "验收", "评估", "benchmark", "测试"],
    }
    lines = [
        "资料整理结果：",
        f"- 标题：{title}",
        f"- 来源：{source_url or '未识别'}",
        f"- 正文抽取：{'已完成' if extraction_ok else '未完成'}",
    ]
    if not extraction_ok:
        lines.append(f"- 原因：{str(extraction.get('error') or '未知原因')}")
    if one_line_summary:
        lines.append(f"- 一句话摘要：{one_line_summary}")
    if should_route_to_business_knowledge:
        lines.extend(
            [
                "",
                "知识归类：",
                "- 类型：业务/产品/市场知识",
                "- 用途：沉淀为企业知识，供具体项目、产品决策或后续研究引用。",
                "- 建议：先保存为企业知识；如果要用于某个项目，请补充项目名或目标。",
                "",
                "边界：不会直接改 Skill、Tool、Workflow、AGENTS、规则或权限；如果后续要改 Agent 能力，需要单独进入能力候选、Review 和 Approval。",
            ]
        )
        return "\n".join(lines)
    matched = [name for name, words in capability_keywords.items() if any(word in lower_text for word in words)]
    capability_value = "有潜在作用" if matched else "暂未发现直接作用"
    suggestion = "进入能力候选复核" if matched else "先沉淀为企业知识，后续有复用场景再评估"
    lines.extend(
        [
            "",
            "对 Agent 团队提升：",
            f"- 初步判断：{capability_value}",
            f"- 可能优化点：{('、'.join(matched)) if matched else '未识别到稳定可复用的能力点'}",
            "- 与现有体系对比：当前只是资料初筛，还不能证明比现有工具、流程或设计理念更好。",
            f"- 建议：{suggestion}",
            "",
            "边界：这一步只保存、整理和初筛资料；只有确认能稳定改变 Agent 行为时，才进入 Skill、Tool、规则、示例或检查点变更。",
        ]
    )
    return "\n".join(lines)


def build_research_material_result(bundle: Bundle, task: dict[str, Any]) -> dict[str, Any]:
    source_refs = as_list(task.get("sourceMaterialRefs"))
    materials = [source_material_payload(bundle, ref) for ref in source_refs]
    first = materials[0] if materials else {"title": str(task.get("title") or "资料"), "sourceRef": "", "content": ""}
    research_question = str(task.get("researchQuestion") or "")
    source_url = infer_material_url(str(first.get("sourceRef") or ""), str(first.get("content") or ""), research_question)
    extraction = extract_external_material_text(source_url) if source_url else {"ok": False, "kind": "none", "title": "", "text": "", "error": "无 URL"}
    title = str(extraction.get("title") or first.get("title") or task.get("title") or "研究资料")
    extracted_text = str(extraction.get("text") or "").strip()
    base_content = extracted_text or str(first.get("content") or "当前资料只包含来源引用，尚未抓取网页全文。")
    summary = f"已整理资料《{title}》。"
    if source_url:
        summary += f" 原始链接：{source_url}。"
    if extracted_text:
        summary += " 已抽取网页/文档正文。"
    elif source_url:
        summary += f" 正文抽取未完成：{extraction.get('error') or '未知原因'}。"
    summary += " 当前处理结果为资料结构化草稿；不会直接修改 Skill、Workflow、AGENTS、规则或权限。"
    structured = "\n".join(
        [
            "## 资料来源",
            "",
            f"- 标题：{title}",
            f"- 原始链接：{source_url or '未识别'}",
            f"- 来源类型：{extraction.get('kind', 'unknown')}",
            f"- 正文抽取：{'成功' if extracted_text else '未完成'}",
            f"- 抽取问题：{str(extraction.get('error') or 'none')}",
            f"- SourceMaterial：{', '.join(source_refs) or 'none'}",
            "",
            "## 用户意图",
            "",
            research_question or "用户通过飞书提交资料，希望保存并整理为可检索参考。",
            "",
            "## 正文内容",
            "",
            base_content,
            "",
            "## 使用边界",
            "",
            "- 这是资料整理草稿，不是已验证知识。",
            "- 默认只保存、整理、索引；只有明确要求改体系时，才进入 Skill/Workflow/规则变更评审。",
            "- 如正文抽取失败，需补充权限、可访问链接或人工上传正文。",
        ]
    )
    knowledge_draft = {
        "title": f"资料整理：{title}",
        "category": "engineering",
        "summary": summary,
        "structured": structured,
        "confidence": "medium" if extracted_text else ("low" if source_url else "low"),
        "knowledgeType": "research_note",
        "applicability": "用于后续体系设计参考；不能直接作为已验证规则。",
        "limits": ["未做人类验收", "不代表体系变更已批准", *([] if extracted_text else ["正文抽取未完成"])],
        "sourceRefs": source_refs,
    }
    feishu_detail = build_feishu_research_done_detail(title, source_url, extraction, extracted_text, base_content)
    return {
        "summary": summary,
        "feishuDetail": feishu_detail,
        "workerContract": {
            "executor": "codex_worker",
            "entry": "feishu_agent_hub",
            "userVisibleResult": True,
            "requiresHumanApproval": False,
            "mutationAllowed": False,
            "guard": "source_saved_deduplicated_structured_checked_before_reply",
        },
        "knowledgeDraft": knowledge_draft,
        "evidenceRefs": source_refs,
        "outputRefs": source_refs,
        "testsOrChecks": [
            "已读取 SourceMaterial 引用。",
            f"正文抽取状态：{'成功' if extracted_text else '未完成'}。",
            "已保持资料整理与体系变更审批边界。",
            "已生成可审查 KnowledgeItem draft。",
        ],
        "nextActions": [
            "如需把资料转成 Agent 能力，请单独发起 Skill/Tool/规则/示例/检查点变更评审。",
            "如正文抽取未完成，请补充可访问正文或飞书文档权限。",
        ],
        "openRisks": [] if extracted_text else [f"正文抽取未完成：{extraction.get('error') or '未知原因'}"],
    }


def validate_codex_worker_result_for_feishu(result_payload: dict[str, Any]) -> None:
    detail = str(result_payload.get("feishuDetail") or "")
    if not detail.strip():
        raise KnowledgeError("Codex Worker result missing Feishu-readable detail")
    missing_sections = [section for section in FEISHU_RESULT_REQUIRED_SECTIONS if section not in detail]
    if missing_sections:
        raise KnowledgeError(f"Codex Worker result missing sections: {', '.join(missing_sections)}")
    forbidden_fragments = ["task-results/", "SourceMaterial：", "resultRef", "codexThreadId", "primaryControlRunner", "dispatchTarget"]
    leaked = [fragment for fragment in forbidden_fragments if fragment in detail]
    if leaked:
        raise KnowledgeError(f"Codex Worker result leaks internal fields: {', '.join(leaked)}")
    contract = result_payload.get("workerContract")
    if not isinstance(contract, dict) or contract.get("executor") != "codex_worker":
        raise KnowledgeError("Codex Worker result missing worker contract")
    if contract.get("mutationAllowed"):
        raise KnowledgeError("Codex Worker result must not mutate central rules from Feishu material intake")


def process_research_material_task(
    bundle: Bundle,
    task_id: str,
    runner_id: str = DEFAULT_FEISHU_DIRECT_RUNNER,
    notify_feishu: bool = True,
    publish_index: bool = True,
    lease_seconds: int = 600,
) -> dict[str, Any]:
    ensure_feishu_direct_material_agent(bundle)
    runner_id = ensure_feishu_direct_material_runner(bundle, runner_id)
    claim = claim_project_task(bundle, task_id, runner_id, lease_seconds=lease_seconds)
    task = claim["task"]
    lease_token = str(claim["leaseToken"])
    if notify_feishu:
        notify_feishu_task_status(bundle, task_id, "processing", actor="feishu-direct-material-processor", detail="正在整理资料。")
    result_payload = build_research_material_result(bundle, task)
    validate_codex_worker_result_for_feishu(result_payload)
    result_path = finish_project_task(
        bundle,
        task_id,
        "done",
        result_payload["summary"],
        output_refs=result_payload["outputRefs"],
        evidence_refs=result_payload["evidenceRefs"],
        next_actions=result_payload["nextActions"],
        runner_id=runner_id,
        lease_token=lease_token,
        executor_agent=str(task.get("executorAgent") or task.get("assignee") or LOCAL_CONTROL_AGENT),
        tests_or_checks=result_payload["testsOrChecks"],
        knowledge_draft=result_payload["knowledgeDraft"],
        handoff_to="agent.core.knowledge-review",
        handoff_summary="资料整理草稿已完成，等待知识审查或后续体系变更评审。",
        open_risks=result_payload.get("openRisks") or [],
    )
    publish_result: dict[str, Any] = {}
    if publish_index:
        try:
            publish_result = publish_knowledge_bundle(bundle, actor="feishu-direct-material-processor", reason=f"feishu direct material processed {task_id}")
        except Exception as exc:
            publish_result = {"ok": False, "error": str(exc)}
    if notify_feishu:
        notify_feishu_task_status(
            bundle,
            task_id,
            "done",
            actor="feishu-direct-material-processor",
            detail=str(result_payload.get("feishuDetail") or result_payload["summary"]),
        )
    return {
        "taskId": task_id,
        "status": "done",
        "resultRef": rel(result_path, bundle.root),
        "detail": str(result_payload.get("feishuDetail") or result_payload["summary"]),
        "publishResult": publish_result,
    }
