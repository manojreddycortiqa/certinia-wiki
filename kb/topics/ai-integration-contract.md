# Veda ↔ AI orchestrator contract: proposal vs answer

> Synthesis of `com` (Veda/Uinno proposal, Oct 26, 2026 — `sources/client-operating-model/11-ai-team-topics.md` + architecture files)
> and `ai-labs-answers` (AI Labs reply, Oct 30, 2026 — `sources/ai-labs-answers.md`).
> Legend: ✅ aligned · ⚠️ partly aligned / needs detail · ❌ conflict or gap to resolve.
> This is an interpretation; when exact wording matters, quote the source files.

## Summary table

| Area | Veda proposed (COM) | AI Labs answered | Status |
|---|---|---|---|
| Event delivery | Pull feed `GET /events?after={cursor}` from `operating_model_audit_trail` (outbox); webhook as alternative | One durable, replayable feed for all selected triggers, same-transaction writes; AI owns consumer + cursor | ✅ mechanism |
| Which events | Operating-model + `project.methodology.*`, `project.team.changed`, `project.health.status_changed`, `project.owner.changed` | Dec triggers: `callpilot.call.ended`, `project.health.status_changed`, `project.methodology.stage_changed` (+ `schedule.daily_check` if needed) | ❌ `callpilot.call.ended` is **not in COM's feed** (today a Celery task to WorkflowService); `schedule.daily_check` new |
| Event payload | IDs only; `before`/`after` changed fields, `context` jsonb | IDs/refs only, **payload version**, seq, `occurred_at`; no message/transcript text | ⚠️ COM rows carry `before`/`after` jsonb — check no sensitive text leaks; add payload version |
| Retention | No pruning, few hundred rows/tenant/day | Append-only v1, minimal sensitive fields; long-term retention agreed before promising indefinite storage | ⚠️ |
| Confidential projects | Left out of feed until decided; ISS access-check fix must ship first | Left out of feed **and context reads**; agreed behaviour when confidentiality changes | ⚠️ need "confidentiality changed" behaviour |
| Context read | `GET /projects/{id}/context`: project, team+roles, methodology+version+current stage, policies (stage/standalone) | Adds: health, **key dates** (start, go-live, milestones, training), assignment metadata (date added, allocation), policies as `{policy_id, revision}` or resolved, **separate instructions field** (OQ #7), **suggestion history**, **signals** (Slack/Teams connected) | ❌ several fields missing in COM's context |
| Methodology input | Snapshot JSON (resolved view) via `GET /methodology-versions/{id}` | Same shape as contract; **interim JSON file** with `schema_version` now (incl. one standalone policy + one activity with explicit agent) | ✅ shape; ⚠️ interim file date/owner = Veda Accelerate |
| Schemas | Contract tests: shared JSON Schema exported from Pydantic, AI validates fixtures in CI | JSON Schema with a version, validated in CI | ✅ |
| Errors / retries / cache | `{detail, code, meta, request_id}`; Redis 60 s per project, invalidated by events | Same error shape; retry 5xx/timeouts never 4xx; 60 s cache fine | ✅ |
| Suggestion endpoint | `POST /internal/orchestration/projects/{id}/suggestions`, batch, per-item accept/reject, dedup key | Per-item result `created`/`duplicate`/`rejected` + error code | ✅ (make result enum explicit) |
| Suggestion fields | type, title, description, payload, targets, deduplication_key, source `{kind, policy_id, activity_id, event_seq}` | + **applicable role**, **evidence + confidence (low/med/high)**, **expires_at**, source incl. **policy revision + methodology version** | ⚠️ add evidence/confidence/role/expires_at; COM's trigger jsonb already gains methodology_version_id, policy_revision, seq |
| Outcome events | Not in COM event catalog | Required in v1 feed: `applied`, `dismissed`, `expired` (before cleanup deletes), action `succeeded`/`failed`; with ids, actor, request id, error code | ❌ gap in COM |
| Who receives | Open in COM topic 4; architecture leans to **Veda resolves roles** (`targets: [{kind: project_role}]` → AudienceResolver at ingestion, owner fallback) | **Orchestrator picks the users**; suggestion names users **and** applicable role; owner fallback with role kept | ⚠️ both supported by `targets` (`user` kind) — but `role` must be carried separately for display/fallback |
| Several holders of a role | One suggestion, multiple assignees, first apply wins (OQ #23, agreed on Uinno call) | Same | ✅ |
| Assignee apply rights | Assignee applies at any level except `change_stage` (needs 400) — OQ #24 | Same | ✅ (Saar still to confirm) |
| Team changes | v1 freezes audience at ingestion; delete trigger removes leaver, empty audience → owner. Role-following targets = future | On `project.team.changed`, AI re-checks pending suggestions: update recipients **or** retire-and-replace atomically; never two live copies | ❌ needs an "update recipients" or atomic "retire+replace" API in Veda |
| Catalog / naming | One catalog (`GET /internal/orchestration/catalog`), lowercase immutable keys, `<domain>.<entity>.<event>`, snake_case reasons, unknown key rejected | Same, **plus status values** (suggestion, outcome, methodology, health) in catalog, catalog version/hash | ⚠️ add statuses + version/hash |
| Versioning | Catalog changes additive; rename/remove needs migration + AI agreement. Public API has **no `/api/v1` prefix** | Version on every event type, methodology schema, activity list, catalog, API (path or header); majors served side by side until retirement date | ⚠️ ISS convention has no path version → use header? |
| Triggers vs text | Policy = trigger and/or description; orchestrator interprets text (OQ #7 proposes separate `instructions`) | Explicit trigger decides *when*, text decides *whether/what*; text-only policies checked only against Dec triggers; conflict → configured trigger wins, flag admin | ✅ |
| Stage moves | `change_stage` suggestion, project admin applies; AI never writes | Same; targets owner + admins; AI builds stage-advance once approved | ✅ |
| Activity "done" | Activity tracking = future; applied suggestions get deleted by `cleanup_suggestions` past `expires_at` | Dec: done = suggestion applied **and** action succeeded (from outcome events) | ⚠️ depends on outcome events; AI must persist its own record since suggestions are deleted |
| Autonomy | Future phase (`orchestrator_autonomy` tenant setting, internal PUT endpoints) | Per-activity setting with policy default (always approve / may act / approve below threshold). Dec = all suggestions | ✅ for Dec |
| Auth | `service_credentials` table (SHA-256 key hash, scopes, allowed_tenants), header **`X-Service-Key`** per environment | Veda **KMS** + credentials API → **short-lived scoped tokens**; bootstrap via **cloud workload identity (AWS IAM role)**; no static secrets | ❌ COM design superseded by meeting agreement; redesign needed |
| Tracing | `X-Request-Id` logged | Same | ✅ |
| Document upload/extraction | v1 stores only; extraction = OQ #14, AI team listed as extractor in Overview | Veda should own conversion (upload → same JSON); if AI Labs builds it → separate scope, result = proposal | ❌ ownership flipped vs COM Overview; owner Artem to decide |
| Test data | — | Synthetic only now; live after written approvals; never in AI Labs repos/CI | n/a (new) |
| Quota | Orchestrator suggestions are unmetered (ISS ingestion doesn't increment usage) | — | ⚠️ unaddressed |

## Open items to close at the joint working session (from AI Labs p. 11)
Dec triggers + delivery (both) · one event layer (both) · interim methodology file format+date (Veda Accelerate) ·
revised suggestion item/endpoint with several target users (Artem; AI Labs reviews) · context endpoint with team
roles + methodology (Artem) · credentials API + trusted workload identity (Veda Accelerate) · autonomy setting +
suggestion-vs-action definitions (Product and architecture) · versioning rules (both) · test data: Monday call
outcome (David) · who converts uploaded documents, #14 (Artem).
