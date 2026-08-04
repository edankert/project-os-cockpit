---
type: "[[reference]]"
id: REFERENCE-SNAPSHOT-FIELD-MIGRATION
title: "Snapshot field migration record: values replaced when title/goal became derived"
status: active
owner: user:edwin
created: 2026-08-04
updated: 2026-08-04
scope: "project"
source: ["FEAT-0022", "TASK-0084", "ADR-0018"]
related: []
---

# Snapshot field migration record

Every `title:`/`goal:` value **project-os-cockpit**'s `SNAPSHOT.yaml` carried before ADR-0018 made those
fields derived, where it differed from the note that now supplies it. Includes entries
later removed by retention, so this is the complete replaced set, not just the survivors.

Reconstructed from `48ea49e2~1` after the first pass wrote an incomplete record: the rollout
re-ran the recorder *after* migrating, when there was no drift left to capture.

140 value(s) replaced.

## FEAT-0074 (`title`)

- **was:** The driver: select with reasons, dispatch, watch, record, next — with the lease and stop conditions proven by drill
- **now:** The standing worker — acquire, select, dispatch, watch, record, release, next; with a lease that refuses and stops that hold

## FEAT-0075 (`title`)

- **was:** DELEGATION.md, approved through the gate it configures; delegate writes carry their authority; the push ADR
- **now:** The delegation policy — a principal-approved note the actuators consult, delegate writes that carry their authority, and the push decision taken as an ADR

## FEAT-0076 (`title`)

- **was:** Timeouts per kind, proceed-on-recorded-assumption, and the stall alarm
- **now:** Escalation with defaults — timeouts per queue kind, proceed-on-recorded-assumption, and an alarm so nothing waits silently forever

## FEAT-0077 (`title`)

- **was:** The charter as acceptance oracle, and the delegated flavour of the runner
- **now:** The intent charter — DES-0003's page graduated into the oracle a delegated acceptance judges against

## FEAT-0059 (`title`)

- **was:** note_writes widens: the human-owned transition table as data, criteria ticks, issue creation
- **now:** note_writes widens: the human-owned transition table as data, criteria ticks, and issue creation — behind the guards it already has

## FEAT-0060 (`title`)

- **was:** The actuator row and live criteria checkboxes
- **now:** The actuator row: a note's legal human actions as buttons under its title, and its criteria checkboxes made live

## FEAT-0061 (`title`)

- **was:** ⌘N capture into triage, and the triage tray
- **now:** A thought becomes a triaged issue: ⌘N capture into triage, and a triage tray where those judgments get made

## FEAT-0062 (`title`)

- **was:** Changes-requested reaches re-review; questions get answered in place
- **now:** The desk's dangling flows close: changes-requested reaches re-review, and a question gets its answer written back

## FEAT-0063 (`title`)

- **was:** Criteria walked one at a time; pass ticks with a witness, fail files the issue
- **now:** The acceptance runner — a feature's criteria walked one at a time; pass ticks with a witness, fail files the issue, the run leaves a log

## FEAT-0064 (`title`)

- **was:** acceptance: absent/requested/accepted — opt-in, owed on the desk, satisfied only by a run
- **now:** Acceptance as an explicit, opt-in gate: requested at close-out, owed on the desk, satisfied only by a run

## FEAT-0065 (`title`)

- **was:** Unverified requirements, unresolved criteria, evidence-free ticks — as a record card
- **now:** The acceptance-debt surface: which requirements have no verification, which criteria sit unticked, what was ticked without evidence

## FEAT-0066 (`title`)

- **was:** Captures into docs/attachments, rendered in notes, offered at the moment of verdict
- **now:** Visual evidence — the shell captures a surface into the repo and the note renders it, so evidence a non-code reader can trust

## FEAT-0067 (`title`)

- **was:** Variants as sandboxed fragments side by side; Choose records the decision
- **now:** Designs render their artefacts — variants as sandboxed fragments side by side, and choosing one records the decision

## FEAT-0068 (`title`)

- **was:** Two surfaces, an element each, the differences as a table
- **now:** The measure view — two surfaces side by side with a computed-style table, so comparisons happen in numbers instead of eyes

## FEAT-0069 (`title`)

- **was:** A pin or selection on a design becomes an anchored review-queue entry
- **now:** Annotate to request — a pin or a selection on a design becomes a review-queue entry with an anchor that degrades honestly

## FEAT-0070 (`title`)

- **was:** design: gates the feature that names it; Derive-requirements dispatches, never generates
- **now:** An accepted design gates the feature that names it, and can scaffold that feature's requirements — by dispatch, never by fiat

## FEAT-0071 (`title`)

- **was:** The watermark, the digest, and a Caught-up that means it
- **now:** Since you looked — a per-workspace watermark, a digest of what happened behind it, and a Caught-up that means it

## FEAT-0072 (`title`)

- **was:** UNRELEASED as a number, Draft-release as an action, the acceptance-tests gate rendered
- **now:** The release surface — done-but-unshipped becomes a number, drafting a release becomes an action, and the acceptance-tests gate finally renders

## FEAT-0073 (`title`)

- **was:** Empty states, the eye toggle, the recorded exceptions, and mode 1 decided once
- **now:** One voice — empty states that say what would appear, the eye toggle retired or defended, the exceptions written down, and mode 1 decided once

## FEAT-0058 (`title`)

- **was:** Every navigator is a live section plus collapsed cards, with a completed divider only where group names do not say finished
- **now:** Every navigator is a live section plus collapsed cards, and a completed divider appears only where the group names do not already say finished

## FEAT-0057 (`title`)

- **was:** Both panes adopt the record column's grammar — one-line rows, status once at the head, finished groups rolled up
- **now:** Both panes adopt the record column's grammar — one-line rows, status said once at the head, and finished groups rolled up behind a divider

## FEAT-0056 (`title`)

- **was:** Open work sorts first, long lists fold, and the context pane never filters
- **now:** Open work sorts first, long lists fold, and the context pane never filters — so a corpus that is 99% complete reads without a switch that empties it

## FEAT-0051 (`title`)

- **was:** Validator errors are session work while a session runs, and issues once it ends
- **now:** Validator errors are session work while a session is running, and issues once it ends

## FEAT-0036 (`title`)

- **was:** Live work views — session work tab, Active nav mode, phase-less Now board
- **now:** Live work views — watch tasks/features/issues move: session work tab, Active nav mode, phase-less Now board

## FEAT-0011 (`title`)

- **was:** Native centre pane + routing (rendered Markdown, history, anchors, checkboxes)
- **now:** Native centre pane + routing (rendered Markdown, history, anchors, interactive checkboxes)

## FEAT-0012 (`title`)

- **was:** Native UX wins (Cmd+P, Cmd+F, context menus, drag-drop, multi-window)
- **now:** Native UX wins (Cmd+P, Cmd+F, context menus, drag-drop, multi-window, per-workspace state)

## FEAT-0015 (`title`)

- **was:** Cockpit IA v2 — mini-rail, modes-on-top, per-workspace terminal
- **now:** Cockpit IA v2 — workspace mini-rail, modes-on-top toolbar, per-workspace terminal

## TASK-0322 (`title`)

- **was:** Selection with reasons — step 2 as code, the ledger says why
- **now:** Selection with reasons — LIFECYCLE step 2 as code, every choice explained in the ledger

## TASK-0323 (`title`)

- **was:** The session loop — dispatch, watch, record, next
- **now:** The session loop — dispatch through the instrumented terminal, watch to close-out or failure, record, next

## TASK-0324 (`title`)

- **was:** The lease — refuse, heartbeat, expire loudly
- **now:** The lease — a claim that refuses a second worker, heartbeats, and expires loudly

## TASK-0325 (`title`)

- **was:** Stop conditions proven by drill
- **now:** Stop conditions proven by drill — budget, backoff, validator red, and the human's stop switch

## TASK-0326 (`title`)

- **was:** DELEGATION.md — approved through the gate it configures
- **now:** DELEGATION.md — what is delegated, what escalates, approved through the gate it configures

## TASK-0327 (`title`)

- **was:** The actions endpoint answers per caller; delegate writes carry authority
- **now:** The actions endpoint answers per caller identity, and a delegate's writes carry their authority

## TASK-0328 (`title`)

- **was:** Publishing under autonomy taken as an ADR
- **now:** The push decision — publishing under autonomy taken as an ADR, not eroded by convenience

## TASK-0329 (`title`)

- **was:** Timeouts per queue kind, from the approved policy
- **now:** Timeouts per queue kind, read from the approved policy

## TASK-0330 (`title`)

- **was:** The assumption path: resolve, tag, lift
- **now:** Proceed on a recorded assumption — resolved where the answer would have gone, tagged on the work, lifted in the digest

## TASK-0331 (`title`)

- **was:** Anything past twice its clock with no default joins NEEDS-YOU
- **now:** The stall alarm — anything past twice its clock with no default joins NEEDS-YOU

## TASK-0332 (`title`)

- **was:** The intent page's role widens from display to oracle
- **now:** DES-0003 revised — the intent page's role widens from display to oracle, and the design goes to the desk

## TASK-0333 (`title`)

- **was:** Goals, non-goals and taste constraints, drafted from the record
- **now:** The charter note — goals, non-goals and taste constraints, drafted from the record, approved by the principal

## TASK-0334 (`title`)

- **was:** The runner with agent:principal as witness, charter-bound
- **now:** Delegated acceptance — the runner with agent:principal as witness, charter in context, worker kept at arm's length

## TASK-0287 (`title`)

- **was:** The criteria payload — the endpoint, sharing the validator's parse
- **now:** The criteria payload — a feature's requirements' criteria with their resolved states, from the parse the validator already trusts

## TASK-0288 (`title`)

- **was:** The runner surface — one criterion at a time, four verbs
- **now:** The runner surface — one criterion at a time, four verbs, progress named

## TASK-0289 (`title`)

- **was:** stamp_acceptance — the run log, the witness, the gate's satisfied state
- **now:** stamp_acceptance — the run log into the feature note, and the gate's satisfied state

## TASK-0291 (`title`)

- **was:** The acceptance field in template and taxonomy, divergence recorded
- **now:** The acceptance field — absent / requested / accepted — in template and taxonomy, divergence recorded

## TASK-0292 (`title`)

- **was:** Awaiting your acceptance — the queue's most human section
- **now:** Awaiting your acceptance — the queue's most human section, first

## TASK-0293 (`title`)

- **was:** ACCEPT-STALE, and the convention proposed upstream
- **now:** The ACCEPT-STALE warning, and the convention proposed upstream

## TASK-0300 (`title`)

- **was:** Variant sections render live, sandboxed, token-true
- **now:** A ## Variant section with fenced html renders live, sandboxed, token-true

## TASK-0304 (`title`)

- **was:** The cockpit measures itself
- **now:** The cockpit measures itself — the by-hand CDP loop made a feature

## TASK-0306 (`title`)

- **was:** The queue learns annotation, with an anchor schema
- **now:** The queue learns `annotation`, with an anchor schema

## TASK-0308 (`title`)

- **was:** Annotations under the design's entry, degrading honestly
- **now:** Annotations under the design's desk entry, degrading honestly

## TASK-0310 (`title`)

- **was:** An accepted design drafts its requirements through an agent
- **now:** An accepted design drafts its requirements — through an agent, never by fiat

## TASK-0320 (`title`)

- **was:** The exceptions written into the design system
- **now:** The desk's headings and the Library's file rows, written into the design system

## TASK-0280 (`title`)

- **was:** Issue creation from template, and the mutation-grade hardening suite over all three verbs
- **now:** Issue creation from template with the next free id, and the mutation-grade hardening suite over all three verbs

## TASK-0281 (`title`)

- **was:** The action row under the note title
- **now:** The action row under the note title — drawn from the server's answer, confirming terminal moves, explaining disabled ones

## TASK-0282 (`title`)

- **was:** Criteria checkboxes tick from the note view
- **now:** Criteria checkboxes tick from the note view, with an inline evidence prompt and the reconcile form behind a menu

## TASK-0283 (`title`)

- **was:** ⌘N capture — title in, triage issue out, under three seconds
- **now:** ⌘N capture — title in, triage issue out, current note linked, under three seconds

## TASK-0284 (`title`)

- **was:** The triage tray — accept-as-severity or decline on every row
- **now:** The triage tray — accept-as-severity or decline on every row, siblings hinted, investigation one dispatch away

## TASK-0285 (`title`)

- **was:** Request re-review from a changes-requested row
- **now:** Request re-review from a changes-requested row — the reviewer dispatched with the note and its prior findings

## TASK-0286 (`title`)

- **was:** Answer a queue question inline
- **now:** Answer a queue question inline — resolved with the answer as outcome, delivered to the asking session

## TASK-0275 (`title`)

- **was:** A group whose every item is terminal renders shut, with its count in the head
- **now:** A group whose every item is terminal renders shut, with its count in the head — the context card's behaviour, in the navigator

## TASK-0276 (`title`)

- **was:** The completed divider appears only where a group's name does not say it is finished
- **now:** The completed divider appears only where a group's own name does not say it is finished — issues and features, not tasks

## TASK-0277 (`title`)

- **was:** The review desk promotes changes-requested and collapses the rest into cards per verdict
- **now:** The review desk promotes changes-requested into a live section and collapses the rest into cards per verdict

## TASK-0271 (`title`)

- **was:** Nav and context rows collapse to one line at the record column's height
- **now:** Nav and context rows collapse to one line — ID, ellipsised title, chip — at the record column's height

## TASK-0273 (`title`)

- **was:** Finished groups roll up behind one divider; a group holding the active note opens itself
- **now:** Finished groups roll up behind one divider, and any group holding the active note opens itself

## TASK-0274 (`title`)

- **was:** The right context pane renders as record cards, body closed when the type is settled
- **now:** The right context pane renders as record cards — a head per type with a count, body closed when the type is settled

## TASK-0267 (`title`)

- **was:** One comparator sorts open before done, within every group
- **now:** One comparator sorts open before done, applied to items within every group, so state orders where no grouping axis can carry it

## TASK-0268 (`title`)

- **was:** Groups that still contain open work sort above groups that do not
- **now:** Groups that still contain open work sort above groups that do not, so the active phase is not buried under twenty finished ones

## TASK-0269 (`title`)

- **was:** The right context pane orders by state and never filters by it
- **now:** The right context pane orders by state and never filters by it, because a note's completed children are what the note is made of

## TASK-0270 (`title`)

- **was:** A long group shows its head and a count, keyed on length and never on status
- **now:** A group longer than the fold threshold shows its head and a count, keyed on length and never on status, so the switch collapses rather than hides

## TASK-0265 (`title`)

- **was:** Unpushed commits and the remote's kind, on the fleet surface
- **now:** Unpushed commits and the remote's kind, on the surface that already reports repo health

## TASK-0262 (`title`)

- **was:** The context menu acts on the link, not the word Chromium selected
- **now:** The context menu acts on the link that was right-clicked, not the word Chromium selected

## TASK-0263 (`title`)

- **was:** Terminal copy survives the right-click; Cmd-C/V route to the focused pane
- **now:** Terminal copy survives the right-click, and ⌘C/⌘V route to whichever pane is focused

## TASK-0258 (`title`)

- **was:** activity_payload — per-day counts across the whole history, cached on HEAD
- **now:** activity_payload — per-day transition and commit counts across the whole history, cached on HEAD

## TASK-0260 (`title`)

- **was:** A History button in the workspace rail
- **now:** A History button in the workspace rail, so the page is reachable from anywhere

## TASK-0255 (`title`)

- **was:** history_payload — transitions from git, grouped by commit, uncommitted band on top
- **now:** history_payload — status transitions from git, grouped by commit, with the uncommitted band on top

## TASK-0256 (`title`)

- **was:** One History tile replacing Activity, Changes and Commits
- **now:** One History tile on the overview, replacing Activity, Changes and Commits

## TASK-0252 (`title`)

- **was:** Subscribe the renderer to cockpit:validation so the active repo's errors are live
- **now:** Subscribe the renderer to cockpit:validation so the active repo's errors are live in the shell

## TASK-0253 (`title`)

- **was:** One row per validator error in the session summary, closing as it is fixed
- **now:** One row per validator error in the session summary, closing as the agent fixes it

## TASK-0254 (`title`)

- **was:** Close-out files what it could not fix, deduped on (code, subject)
- **now:** Close-out files the validator errors it could not fix, as issues, without filing the same one twice

## TASK-0250 (`title`)

- **was:** The validator badge on the rail and tabs, without colliding with the agent-state dot
- **now:** The validator badge on the workspace rail and tabs, without colliding with the agent-state dot

## TASK-0214 (`title`)

- **was:** Design-note convention and validator support
- **now:** Consume the design note type in the cockpit

## TASK-0219 (`title`)

- **was:** Design tokens checked against the implementation's CSS
- **now:** Scoped palette parity — a design's status colours must match statuses.py

## TASK-0161 (`title`)

- **was:** Burn-rate projection — time left at current burn from recent usage samples
- **now:** Burn-rate projection — '~1h 05m left at current burn' from recent usage samples

## TASK-0163 (`title`)

- **was:** Session rail 'work' tab — status boxes per touched note, filling live
- **now:** Session rail 'work' tab — status boxes per touched note, filling live as the agent closes items

## TASK-0165 (`title`)

- **was:** Phase-less Now board — overview centre renders the Active data full-width
- **now:** Phase-less Now board — the overview centre renders the Active data full-width with animated transitions

## TASK-0153 (`title`)

- **was:** External hook adopts the Notification subtype gate
- **now:** External hook adopts the Notification subtype gate — needs-input means the same thing on every path

## TASK-0017 (`title`)

- **was:** Cockpit platform filter (auto-discovered)
- **now:** Cockpit platform filter (auto-discovered, picker only when used)

## TASK-0053 (`title`)

- **was:** Cockpit: server-side state — agent_focus, per-tab state, history (GET /api/cockpit/state, POST /api/cockpit/tab-state)
- **now:** Cockpit: server-side state (agent_focus, per-tab state, history)

## TASK-0054 (`title`)

- **was:** Cockpit: `cockpit state` + `cockpit history` CLI subcommands
- **now:** Cockpit: `cockpit state` + `cockpit history` CLI

## TASK-0055 (`title`)

- **was:** Cockpit: JS tab-state pings (nav events + 15s heartbeat + tab_id in localStorage)
- **now:** Cockpit: JS tab-state pings + heartbeat

## TASK-0056 (`title`)

- **was:** Cockpit: LLM directives for reading the user's view (COCKPIT.md + cockpit-driving SKILL)
- **now:** Cockpit: LLM directives for reading the user's view

## TASK-0080 (`title`)

- **was:** Activity-bar layout shell — rail + in-workspace nav + stage
- **now:** Activity-bar layout shell — rail + in-workspace nav + stage (+ right pane column)

## TASK-0081 (`title`)

- **was:** Persist agent-state to .cockpit/agent-state.json
- **now:** Persist agent-state to `<project-root>/.cockpit/agent-state.json` (FEAT-0013 amendment)

## ISS-0093 (`title`)

- **was:** Three nested paddings pushed a phase id right of its own features, and a second section-heading style duplicated one that existed
- **now:** Three nested paddings pushed a phase id further right than the features beneath it, and a second section-heading style was written without checking the first existed

## ISS-0092 (`title`)

- **was:** A severity bucket holding both open and fixed issues had to be placed whole
- **now:** A severity bucket holding both open and fixed issues had to be placed whole, so one open issue could keep fifty-six fixed ones above the completed divider

## ISS-0091 (`title`)

- **was:** Two levels of one tree drew different expand handles, and a group head's id shrank to 7px
- **now:** Two levels of one tree drew different expand handles, and a group head's id shrank to 7px because flex:none was scoped to rows

## ISS-0090 (`title`)

- **was:** Phase rows differed from the overview's, and a plan's empty id dropped it out of the id column
- **now:** Phase rows still differ from the overview's, and a plan's empty id drops it out of the id column so it sits 78px left of its sibling requirements

## ISS-0089 (`title`)

- **was:** Copying the context card's head styling made phase names render as labels
- **now:** Copying the context card's head styling made phase names render as labels — a card head names a category, a phase head names a thing, and only one of those can be faint

## ISS-0088 (`title`)

- **was:** The completed sections behaved like the right pane's cards but did not look like them; heads carried an icon, an uncoloured id and an inconsistent pill
- **now:** The completed sections behave like the right pane's cards but do not look like them, and the group heads carry an icon, an uncoloured id and an inconsistent pill

## ISS-0087 (`title`)

- **was:** The navigator's group headers were twice the height of the context cards they were aligned to
- **now:** The navigator's group headers are twice the height of the context cards they were aligned to, because only their type was matched and not their padding

## ISS-0086 (`title`)

- **was:** The roll-up collapsed the phase list, the status vocabulary and the severity ladder into one line
- **now:** The roll-up collapsed the phase list, the status vocabulary and the severity ladder into one line — structure, not noise, and the overview never made that mistake

## ISS-0085 (`title`)

- **was:** The one-line grammar reached one of four row renderers, and the subtitle put a second line back on that one
- **now:** The one-line grammar reached one of the left pane's four row renderers, and the subtitle put a second line back on that one

## ISS-0084 (`title`)

- **was:** A change note's id is its description, so a row rendered the description twice
- **now:** A change note's id is its description, so a row renders the description twice and the CHG slug is the widest thing in the pane

## ISS-0083 (`title`)

- **was:** The navigator never highlights the open note — refreshActiveNavRow selects li.nav-item, but that class is on the inner div
- **now:** The navigator never highlights the open note, because refreshActiveNavRow selects li.nav-item while the class sits on the inner div

## ISS-0082 (`title`)

- **was:** A phase rename forked its children into a phantom group, because two code paths read the phase link differently
- **now:** Two code paths read the phase link differently, so renaming PHASE-016 during the merge forked its children into a phantom group in the features navigator while the overview showed them correctly

## ISS-0081 (`title`)

- **was:** Right-click word-select plus copy-on-select overwrote the clipboard before the paste read it
- **now:** xterm's right-click word-select combined with unconditional copy-on-select to overwrite the clipboard with the word under the cursor, so right-click-to-paste pasted that word back

## ISS-0080 (`title`)

- **was:** Replace the console context menu with select-copies / right-click-pastes
- **now:** The console's context menu does not work for the user across three attempts — replace it with the terminal convention (select copies, right-click pastes) rather than debug a menu a console does not need

## ISS-0079 (`title`)

- **was:** The note context menu keyed off closest('a'), so button-shaped rows got the word menu
- **now:** The note context menu keyed off `closest('a')`, so every button-shaped row — History, the uncommitted band — got the word menu and no way to copy anything about the note it names

## ISS-0078 (`title`)

- **was:** PHASE-003's pilot was overtaken by workspace discovery; CLAUDE.md still claims the shim exists
- **now:** PHASE-003's downstream pilot was overtaken by workspace discovery and never built, while CLAUDE.md still tells every session the shim exists

## ISS-0077 (`title`)

- **was:** A phase became the unit of a request — nine in a day at a fifth of the historical size
- **now:** Nine phases opened in one day against nine in the preceding twelve weeks — a phase became the unit of a request rather than of a delivery push, at a fifth of the historical size

## ISS-0076 (`title`)

- **was:** The overview's Phases section shows titles and never phase IDs
- **now:** The overview's Phases section shows each phase's title and never its ID, so the one place that lists every phase cannot be cross-referenced with anything that names them

## ISS-0075 (`title`)

- **was:** Contribution grid: the busiest days render 33% smaller — the second channel was subtractive
- **now:** The contribution grid's busiest days render 33% smaller than its quietest — the 'second channel' was subtractive, so the strongest signal was the weakest mark

## ISS-0074 (`title`)

- **was:** 16 of 19 notes naming PHASE-999 are terminal — the strip draws 16 delivered squares under 'Future'
- **now:** 16 of the 19 notes naming PHASE-999 are terminal, so the phase strip draws 16 `delivered` squares inside a phase titled 'Future / Unphased'

## ISS-0073 (`title`)

- **was:** SwiftUI 0-1 Color(red:green:blue:) reads as unresolved
- **now:** SwiftUI's 0–1 Color(red:green:blue:) reads as unresolved, so a real colour renders as a source expression

## ISS-0072 (`title`)

- **was:** SNAPSHOT.yaml edits never re-trigger validation — METRICS drift cannot clear live
- **now:** The validator never re-runs on a SNAPSHOT.yaml edit — its dedicated project-root observer does not fire, so METRICS drift never clears live

## ISS-0032 (`title`)

- **was:** Dispatch agent vocabulary is a closed two-value union; its ternaries coerce any third agent to 'claude'
- **now:** The dispatch agent vocabulary is a closed two-value union restated across nine sites; a third agent is dropped from the persisted queue and coerced in two preference paths

## ISS-0030 (`title`)

- **was:** Phase completion is inferred from task counts and ignores the phase's own status, so a superseded phase reads live; live phases also sort by order: rather than active-first
- **now:** Phase completion is inferred from task counts and ignores the phase's own status, so a superseded phase reads live; live phases also sort by `order:` rather than active-first

## ISS-0026 (`title`)

- **was:** The cockpit bundles its own copy of validate-docs.py and it has already drifted from the template (875 vs 885 lines)
- **now:** The bundled validator is guarded against local drift but not against upstream template lag — it was 10 lines behind project-os

## ISS-0020 (`title`)

- **was:** Strip misses the session’s implemented tasks — status changes (esp. via non-Edit-tool writes) and cross-prompt completions never surface
- **now:** Strip misses the session's implemented tasks — status changes (esp. via non-Edit-tool writes) and cross-prompt completions never surface

## ISS-0022 (`title`)

- **was:** Repo is behind the project-os template: its vendored validator cannot see 8 real errors (deferral provenance + stale metrics), and it never adopted the generated adapter surface
- **now:** Repo is behind the project-os template: its vendored validator cannot see 8 real errors, and it never adopted the generated adapter surface

## ISS-0010 (`title`)

- **was:** Agent strip (and its files view) vanishes the moment a session ends — regression from ISS-0009
- **now:** Agent strip (and its files view) vanishes the moment a session ends — regression from the ISS-0009 strip-hide

## ISS-0001 (`title`)

- **was:** Watcher-indexed paths poison _records under a mismatched case on macOS, so /api/render returns empty frontmatter for files created/modified after cockpit start
- **now:** Watcher-indexed paths poison the in-memory _records under a different case than the initial walk on case-insensitive filesystems, so /api/render returns empty frontmatter for any file created or modified after cockpit start

## REQ-0019 (`title`)

- **was:** Cross-workspace agent detail — state, session, cost, queue, rate limits — on one dedicated screen
- **now:** Cross-workspace agent detail — state, session, cost, queue, rate limits — is available on one dedicated screen

## PHASE-013 (`title`)

- **was:** Fleet surfaces — the cockpit reports on every repo it can see
- **now:** Fleet surfaces — the cockpit reports on every repo it can see, not just the open one

## TST-0018 (`title`)

- **was:** Status-diff layer transitions emit once; non-changes and cold seed silent
- **now:** Status-diff layer — transitions emit once, non-changes and cold seed are silent

## TST-0003 (`title`)

- **was:** Unknown POST drains body — HTTP/1.1 keep-alive stays synced
- **now:** Unknown POST drains body — keep-alive stays synced

## CHG-20260721-Agent-Label-And-Per-Project-Sessions (`title`)

- **was:** Agent label follows live signal; ~agents per-project session history
- **now:** Agent label follows the live signal; ~agents screen gets per-project session history

## CHG-20260721-Overview-Declutter (`title`)

- **was:** Overview project-focused; session history to ~agents
- **now:** Overview is project-focused — agent surfaces dropped; session history moves to the ~agents screen

## CHG-20260720-Progress-Counts-Terminal-Resolved (`title`)

- **was:** Overview progress counts terminal-resolved items (retired/superseded)
- **now:** Overview progress counts terminal-resolved items — retired requirements + superseded features complete the bar

## CHG-20260720-Attention-No-Decay (`title`)

- **was:** Attention states no longer decay (REQ-0018)
- **now:** Attention states no longer decay — needs-input/waiting persist until acted or dismissed (REQ-0018)

## CHG-20260720-Index-Case-Canonicalisation (`title`)

- **was:** Index re-roots watcher paths to docs_root case (ISS-0001)
- **now:** Index re-roots watcher paths to docs_root case — /api/render finds files created/modified after cockpit start (ISS-0001)

## CHG-20260720-Usage-Freshness (`title`)

- **was:** Usage block account-global + self-refreshing - freshest wins, poll, manual refresh, as-of
- **now:** Usage block account-global + self-refreshing — freshest wins, poll, as-of caption

## CHG-20260719-Context-Menus (`title`)

- **was:** Context menus & clipboard - native edit menu, terminal menu, dispatch-selection
- **now:** Context menus & clipboard — native edit menu, terminal menu, dispatch-selection

## CHG-20260719-Live-Work-Views (`title`)

- **was:** Live work views - status-diff layer, work tab, Active mode, Now board
- **now:** Live work views — status-diff layer, session work tab, Active nav mode, phase-less Now board

## CHG-20260719-Terminal-Survivability-And-Identity-Guard (`title`)

- **was:** tmux-backed terminal survivability + sidecar identity guard
- **now:** tmux-backed terminal survivability + sidecar identity guard (agents outlive the app; hooks can't cross workspaces)

## CHG-20260509-Cockpit-LLM-Drives-Cockpit (`title`)

- **was:** Cockpit: agent drives cockpit — focus endpoint, CLI, Following toggle, discoverable URL
- **now:** Cockpit: agent drives cockpit — focus endpoint, CLI helper, Following toggle, discoverable URL

## CHG-20260525-Agent-Waiting-Notification (`title`)

- **was:** OS notification on agent `waiting` — first FEAT-0012 task
- **now:** OS notification on agent `waiting` — first FEAT-0012 task; FEAT-0012 plan + 5 remaining tasks drafted

## CHG-20260525-Native-UX-Wins (`title`)

- **was:** Native UX wins: ⌘P, ⌘F, native context menus, drag-drop, multi-window + hiddenInset title bar
- **now:** Native UX wins: ⌘P, ⌘F, native context menus, drag-drop, multi-window — plus FEAT-0009 hiddenInset title bar

## CHG-20260525-Overview-Dashboard (`title`)

- **was:** Overview dashboard: hero strip, phase progress, status donuts, activity histogram + recent CHG feed; plus identicons / colour swatches / emoji icon picks, ⌘P paste-a-path fix, header height alignment, top-bar back/forward + search bar + star pin
- **now:** Overview dashboard + dashboard-adjacent polish (identicons, colour swatches, top-bar back/forward + search + star, paste-a-path, header alignment)

## CHG-20260705-Adopt-Mechanical-Verification (`title`)

- **was:** Adopt project-os mechanical verification: docs validator + blocking hooks + pre-commit/CI, independent-review and docs-audit skills; fixed snapshot drift the validator caught
- **now:** Adopt project-os mechanical verification (validator, blocking hooks, pre-commit/CI) and fix snapshot drift it caught

