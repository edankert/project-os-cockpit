---
type: "[[change]]"
id: CHG-20260830-Five-Fixes-To-The-Release-Page-The-Checks-Page-And-The-Gate
title: "Five fixes to the release page, the checks page and the acceptance gate"
status: merged
owner: user:edwin
created: 2026-08-30
updated: 2026-09-20
source: ["[[ISS-0271-Five-Tasks-Joined-A-Feature-That-Was-Done-And-Reviewed]]: this note is the one the five tasks owed and nobody wrote", "Independent review of 46d6593..c861414, 2026-08-30"]
commit: "c861414"
pr: ""
impacts: ["[[SUR-0001]]"]
issues: ["[[ISS-0261-A-Release-Is-Offered-Features-Its-Platform-Cannot-Ship]]", "[[ISS-0262-Marking-A-Check-Clears-The-Filter-You-Are-Walking]]", "[[ISS-0263-A-Write-Evicts-The-Reader-From-The-Checks-Page]]", "[[ISS-0264-A-Write-Is-Not-Readable-By-The-Next-Request]]", "[[ISS-0265-A-Retired-Check-Still-Gates-The-Release]]", "[[ISS-0271-Five-Tasks-Joined-A-Feature-That-Was-Done-And-Reviewed]]"]
features: ["[[FEAT-0143-The-Fleet-Runs-One-Validator]]"]
reviewed_by: model:claude-opus-5
review_date: 2026-08-30
review_verdict: changes-requested
review_response: "The review's own finding about these five tasks is [[ISS-0266-Five-Mutants-Survive-The-Guards-Written-For-Them]], and it was acted on on 2026-09-20 under [[TASK-0632-Fix-The-Seven-Defects-From-The-Issue-Review]]: all five surviving mutants now fail a named test and the weak subset assertion is an equality. The verdict is left standing."
review_response_date: 2026-09-20
related: ["[[TASK-0587-The-Derived-Set-Is-This-Releases-Platforms]]", "[[TASK-0588-A-Write-Is-Not-A-Navigation]]", "[[TASK-0589-A-View-Knows-Which-Pages-It-Owns]]", "[[TASK-0590-A-Write-Is-Readable-When-It-Answers]]", "[[TASK-0591-Retiring-Removes-The-Obligation]]", "[[ADR-0040-A-Release-Selects-Its-Features-Not-Its-Excuses]]"]
tags: [change, release-page, checks-page, acceptance]
---

# Five fixes to the release page, the checks page and the acceptance gate

## Summary

Five behaviours changed on 2026-08-30 and no change note said so. **This note is written on 2026-09-20 and back-dated to the day the code landed**, because a change note is a record of when something changed and not of when somebody noticed the record was missing. [[ISS-0271-Five-Tasks-Joined-A-Feature-That-Was-Done-And-Reviewed]] is the issue that found the gap.

The five sit under [[FEAT-0143-The-Fleet-Runs-One-Validator]], a feature about moving the fleet onto one validator. They are not that, and anyone asking in six months why the checks page stopped clearing their filters would have been routed to a validator migration. They stay there — re-homing a task changes the history rather than recording it — and this note is the pointer that was missing.

## Impact

- **A release page offers only what its platform can ship.** An Android release was being offered every unshipped iOS and web feature, none of which an Android build can contain. The page now derives its rows from `publication.shipping_in`, which excludes a feature naming a *different* platform, and counts the rows it is showing instead of the fleet-wide total ([[ISS-0261]], [[TASK-0587]]).
- [[SUR-0001]]: **Ticking a check no longer clears the tier and area you are walking.** Every mark repainted the page through the address-driven renderer, which resets both filters because arriving at a bare `~checks` must not inherit the last page's. Writes now go through `repaintChecksPage`, which opts out of the reset; navigation is unchanged ([[ISS-0262]], [[TASK-0588]]).
- [[SUR-0001]]: **A write no longer throws you off the checks page.** Marking a check wrote a note, the watcher fired, and the landing guard — an equality against one page — sent the reader to the Needs-you landing on every tick. A view now knows the family of pages it owns, which Publication and Design already had ([[ISS-0263]], [[TASK-0589]]).
- [[SUR-0001]]: **A mark or a retirement is visible to the very next request.** The index was refreshed by the watcher, asynchronously: the endpoint answered in about a millisecond and the index caught up at about fifty, so the first tick appeared to do nothing and the second showed the first one's result. Both endpoints now reindex before they answer ([[ISS-0264]], [[TASK-0590]]).
- **A retired check no longer blocks a release, in every repo the gate reaches.** Retiring is `TESTING.md`'s removal path; the check stayed in the walkable suite, in the `unclear` filter and in the blocking set. On `../your-trainer` the gate total went from 103 to 100 ([[ISS-0265]], [[TASK-0591]]).

**Two of the five have no surface note to name.** The release page and the acceptance gate are not described by any `SUR-*`; this repo has one surface note for roughly fourteen screens, which is [[ISS-0306]]. They are stated above as what a person sees instead.

## Documentation Coverage (All Types Considered)

- features: updated — [[FEAT-0143]]'s `acceptance_exception:` is narrowed on 2026-09-20 to cover only its migration tasks; the five page fixes are excluded from the waiver and named here instead.
- requirements: not-applicable — no requirement boundary moved. [[REQ-0059]] is cited by TASK-0591's reasoning, not changed by it.
- tasks: updated — [[TASK-0587]] to [[TASK-0591]], all `done`.
- issues: updated — [[ISS-0261]] to [[ISS-0265]] are `fixed`; [[ISS-0266]] records that the guards were weaker than the notes claimed and was itself fixed on 2026-09-20; [[ISS-0271]] is this note's cause.
- tests: updated — the guards named in each task note, plus the six assertions [[ISS-0266]] added on 2026-09-20.
- workflows: not-applicable.
- decisions: not-applicable — [[ADR-0040]]'s direction is followed by TASK-0587, not amended.
- risks: not-applicable — no new dependency, environment variable or trust boundary.
- changes: new — this note.
- snapshot: not-applicable — the items were already carried; no status moved on 2026-09-20 as a result of writing this.

## Why it is late, stated rather than smoothed over

The independent-review skill fires on *"a change carries a `CHG-*` note"*. Not writing one is therefore how a change of this size reaches `main` without the trigger firing — which is what happened, and it is the second-order cost [[ISS-0271]] is really about. The review did happen, on the diff; its findings are [[ISS-0266]] and [[ISS-0271]] themselves.

## Follow-ups
- [x] Narrow [[FEAT-0143]]'s `acceptance_exception:` so it no longer claims the feature ships no user-facing surface (2026-09-20).
- [x] Add the assertions that make the five guards fail when the fixes are undone — [[ISS-0266]], fixed 2026-09-20.
- [ ] Decide whether the five tasks want a feature of their own. Not done: it would move a reviewed feature's contents after the fact, and this note gives a reader the route without that.
