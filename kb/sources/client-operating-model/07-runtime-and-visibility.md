# COM · Project runtime (current stage) and the Visibility standard

> Source: `docs/MOON-2389 Client Operating Model.docx.pdf` pp. 28–30 · Source ID `com`

## Project runtime: current stage (pp. 28–29)
> **Possibly in scope.** Needs refinement; may not be built in v1. No story asks for it: MOON-2389 needs no
> visual stage tracker in the first release (`base.md:61`), and MOON-2393 excludes stage progress in the
> project workspace (`:387`). Only the Figma stage card shows it.

A project with a methodology keeps one piece of runtime state: its **current stage**. It drives the Overview
stage card ("Stage 2/5 · Discovery and Scope"). Activity tracking, the "Medium adherence" label, deviations
and manual marking are future phase.

- Assigning a methodology sets `current_stage_id` to the first stage.
- A person changes it from the stage card's edit button with `PUT …/methodology/stage`.
- The orchestrator does **not** move stages by default. It creates a `project.methodology.change_stage` suggestion with evidence (e.g. the call where scope sign-off was agreed). Applying runs the same RPC a person uses, so only a project admin (400+) or tenant admin can apply it.
- The card shows the stage name only. Figma adds the next open activity after a colon ("Gap analysis"); that needs activity tracking (future).
- A project with no methodology keeps showing the **Certinia stage card**, as today. When both exist, which card shows is an open question (#19).

## Visibility standard (pp. 29–30)
Suggestions, feed items and subscriber events already share one pattern for who sees what, but it was never
written down, and suggestions use only half of it. Every user-facing row follows these rules from now on,
starting with MOON-2389.

| Concept | Columns | Meaning | Enforced by |
|---|---|---|---|
| Target | `target_type`, `target_id` | Who may see the row | RLS only |
| Scopes | `*_scopes(entity_type, entity_id)` | Where it shows (list filters) | Nothing; never a permission |
| Subject (feed only) | `subject_type`, `subject_id` | What it is about | Read-time resolution |

### Rules
1. **Only the target decides who sees a row.** A feature never adds its own visibility table or RLS clause.
2. **Three target types:** `project` (everyone with access, as today), `user` (one person; feed mentions already use it), and the new **`audience`** (a stored list of people inside one project).
3. A row derived from another row **copies its target**. The suggestion's feed item takes the suggestion's target_type/target_id; `SuggestionCreatedActivity` stops hardcoding `project`.
4. Producers state an **intent**, and one ISS **`AudienceResolver`** turns it into a target. Intent = `project`, `user_ids`, `role_ids` or a mix. Roles resolve to the people holding them **at that moment**. An intent resolving to nobody falls back to the **project owner**.
5. **Seeing and acting are separate checks.** The target controls only who sees; each module decides who may act. For suggestions, an assignee may apply at any access level (proposed, OQ #24) and anyone else needs Editor; a type changing protected project state sets its own minimum (`change_stage` needs project admin).

### Audience tables
- `audiences(id, tenant, project, created_at)`: one audience per row in v1, never shared between rows.
- `audience_members(audience, user_id, via_role_id)`: `via_role_id` records why a person is included ("assigned as BA"); null = named directly. A person is in an audience once; if they hold several targeted roles, `via_role_id` is the first in the order the orchestrator listed them in `targets`.
- A trigger on `project_assignment` delete removes that user's memberships in the project's audiences. If that empties an audience, its rows move to the project owner.

### RLS
Audience branch is a plain SQL policy on `suggestions` and `feed_items`, **not** a new case in
`check_entity_access` (plpgsql, runs per row; this subquery runs once per query as a hashed set):
```sql
CREATE POLICY "Read access via audience" ON public.suggestions FOR SELECT USING (
  target_type = 'audience'
  AND target_id::uuid IN (
    SELECT audience FROM public.audience_members WHERE user_id = (SELECT auth.uid())
  )
);
```
- Policies are permissive and OR together; `check_entity_access` returns false for audience. Project/user-targeted rows cost the same as today.
- Membership is the only check. The removal trigger keeps it in line with project access.

### Cleanup
- `target_id` is polymorphic text, so no FK can delete an audience when its rows go.
- A daily step next to `cleanup_suggestions` and `cleanup_expired_feed_items` in **workflow-service** deletes audiences older than one day that no suggestion, feed item or subscriber event targets. Members cascade.
- `suggestions`, `feed_items`, `subscriber_events` each get a partial index `(target_id) WHERE target_type = 'audience'`.
- An audience lives as long as anything points to it, including applied/dismissed suggestions, so history stays visible to its assignees.

### Code changes
- `SuggestionTargetType` and `FeedTargetType` gain `audience`.
- New `AudienceResolver` in ISS, used by suggestion ingestion.
- `SuggestionCreatedActivity` copies the suggestion's target.
- Existing rows don't change; project and user targets stay valid.

Later steps → `13-future-phase.md`.
