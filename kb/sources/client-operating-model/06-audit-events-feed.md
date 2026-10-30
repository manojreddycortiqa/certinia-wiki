# COM · Audit, event catalog and feed semantics

> Source: `docs/MOON-2389 Client Operating Model.docx.pdf` pp. 26–28 · Source ID `com`

> **Possibly in scope.** This section needs refinement and may not be built in the first version. The stories
> (MOON-2393, MOON-2394) ask for audit history, so leaving it out needs Product's agreement.

Every write RPC appends to `operating_model_audit_trail` **in the same transaction**. That one table is the
audit log required by MOON-2389 **and** the outbox behind the AI event feed.

## Why not `tenant_audit_trail` (p. 26)
- Its trigger (`private.log_tenant_audit_trail`) returns early unless `auth.role() = 'authenticated'`. ISS writes with the service-role client, so nothing would be logged.
- It's off unless the tenant enables `audit_logging_enabled`.
- The feed view prunes rows after 30–180 days.

## How rows are written (p. 27)
- One SQL helper: `private.log_operating_model_audit(p_tenant, p_actor_type, p_actor_id, p_entity_type, p_entity_id, p_action, p_project, p_before, p_after, p_context)`.
- Every RPC takes `p_actor_type` and `p_actor_id` explicitly (`auth.uid()` is null under service role).
- `before`/`after` hold only changed fields; inserts and deletes hold the whole row.
- `context` carries `request_id`, `source` (channel: ui / internal_api / migration; *who* acted is actor_type), and related ids (methodology_id, policy_id, suggestion_id).
- `project.project_owner` is still written directly by the frontend. A new `AFTER UPDATE OF project_owner` trigger writes `project.owner.changed` (actor = last_modified_by) so owner changes reach the feed.

## Naming (p. 27)
Event, suggestion source and scope keys: `<domain>.<entity>.<event in past tense>` — as ISS already does
(`callpilot.call.ended`, `project.health.status_changed`, `ticketing.ticket.user_mentioned`). Project-level
entities use `project.`; the org library (roles, policies, methodologies) uses `operating_model.`. A policy
trigger key is the event key where one exists, e.g. `project.methodology.stage_changed`.

**Error codes** follow the module path: `operating_model.<submodule>.<code>` (e.g.
`operating_model.methodology.in_use`, `operating_model.team_role.not_found`,
`operating_model.project_methodology.not_assignable`). Each submodule has its own `error_codes.py`.

## Event catalog (pp. 27–28)
Event = entity type + "." + action.

| Entity type | Actions | In AI feed |
|---|---|---|
| `operating_model.team_role` | created, renamed, reordered, deleted | Yes |
| `project.team` | changed (members added, removed, access level or roles changed) | Yes |
| `project.owner` | changed | Yes |
| `operating_model.policy` | created, updated (with revision), archived, restored, deleted | Yes |
| `operating_model.methodology` | created, settings_updated, structure_saved, archived, restored, deleted | Only archived and deleted; drafts never reach runtime |
| `operating_model.methodology_version` | published | Yes |
| `operating_model.methodology_document` | uploaded | Yes; starts extraction |
| `project.methodology` | assigned, replaced, version_upgraded, removed, stage_changed. A stage change made by applying a suggestion carries `suggestion_id` in its context. | Yes |
| `project.health` | status_changed, mirrored by a trigger on `project_health_webhook_events` | Yes. One feed for the orchestrator instead of two |

> Not in this catalog but requested by AI Labs: suggestion outcome events (applied / dismissed / expired /
> action succeeded / failed), `callpilot.call.ended` in the feed, `schedule.daily_check`. See
> `topics/ai-integration-contract.md`.

## Feed semantics (p. 28)
- **Ordering and cursor:** ordered by `(txid, seq)`; only returns rows whose `txid < pg_snapshot_xmin(pg_current_snapshot())`.
  - Every transaction below that horizon has finished, so no row can appear later behind the cursor, however long a transaction runs.
  - Cursor = last `(txid, seq)`, encoded as an opaque string.
- **Filtering:** by the key's `allowed_tenants`; leaves out confidential projects unless decided otherwise.
- **Delivery:** at-least-once; consumers must be idempotent on `seq`.
- **Retention:** no pruning. Expected volume: a few hundred rows per tenant per day.

## Where people see history (p. 28)
- Project, methodology, policy: **no history view or endpoint in the first version** (no story/Figma shows it; stories only require recording). A history view reads the same table later (Future phase).
- Org Audit Logs page (`tenant-audit.service.ts`) reads `tenant_audit_trail_feed`. Showing these events there needs a UNION in that view; decided later.
