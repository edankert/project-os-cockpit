---
type: "[[adr]]"
id: ADR-0040
aliases: ["ADR-0040"]
title: "A release selects its features, and a check that cannot be walked is excused rather than deselected — scope narrows what a gate is about, it never launders what a gate found"
status: "proposed"
owner: user:edwin
created: 2026-08-20
updated: "2026-08-20"
decision_date: ""
phase: "[[PHASE-999-Future]]"
source: ["Edwin 2026-08-20: 'If we can just have all the features available for the release in the release document at first with a checkbox all new features checked and then the user can uncheck/check some of them if they need to be included, the acceptance tests for the release can then be adjusted based on the selected features.'", "Edwin 2026-08-20: 'on the pre-existing open tsts, yes these are open because of multiple of reasons and happy to re-evaluate them for each release to see if we can resolve them but more than likely they will stay open for this release as well. (for instance I don't have the hardware to test those corner cases)'"]
supersedes: ""
superseded: ""
related: ["[[FEAT-0142-A-Release-Says-What-Is-In-It]]", "[[ADR-0035-A-Release-Page-Reports-It-Does-Not-Record]]", "[[ADR-0037-A-Verdict-Is-An-Event]]", "[[ISS-0206-A-Check-Cannot-Belong-To-A-Release]]", "[[ISS-0209-The-Acceptance-Gate-Reaches-No-Fleet-Repo]]", "[[ISS-0210-The-Release-Page-Offers-Sixty-Live-Marks]]"]
tags: [release, acceptance, conventions]
decided_option: ""
---

# A release selects its features, and excuses its checks

## Status

**Proposed**, 2026-08-20. Nothing in [[FEAT-0142]] is built until this is accepted — the same gate [[ADR-0030]], [[ADR-0034]] and [[ADR-0037]] each used.

## Context

A release page today has two modes and no third: **derived** (every feature unshipped since the last tag — nobody chose) and **frozen** (the note's `features:` list, written by hand, recorded only at the moment it ships). There is no act of deciding what a release contains, so *"what is in it"* is a statement about **when work finished**.

Edwin's proposal supplies the act: the release document lists every available feature as a checkbox, new ones checked, and a person unchecks what is not going in. Then — *"the acceptance tests for the release can then be adjusted based on the selected features."*

The first half is uncontroversial and fits the grain of the system. The second half is a rule about what a gate means, and the measurements say it is a much larger lever than it looks.

### What the gate is actually made of, measured 2026-08-20 on `your-trainer` at HEAD

59 blocking checks:

| composition | count |
|---|---|
| cover at least one `FEAT` | 39 |
| cover only `ISS` or `PHASE` | 18 |
| carry no `covers:` at all | 2 |

The 39 land on **nine features**, and the distribution is the whole of the argument:

| | features | checks |
|---|---|---|
| in this release's derived contents (32 features) | 3 | 3 |
| **not in it** | **6** | **36** |

`FEAT-0074` alone carries 20 and is still `backlog` — its twenty are also the entire `quiet` bucket. `FEAT-0051` shipped in **REL-0006**. Five of the six out-of-scope carriers are `done`.

So **36 of the 39 feature-covering blockers are about work this release does not contain**, and a naive reading of *adjust the tests to the selection* takes the gate from 59 to about 23 on the first render, before anybody unchecks a box.

### Why those 36 are not a scoping problem

Edwin, on the same day: *"these are open because of multiple of reasons and happy to re-evaluate them for each release to see if we can resolve them but more than likely they will stay open for this release as well. (for instance I don't have the hardware to test those corner cases)"*

That is not *"this feature is not in the release"*. It is *"this check cannot be walked this cycle, and ask me again next cycle"* — and [[ADR-0037]] already built exactly that, in the outcome vocabulary the ledger enforces:

| outcome | clears the gate | survives the seal | means |
|---|---|---|---|
| `na` | yes | **yes** | a statement about the check and the platform — *there is no such surface here*. Re-asking it every release is the maintained-matrix failure ADR-0037 exists to remove. |
| `excused` | yes | **no** | *not done this cycle, by decision*. Owed again after the seal. |
| `blocked` | **no** | — | could not be run right now, by accident. Blocks deliberately: *"a gate that clears because the rig was down clears on whatever happens to be broken that day."* |

`excused` **is** the re-evaluate-every-release behaviour, by construction: it expires when the ledger seals, so next release asks again. No hardware for a corner case is `excused` if it may be obtainable, `na` if the check can never apply to this platform, and `blocked` only while something is temporarily broken.

**The mechanism exists and is unused where it is needed.** `your-trainer` has **no `docs/releases/ledgers/` directory at all** — not one recorded verdict — and its checks still carry `mark:` in frontmatter. So the 59 are unticked notes rather than considered decisions, and the tool has never been given the chance to hold the reason. That is [[ISS-0209]]'s subject arriving from a new direction.

### The hazard this decision exists to prevent

[[ISS-0210]] found sixty live mark buttons on the page whose entire purpose is to report a release was blocked — *the fastest way to unblock a release was to tick the things saying it was blocked*. [[ADR-0035]] removed them.

*"Uncheck the feature whose checks are red"* is the same shape in different clothing. Deselecting a feature is a legitimate release-management act; deselecting one **because its checks are failing** is the ISS-0210 defect with an extra step, and nothing in the mechanism distinguishes the two from the outside.

## Options

1. **Selection scopes the gate: only checks covering a selected feature gate.** Simple to state. Takes `your-trainer` to ~23 immediately and permanently retires the 36 from view — including the `chronic` bucket, whose entire purpose is to keep *unticked at baseline and shipped anyway* visible.
2. **Deselection subtracts: all checks gate except those covering only deselected features.** Nothing changes until somebody unchecks. Preserves the chronic population. Requires saying what happens to a check covering both a selected and a deselected feature.
3. **Selection scopes nothing; the gate is unchanged and excuses do all the work.** Honest and already built — but leaves the release page unable to express *this feature is not in this release*, which is the thing that was asked for.

## Decision

**Option 2, with three constraints.**

### 1. Selection subtracts; it never divides

Every check gates **except** one whose `covers:` names only deselected features. A check covering a selected feature **and** a deselected one still gates — any selected subject is enough. A check with no `covers:`, or covering only an `ISS`, `REQ` or `PHASE`, is **untouched by selection**: 20 of `your-trainer`'s 59 are in that class today, and they are exactly the repo-wide and regression obligations that no feature list can speak for.

The default is therefore *the gate you have now*. Selection can only ever remove, one feature at a time, by an act somebody performed.

### 2. A check that cannot be walked is `excused`, not deselected

Scope and excuse answer different questions, and the split is enforced rather than advised:

- **Scope** answers *is this feature part of this release* — a fact about the release, recorded in the release document.
- **`excused`** answers *can this check be walked this cycle* — a fact about the check, the platform and the release, recorded as a ledger event that expires at the seal.

The hardware case is `excused`. Using deselection for it would put a fact about a check into a list about features, lose the reason, and — because scope has no expiry — make it permanent, which is precisely the property `excused` was designed not to have.

### 3. Removing a check from the gate is never silent

- An exclusion **carries a reason**, on the same rule that already makes everything but `pass` carry its justification in the ledger.
- The release page says **`N features held back · M checks no longer gating`**. A number that fell must say why it fell; a smaller total on its own is indistinguishable from progress.
- **`chronic` continues to count the excluded.** Its subject is *what has been shipped over, repeatedly*, and a check that stopped gating because its feature was deselected is the single most important member of that set, not an exempt one. Excluded checks stop **blocking**; they do not stop being **counted**.

### 4. Deselecting a `done` feature does not remove it from the build

Five of the six out-of-scope gate-carriers on `your-trainer` are `done` — merged, and in the binary regardless of what any list says. So a checkbox controls what a release is **accountable for**, never what it **contains**, and dropping the checks of a `done` feature means shipping unverified code rather than deferring code.

That is a legitimate decision — behind a flag, or as accepted risk — and an illegitimate convenience. The page must therefore distinguish **held for a later release** from **in the build, not verified here**, and the second must read as the liability it is.

## Alternatives considered

**Let selection scope the gate outright (option 1).** Rejected on the measurement: it would remove 36 of 39 feature-covering blockers on the first repo to adopt it, none of them by anybody's decision, and it would empty `chronic` — the one bucket built to make long-carried debt impossible to ignore.

**Do nothing and rely on `excused` alone (option 3).** Rejected because it answers a different question than the one asked. It is, however, the *right* answer for the 36, and this decision keeps it.

## Consequences

- `FEAT-0142` gains a mechanism and loses its two open questions; it stays parked until this is accepted.
- **`excused` becomes load-bearing, and nothing in the fleet has ever written one.** A repo with no ledger cannot excuse anything, so the re-evaluate-each-release loop Edwin described cannot run in `your-trainer` today. That is a prerequisite, and it belongs to [[ISS-0209]] rather than to this decision.
- `ISS-0206` — *a check cannot belong to a release* — is answered from the other end: it still does not, and it does not need to. A check belongs to its subject; a release selects subjects; the gate follows.
- Nothing here weakens [[ADR-0035]]. Scope is written to the release note, which is the release's own record. No write path to a check appears on the release page.
