# COM · Tenancy, concurrency, limits, performance, testing, risks, sources

> Source: `docs/MOON-2389 Client Operating Model.docx.pdf` pp. 34–38 · Source ID `com`

The database itself enforces tenant boundaries, so a bug in one RPC can't link one tenant's role to another
tenant's activity.

## Tenancy (pp. 34–35)
- Every table, children included, carries `tenant`. FKs point at `subscriber(tenant)` (94 existing tables do; 19 use `subscriber(id)`).
- Cross-entity references use **composite FKs on (tenant, id)**, backed by UNIQUE (tenant, id) on the parent. Examples: activity → role, stage → policy, activity → agent.
  - Agent case needs a new UNIQUE (tenant, form_id) on `query_form` (form_id already unique, so it always holds).
  - Nullable references use `ON DELETE SET NULL (column)` so a delete never nulls tenant.
- RPCs take `p_tenant` from `user.tenant`, or from the project row on project routes. **A request body never supplies the tenant.**
- A reference to another tenant's id returns **404, not 403**, so ids don't leak.
- Internal API derives tenant from the project/methodology it loads. Tenant-wide routes carry the tenant in the path and check it against the key's `allowed_tenants`.
- **Confidential projects:** ISS checks access with `get_project_user_access_level`, which lacks the confidential check that `get_project_if_access_level` applies. **The fix must ship before runtime data is exposed.** Until decided otherwise, the event feed leaves confidential projects out.

## Concurrency (p. 35)
- Optimistic revisions: `client_methodologies.revision`, `client_policies.revision`, `project_methodology.revision`. Stale write → 409 `*.revision_conflict` with current revision in `meta`.
- Each RPC locks its aggregate root `FOR UPDATE` first (methodology, policy, or project_methodology row).
- Reordering runs in one RPC using deferrable unique constraints on position.
- Suggestion apply keeps its existing distributed lock. First assignee to apply wins.

## Limits (p. 35)

| Item | Limit | Error code |
|---|---|---|
| Name | 200 chars | `*.name_too_long` |
| Description | 5,000 chars | `*.description_too_long` |
| Prompt | 10,000 chars | `operating_model.activity.prompt_too_long` |
| Stages per methodology | 50 | `operating_model.methodology.too_many_stages` |
| Activities per stage or policy | 100 | `operating_model.activity.too_many` |
| Roles per activity | 20 | `operating_model.activity.too_many_roles` |
| Document size | 25 MB | `operating_model.methodology.file_too_large` |

*(Note: role names are 1–100 chars per the roles table, vs the 200-char general name limit.)*

## Performance (p. 35)
- Expected per tenant: up to 50 methodologies, 20 stages each, 30 activities per container ⇒ one tree < ~1,000 rows; snapshot < 200 KB.
- Draft tree read by one RPC returning jsonb (avoids N+1 PostgREST calls from Python).
- **Context API caches in Redis per project for 60 s**; events on that project (stage, roles, methodology) invalidate it.
- Production runs **Postgres 15.8**; migrations avoid newer features (the `combine-sprint-migrations` skill has the grep list). `ON DELETE SET NULL (column)` and `xid8` are available in 15.

## Testing strategy (p. 36)
Most logic lives in plpgsql RPCs, so the integration tier carries the weight. ISS already runs it against real
Postgres, PostgREST and GoTrue (`tests/harness/`).

| Tier | Location | Covers |
|---|---|---|
| Unit | `integration-sync-service/tests/unit/modules/<module>/` | Request validators and limits, catalog mapping, file-type detection, role-to-user resolution, error-code mapping |
| Integration | `integration-sync-service/tests/integration/modules/<module>/` | Every endpoint for admin vs member vs outsider (401/403/404). Tenant isolation with two factory tenants. Atomicity (failure midway persists nothing). Revision conflicts. Role delete cascades. Publish idempotency. Pinned project unaffected by later publish. Suggestion ingestion with role resolution and dedup. One event row per action. Feed order and safety lag. |
| Migration | `combine-sprint-migrations` skill (`roundtrip.sh`) | up → down → up on scratch DB, parity with `schema.sql`, PG15 compatibility |
| Cross-service | `workflow-service/tests` | `RemovePreviousCallSuggestions` leaves orchestrator suggestions alone |
| Contract | Shared JSON Schema exported from Pydantic models | AI team validates its payloads against schemas and example fixtures in CI; Veda runs the same fixtures through ingestion |
| Frontend unit | Jest, specs next to components | NGXS states, canvas store (undo/redo, tree serialization), form validation |
| Frontend e2e | Playwright (`frontend/tests/`) | Create a role and assign it in the team modal. Create a policy with activities. Build, save, publish a methodology. Assign it in Project Settings. Move the stage from the stage card. |

Setup notes: the test harness loads `schema.sql`, so a new table is visible to tests only after `make pull-schema`
(or a harness SQL file) includes it. Each route change also updates its Postman YAML under `postman/collections/`.

## Risks (p. 37)

| Risk | Impact | Mitigation |
|---|---|---|
| Shared `X-API-KEY` reused for the AI team | Cross-tenant read/write with all flags on | Scoped key must exist before any access is handed out |
| Call regeneration deletes orchestrator suggestions | Suggestions disappear silently | Trigger-type filter in `RemovePreviousCallSuggestions` ships with the ingestion endpoint |
| Closed suggestion-type enum blocks new activity types | Every new type costs ISS + frontend work | Map onto existing types; add new types only when product asks for a specific UI |
| "Stage" means three things | UI confusion, wrong data shown | Use "methodology stage" in code/API; product decision on Overview card (OQ #19) |
| No Python transactions in ISS | Partial writes if logic leaks into Python | Every multi-row write is one RPC; code review enforces it |
| Frontend writes to `project`, agent assignments and `users.default_project_team_role_id` bypass ISS | No event for owner/member changes | DB triggers write events for owner changes; team members go through ISS; roles cascade with assignment row |

## Sources the doc was based on (pp. 37–38) — read 2026-10-26, paths relative to the veda workspace
- **Product:** `features/client-methodology/base.md` (MOON-2389 → MOON-2394); `meetings/1.md` (roles, Gate → Stage, Action → Activity, AI team split); `meetings/2.md` (20 Oct: policies, triggers).
- **Figma — Company Methodologies** frames: Org Defaults tiles, Company Methodologies list, Create Methodology, Upload tooltip, Methodology editor, Editor + Engage with Agent, Methodology Settings, Create Stage, Create Activity, Add Policy, Policies list, Create Policy, Create Policy – Add Activity, Trigger dropdown, Type dropdown, Project Interface – Project Roles, Account Settings – Project role, Project Overview (Certinia stage), View methodology suggestion, Manage project team, Project Settings – General, Project Settings – Methodology, Method Deviation.
- **integration-sync-service:** `schema.sql` (project, project_assignment, suggestions, suggestion_settings, suggestion_scopes, tenant_audit_trail, private.log_tenant_audit_trail, project_health_webhook_*, users, query_form); `src/modules/ticketing/collection_template/` (reference module); `src/modules/suggestion/` (routers, services/manager_service.py, enums/base.py, types/); `src/modules/project/deps.py`, `src/modules/auth/guards.py`, `src/shared/deps.py`; `src/modules/file/storage.py`, `src/modules/ticketing/attachment/_guards.py`; `src/modules/ticketing/ticket_event/` (precedent for event history).
- **Other services:** suggestion-service (`src/modules/api/`, `src/modules/engine/ARCHITECTURE.md`, `CONTEXT.md`); workflow-service (`src/workflows/generate_call_suggestions.py`, `src/event_handlers/`, `src/modules/engine/`); frontend (`org-defaults/pages/org-list/`, `project-config-list/`, `users-actions-modal/`, `settings-modal/`, `certinia-stage-card/`, `agent-studio/.../agent-workflow/`, `suggestion-card/`); pathfinder-service (`main.py /textextract`, `mimetypes_list.py`).
