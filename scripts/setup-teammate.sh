#!/usr/bin/env bash
# Bootstrap a teammate's local AI tool against the Zhenzhi Knowledge Core.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REMOTE_URL="${ZHENZHI_KNOWLEDGE_REMOTE:-https://github.com/meimei7959/company_knowledge_core.git}"
PROD_API_URL="${ZHENZHI_KNOWLEDGE_API_PROD:-http://124.221.138.151/knowledge-api}"
TOKEN_ENV="${ZHENZHI_KNOWLEDGE_API_TOKEN_ENV:-ZHENZHI_KNOWLEDGE_API_TOKEN_PROD}"
DEFAULT_PROJECT="company-knowledge-core"
USER_ID="${USER:-unknown}"
AI_TOOL="codex"
AGENT_ID=""
AGENT_NAME=""
PURPOSE="local AI development"
SKIP_PIP_INSTALL=0

usage() {
  cat <<'USAGE'
Usage:
  export ZHENZHI_KNOWLEDGE_API_TOKEN_PROD=<team-token>
  bash scripts/setup-teammate.sh --user-id <name> --ai-tool codex

Options:
  --user-id <id>             teammate id, default current $USER
  --ai-tool <tool>           codex | antigravity | claude | other, default codex
  --agent-id <id>            default agent.<user-id>.<ai-tool>
  --agent-name <name>        default "<user-id> <ai-tool>"
  --project <project-id>     default company-knowledge-core
  --api-url <url>            default http://124.221.138.151/knowledge-api
  --token-env <env-name>     default ZHENZHI_KNOWLEDGE_API_TOKEN_PROD
  --skip-pip-install         skip local package install
USAGE
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --user-id)
      USER_ID="$2"
      shift 2
      ;;
    --ai-tool)
      AI_TOOL="$2"
      shift 2
      ;;
    --agent-id)
      AGENT_ID="$2"
      shift 2
      ;;
    --agent-name)
      AGENT_NAME="$2"
      shift 2
      ;;
    --project)
      DEFAULT_PROJECT="$2"
      shift 2
      ;;
    --api-url)
      PROD_API_URL="$2"
      shift 2
      ;;
    --token-env)
      TOKEN_ENV="$2"
      shift 2
      ;;
    --skip-pip-install)
      SKIP_PIP_INSTALL=1
      shift
      ;;
    -h|--help|help)
      usage
      exit 0
      ;;
    *)
      echo "unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [ -z "${AGENT_ID}" ]; then
  AGENT_ID="agent.${USER_ID}.${AI_TOOL}"
fi

if [ -z "${AGENT_NAME}" ]; then
  AGENT_NAME="${USER_ID} ${AI_TOOL}"
fi

if [ -z "${!TOKEN_ENV:-}" ]; then
  echo "missing token env: ${TOKEN_ENV}" >&2
  echo "ask the project owner for the team token, then run:" >&2
  echo "  export ${TOKEN_ENV}=<team-token>" >&2
  exit 1
fi

cd "$ROOT"

if [ "$SKIP_PIP_INSTALL" -eq 0 ]; then
  echo "==> install zhenzhi-knowledge CLI"
  python3 -m pip install --user -e .
fi

echo "==> write local connector config"
python3 -m zhenzhi_knowledge --root "$ROOT" install \
  --user-id "$USER_ID" \
  --ai-tool "$AI_TOOL" \
  --agent-id "$AGENT_ID" \
  --remote "$REMOTE_URL" \
  --default-project "$DEFAULT_PROJECT" \
  --register-agent \
  --agent-name "$AGENT_NAME" \
  --purpose "$PURPOSE"

echo "==> configure production API profile"
python3 - "$ROOT" "$PROD_API_URL" "$TOKEN_ENV" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
api_url = sys.argv[2].rstrip("/")
token_env = sys.argv[3]
config_path = root / ".zhenzhi" / "config.json"
config = json.loads(config_path.read_text(encoding="utf-8"))
profiles = config.setdefault("profiles", {})
profiles["production"] = {
    "backend": "api",
    "apiBaseUrl": api_url,
    "apiTokenEnv": token_env,
}
config["activeProfile"] = "production"
config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
PY

echo "==> verify production API"
python3 -m zhenzhi_knowledge --root "$ROOT" status
python3 -m zhenzhi_knowledge --root "$ROOT" api export >/dev/null

cat <<DONE

Setup complete.

Entrypoint:
  ${ROOT}/.zhenzhi/agent-entrypoint.md

Production API:
  ${PROD_API_URL}

Daily commands:
  zhenzhi-knowledge start --project ${DEFAULT_PROJECT} --agent ${AGENT_ID} --task "<task>"
  zhenzhi-knowledge finish --project ${DEFAULT_PROJECT} --agent ${AGENT_ID} --summary "<summary>"
DONE
