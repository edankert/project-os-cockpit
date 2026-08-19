---
type: "[[issue]]"
id: ISS-0238
aliases: ["ISS-0238"]
title: "A check leaves the manual walk for three different reasons and the display has one category for them — `retired` reads as *no longer verified* about checks that are verified on every CI run"
status: open
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
severity: high
component: cockpit-desktop
phase: "[[PHASE-999-Future]]"
related: ["[[ISS-0237-An-Automated-Check-Still-Blocks-The-Manual-Walk]]", "[[FEAT-0138-Coverage-Is-Observed-Not-Declared]]", "[[ADR-0008]]", "[[ISS-0235-A-Surface-Wore-Its-Features-Title]]"]
---

# Three reasons, one category

**A check leaves the manual walk for three reasons and they are not interchangeable:**

| reason | still verified? | how often |
| --- | --- | --- |
| **automated** — a test took it over | **yes** | every CI run |
| **retired** — the surface is gone, or folded into another | no | never again |
| **not applicable** — never applied on this platform | n/a | n/a |

The first two collapse into one terminal presentation that reads as the second.

## It has already produced a real mistake

In `your-trainer` the 67 Tier 3 checks were briefly set to `status: retired` on the reading that `TESTING.md` § *"When to remove"* says a Tier 3 check is removed once covered by passing tests. **It was wrong, and the reason is a modelling gap rather than a slip:**

- `retired` asserts *no longer verified*. These are verified **more** than before.
- **`retired` is a one-way door.** It cannot notice the covering test being renamed or deleted. A `command:` can — it stops resolving, and the run says so on the next push. **That is the self-correcting property [[FEAT-0138]] is built on, and retiring discards it.**

The fix was `command:`, not a status. The display still has no category for it.

## Suggested treatment — derived, and no new status value

Consistent with [[FEAT-0135]] (downstream is a query) and with [[ADR-0008]], which spent a measurement collapsing status vocabularies:

- **`command:` present → Automated.** Out of the manual walk; presence of the field is the whole test. **Render no pass/fail here** — the note does not hold one and must not. A red covering test is already blocking the pre-push hook and CI, which is louder and more current than anything frontmatter could say.
- **`status: retired` → Retired**, and genuinely gone.
- **Neither → the manual walk**, which is what the tier/area grouping is *for*.

## Two things the fix must settle

**1. `tier:` and `area:` on an automated check.** All 67 still read `area: "Moved from Tier 1 / Tier 2 — Fully Automated"` — **a section name in a deleted document, not a place in the application**, which is exactly the distinction [[ISS-0235]] drew. And all 67 read `tier: 3`, which `TESTING.md` defines as *temporary* while these are permanently automated. If tier only gates the manual walk, tier on an automated check may mean nothing and can go the way of the seven fields [[FEAT-0134]] removed. Assigning 67 real areas is **authoring, not migration**, and the target depends on whether automated checks appear under an app area at all.

**2. An upstream contract ambiguity.** `STATUSES.md` attributes *"acceptance checks are never removed, only deprecated"* to `TESTING.md` — but `TESTING.md` scopes that to **Tier 1 and Tier 2** and says Tier 3 **is** removed once covered. Read together they say a Tier 3 check should be retired, which is precisely the false start above. **The two documents must stop disagreeing**, whichever way it settles.

## One correction to the source report

It states *"6 checks are genuinely `retired`"*. Measured 2026-08-19: **zero** acceptance checks in `your-trainer` carry `status: retired`. Either the revert took them with it or they were never written. The 89 `command:` figure is exact.

## Done when

- [ ] Automated, retired and manual are three visibly different dispositions, derived rather than declared.
- [ ] No new status value ([[ADR-0008]]).
- [ ] `tier:`/`area:` on an automated check are decided, not left reading a deleted document's section name.
- [ ] `STATUSES.md` and `TESTING.md` agree about Tier 3, upstream.
