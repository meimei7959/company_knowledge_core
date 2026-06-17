from __future__ import annotations

import hmac
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .core import (
    Bundle,
    KnowledgeError,
    export_api_snapshot,
    gateway_context,
    invoke_tool,
    review_path,
    search_audit_logs,
    search_retrieval,
    search_index,
    validate_bundle,
)
from .feishu import handle_feishu_event


class KnowledgeHTTPServer(ThreadingHTTPServer):
    def __init__(self, server_address: tuple[str, int], bundle: Bundle, api_token: str = ""):
        self.bundle = bundle
        self.api_token = api_token
        super().__init__(server_address, KnowledgeHandler)


class KnowledgeHandler(BaseHTTPRequestHandler):
    server: KnowledgeHTTPServer

    def log_message(self, format: str, *args: object) -> None:
        return

    def _json(self, status: int, payload: dict | list) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length == 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw)

    def _authorized(self) -> bool:
        token = self.server.api_token
        if not token:
            return True
        header = self.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return False
        supplied = header.removeprefix("Bearer ").strip()
        return hmac.compare_digest(supplied, token)

    def _reject_unauthorized(self) -> None:
        self._json(401, {"error": "unauthorized"})

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/health":
                problems = validate_bundle(self.server.bundle)
                self._json(200 if not problems else 500, {"ok": not problems, "problems": problems})
            elif not self._authorized():
                self._reject_unauthorized()
            elif parsed.path == "/v0/snapshot":
                self._json(200, export_api_snapshot(self.server.bundle))
            elif parsed.path == "/v0/objects":
                query = parse_qs(parsed.query)
                filters = {
                    "type": first(query, "type"),
                    "status": first(query, "status"),
                    "projectId": first(query, "projectId"),
                    "agentId": first(query, "agentId"),
                    "toolId": first(query, "toolId"),
                    "riskLevel": first(query, "riskLevel"),
                    "text": first(query, "text"),
                }
                self._json(200, {"apiVersion": "v0.1", "kind": "ObjectList", "objects": search_index(self.server.bundle, filters)})
            elif parsed.path == "/v0/rag/search":
                query = parse_qs(parsed.query)
                rows = search_retrieval(
                    self.server.bundle,
                    first(query, "query"),
                    project_id=first(query, "projectId"),
                    scopes=query.get("scope") or [],
                    limit=int(first(query, "limit") or "5"),
                )
                self._json(200, {"apiVersion": "v0.1", "kind": "RetrievalResult", "chunks": rows})
            elif parsed.path == "/v0/audit":
                query = parse_qs(parsed.query)
                rows = search_audit_logs(
                    self.server.bundle,
                    project_id=first(query, "projectId"),
                    agent_id=first(query, "agentId"),
                    tool_id=first(query, "toolId"),
                    target=first(query, "target"),
                )
                self._json(200, {"apiVersion": "v0.1", "kind": "AuditLogList", "auditLogs": rows})
            else:
                self._json(404, {"error": "not found"})
        except KnowledgeError as exc:
            self._json(400, {"error": str(exc)})

    def do_POST(self) -> None:
        try:
            if self.path == "/integrations/feishu/events":
                payload = self._read_json()
                self._json(200, handle_feishu_event(self.server.bundle, payload))
                return
            if not self._authorized():
                self._reject_unauthorized()
                return
            payload = self._read_json()
            if self.path == "/v0/gateway/context":
                result = gateway_context(
                    self.server.bundle,
                    require(payload, "projectId"),
                    require(payload, "agentId"),
                    require(payload, "task"),
                )
                self._json(200, result)
            elif self.path == "/v0/review/update":
                audit_path = review_path(
                    self.server.bundle,
                    Path(require(payload, "target")),
                    require(payload, "status"),
                    require(payload, "reviewer"),
                )
                self._json(200, {"apiVersion": "v0.1", "kind": "ReviewResult", "auditRef": str(audit_path)})
            elif self.path == "/v0/tool/invoke":
                result = invoke_tool(
                    self.server.bundle,
                    require(payload, "toolId"),
                    require(payload, "projectId"),
                    require(payload, "agentId"),
                    str(payload.get("input", "")),
                    bool(payload.get("execute", False)),
                )
                self._json(200, result)
            else:
                self._json(404, {"error": "not found"})
        except (KnowledgeError, KeyError, json.JSONDecodeError) as exc:
            self._json(400, {"error": str(exc)})


def first(query: dict[str, list[str]], key: str) -> str:
    values = query.get(key) or [""]
    return values[0]


def require(payload: dict, key: str) -> str:
    value = payload.get(key)
    if not value:
        raise KnowledgeError(f"missing required field: {key}")
    return str(value)


def serve(bundle: Bundle, host: str, port: int) -> None:
    httpd = KnowledgeHTTPServer((host, port), bundle, os.environ.get("ZHENZHI_KNOWLEDGE_API_TOKEN", ""))
    print(f"zhenzhi-knowledge API listening on http://{host}:{httpd.server_port}")
    httpd.serve_forever()
