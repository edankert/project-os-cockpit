---
type: "[[feature]]"
id: FEAT-0105
aliases: ["FEAT-0105"]
title: "There is always a release — work accumulates into the next one from the moment the last shipped, and the gate asks when you say you are preparing to ship"
status: done
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
reviewed_by: "model:claude-opus-5"
review_date: 2026-08-16
review_verdict: changes-requested
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["Edwin 2026-08-16: 'maybe it would be good to always have a release prepared when starting new developments after a previous release, i.e. there is always a release and any features/phases/issues etc … committed/pushed after the previous release are naturally part of the new release'"]
goal: "Make the next release a place work arrives in rather than a note somebody remembers to write: everything unshipped belongs to it from the moment the last one shipped, it stays silent while it accumulates, and the acceptance gate starts asking only when a person says they intend to ship."
requirements: []
tasks: ["[[TASK-0438-Preparing-Is-A-Flag-Not-A-Status]]", "[[TASK-0439-The-Next-Release-Accumulates]]"]
design: ""
release: ""
depends: ["[[FEAT-0102-Publication-Becomes-A-View]]"]
related: ["[[ADR-0028-Work-Has-Three-Phases]]", "[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]", "[[FEAT-0072]]", "[[FEAT-0104-The-Suite-Is-The-Surface]]"]
tests: ["[[TST-0032-The-Release-Accumulates-Then-Asks]]"]
---

# There is always a release

## Three states, and why the middle one exists

```
open        accumulating — everything unshipped belongs to it, gate silent
  ↓         a person says "I intend to ship this"
preparing   the gate asks: N checks stand between this and shipping
  ↓         walked, or excepted with justification
released    shipped — exceptions expire, the next one opens
```

**The middle state is the whole design.** If a release is always open and the gate asks whenever one exists, the gate asks **forever** — which is precisely the self-re-arming badge [[ADR-0027]] excludes staleness for and that [[PHASE-034]] exists to avoid producing. Being *open* and being *prepared for ship* are different facts, and only the second is a debt.

## `preparing` is a flag, not a status

`STATUSES.md` allows a release `draft`, `released`, `reverted`, and it is **template-owned** — adding vocabulary there would report as divergence on the next sync.

So `preparing:` is frontmatter on a `draft` release, which is the pattern [[DES-0006]] already established and which `obligations.py` already documents for features: *"`acceptance: requested` in frontmatter, not a status."* One precedent, applied again, and no template change.

## The open release has no note

Edwin pictured `REL-0013 (open)` as a note. It is **derived** instead, and the reason is that the computation already exists: `unreleased_payload` ([[FEAT-0072]]) answers *done but not shipped* — a feature is shipped when a `released` note names it in `features:`.

So the open release needs no list of its own, and a note is written only when somebody declares `preparing` with a version. Three reasons:

1. **No auto-written notes.** `CLAUDE.md`: *"issues appearing without anyone asking is a worse failure than one occasionally missed."*
2. **A note with no version and no content is a placeholder** that would need cleaning up on every project that never ships.
3. **No dates are needed.** Edwin described membership as *"committed/pushed after the previous release"*, which is date-based — and [[FEAT-0072]] deliberately rejected dates, because features carry no completion timestamp and `updated:` moves for a typo. *Unshipped* already means *no released note names it*, which gives the same set without a clock.

## Acceptance criteria

- [x] Publication always shows the next release, with what has accumulated since the last shipped one, **without any note existing** — the `release-next` group is first and present with no note behind it
- [x] Membership is derived from `unreleased_payload`, not from dates and not from a hand-kept list — read by `release_payload`; `test_contents_come_from_the_existing_computation` pins the keys after a first draft invented `rows`/`latest` and silently reported nothing
- [~] `Prepare ▸` writes a `REL-*` at `draft` with a version and `preparing:` set — reconciled by [[FEAT-0107]] — the control moved to the release page's version field, because a navigator row popping a dialog was the wrong shape AND the dialog was dead (ISS-0176). The write is unchanged
- [x] The acceptance gate asks **only** when a release is `preparing` — never merely because one is open — `test_preparing_is_what_makes_the_gate_ask` and `test_an_open_release_asks_nothing`
- [x] A repo with no release in preparation owes nothing for its suite, however many checks are unchecked — asserted; your-trainer owed nothing for 60 unchecked rows until 2.1.7 was declared
- [~] On ship, `features:` is frozen into the note from the derived set, and exceptions reset — **partially** — the frozen set is READ (`contents.kind == 'frozen'`) and rendered. Writing it at ship is not built; twelve releases have filled `features:` by hand and nothing asked them to
- [x] The version guards from [[TASK-0431]] still hold: at or below the newest `released` is refused, and two in preparation are refused — `test_a_version_at_or_below_the_newest_released_is_refused`, `test_a_second_open_release_is_refused`
- [x] No write path widened; declaring still publishes nothing ([[ADR-0022]]) — suite green at 1388; the loopback enumeration covers both new routes


## Criteria resolved 2026-08-16, after the fact

This feature reached `done` with **0 of 8 criteria ticked**, and an independent review found it. So did [[FEAT-0106]], at 0 of 9. Nothing catches this: the validator has `REQ-BOXES` for requirements and `PHASE-BOXES` for phases and no equivalent for a feature's own acceptance criteria, and both features carry `requirements: []` so `FEATURE-REQ` is inert too.

Two are reconciled rather than ticked. The `Prepare ▸` control moved to the release page ([[FEAT-0107]]), and freezing `features:` at ship is read but not written — recorded as owed rather than claimed.
