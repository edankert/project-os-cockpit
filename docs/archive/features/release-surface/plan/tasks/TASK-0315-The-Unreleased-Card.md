---
type: "[[task]]"
id: TASK-0315
aliases: ["TASK-0315"]
title: "UNRELEASED · N — done features since the last release"
status: done
phase: "[[PHASE-026-The-Returning-Human]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[FEAT-0072-The-Release-Surface]]"]
parent: "[[FEAT-0072-The-Release-Surface]]"
effort: S
depends: []
blocks: []
related: []
tests: []
---

# UNRELEASED · N

## Definition of Done

- Record card counting features done since the newest REL note (or ever, when none); rows navigate; absent when zero.

## Done — 2026-08-11

`Unreleased · 70` on the overview's record column, above the corpus counts.

**Membership decides it, not dates.** A feature is shipped when a `[[release]]` note names it in `features:`. Deriving "since the last release" from timestamps would need a completion date features do not carry — `updated:` moves for a typo — and would mis-sort anything closed out late.

**Only a `released` release ships anything.** `draft` is *"prepared and verified, not yet live"*, so drafting must not empty the card; a count that fell to zero when somebody wrote a plan would assert the release had happened. Today that is the whole story: REL-0001 is `draft` and names 27 features, so **nothing has shipped and all 70 done features are unreleased** — the card reads *"70 features done, none in a shipped release yet"* rather than naming a release that does not exist.

Absent at zero, as specified. Rows navigate — verified by clicking FEAT-0001 through to `features/render-server/FEAT-0001-Render-Server.md`.

**The branch this repo cannot exercise was the one that broke.** No release here has ever been `released`, so the subtract-shipped path never runs against the live corpus — and the first version called an `extract_ids` that `cockpit.py` does not import. It would have raised `NameError` the moment anybody shipped, and every test against the real corpus would have stayed green. `tests/test_unreleased.py` builds a released release explicitly: 70 → 59 when REL-0001 is marked `released`, dropping exactly the 11 done features it names.
