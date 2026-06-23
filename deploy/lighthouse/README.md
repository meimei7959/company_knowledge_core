# Lighthouse Deployment

This deploys the knowledge API as an independent service on the Agent Work Lighthouse host.

Default remote path:

```txt
/opt/projects/company_knowledge_core/repo
```

Default container:

```txt
zhenzhi-knowledge-api
```

Server allocation:

```txt
Agent Work compose project: lighthouse
Agent Work app port: 127.0.0.1:8089
Knowledge compose project: zhenzhi_knowledge
Knowledge API port: 127.0.0.1:8765
Public route: http://124.221.138.151/knowledge-api
Remote path: /opt/projects/company_knowledge_core/repo
```

Setup:

```bash
cp deploy/lighthouse/.env.example deploy/lighthouse/.env
python3 -c "import secrets; print('ZHENZHI_KNOWLEDGE_API_TOKEN=' + secrets.token_urlsafe(32))"
```

Put the generated token in `deploy/lighthouse/.env`.

Deploy:

```bash
bash deploy/lighthouse/deploy.sh
```

Publish behavior:

- Container startup runs `zhenzhi-knowledge publish`, which validates the bundle and rebuilds object/RAG indexes.
- `deploy.sh` calls `POST /v0/publish/rebuild` after health checks, so synced knowledge is published into the service index before deploy is considered successful.
- Runtime retrieval still checks source fingerprints before search and rebuilds stale RAG indexes as a final fallback.

Client profile:

```bash
export ZHENZHI_KNOWLEDGE_API_PROD=http://124.221.138.151/knowledge-api
export ZHENZHI_KNOWLEDGE_API_TOKEN_PROD=<token>
zhenzhi-knowledge profile use production
zhenzhi-knowledge api export
```

Keep `ZHENZHI_KNOWLEDGE_API_BIND=127.0.0.1`. The deploy script adds an Nginx route at `/knowledge-api/`.
