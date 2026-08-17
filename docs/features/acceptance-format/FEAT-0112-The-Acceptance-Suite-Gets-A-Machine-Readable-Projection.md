---
type: "[[feature]]"
id: FEAT-0112
aliases: ["FEAT-0112"]
title: "The acceptance suite gets a machine-readable projection — Markdown stays the source of truth and the structure is derived, not authored"
status: backlog
owner: user:edwin
created: 2026-08-17
updated: "2026-08-17"
phase: "[[PHASE-999-Future]]"
source: ["Edwin 2026-08-17: 'I am now considering is this the right format (.md) for the acceptance tests and maybe we need a different format acceptance-tests.json and simply create a tool to manage these and then for a release store the results in an .md file??? review this and suggest if this makes sense and pros and cons'"]
goal: "Give the acceptance suite the machine-readable half it lacks without giving up the human-readable half it has: expose the structure `acceptance.parse` already computes as a derived projection the tool never authors, and keep `ACCEPTANCE_TESTS.md` as the source of truth."
requirements: []
tasks: []
design: ""
release: ""
depends: []
related: ["[[ADR-0029-The-Acceptance-Mark-Vocabulary-Is-Minimals]]", "[[ADR-0009-The-Principal-Is-A-Role]]", "[[FEAT-0104-The-Suite-Is-The-Surface]]", "[[FEAT-0108-The-Gate-Is-A-Delta-Not-A-Census]]", "[[ISS-0175-The-Nth-Checkbox-Is-Not-The-Nth-Task-Line]]", "[[PHASE-999-Future]]"]
tests: []
---

# The acceptance suite gets a machine-readable projection

## Where the question came from

Edwin asked it after five rounds of defects on the acceptance mark control, and the honest first thing to say is that **almost none of that pain was the format**. Of the defects in [[ISS-0185]] through [[ISS-0189]], the tally is:

| defect | format's fault? |
| --- | --- |
| control boxed inside tasklist's leftover indicator | no — my DOM handling |
| cycle wrote three states to reach one | no — my interaction design |
| decorative glyphs, cramped dialog | no — my styling |
| scroll lost, three separate paths | no — the renderer's re-render paths |
| a refusal swallowed silently | no — `postJson` throws and I read a return value |
| `pymdownx.tasklist` knows only two marks | **yes** — fixed, [[FEAT-0104]] |
| 37 rows absorbed by lazy continuation | **yes** — named, [[TASK-0457]] |

Two of seven, both now fixed and guarded. A format change proposed on the strength of the other five would be treating the wrong cause.

That said, the two that *were* the format are the two that took the longest to find, and the question deserves an answer on its merits rather than a deflection.

## What JSON would genuinely buy

- **The lazy-continuation class disappears.** A row is an object; there is no Markdown rule about blank lines that can make one vanish from the rendered document while a line-based reader still counts it ([[ISS-0175]]).
- **No vocabulary negotiation with an extension.** `[!]` and `[?]` are marks a Markdown extension has never heard of, which is why the row draws its own control at all ([[ADR-0029]]).
- **Addressing by id instead of position.** `Item.number` is section-and-ordinal and shifts when a section is inserted; an explicit `id` never does.
- **Structure instead of grammar.** `tier`, `refs`, `burden`, and the whole `**Verdict DATE** — reason` convention become fields rather than regexes. The `RE-RUN (TASK-####: …)` annotations stop being prose that 54 rows happen to share.
- **Per-check history becomes possible.** Markdown holds one verdict per row legibly and cannot hold five.

## What it would cost, and why that decides it

**The suite stops being readable and editable everywhere it currently is** — Obsidian, a diff, a phone, a text editor, `grep`. That is not a nice-to-have here; it is the premise of the whole record. [[ADR-0009]] makes notes the authored source of state, and the project's own instructions say the Markdown notes are *"the durable human-readable record"*.

A JSON file the tool owns inverts that relationship: **you would need the tool to change a check.** Every other artefact in twelve repos can be edited by a person with any editor, and the acceptance suite would become the exception.

Concretely, measured 2026-08-17 — and these are a living corpus, so they are a snapshot rather than a constant:

- **1,011 acceptance rows across the fleet**, 851 already ticked, would need migrating
- the git history of *who ticked what and when* is currently reviewable line by line; it becomes a diff of reordered JSON
- `../your-trainer`'s suite carries prose that is genuinely prose — *"(partially automated: `ScannerModalTest` covers the device-wide tier resolution; Play Billing purchase + tier-flip state stays manual.)"* — appearing on 181 rows. That is documentation, and it survives a schema only as a string field nobody formats

## The recommendation: derive, do not author

Keep `ACCEPTANCE_TESTS.md` as the source of truth and **expose the structure as a projection the tool computes and never writes**.

`acceptance.parse` already produces exactly this: every row with its tier, section, ordinal, mark, refs, `rerun` annotation and text. Nothing needs designing; it needs a route.

```
GET /api/cockpit/acceptance.json
{ "rel": "tests/ACCEPTANCE_TESTS.md",
  "rows": [ { "number": "1.1.1", "name": "First Run", "tier": 1,
              "mark": "x", "gating": true, "refs": ["FEAT-0002"],
              "rerun": "", "text": "…" }, … ] }
```

**Why this is the right shape rather than a compromise:**

- the machine-readable half arrives for scripts, a future run-plan generator, the [[FEAT-0108]] delta, and anything outside this repo that wants to read a gate
- the human-readable half is untouched, so nothing migrates and no history is lost
- a projection **cannot drift from its source**, because it has no independent existence. A second authored file always can, and this project has paid for that twice — `docs/PHASES.md` against `SNAPSHOT.yaml`, and the suite's own hand-maintained `## Manual Test Environment Breakdown` claiming ≈120 rows against a file holding 579
- it is roughly a day's work, against a migration measured in weeks

**On the second half of Edwin's question** — *"for a release store the results in an .md file"* — that already exists and is the part worth keeping either way: `tests_verified:` on the release note, graded by [[FEAT-0109]], plus the delta against the shipped tag. A release already records what it stood behind.

## Acceptance criteria

- [ ] A derived JSON projection of the suite is served, computed from `acceptance.parse` with **no second parser**
- [ ] Nothing writes it. It has no path on disk, so it cannot be edited, cannot go stale, and cannot be committed out of step with its source
- [ ] Every field it exposes is one the parser already computes — a field that needs new prose conventions is a change to the *document*, decided separately
- [ ] The projection and the rendered document agree on the number of rows, asserted rather than assumed ([[ISS-0175]]'s lesson: two readers of one file must be reconciled or one must refuse)
- [ ] A repo with no suite yields a stated absence, not an empty array that reads as *nothing to do*

## The condition that would change the answer

**Per-check history.** If it becomes worth knowing every verdict a check has ever carried — walked and passed in v2.0.5, excused in v2.1.0, failed in v2.1.6 — Markdown cannot hold that on one line and stay readable, and no projection helps because the data would not exist in the source.

At that point JSON stops being a preference and becomes the only option, and the trade above genuinely reverses. **That is the thing to watch for**, and it is a decision that would want an [[ADR]] rather than a feature note, because it overturns [[ADR-0009]]'s premise for one corpus.

Two weaker signals worth noticing in the same direction: if the `RE-RUN` annotations ever need a *date* as well as a task, or if burden tags are wanted on the gating suite rather than on one `TST-*` ([[TASK-0449]], cancelled for exactly that absence), the prose is being asked to carry structure and the balance is shifting.

## What this note deliberately does not do

It does not decide the wholesale move. The analysis says the derived projection is the better first step by a wide margin, and if the answer ever changes it changes on evidence — per-check history being wanted — rather than on the memory of a bad afternoon with a renderer.
