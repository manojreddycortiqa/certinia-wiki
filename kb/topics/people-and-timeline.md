# People, teams, timeline and action items

> From all sources. Pronouns are not stated in the docs; refer to people by name.

## Teams / organisations
| Team | Role in MOON-2389 | Source |
|---|---|---|
| **Uinno** | Backend + frontend vendor building storage, admin UI, editor, Project Settings, suggestion delivery, the contract | com/00 |
| **Veda / Veda Accelerate team** | Product side; owns interim methodology file, credentials API, upload experience (first priority per 30 Oct meeting) | ai-labs |
| **AI team / AI Labs** | Builds the orchestrator (triggers, policy interpretation, suggestion content) | com, ai-labs |
| **Moonnox** | "Routes and executes" (COM p. 40 diagram); owns the scheduler clock for time-based triggers; may host live data | com/11, ai-labs |
| **Certinia** | Customer/partner org; Certinia stage + RAID via Salesforce; Certinia legal/privacy/security approve live data | com, ai-labs |
| **Design** | Figma (Company Methodologies frames) | com |

## People
| Name | Role as seen in the docs |
|---|---|
| **Artem Derevyanko** | Author of the COM Architecture tab (Oct 26). Owns: revised suggestion item + endpoint (AI Labs reviews), context endpoint, who converts uploaded documents (#14) |
| **Saar / Sa'ar** | Product decision-maker; owner of most open questions (#5, #7, #8, #9, #12–#20, #23, #24, #29, #30); decides whether upload is in v1 |
| **Nadia** | Co-owner of #29; decided #1 (no role reorder) |
| **Yulia** | Design; reworks forms (#7), users screens (#3), removes "Project roles" (#4), proposes two-widget stage display (#19), template flow (#15), Engage with Agent expectations (#16) |
| **David** | Leads the Monday (2026-11-02) call deciding live test data |
| **"@Someone"** | Author tag on the AI Labs answers doc (placeholder) |
| Anna Smith, Bob, Mark, Kate | **Fictional examples** in the docs (Coca Cola / Acme ERP Rollout scenarios) — not real people |

## Timeline
| Date | Event | Source |
|---|---|---|
| 2026-10-20 (Tue) | Meeting 2: policies, triggers; Gate → Stage, Action → Activity rename | com/01, 10 |
| 2026-10-26 (Mon) | COM Architecture doc written; sources read | com/01 |
| 2026-10-30 (Fri) | Working session with Veda Accelerate; AI Labs answers doc published | ai-labs |
| "within days" of 10-30 | Veda Accelerate to share interim methodology JSON file | ai-labs T2 |
| 2026-11-02 (Mon) | Monday call led by David on live test data | ai-labs |
| **2026-11-04 (Wed)** | **December use cases frozen**; final catalog keys and triggers follow | ai-labs |
| TBD | Joint working session to close open items | ai-labs |
| December 2026 | Milestone / demo: 2–3 triggers, context, suggestions, credentials; everything human-approved | ai-labs, com #29 |
| 2026-11-12 / Nov 18 | Appear only in examples (snapshot `published_at`, "call of Nov 18") | com |

## Action items by owner (latest known)
- **Artem:** revised suggestion item + endpoint (several target users); context endpoint with team roles + methodology; decide document conversion owner (#14).
- **Veda Accelerate:** interim methodology file (format + date); credentials API + trusted workload identity; upload experience.
- **AI Labs:** review Artem's suggestion structure; confirm Certinia A/B/C with Certinia; confirm final catalog lists after 4 Nov; build stage-advance suggestion once approved.
- **Both teams:** pick Dec triggers + delivery; one event layer; versioning rules.
- **Product and architecture:** autonomy setting; suggestion vs action definitions.
- **David:** test data decision (Monday call).
- **Saar:** decisions on #9, #8, #7, #14 (v1 inclusion), #15, #16, #19, #20, #23, #24, #29, #30.
