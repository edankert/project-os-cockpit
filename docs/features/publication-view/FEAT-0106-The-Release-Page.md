---
type: "[[feature]]"
id: FEAT-0106
aliases: ["FEAT-0106"]
title: "The release page — one place that says what is in the next release, lets you start it, and shows what stands between it and shipping"
status: done
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
reviewed_by: "model:claude-opus-5"
review_date: 2026-08-16
review_verdict: changes-requested
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["Edwin 2026-08-16: 'I would have expected that if I selected the Next Release item that this would bring up a virtual page which showed what would be in this release and for me then to be able to start the release in the main section of the tool?'", "Edwin 2026-08-16: 'Also, where is my acceptance-tests?'"]
goal: "Give the release a page instead of a row and a modal: what has accumulated, a version field and a Start button in the centre pane, and the gate with its checks — so the acceptance tests have an obvious home rather than being the sixth group down a navigator."
requirements: []
tasks: ["[[TASK-0440-The-Release-Payload]]", "[[TASK-0441-The-Release-Page-And-An-Input-That-Works]]"]
design: ""
release: ""
depends: ["[[FEAT-0105-There-Is-Always-A-Release]]"]
related: ["[[ISS-0176-Every-Prompt-In-The-Desktop-Shell-Is-Dead]]", "[[FEAT-0105-There-Is-Always-A-Release]]", "[[FEAT-0104-The-Suite-Is-The-Surface]]", "[[ADR-0022]]"]

---

# The release page

## Why

Three reports, one cause. Edwin: *"the prepare button is not working"*, *"I would have expected that if I selected the Next Release item that this would bring up a virtual page"*, *"where is my acceptance-tests?"*

The button was dead because it called `window.prompt`, which Electron does not implement ([[ISS-0176]]). But the deeper mistake was the shape: **a left-pane row that pops a modal**. The navigator navigates; the centre pane is where you act — which is how `~overview`, `~history` and `~design/<id>` already behave. A page also removes the need for a dialog at all, because the version becomes a field.

And it gives the acceptance tests a home. They were never missing — `Release gate · 60 unchecked` is the **sixth of seven** groups in the navigator, under a row that did nothing when clicked. Not absent; lost.

## The page

```
Next release                              [ 2.1.7 ] [Start ▸]

What's in it — 32 features unshipped since REL-0012
   FEAT-0104  Multi-rider FREE and PRO seat
   …

Release gate · 60 unchecked
   1.6.15  Multi-Rider on FREE            → open in suite
   …                                      [Open the suite]
```

`~release/next` for the accumulating one, `~release/<id>` for a named release.

## Acceptance criteria

- [x] Selecting the next-release row opens a page in the centre pane; nothing pops a dialog — true now, and it was NOT true when this feature was marked done — the row carried `~prepare-release`, which opened a `window.prompt` Electron does not implement. Edwin found it by pressing it five times. Fixed by [[ISS-0176]] and [[FEAT-0107]]
- [x] The page lists what has accumulated, derived from `unreleased_payload` — no second computation — `test_contents_come_from_the_existing_computation`
- [x] A version field and `Start` declare the release **in the page**, and the surface updates without a reload — `renderReleasePage`; Edwin used it to declare 2.1.7
- [x] Starting refuses the same cases the write path refuses, and shows the reason on the page rather than in a toast that disappears — the refusal renders beside the field, not in a toast
- [x] The gate is a section of the page: the outstanding count, the checks, and a link into the suite at the right section — and is absent for a shipped release, which it was not — see [[FEAT-0107]]
- [x] `window.prompt` appears nowhere in the renderer, and a guard fails if it returns ([[ISS-0176]]) — `test_the_renderer_never_calls_window_prompt`
- [x] The other four dead prompts are converted to the same input — drafting a release, reconciling a criterion, filing an issue from a failure, annotating a design — all five share `askForText`
- [x] Nothing here publishes ([[ADR-0022]]) — unchanged
- [x] A repo with no releases and no suite renders the page as complete rather than blank — `test_no_suite_is_reported_rather_than_read_as_clear`


## Criteria resolved 2026-08-16, after the fact

`done` at **0 of 9**, found by independent review. The first criterion is the one that matters: *"nothing pops a dialog"* was written here, left unticked, and the feature shipped with a dialog that could not open. Edwin pressed it five times and the app logged the reason each time.

Ticking is not a formality. Had this list been walked before the status moved, the dead control would have been found by the person who wrote the criterion rather than by the person it failed.
