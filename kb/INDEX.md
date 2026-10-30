# Knowledge base index — December milestone (MOON-2389)

Start here. Find the question type in the router, open the listed file(s), cite source + page.

## Source registry
Every file in `docs/` must have a row. `sha256` = first 12 hex chars of `shasum -a 256` (detects replaced files).

| ID | File in `docs/` | Date / author | Pages | sha256 | Markdown | Raw text |
|---|---|---|---|---|---|---|
| `com` | `MOON-2389 Client Operating Model.docx.pdf` | 2026-10-26 · Artem Derevyanko (Architecture tab) | 65 | `36132d752c5c` | `sources/client-operating-model/` (14 files) | `raw/com.txt` |
| `ai-labs-answers` | `MOON-2389 AI Labs answers to the AI team topics.pdf` | 2026-10-30 · AI Labs ("@Someone") | 11 | `5e4a3f6c3166` | `sources/ai-labs-answers.md` | `raw/ai-labs-answers.txt` |

Precedence when sources disagree: the **newer** source reflects the latest position, but a reply/proposal is not
an agreement — say which source says what. `ai-labs-answers` (Oct 30) is a response to `com` (Oct 26).

## `com` section map (page → file)
| Pages | File | Contents |
|---|---|---|
| 1–3 | `00-overview.md` | Plain-language summary, building blocks, who does what, what ships when |
| 4–8 | `01-architecture-decisions.md` | 11 decisions, scope, glossary, name clashes, system overview diagram |
| 8–14 | `02-domain-model.md` | All 16 tables, conventions, entity diagram, trigger params |
| 14–17 | `03-methodology-lifecycle.md` | Draft/active/archived, publish RPC, snapshot JSON, policy revisions, upgrades |
| 17–25 | `04-public-api.md` | Tree format (TS types), every public endpoint (roles, team, policies, catalog, methodologies, project methodology) |
| 25–26 | `05-permissions.md` | Permission matrix, why 400 |
| 26–28 | `06-audit-events-feed.md` | Audit trail, event catalog, feed cursor semantics |
| 28–30 | `07-runtime-and-visibility.md` | Current stage, visibility standard, audiences, RLS |
| 31–33 | `08-suggestion-integration.md` | Assignees, source attribution, dedup, change_stage, activity→suggestion map |
| 33–34 | `09-document-upload.md` | Upload pipeline + error codes |
| 34–38 | `10-tenancy-limits-testing-risks.md` | Tenancy, concurrency, limits, perf, tests, risks, doc sources |
| 39–47 | `11-ai-team-topics.md` | Veda's proposal to the AI team (topics 1–6, flow diagram, catalog example) |
| 48–57 | `12-open-questions.md` | Open + decided questions as written |
| 58–65 | `13-future-phase.md` | Deviations, adherence, activity tracking, autonomy, proposals, suggestion sets |

## Question router
| If the question is about… | Read first | Then |
|---|---|---|
| What the feature is / non-technical summary | `sources/client-operating-model/00-overview.md` | `topics/glossary.md` |
| What's in December / v1 scope | `topics/open-questions-status.md` (#29) | `sources/ai-labs-answers.md` (headline asks), `com/00` "What ships when", `com/01` scope |
| AI orchestrator integration, contract, what's agreed vs not | `topics/ai-integration-contract.md` | `sources/ai-labs-answers.md`, `com/11` |
| Events, triggers, feed, cursor | `com/06` | `ai-labs` Topic 1, `topics/catalog-keys.md` |
| Context the AI reads | `com/11` §2 | `ai-labs` Topic 2 |
| Suggestions (shape, targets, assignees, dedup, apply) | `com/08` | `com/07`, `ai-labs` Topics 3–4 |
| Tables / columns / constraints | `com/02` | `raw/com.txt` for exact wording |
| Endpoints, request/response shapes | `com/04` | `topics/catalog-keys.md` (endpoint list) |
| Permissions / who can do what | `com/05` | `com/08` (apply rules) |
| Methodology versions, publish, upgrade | `com/03` | OQ #9/#18 in `topics/open-questions-status.md` |
| Stages / stage moves | `com/07` | `ai-labs` Topic 6, OQ #19/#20 |
| Policies, triggers vs instructions | `com/02` (trigger params) | OQ #7, `ai-labs` "Policies, activities and autonomy" |
| Auth / credentials / security | `topics/ai-integration-contract.md` (Auth row) | `ai-labs` Technical details, `com/02` service_credentials, `com/10` tenancy |
| Document upload / extraction | `com/09` | OQ #14, `ai-labs` OQ #14, `com/13` |
| Test data / live data | `ai-labs` Test data | — |
| A specific key / error code / endpoint name | `topics/catalog-keys.md` | — |
| Who owns what / dates / next steps | `topics/people-and-timeline.md` | `ai-labs` joint session table |
| Status of an open question | `topics/open-questions-status.md` | `com/12` for full original text |
| Later / out-of-scope features | `com/13` | — |
| Risks | `com/10` Risks | `topics/ai-integration-contract.md` ❌ rows |

(`com/NN` = `sources/client-operating-model/NN-*.md`; `ai-labs` = `sources/ai-labs-answers.md`.)

## Images
`assets/com/p8_0.png` system overview · `p9_0.png` entity diagram · `p14_0.png` methodology lifecycle · `p40_0.png` flow A sequence. Each is described in text in its section file.
