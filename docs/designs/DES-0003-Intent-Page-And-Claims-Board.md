---
type: "[[design]]"
id: DES-0003
aliases: ["DES-0003"]
title: "The intent page and the claims board"
role: proposal
status: draft
owner: user:edwin
created: 2026-07-29
updated: 2026-07-29
source: ["design conversation 2026-07-29", "[[project-os-dev#ADR-0014]]"]
asset: ""
implements: []
supersedes: ""
superseded_by: ""
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[DES-0002-Cockpit-Design-System]]", "[[FEAT-0045-Project-Inbox]]", "[[FEAT-0041-Review-Desk]]"]
---

# The intent page and the claims board

## Problem

The cockpit renders **notes**. Open `TASK-0234` and you get a Markdown file, rendered well, with a nav tree beside it.

But a task is not a document. `TASK-0234` is: a note, ~300 lines of renderer diff, three tests that were mutation-checked against it, two defects it uncovered along the way ([[ISS-0060-Electron-32-Removed-File-Path|ISS-0060]], [[ISS-0061-Screenshot-Permission-Error-Was-Unreadable|ISS-0061]]), four rebuild cycles, the agent that wrote it, and seven DoD claims of which some are still supported at `HEAD` and some may not be. The cockpit shows one of those things and makes you reconstruct the rest by navigating between notes and dropping to a terminal for `git log`.

The second, sharper problem: **the cockpit cannot tell a true claim from a false one, and neither can anything else.** On 2026-07-28 six claims in this repo asserted more than the code did — a scrub whose test name promised a field it never touched, a 25 MB limit a shared reader capped at 2 MB, and *"thumbnail rendered"* for images a Content-Security-Policy had blocked from ever painting. Every one was caught by a person reading carefully. The surface that renders those claims rendered all of them identically, in the same grey, with the same tick.

## Approach

Two surfaces, one substrate.

### The intent page

The unit of the UI becomes the **intent**, not the file. One page per `TASK-*` / `ISS-*` / `FEAT-*` / `REQ-*`, assembling:

- the note prose (what exists today, unchanged — it is the best part)
- **claims** — each DoD line with its evidence token, its strength, and whether it still holds at the current revision
- **code** — the commits and the files this intent produced, at the *structural* level (which modules and symbols appeared, moved, vanished) with the text diff available but collapsed
- **verification** — the tests linked to it, and their last real run
- **lineage** — what it came from, what it produced, what it broke
- **provenance** — agent, model, review passes, and what was verified in which runtime

The design bet is that the diff belongs *at the bottom of the page*, not at the centre of the product. The evidence from this repo supports it: the CSP fix was one line in a meta tag and meant "no inbox image has ever rendered"; the change beside it was ~300 lines of renderer and meant "the inbox is a tray now". Sorting by line count sorts by nothing.

### The claims board

A single view over every ticked claim in the project, sorted by weakness:

```
STALE      TASK-0234  "thumbnails paint"          runtime:@85fa50c  · 3 commits behind
ASSERTED   TASK-0229  "the ledger route dedupes"  asserted:         · never checked
TEST       TASK-0233  "a dropped file lands"      test:@2011420     · current
MUTATION   TASK-0233  "loopback-only"             mutation:@2011420 · current
```

This is the surface the cockpit does not have and cannot fake: it requires [[project-os-dev#ADR-0014]] upstream, because without typed tokens every row would read the same. With them it is close to free — the tokens are already in the notes, and the cockpit already parses notes.

## Why the cockpit, and not a hosted service

`ADR-0015` (project-os-dev) parks the hosted product deliberately. These two surfaces do **not** depend on it. They work on one machine, over local repos, against notes that are already there — which makes them the cheap test of the expensive thesis. If rendering intents instead of notes does not make reviewing agent work faster on eleven local repos, a server will not change that.

The existing pieces are further along than they look: the review desk already models "things awaiting a human decision", the dispatch ledger already models transient runtime state ([[ADR-0007]]), the design bench already renders a non-note artifact in the stage, and `~inbox/<name>` already demonstrates a virtual route rendering something that is not a Markdown file.

## Constraints

- **Notes stay the source of state** ([[ADR-0009]]). The intent page is a *projection*; nothing on it is authored there except through the existing guarded write-back.
- **No new status values.** Staleness is a computed finding, not a state ([[ADR-0008]], [[ADR-0010]]).
- **Degrade honestly.** Against a repo that has not adopted typed evidence, every claim reads `asserted:` and the board says so, rather than hiding the column and implying the claims are fine.
- **The stage is the viewer.** Same split the inbox settled on in `TASK-0234`: narrow panes list, the centre shows the thing at a size you can actually read.

## Open questions

1. **Where does the intent page live** — a new nav mode, or does opening any note with an ID simply become the intent page? The second is more honest (there is no separate "note view" worth keeping) and much more disruptive.
2. **How is blast radius computed** for staleness — the files the claim's commit touched, or something declared? This is the same open question as `FEAT-0020` upstream and should be answered once, there.
3. **Does the claims board belong per-project or fleet-wide?** Fleet-wide is where the value is (eleven repos, one queue), but the cockpit's whole model is one active workspace at a time.
4. **Is `role: proposal` the right register** for this note, or should it wait for an `asset:` — a rendered mock — before it can be argued with properly? `DES-0002` earns its keep by *being* the artifact it describes; this one currently describes surfaces nobody can see.
