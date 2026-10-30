# COM · Public API catalog

> Source: `docs/MOON-2389 Client Operating Model.docx.pdf` pp. 17–25 · Source ID `com`

All endpoints are new routers in `integration-sync-service` and follow its conventions:
- no `/api/v1` prefix; kebab-case paths
- `page` / `per_page` pagination and `sort=-field`
- errors as `{detail, code, meta, request_id}`
- PATCH bodies use `Unset`
- every route documented in `postman/collections/`

Module layout follows `src/modules/ticketing/collection_template/` (router, schemas, models, repository,
service, error_codes). All new code lives in `src/modules/operating_model/` with submodules `team_role`,
`policy`, `activity`, `methodology`, `project_methodology`, `orchestration` (p. 27).

## Methodology tree format (pp. 17–18)
A stage holds one ordered list, `items`. Every item has `id` and `kind`; other fields depend on kind. Reads
and writes use the same envelope, so a new kind later (checklist, milestone, nested policy) is one new
variant. Today: two kinds, `activity` and `policy`.

**Write shape** (used by `PUT …/structure` and by policy create/update):
```ts
type StageItemInput = ActivityItemInput | PolicyItemInput

type ActivityItemInput = {
  kind: "activity"
  id: string          // client-generated UUID, permanent
  name: string
  type: string        // activity type catalog key
  description?: string
  role_ids: string[]
  agent_id?: string
  prompt?: string
  is_required: boolean
}

type PolicyItemInput = {
  kind: "policy"
  id: string          // client-generated UUID of the stage-policy link
  policy_id: string   // the shared policy; its content is not edited here
}
```

**Read shape** (returned by `GET …/{id}`, `GET …/versions/{version_id}` and the internal context API):
```ts
type StageItem = ActivityItem | PolicyItem

type ActivityItem = Omit<ActivityItemInput, "role_ids" | "agent_id"> & {
  roles: { id: string; name: string }[]
  agent: { id: string; name: string } | null
}

type PolicyItem = {
  kind: "policy"
  id: string
  policy_id: string
  revision: number
  name: string
  description: string | null
  trigger: { type: string; reason: string | null; params: object } | null
  status: "active" | "archived"
  items: ActivityItem[]   // read-only inside a methodology
}
```
- Order = array order. RPC writes `position` from the index: one sequence per stage across direct activities and policy links; one per policy for its own items.
- Discriminator: `kind`, Pydantic discriminated union (`Field(discriminator="kind")`) in ISS, TS union in frontend. Unknown kind → `422 operating_model.methodology.unknown_item_kind`.
- A policy can be linked once per stage; second link → `422 operating_model.methodology.duplicate_policy`. A policy item carries its own items, so the editor draws a policy with the same code as a stage. Policy create/update take items with `kind: "activity"` only.
- Ids follow the client-generated id rule (see 03-methodology-lifecycle).

## Project Team Roles — module `project_team_role` (pp. 18–20)

| Method and path | Guard | Behavior |
|---|---|---|
| `GET /project-team-roles` | AuthenticatedUser | Ordered list `{id, name, position, is_default}`. |
| `POST /project-team-roles` | RequireTenantAdmin | `{name}`. 409 `operating_model.team_role.name_taken`. |
| `PATCH /project-team-roles/{role_id}` | RequireTenantAdmin | Rename. |
| `PUT /project-team-roles/order` | RequireTenantAdmin | `{role_ids[]}`, full ordered list. 422 if any role missing. *(Note: decided OQ #1 says no manual reorder in UI.)* |
| `GET /project-team-roles/{role_id}/usage` | RequireTenantAdmin | `{assignment_count, project_count, activity_count}` for the delete warning. |
| `DELETE /project-team-roles/{role_id}` | RequireTenantAdmin | One RPC deletes the role, its assignments and activity links. Frontend shows usage counts in a confirm modal first; API doesn't ask again. |
| `GET /projects/{project_id}/team` | ViewerProjectSummary | People with an active assignment, each with access level, `granted_via_hierarchy` and roles. Owner appears only with an assignment row. Optional `?role_id=` (CSV) keeps members holding any of those roles (covers MOON-2390 "active project members assigned to a specified role"). Active = active assignment + active user; agent rows never returned. 422 `operating_model.team_role.not_found` for a role outside the tenant; a valid role nobody holds → empty list. One repository method `find_members(project_id, role_ids=None)` also backs the internal members endpoint and assignee routing. |
| `PUT /projects/{project_id}/team` | AdministratorProjectSummary | `{members: [{user_id, access_level, role_ids[]}]}` = full list of people. Calls `save_project_team` with the caller's JWT: adds, updates, removes assignments and sets roles in one transaction. 422 `operating_model.team_role.not_found`; DB guard errors (escalation, confidential, limits) → 403 or 422 with their message. |

**Team save RPC** `save_project_team(p_project uuid, p_members jsonb)` (p. 20): `SECURITY INVOKER`; ISS calls it
through `user.supabase` (caller's JWT), **never the service-role client**, so all existing `project_assignment`
RLS and triggers still apply (check_user_permissions and shares, guard_assignment_escalation, confidential
guards, created_by_id/last_modified_by, user tags, hierarchy shares, sync webhook).
1. Lock the project's people assignments (`FOR UPDATE`).
2. Diff against `p_members`: insert new, update changed access levels, delete missing. Agent rows and `granted_via_hierarchy` rows left alone.
3. Replace each member's rows in `project_assignment_team_roles`.
4. Write one `project.team.changed` event with before/after member lists.
The owner is treated like anyone else: gets an assignment row only if the payload lists them.

## Client Policies — module `client_policy` (pp. 20–22)

| Method and path | Guard | Behavior |
|---|---|---|
| `GET /client-policies` | AuthenticatedUser | Filters: `search` (name+description), `status`, `usage=standalone\|in_methodology`, `trigger_type`. Paged (`page`, `per_page` default 10 max 100) → `{items, page, per_page, total, total_pages}`, ordered by name then id. Item: `{id, name, description, trigger, status, updated_at}`; `trigger` is `{type, reason, params}` or null. |
| `GET /client-policies/recent?limit=3` | AuthenticatedUser | "Recently used" in the Add Policy modal, ordered by last time attached to a stage. |
| `POST /client-policies` | RequireTenantAdmin | `{name, description?, trigger?: {type, reason?, params?} \| null, items: ActivityItemInput[]}`. Created atomically by an RPC (also writes revision 1). ISS maps trigger → trigger_type/reason/params columns; null clears all three. `params` defaults `{}`, validated against the reason's param model; mismatch → 422 `operating_model.policy.invalid_trigger_params` with field path (e.g. `trigger.params.value`). |
| `GET /client-policies/{policy_id}` | AuthenticatedUser | Policy with activities, revision and `used_in: [{methodology: {id, name}, stages: [{id, name}], published}]` (empty when standalone). `published` true when any published version references it; an entry can have `stages: []` after the draft dropped it. Drawer's "Used in N methodologies" = length of used_in. |
| `PUT /client-policies/{policy_id}` | RequireTenantAdmin | Full replace (same body as POST) plus `expected_revision`. 409 `operating_model.policy.revision_conflict`. |
| `POST /client-policies/{policy_id}/archive` and `/restore` | RequireTenantAdmin | Archive allowed while in use; publishing a methodology that references it is then blocked. |
| `DELETE /client-policies/{policy_id}` | RequireTenantAdmin | 409 `operating_model.policy.in_use` when any stage or published version references it, with `used_in` in `meta`. |
| `GET /operating-model/catalog` | AuthenticatedUser | Keys defined in ISS code: `{trigger_types: [{key, label, reasons: [{key, label, params_schema}]}], activity_types: [{key, label, suggestion_type}]}`. `params_schema` = JSON Schema of the reason's trigger_params (no-param reason → object schema with no properties). `suggestion_type` = type the activity maps to. Same for every tenant, changes only on deploy → cacheable (ETag). |

## Client Methodologies — module `client_methodology` (pp. 22–23)

| Method and path | Guard | Behavior |
|---|---|---|
| `GET /client-methodologies` | AuthenticatedUser | Filters: `search`, `status`, `type`, `published` (true = only those with a published version; Project Settings select calls `?status=active&published=true&search=`). Paged like policies, ordered by name then id. Item: `{id, name, type, status, stage_names[], current_version, has_unpublished_changes, updated_at}`. `current_version` = `{id, version_number, published_at}` of latest published, or null. Both feed the status badge (OQ #9). |
| `POST /client-methodologies` | RequireTenantAdmin | `{name, type}`. Creates a draft. |
| `PUT /client-methodologies/{id}/document` | RequireTenantAdmin | Multipart file. Attaches a document; later upload replaces it. Creating from a document = POST then this. See 09-document-upload. |
| `GET /client-methodologies/{id}` | AuthenticatedUser | Methodology, revision, draft tree. Attached policies expanded read-only. |
| `PATCH /client-methodologies/{id}` | RequireTenantAdmin | `{name?, type?}` from Settings modal. Bumps revision. |
| `PUT /client-methodologies/{id}/structure` | RequireTenantAdmin | `{expected_revision, stages: [{id, name, description, items: StageItemInput[]}]}`. Returns `{revision, stages}` in read shape. |
| `POST /client-methodologies/{id}/publish` | RequireTenantAdmin | `{expected_revision, change_note?}`. Returns the version. |
| `GET /client-methodologies/{id}/versions` and `/versions/{version_id}` | AuthenticatedUser | Version list (paginated) or one snapshot. |
| `POST /client-methodologies/{id}/archive`, `/restore` | RequireTenantAdmin | Archive removes from project selection; pinned projects keep their version. Restore makes it selectable again. **No Duplicate**: a new version of the same methodology is the way to change it. |
| `DELETE /client-methodologies/{id}` | RequireTenantAdmin | 409 `operating_model.methodology.in_use` once published. Use Archive. |
| `GET /client-methodologies/{id}/document` | AuthenticatedUser | 307 redirect to a signed URL. |

## Project runtime — module `project_methodology` (pp. 24–25)

| Method and path | Guard | Behavior |
|---|---|---|
| `GET /projects/{project_id}/methodology` | ViewerProjectSummary | `{methodology {id, name, type}, version {id, version_number, published_at}, upgrade_available {id, version_number} \| null, current_stage {id, name, position, total, set_at, set_by {id, name}} \| null, assigned_at, assigned_by {id, name}, revision}`. Body is null (200) when no methodology. `upgrade_available` set only when a newer published version exists (drives "Upgrade" notice). `revision` sent back on both PUTs. Not embedded in `GET /projects/{project_id}` (stays thin ProjectSummary). |
| `PUT /projects/{project_id}/methodology` | AdministratorProjectSummary | `{methodology_id, version_id?, revision?}`; default = current version; `revision` required once project has a methodology. One endpoint covers assign, replace, upgrade. 422 `operating_model.project_methodology.not_assignable` when methodology not active or has no published version. |
| `DELETE /projects/{project_id}/methodology` | AdministratorProjectSummary | Removes the association. History and versions remain. |
| `PUT /projects/{project_id}/methodology/stage` | AdministratorProjectSummary | `{stage_id, note?, revision}`. Any stage in the pinned version, forward or back. Nothing checks earlier stages' activities (that comes with activity tracking — Future phase). |
