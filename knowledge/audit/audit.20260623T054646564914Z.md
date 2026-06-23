---
type: AuditLog
title: audit.20260623T054646564914Z
timestamp: "2026-06-23T05:46:46Z"
auditId: audit.20260623T054646564914Z
actor: agent.company.architecture
action: runtime.postgres_local_port_mapping.update
targetRef: deploy/lighthouse/docker-compose.yml
before: "postgres service had no host port mapping; README used 127.0.0.1:5432 but local validation could not connect"
after: postgres service maps POSTGRES_BIND/POSTGRES_PORT to container 5432; README and .env.example use 55432 for local validation
policyResult: environment_validation_fix
---

## Details

Updated deploy/lighthouse/docker-compose.yml, deploy/lighthouse/.env.example, and README.md so local PostgreSQL runtime validation can use host port 55432 without changing secret-bearing deploy/lighthouse/.env.
