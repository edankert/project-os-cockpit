---
type: "[[issue]]"
id: ISS-0236
aliases: ["ISS-0236"]
title: "`platform:` on a feature is the same shape `mark:` was on a check — a feature ships on a platform *in a release*, and a scalar cannot hold that"
status: open
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
severity: medium
component: docs
phase: "[[PHASE-999-Future]]"
related: ["[[ADR-0037-A-Verdict-Is-An-Event]]", "[[FEAT-0129-A-Release-Names-Its-Own-Contents]]", "[[DES-0012-Tests-In-Two-Flows]]", "[[FEAT-0130-Surfaces-Are-A-First-Class-Type]]"]
---

# The same defect, one level up

Edwin, 2026-08-19: *"a feature can be (is more than likely) delivered to multiple platforms in the future or am I mistaken?"*

He is not mistaken, and the observation is worth keeping because it names a defect **before** it costs anything.

## Measured, `your-trainer`, 103 features

| `platform:` | count |
| --- | --- |
| `android` | 45 |
| `ios` | 9 |
| blank — cross-platform by the schema | 25 |

**And the nine iOS features are not twins of Android ones.** They are `iOS BLE Hardening`, `iOS Workout Engine Hardening`, `iOS parity — bring the iOS app to full feature parity`. The *porting work* is modelled as its own features.

That works today and it is the `PARITY_MATRIX` shape in another form: a separate artefact whose job is tracking what has crossed. This project already knows how that ends — a maintained matrix rots.

## The defect, stated

**A feature is not *on* a platform. It *ships on* a platform, *in a release*.**

That is `(feature × platform × release)` — the same three-tuple [[ADR-0037]] found a scalar `mark:` could not hold, one level up from the check. `platform: "android"` is a scalar standing in for it, and the moment one feature ships to both platforms it will be wrong in exactly the way 579 acceptance notes were wrong about Android: claiming a fact about the app when it held a fact about one build.

**It is not wrong yet**, because the corpus avoids the case by minting a second feature. It becomes wrong the day parity lands and a new capability is built once and shipped twice.

## The container already exists

A release's `features:` list holds it with the right arity and no new mechanism:

```
REL-0012 (android) → [FEAT-0042, …]
REL-0013 (ios)     → [FEAT-0042, …]
```

*Shipped on both, at these two moments* — said without any field on the feature claiming anything. That is the same move the ledger made: **the fact lives where there is room for it to be true.**

## Suggested direction, not yet a decision

`platform:` on a feature becomes **derived** — the union of the platforms whose releases contain it — rather than authored.

**Do not do this now.** It is a separate decision from [[FEAT-0129]] and this phase has had enough of them; the corpus has not yet produced the case that makes it urgent; and a derived field needs somewhere to be computed and cached before it can replace a read.

What it *does* settle immediately is a rule [[FEAT-0129]] needs: **a feature in two open releases on the same platform is an error; across platforms it is the normal case.** An earlier draft of that rule said any two open releases, which would have been wrong the first time a feature crossed.

## Done when

- [ ] A decision records whether `platform:` on a feature is authored or derived.
- [ ] Whichever it is, one encoding — not a field and a release list that can disagree.
