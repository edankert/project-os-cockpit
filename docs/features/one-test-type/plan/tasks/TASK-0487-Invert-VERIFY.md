---
type: "[[task]]"
id: TASK-0487
aliases: ["TASK-0487"]
title: "Invert VERIFY — resolve a feature's tests from a reverse index over `covers:`"
status: done
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
source: ["[[FEAT-0121-The-Verification-Link-Normalises]]"]
parent: "[[FEAT-0121-The-Verification-Link-Normalises]]"
effort: M
depends: ["[[TASK-0486-Backfill-Covers-On-The-Ten]]"]
blocks: []
related: []
tests: []
---

# Invert VERIFY

`validate-docs.py` reads `entry.get("tests")` and `fm.get("tests")` off the feature and demands each linked test be `passing`. It must instead build a reverse index over every test's `covers:` once at load, and look the feature up in it.

**The validator has no index of its own** — it works from `SNAPSHOT.yaml` plus note frontmatter, so it builds one. The cockpit's `Index` already has a backlink graph and is not available here; the bundled mirror must match the script exactly, as always.

**Prove the inversion is behaviour-preserving before it ships:** run both implementations over the current fleet corpus and assert the same VERIFY violations, note for note. An inversion that changes which violations fire is a silent gate change, and this gate is what keeps a feature from reaching `done` unverified.

Done when: both validators resolve by reverse index, the violation set on the fleet is identical to the field-based one, and twelve repos still validate green.

## Done

`validate-docs.py` builds a `covers_index` once — subject id → the tests naming it — and `linked_tests` reads it. For a **feature** that is the reverse index alone; `task`, `issue` and `requirement` still union their own `tests:`, because those three are not normalised yet (330 live edges fleet-wide against the feature's 62) and silently dropping their links would weaken three gates nobody asked to change.

**The behaviour-preservation proof, and the false pass it started with.** The first comparison reported 56 findings before and 56 after, byte-identical — because *the edit had never been written to disk*: the script that made it raised before its `write_text`. It was caught by asking which single repo's finding **should** have moved and finding it had not. **An inversion that changes which violations fire is a silent gate change**, and one that changes none because it did not run is the same failure wearing a passing result.

Re-run against the real change, across all twelve repos:

- **56 → 55.** `obsidian-supernote-sync` lost its one finding, because its TST-0001 declares `verifies:` and nothing had rewritten it. **A gate that quietly stops firing in a repo nobody is looking at is the worst shape this change could have taken** — so `covers_index` falls back to the forward fields (`features`/`verifies`/`validates`) for a repo that has not consolidated. That is a *rename* transition: every one of those names points test → subject, so it is not a return to the bidirectional pair. The subject's own `tests:` is still not read for a feature.
- **56 → 57 with the fallback.** One finding **added**, in `your-trainer`: *"FEAT-0086 is done but linked test TST-0013 is 'ready', not passing"*. Genuine — TST-0013 names FEAT-0086 among its nine features and has never been walked, while the feature is `done`. The old lookup could not see it because FEAT-0086's `tests:` does not name TST-0013. **The reverse encoding was blind to a real violation, and the inversion is what surfaced it.**

`your-trainer` was already failing (599 errors before this change, 600 after), so nothing green was broken. The delta is one true finding, and no repo lost coverage.
