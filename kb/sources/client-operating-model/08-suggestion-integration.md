# COM · Suggestion integration

> Source: `docs/MOON-2389 Client Operating Model.docx.pdf` pp. 31–33 · Source ID `com`

Orchestrator suggestions go into the **existing store** in `src/modules/suggestion/`, so listing, apply,
dismiss, prioritization and the feed keep working. **Five changes** are needed.

## What exists today (p. 31)
- `suggestion-service` only generates. ISS stores, lists and applies (`services/manager_service.py`).
- `target_type` is always `project`. Anyone with view access sees a suggestion; applying needs Editor.
- `type` is a closed enum (`enums/base.py`). Each type has a resolver and an executor under `types/`.
- `trigger` jsonb and `suggestion_scopes` (generic entity_type / entity_id) describe where a suggestion came from.
- Ingestion is `POST /suggestions/bulk/create` behind the shared API key.

## 1. Assignees (p. 31)
- Assignees are an **audience** target: `target_type = 'audience'`, each assignee an `audience_members` row.
- One suggestion can have several assignees; **the first one to apply finishes it for everyone** (avoids two people sending the same email).
- Orchestrator sends `targets`: list of `{kind, id}` where kind is `project_role` or `user` today (more, e.g. `team`, later). `AudienceResolver` resolves project roles to users holding them **at ingestion time** and stores `via_role_id`.
- Unresolvable role (nobody holds it) → falls back to **project owner**, `via_role_id` kept so UI can say "No BA assigned".
- **Visibility:** assignees see it; **nobody else sees suggestions that have assignees, project admins included**; suggestions without assignees stay visible to the whole project. `GET /suggestions` gains `assigned_to_me=true`; RLS gains the audience policy; feed item copies the target.
- **Apply:** an assignee may apply/dismiss their own suggestion at any access level, Viewer (100) included; non-assignees still need Editor (300). **Exception:** `project.methodology.change_stage` always needs project admin (400) or tenant admin. Assignee rule = OQ #24.

## 2. Source attribution (pp. 31–32)
- New `suggestion_scopes` entity types: `operating_model.activity`, `operating_model.stage`, `operating_model.policy`. Existing PK (suggestion, entity_type) allows one of each — enough.
- New `SuggestionTriggerType` values: `orchestrator.methodology`, `orchestrator.policy`, `orchestrator.event`.
- `trigger` jsonb gains `methodology_version_id`, `policy_revision` and the event `seq` that caused it.
- `SuggestionSourceInfo` gets resolvers for new sources, so the card shows the "Methodology" badge and "Policy: Low Project Health".

## 3. Deduplication and lifetime (p. 32)
- `RemovePreviousCallSuggestions` in workflow-service must also filter on `trigger->>'type' = 'callpilot.call.ended'`. Otherwise regenerating a call **deletes orchestrator suggestions** carrying the same call scope. Trigger type already records who created it; no new column.
- New column `deduplication_key`, unique per tenant **whatever the status**. A replayed event returns the existing id and never recreates an applied/dismissed suggestion.
- `expires_at` honored as today.
- **Quota:** only workflow-service's call pipeline calls `increment_suggestion_generation_usage` (once per generation run). ISS ingestion never does ⇒ **orchestrator suggestions are unmetered** unless a counter is added.

## 4. Stage move suggestion (p. 32)
`project.methodology.change_stage` with payload `{stage_id, evidence}`. Executor checks the person applying is
project admin (400+) or tenant admin, else returns `suggestion.apply.insufficient_access`; anyone else can still
see and dismiss it. Orchestrator targets it at the project owner and admins. Executor calls the same RPC a person uses.

## 5. Activity type → suggestion type (pp. 32–33)
Figma activity types already match executable types, so most need no new executor. *Insight/content creation*
and *Generate document* match none; not suggested in v1 until Product defines them.

| Activity type (Figma) | Catalog key | Suggestion type | Executed by |
|---|---|---|---|
| Insight/content creation | `insight_content` | None in v1 | Not suggested |
| Email | `email` | `messaging.email.send_email` | ISS email executor |
| Calendar | `calendar` | `scheduling.calendar.create_event` | ISS calendar executor |
| Slack/Teams | `slack_teams` | `messaging.slack.post_update` or `messaging.teams.post_update`, depending on tenant's integration | ISS Slack / Teams executors |
| PM Tool/Jira | `pm_tool` | `project.ticketing.create_ticket` or `update_ticket` | Native or Jira ticketing |
| Generate document | `generate_document` | None in v1 | Not suggested |
| Certinia suggestion A | `certinia_stage` | `project.certinia.update_stage` | Salesforce, through the user's MCP connection |
| Certinia suggestion B | `certinia_raid_create` | `project.certinia.create_raid_record` | Same |
| Certinia suggestion C | `certinia_raid_update` | `project.certinia.update_raid_record` | Same |

**The Certinia rows are a guess** — the Figma type list only says "A / B / C". (AI Labs will confirm with Certinia.)
