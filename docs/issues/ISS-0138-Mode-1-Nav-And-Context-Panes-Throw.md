---
type: "[[issue]]"
id: ISS-0138
aliases: ["ISS-0138"]
title: "The browser front door's nav and context panes are dead — cockpit.js calls groupIsSettled four times and nothing defines it there, so both panes render an error box"
status: fixed
severity: high
owner: user:edwin
created: 2026-08-11
updated: 2026-08-11
phase: "[[PHASE-029-One-Tool-Two-Front-Doors]]"
features: ["[[FEAT-0083-The-Browser-Cockpit-Answers-Questions]]", "[[FEAT-0084-One-View-Vocabulary]]"]
tasks: []
related: ["[[ADR-0010-What-The-Browser-Cockpit-Is-For]]", "[[REQ-0032-Two-Front-Doors-Agree-Or-Differ-On-The-Record]]", "[[ADR-0021]]", "[[REL-0001-The-Human-Has-Levers]]"]
tags: [issue, mode-1, drift]
---

# Mode 1's nav and context panes throw on every page

## What happens

Open any note in the browser front door — `python -m project_os_cockpit <repo>/docs`, then any `/docs/**.md`. The centre pane renders correctly. **Both side panes render an error box instead of content:**

```
Nav failed: groupIsSettled is not defined
Context failed: groupIsSettled is not defined
```

Observed 2026-08-11 on `/docs/requirements/REQ-0007-Auto-Index.md` while walking [[REL-0001]]'s check *"`implemented` reads as done everywhere — on both front doors"*. The check cannot be walked in mode 1 because mode 1 has no nav pane to read.

## Cause — and it is the twin problem again

`groupIsSettled` is called **four times** in `src/project_os_cockpit/static/cockpit.js` (lines 1534, 1595, 1681, 1901) and **defined nowhere in that file**.

It is defined in `desktop/src/renderer/completed-work.ts`. Mode 3 gets it because the Electron shell loads `completed-work.js` as a **plain script publishing a global**, before `renderer.js` — the same "plain-script module TypeScript cannot see through" arrangement the renderer's own comments describe.

Mode 1 loads exactly one script: `templates.py` emits `<script src="/_static/cockpit.js" defer>`. There is no `completed-work.js` on that page and no equivalent function in `cockpit.js`. So the call is a `ReferenceError` the first time either pane renders a group — which is every page.

**This is the hand-written-twin drift [[ADR-0021]] proposes to end**, in its most expensive form yet: not two surfaces disagreeing, one surface simply not running. The three earlier instances were divergence; this one is absence.

## Why `high`

Mode 1 is the LAN reading surface — [[FEAT-0083]]'s whole point is *"a tablet gets the current tool rather than the one that existed before PHASE-008"*. Two of its three panes are dead, and the failure is loud on screen rather than silent, which is the only good thing about it.

It also means **[[REQ-0032]] cannot currently be assessed**: the two front doors cannot be compared on the record when one of them does not render the record.

## Not caught by anything, and that is the finding

`statuses.py` already parses `static/cockpit.js` for the status vocabulary, so mode 1's script *is* read by a test — for its strings, never for whether its identifiers resolve. Nothing loads that file in a JS runtime, so a missing global is invisible to the suite. The 1137-test suite is green with this shipped.

## Fix, and the trap in it

The narrow fix is to give `cockpit.js` its own `groupIsSettled`, which **adds a fifth hand-copied twin** — the exact debt [[ADR-0021]] exists to stop. The better fix is the shared module that ADR proposes, with mode 1 loading it the same way mode 3 does.

Either way the regression guard is the same and is the part that must not be skipped: **something has to evaluate `cockpit.js` and assert every identifier it calls is reachable.** A static scan for called-but-undefined names in that file would have caught this without a browser.

## Verification

- A test that fails while `cockpit.js` calls a name it cannot resolve.
- Then re-walk this note in mode 1 and confirm all three panes render.

## Fixed — 2026-08-11

`groupIsSettled` is now defined in `cockpit.js`, beside the `completionRank` it calls. Three lines.

**Yes, this is a fifth hand-copied twin, and it is the wrong long-term answer.** [[ADR-0021]] proposes the shared module; that is a decision for the principal and a larger change than a page that does not render can wait for. The function carries a comment saying so, and the file's own header — which said *"the three functions below are its twin"* while the desktop side had four — now says four.

**The guard is the part that matters**, and it is what this note asked for: `tests/test_mode1_identifiers_resolve.py` statically resolves every name `cockpit.js` calls against what it defines plus a list of real browser globals. Deleting `groupIsSettled` again fails two tests and names it in the message. A fourth test asserts all four fold functions exist on **both** front doors, so the next missing twin fails here rather than in someone's browser.

*The guard's own first draft was wrong in an instructive way: it stripped `//` comments before strings, so any string containing `//` left an unpaired quote and prose downstream started parsing as code — it reported `drift`, `events` and `mismatch` as undefined functions. Strings are stripped first now, and the reason is in the test.*

**Verified on the surface:** `/docs/requirements/REQ-0007-Auto-Index.md` in the browser front door renders all three panes — the nav tree with `OPEN · 3` and `COMPLETED · 23`, the note, and a context pane carrying `FEATURES 2 · done`, `CHANGES 1 · merged`, `PHASES 1 · done` — with the validator chip reading `OK`. This also unblocked acceptance check 2.3.1, which asks about both front doors and could not be answered while one of them was dark.
