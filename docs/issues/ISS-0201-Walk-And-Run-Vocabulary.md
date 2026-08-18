---
type: "[[issue]]"
id: ISS-0201
aliases: ["ISS-0201"]
title: "\"Walk\" and \"Run\" are two words for one act, and the release page still offers the whole suite instead of what is outstanding"
status: triage
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
severity: medium
component: ui
phase: "[[PHASE-999-Future]]"
related: ["[[TESTING-MODEL]]", "[[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]]", "[[FEAT-0116-A-Release-Can-Be-Finished]]"]
---

# Walk, run, and what the release page should show

Edwin, 2026-08-18: *"The current UX functionality feels wrong, why did you use the term walk/run? The release page shows all the clickable items again, it should probably now just show a list of unchecked/open acceptance tests and link to this?"*

## Two words, one act

The corpus uses **walk** for an acceptance test and **run** for an executable one, and the registry's verb for the `test` obligation is `Run`. That split made sense while they were different types. Under [[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]] they are one type on a scale, so the surface now has two words for the same act separated by a field the reader cannot see.

It shows up directly: the Tests view has a group called **`Needs a run`** which contains only *non-acceptance* manual tests, while the acceptance population — the thing a person actually walks — sits under `Tier 1/2/3` with no verb at all. A reader looking for "what do I have to do by hand" finds one of the two populations under a heading that names the other's verb.

## The release page

It renders the acceptance rows as clickable items again — a second copy of the suite, on a page whose job is to say **what stands between this release and shipping**. Since [[FEAT-0114]] the suite has its own view at `~checks`, so the release page is now duplicating a surface that did not exist when it was written.

Edwin's proposal, which reads correctly: **show the outstanding set and link to the walk.** The gate's number is already computed (`gate_payload`); what the page owes is the list behind it, not a re-render of all 579 rows.

## What would settle it

- [ ] One verb for one act, chosen deliberately, and applied to the registry, the group headings and the buttons.
- [ ] The release page shows unsettled Tier 1/2 rows only, each linking into `~checks` at that row — with the settled majority reachable but not rendered.

## Independent review

**2026-08-18, `model:claude-opus-5`, fresh context, against the live payloads on `:8765`/`:8766` and `desktop/src/renderer/renderer.ts`.** The vocabulary half is right and can be made stronger. The release-page half is wrong about what the page does, and right by accident about what it should do.

### Two words, one act — confirmed, and it is not only prose

The registry carries **both verbs at once, over one type**: `OBLIGATIONS["test"].verb == "Run"` and the note-less `release gate` obligation's verb is `"Walk"`. Live on `your-trainer` right now: the Tests view badge says *Run 5 tests* and the Publication badge says *Walk 1 release gate*, and after ADR-0031 both populations are `[[test]]`. The split is therefore encoded in the registry, not merely in headings — which is where a single-verb decision has to land.

### The release page does not re-render the suite

`gate_payload` returns `suite.blocking()` — unsettled Tier 1/2 only. Measured on `your-trainer`: **60 blocking of 579**, rendered as `New 13` + `Chronic 27` + `Regressed 0`, with `Quiet 20` collapsed behind a `<details>` and `Stale 0`. `gateGroup` caps every list at 40 rows and appends *"…N more"*. The 579 rows are never sent to the page and never were. **The first "Done when" bullet is substantially already true**, and the note should not claim otherwise — it describes finished work as outstanding.

### What is actually wrong on that page, which the note does not name

Every blocking row is addressed by its **document** number (`item.number`, e.g. `1.4.20`) and its click handler navigates to `/docs/${gate.rel}${'#'+item.anchor}` — where `gate.rel` is the directory `tests/acceptance` and `item.anchor` is the deleted document's slug (`16-monetization-licensing`). That resolves to the suite **README**, with a dead fragment. `item.rel` — `tests/acceptance/TST-0076-Multi-Rider-FREE.md` — is in the same payload and unused. `_acceptance_tier_groups` substitutes `~checks` for the notes shape; this call site inherited the pre-migration form and nothing caught it. So *"link to the walk"* is the right ask, reached through the wrong diagnosis: the page is not showing too much, it is pointing the rows it already shows at a page that no longer describes them.

### The second bullet reverses a one-day-old decision without saying so

*"each linking into `~checks` at that row"* means removing the live mark control from the gate rows. That control is [[ISS-0190]], 2026-08-17, at your own instruction — *"you can have the checkbox on the left as long as the check box functionality is the same as in the .md file"* — and it was built specifically to retire a second vocabulary (`Pass · Partial · Fail`) on those same rows. Reversing it may still be right, but the note should record that it is a reversal and answer ISS-0190's argument, or the two decisions will simply take turns.

**Verdict: keep the vocabulary half; rewrite the release-page half around the addressing defect, and correct "all 579 rows" to the 40 live rows the page actually renders.**
