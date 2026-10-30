# COM · Overview (non-technical)

> Source: `docs/MOON-2389 Client Operating Model.docx.pdf` pp. 1–3 · Source ID `com`
> The "Overview" tab of the doc. Plain-language summary; other tabs hold engineering detail.

## The idea in one paragraph (p. 1)
Every client runs projects their own way: own steps, own rules, own people in specific roles. Today
Veda gives everyone the same generic guidance. With MOON-2389 a client describes how they work
once, in Veda, and from then on the AI suggests the right next step to the right person at the right
moment, following that client's way of working.

## The three building blocks (p. 1)

| Building block | What it is | Example | Who manages it |
|---|---|---|---|
| **Project Team Roles** | The part someone plays on a project. **Not** the same as their access level. | PM, Business Analyst, Designer | Company admins keep the list; project admins assign roles to team members |
| **Policies** | A reusable rule: what should happen, optionally when, and the activities it involves. | "New Project Kickoff": when a project starts, schedule the kickoff meeting and post an update to Slack | Company admins |
| **Methodologies** | The client's way of running a project, as ordered stages. Each stage holds activities and can include policies. | "Enterprise Delivery Framework": Initiation → Discovery and Scope → Delivery → … | Company admins build them in a visual editor (Figma) |

An **activity** is one piece of expected work ("send the kickoff email", "create the RAID record"). It
says which roles it is for and, optionally, which Veda agent helps with it.

## How it works on a real project (pp. 1–2)
1. A company admin sets up roles, policies and a methodology, then publishes it. Edits stay in a draft
   until published. *Whether publishing changes projects already using the methodology is still being decided* (→ OQ #9).
2. A project admin picks the methodology in Project Settings and gives team members their roles.
3. As the project moves along (a call happens, a deadline nears, project health turns red), the AI team's
   **orchestrator** reads the methodology and policies and decides what should happen next.
4. It sends a **suggestion** to the people in the right role, e.g. "Post a Slack update about scope sign-off" to the PM.
5. A person reviews it and applies or dismisses it. Applying runs the action (e.g. posts the message).
6. When the AI thinks the project is ready for the next stage, it suggests the move; a project admin
   confirms; the Overview stage card shows the new stage. *Whether stages are in the first version is still being decided.*

**People stay in control.** The AI only suggests; it never changes a project on its own in the first version.

## Who does what (p. 2)

| Team | Responsible for |
|---|---|
| **Uinno** (backend and frontend) | Storing roles, policies and methodologies; admin screens and the editor; Project Settings; delivering suggestions to the right people; the agreed contract with the AI team |
| **AI team** | Deciding when something should happen, interpreting policies, writing the suggestions, and later reading methodologies out of uploaded documents |

## What ships when (p. 2)

| | Included |
|---|---|
| **First version** | Role library and role assignment; policy library; methodology editor; choosing a methodology for a project; suggestions sent to the right roles |
| **Possibly in first version** (still being refined) | Publish and versions; document upload (stored only); project's current stage and the stage card; full change history (audit); the connection the AI team uses to read this data and send suggestions |
| **Later** | Tracking which activities are done; recording why a required step was skipped; adherence score; letting the AI act without approval; AI-proposed changes to methodologies; reading methodologies from documents; Suggestion Sets |

## Where to read more (p. 3)
Architecture (→ files 01–10) · AI team contract (→ 11) · Open questions (→ 12) · Future phase (→ 13).
