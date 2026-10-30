# Glossary and disambiguation

> Terms across all sources. Detailed definitions: `sources/client-operating-model/01-architecture-decisions.md`.

## Domain terms
| Term | Meaning | Table |
|---|---|---|
| **MOON-2389** | Epic/ticket for the Client Operating Model feature (stories MOON-2389 → MOON-2394) | — |
| **Client Operating Model** | Feature letting a client define roles, policies and methodologies so the AI suggests the right next step to the right person | — |
| **Methodology** | Org-owned way of running a project, as ordered stages; type one_time or recurring | `client_methodologies` |
| **Methodology version** | Immutable published snapshot; projects pin one | `client_methodology_versions` |
| **Stage** (methodology stage) | Ordered step in a methodology. Formerly **Gate** | `client_methodology_stages` |
| **Activity** | One piece of expected work: type, description, roles, optional agent, prompt, required flag. Belongs to exactly one policy **or** one stage. Formerly **Action** | `client_activities` |
| **Policy** | Reusable rule: name, description and/or trigger (+ reason, params), plus own activities; standalone or attached to stages | `client_policies` |
| **Trigger / reason / params** | Event kind a policy reacts to (decides *when* to look) / optional sub-condition (e.g. `low_health_score`) / parameter values (e.g. threshold) | columns on `client_policies` |
| **Instructions** | Proposed separate free-text field the orchestrator follows (OQ #7); AI Labs treats as untrusted input | proposed column |
| **Project Team Role** | Functional role on a project (PM, BA…). **Not an access level** | `project_team_roles` |
| **Access level** | Viewer 100 / Contributor 200 / Editor 300 / Administrator 400 | `project_assignment` |
| **Current stage** | Project's position in its pinned version | `project_methodology` |
| **Suggestion** | Proposed action shown to a person who applies or dismisses it | `suggestions` |
| **Autonomous action** | Action executed without human approval — not in v1/December | — |
| **Audience** | Stored list of people inside one project; a suggestion's assignees | `audiences`, `audience_members` |
| **AudienceResolver** | ISS component turning an intent (project / user_ids / role_ids) into a target | — |
| **Orchestrator** | AI team's service: detects triggers, interprets policies, writes suggestions | — |
| **Event feed / outbox** | Append-only `operating_model_audit_trail`, read with a `(txid, seq)` cursor | `operating_model_audit_trail` |
| **Deviation / adherence / activity tracking** | Future-phase concepts (skip reason, compliance score, per-activity state) | future tables |
| **Suggestion Sets** | Epic concept of methodology-linked suggestion bundles; future/hidden | — |
| **Interim methodology file** | JSON file per methodology in the final snapshot shape, shared by Veda Accelerate before the endpoint exists | — |

## Words that mean several things
- **Stage** — (1) methodology stage (new); (2) `project.project_stage` enum Pre-Sale/Delivering/Inactive shown as "Status"; (3) **Certinia stage** from Salesforce ("7/8 Negotiation/Review"). Always say "methodology stage". No sync between methodology and Certinia stage.
- **Role** — Project Team Role vs "Access Roles" (`subscriber_role_hierarchy`, `users.role`) vs "Profiles" (`subscriber_user_profiles`).
- **Policy** — client policy vs `llm_policies*` (LiteLLM guardrails) vs `auth_ip_policy`.
- **Methodology** — client methodology vs `collection_methodology` enum (sprint_based/continuous) on ticketing boards.
- **Agent** — Veda agents = `query_form` rows (e.g. Emily, Cosmo); `relay_agents` = suggestion prompt profiles; "Quality agent" emits health events.
- **Action** — reserved by the wider orchestration project; not used for activities.

## Systems and services
| Name | What it is |
|---|---|
| **Veda** | The product (Project IQ, org settings, suggestions) |
| **ISS / integration-sync-service / Integration Sync** | Python backend (supabase-py, no Python transactions) that owns all new writes, public + internal APIs |
| **suggestion-service** | Generates call suggestions (unchanged) |
| **workflow-service / WorkflowService** | Celery-based workflows: call suggestion pipeline, cleanups (`cleanup_suggestions`, audience cleanup) |
| **CallPilot** | Call capture; emits `callpilot.call.ended` |
| **pathfinder-service** | `/textextract` document text extraction |
| **Supabase Postgres** | Shared DB (prod Postgres 15.8), RLS, RPCs |
| **Frontend** | Angular (NGXS, Jest, Playwright) |
| **Project IQ** | Project workspace UI (Overview stage card, "For you" suggestions) |
| **Agents service** | Agents used by activities |
| **KMS** | Veda's key management, to issue scoped service credentials (AI Labs ask) |
| **Arthur** | Named as the destination for "scoring" of fields (AI Labs test-data section); exact nature not stated |
