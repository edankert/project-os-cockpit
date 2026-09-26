---
type: "[[task]]"
id: TASK-0313
aliases: ["TASK-0313"]
title: "The workspace card says since-when and how-many"
status: done
phase: "[[PHASE-026-The-Returning-Human]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-10
source: ["[[FEAT-0071-Since-You-Looked]]"]
parent: "[[FEAT-0071-Since-You-Looked]]"
effort: S
depends: ["[[TASK-0312]]"]
blocks: []
related: []
tests: []
---

# The workspace card says since-when and how-many

## Definition of Done

- One line per workspace: `since Thu · 14 transitions · 2 need you`, derived from history_payload and the registers; NEEDS-YOU cards widen to anything-waiting.

## Groundwork landed 2026-08-10 — the payload, not the surface

`GET /api/cockpit/digest` exists: `cockpit.digest_payload()` returns the transitions since the watermark and the items that need a human, split — because that split is the point. **This task's renderer is not built**, and the task stays `backlog`.

Two decisions already taken in the payload, so the surface inherits rather than re-decides them:

- **It errs toward re-showing, never hiding.** `history_payload` reports commit dates at *day* granularity while the watermark is a timestamp, so a same-day commit cannot be ordered against a same-day watermark. The watermark's own day is therefore **included**: re-showing what was seen is corrected by reading, whereas hiding what came after catching up is invisible. Same asymmetry as the epoch default.
- **`computed_at` is what a `Caught up` should record**, not the moment the button is pressed — otherwise anything landing while the human reads is silently marked seen.

`needs_you` is deduplicated: an item owed for two reasons is still one thing to do — the rule the triage tray had to learn the hard way.

**Not a second obligation vocabulary.** `DIGEST_NEEDS_YOU` is one list in one module with one consumer, and it reads from [[FEAT-0089]]'s registry once that lands. If it outlives the registry it becomes exactly the drift [[ISS-0023]] describes.

## The registry swap landed 2026-08-10 — still not the surface

`DIGEST_NEEDS_YOU` is gone. `digest_payload` reads [[FEAT-0089]]'s registry through `_owed_flag`, which is what the paragraph above said to do once the registry existed.

**Measured, and the drift was already real:** the hand-written list held six types and omitted `change` (81 owed here) and `feature` (`acceptance: requested`), and had no way to express the `test` predicate's manual-only clause. A digest built from it would have told the returning human that 8 things needed them while the badges said 96. `test_the_digest_and_the_badges_count_the_same_things` now pins the two together — allowing exactly one gap, the standing documents, whose subject is a manifest entry rather than a note.

Every `needs_you` row also carries its `owed_verb` now, so the band this task builds can say *what* is owed rather than only that something is.

## Done 2026-08-10

### "One line per workspace" looked impossible, and the reason was a discarded value

The DoD says one line per workspace, and the digest is served per-sidecar — so the obvious reading was that only the active workspace could be asked, and the criterion would have to be narrowed to *"a line for the workspace we can reach"*.

It did not. The shell spawns one sidecar per workspace and announces each with a `ready` event carrying `{workspaceId, url}`. The renderer's handler opened with `if (p.workspaceId !== activeId) return;` — **throwing away every URL but the active one**, at the top of the function, before doing anything with it. Keeping them in a map is two lines, and the criterion is met as written.

Worth recording because the shape recurs: the surface looked impossible, the data was already arriving, and the guard that discarded it was written for a different purpose (don't re-point the *active* sidecar) and quietly took the rest with it.

### The cards knew only about terminals, which was DES-0008's actual complaint

`attentionEntries()` read `agentStates` and nothing else, so its kinds were `needs-input` and `waiting` — both properties of a **terminal**. A repo with eleven things needing a human and a quiet terminal rendered identically to a repo with nothing to do.

A third kind, `record`, now appears for a workspace whose digest reports owed work. Three placement decisions, each with a reason:

- **It rides on the existing card when one is there.** A workspace with both a waiting agent and owed work gets its since-line appended, not a second row — one thing as two rows on one screen is the failure [[ISS-0068]] names.
- **It sorts last.** `needs-input` → `waiting` → `record`: act now, then review, then read. Nothing in a record card arrived while you were watching, so it is never urgent.
- **It opens the overview, not the terminal.** The terminal is where the agent is; the record is read on the overview, where [[TASK-0314]]'s band sits. Sending every card to the terminal is precisely what made them terminal-only.

### The line itself

`since Thu · 14 transitions · 2 need you`, and **absent rather than zero** — a permanent `0 transitions · 0 need you` under every workspace is the shape of thing a reader learns to stop seeing. An unset watermark reads `since first run`, not `since 1 Jan 1970`: the epoch is the payload's way of saying *show everything*, not a date anyone wants to read.

Pulled, never pushed ([[DES-0008]]'s Out of Scope), and rate-limited to once every 30 seconds — `refreshAttention` is called from a dozen places as a plain redraw, so the fetch behind it must not run every time. It repaints through `paintAttention` rather than calling itself, so a slow sidecar cannot start a loop.

### Verification

`927 passed, 2 skipped`; `validate-docs: OK`; `tsc --noEmit` clean; `dist/` rebuilt. Source-level assertions, which [[TST-0022]] already discloses as the limit for a renderer with no exports and no DOM harness — the payload half is behavioural, in `test_watermark.py` and `test_the_digest_and_the_badges_count_the_same_things`.

Adequacy by mutation:

| mutation | killed by |
|---|---|
| keep the URL *after* the active-workspace guard returns | `test_every_workspaces_sidecar_url_is_kept` |
| drop the `carded` check, so a workspace can hold two cards | `test_the_landing_cards_widened_past_waiting_terminals` |
