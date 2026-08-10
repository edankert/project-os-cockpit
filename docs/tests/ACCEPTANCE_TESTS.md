---
type: "[[reference]]"
id: ACCEPTANCE-TESTS
aliases: ["ACCEPTANCE-TESTS"]
title: "Acceptance test suite"
status: active
owner: user:edwin
created: 2026-08-10
updated: 2026-08-10
scope: tests
related: ["[[TASK-0373-The-Tier-Suite-And-The-Release-Gate]]", "[[FEAT-0086-Tests-Becomes-A-View]]", "[[REL-0001-The-Human-Has-Levers]]"]
---

# Acceptance Test Suite: project-os-cockpit

## Test Tiers

- **Tier 1 — Feature Tests (permanent):** verify core user-facing capabilities; one or more per feature; never removed.
- **Tier 2 — Regression Tests (permanent):** guard previously-broken behavior; each references the `ISS-*` that created it.
- **Tier 3 — Verification Tests (temporary):** one-time checks for a specific build or fix; promoted to Tier 2 or removed after a verified release.

Full tier rules: `tools/instructions/TESTING.md`.

## Rules

1. New feature implemented → add Tier 1 test(s) under the feature's area heading.
2. Bug fixed → add a Tier 2 test referencing the `ISS-*`.
3. Any code change unchecks overlapping Tier 1/Tier 2 tests (mark for re-run).
4. A release is blocked while any Tier 1/Tier 2 test is unchecked (exceptions must be documented in the release note).
5. Tier 3 tests are removed or promoted after each verified release.

## Why this document exists, and what it is not

The tier contract has existed since the template was written. **No repo had ever instantiated it** — measured 2026-08-10 across the twelve the cockpit renders: 92 `TST-*` notes between them, zero tier classification, and a release gate that had never been able to fire. This is the first instance, created by [[TASK-0373]].

**It is not a second test register.** `TST-*` notes are formal specifications with frontmatter, procedure and evidence; 22 of this repo's 23 are automated pytest modules that CI runs on every commit. This document is the **manual acceptance checklist** — the things a person has to look at, which no pytest run can answer. `TESTING.md` is explicit that both coexist, and that is the reason the two populations are grouped separately in the Tests view rather than merged into one list.

**Tier lives here, not in `TST-*` frontmatter.** A `tier:` field on the notes was the obvious alternative and is wrong twice over: it would tier the wrong objects (Tier 1 is *"one or more per feature"* covering user-visible behaviour, while a `TST-*` is usually one pytest module covering an internal contract), and it would leave the checkbox — which is what the gate actually reads — with nowhere to live. Recorded here because the alternative is the one a reader will think of first.

**Every box below is unchecked, deliberately.** Nothing here has been walked yet. That is the honest starting state for a checklist created today, and it means the gate on [[REL-0001]] is firing rather than passing vacuously — which is the first time that has been true in this project.

---

# Tier 1 — Feature Tests

## 1.1 Render server and the browser front door ([[FEAT-0001]], [[FEAT-0002]], [[FEAT-0006]])

- [ ] **Serve a repo:** `python -m project_os_cockpit <repo>/docs` and open the printed URL. Expect: the three-pane cockpit, README rendered, wikilinks resolving to other notes.
- [ ] **Live reload:** edit a note on disk while the page is open. Expect: the centre pane updates without a manual refresh.
- [ ] **A tablet can read it:** open the same URL from another device on the Wi-Fi. Expect: the page renders; every write control is either absent or refuses (the render port binds `0.0.0.0`, writes are loopback-only).

## 1.2 Desktop shell and workspaces ([[FEAT-0007]], [[FEAT-0009]], [[FEAT-0016]])

- [ ] **Discovery:** launch the shell with no arguments. Expect: every `SNAPSHOT.yaml`-bearing repo under `~/Dev/repos/` appears in the rail, each with its own sidecar.
- [ ] **Switching:** click between two workspaces. Expect: nav, centre and right pane all follow; per-workspace state (nav mode, pins, follow mode) is remembered separately.

## 1.3 The navigator ([[FEAT-0010]], [[FEAT-0046]], [[FEAT-0058]], [[FEAT-0085]])

- [ ] **Features is the structural tree:** open Features. Expect: phase → feature → its requirements, then its plan, then its tasks; finished groups collapsed beneath the live ones.
- [ ] **Nothing is unreachable:** pick a task, a plan and a requirement at random from `docs/` and find each in the tree. Expect: all three, without using the find bar.
- [ ] **Issues opens on what is owed:** open Issues. Expect: `Needs triage` first when anything is at `triage`, absent when nothing is, severity cards beneath.

## 1.4 The note page ([[FEAT-0011]], [[FEAT-0060]])

- [ ] **Actuators:** open a note whose status is a human-owned intake state (a `draft` requirement, a `proposed` ADR). Expect: an `Owed` row of buttons naming that type's own vocabulary; a note with nothing owed shows no row at all.
- [ ] **A criterion ticks with evidence:** tick an acceptance criterion from the note page. Expect: the box fills, the line gains `— evidence: … (actor, date)`, and the rest of the file is untouched.

## 1.5 The overview ([[FEAT-0017]], [[FEAT-0023]], [[FEAT-0040]], [[FEAT-0048]])

- [ ] **Every stat tile lands somewhere true:** click each of Features, Tasks, Tests, Issues, Risks. Expect: each opens a view that contains that type. (Reqs is inert by decision.)
- [ ] **Changes read on the overview:** recent change notes in the history band, older ones collapsed by month and still openable.

## 1.6 Design and the constraints view ([[FEAT-0042]], [[FEAT-0043]], [[FEAT-0044]])

- [ ] **The brief opens first:** open Design. Expect: the project's own brief, not a file list.
- [ ] **A design renders its artifact:** open a `DES-*` with a committed artifact. Expect: it renders in the frame, in this project's own tokens, in both light and dark.

## 1.7 Tests ([[FEAT-0086]])

- [ ] **The view lists what we verify:** open Tests. Expect: every `TST-*` in the corpus, grouped by state, each row naming the feature it verifies; both `docs/tests/` and `plan/tests/` present with no sign of the split.
- [ ] **A manual run works end to end:** open a manual test, press `Run ▸`, walk the steps with evidence, record. Expect: the note gains `status`, `last_run` and a `## Runs` entry, and nothing else changes.
- [ ] **A failing run offers its issue:** fail a step and record. Expect: an offer naming the step, quoting what the note expected and what you observed; nothing is filed until you press Enter in the capture box.

## 1.8 Issues and capture ([[FEAT-0061]])

- [ ] **⌘N from anywhere:** press ⌘N on any note, type a sentence, Enter. Expect: an `ISS-*` at `triage`, linked to the note you were on, appearing in the triage tray without a reload.

## 1.9 The embedded terminal ([[FEAT-0003]], [[FEAT-0037]])

- [ ] **A real shell:** open the terminal, run an agent CLI, complete a turn. Expect: it behaves like a terminal — resize, scrollback, copy and paste from the context menu.
- [ ] **Loopback only:** confirm the terminal endpoint refuses a connection from another device on the network.

## 1.10 Agents and sessions ([[FEAT-0019]], [[FEAT-0020]], [[FEAT-0032]])

- [ ] **A session is visible while it runs:** start an agent in the terminal. Expect: the workspace dot tracks its state, the activity strip fills, and the notes it touches show the agent chip.
- [ ] **The fleet view:** open `~agents`. Expect: sessions across every workspace, with cost and queue state.

## 1.11 Verification health and the fleet ([[FEAT-0018]], [[FEAT-0028]])

- [ ] **The validator's answer is on screen:** expect the health surface to agree with `bash tools/scripts/validate-docs.sh` run in a terminal — same error count, same notes named.
- [ ] **Fleet roll-up:** expect a validator badge per discovered repo, and a push action that refuses a deploy remote.

## 1.12 History ([[FEAT-0052]], [[FEAT-0053]])

- [ ] **State changes are the rows:** open History. Expect: status transitions as rows with commits as dividers, and the contribution grid clicking through to a day.

## 1.13 Close-out ([[FEAT-0055]])

- [ ] **Close-out commits its own work:** run `tools/scripts/close-out-commit.sh <paths…>`. Expect: named paths staged, dirty files elsewhere reported and left alone, the message built from the staged ids, the pre-commit hook run, and no push.

## 1.14 Obligations ([[FEAT-0089]])

- [ ] **The badges cover everything owed:** expect a count on each view button, the sum equal to the registry's total, and no badge at all where nothing is owed.

---

# Tier 2 — Regression Tests

## 2.1 Plans are visible ([[ISS-0062]])

- [ ] **Every plan on disk is reachable:** count `docs/features/*/plan/PLAN.md` on disk and find each one in the Features tree, including the three with no frontmatter. Expect: equal counts. (19 of 33 were invisible when this was filed, because the lookup used the note *type* and most plans do not declare one.)

## 2.2 Stat tiles are not dead ends ([[ISS-0063]])

- [ ] **Every tile navigates, and lands where its type lives:** click all five live tiles. Expect: no tile that looks clickable and does nothing, and no tile that opens a pane its type has left. (Risks pointed at Issues for a commit after risks moved to the constraints view.)

## 2.3 One status vocabulary ([[ISS-0023]], [[ISS-0024]])

- [ ] **`implemented` reads as done everywhere:** expect an `implemented` requirement to render in the done band, rank as completed in the fold, and count as done in the progress boxes — on both front doors.

## 2.4 One home per obligation ([[ISS-0068]])

- [ ] **Nothing is listed twice on one screen:** expect no item to appear both in a triage tray and a severity card, both in a badge count and a second list, or both in a group and a roll-up of the same group.

## 2.5 A settled verdict is not owed ([[ISS-0121]])

- [ ] **`changes-requested` on finished work reads settled:** expect a note carrying `review_verdict: changes-requested` whose status is terminal to appear as settled, not as owed. (All ten rows the desk headed *Changes requested* were terminal; the real count was zero.)

## 2.6 Writes are loopback-only ([[ISS-0129]])

- [ ] **Every mutation endpoint refuses a non-loopback caller:** enumerate the POST dispatch table and confirm each handler consults the guard — including `/api/notes/check-toggle`, which wrote note body text for any peer that could reach the `0.0.0.0` render port.

## 2.7 The record column has its own source ([[ISS-0065]])

- [ ] **Decisions survive a nav-mode change:** expect the overview's Decisions card to list every ADR, sourced from its own endpoint rather than harvested from a navigator that a later change can empty.

---

# Tier 3 — Verification Tests (current build)

<!-- Temporary. Promote to Tier 2 or remove after the next verified release. -->

## 3.1 The Tests view renders ([[TASK-0371]])

- [ ] **Look at the pane:** the payload and the renderer source are both asserted; nobody has looked at the result. Expect: `Stale · over 90 days · 2` above `Verified · 21`, each row naming its feature, no settled divider. *Temporary: this is a one-time visual confirmation of a new surface; the grouping itself is covered by `tests/test_tests_view.py`.*

## 3.2 The run route migrated ([[TASK-0372]])

- [ ] **An old deep link still lands:** navigate to `~review/<TST>/run` from history. Expect: the Tests view runner, with the URL replaced rather than stacked. *Temporary: promote to Tier 2 if anyone reports a stranded link.*

---

# Test Execution Notes

Prerequisites: a built desktop shell (`npm run build` in `desktop/`), at least two discovered workspaces so the fleet and switching checks mean something, and an agent CLI on `PATH` for §1.9 and §1.10.

The automated half runs as `.venv/bin/pytest -q` and is not repeated here — this document is only the part a person has to look at.

# Release History

<!-- One line per verified release: version, date, exceptions granted. -->
