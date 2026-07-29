---
type: "[[test]]"
id: TST-0022
aliases: ["TST-0022"]
title: "Surface ownership — every moved type is reachable, and Library is reduced"
status: passing
phase: "[[PHASE-010-Surface-Ownership]]"
owner: user:edwin
created: 2026-07-29
updated: 2026-07-29
source: ["[[PHASE-010-Surface-Ownership]]"]
verifies: ["[[REQ-0025-No-Type-Loses-Its-Surface]]", "[[FEAT-0046-Plans-On-The-Feature]]", "[[FEAT-0047-Risks-On-The-Issues-Surface]]", "[[FEAT-0048-Changes-On-The-Overview]]", "[[FEAT-0049-Review-Desk-As-Record]]", "[[FEAT-0050-Library-Reduction]]", "[[ISS-0062-Most-Plans-Are-Invisible]]", "[[ISS-0063-Dead-Stat-Tiles]]"]
path: "tests/test_surface_ownership.py"
command: ".venv/bin/pytest tests/test_surface_ownership.py -q"
last_run: "2026-07-29T21:13Z"
exit_code: 0

---

# TST-0022 — Surface ownership

## Intent

[[REQ-0025]] gates [[FEAT-0050]] on a property nothing else in the toolchain checks: that removing a type's Library group did not make the type unreachable. The validator reads the corpus, not the UI. The existing payload tests assert group *shape*, which passes just as happily on a group that lost its contents.

This suite asserts reachability by **count against the corpus**, so a regression that silently drops rows fails rather than rendering a plausible shorter list — the exact failure mode of [[ISS-0062]], where a type-based lookup returned 14 convincing rows out of 33.

## Coverage

1. **Plans, by count.** Every feature's `plan/PLAN.md` resolves through the path-based lookup. Asserted against a **filesystem glob**, not a literal: the corpus was 33 plans / 14 typed when [[ISS-0062]] was filed and is 38 / 19 now that this phase added five features, so a frozen number would fail on the next feature created. A revert to `notes_by_type("plan")` fails here because the typed subset is smaller than the glob.
2. **Plans, untyped.** A feature whose plan has no frontmatter still yields a child row. Asserted on a real untyped plan from the corpus, not a fixture.
3. **Risks in the Issues mode.** The `issues` payload contains every `[[risk]]` record, and a corpus with no risks produces a payload byte-identical to the pre-change one.
4. **Changes payload.** `changes_payload` bucket labels and membership match what `_changes_subgroups` produced under Library, and the recent split does not lose an item — the union of recent + buckets equals the CHG record set.
5. **Tests register.** `review_queue_payload["registers"]["tests"]` has one entry per `[[test]]` note (22 here), while the `runs` queue group stays gated to manual-and-`ready` (1 here). Both counts are asserted so collapsing one into the other fails.
6. **Reviewed register.** One entry per note carrying a **non-empty** `review_verdict` (62 here), sorted most-recent-first. Two edge cases asserted in opposite directions: a note with a verdict but no `review_date` still lists (sorted last); a note declaring `review_verdict: ""` does **not** (six such notes exist, and counting them would report 68 reviewed where 62 were reviewed).
7. **Library reduction.** `nav_payload(mode="library")` group keys are a subset of `{pinned, docs-tree}`.
8. **Auto-discovery survives.** A synthetic corpus with ≥5 notes of an unknown type still gets its `by-type:` group — the reduction removes canonical-type groups, not the discovery mechanism.
9. **Workflows in the tree.** The Docs-tree group contains a `workflows` folder holding the WF notes.
10. **Desk section naming and order** ([[ISS-0064]]). Exactly one section heading is `Reviewed`, and the pane order is Queue → Reviewed → Tests. Source-level, because both registers are appended at the tail of one function — the order is positional, so the next append in the obvious place reshuffles it with nothing failing. That is how ISS-0064 happened.
11. **The advisory tally is gone** ([[ADR-0007]] settled, [[TASK-0247]]). Renderer *and* stylesheet, since a stylesheet keeping selectors for a deleted block is how CSS rots. Deliberately does **not** assert the payload: `outcomes`/`reviewed` still ship and `test_queue_reports_the_advisory_phase_tally` still guards them — the recording survives the surface.

## Evidence

```
$ .venv/bin/pytest tests/test_surface_ownership.py -q
20 passed in 0.25s

$ .venv/bin/pytest -q
552 passed, 1 skipped in 75.04s
```

Payloads additionally confirmed end to end over HTTP against this repo's own corpus, on a sidecar started from `src/`:

```
$ curl -s localhost:8899/api/cockpit/nav?mode=library   → groups: ['docs-tree']
$ curl -s localhost:8899/api/cockpit/nav?mode=issues    → critical 1, high 15, medium 39, low 8,
                                                          risk:high 1, risk:medium 2, risk:low 1
$ curl -s localhost:8899/api/cockpit/nav?mode=features  → 38 plan child rows
$ curl -s localhost:8899/api/cockpit/changes            → total 96, recent 4, buckets partition the rest
$ curl -s localhost:8899/api/cockpit/review-queue       → tests register 22, reviewed register 62, queue 2
```

## Adequacy

The count assertions are equalities against the live corpus rather than non-emptiness checks, which is what distinguishes this from the payload-shape tests already in `test_cockpit.py`. A group that renders but has lost half its rows passes those and fails these.

**Not covered by the automated suite:** that a rendered payload is actually *visible* in the UI. These tests assert the data reaches the payload; whether the renderer draws it is the manual pass below, and **both cockpit reachability bugs in PHASE-009 were renderer-side with correct payloads**.

The renderer is covered here only by `tsc` and by two source-parsing assertions (the stat-tile destinations). Neither runs the DOM. A tile that is built and never appended, a register appended to a detached node, a row whose click handler never fires — every one of those passes everything automated in this suite. The 2026-07-29 manual run bears that out: it found a layout defect (`Changes97`) that every automated assertion passed over.

**Still not covered, even after the manual run:** visual appearance beyond the one measured layout property. The pass asserted structure and geometry over CDP — element presence, counts, computed `display`, click destinations — not that the tile *looks* right. That remains a human judgement.

## Steps

Run against a restarted app on 2026-07-29 — see `## Runs`. The first attempt that day was abandoned: the shell command meant to launch a throwaway Electron instance failed (`timeout` is not present on macOS), so the CDP session attached to **Edwin's own running app** instead of a new one. Its sidecars had been up since 10:44 and served pre-change code, which is why the Changes tile read as absent. That window's `sidecarBaseUrl` and route were altered and then restored; the run was stopped rather than continued against a live instance, and the app was restarted before the real pass.

One thing that first attempt established by accident and worth keeping: against an **older sidecar with no `/api/cockpit/changes`**, the tile removes itself rather than rendering an empty box — TASK-0240's degradation requirement, observed rather than assumed.

1. Open the Features mode. Pick a feature whose plan has no frontmatter (e.g. `agent-verbs`). Confirm the plan row appears under it and opens.
2. Open the Issues mode. Confirm the four RISK notes appear, grouped by severity, distinguishable from issues.
3. On the overview, click the Risks tile — confirm it navigates to Issues. Click the Tests tile — confirm it navigates to `~review`.
4. On the overview, find the Changes tile. Confirm recent changes are visible and an older bucket opens.
5. Open `~review` with an empty queue. Confirm the Tests and Reviewed registers are both present and populated.
6. Open the Library mode. Confirm it shows Pinned and the Docs tree, that `workflows/` is in the tree, and that the pane is not empty.
7. Still on `~review`: read the left pane top to bottom. Confirm the order is Queue → Reviewed → Tests, that **no two sections share a heading word**, and that no outcomes/tally block remains. Added after [[ISS-0064]] — step 5 checked both registers existed and was blind to what they were called or where they sat.

## Runs

### 2026-07-29 — PASS (6/6), driven over CDP against a restarted app

Sidecar `127.0.0.1:8765` from a clean restart; renderer from `dist/` at 18:47.

1. **Plan rows** — PASS. 38 `plan/PLAN.md` child rows across the Features mode, including untyped ones (`features/agent-verbs/`, `features/agent-hooks/`, `features/task-dispatch/` all present with no `data-status`). With Edwin's hide-completed setting on, 6 remain visible — `done` plans hide like any other completed item, which is correct rather than a miss. Child-toggle labels read `1 requirement`, `plan`, `1 requirement · plan`.
2. **Risks in Issues** — PASS. Groups `Risks · high` / `Risks · medium` / `Risks · low`, 4 risk rows, each carrying `data-type=risk` so the shield icon distinguishes them from issues.
3. **Tile click-through** — PASS. Risks tile → `issues`; Tests tile → `~review`. Tile strip reports `Features → · Tasks → · Reqs (dead) · Tests → · Issues → · Risks →`, with Reqs deliberately inert.
4. **Changes tile** — PASS. Present in the history band between Activity and Commits. 5 recent rows expanded, 3 collapsed top-level buckets (`Last week · 24`, `Earlier this month · 20`, `May 2026 · 48`), the May bucket nesting its own week sub-buckets.
5. **Desk registers** — PASS. `Tests · 22/22` (22 rows) and `Reviewed · 62` (62 rows), both rendered beneath the queue.
6. **Library** — PASS. `Docs tree` only, containing `reference/`, `references/` and `workflows/`.

**One defect found and fixed during the run.** The Changes tile's count rendered as `Changes97` — glued to the title, because tile `h3`s are `display: block` and the count's `margin-left: auto` does nothing there. Fixed with `.ov-changes h3 { display: flex; align-items: baseline; }`; re-verified `display: flex` and the count flush to the right edge (0px offset). This is exactly the class of defect the automated suite cannot see, which is why these steps exist.

**A second defect this run missed, and Edwin caught by looking** ([[ISS-0064]]). Step 5 asserted both registers were present and populated, which they were — and said nothing about their order, or about the pre-existing ADR-0007 tally a few rows above the Reviewed register also being headed `Reviewed`, with a different count (1 against 62). The step was derived from [[REQ-0025]], which asks whether a type is *reachable*; by that measure nothing was wrong. Legibility was never in its scope, and a checklist inherits the blind spots of the requirement it came from.

### 2026-07-29 (second run) — desk section order, PASS

After [[TASK-0246]]. Direct children of `.review-queue` in document order: `HEADING: Queue`, `meta review-queue-empty`, `TALLY: Outcomes · 1`, `REGISTER: Reviewed · 62`, `REGISTER: Tests · 22/22`. `reviewedHeadingCount: 1`.

### 2026-07-29 (third run) — tally removed, PASS

After [[TASK-0247]] and [[ADR-0007]] settling. `tallyPresent: false`; pane headings are exactly `Queue`, `Reviewed · 62`, `Tests · 22/22`.

Worth noting against the second run: the `Outcomes` rename was the right fix for the collision and the wrong fix for the underlying problem. Renaming made two sections legible; asking what the section was *for* made one of them unnecessary. Edwin's question ("there is nothing for me to select there") got further than the bug report did.
