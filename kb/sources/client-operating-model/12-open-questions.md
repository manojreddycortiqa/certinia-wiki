# COM · Open questions tracker (as written in the doc)

> Source: `docs/MOON-2389 Client Operating Model.docx.pdf` pp. 48–57 · Source ID `com`
> Status here is **as of the doc (Oct 26, 2026)**. For the latest cross-doc status (incl. AI Labs answers
> to #5, #14, #23, #24) see `kb/topics/open-questions-status.md`.

## Open (pp. 48–56)

### #29 — Which runtime parts must be ready for the December demo? · Owner: Saar, Nadia · Open
- **Why:** sets v1 scope. From the Uinno call: unknown whether stage changes and stage display (#19, #20) are in this version.
- **Recommendation:** Stage card and suggestions. Deviations and adherence are future phase.

### #14 — What should uploading a methodology document do beyond storing it? · Owner: AI team, Saar · Open
- Will the AI team extract stages and activities? Is document upload needed in v1 at all?
- **Why:** MOON-2392 only stores the file "for later processing" and puts extraction out of scope; meetings 1 and 2 only say the AI team will use it. Nothing says what the user gets after uploading.
- **Recommendation:** Until answered, upload only stores the file. Turning extracted content into methodology changes is future phase.

### #15 — What does the "Download template" file contain, and in what format? Needed in v1? · Owner: Saar · Open
- **Why:** Yulia: user downloads the template, fills it in and uploads it, so the document is structured and easy to process. Format/content not defined yet.
- **Recommendation:** Serve it as a static file once written; no endpoint generates it. Until then, hide the button.

### #16 — Is "Engage with Agent" in the first version? · Owner: Saar · Open
- **Why:** Figma shows an "Engage with Agent" chat next to the methodology editor; no story describes it. Yulia expects it wanted in v1, working like the Workflow editor: the agent changes the editor's local state, the user saves separately.
- **Recommendation:** If in v1, it's frontend + agent work: frontend sends current structure to the agent; backend needs nothing beyond normal save. Saar decides.

### #9 — Should a methodology change reach projects already using it, and when? · Owner: Uinno, Saar · Open
- Example: "Acme ERP Rollout" is in stage 2 "Discovery and Scope"; an admin deletes that stage and saves. What happens to the project?
- **Why:** MOON-2391 and MOON-2393 ask for Draft/Active status, versions and a per-project pinned version, but Figma has none. Saar asked whether methodology changes can flow into attached projects, which conflicts with pinning. Keeping versions only in metadata while changes apply automatically is not versioning (same cost, protects nothing). **Design waits for this answer.**
- **Options:**
  - **A. Live.** Save applies to every project at once. No draft, versions or Publish (as in Figma today). Deleting a stage that projects are in is blocked until they're moved. Cheapest; every edit changes running projects immediately.
  - **B. Draft, then Publish to all.** Edits stay in draft; Publish applies to every project at once and first asks where to move projects whose stage was removed. UI: Publish button + status badge (canvas screens 1–3).
  - **C. Draft, Publish, projects pinned.** Like B, but each project stays on its version until a project admin upgrades it (screens 4–6). Most control, most UI.
- **Recommendation:** B or C. With B, changes still reach projects (as Saar asked) but only when an admin publishes; removed stages handled in one place; versions internal (audit + orchestrator), no version picker in Project Settings. C adds per-project control at the cost of more UI (see #18). *(The architecture tabs are written for option C.)*

### #18 — How does a project move to a newer methodology version? Depends on #9 · Owner: Saar · Open
- **Why:** only option C pins; A has no versions; B moves all on Publish.
- **Recommendation:** If #9 is A or B: close. If C: project admin re-selects the methodology manually, with a "v4 available" notice in Project Settings.

### #8 — Do policies and methodologies need archive/restore, or is delete enough? · Owner: Saar · Open
- Example: admin no longer wants the "Low health alert" policy.
- **Why:** MOON-2391 and MOON-2394 ask for archive, restore, Active/Archived filter and who archived it and when. Policies and Methodologies lists (Figma) show only edit and delete; neither Uinno nor Design remembers agreeing on archive. Archive adds a status, filter, badge, Restore and new screens.
- **Recommendation:** Delete only, as in Figma. A policy used by a methodology, or a methodology used by a project, can't be deleted; confirmation lists where it's used. Add archive later if users ask. *(Note: the architecture/API tabs still describe archive/restore endpoints.)*

### #30 — What happens when a policy is edited from inside the methodology editor? · Owner: Saar · Open
- Example: "New Project Kickoff" is used by two methodologies; admin changes its activities while editing one.
- **Why:** policies are shared; editor picks them from the library and never creates them. Per-methodology copies would confuse users ("copy 1", "copy 2").
- **Recommendation:** Edit the shared policy, not a copy; editor warns "Used in 2 methodologies". **Agreed on the Uinno call; Saar to confirm.**

### #7 — How should the Create Policy form let users choose between a trigger and written instructions? · Owner: Saar, Design · Open
- Example: "Low health alert" via trigger (project health, reason `low_health_score`) or written as "When the client sounds unhappy on a call, suggest a check-in with the PM". Today Description is required and trigger optional, hiding that these are two ways to define a policy.
- **Why:** users think a trigger is always needed; "Description" does two jobs (summary + instructions the orchestrator follows when there's no trigger). **The AI team needs to know which text is instructions.**
- **Recommendation:** Split the jobs. Description = short summary. Radio button picks **Trigger** (trigger + reason) or **Instructions** (free text, called "Prompt" in previous design); chosen one required. Backend adds an `instructions` column. Yulia reworks the form once Saar agrees.

### #19 — On Overview, show the methodology stage, the Certinia stage, or both? Needed in v1? · Owner: Saar · Open
- **Why:** both labelled "Stage"; users can't tell them apart.
- **Options:** Option 1: methodology card when assigned, Certinia card otherwise. Option 2 (Yulia): two widgets (Certinia/Salesforce stage + methodology stage). How the two relate is unclear.

### #20 — Who moves a project to its next methodology stage? · Owner: Saar · Open
- Example: project follows "Enterprise Delivery Framework" (5 stages), in stage 2 "Discovery and Scope"; client signed off scope on today's call. Who moves it to stage 3 "Build": PM by hand, AI suggesting for a person to accept, or sync from the Certinia stage in Salesforce?
- **Why:** methodology stage is new and lives in Veda; not the Certinia stage (Salesforce, e.g. "7/8 Negotiation/Review"); the lists are separate and don't map 1:1. Answer decides what's built (stage picker, `change_stage` type, or per-methodology Certinia picklist mapping) and when the orchestrator suggests the next stage's activities. From the Uinno call: no story covers changing or showing the stage. Older design let a user change it, a suggestion propose it, and skipping a stage needed a reason; activities in a stage ran in order. Whether v1 shows stages at all is unknown.
- **Recommendation:** People and AI suggestions, **no Certinia sync**. Project admins move the stage from the Overview card, to any stage. AI never moves it directly: sends `change_stage` with evidence ("scope signed off on the call of Nov 18"); a project admin applies.

### #12 — What happens to an activity when its agent is deleted? · Owner: Saar · Open
- **Recommendation:** Clear it and flag the activity "Agent removed" in the editor. If #9 keeps versions (B/C), each version keeps the agent's name in its snapshot; with A only the flag remains.

### #13 — What happens to an activity when one of its roles is deleted? · Owner: Saar · Open
- **Why:** an activity can end up with no role, and then the orchestrator has nobody to assign it to.
- **Recommendation:** Remove the link (delete confirmation already shows how many activities use the role). Flag an activity with no role as "No role". Versions keep role names in snapshots (B/C).

### #23 — Role held by several people: one shared suggestion, or one copy per person? · Owner: Saar · Open
- Example: "Send kickoff email" for PM; project has two PMs, Anna and Bob.
- **Why:** with copies, both can apply ⇒ two kickoff emails / two Jira tickets. Preventing that needs grouping and cancelling. Also decides what Bob sees after Anna acts.
- **Recommendation:** One suggestion with both as assignees; shows in "For you" for both; first to apply sends; shows as applied for both. **Agreed on the Uinno call; Saar to confirm.**

### #24 — Can the assignee apply whatever their access level? · Owner: Saar · Open
- Example: Kate holds BA but is Viewer (100). Orchestrator assigns "Create Jira ticket for the gap analysis" via the BA role. Should Apply work?
- **Why:** today apply needs Editor (300), so Kate gets an error and the suggestion sits until it expires. Roles are assigned regardless of access level, so this will happen for every Viewer/Contributor holding a role.
- **Recommendation:** — (none given in the tracker; architecture proposes "yes, except change_stage").

### #5 (incl. #6) — Exact values and names of each shared list · Owner: AI team, Saar · Open
- Lists: trigger types, trigger reasons, activity types (incl. what "Certinia suggestion A/B/C" are), suggestion types, event types, target kinds, source kinds, methodology types.
- **Why:** ISS, frontend and orchestrator must use the same keys; renaming later needs a data migration. None final: Figma's four trigger labels came from Saar's comments, Figma has no reasons, activity-type keys (`email`, `slack_teams`, …) use an old naming style, and "PM Tool / Jira" could mean create or update.
- **Recommendation:** Agree with the AI team in topic 5. Triggers/events named `<domain>.<entity>.<event>`; reasons snake_case (e.g. `low_health_score`).

## Decided (pp. 56–57)
Each keeps its original number.

| # | Question | Decision | Decided by |
|---|---|---|---|
| 1 | Do Project Team Roles need manual order (drag to reorder)? | **No manual reorder.** New roles go last. MOON-2390 asked for reorder, but Figma never had it and Nadia confirmed it's not needed. | Uinno, Nadia |
| 2 | Build a user's default project role (no story, but meeting 1 + Figma field)? | **Build as assumed.** One optional default role per user (`users.default_project_team_role_id`), set in Personal Information; prefills the role select when the user is added to a team; whoever adds them can change it. Never changes existing roles or access. Deleting the role clears it. Direct Supabase write. | Uinno |
| 3 | How does an admin set another user's default role? | Design (Yulia) adds it to the users screens; frontend builds it when ready. Self-service field ships first. No backend work (users RLS already allows tenant admins). | Uinno, Design |
| 4 | What does "Project roles" in Project Settings → Methodology mean? | **Remove it** — leftover from older design; Yulia removes from Figma. | Uinno, Design |
| 10 | What does a Recurring methodology mean at runtime? | One-Time stops after last stage; **Recurring restarts at stage 1**, like sprints. | Uinno |
| 11 | Does the Activity form need a "Guidance / expected outcome" field? | **No.** Prompt covers expected outcome. | Uinno |
| 17 | Who can select a project's methodology? | **Access level 400**, matching who can open Project Settings. | Uinno |

*(Numbers not present in the doc: #6 is folded into #5; #21, #22, #25–#28 do not appear.)*
