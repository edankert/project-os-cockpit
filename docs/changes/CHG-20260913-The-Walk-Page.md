---
type: "[[change]]"
id: CHG-20260913
aliases: ["CHG-20260913"]
title: "The publication view hands the owed checks over as a procedure: ~walk/<platform>, the survey first, the steps on the row"
date: 2026-09-13
status: merged
owner: user:edwin
phase: "[[PHASE-043-The-Walk-Page]]"
source: ["[[FEAT-0149-The-Walk-Page]]"]
implements: ["[[FEAT-0149-The-Walk-Page]]"]
tasks: ["[[TASK-0618-The-Walk-Payload]]", "[[TASK-0619-The-Walk-Page]]", "[[TASK-0620-The-Survey]]", "[[TASK-0621-The-Release-Rung-Points-At-The-Walk]]"]
related: ["[[TST-0088-The-Walk-Page-Hands-Over-The-Owed-Checks]]", "[[ISS-0303-The-Walk-Sheet-Lists-Retired-Checks]]", "[[ISS-0304-The-Walk-Order-Reader-Splits-Inside-A-Quoted-String]]", "[[ADR-0041-A-Release-May-Settle-A-Check-It-May-Never-Pass-One]]"]
tags: [change, acceptance, publication, walk]
---

# The walk page

## What changed

A person preparing a release can now open **one page that says what to do and in what order**. `~walk/<platform>` lists every check the platform still owes, grouped into the sittings the repo authored, with each check's setup, steps and expected result printed on its row, and a tick that writes the ledger.

Before this, the cockpit had a list and a ledger and nothing in between. `~checks` said what was owed, ordered by section, area and id. The release page said whether the gate held. Neither said which check to walk first, what had to be on the bench before a sitting started, or which screens the release had changed. Edwin, 2026-09-13: *"I find it increasingly difficult to understand what steps need to be done to satisfy the outstanding acceptance tests"*, and *"one thing I notice the tests do not suggest me doing is to look at the changed screens at all, which is strange because that is normally the first step I would do."*

## What a walker sees

**The survey comes first** — the surfaces whose owed checks a change reopened, each naming the change or task that reopened them, and quoting that note's `## Acceptance checks reopened` section where it has one. On `your-trainer`'s open Android release that is six surfaces and eleven tasks. Nothing was filed to produce it: an invalidation has been a dated ledger event since [[ADR-0037-A-Verdict-Is-An-Event]], and every check names its surface in `area:`. Close-out is asked no new question, which is what [[ADR-0036-The-Sweep-Is-Withdrawn]] required of any replacement.

**Then the sittings**, in the order the repo wrote down. A sitting is a group of checks that share one product state; it prints the state it needs and what must be on the bench, both verbatim. Those were the two facts the hand-written run plan carried and no note could.

**Then the rows.** Each is the `~checks` row with the check's Setup, Steps and Expect underneath. A note that states none of them says so and offers the note, which is the ordinary case today: 53 of `your-trainer`'s 61 owed rows have no `## Steps` heading, and the row prints their prose rather than nothing.

**A tick is the mark dialog the walker already knows**, and it writes one ledger event through `/api/notes/mark-check` — the same path `~checks` uses. There is no second store and no second write path. The row keeps its place, the page keeps its scroll, and nothing reorders: *"a list that reorders itself as you tick things is one you lose your place in"* ([[TASK-0556-Incomplete-First]]).

## How to reach it

- The publication ladder's release rung gains a **Walk them** row saying how many are owed on which platform, while a release is in preparation.
- The release page's gate section gains **`N owed · walk them`**. It still records nothing itself: the settle marks stay `na`, `excused` and `blocked` ([[ADR-0035-A-Release-Page-Reports-It-Does-Not-Record]], [[ADR-0041-A-Release-May-Settle-A-Check-It-May-Never-Pass-One]]).
- The checks page header gains **walk them** while its payload names a platform.

Each appears only when there is a walk to do. A link to an empty walk is the permanent blank button [[FEAT-0102-Publication-Becomes-A-View]] records the rule about twice.

## The order is authored, never inferred

The sittings come from `docs/tests/acceptance/WALK.md` in the browsed repo, one `### ` heading per sitting with a fenced `yaml` block naming what it claims (`surfaces`, `checks`) and what it needs (`state`, `bench`). A repo without one gets one sitting per surface in id order, a banner saying the order is nobody's, and a link to the template.

Nothing is inferred from prose. [[TASK-0449-Order-The-Walk-By-Its-Setup-Cost]] was cancelled for trying, on a measurement of six false positives out of six, and its guard rails outlive it: **no time estimates anywhere**, in the payload or on the page. Counts of rows are the only numbers. Two tests hold that — one walks the payload for a banned key, one reads the whole of every walk function in the renderer.

This repo now has a walk order of its own, `docs/tests/acceptance/WALK.md`: five sittings that climb from the server in a browser, through the shell and one workspace, to the rows that write.

## Where the rules live

The ordering, placement and survey rules are the template's, stated once upstream in `tools/instructions/TESTING.md`, "The walk". `tools/scripts/walk-sheet.py` implements them, and the sidecar **bundles that file verbatim** as `src/project_os_cockpit/walk_sheet_bundled.py` — the way it bundles the validator — with a test asserting the two are byte-identical. The cockpit supplies three things the generator cannot have and which are lookups rather than rules: its own check scoping, its ledger reader, and the note index that turns an id into a title.

That arrangement earned its keep immediately. Running the generator beside the page on this repo produced two answers that differed, and both differences were real:

- **[[ISS-0303-The-Walk-Sheet-Lists-Retired-Checks]]** — the sheet listed a check at `status: retired`, so the one thing retiring does was undone by the document a walker reads. The page never did, because it reads the cockpit's suite.
- **[[ISS-0304-The-Walk-Order-Reader-Splits-Inside-A-Quoted-String]]** — a comma inside a quoted `bench:` entry split it in two, so *"a second device on the same Wi-Fi, for the tablet row"* printed as a bench item that is not a thing.

**Both were fixed upstream the same day and re-synced here**, and the bundled copy was re-copied with them. Neither was patched locally, which is the part that matters: a local patch to a bundled copy is how one rule becomes two. The sheet and the page now agree at 3 owed rows on this repo's `macos` ledger. The correction is much larger on `your-trainer`, which carries 217 retired checks: its Android sheet goes from 61 owed rows to 39, the number the page has reported all along.

*(Written first as "neither is patched here", present tense, while both were still open. Corrected after independent review, 2026-09-13.)*

## Paths and contracts

- **New route:** `GET /api/cockpit/walk?platform=<p>&release=<id>`. One platform only. `all` is refused with a 400, and so is a name no ledger carries — a walk read from no ledger reads no verdicts and reports **every check in the repo** as owed, which upstream measured at 545 rows on `your-trainer` for a single typo. An absent platform resolves to the open release's, the rule `/api/cockpit/acceptance` already uses.
- **New page:** `~walk`, `~walk/<platform>`, inside the publication nav mode, which now owns it — so reselecting Publication mid-walk does not evict the walker.
- **New per-workspace key:** `cockpit:walk-place:<workspaceId>`.
- **New file read in a consumer repo:** `docs/tests/acceptance/WALK.md`. Optional; its absence is a labelled fallback, never an error.
- **Changed signature:** `buildCheckRow` takes a fourth argument, which page repaints after a mark. It defaults to the checks page's writer, so every existing caller behaves exactly as before.

## What the walk of it found

`TST-0088` was walked on the live harness against a sidecar on this repo, and the walk found two defects in the page before it shipped. A check that **does** state its Setup was told *"Setup: not stated"* — one sentence had been used for *the note has none* and for *this is not the heading that was asked for*. And the row a walker had just ticked kept its `[ ]` glyph, *nobody has walked this*, because a `pass` removes the check from the owed set and so from the payload the page fetches next. Both are fixed, and both now have a test that fails without the fix.

Its verdict is `partial` rather than `pass`, and the reason says why: step 13 walks this register's own detection commands, and the rows for the walk are written in this same commit.
