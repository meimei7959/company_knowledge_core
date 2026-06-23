#!/usr/bin/env bash
# Deploy company_knowledge_core API to the same Lighthouse host used by Agent Work.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
HOST="${LIGHTHOUSE_HOST:-124.221.138.151}"
IDENTITY="${LIGHTHOUSE_IDENTITY:-$HOME/.ssh/lighthouse_agentwork}"
REMOTE_BASE="/opt/projects/company_knowledge_core"
REMOTE_REPO="${REMOTE_BASE}/repo"
COMPOSE_PROJECT="zhenzhi_knowledge"
ENV_LOCAL="${ROOT}/deploy/lighthouse/.env"
CONTROL_PATH="/tmp/zhenzhi-knowledge-${HOST}-%r@%h:%p"
SSH_OPTS=(
  -i "$IDENTITY"
  -o IdentitiesOnly=yes
  -o StrictHostKeyChecking=accept-new
  -o ServerAliveInterval=30
  -o ControlMaster=auto
  -o ControlPersist=120
  -o ControlPath="$CONTROL_PATH"
)

if [ ! -f "$ENV_LOCAL" ]; then
  echo "missing ${ENV_LOCAL}; copy deploy/lighthouse/.env.example and set ZHENZHI_KNOWLEDGE_API_TOKEN" >&2
  exit 1
fi

if grep -q '^ZHENZHI_KNOWLEDGE_API_TOKEN=CHANGE_ME' "$ENV_LOCAL"; then
  echo "ZHENZHI_KNOWLEDGE_API_TOKEN is still CHANGE_ME" >&2
  exit 1
fi

pick_ssh_user() {
  if [ -n "${LIGHTHOUSE_USER:-}" ]; then
    echo "${LIGHTHOUSE_USER}"
    return
  fi
  for candidate in ubuntu root; do
    if ssh "${SSH_OPTS[@]}" -o BatchMode=yes -o ConnectTimeout=8 "${candidate}@${HOST}" "true" >/dev/null 2>&1; then
      echo "${candidate}"
      return
    fi
  done
  echo "cannot SSH to ${HOST}" >&2
  exit 1
}

USER="$(pick_ssh_user)"
SSH_TARGET="${USER}@${HOST}"
RSYNC_SSH="ssh ${SSH_OPTS[*]}"
SUDO="sudo"
if [ "$USER" = "root" ]; then
  SUDO=""
fi

echo "==> SSH ${SSH_TARGET}"
ssh "${SSH_OPTS[@]}" "${SSH_TARGET}" "${SUDO} mkdir -p ${REMOTE_REPO} && ${SUDO} chown -R ${USER}:${USER} ${REMOTE_BASE}"

echo "==> sync repository"
rsync -az --delete -e "${RSYNC_SSH}" \
  --filter "P /agents/***" \
  --filter "P /knowledge/***" \
  --filter "P /policies/***" \
  --filter "P /projects/***" \
  --filter "P /runs/***" \
  --filter "P /tools/***" \
  --exclude ".git/" \
  --exclude ".zhenzhi/" \
  --exclude ".codegraph/" \
  --exclude "backups/" \
  --exclude "deploy/lighthouse/.env" \
  "${ROOT}/" "${SSH_TARGET}:${REMOTE_REPO}/"

rsync -az -e "${RSYNC_SSH}" \
  "${ENV_LOCAL}" "${SSH_TARGET}:${REMOTE_REPO}/deploy/lighthouse/.env"

rsync -az -e "${RSYNC_SSH}" \
  "${ROOT}/.zhenzhi/config.json" "${SSH_TARGET}:${REMOTE_REPO}/.zhenzhi/config.json"

echo "==> env synced"

echo "==> docker compose up"
ssh "${SSH_OPTS[@]}" "${SSH_TARGET}" bash -s -- "${COMPOSE_PROJECT}" <<REMOTE
set -euo pipefail
COMPOSE_PROJECT="\$1"
cd "${REMOTE_REPO}/deploy/lighthouse"
DC="docker compose"
if ! ${SUDO} docker compose version >/dev/null 2>&1; then
  DC="docker-compose"
fi
if ${SUDO} docker ps -a --format '{{.Names}}' | grep -qx 'zhenzhi-knowledge-api'; then
  ${SUDO} docker rm -f zhenzhi-knowledge-api >/dev/null 2>&1 || true
fi
${SUDO} \${DC} -p "\${COMPOSE_PROJECT}" up -d --build --force-recreate
${SUDO} \${DC} -p "\${COMPOSE_PROJECT}" ps
REMOTE

echo "==> nginx route /knowledge-api/"
ssh "${SSH_OPTS[@]}" "${SSH_TARGET}" bash -s <<'REMOTE'
set -euo pipefail
NGINX_SITE="/etc/nginx/sites-available/agentwork"
if [ ! -f "${NGINX_SITE}" ]; then
  echo "skip nginx route: ${NGINX_SITE} not found"
  exit 0
fi
if grep -q "location /knowledge-api/" "${NGINX_SITE}"; then
  echo "nginx route already exists"
  exit 0
fi
sudo cp "${NGINX_SITE}" "${NGINX_SITE}.bak.$(date +%Y%m%dT%H%M%S)"
sudo python3 - "${NGINX_SITE}" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text()
block = """    location /knowledge-api/ {
        proxy_pass http://127.0.0.1:8765/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
    }

"""
marker = "    location / {"
if marker not in text:
    raise SystemExit("nginx marker not found")
path.write_text(text.replace(marker, block + marker, 1))
PY
sudo nginx -t
sudo systemctl reload nginx || sudo systemctl restart nginx
REMOTE

echo "==> health"
ssh "${SSH_OPTS[@]}" "${SSH_TARGET}" bash -s <<'REMOTE'
set -euo pipefail
wait_health() {
  url="$1"
  label="$2"
  for attempt in $(seq 1 30); do
    if curl -fsS "$url"; then
      echo ""
      echo "${label} healthy"
      return 0
    fi
    sleep 2
  done
  echo "${label} health check failed after waiting" >&2
  exit 1
}
wait_health "http://127.0.0.1:8765/health" "api"
wait_health "http://127.0.0.1/knowledge-api/health" "nginx route"
REMOTE

echo "==> publish knowledge indexes"
ssh "${SSH_OPTS[@]}" "${SSH_TARGET}" bash -s <<'REMOTE'
set -euo pipefail
cd /opt/projects/company_knowledge_core/repo/deploy/lighthouse
TOKEN="$(grep '^ZHENZHI_KNOWLEDGE_API_TOKEN=' .env | head -n 1 | cut -d= -f2-)"
if [ -z "${TOKEN}" ] || [ "${TOKEN}" = "CHANGE_ME" ]; then
  echo "missing ZHENZHI_KNOWLEDGE_API_TOKEN in remote .env" >&2
  exit 1
fi
curl -fsS \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"actor":"deploy.lighthouse","reason":"deploy-script-post-health"}' \
  http://127.0.0.1:8765/v0/publish/rebuild
echo ""
REMOTE
echo ""
echo "deployed: http://${HOST}/knowledge-api"
