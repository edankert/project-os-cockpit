---
type: "[[reference]]"
title: "Intent — what this project is for, what it must never become, and the taste its record has paid for"
status: draft
owner: user:edwin
created: 2026-08-11
updated: 2026-08-11
source: ["[[REL-0001-The-Human-Has-Levers]]", "[[ADR-0009-The-Principal-Is-A-Role]]", "[[project-os-dev#ADR-0013]]", "[[ADR-0020-Obligations-Live-With-Their-Subject]]", "[[DES-0002]]", "[[DES-0003-Intent-Page-And-Claims-Board]]", "[[PHASE-022]]"]
---

# Intent

**Status: `draft`.** Only an `approved` charter is usable ([[FEAT-0077]]), and approving it is the principal's — [[REQ-0026]]'s human-owned territory. Until then no delegated judgment may cite it.

**Every clause below is quoted or derived from the record, not invented.** [[TASK-0333]]'s rule: *"first draft dispatched from the corpus's ADRs, phase close-outs and design-system notes, never invented."* Each carries where it came from, so a reader can check the source rather than trust the summary — and so anything that drifted from its origin is findable.

## What this is for

The record already states it, in [[REL-0001]]'s own words, assembled there from [[ADR-0009]], [[ADR-0020]], [[DES-0003]] and [[PHASE-028]]:

> The cockpit is how a person governs a project they did not write. It must not be able to say something false about that project without saying so — and everything it shows as owed must be theirs to discharge.

Three clauses, and each has a body of work behind it:

1. **Governs a project they did not write** — the reader is a principal, not an author. They arrive at a corpus somebody else (often an agent) produced, and the tool's job is to make it answerable.
2. **Must not say something false without saying so** — surfaces that assert are held to it. Measured examples the record already paid for: ten `Changes requested` rows that were all terminal ([[ISS-0121]]), a badge total that disagreed with its parts, a Tests view showing the features tree for 33 hours because a stale process fell back silently.
3. **Everything owed must be theirs to discharge** — an obligation the reader cannot act on is a nag. [[ADR-0020]] put obligations with their subjects for this reason.

## What it must never become

- **A tool that grants itself authority.** [[ADR-0009]]: the principal is a role, and a delegate is *always distinguishable* ([[REQ-0029]] — *"delegation without distinguishability is impersonation"*). Concretely: no self-approval, no answering its own permission prompt ([[ISS-0094]]), no rewinding its own turns ([[FEAT-0078]]), no pushing ([[ADR-0022]]).
- **A tool whose defaults grant.** Absence must mean *no*: no delegation policy means no worker ([[FEAT-0075]]), an unknown escalation kind alarms rather than passing ([[FEAT-0076]]), an unreadable status is unapproved. A default that grants authority is authority nobody granted.
- **An editor.** [[ISS-0096]]: *"the cockpit is not an editor, and the persona is not reading implementations."* Shape first; contents on request.
- **A second place to look.** [[ISS-0068]] forbids two lists of one obligation. One item may have two addresses (the Library and Intent both show a standing document) — but not two lists of the same thing owed.
- **A gate that becomes a rubber stamp.** Where the judgment cannot be automated, the check **warns** and never blocks — `ACCEPT-STALE`, `DESIGN-GATE`, independent review. A blocking gate on an unautomatable judgment gets cleared to unblock the build rather than because somebody looked.

## The taste its record has paid for

These are not preferences; each cost a correction, and the correction is cited.

- **One border per object.** Eighteen frames read as clutter, eighteen hairlines read as a table ([[ISS-0088]]/[[ISS-0089]]). Reversed once more on 2026-08-11 when the count changed — the rule survives, the count is the input.
- **Fold on volume, never on meaning.** A fold shortens a view; it may never empty one ([[TASK-0270]]).
- **A name is not a label.** `TASKS` is scaffolding you read past — faint and uppercase is right. `PHASE-007 · Agent instrumentation` **is the content**, and the same treatment renders the thing you opened the pane to find as though it were furniture ([[ISS-0089]]).
- **Absent beats zero.** A permanent `· 0` is a thing readers learn to stop seeing. This surface has been taught it twice.
- **Say what the pane shows and the shortest path to having some.** Every empty state, one voice ([[TASK-0318]]).
- **A number says what it counts.** `81 change notes to review`, not `81 items here need a person` ([[ISS-0133]]).
- **Evidence names its witness.** [[REQ-0028]], written because PHASE-022 ran twelve acceptance rounds whose only record was a chat transcript.
- **Never floats to the wrong spot.** An anchor that cannot be re-found says it is lost; a comment silently re-attached to different content is worse than one that admits it ([[FEAT-0069]]).

## How to judge against this

A delegated acceptance run ([[FEAT-0063]], [[TASK-0334]]) reads this charter, judges the feature's criteria, and stamps a witness naming both this charter's sha and the delegation's. **Amending this note changes its sha**, so a judgment cannot silently inherit a standard that moved.

Where a criterion demands using the product, use it. Twelve PHASE-022 corrections argue that reading a diff is not the same as looking at the result — which is also why this project's own sessions kept finding defects by opening the app rather than by running the suite.
