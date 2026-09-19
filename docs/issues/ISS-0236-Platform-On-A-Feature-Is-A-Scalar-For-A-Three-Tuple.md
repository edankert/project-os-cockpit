---
type: "[[issue]]"
id: ISS-0236
aliases: ["ISS-0236"]
title: "`platform:` on a feature is the same shape `mark:` was on a check — a feature ships on a platform *in a release*, and a scalar cannot hold that"
status: open
owner: user:edwin
created: 2026-08-19
updated: "2026-09-19"
reported_by: user:edwin
severity: medium
component: docs
phase: "[[PHASE-999-Future]]"
related: ["[[ADR-0037-A-Verdict-Is-An-Event]]", "[[FEAT-0129-A-Release-Names-Its-Own-Contents]]", "[[DES-0012-Tests-In-Two-Flows]]", "[[FEAT-0130-Surfaces-Are-A-First-Class-Type]]"]
question: "Should a feature's `platform:` stay authored (blank/`cross`/`all` already means every platform, and each release's frozen `features:` list records where it shipped) or become derived from the releases that contain it? Options: keep authored and decline this issue; derive it from releases. Recommendation: keep authored and decline, because with two platforms `cross` already covers a feature built once and shipped twice."
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

## Checked against the code, 2026-09-19: a question for Edwin

**What a user notices:** Nothing today. A feature shipped on both Android and iOS can already say `platform: "cross"`, and release pages include it on both.

Evidence: `publication._ships_on` (src/project_os_cockpit/publication.py:891-910) keeps a feature in a release unless the feature names a different platform, and treats blank, `shared`, `cross`, `all` and `both` as every platform (`_EVERY_PLATFORM`, publication.py:888). The rule this issue asked for is built: FEAT-0129:37 refuses a feature in two open releases on the same platform and allows it across platforms, with tests. your-trainer's features currently read `android` 3, `ios` 3, `cross` 2, `all` 3. What remains is the design choice in "Done when", which only Edwin can make.

**Belongs to:** FEAT-0129's area (release contents); no open feature. **Next:** Edwin answers the `question:` field; on "keep authored", set `status: declined`.

Checked as part of project-os-dev FEAT-0036 (TASK-0141).
