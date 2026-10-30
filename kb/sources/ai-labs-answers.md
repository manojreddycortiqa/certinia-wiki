# AI Labs answers to the AI team topics (MOON-2389)

> Source: `docs/MOON-2389 AI Labs answers to the AI team topics.pdf` · 11 pages · Source ID `ai-labs-answers`
> Dated **Oct 30, 2026 (Friday)**, author shown as "@Someone" (AI Labs).
> Answers the COM doc's "AI team: topics to discuss" (COM pp. 39–47 → `client-operating-model/11-ai-team-topics.md`),
> open questions **#5, #14, #23, #24**, and actions from the **30 Oct working session with the Veda Accelerate team**.

## Headline asks for December (p. 1)
1. Two or three **priority triggers** delivered as documented events in **one durable feed**.
2. A **context endpoint** with team roles and methodology content.
3. An **interim methodology file** in the final format.
4. A **suggestion endpoint** that accepts **several target users** and **reports outcomes**.
5. **Scoped credentials issued by Veda's key management** (KMS).

**Every December action is a suggestion a person approves.** Final catalog keys follow once the December use
cases are agreed (**frozen 4 Nov**, Wednesday 2026-11-04).

---

## Topic 1 — Which events reach the orchestrator, and how? (pp. 1–2)
**Q:** Which 2–3 triggers in December, how is each received, do we need one consolidated event layer for the MVP?
**A:** Three December triggers, plus a fourth only if a December use case needs it. Final choice follows the December use cases (frozen 4 Nov).

| Event | Where the signal is today | Identifiers in payload | Time and history | Delivery |
|---|---|---|---|---|
| `callpilot.call.ended` (a call completed) | CallPilot; sent straight to WorkflowService as a **Celery task** today | tenant, project ID, call ID | `occurred_at`; transcript and summary read by call ID | Event feed |
| `project.health.status_changed` (e.g. health turns red) | Project health webhook events in Integration Sync | tenant, project ID, from and to status | `occurred_at`; previous status in payload | Event feed |
| `project.methodology.stage_changed` | New project methodology table | tenant, project ID, methodology version ID, from and to stage ID, who moved it (person or applied suggestion, with `suggestion_id`) | `occurred_at` | Event feed |
| `schedule.daily_check` (**only if needed**, e.g. chasing pre-work before training) | Veda's scheduler | tenant, project ID | scheduled date, in tenant's time zone | Event feed |

**Later candidates:** a user question or request; a delegated agent action completed; a task completed or changed.

**One event layer: yes**, for the selected triggers. Each should arrive through the same durable, replayable feed:
MOON-2389's append-only table, written **in the same transaction as the change**. Two delivery paths with
different replay/dedup rules is the main risk. If a signal can't move into the feed by December, it needs an
equally durable alternative.

**Every event carries:** documented stable name (`<domain>.<entity>.<event>`), payload version, sequence number,
`occurred_at`, and **IDs/references only — no message or transcript text**. AI never infers meaning from raw
application tables or discovers events at runtime.

**AI Labs side:** owns the feed consumer and its cursor; saves the cursor with its own record of what it
processed; suggestion dedup key makes replay after a crash harmless. If one event leads to several suggestions,
it moves past the event only once every item is created or recorded as rejected for good.

**AI Labs needs:**
1. The feed, and the selected triggers in it, in the first version.
2. Feed rows append-only for v1, minimal sensitive fields; long-term retention agreed before indefinite storage is promised.
3. Confidential projects left out of the feed and context reads, and an agreed behavior when a project's confidentiality changes.
4. A test feed with synthetic data in a dev tenant.

## Topic 2 — What does the orchestrator need to read from Veda? (pp. 3–4)
**Q:** Minimum context for the MVP; how the context integration works (schemas, auth, errors, retries, idempotency, observability).
**A:** One **context endpoint per project**, plus the **methodology-version endpoint**, covers the MVP. Minimum context:
1. **Project:** tenant, project ID, name, status and health, key dates (start, go-live, milestones, training).
2. **Team:** per member — user ID, name, project role(s), access level, owner flag, assignment metadata (date added; allocation if available). Used to choose who receives a suggestion (topic 4).
3. **Methodology:** pinned version, current stage, stage's activities, applicable policies (stage-linked and standalone) as `{policy_id, revision}` or resolved content, and a **separate instructions field** (OQ #7). Instructions are client-written ⇒ treated as **untrusted input, never commands**.
4. **Suggestion history:** what was already sent on the project and where each stands (avoid repeats).
5. **Signals:** whether Slack or Teams is connected. Certinia data (opportunity stage, RAID) keeps coming through Integration Sync's existing Certinia context endpoint.

**How the integration works:**
- **Schemas:** request/response shapes published as **JSON Schema with a version** (topic 5); AI validates in CI.
- **Authentication:** see Technical details.
- **Errors:** `{detail, code, meta, request_id}`, stable error codes.
- **Retries:** reads idempotent; retry timeouts and 5xx with backoff, **never 4xx**.
- **Caching:** 60-second cache per project, cleared by that project's events — fine.
- **Observability:** `X-Request-Id` on every call; both sides log it.

### Methodology input and the interim file (pp. 3–4)
**Q:** Text file, structured data, or both? Who converts uploaded documents; how is methodology content retrieved
and updated? Veda Accelerate will share an interim file within days so integration can start before UI/backend are finished.
**A:** **Structured data is the contract**, with natural-language parts carried inside it.
- **Format:** JSON in the same shape the methodology product will publish — the methodology version snapshot in MOON-2389 (methodology, stages, items of kind activity or policy, policy triggers, roles, agents), plus standalone policies and the project or practice each applies to. Policy instructions, activity descriptions and prompts are text fields inside it.
- **Interim file:** one JSON file per methodology in exactly that shape, with a `schema_version`. AI builds against it now; production endpoint replaces it with no change beyond the URL. Please include **at least one methodology with a standalone policy** (e.g. health turns red) and **one activity with an explicit agent or action**.
- **Retrieval:** through context + methodology-version endpoints. For the interim file, a shared location is fine until the endpoint exists.
- **Updates:** clients change methodology through Veda's product (upload, then incremental edits). AI doesn't write methodology in v1; later, any AI change goes through Veda's proposals flow for an admin to accept.
- **Conversion of uploaded documents:** proposes **Veda owns it**, as part of the upload experience, producing the same JSON. If Veda wants AI Labs to build extraction, it's separate scope with its own timeline (OQ #14).

## Topic 3 — How does the orchestrator send suggestions back? (pp. 4–5)
**Q:** What does the suggestion item need; one target user or several? **Artem** will send the revised suggestion-item structure and endpoint for AI Labs to review.
**A:** AI Labs will review Artem's revised structure. Needed per item:

| Field | Why |
|---|---|
| Target users (one or more) | AI chooses who receives it (topic 4) |
| Applicable role | Shown to the user; used for the owner fallback |
| Project ID | Every suggestion belongs to one project |
| Suggestion type | One of the actions Veda runs, from the activity type |
| Title and narrative | What the person reads |
| Action payload | The schema Veda already uses for that type |
| Source | Event sequence number, policy and revision, activity, methodology version |
| Evidence and confidence | Evidence references (call, ticket, health event) and a low / medium / high label |
| `expires_at` | Some suggestions stop being useful after a date |
| Deduplication key | A repeat is ignored, so retries are safe |

**From the endpoint AI Labs needs:**
1. **Several target users per suggestion:** one shared suggestion; first person to apply completes it for everyone (#23).
2. **A result per item:** `created`, `duplicate` or `rejected`, with machine-readable error code; one bad item doesn't fail the rest.
3. **Outcome events in the feed**, in v1, written in the same transaction as the change: `applied`, `dismissed`, `expired` (sent **before** cleanup deletes the suggestion), and the action's `succeeded` or `failed`. Each carries stable IDs, timestamp, who acted, request ID and error code. An applied suggestion can still fail, so the two must be separate.
4. **Payload schemas** for each suggestion type, published in the catalog.

**Observability tracked:** feed lag, time from event to suggestion, duplicate and rejection rates, counts of
applied/dismissed/expired suggestions and of actions that succeeded/failed.

## Topic 4 — Who receives a suggestion? (pp. 5–6)
**Q:** Role, specific user, or both? Who picks the user; what if several people hold the role?
**A:** **The orchestrator picks the users**; the suggestion names them **and** the role it applies to.
1. Veda provides the team (project ID, user ID, role(s), assignment metadata) in the context (topic 2).
2. AI chooses: the activity's role narrows candidates; methodology, project context, current commitments and prior work on the project pick the most appropriate person.
3. **No reliable distinction:** one shared suggestion to everyone holding the role; first to apply completes it for all (#23).
4. **Nobody holds the role:** goes to the **project owner**, with the role kept so the UI can say no one holds it.
5. **Who can apply (#24):** the person a suggestion is for can apply it **whatever their access level, except stage moves**, which need a project admin.
6. **Team changes:** when `project.team.changed` arrives, AI re-checks only **pending** suggestions — either recipients are updated, or the old one is retired and replaced in one step. **Never two live copies** (e.g. sending the same email twice).

## Topic 5 — Shared values and versioning (pp. 6–7)
**Q:** Which shared lists/canonical values, and how are events, methodology schemas, activity types and APIs versioned?
**A:** **One catalog in Veda**, read through the catalog endpoint, is the source for every shared value:
- Keys lowercase and never change once used; labels display-only.
- Events and triggers named `<domain>.<entity>.<event>`; reasons and status values `snake_case`.
- Catalog includes **status values** (suggestion, outcome, methodology, project health), not just types.
- Unknown key → rejected with an error, never guessed.

**Versioning:**
- Each event type, the methodology schema, the activity-type list, the catalog and each API carries a version (`schema_version` in payloads; a version in the API path or header).
- Adding a value or optional field = minor (readers ignore unknowns). AI contracts already read this way.
- Renaming/removing a key or making a field required = **new major version**; both served side by side until an agreed retirement date; neither team changes this alone.
- Catalog has a version or hash, so changes are noticed.

**Time-based triggers:** if a December use case needs one, Veda's scheduler adds one scheduled event per project to
the feed (topic 1); AI evaluates date rules against project context. **Moonnox owns that clock.**

Final keys follow once December use cases are agreed. **Certinia suggestion A, B, C:** the Architecture tab's
mapping (stage update, create RAID, update RAID) is a guess; AI Labs will confirm with Certinia.
Insight/content creation and document generation have no suggestion type in v1; AI Labs will check the December
use cases don't need them.

### Policies, activities and autonomy (pp. 7–8)
**Q:** How do a policy's natural-language trigger and an explicit configured trigger coexist? How are activity
descriptions and explicit agent/action assignments read? How is autonomy configured; suggestion vs autonomous action?
**A:**
- **Explicit vs natural-language triggers:** the explicit trigger decides **when** a policy is looked at; the text decides **whether** it applies and **what** to suggest. A text-only policy is checked against the December triggers, not every event. If text contradicts the configured trigger, **the configured trigger wins** and the conflict is flagged to the admin.
- **Activities:** the activity type decides the suggestion type. An explicit agent/action assignment always wins over anything read from the description; description and prompt shape the content.
- **Suggestion vs autonomous action:** a suggestion is shown to a person who applies or dismisses; nothing happens until applied. An autonomous action is carried out without approval.
- **Autonomy setting**, per activity with a policy-level default: *always needs approval*; *may act autonomously*; or *needs approval when confidence or context is below a threshold*.
- **December: every action is a suggestion a person approves.** An autonomous use case starts only when both teams approve it, with a confidence threshold, an audit record of every action, a way to undo it, and an off switch per tenant.

## Topic 6 — How do stage changes work? (p. 8)
**A:** A project admin moves the stage; AI only suggests the move with `project.methodology.change_stage` and evidence, sent to the **project owner and admins**. Applying runs the same step a person uses.
- AI will build the stage-advance suggestion once approved. Sent when evidence shows the stage's required activities are done, citing it. A stage can also look complete from a call (e.g. scope signed off).
- **Knowing an activity is done:** MOON-2389 defers activity tracking. For December, AI counts an activity done when **a suggestion for it was applied and its action succeeded** (topic 3 outcome events). Activities done outside Veda won't be seen until activity tracking exists.
- Stage-change events say whether a person or an applied suggestion made the move (with `suggestion_id`). On arrival, AI suggests the next stage's activities.
- **Methodology stage and Certinia stage stay separate, no automatic sync.**

### Methodology versions and updates (pp. 8–9)
**Q:** Clients update methodology after retrospectives. How do updates affect active projects and existing suggestions?
**A:**
- Every suggestion records the methodology version and policy revision it came from.
- New evaluations use the version the project is on: immediately after publishing, or after project upgrade, depending on OQ #9.
- Pending suggestions whose activity/policy was removed or archived are **retired**; the rest stay valid until they expire.
- Applied and dismissed suggestions are history and never change.

## Technical details: authentication and tracing (p. 9)
**Q:** How does the orchestrator authenticate? The meeting agreed **Veda implements scoped service credentials in its
KMS**, with rotation and secure storage, and a secure API so AI retrieves credentials/authorization at runtime rather than static config.
**A:** Agreed. Needed from the design:
1. **Runtime retrieval:** AI service calls Veda's credentials API, receives a **short-lived, scoped token (minutes, not days)**. No long-lived secret in AI config.
2. **First call identity:** AI proposes its service's **cloud workload identity** (e.g. an **AWS IAM role, per environment**) rather than a stored bootstrap secret. Veda confirms which identity it trusts.
3. **Scopes:** read event feed; read context and methodology; write suggestions — each limited to allowed tenants. Nothing else.
4. **Rotation/expiry:** keys rotate in Veda's KMS without AI action; tokens expire and AI refreshes before.
5. **Revocation/incidents:** either side can revoke AI's identity at once; agree who is called, and how fast, if a credential may be exposed.
6. **Validation:** a dev-tenant test shows every call (feed, context, methodology, catalog, suggestions) succeeds with the right scope and fails without it.
7. **Tracing:** `X-Request-Id` on every call, logged as correlation ID.

**This must be in place before any access is granted.**

## Open question #14 — What should uploading a methodology document do? (p. 10)
Context: the meeting made **the upload experience Veda Accelerate's first priority**, generating the structured file from an uploaded document.
- Upload produces the **same structured JSON as the interim file**, so uploaded and hand-built methodology are read the same way.
- **Who converts:** AI Labs proposes **Veda owns the conversion**. If AI Labs builds it: separate scope + timeline; its result would be a **proposal an admin accepts**, with publishing a separate step.
- **Whether upload is in v1 is Sa'ar's decision**; the orchestrator works either way.
- **Later, not December:** quality check at upload (ambiguity, contradictions, undefined terms); comparing activities against the agent registry to find activities with no agent; project-specific agents for those gaps. AI Labs can contribute to all three.

## Open question #5 — Shared list values and names (p. 10)
As in topic 5: one versioned catalog in Veda with those naming rules. AI Labs will confirm final lists, any
time-based trigger keys and the Certinia mapping once December use cases are agreed.

## Test data (pp. 10–11)
**Q:** Live customer data, synthetic, or staged combination; what approvals/controls?
**A:** A **staged combination**:
1. **Now:** synthetic data only, in a dev tenant.
2. **Live data** only after written approval from the customer, Certinia legal, privacy and security, and AI Labs. **The outcome of the Monday call (led by David)** decides whether and when. *(Monday after the doc date = 2026-11-02.)*
3. **Where it runs:** live data stays in a Certinia- or Moonnox-hosted environment, **never in AI Labs repositories, test fixtures or CI**.
4. AI code keeps rejecting real data until approval exists; the rule then changes through a reviewed change, not before.
5. **Controls to agree:** masking/anonymization, access, retention, deletion at end of MVP, and which fields may be sent to **Arthur** for scoring.

## For the joint working session — items to close (p. 11)

| Item | Owner |
|---|---|
| The two or three December triggers and their delivery (topic 1) | Both teams |
| One event layer for the selected triggers | Both teams |
| Interim methodology file: format and delivery date | Veda Accelerate |
| Revised suggestion item and endpoint, several target users | Artem; AI Labs reviews |
| Context endpoint with team roles and methodology | Artem |
| Credentials API and the workload identity it trusts | Veda Accelerate |
| Autonomy setting and the suggestion vs action definitions | Product and architecture |
| Versioning rules for events, schemas and APIs | Both teams |
| Test data: outcome of the Monday call | David |
| Who converts uploaded documents (#14) | Artem |
