---
type: "[[feature]]"
id: FEAT-0116
aliases: ["FEAT-0116"]
title: "A release can be finished — Mark released freezes the record behind two refusals, Start shrinks to naming the version, and the page reports what it kept"
status: done
owner: user:edwin
created: 2026-08-17
updated: "2026-08-17"
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
source: ["Edwin 2026-08-17: 'it would however be really good if the releases would capture the test levels/confidence (is this a feature stat) and wether all acceptance tests have been considered'", "Edwin 2026-08-17: 'not sure if the start button should even exist ever'", "Independent functionality review, rounds 1-2, 2026-08-17 — no path from draft to released exists (HUMAN_TRANSITIONS has no release key), and REL-0013 will ship reading 'What shipped — 0 feature(s)'"]
goal: "The release process gets its missing end: Mark released writes status, date and tag, freezes the derived feature list into features:, and refuses while the gate is blocked without written exceptions or while any frozen feature lacks acceptance_impact — naming which. Start survives as exactly one thing, naming the version, scaffolded from the repo's own template. The page reports confidence as a roll-up of check automation, still-owed boxes counted honestly, prose tests_verified rendered as the record it is, and the note itself reachable."
requirements: []
tasks: ["[[TASK-0469-Mark-Released]]", "[[TASK-0470-Name-The-Version]]", "[[TASK-0471-The-Page-Reports-Its-Record]]"]
design: ""
release: ""
depends: ["[[FEAT-0115-The-Sweep-Is-Continuous]]"]
related: ["[[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]]", "[[FEAT-0105-There-Is-Always-A-Release]]", "[[FEAT-0110-Still-Owed-By-A-Shipped-Release]]", "[[ISS-0181-Four-Things-The-Release-Surface-Cannot-Do]]", "[[PHASE-035-Acceptance-Checks-Are-Notes]]"]

---

# A release can be finished

## The gap, measured

The view can begin a release and walk its gate; it cannot finish one. `HUMAN_TRANSITIONS` in `note_writes.py` has no `release` key — [[ISS-0181-Four-Things-The-Release-Surface-Cannot-Do]] item 4, still open, and FEAT-0111 recorded the ship transition as deliberately unplanned. The consequence is already on disk in `your-trainer`: REL-0013 was prepared by the cockpit with `features: []` (the derived list is never frozen), so the moment its status flips to `released` its page will read **"What shipped — 0 feature(s)"**. And `create_release` ignores `docs/__templates__/release.md`, so the note it writes has no Known-issues section and no Post-Release-Actions section — FEAT-0110 reads a heading the tool's own writer never produces.

## Where Edwin's "considered" question landed

*"whether all acceptance tests have been considered … when somebody presses that release start button or maybe even before this"* — before it, always: the sweep is continuous ([[FEAT-0115-The-Sweep-Is-Continuous]]) and **Mark released is where considered-ness is enforced**, because it is the one moment that is both cheap and final. It refuses while any feature being frozen lacks `acceptance_impact`, naming which. Start survives — `preparing:` is what stops the gate obligation asking forever, and the draft note is the hook `tests_verified`, known issues and artifacts hang off — but it shrinks to **Name the version** and stops implying the process begins there. Confidence — *"(is this a feature stat)"* — is **not** a feature stat: it is a check property (`automation:`) rolled up, so the page reports "of the N checks touching what shipped: a automated, b partial, c manual" without authoring the same fact twice.

## Acceptance criteria

- [ ] Mark released writes `status: released`, `date:`, `tag:` and freezes the derived features into `features:` — and REL-0013's "0 features" future is unrepresentable.
- [ ] It refuses on a blocked gate without recorded exceptions, and on any frozen feature missing `acceptance_impact`, naming the features in the refusal.
- [ ] It prints the `git tag`/`git push` commands and runs neither — publishing stays a human act.
- [ ] Name the version scaffolds from `docs/__templates__/release.md` — `previous_release:` set, Known-issues and Post-Release-Actions sections present, filename matching the corpus convention.
- [ ] The page shows: the note as a clickable row, still-owed as `N open · M done · K unknowable` with open first, prose `tests_verified` entries rendered as recorded claims rather than broken links, and the confidence roll-up.

## Closed 2026-08-18

Every task scope-resolved and the linked tests `passing` — the feature had sat at `review` since its build leg finished on 2026-08-17, which is the state PHASE-035 could not close through.

**And it is closed knowing what came next.** [[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]] superseded this phase's own [[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]] one day after it was accepted, so parts of what this feature built have already been replaced. That is not a reason to leave it open: what it delivered was delivered, the record of *why the sibling type existed* is what makes ADR-0031 legible, and a feature left at `review` because its decision moved on is a phase that can never close.
