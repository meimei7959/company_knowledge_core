from __future__ import annotations

import html
import os
import re
import shutil
import subprocess
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
    create_audit_log,
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
FEISHU_RESULT_REQUIRED_SECTIONS = ("存储内容预览：",)
WECHAT_BROWSER_USER_AGENT = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.49(0x1800312e) NetType/WIFI Language/zh_CN"


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
            "处理飞书入口收到的研究资料，生成可读摘要、分类和来源引用。",
        )
    update_frontmatter_file(
        agent_path,
        {
            "allowedProjects": sorted(set(as_list(load_object(agent_path).get("allowedProjects")) + [slug(project_id)])),
            "writePermissions": ["source_material:update"],
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
                    "description": "Allows the Feishu direct material processor to update classified source references.",
                    "timestamp": utc_now(),
                    "policyId": f"policy.{agent_id}",
                    "owner": "knowledge-engineering",
                    "agentId": agent_id,
                    "status": "active",
                    "allowedProjects": [slug(project_id)],
                    "allowedKnowledgeScopes": ["engineering"],
                    "allowedToolRiskLevels": ["L1"],
                    "writePermissions": ["source_material:update"],
                },
                "## Scope\n\nOnly for direct Feishu material processing and source reference writeback.\n",
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
    content = extract_material_body_content(body)
    return {
        "title": str(fm.get("title") or path.stem),
        "sourceRef": str(fm.get("sourceRef") or source_ref),
        "storageRef": str(fm.get("storageRef") or ""),
        "content": compact_material_body(content),
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


def extract_material_body_content(body: str) -> str:
    for marker in ["## Extracted Text", "## Original Text"]:
        if marker not in body:
            continue
        content = body.split(marker, 1)[1]
        next_section = content.find("\n## ")
        if next_section >= 0:
            content = content[:next_section]
        return content.strip()
    return body.strip()


def infer_material_url(*values: str) -> str:
    for value in values:
        match = URL_RE.search(value or "")
        if match:
            return match.group(0)
    return ""


def meaningful_fallback_content(content: str) -> str:
    cleaned = URL_RE.sub("", content or "")
    for prefix in ["研究一下", "研究下", "看一下", "看看", "分析一下", "分析下", "整理一下", "整理下", "参考一下"]:
        cleaned = cleaned.replace(prefix, "")
    cleaned = normalize_extracted_text(cleaned, 2000)
    return cleaned if len(cleaned) >= 8 else ""


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
    meta_title = extract_meta_content(raw_html, ["og:title", "twitter:title"])
    if meta_title and not title:
        title = meta_title
    wechat_match = re.search(r"<h1[^>]*(?:id=[\"']activity-name[\"']|class=[\"'][^\"']*rich_media_title)[^>]*>(.*?)</h1>", raw_html, re.I | re.S)
    if wechat_match:
        title = normalize_extracted_text(re.sub(r"<[^>]+>", "", wechat_match.group(1)), 200) or title
    js_title = extract_js_string(raw_html, "msg_title")
    if js_title:
        title = js_title
    content_parser = ContainerTextHTMLParser({"js_content"}, {"rich_media_content"})
    content_parser.feed(raw_html)
    content_text = content_parser.text
    if content_text:
        text = content_text
    return {"title": title, "text": text}


def extract_meta_content(raw_html: str, names: list[str]) -> str:
    for name in names:
        pattern = rf"<meta[^>]+(?:property|name)=[\"']{re.escape(name)}[\"'][^>]+content=[\"']([^\"']+)[\"'][^>]*>"
        match = re.search(pattern, raw_html, re.I | re.S)
        if match:
            return normalize_extracted_text(match.group(1), 200)
    return ""


def extract_js_string(raw_html: str, name: str) -> str:
    match = re.search(rf"\b{name}\s*=\s*(['\"])(.*?)\1", raw_html, re.I | re.S)
    if not match:
        match = re.search(rf"\bvar\s+{name}\s*=\s*(['\"])(.*?)\1", raw_html, re.I | re.S)
    if not match:
        return ""
    value = match.group(2).replace(r"\/", "/").replace(r"\'", "'").replace(r'\"', '"')
    return normalize_extracted_text(value, 200)


def looks_like_wechat_access_wall(text: str) -> bool:
    normalized = normalize_extracted_text(text, 4000)
    if not normalized:
        return False
    noise_terms = [
        "微信扫一扫",
        "可打开此内容",
        "使用完整服务",
        "使用小程序",
        "取消",
        "允许",
        "分享",
        "留言",
        "收藏",
        "听过",
        "轻点两下",
    ]
    noise_hits = sum(1 for term in noise_terms if term in normalized)
    lines = [line.strip() for line in normalized.splitlines() if line.strip()]
    short_ui_lines = sum(1 for line in lines if line in {"取消", "允许", "分享", "留言", "收藏", "赞", "在看", "视频", "小程序"})
    return noise_hits >= 3 and short_ui_lines >= 3


def is_wechat_url(url: str) -> bool:
    return "mp.weixin.qq.com" in urllib.parse.urlparse(url or "").netloc.lower()


def wechat_browser_extract_enabled() -> bool:
    value = os.environ.get("ZHENZHI_WECHAT_BROWSER_EXTRACT", "1").strip().lower()
    return value not in {"0", "false", "no", "off", "disabled"}


def find_browser_executable() -> str:
    configured = os.environ.get("ZHENZHI_BROWSER_BIN", "").strip()
    if configured:
        return configured
    for candidate in ["chromium", "chromium-browser", "google-chrome", "google-chrome-stable"]:
        found = shutil.which(candidate)
        if found:
            return found
    return ""


def fetch_wechat_article_text_with_browser(url: str, timeout: float = 24.0) -> dict[str, Any]:
    if not wechat_browser_extract_enabled():
        return {"ok": False, "kind": "wechat_article_browser", "title": "", "text": "", "error": "浏览器正文抽取已关闭"}
    browser = find_browser_executable()
    if not browser:
        return {"ok": False, "kind": "wechat_article_browser", "title": "", "text": "", "error": "未找到可用浏览器，无法打开公众号链接补抽正文"}
    command = [
        browser,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-extensions",
        "--disable-background-networking",
        "--disable-sync",
        "--hide-scrollbars",
        "--ignore-certificate-errors",
        "--lang=zh-CN",
        "--window-size=430,932",
        f"--user-agent={WECHAT_BROWSER_USER_AGENT}",
        "--virtual-time-budget=9000",
        "--dump-dom",
        url,
    ]
    try:
        completed = subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False)
    except subprocess.TimeoutExpired:
        return {"ok": False, "kind": "wechat_article_browser", "title": "", "text": "", "error": "浏览器打开公众号链接超时"}
    except OSError as exc:
        return {"ok": False, "kind": "wechat_article_browser", "title": "", "text": "", "error": f"浏览器启动失败：{exc}"}
    dom = completed.stdout or ""
    stderr = normalize_extracted_text(completed.stderr or "", 500)
    if not dom.strip():
        return {"ok": False, "kind": "wechat_article_browser", "title": "", "text": "", "error": stderr or f"浏览器未返回页面内容，退出码 {completed.returncode}"}
    parsed = parse_html_readable_text(dom)
    title = parsed.get("title") or ""
    text = str(parsed.get("text") or "")
    if looks_like_wechat_access_wall(text):
        return {"ok": False, "kind": "wechat_article_browser", "title": title, "text": "", "error": "浏览器打开后仍是微信打开/授权中间页，未拿到公众号正文"}
    if not text.strip():
        return {"ok": False, "kind": "wechat_article_browser", "title": title, "text": "", "error": "浏览器已打开页面，但未识别到公众号正文"}
    return {"ok": True, "kind": "wechat_article_browser", "title": title, "text": text, "error": ""}


def fetch_url_body(url: str, headers: dict[str, str], timeout: float = 10.0) -> tuple[str, str]:
    request = urllib.request.Request(
        url,
        headers=headers,
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        content_type = response.headers.get("Content-Type", "")
        raw = response.read(2_000_000)
    encoding = "utf-8"
    match = re.search(r"charset=([^;]+)", content_type, re.I)
    if match:
        encoding = match.group(1).strip()
    return content_type, raw.decode(encoding, errors="replace")


def default_web_headers(user_agent: str = "Mozilla/5.0 ZhenzhiKnowledgeBot/0.1 (+https://zknowai.com)") -> dict[str, str]:
    return {
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,text/plain;q=0.8,*/*;q=0.5",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.6",
    }


def fetch_general_webpage_text(url: str, timeout: float = 10.0) -> dict[str, Any]:
    content_type, body = fetch_url_body(url, default_web_headers(), timeout)
    if "html" in content_type.lower() or "<html" in body[:500].lower():
        parsed = parse_html_readable_text(body)
        return {"ok": bool(parsed["text"]), "kind": "webpage", "title": parsed["title"], "text": parsed["text"], "error": ""}
    return {"ok": True, "kind": "text", "title": "", "text": normalize_extracted_text(body), "error": ""}


def fetch_wechat_article_text(url: str, timeout: float = 10.0) -> dict[str, Any]:
    user_agents = [
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.49(0x1800312e) NetType/WIFI Language/zh_CN",
        "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/120.0.0.0 Mobile Safari/537.36 MicroMessenger/8.0.49.2600 NetType/WIFI Language/zh_CN",
        "Mozilla/5.0 ZhenzhiKnowledgeBot/0.1 (+https://zknowai.com)",
    ]
    last_title = ""
    last_error = "未拿到公众号正文"
    for user_agent in user_agents:
        headers = default_web_headers(user_agent)
        headers["Referer"] = "https://mp.weixin.qq.com/"
        content_type, body = fetch_url_body(url, headers, timeout)
        parsed = parse_html_readable_text(body) if ("html" in content_type.lower() or "<html" in body[:500].lower()) else {"title": "", "text": normalize_extracted_text(body)}
        last_title = parsed.get("title") or last_title
        text = str(parsed.get("text") or "")
        if looks_like_wechat_access_wall(text):
            last_error = "微信返回了打开/授权中间页，未拿到公众号正文"
            continue
        if text.strip():
            return {"ok": True, "kind": "wechat_article", "title": last_title, "text": text, "error": ""}
    browser_result = fetch_wechat_article_text_with_browser(url)
    if browser_result.get("ok"):
        return browser_result
    browser_error = str(browser_result.get("error") or "")
    return {"ok": False, "kind": "wechat_article", "title": str(browser_result.get("title") or last_title), "text": "", "error": f"{last_error}；浏览器补抽失败：{browser_error}", "browserPending": True}


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
        if "mp.weixin.qq.com" in host:
            return fetch_wechat_article_text(url)
        result = fetch_general_webpage_text(url)
        return result
    except (urllib.error.URLError, TimeoutError, OSError, UnicodeError) as exc:
        return {"ok": False, "kind": "webpage", "title": "", "text": "", "error": str(exc)}


def classify_research_reference(title: str, text: str, source_kind: str = "") -> dict[str, Any]:
    lower_text = f"{title}\n{text}".lower()
    categories = [
        (
            "agent_engineering",
            "Agent/知识工程资料",
            ["agent", "智能体", "workflow", "工作流", "skill", "tool", "工具", "codex", "claude", "prompt", "知识工程"],
        ),
        (
            "product_business",
            "业务/产品/市场资料",
            ["用户", "需求", "市场", "竞品", "产品", "运营", "增长", "客户", "商业", "价格", "留存", "转化"],
        ),
        (
            "technical_reference",
            "技术资料",
            ["api", "github", "代码", "架构", "数据库", "前端", "后端", "工程", "开源", "框架"],
        ),
    ]
    for category, label, keywords in categories:
        matched = [keyword for keyword in keywords if keyword in lower_text]
        if matched:
            tags = sorted(set([source_kind, *matched] if source_kind else matched))
            return {"category": category, "categoryLabel": label, "tags": tags[:12]}
    tags = [source_kind] if source_kind else []
    return {"category": "general_reference", "categoryLabel": "通用资料", "tags": tags}


def build_feishu_research_done_detail(
    title: str,
    source_url: str,
    extraction: dict[str, Any],
    extracted_text: str,
    source_text: str = "",
) -> str:
    visible_text = extracted_text or (source_text if not source_url else "")
    extraction_ok = bool(extracted_text) or (bool(visible_text) and not source_url)
    browser_pending = bool(extraction.get("browserPending"))
    one_line_summary = compact_feishu_result_text(visible_text, 220) if visible_text else ""
    classification = classify_research_reference(title, visible_text, str(extraction.get("kind") or ""))
    lines = [
        "资料已接收，正在浏览器补抓：" if browser_pending else "资料已入库：",
        f"- 标题：{title}",
        f"- 来源：{source_url or '未识别'}",
        f"- 分类：{classification['categoryLabel']}",
        f"- 正文抽取：{'已完成' if extraction_ok else ('等待浏览器补抓' if browser_pending else '未完成')}",
    ]
    if not extraction_ok:
        lines.append(f"- 原因：{str(extraction.get('error') or '未知原因')}")
    lines.extend(
        [
            "",
            "存储内容预览：",
            one_line_summary or ("正文尚未入库；系统会用浏览器打开公众号链接，读到正文后自动保存并更新索引。" if browser_pending else "暂未抽取到正文，只保存了来源链接。"),
            "",
            "内容不对可直接回复：修正：<正确内容>。",
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
    fallback_content = meaningful_fallback_content(str(first.get("content") or "")) if source_url else str(first.get("content") or "")
    manual_content_ok = bool(fallback_content and len(fallback_content) >= 80)
    base_content = extracted_text or fallback_content
    summary = f"已整理资料《{title}》。"
    if source_url:
        summary += f" 原始链接：{source_url}。"
    if extracted_text:
        summary += " 已抽取网页/文档正文。"
    elif manual_content_ok:
        summary += " 已使用用户提供正文。"
    elif source_url:
        summary += f" 正文抽取未完成：{extraction.get('error') or '未知原因'}。"
    classification = classify_research_reference(title, base_content, str(extraction.get("kind") or ""))
    summary += f" 已归类为{classification['categoryLabel']}并存入来源资料库。"
    stored_reference = {
        "title": title,
        "sourceUrl": source_url,
        "sourceKind": "user_supplied_text" if manual_content_ok and not extracted_text else str(extraction.get("kind") or "unknown"),
        "extractionOk": bool(extracted_text) or manual_content_ok,
        "extractionError": "" if manual_content_ok and not extracted_text else str(extraction.get("error") or ""),
        "browserPending": bool(extraction.get("browserPending")) and not manual_content_ok and is_wechat_url(source_url),
        "content": base_content,
        "summary": summary,
        "category": classification["category"],
        "categoryLabel": classification["categoryLabel"],
        "tags": classification["tags"],
        "sourceRefs": source_refs,
    }
    detail_extracted_text = extracted_text or (fallback_content if manual_content_ok else "")
    feishu_detail = build_feishu_research_done_detail(title, source_url, extraction, detail_extracted_text, base_content)
    return {
        "summary": summary,
        "feishuDetail": feishu_detail,
        "workerContract": {
            "executor": "codex_worker",
            "entry": "feishu_agent_hub",
            "userVisibleResult": True,
            "requiresHumanApproval": False,
            "mutationAllowed": False,
            "guard": "source_saved_classified_chunked_before_reply",
        },
        "storedReference": stored_reference,
        "evidenceRefs": source_refs,
        "outputRefs": source_refs,
        "testsOrChecks": [
            "已读取 SourceMaterial 引用。",
            f"正文抽取状态：{'成功' if extracted_text else '未完成'}。",
            f"已完成资料分类：{classification['categoryLabel']}。",
            "已按 SourceMaterial 存储，检索索引负责切片。",
        ],
        "nextActions": [
            "知识工程 Agent 后续按周期统一复盘、清理、合并和系统化。",
            "如正文抽取未完成，请补充可访问正文或飞书文档权限。",
        ],
        "openRisks": [] if extracted_text else [f"正文抽取未完成：{extraction.get('error') or '未知原因'}"],
    }


def store_research_material_reference(bundle: Bundle, source_ref: str, reference: dict[str, Any]) -> str:
    path = bundle.root / source_ref
    if not source_ref.strip() or not path.exists():
        return ""
    fm = load_object(path)
    if fm.get("type") != "SourceMaterial":
        return ""
    before_status = str(fm.get("status") or "")
    title = str(reference.get("title") or fm.get("title") or path.stem)
    source_url = str(reference.get("sourceUrl") or fm.get("sourceRef") or "")
    content = str(reference.get("content") or "")
    extraction_ok = bool(reference.get("extractionOk"))
    browser_pending = bool(reference.get("browserPending")) and not extraction_ok and is_wechat_url(source_url)
    tags = as_list(reference.get("tags"))
    status = "browser_pending" if browser_pending else "stored"
    extraction_status = "browser_pending" if browser_pending else ("extracted" if extraction_ok else "referenced")
    fm.update(
        {
            "title": title,
            "description": "Source reference captured by Feishu direct material intake; browser extraction pending." if browser_pending else "Classified source reference stored by Feishu direct material intake.",
            "status": status,
            "extractionStatus": extraction_status,
            "extractionTool": "feishu-direct-material-processor",
            "sourceRef": source_url or str(fm.get("sourceRef") or ""),
            "knowledgeCategory": str(reference.get("category") or "general_reference"),
            "knowledgeCategoryLabel": str(reference.get("categoryLabel") or "通用资料"),
            "topicTags": tags,
            "chunkingStrategy": "retrieval_index_chunk_text_900_chars",
            "updatedAt": utc_now(),
        }
    )
    body = "\n".join(
        [
            "## Source",
            "",
            f"- sourceRef: {source_url or 'none'}",
            f"- sourceKind: {reference.get('sourceKind') or fm.get('materialType') or 'unknown'}",
            f"- extractionStatus: {fm['extractionStatus']}",
            f"- extractionError: {reference.get('extractionError') or 'none'}",
            "",
            "## Classification",
            "",
            f"- category: {fm['knowledgeCategory']}",
            f"- categoryLabel: {fm['knowledgeCategoryLabel']}",
            f"- tags: {', '.join(tags) if tags else 'none'}",
            "",
            "## Summary",
            "",
            str(reference.get("summary") or title),
            "",
            "## Extracted Text",
            "",
            content or ("正文尚未入库；等待浏览器补抓公众号正文。" if browser_pending else "正文尚未抽取成功；请补充可访问链接、正文或文档权限。"),
            "",
            "## Retrieval",
            "",
            "- Browser extraction pending; do not answer from this material yet." if browser_pending else "- Stored as SourceMaterial reference.",
            "- Retrieval index chunks this body for search." if not browser_pending else "- Retrieval starts after browser extraction succeeds.",
            "- This material is source evidence, not verified policy or approved workflow.",
        ]
    )
    write_text(path, render_doc(fm, body))
    create_audit_log(
        bundle,
        "feishu-direct-material-processor",
        "material.referenceStored",
        rel(path, bundle.root),
        before=before_status,
        after=status,
        policy_result="browser_pending" if browser_pending else "source_reference",
        details=f"sourceRef={source_url}\ncategory={fm['knowledgeCategory']}\nchunking={fm['chunkingStrategy']}\nextractionStatus={extraction_status}",
    )
    return rel(path, bundle.root)


def store_research_material_references(bundle: Bundle, source_refs: list[str], reference: dict[str, Any]) -> list[str]:
    stored: list[str] = []
    for source_ref in source_refs:
        stored_ref = store_research_material_reference(bundle, source_ref, reference)
        if stored_ref:
            stored.append(stored_ref)
    return stored


def pending_wechat_browser_source_refs(bundle: Bundle, limit: int = 20) -> list[str]:
    source_roots = [
        bundle.root / "projects" / "company-knowledge-core" / "sources",
        bundle.root / "sources",
    ]
    refs: list[str] = []
    for source_root in source_roots:
        if not source_root.exists():
            continue
        for path in sorted(source_root.glob("*.md")):
            if limit and len(refs) >= limit:
                return refs
            try:
                source = load_object(path)
            except Exception:
                continue
            source_url = str(source.get("sourceRef") or "")
            if source.get("type") != "SourceMaterial":
                continue
            if str(source.get("status") or "") != "browser_pending" and str(source.get("extractionStatus") or "") != "browser_pending":
                continue
            if not is_wechat_url(source_url):
                continue
            refs.append(rel(path, bundle.root))
    return refs


def repair_pending_wechat_browser_sources(bundle: Bundle, limit: int = 20, publish_index: bool = True) -> dict[str, Any]:
    repaired: list[str] = []
    failed: list[dict[str, str]] = []
    for source_ref in pending_wechat_browser_source_refs(bundle, limit=limit):
        payload = source_material_payload(bundle, source_ref)
        source_url = infer_material_url(str(payload.get("sourceRef") or ""), str(payload.get("content") or ""))
        if not is_wechat_url(source_url):
            continue
        extraction = fetch_wechat_article_text_with_browser(source_url)
        if not extraction.get("ok"):
            failed.append({"sourceRef": source_ref, "error": str(extraction.get("error") or "browser extraction failed")})
            create_audit_log(
                bundle,
                "feishu-browser-material-repair",
                "material.browserExtractionFailed",
                source_ref,
                before="browser_pending",
                after="browser_pending",
                policy_result="browser_pending",
                details=f"sourceRef={source_url}\nerror={str(extraction.get('error') or '')}",
            )
            continue
        text = str(extraction.get("text") or "").strip()
        title = str(extraction.get("title") or payload.get("title") or "公众号资料")
        classification = classify_research_reference(title, text, str(extraction.get("kind") or "wechat_article_browser"))
        summary = f"已通过浏览器补抽公众号资料《{title}》。 原始链接：{source_url}。 已归类为{classification['categoryLabel']}并存入来源资料库。"
        reference = {
            "title": title,
            "sourceUrl": source_url,
            "sourceKind": str(extraction.get("kind") or "wechat_article_browser"),
            "extractionOk": True,
            "extractionError": "",
            "browserPending": False,
            "content": text,
            "summary": summary,
            "category": classification["category"],
            "categoryLabel": classification["categoryLabel"],
            "tags": classification["tags"],
            "sourceRefs": [source_ref],
        }
        stored_ref = store_research_material_reference(bundle, source_ref, reference)
        if stored_ref:
            repaired.append(stored_ref)
    publish_result: dict[str, Any] = {}
    if repaired and publish_index:
        try:
            publish_result = publish_knowledge_bundle(bundle, actor="feishu-browser-material-repair", reason=f"browser repaired {len(repaired)} wechat materials")
        except Exception as exc:
            publish_result = {"ok": False, "error": str(exc)}
    return {"checked": len(repaired) + len(failed), "repaired": repaired, "failed": failed, "publishResult": publish_result}


def validate_codex_worker_result_for_feishu(result_payload: dict[str, Any]) -> None:
    detail = str(result_payload.get("feishuDetail") or "")
    if not detail.strip():
        raise KnowledgeError("Codex Worker result missing Feishu-readable detail")
    if "资料已入库：" not in detail and "资料已接收，正在浏览器补抓：" not in detail:
        raise KnowledgeError("Codex Worker result missing material intake status")
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
    stored_refs = store_research_material_references(bundle, result_payload["evidenceRefs"], result_payload["storedReference"])
    if stored_refs:
        result_payload["outputRefs"] = stored_refs
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


def process_research_material_source(
    bundle: Bundle,
    source_ref: str,
    publish_index: bool = True,
) -> dict[str, Any]:
    pseudo_task = {
        "title": "Process source material",
        "sourceMaterialRefs": [source_ref],
        "researchQuestion": source_material_payload(bundle, source_ref).get("content", ""),
    }
    result_payload = build_research_material_result(bundle, pseudo_task)
    validate_codex_worker_result_for_feishu(result_payload)
    stored_refs = store_research_material_references(bundle, result_payload["evidenceRefs"], result_payload["storedReference"])
    publish_result: dict[str, Any] = {}
    if publish_index:
        try:
            publish_result = publish_knowledge_bundle(bundle, actor="feishu-direct-material-processor", reason=f"feishu source material stored {source_ref}")
        except Exception as exc:
            publish_result = {"ok": False, "error": str(exc)}
    return {
        "sourceRef": source_ref,
        "status": "browser_pending" if result_payload["storedReference"].get("browserPending") else "stored",
        "storedRefs": stored_refs,
        "detail": str(result_payload.get("feishuDetail") or result_payload["summary"]),
        "publishResult": publish_result,
    }
