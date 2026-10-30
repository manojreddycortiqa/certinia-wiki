# Open questions — consolidated status across all sources

> Merges the COM tracker (`sources/client-operating-model/12-open-questions.md`, as of Oct 26, 2026) with later
> input (`sources/ai-labs-answers.md`, Oct 30, 2026). **Update this file whenever a new source changes a status.**
> "Latest input" = newest source that says something about the question.

| # | Question (short) | Owner | COM status | Latest input | Current read |
|---|---|---|---|---|---|
| 29 | Which runtime parts ready for the December demo? | Saar, Nadia | Open — rec.: stage card + suggestions | AI Labs: Dec = 2–3 triggers, context, suggestions with several users, outcomes; all actions human-approved | **Open** |
| 14 | What does methodology document upload do? Extraction? | AI team, Saar (AI Labs: Artem; v1 inclusion = Sa'ar) | Open — rec.: store only | AI Labs: upload should produce the same structured JSON; **Veda owns conversion** (proposal); AI-built = separate scope, output = proposal; meeting made upload experience **Veda Accelerate's first priority** | **Open** — ownership to settle (Artem) |
| 15 | "Download template" content/format; needed in v1? | Saar | Open — rec.: static file; hide button until written | — | **Open** |
| 16 | "Engage with Agent" in v1? | Saar | Open | — | **Open** |
| 9 | Do methodology changes reach existing projects? (A live / B publish-to-all / C pinned) | Uinno, Saar | Open — rec.: B or C (architecture written for C) | AI Labs: works either way; new evaluations use the project's version | **Open** — blocks design |
| 18 | How does a project upgrade versions? | Saar | Open — depends on #9 | — | **Open** |
| 8 | Archive/restore vs delete for policies & methodologies | Saar | Open — rec.: delete only | AI Labs: pending suggestions for removed/archived items are retired | **Open** |
| 30 | Editing a shared policy from the methodology editor | Saar | Agreed on Uinno call; Saar to confirm (edit shared, warn "Used in N") | — | **Agreed, pending confirmation** |
| 7 | Trigger vs written instructions in Create Policy form | Saar, Design | Open — rec.: radio Trigger/Instructions + `instructions` column | AI Labs wants a **separate instructions field** in context, treated as untrusted input | **Open** (AI Labs supports rec.) |
| 19 | Overview: methodology stage, Certinia stage, or both? | Saar | Open (Option 1 vs Option 2) | — | **Open** |
| 20 | Who moves the methodology stage? | Saar | Open — rec.: people + AI suggestions, no Certinia sync | AI Labs agrees: admin moves, AI suggests `change_stage`; **no automatic Certinia sync** | **Open**, both teams aligned on rec. |
| 12 | Activity's agent deleted | Saar | Open — rec.: clear + flag "Agent removed" | — | **Open** |
| 13 | Activity's role deleted | Saar | Open — rec.: remove link + flag "No role" | (AI Labs: nobody holds role → owner fallback) | **Open** |
| 23 | Role held by several people: shared vs copies | Saar | Agreed on Uinno call; Saar to confirm (one shared, first apply wins) | AI Labs: **same** | **Aligned, pending Saar** |
| 24 | Can an assignee apply at any access level? | Saar | Open — no rec. in tracker; architecture proposes yes except `change_stage` | AI Labs: **yes, except stage moves (need project admin)** | **Aligned proposal, pending Saar** |
| 5 (+6) | Exact values/names of shared lists | AI team, Saar | Open — rec.: catalog, naming rules | AI Labs: agree on catalog + rules; add status values; final keys after **Dec use cases frozen 4 Nov**; Certinia A/B/C to confirm with Certinia | **Open** until ~4 Nov+ |
| 1 | Manual role reorder? | Uinno, Nadia | **Decided:** no | — | Decided |
| 2 | User default project role? | Uinno | **Decided:** build (`users.default_project_team_role_id`) | — | Decided |
| 3 | Admin sets another user's default role? | Uinno, Design | **Decided:** Yulia designs; self-service first | — | Decided |
| 4 | "Project roles" in Project Settings → Methodology? | Uinno, Design | **Decided:** remove | — | Decided |
| 10 | Recurring methodology at runtime? | Uinno | **Decided:** restarts at stage 1 | — | Decided |
| 11 | "Guidance / expected outcome" field? | Uinno | **Decided:** no | — | Decided |
| 17 | Who selects project methodology? | Uinno | **Decided:** access level 400 | — | Decided |

## New questions raised by AI Labs (not numbered in COM)
- Which **2–3 December triggers** (and whether `schedule.daily_check` is needed) — both teams, after Dec use cases (4 Nov).
- Getting **`callpilot.call.ended`** into the durable feed (today a Celery task) or an equally durable alternative.
- **Outcome events** (applied/dismissed/expired/succeeded/failed) in the v1 feed.
- **Feed retention** policy; behaviour when a project's **confidentiality changes**.
- **Credentials API** (KMS, short-lived tokens) and which **workload identity** Veda trusts — Veda Accelerate.
- **Autonomy setting** and suggestion-vs-action definitions — Product and architecture.
- **Versioning rules** for events, schemas, APIs — both teams.
- **Test data / live data approval** — Monday 2026-11-02 call led by David.
- **Interim methodology JSON file** format and delivery date — Veda Accelerate.
