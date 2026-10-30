# COM · Permissions

> Source: `docs/MOON-2389 Client Operating Model.docx.pdf` pp. 25–26 · Source ID `com`

Every check reuses an existing guard; **no new permission model** for the first release.
- Org-level writes use `RequireTenantAdmin`, which checks `users.company_admin` (`src/modules/auth/guards.py`).
- Project-level checks use the access-level dependencies in `src/modules/project/deps.py`. Company admins already resolve to level 400 on every project.
- **Project Team Roles never change access.** Role tables are not read by `get_project_user_access_level` or any RLS policy.

## Matrix (pp. 25–26)

| Action | Tenant admin | Project admin (400) | Project editor (300) | Project member (100–200) | AI service |
|---|---|---|---|---|---|
| Read role, policy, methodology and catalog libraries | Yes | Yes | Yes | Yes | Yes (internal API) |
| Create, edit, reorder, delete roles | Yes | No | No | No | No |
| Create, edit, archive, delete policies | Yes | No | No | No | No |
| Create, edit, publish, archive, delete methodologies | Yes | No | No | No | No |
| Select, replace, upgrade, remove the project methodology | Yes | Yes | No | No | No |
| Assign Project Team Roles to members | Yes | Yes | No | No | No |
| Move the current stage | Yes | Yes | No | No | Through `change_stage` suggestions only, applied by a project admin |
| View project methodology and stage | Yes | Yes | Yes | Yes | Yes |
| Set own default project role | Yes | Yes | Yes | Yes | No |
| Create suggestions | No | No | No | No | Yes (internal API) |
| Apply or dismiss a suggestion | Yes | Yes | Yes | Only when assigned (OQ #24) | No |

Access levels: Viewer 100 / Contributor 200 / Editor 300 / Administrator 400.

## Why these levels (p. 26)
- **Team saves need Administrator (400)**, same as today. Adding a member or changing access level already passes `guard_assignment_escalation`, which requires `has_preexisting_access(project, tenant, 400)`: a direct active assignment at 400, the project owner, or a company admin. Roles follow the same bar (MOON-2390: users who can't manage team assignments can't change role assignments). ISS checks `AdministratorProjectSummary` first so an Editor gets a clean 403. Someone reaching 400 only via a share or the role hierarchy passes ISS but is still refused by the trigger, as today; the RPC maps that error and the assignment-limit error to 403 and 422.
- **Methodology selection uses Administrator (400)** because the frontend only opens Project Settings at 400. Existing suggestion settings use the stricter `RequireProjectOwnerOrAdmin` (rejects an assignee at 400); OQ #17 confirmed level 400 for methodology selection.
- **The AI never writes project state directly.** `base.md` asks for human-in-the-loop, so the orchestrator proposes stage moves as `change_stage` suggestions. Direct writes (autonomy) are a future phase.
