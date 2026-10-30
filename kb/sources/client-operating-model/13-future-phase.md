# COM · Future phase (out of the first version)

> Source: `docs/MOON-2389 Client Operating Model.docx.pdf` pp. 58–65 · Source ID `com`

Everything here is out of v1: stories exclude it or no story asks for it. Designs kept so the work isn't lost.
v1 may keep the current stage and the stage card in Project IQ (OQ #19, #20, #29), and keeps the internal API for
reading context and writing suggestions.

## Feature list and why it waits (pp. 58–59)

| Feature | Why it waits |
|---|---|
| Deviations and deviation reasons | MOON-2391, MOON-2393 exclude "deviation detection" (`base.md:386, :621`) |
| Stage-advance check (409 on incomplete required activities) | Only makes sense with deviations; in v1 a stage moves freely |
| Adherence score, level, snapshots | Excluded with "adherence tracking" (`:386, :621`); epic starts with data capture only (`:186`) |
| Activity tracking (`project_methodology_activity_states`) | No story; stories exclude rendering activity progress (`base.md:387`). Only v1 reader would be the orchestrator — question for AI team |
| Manual activity marking (activities drawer, `complete_activity` suggestion) | No story, no Figma; builds on activity tracking |
| Orchestrator autonomy (direct stage and activity-state writes) | Initial release is human-in-the-loop (`:141`) |
| AI-proposed changes to methodologies and policies | Epic lists approval workflow as future (`:165`) |
| Methodology extraction from documents | Out of scope for MOON-2392 (`:485`); OQ #14 |
| Engage with Agent | No story; OQ #16 |
| Suggestion Sets | Excluded by every story (`:310, :382–384, :489, :622, :792`) |
| History view (project, methodology, policy) | Stories only require recording. Later: cursor-paginated `GET /projects/{project_id}/methodology/history` + History panels reading `operating_model_audit_trail` |
| Agent prompt suggestion (`agent.run_prompt`) | No story |
| Visibility standard, later steps | No MOON-2389 story needs them; they touch shared ticketing/callpilot code |

## Deviations (pp. 59–60)
Records why a required activity was skipped. Fields from the Method Deviation modal: reason (required), notes (optional), document (required).

| Table | Columns | Constraints |
|---|---|---|
| `project_methodology_deviations` | project, version_id, stage_id, activity_id, reason_id → client_deviation_reasons, notes, document_path, document_filename, document_size, created_at, created_by | Index (project, created_at desc). Append-only; a correction is a new deviation. |
| `client_deviation_reasons` | name, name_key, position, is_active | UNIQUE (tenant, name_key). Org-managed; seeded with defaults like "Client refused scope". |

| Method and path | Guard | Behavior |
|---|---|---|
| `POST /projects/{project_id}/methodology/deviations` | EditorProjectSummary | Multipart activity_id, reason_id, notes, file (required). Marks activity skipped. |
| `GET /projects/{project_id}/methodology/deviations` | ViewerProjectSummary | Deviations with signed document links. |
| `GET, POST, PATCH, DELETE /deviation-reasons`, `PUT …/order` | Read: AuthenticatedUser; Write: RequireTenantAdmin | Org-managed reason list. |

- Document uploaded first to `{tenant}/projects/{project}/deviations/{upload_uuid}/{filename}` in `operating-model` bucket (25 MB, same content checks); then RPC inserts; on failure the file is deleted.
- Every deviation writes `project.deviation.recorded` (`{activity_id, reason_id}`) — orchestrator can use as a risk signal.
- Permissions: Editor (300+) records deviations; tenant admins manage reasons.
- Frontend: Method Deviation modal (Reason*, Notes, Document*) and a deviation-reasons admin section on the Policies page.

## Stage-advance check (p. 60)
1. Backward or same stage: always allowed.
2. Forward: RPC collects required activities in every stage passed (current up to, not including, target) whose state isn't completed / skipped / not_applicable.
3. If non-empty, `PUT …/methodology/stage` → 409 `operating_model.project_methodology.required_activities_incomplete` with `meta.activities[]` (stage name, activity name, activity id).
4. Frontend opens Method Deviation modal once per listed activity; each Confirm sends `POST …/methodology/deviations` (marks skipped).
5. Frontend retries the stage change, which succeeds.
With autonomy on and the orchestrator moving the stage directly, the move is allowed; missing required activities count as overdue; only a person can write a deviation reason.

## Adherence (p. 60)
Figma Project IQ shows "Medium adherence" next to the stage; hidden in v1.
- Due = required activities in stages before the current one, per (stage, activity). Done = due & completed. Justified = due & skipped with deviation.
- **Score = (done + justified) / due × 100**; no due ⇒ no score.
- **Level:** High ≥ 85, Medium 60–84, Low < 60 (placeholders for Product).
- Deviations count as justified but are reported separately.
- `get_project_methodology_adherence(p_project)` computes from pinned snapshot + state rows. RPCs changing stage / activity state / deviation recompute and store `adherence_score numeric(5,2)` and `adherence_level` on `project_methodology`. Level change writes `project.methodology.adherence_level_changed` (`{from_level, to_level, score}`).
- Daily workflow-service beat job `snapshot_project_methodology_adherence()` fills `project_methodology_adherence_snapshots` (project, snapshot_date, version_id, stage_id, required_due, required_done, required_justified, score, level; PK (project, snapshot_date)).
- API: `GET /projects/{project_id}/methodology/adherence` (ViewerProjectSummary) → current score + daily trend; methodology summary gains `adherence {score, level}`. Stage card shows a level dot, score in tooltip.

## Activity tracking (p. 61)
Records per project which methodology activities are done. Deviations, adherence, manual marking, autonomy and
the "next activity" text on the stage card all build on it.
**Why a table, not applied suggestions:** applied suggestions don't last — `cleanup_suggestions` in workflow-service
deletes every suggestion past `expires_at` (applied included), and deleting a project or regenerating a call removes
them too. A durable record needs its own table.

`project_methodology_activity_states`:

| Column | Notes |
|---|---|
| project | → project CASCADE |
| stage_id, activity_id | Ids from the pinned snapshot; stable across versions ⇒ states carry over on upgrade |
| status | pending / completed at first; in_progress, skipped, not_applicable come with manual marking and deviations |
| changed_at, changed_by | Who and when |
| suggestion_id | → suggestions SET NULL; suggestion whose apply completed it |

PK (project, stage_id, activity_id). `actor_type` and `evidence jsonb` added with writers that need them.
- **Fill:** SECURITY DEFINER trigger `AFTER UPDATE OF status ON suggestions WHEN (NEW.status = 'applied')` reads the suggestion's `operating_model.stage` and `operating_model.activity` scopes and upserts `completed` in the same transaction.
- Every change writes `project.activity_state.changed` to the audit trail ⇒ orchestrator can stop suggesting completed activities.
- Context API returns `activity_states: [{stage_id, activity_id, status, changed_at}]`.
- Stage card shows the first not-completed activity of the current stage. Read access: Viewer (100).

## Manual activity marking (p. 62)

| From | To | Who | Evidence |
|---|---|---|---|
| pending | in_progress / completed / not_applicable | Editor (300+), or AI via `project.methodology.complete_activity` suggestion (`{stage_id, activity_id, evidence}`) | Optional note; for AI the source call, ticket or suggestion id |
| pending / in_progress | skipped | Only by recording a deviation | Deviation id |
| any | pending | Editor (300+) | Optional note |

API: `GET /projects/{project_id}/methodology/activities`; `PUT /projects/{project_id}/methodology/stages/{stage_id}/activities/{activity_id}/state` (`{status, evidence?}`, EditorProjectSummary). Frontend: "Methodology activities" drawer from the stage card (no Figma yet).

## Orchestrator autonomy (p. 62)
Tenant setting `orchestrator_autonomy` in `subscriber_org_defaults` (off by default) lets the orchestrator write project state directly.

| Internal endpoint | Scope | Behavior |
|---|---|---|
| `PUT /internal/orchestration/projects/{project_id}/stage` | orchestration:write | `{stage_id, evidence: {source_type, source_id, summary}, confidence}`. Recorded with `actor_type = ai`. Adds `current_stage_source` (user / ai, default user) to `project_methodology`. |
| `PUT /internal/orchestration/projects/{project_id}/stages/{stage_id}/activities/{activity_id}/state` | orchestration:write | `{status: in_progress \| completed \| not_applicable, evidence}`. `skipped` reserved for human deviations. |

Errors: 403 `operating_model.orchestration.autonomy_disabled`; 409 `operating_model.project_methodology.not_assigned`; 422 `operating_model.project_methodology.stage_not_in_version`. Idempotency: same target state = no-op; optional `Idempotency-Key` remembered 24 h.

## AI-proposed changes to methodologies and policies (p. 63)
Epic: "AI-derived methodology or policy refinements must be proposed for client approval before becoming active" (`base.md:136, :178`).
- Producers: document extraction, "Engage with Agent" chat, later transcript-learned refinements.
- Table `operating_model_proposals`: entity_type (methodology / policy), entity_id nullable (null = new policy), base_revision, proposed jsonb, summary, source (`operating_model.document` / `agent.chat` / `callpilot.call`), source_ref jsonb, status (pending / accepted / rejected / superseded), created_by_service, decided_at, decided_by, decision_note.
- Shape: `proposed` = same body as `PUT …/structure` or `PUT /client-policies/{id}`.
- API: internal `POST /internal/orchestration/proposals` (proposals:write); public `GET /client-methodologies/{id}/proposals`, `POST /operating-model-proposals/{proposal_id}/accept` and `/reject` (RequireTenantAdmin).
- Review: editor banner "AI proposed changes" with canvas diff, Accept/Reject.
- Accept: RPC `accept_operating_model_proposal` via the structure RPC; stale base_revision → 409 `operating_model.proposal.stale` (ask again or "Replace draft"). Extraction is slow, so its proposals are often stale.
- Activation: accepting a methodology proposal changes only the draft (Publish stays a human step). Policies have no draft ⇒ accepting writes a new revision (acceptance = approval).
- New pending proposal supersedes older pending ones. Events: `operating_model.proposal` created / accepted / rejected / superseded.
- Once proposals exist, the orchestrator can suggest a trigger for a trigger-less policy via a policy proposal.

## Methodology extraction from documents (p. 63)
v1: document only stored and announced. Extraction would read stages, activities, roles and policies and return a methodology proposal. `client_methodology_documents.extraction_status` (not_requested / pending / completed / failed), updated by the AI team via an internal endpoint. OQ #14.

## Engage with Agent (pp. 63–64)
Would open `assistant-panel-layout` with a methodology agent; `chat-assistant.directive.ts` assumes a project context and needs an org-level mode. Changes go through proposals. OQ #16.

## Suggestion Sets (p. 64)
Only the epic describes them ("Linked suggestion set or flow", `base.md:48`, also `:145, :160`), applied when a project selects that methodology while PMs keep permitted adjustments (`:124`). Figma has a "Suggestions Sets" tile and a select in Project Settings, no editor screens. Both stay hidden; projects keep per-project `suggestion_settings`.
Earlier draft (starting point only, doesn't match the epic's activity-level idea):
- `suggestion_sets`: name, name_key, description, volume, categories jsonb, enabled_activity_types text[] (empty = all), relay_agent_overrides jsonb, is_default, status.
- `project_suggestion_sets`: project PK, suggestion_set_id RESTRICT, selected_at, selected_by.
- Resolution: selected set → project override row in `suggestion_settings` → org row.
- API: CRUD + archive on `/suggestion-sets`; `PUT /projects/{project_id}/suggestion-set`. Optional `default_suggestion_set_id` on a methodology.

## Visibility standard: later steps (pp. 64–65)

| Step | What changes | Why it waits |
|---|---|---|
| One scope shape | `suggestion_scopes` and `subscriber_event_scopes` get the same PK (owner, entity_type, entity_id); NULL wildcard goes; "shows in every collection" becomes an explicit flag; `_apply_scope_filter` and `count_unseen_suggestions` change | Touches ticketing and callpilot suggestions; no gain for this feature |
| Reuse audiences | Audience keyed by hash of sorted members, unique per project; rows targeting same people share it | Only matters if one audience per row grows tables. Measure first |
| Incremental cleanup | Daily step checks only audiences whose rows were deleted since last run, in batches | Full scan is cheap at today's volume |
| Events use audiences | `subscriber_events` producers state an intent and go through `AudienceResolver` | No event needs a group audience yet |
| Role-based targets | Target follows a role (re-resolved on team change) instead of a list frozen at creation | v1 freezes the list at ingestion, which matches what a suggestion needs |
