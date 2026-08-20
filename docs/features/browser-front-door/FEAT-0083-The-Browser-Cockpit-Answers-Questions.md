---
type: "[[feature]]"
id: FEAT-0083
aliases: ["FEAT-0083"]
title: "The browser cockpit answers questions — the overview and the design register reach the reading surface, and the desk deliberately does not"
status: planned
phase: "[[PHASE-029-One-Tool-Two-Front-Doors]]"
owner: user:edwin
created: 2026-08-09
updated: "2026-08-20"
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: changes-requested
review_note: "Second pass 2026-08-20 (fresh context, separate session): criterion 4's stated measurement is wrong and its pin is defeatable — see the review section at the foot of this note."
source: ["[[ADR-0010-What-The-Browser-Cockpit-Is-For]]"]
goal: "Give the LAN reading surface the two read-only surfaces that answer questions — the project overview and the design register — so a tablet gets the current tool rather than the one that existed before PHASE-008."
requirements: ["[[REQ-0032-Two-Front-Doors-Agree-Or-Differ-On-The-Record]]"]
tasks:
  - "[[TASK-0361-The-Overview-On-The-Reading-Surface]]"
  - "[[TASK-0362-The-Design-Register-Read-Only]]"
  - "[[TASK-0363-The-Read-Only-Guard]]"
release: ""
related: ["[[PHASE-029-One-Tool-Two-Front-Doors]]", "[[RISK-0001-Render-Server-Exposure]]", "[[FEAT-0040-Overview-Rework]]", "[[FEAT-0079-Supervision-From-A-Phone]]"]

---

# The browser cockpit answers questions

## Goal

Mode 1 has no Overview, no Design and no Review. Two of those three are pure reads and belong on the reading surface; the third does not, and saying so is part of the work.

`/api/cockpit/stats` already serves the overview payload and mode 1 already consumes several cockpit APIs, so this is renderer work against endpoints that exist, not new server capability.

## Scope

**In:**

- The project overview in `cockpit.js`, including the phase accordion and the scope rows — the same payload the shell renders
- The design register and read-only artifact framing
- A test that fails if any actuating endpoint becomes reachable from a non-loopback peer

**Out:**

- **The review desk's WRITE half.** Per [[ADR-0010]]: its endpoints refuse non-loopback callers, and a queue of obligations you cannot discharge is worse than no queue. A read-only *digest* of what is owed belongs to [[FEAT-0079]]'s authenticated path, which is designed for it.

  *(**Split 2026-08-20, independent review.** This bullet read *"The review desk"* unqualified and was overturned sixty lines below by `~review` appearing among the eleven owed reading views — an overturned decision left standing in the same note as the decision that overturned it. The later reading is right and the split is the whole point of the stage decomposition: `~review` **reads** what is owed, which nothing gates, while marking and recording go behind the authenticated write path. Reading the queue is not the same act as discharging it, and the original bullet conflated them.)*
- **Every verdict, tick, capture and test-run control.** Reading a design is reading; judging it is not.
- **Feature parity as a goal.** [[ADR-0010]] chose subset-by-classification over parity.

## Acceptance

- [ ] Mode 1 exposes the project overview, rendering the same `/api/cockpit/stats` payload as the shell, with phases and scope rows
- [ ] Mode 1 exposes the design register and can frame an artifact, with no verdict or capture control present in the DOM
- [x] A test asserts that every actuating endpoint refuses a non-loopback peer, and it fails if a new one is added without that check — [[TASK-0363]] done 2026-08-20; `tests/test_remote_peer_refusal.py` sends the requests, `test_every_note_mutating_endpoint_requires_loopback` catches the new route
- [x] Nothing in mode 1 issues a POST to a `note_writes`-backed endpoint — measured **and corrected after review**: `cockpit.js` reaches **five** `/api/` endpoints plus the `/_events` SSE stream (`tab-state`, `terminal`, `cockpit/validation`, `cockpit/nav`, `cockpit/context`), and **exactly one of them is a POST** — `/api/cockpit/tab-state`, which is on the runtime-only open list. No `note_writes`-backed route appears in the client in any form. Pinned by three predicates — no guarded path as a literal, the full endpoint inventory, and a POST count of one
- [ ] [[RISK-0001]] is re-scanned and updated with what this changed

## Links

- Decision: [[ADR-0010-What-The-Browser-Cockpit-Is-For]] — gates this feature; nothing starts until it is accepted
- Requirements: [[REQ-0032-Two-Front-Doors-Agree-Or-Differ-On-The-Record]]
- Paths: `src/project_os_cockpit/static/cockpit.js`, `src/project_os_cockpit/static/cockpit.css`, `src/project_os_cockpit/server.py`

## Widened 2026-08-20 — two of eleven, measured

This feature plans the **overview** and the **design register**. Measured while closing [[TASK-0511]], the gap is larger than two:

| front door | virtual pages |
|---|---|
| `desktop/src/renderer/renderer.ts` | **12** — `~agents` `~checks` `~design` `~features` `~history` `~inbox` `~issues` `~overview` `~publication` `~release` `~review` `~tests` |
| `src/project_os_cockpit/static/cockpit.js` | **2** — `~note` `~root` |

[[ADR-0010]] is `accepted` on **option 4 — parity gated on an authenticated write path**, decided 2026-08-12, and Edwin confirmed parity again on 2026-08-20. So the eleven **reading** views are owed and nothing gates them; `~release` is the twelfth and is gated.

### The eleven, and the order

`~overview` and `~design` already have tasks ([[TASK-0361]], [[TASK-0362]]) and are the right first two: the overview is where a reader lands, and the design register is the one this phase just gave a new group ([[TASK-0516]]).

The other nine, unplanned until now:

`~features` · `~issues` · `~tests` · `~checks` · `~history` · `~publication` · `~review` · `~agents` · `~inbox`

**Deliberately not nine task notes yet.** Each would say *"port view X"* and nothing else, and a task note per view is the thin-note proliferation [[ISS-0077]] warns about — they get minted as work starts, when there is something to say about each. What is recorded here is the **scope**, which is what [[ISS-0246]] asked for and what `planned` was missing.

### The one thing that is not a port

`~checks` and `~review` **carry write paths** on the desktop side — marking a check, recording a verdict. The reading half is owed now; the acting half joins `~release` behind the authenticated write path. Splitting them at the view boundary rather than porting whole is the difference between this being eleven reads and eleven reads plus three writes nobody authorised.

### Why the loopback check is not a detail to route around

[[REL-0001]]'s acceptance pass drove every mutation endpoint over the real LAN interface: **ten of ten returned 403 while reads returned 200** ([[REQ-0027]], [[RISK-0005]]). [[ADR-0010]]: *"The loopback check is not a safety feature on top of an authorisation model. It **is** the authorisation model."* There is no authentication anywhere in this tool.

## Independent review — fourth pass, 2026-08-20

Fresh context, separate session, `model:claude-opus-5`. Verdict: **changes-requested**. Re-measured or re-executed, not read.

The widening is sound and the split is faithful to `ADR-0010` option 4: 12 views, `~release` gated because it composes contents, the other **11** owed as reads, and `~checks`/`~review` split at the view boundary so their write halves stay behind the authenticated path. Decisions 1–3 of the ADR support each part. The 12-against-2 count reproduces (`cockpit.js` implements exactly `~note` and `~root`).

**But an earlier scoping decision is left standing beside the later one that overturns it.** The `## Scope` / **Out** list still reads:

> **The review desk.** Per [[ADR-0010]]: its endpoints refuse non-loopback callers, and a queue of obligations you cannot discharge is worse than no queue.

— unqualified, as current scope. Sixty lines below, `~review` is listed among *"the eleven"* owed reading views, with its acting half deferred. The later reading is the right one; the earlier bullet now contradicts it, and a reader taking the Scope section at face value gets the opposite answer. This is the pattern this phase has been repeatedly bitten by, and the fix is a clause on the Out bullet, not a new section.

## 2026-08-20 — the guard landed, and it was already half there

[[TASK-0363]] is `done`. It is the task this feature said must land **before** the two porting tasks, and closing it first was right for a reason the task did not anticipate: **most of it already existed.**

`test_every_note_mutating_endpoint_requires_loopback` (TASK-0280) has enumerated the POST dispatch for months. It fails when a new route forgets the guard, it names the five runtime-only exemptions individually, and it checks each exemption really writes nothing under `docs/`. That is this feature's third criterion, apparently satisfied.

**It decides by reading source text.** It asserts the substring `_require_loopback` appears in the handler body, and it has never sent a request. Given a guard that is present and disabled —

```python
if False and not self._require_loopback():   # MUTANT
```

— it passes. The new test fails, and the failure shows the remote peer receiving `400 {"error": "'' is not a verdict; expected one of clear, excused, failed, partial, pass, question, rerun"}`. So a dead guard does not just permit the write; it parses the LAN caller's body first and returns the API's internal vocabulary. All 27 guarded routes were confirmed to refuse **before** parsing — every one 403, none 400.

### What this changes about the porting order

Criterion 4 is also ticked, and measuring it was the useful part. `cockpit.js` fetches **exactly two** endpoints today. That number is the baseline the eleven views will move, and it is now pinned in a test — not as a wall, but so that growth appears in a diff. A ported view that brings a desktop write control with it would be refused over the LAN and would *work on the Mac*, which is the confusing half of [[ADR-0010]] that the reading/acting classification exists to prevent. The test asserts against the **guarded set** rather than a list of paths, so an endpoint added tomorrow is in its domain today.

### One finding, filed

The `note_writes` cross-check run in reverse: `retire_check` and `cover_check` are complete write functions reachable from nothing but `tests/`. Not a security finding — unreachable from the dispatch is unreachable from the LAN. But [[TASK-0518]] asks whether 83 rested checks should retire and there is no way to record the answer. [[ISS-0249]].

## Independent review 2026-08-20 (second pass) — criterion 4's measurement is wrong

### "`cockpit.js` fetches exactly two endpoints" is false, and it is the tick's stated evidence

Measured from the file with comments stripped, mode 1's client reaches at least **five** `/api/` endpoints on load — `/api/cockpit/tab-state` (POST, line 145), `/api/terminal` (line 836), `/api/cockpit/validation` (line 1143, via `fetchJson`), `/api/cockpit/nav` (line 1856) and `/api/cockpit/context` (line 2048) — plus `EventSource("/_events")` (line 1160). The three unlisted ones are unconditional: `mountHealthBadge()` runs at line 2220, `loadLeftPane()` and `loadRightPane()` at lines 684-685.

The test's regex `fetch\("(/api/[^"]+)"` sees only a path literal written directly inside `fetch(`, and this file's own idiom for read APIs is `fetchJson(url)` with the URL built by concatenation. So the property `test_the_browser_client_still_only_talks_to_two_endpoints` claims — *"a ported view that starts calling a read API also shows up here"* — does not hold. Executed: inserting `fetchJson("/api/cockpit/stats")`, which is precisely what [[TASK-0361]] will add, leaves all eight tests green.

### The criterion's substance is true; the pin is weaker than the note says

Checked separately: none of the 19 `note_writes`-backed routes appears in `cockpit.js` in any form, so **nothing in mode 1 posts to a write endpoint today**. What is wrong is the measurement quoted as evidence, and the strength of the guard against that regressing.

`test_mode_one_posts_to_nothing_note_backed` matches whole path literals (`f'"{p}"' in js`). Executed: `var wu = "/api/notes/" + "tick"; fetch(wu, { method: "POST" });` — a POST to a loopback-guarded write endpoint, sitting in the reading surface — passes all eight tests. Concatenated URLs are not a contrived form here: `/api/cockpit/nav?mode=` is built exactly that way a few hundred lines below.

### Criterion 3

"Refuses" is verified: 27 of 32 POST routes answer 403 to a peer at `203.0.113.7` over a real socket, re-measured with an independent fixture, none answering 400. "Fails if a new one is added without that check" holds only for handlers named `_serve_*` — see the review section on [[TASK-0363]], which also carries a blocking finding about a guard that is called and its result ignored.

**Recommended before re-ticking:** restate the baseline as the endpoints actually reached, and widen the inventory to `fetchJson` and concatenated URLs. Asserting on the set of `/api/` literals present in the file, rather than on `fetch(` call sites, would close both findings at once.
