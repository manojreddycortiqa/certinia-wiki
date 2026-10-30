# certinia-wiki — document knowledge base (MOON-2389, December milestone)

This repo is a **Q&A knowledge base**, not a code project. The user uploads design docs (PDFs) into
`docs/` and asks questions about them. The PDFs have been converted into structured markdown under `kb/` so
questions can be answered without re-parsing PDFs. (Moved here from `Docs/dec-milestone` on 2026-10-31.)

**Stay inside this repo** (`/Users/mreddy.c/workspace/certinia-wiki`) unless the user explicitly says otherwise.

## Layout
```
docs/                     Original uploads. Source of truth. Never edit, rename or delete.
kb/
  INDEX.md                Source registry + page→file map + question router. START HERE.
  sources/                Faithful per-document markdown (one file, or a folder split by section for big docs).
    client-operating-model/   00–13, one file per tab/section of the 65-page COM doc
    ai-labs-answers.md
  topics/                 Cross-document synthesis (updated whenever a new source arrives)
    ai-integration-contract.md   Veda proposal vs AI Labs answer, ✅/⚠️/❌ per area
    open-questions-status.md     Every OQ with latest status across all sources
    catalog-keys.md              Event/trigger/activity/suggestion keys, endpoints, error codes
    glossary.md                  Terms, ambiguous words, systems
    people-and-timeline.md       Teams, people, dates, action items
  raw/<id>.txt            Verbatim page-marked text extraction (grep this for exact quotes)
  assets/<id>/pN_i.png    Diagrams extracted from the PDFs (N = page)
tools/extract_pdf.py      PDF → raw text + images
.venv/                    Python venv with pdfplumber + pypdf (for tools/); git-ignored, rebuild per machine
```

## Answering questions
1. Open `kb/INDEX.md`, use the **question router** to pick 1–3 files. Read only those; don't load everything.
2. Answer from the markdown. For exact wording, or if the markdown seems to be missing something, `grep -n` the
   relevant `kb/raw/<id>.txt` (page markers: `===== PAGE N =====`). Only fall back to the PDF itself if raw is unclear
   (e.g. a diagram) — the Read tool can't render PDFs here (no poppler), so use the extracted PNGs in `kb/assets/`.
3. **Cite** source and page, e.g. "(COM p. 31)" or "(AI Labs p. 5)". Source IDs: `com`, `ai-labs-answers`.
4. **Distinguish proposal / answer / decision.** The COM doc is a proposal with many open questions; the AI Labs doc
   is a reply, not an agreement. Only the COM "Decided" table (#1, 2, 3, 4, 10, 11, 17) records decisions. Say who
   said what, and flag conflicts (see `topics/ai-integration-contract.md`).
5. Prefer the newer source for "current position", but never silently drop the older one's view.
6. The docs contain fictional example people (Anna, Bob, Mark, Kate; projects "Coca Cola", "Acme ERP Rollout"). Don't treat them as real.
7. Docs give no pronouns for real people (Artem, Saar, Nadia, Yulia, David) — use names or they/them.

## Ingesting a new document (when the user uploads more docs)
1. Detect new/changed files: compare `ls docs/` and `shasum -a 256 docs/*` against the registry in `kb/INDEX.md`.
2. Pick a short kebab-case source ID (e.g. `dec-use-cases`). Extract:
   `.venv/bin/python -I tools/extract_pdf.py "docs/<file>.pdf" <id>`
   (If `.venv` is missing: `python3 -m venv .venv && .venv/bin/pip install pdfplumber pypdf`.)
   For `.docx` / `.md` / `.txt` uploads, read directly; for `.docx`/`.pptx`/`.xlsx` use the matching skill.
3. Read the whole raw file. View every image in `kb/assets/<id>/` and describe diagrams in text.
4. Write `kb/sources/<id>.md` (≤ ~15 pages) or `kb/sources/<id>/NN-section.md` (split by the doc's own tabs/headings).
   Each file starts with a `> Source: docs/<file> pp. X–Y · Source ID <id>` line; keep page refs in headings;
   keep tables as markdown tables and JSON/TS/SQL as code blocks; keep it faithful — no invented content,
   mark your own notes as *(Note: …)*.
5. Update `kb/INDEX.md`: registry row (date, author, pages, sha256), section map if split, router entries.
6. Update every affected `kb/topics/*` file (open-question statuses, contract table, keys, glossary, people/timeline).
   Add a new topic file only when a theme spans ≥2 sources and doesn't fit an existing one.
7. If a doc replaces an older version: regenerate its source files, keep the same ID, note the change in INDEX.
8. Tell the user what was added and any new conflicts or decisions it introduced.

## Context snapshot (as of 2026-10-31 — re-verify against kb/ before relying on it)
- Feature: **MOON-2389 Client Operating Model** in Veda — clients define Project Team Roles, Policies and
  Methodologies (stages → activities); an AI **orchestrator** (AI team / AI Labs) turns events into role-targeted
  **suggestions** a person applies. Backend: `integration-sync-service` (ISS) on Supabase Postgres; built by **Uinno**.
- December: 2–3 triggers in one durable feed, context endpoint, interim methodology JSON, multi-user suggestion
  endpoint with outcomes, KMS-issued scoped credentials. **Every December action is human-approved.**
- Key dates: Dec use cases frozen **2026-11-04**; live-data decision at the **2026-11-02** call (David).
- Biggest unresolved: OQ #9 (versioning model, blocks design), #29 (Dec runtime scope), #14 (who converts uploads),
  auth model (service key vs KMS tokens), outcome events + `callpilot.call.ended` in the feed.
