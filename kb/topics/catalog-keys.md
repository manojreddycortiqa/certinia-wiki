# Keys, endpoints and error codes — quick lookup

> Collected from all sources. ⚠ None of the catalog lists are final (OQ #5) — final keys follow the December use
> cases (frozen 4 Nov 2026). Source file in brackets.

## Naming rules
- Events / triggers / suggestion types / source & scope keys: `<domain>.<entity>.<event in past tense>`; project-level → `project.`, org library → `operating_model.` [com/06]
- Reasons and status values: `snake_case` [com/12 #5, ai-labs T5]
- Error codes: `operating_model.<submodule>.<code>` [com/06]
- Keys lowercase, never change once used; labels display-only; unknown key → rejected [com/11, ai-labs T5]

## Event types
| Key | Notes | Source |
|---|---|---|
| `operating_model.team_role.{created,renamed,reordered,deleted}` | in AI feed | com/06 |
| `project.team.changed` | before/after member lists | com/04, 06 |
| `project.owner.changed` | DB trigger on `project_owner` | com/06 |
| `operating_model.policy.{created,updated,archived,restored,deleted}` | updated carries revision | com/06 |
| `operating_model.methodology.{created,settings_updated,structure_saved,archived,restored,deleted}` | only archived/deleted reach AI feed | com/06 |
| `operating_model.methodology_version.published` | | com/03, 06 |
| `operating_model.methodology_document.uploaded` | "starts extraction" | com/06, 09 |
| `project.methodology.{assigned,replaced,version_upgraded,removed,stage_changed}` | stage_changed via suggestion carries `suggestion_id` | com/06 |
| `project.health.status_changed` | mirrored from `project_health_webhook_events`; payload from/to status | com/06, ai-labs T1 |
| `callpilot.call.ended` | existing; **not yet in the feed** (Celery task) — AI Labs Dec trigger | ai-labs T1 |
| `schedule.daily_check` | proposed, only if needed; Veda scheduler, Moonnox owns clock | ai-labs T1, T5 |
| `agent.chat.message_sent` | listed as trigger type example | com/11 |
| Suggestion outcomes: `applied`, `dismissed`, `expired`, action `succeeded`/`failed` | **requested by AI Labs; no keys yet** | ai-labs T3 |
| Future: `project.deviation.recorded`, `project.activity_state.changed`, `project.methodology.adherence_level_changed`, `operating_model.proposal.{created,accepted,rejected,superseded}` | future phase | com/13 |

## Trigger reasons (examples only)
`low_health_score`, `health_declining` (for `project.health.status_changed`) [com/11]

## Activity type → suggestion type
| Activity key | Figma label | Suggestion type | Executor |
|---|---|---|---|
| `email` | Email | `messaging.email.send_email` | ISS email |
| `calendar` | Calendar | `scheduling.calendar.create_event` | ISS calendar |
| `slack_teams` | Slack/Teams | `messaging.slack.post_update` / `messaging.teams.post_update` | ISS Slack/Teams (by tenant integration) |
| `pm_tool` | PM Tool/Jira | `project.ticketing.create_ticket` / `project.ticketing.update_ticket` | Native or Jira |
| `certinia_stage` | Certinia suggestion A (guess) | `project.certinia.update_stage` | Salesforce via user's MCP |
| `certinia_raid_create` | Certinia suggestion B (guess) | `project.certinia.create_raid_record` | same |
| `certinia_raid_update` | Certinia suggestion C (guess) | `project.certinia.update_raid_record` | same |
| `insight_content` | Insight/content creation | none in v1 | not suggested |
| `generate_document` | Generate document | none in v1 | not suggested |
| — | (stage move) | `project.methodology.change_stage` `{stage_id, evidence}` | same RPC as a person; needs 400 |
| — | future | `project.methodology.complete_activity`, `agent.run_prompt` | — |

## Other lists
- Target kinds: `project_role`, `user` (later `team`) · Visibility target types: `project`, `user`, `audience` [com/07, 08]
- Source kinds: `operating_model.policy`, `operating_model.stage` · Scope entity types: `operating_model.activity`, `operating_model.stage`, `operating_model.policy` [com/08, 11]
- `SuggestionTriggerType` new values: `orchestrator.methodology`, `orchestrator.policy`, `orchestrator.event` [com/08]
- Methodology types: `one_time`, `recurring` · statuses: `draft`, `active`, `archived` · policy statuses: `active`, `archived` [com/02, 03]
- Audit `actor_type`: `user`, `ai`, `system`, `service` · `context.source`: `ui`, `internal_api`, `migration` [com/02, 06]
- Access levels: Viewer 100, Contributor 200, Editor 300, Administrator 400 [com/01]
- Seed roles: Project Manager, Product Owner, Business Analyst, Solution Architect, Engineer, QA Lead, Delivery Lead, Executive Sponsor [com/02]
- Confidence labels (AI Labs): `low`, `medium`, `high` · ingestion result: `created`, `duplicate`, `rejected` [ai-labs T3]

## Endpoints
**Public (ISS, JWT)** — full detail in `sources/client-operating-model/04-public-api.md`
- `/project-team-roles` (GET, POST), `/{role_id}` (PATCH, DELETE), `/order` (PUT), `/{role_id}/usage` (GET)
- `/projects/{project_id}/team` (GET, PUT)
- `/client-policies` (GET, POST), `/recent`, `/{policy_id}` (GET, PUT, DELETE), `/archive`, `/restore`
- `/operating-model/catalog` (GET)
- `/client-methodologies` (GET, POST), `/{id}` (GET, PATCH, DELETE), `/structure` (PUT), `/publish` (POST), `/versions[/{version_id}]` (GET), `/archive`, `/restore`, `/document` (PUT upload, GET 307)
- `/projects/{project_id}/methodology` (GET, PUT, DELETE), `/stage` (PUT)
- Suggestions: `GET /suggestions?assigned_to_me=true`, `POST /suggestions/:id/apply`; legacy ingestion `POST /suggestions/bulk/create` (shared key)

**Internal (`/internal/orchestration/*`, service credential)** — `sources/client-operating-model/11-ai-team-topics.md`
- `GET /events?after={cursor}` · `GET /projects/{project_id}/context` · `GET /methodology-versions/{version_id}` · `GET /tenants/{tenant}/policies?trigger_type=` · `GET /catalog` · `POST /projects/{project_id}/suggestions`
- Future: `PUT /projects/{id}/stage`, `PUT /projects/{id}/stages/{sid}/activities/{aid}/state`, `POST /proposals`
- AI Labs also needs: a **credentials API** (KMS, short-lived tokens)

**Headers:** `X-Request-Id` (tracing, both sides) · `X-Service-Key` (COM proposal; AI Labs wants short-lived tokens) · legacy `X-API-KEY` (do not reuse) · future `Idempotency-Key` (24 h)

## Error codes
| Code | HTTP | Source |
|---|---|---|
| `operating_model.methodology.invalid_id` | 422 | com/03 |
| `operating_model.methodology.in_use` | 409 | com/03, 04 |
| `operating_model.methodology.revision_conflict` | 409 | com/03 |
| `operating_model.methodology.policy_archived` | — | com/03 |
| `operating_model.methodology.unknown_item_kind` | 422 | com/04 |
| `operating_model.methodology.duplicate_policy` | 422 | com/04 |
| `operating_model.methodology.too_many_stages` | — | com/10 |
| `operating_model.methodology.file_missing` / `file_too_large` / `file_type_unsupported` / `file_type_mismatch` / `file_unreadable` | 422 | com/09 |
| `operating_model.methodology.storage_failed` | 502 | com/09 |
| `operating_model.team_role.name_taken` | 409 | com/04 |
| `operating_model.team_role.not_found` | 422 | com/04 |
| `operating_model.policy.invalid_trigger_params` | 422 | com/04 |
| `operating_model.policy.revision_conflict` | 409 | com/04 |
| `operating_model.policy.in_use` | 409 | com/04 |
| `operating_model.project_methodology.not_assignable` | 422 | com/04 |
| `operating_model.activity.prompt_too_long` / `too_many` / `too_many_roles` | — | com/10 |
| `*.name_too_long`, `*.description_too_long`, `*.revision_conflict` | —/409 | com/10 |
| `suggestion.apply.insufficient_access` | — | com/08 |
| Future: `operating_model.project_methodology.required_activities_incomplete` (409), `.not_assigned` (409), `.stage_not_in_version` (422), `operating_model.orchestration.autonomy_disabled` (403), `operating_model.proposal.stale` (409) | | com/13 |
