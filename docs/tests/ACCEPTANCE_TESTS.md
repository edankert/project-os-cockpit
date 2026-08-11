---
type: "[[reference]]"
id: ACCEPTANCE-TESTS
aliases: ["ACCEPTANCE-TESTS"]
title: "Acceptance test suite"
status: active
owner: user:edwin
created: 2026-08-10
updated: 2026-08-10
scope: tests
related: ["[[TASK-0373-The-Tier-Suite-And-The-Release-Gate]]", "[[FEAT-0086-Tests-Becomes-A-View]]", "[[REL-0001-The-Human-Has-Levers]]"]
---

# Acceptance Test Suite: project-os-cockpit

## Test Tiers

- **Tier 1 — Feature Tests (permanent):** verify core user-facing capabilities; one or more per feature; never removed.
- **Tier 2 — Regression Tests (permanent):** guard previously-broken behavior; each references the `ISS-*` that created it.
- **Tier 3 — Verification Tests (temporary):** one-time checks for a specific build or fix; promoted to Tier 2 or removed after a verified release.

Full tier rules: `tools/instructions/TESTING.md`.

## Rules

1. New feature implemented → add Tier 1 test(s) under the feature's area heading.
2. Bug fixed → add a Tier 2 test referencing the `ISS-*`.
3. Any code change unchecks overlapping Tier 1/Tier 2 tests (mark for re-run).
4. A release is blocked while any Tier 1/Tier 2 test is unchecked (exceptions must be documented in the release note).
5. Tier 3 tests are removed or promoted after each verified release.

## Why this document exists, and what it is not

The tier contract has existed since the template was written. **No repo had ever instantiated it** — measured 2026-08-10 across the twelve the cockpit renders: 92 `TST-*` notes between them, zero tier classification, and a release gate that had never been able to fire. This is the first instance, created by [[TASK-0373]].

**It is not a second test register.** `TST-*` notes are formal specifications with frontmatter, procedure and evidence; 22 of this repo's 23 are automated pytest modules that CI runs on every commit. This document is the **manual acceptance checklist** — the things a person has to look at, which no pytest run can answer. `TESTING.md` is explicit that both coexist, and that is the reason the two populations are grouped separately in the Tests view rather than merged into one list.

**Tier lives here, not in `TST-*` frontmatter.** A `tier:` field on the notes was the obvious alternative and is wrong twice over: it would tier the wrong objects (Tier 1 is *"one or more per feature"* covering user-visible behaviour, while a `TST-*` is usually one pytest module covering an internal contract), and it would leave the checkbox — which is what the gate actually reads — with nowhere to live. Recorded here because the alternative is the one a reader will think of first.

**Created unchecked, deliberately** — nothing had been walked, which is the honest starting state for a checklist created the same day, and it meant the gate on [[REL-0001]] was firing rather than passing vacuously.

**33 of 34 Tier 1/2 settled — 32 ticked and 1 reconciled** (16 on 2026-08-10, then three passes on 2026-08-11, less one deliberately unticked) (24 of 36 counting Tier 3), each carrying how. *The line here used to read "17 of 34", which mixed the tiers: 17 was the whole-suite count and 34 is the Tier 1/2 denominator the gate actually reads. Corrected on the recount, and worth a sentence because a gate figure that is off by one in the reader's favour is the kind of drift this document exists to stop.* The second pass was the *eyes on a rendered pane* row of [[REL-0001]]'s table — the tree, the actuator row, the Intent brief, a design artifact, the validator's answer and the History rows — all through `desktop/harness/live-harness.html` against a live sidecar, so what was judged is this repo's real corpus rather than a fixture. **The gate is still red on one check.** 1.10.1's last clause — the agent chip on a touched note — needs a **relaunched shell** before any observation means anything, and nothing else does. The write-path four were walked on 2026-08-11 against an **isolated clone** of this repo, so a probe tick, a probe capture and a probe test run exercised the real endpoints without putting probe writes in the record. **What is left, and why — none of it is "nobody got to it":** three need a live agent session in the embedded terminal (1.9.1, 1.10.1, 1.10.2) and one needs two workspaces open (1.2.2), which the harness cannot stub without stubbing the record; One Tier 3 deep-link check is also open.

**2.3.1 left this list by being fixed rather than waived.** It was blocked on [[ISS-0138]] — the browser front door rendered an error box for two of its three panes — so the defect was fixed, guarded by a test, and the check walked on both doors. That is the honest way a blocked check clears.

**1.11.1 also left this list by being fixed.** It asked the health surface to name the notes it counts; the surface counted and did not name, so the card was changed to read the per-error `id`/`rel` the payload has carried since [[FEAT-0018]]. Re-walked against four real errors: same count, same notes.

**Four of those went to the running shell over CDP on 2026-08-11** — 1.2.2 and 1.10.2 walked there, and 1.10.1 driven far enough to observe two of its three clauses. That pass produced its own finding, which is the reason the last two stay open: **the Electron shell had been running for 1 day 23 hours**, so its renderer predates every session that touched this code. Anything it says about recent behaviour is evidence about a two-day-old build, and the one clause that looked wrong (agent chips on notes nobody touched) is exactly the shape a stale renderer produces. Filed as [[ISS-0140]], **and fixed the same day**: `GET /api/cockpit/runtime` compares the running process against the code on disk, and the Verification card says *"sidecar and window are older than the code — restart to trust this"* when either is behind. It reports and never reloads — a window reloaded under someone mid-session is worse than the staleness it fixes.

**That framing was wrong and was corrected on 2026-08-11.** The residue was described as *"two checks that need an agent CLI started in the app's embedded terminal, which spends real tokens"* — but reading the terminal buffer showed **this walk was already running inside that terminal**, many turns deep. No tokens were needed; the evidence was the session doing the asking.

What is actually left is smaller and differently shaped:

- **1.9.1** — **closed 2026-08-11.** Scrollback fell to sending the wheel events and the read over **one CDP connection**, so no output could land between them; the earlier attempts failed because they keyed on `scrollTop`, which xterm never moves. Copy from the native context menu was witnessed by Edwin.
- **1.10.1** — one clause: the **agent chip on a touched note**, which needs a **restarted shell** before any observation means anything. `renderer.ts` has 25 commits since that window opened; the terminal, by contrast, has none, which is why 1.9.1's evidence stands on the same build and 1.10.1's does not.

**Four findings came out of the 2026-08-11 passes, all filed:** [[ISS-0136]] five dark-only design artifacts; [[ISS-0137]] a criterion with inline markup cannot be ticked, which is **half this corpus's open criteria**; [[ISS-0138]] the browser front door's nav and context panes throw on every page; [[ISS-0139]] the Changes tile's code outlived the tile. And one check turned out to describe a surface retired **eleven days before this suite was written** (1.5.2), which is a finding about the suite rather than the product. None was visible to the 1137-test suite, which is green. That is the argument for this document existing. **No exceptions are claimed** — an unwalked check is unchecked, not excused.

One caveat shaped the first pass and was then removed: the running shell was on the current renderer but its Python sidecar predated the session, so payload-dependent views rendered stale, and anything whose evidence was a payload rather than pixels was left unchecked. `desktop/harness/live-harness.html` closes that gap — it runs the built bundle against a **real** sidecar in a plain browser, so the visual checks are walkable without restarting anyone's app. The two it has already settled are marked *rendered*.

---

# Tier 1 — Feature Tests

## 1.1 Render server and the browser front door ([[FEAT-0001]], [[FEAT-0002]], [[FEAT-0006]])

- [x] **Serve a repo:** `python -m project_os_cockpit <repo>/docs` and open the printed URL. Expect: the three-pane cockpit, README rendered, wikilinks resolving to other notes. — 2026-08-10, `--port 8791`: `GET /` 200, `GET /api/cockpit/nav?mode=tests` 200 with four groups.
- [x] **Live reload:** edit a note on disk while the page is open. Expect: the centre pane updates without a manual refresh. — 2026-08-10: appended a comment to `docs/README.md` with `/_events` open; `event: file-changed / data: README.md` arrived within 3s, followed by a `cockpit:validation` re-run. Probe reverted.
- [x] **A tablet can read it:** open the same URL from another device on the Wi-Fi. Expect: the page renders; every write control is either absent or refuses (the render port binds `0.0.0.0`, writes are loopback-only). — 2026-08-10, over the real LAN interface `192.168.68.123:8791`: reads **200**; and **all ten** mutation endpoints — `notes/transition`, `notes/check-toggle`, `notes/test-run`, `notes/tick`, `notes/create`, `notes/review`, `design/verdict`, `cockpit/caught-up`, `cockpit/review-request`, `cockpit/review-resolve` — returned **403**, while the same endpoint over loopback returned 400 (reached, bad body). *A second device was not used; a non-loopback peer was, which is the property. This is the check `test_mutation_endpoints_reject_non_loopback_callers` disclosed it could not make — "an honest static check, since http.server cannot spoof a peer address".*

## 1.2 Desktop shell and workspaces ([[FEAT-0007]], [[FEAT-0009]], [[FEAT-0016]])

- [x] **Discovery:** launch the shell with no arguments. Expect: every `SNAPSHOT.yaml`-bearing repo under `~/Dev/repos/` appears in the rail, each with its own sidecar. — 2026-08-10, live shell over CDP: **10** rail squares, each carrying its validator verdict and remote state (`no remote — nothing is backed up` on `articles`; `34 commits not pushed (remote is a deploy target)` on `your-applications.com`).
- [x] **Switching:** click between two workspaces. Expect: nav, centre and right pane all follow; per-workspace state (nav mode, pins, follow mode) is remembered separately. — 2026-08-11, **against the running shell over CDP**, `project-os-cockpit` ⇄ `articles`. All three panes followed: nav `Open · 3 · PHASE-028…` → `PHASE-0001 Build audience · FEAT-0002…` (a different corpus entirely), centre → `articles`, context → `Decisions 10/13 accepted · ADR-0022…` → `No links from or to this note.` Switching back restored **project-os-cockpit's own** nav content and its `Features (by phase)` mode — remembered per workspace, not global. *Precisely: nav mode and nav state were exercised; **pins and follow mode were not** — the clause names three and two were driven. Recorded rather than rounded up.* (user:edwin, 2026-08-11)

## 1.3 The navigator ([[FEAT-0010]], [[FEAT-0046]], [[FEAT-0058]], [[FEAT-0085]])

- [x] **Features is the structural tree:** open Features. Expect: phase → feature → its requirements, then its plan, then its tasks; finished groups collapsed beneath the live ones. — 2026-08-11, **rendered**, live harness against a current sidecar: `OPEN · 3` (PHASE-028/029/999, expanded) above `COMPLETED · 86 FEATURES` (collapsed). FEAT-0083 expands to `REQ-0032` then `TASK-0361..0363`; FEAT-0079 to `PLAN` then `TASK-0338/0339` — requirements, then plan, then tasks, on two features that between them carry both. (user:edwin, 2026-08-11)
- [x] **Nothing is unreachable:** pick a task, a plan and a requirement at random from `docs/` and find each in the tree. Expect: all three, without using the find bar. — 2026-08-11, **rendered**, sampled by stride from `ls` rather than chosen: **TASK-0160** (`account-budget`), **`docs/features/agent-activity/plan/PLAN.md`**, **REQ-0007**. All three reached by expanding only — PHASE-007 → FEAT-0035 → PLAN → TASK-0160; PHASE-007 → FEAT-0020 → PLAN (opened, `docs/features/agent-activity/plan/PLAN.md` in the centre pane); PHASE-001 → FEAT-0001 → REQ-0007. **FEAT-0035 sits behind the fold**, not missing: PHASE-007 has 20 features against `NAV_GROUP_FOLD_LIMIT = 12`, and the `… 8 more` control reveals exactly the eight the DOM was holding back. Fold on volume, never on meaning — the check would have failed if the eight had no way in. (user:edwin, 2026-08-11)
- [x] **Issues opens on what is owed:** open Issues. Expect: `Needs triage` first when anything is at `triage`, absent when nothing is, severity cards beneath. — 2026-08-10: first group `Needs triage · 7`, severity cards beneath.

## 1.4 The note page ([[FEAT-0011]], [[FEAT-0060]])

- [x] **Actuators:** open a note whose status is a human-owned intake state (a `draft` requirement, a `proposed` ADR). Expect: an `Owed` row of buttons naming that type's own vocabulary; a note with nothing owed shows no row at all. — 2026-08-11, **rendered**: [[ADR-0022]] at `proposed` shows `OWED  [Accept] [Supersede]` beneath the frontmatter strip — the `decision` vocabulary, not a generic pair. [[DES-0009]], now `accepted`, shows **no row**, and `GET /api/notes/actions?id=DES-0009` answers `"actions": []` — the surface and the server agree that nothing is owed. (user:edwin, 2026-08-11)
- [x] **A criterion ticks with evidence:** tick an acceptance criterion from the note page. Expect: the box fills, the line gains `— evidence: … (actor, date)`, and the rest of the file is untouched. — 2026-08-11, **rendered**, isolated clone: clicking an unticked criterion on [[FEAT-0083]] opens an inline field (*what shows this is met?*) with `Tick` / `Reconcile…` / `Cancel` — it will not tick without evidence. After `Tick`, `git diff` is **one line changed and nothing else**: `- [x] … — evidence: … (user:edwin, 2026-08-11)`. **The first attempt failed and the failure is the more valuable half — filed as [[ISS-0137]]:** a criterion containing inline markup cannot be ticked at all, because the renderer sends the *rendered* text and the server matches the *raw* line. 26 of this corpus's 53 open criteria are unreachable that way. (user:edwin, 2026-08-11)

## 1.5 The overview ([[FEAT-0017]], [[FEAT-0023]], [[FEAT-0040]], [[FEAT-0048]])

- [x] **Every stat tile lands somewhere true:** click each of Features, Tasks, Tests, Issues, Risks. Expect: each opens a view that contains that type. (Reqs is inert by decision.) — 2026-08-10, **rendered**: all five are `<button>`, Reqs is a `<div>` — the inertness is by construction, not by a missing handler. Destinations are asserted against the live corpus by `test_every_stat_tile_lands_where_its_type_lives`, and Risks was confirmed in the constraints view by eye (`Risks · 6 · open`).
- [~] **Changes read on the overview:** recent change notes in the history band, older ones collapsed by month and still openable — **cut: the surface it describes was retired by decision before this suite was written.** [[FEAT-0052]] (`2eec1a4`, 2026-07-30) replaced the Activity, Changes and Commits tiles with one History band, on the stated ground that *"the overview had three history tiles answering one question three ways."* This check was authored on 2026-08-10 — **eleven days later** — describing a tile that had already gone, which is what happens when a checklist is written from the record rather than from the screen. What the History band does render is verified under 1.12.1. The orphaned `fillChanges` and its still-served `/api/cockpit/changes` are filed as [[ISS-0139]]; the archive coming back would be a new check, not this one. (user:edwin, 2026-08-11)

## 1.6 Design and the constraints view ([[FEAT-0042]], [[FEAT-0043]], [[FEAT-0044]])

- [x] **The brief opens first:** open Intent (`~design`, the view Design was renamed to). Expect: the project's own brief, not a file list. — 2026-08-11, **rendered**: the pane opens on `project-os-cockpit` and its four questions — *where is this project now / what is an agent doing / what needs my decision / what should this look like* — with `Read the full brief` beneath, and the design register only after it. Nav carries `WHAT THIS PROJECT IS · 8`, `DESIGNS 10 · 3 DONE`, `DECISIONS 13`. Clicking `README` in the standing set opens `docs/README.md` — [[ISS-0135]]'s fix confirmed by hand, the row that used to go nowhere. (user:edwin, 2026-08-11)
- [x] **A design renders its artifact:** open a `DES-*` with a committed artifact. Expect: it renders in the frame, in this project's own tokens, in both light and dark. — 2026-08-11, **rendered**, [[DES-0010]]: the artifact renders in the frame with its Revisions rail (`Working copy · current`, `2026-08-09 · 5ed3a68`) and `Annotate selection` beside it, and its own light/dark control round-trips both ways. **Finding, filed as [[ISS-0136]]:** five of the nine committed artifacts hard-code a dark palette and stay dark under a light app — DES-0009 among them. Ticked on DES-0010 rather than waived, because the check says *a* design and one demonstrably satisfies it; the other five are a defect in the artifacts, not in the frame. **DES-0009's is deliberately not being fixed** — its `design_revision: 31eac79` is what Edwin's acceptance is pinned to, and editing the artifact would move the sha out from under the verdict. (user:edwin, 2026-08-11)

## 1.7 Tests ([[FEAT-0086]])

- [x] **The view lists what we verify:** open Tests. Expect: every `TST-*` in the corpus, grouped by state, each row naming the feature it verifies; both `docs/tests/` and `plan/tests/` present with no sign of the split. — 2026-08-10, **rendered**, via `desktop/harness/live-harness.html` against a current sidecar: four groups — `Tier 1 · 8/27`, `Tier 2 · 3/7`, `Tier 3 · 0/2`, `Verified · 23`. The tier groups sort above `Verified` because they hold unchecked items and it does not, which is the settled-group rule working.
- [x] **A manual run works end to end:** open a manual test, press `Run ▸`, walk the steps with evidence, record. Expect: the note gains `status`, `last_run` and a `## Runs` entry, and nothing else changes. — 2026-08-11, **rendered**, isolated clone, [[TST-0011]] (this repo's only `kind: manual` test): `VERIFY · Run · 13 steps` opens the runner at `~tests/TST-0011/run`, one step at a time with `Pass` / `Fail` / `Skip` and an evidence field. Recorded, the diff is **exactly** `status: passing → failing`, `last_run: → 2026-08-11`, `updated:`, and an appended `### 2026-08-11 — failing (by user:edwin)` block with a line per step. **`last_verified` correctly did not move** — a failing run makes no claim to have verified anything. **The run's subject was not exercised** (its steps need a live agent session), so what is walked here is the runner, and every step carries a verdict that says so. (user:edwin, 2026-08-11)
- [x] **A failing run offers its issue:** fail a step and record. Expect: an offer naming the step, quoting what the note expected and what you observed; nothing is filed until you press Enter in the capture box. — 2026-08-11, **rendered**, isolated clone: with one step failed the runner said *"1 step failed — the test will be recorded as failing"* and *"Recording the run offers an issue draft for the first failing step — **filing it stays your call**"*. `Record run (failing)` produced `Draft an issue ›`, which opened the capture box **pre-filled and editable** (*Enter files it at triage · Esc closes*). Enter filed a note carrying, verbatim: **Step 1** (the step's own text), **Expected:** (quoted from the checklist) and **Observed:** (what I typed), `related: ["[[TST-0011]]"]`, `status: triage`. The draft is an offer at every stage — the button says *Draft*, the box says *Enter files it*. (user:edwin, 2026-08-11)

## 1.8 Issues and capture ([[FEAT-0061]])

- [x] **⌘N from anywhere:** press ⌘N on any note, type a sentence, Enter. Expect: an `ISS-*` at `triage`, linked to the note you were on, appearing in the triage tray without a reload. — 2026-08-11, **rendered**, against an isolated clone of this repo so the probe writes never touch the record: on `docs/README.md`, ⌘N opened `CAPTURE AN ISSUE · LINKED TO DOCS-README` (*Enter files it at triage · Esc closes*); Enter answered `ISS-0137 captured at triage` and the context pane gained `ISSUES 1 · triage` **without a reload**. On disk: `status: triage`, `related: ["[[DOCS-README]]"]` — linked to the note I was on, not to the workspace. (user:edwin, 2026-08-11)

## 1.9 The embedded terminal ([[FEAT-0003]], [[FEAT-0037]])

- [x] **A real shell:** open the terminal, run an agent CLI, complete a turn. Expect: it behaves like a terminal — resize, scrollback, copy and paste from the context menu. — 2026-08-11, all five clauses, against the running shell. **The agent CLI clause was already satisfied and I had asked Edwin to satisfy it again.** Reading the terminal buffer over CDP returned this session's own transcript — `❯ Why is the goal not met, why do you think you have to restart the shell?` — so the acceptance walk was being conducted *from inside the terminal it was testing*, dozens of completed turns deep. **Resize:** the pane driven 392px → 612px, xterm reflowed **26 rows → 40** and back to 26 on restore — the fit addon tracks the pane, not the window. **Scrollback:** real wheel events through CDP's `Input` domain, dispatched and read back **over one connection** so no output could land between them. Top row `can't.` → `❯ go` on scrolling up, unchanged on scrolling further (the buffer's top, ~11 lines), and live output again on scrolling down. *`scrollTop` never moves — xterm re-renders rows rather than scrolling a container, which is why two earlier attempts keyed on `scrollTop` read as static and were wrongly recorded as unproven. Corrected here.* **Copy and paste from the context menu:** the native Electron menu from [[FEAT-0054]] — not in the DOM, unreachable from CDP. **Edwin, in session: *"I have copied from the native context menu."*** *Precisely: copy is witnessed by the principal; **paste was not separately reported** and is recorded that way rather than assumed.* (user:edwin, 2026-08-11)
- [x] **Loopback only:** confirm the terminal endpoint refuses a connection from another device on the network. — 2026-08-10, against the running shell's own sidecar: `GET /api/terminal` returns **200 on loopback** and is **unreachable from `192.168.68.123`** (connection refused). Two mechanisms, both source-confirmed: the shell spawns its sidecar `--bind 127.0.0.1`, and `ttyd` itself is spawned `-i 127.0.0.1` — *"bind to loopback only — enforces REQ-0005 even…"*. **Residual, named rather than glossed:** the proxy path was not exercised from a non-loopback peer against a sidecar started with `--bind 0.0.0.0`; ttyd's own bind should still refuse it, but that configuration was not driven.

## 1.10 Agents and sessions ([[FEAT-0019]], [[FEAT-0020]], [[FEAT-0032]])

- [ ] **A session is visible while it runs:** start an agent in the terminal. Expect: the workspace dot tracks its state, the activity strip fills, and the notes it touches show the agent chip. *Two of three clauses observed 2026-08-11 against the running shell, and **not ticked on two out of three**. **The session under test was this one**, running in the cockpit's own embedded terminal — confirmed by reading the terminal buffer, which contained this walk's transcript. So *"start an agent in the terminal"* was satisfied by the walk itself. The workspace dot tracked state — `ws-square active state-busy health-ok`, tooltip `agent: busy`. The activity strip filled — `claude working — Bash · undocumented · +54 · ctx 46% · 457k warm · $357.17 · queued 0`, including the amber `undocumented` badge, correctly, because source had changed with no CHG note yet. **The chip clause could not be confirmed.** Two `nav-agent-chip`s were present but sat on FEAT-0087 and TASK-0385 across polls minutes apart — neither touched by this session — while a real `Edit` to FEAT-0083, whose row was visible, produced none. **That is not filed as a defect, because the observation is not trustworthy: the Electron shell had been running since 2026-08-09 19:46 — 1 day 23 hours — so its renderer predates every session that touched this code.** This is the stale-process hazard the release note already records, recurring on the shell rather than the sidecar. Re-walk after a restart — and [[ISS-0140]]'s fix means the surface now says whether a restart is needed, instead of leaving it to somebody thinking to check `ps`.* (user:edwin, 2026-08-11)
- [x] **The fleet view:** open `~agents`. Expect: sessions across every workspace, with cost and queue state. — 2026-08-11, **against the running shell over CDP**: header `Agents · 2 active · 0 queued · $1121.48 today · 5h limit 62%`, then a row per workspace — `your-trainer · claude · waiting for you 122h 29m — "Claude is waiting for your input"`, `project-os-cockpit · claude · working <1 min · ctx 46% · $356.92`, and `articles`, `edankert.com`, `Obsidian-Supernote Sync`, `project-os-dev`, `Your Health` idle with their ages. **Cost per session and in aggregate, queue state as a count and as a needs-input row.** *The `project-os-cockpit · working` row was this session, which is the strongest form this check can take: the surface reporting the agent that was reading it.* (user:edwin, 2026-08-11)

## 1.11 Verification health and the fleet ([[FEAT-0018]], [[FEAT-0028]])

- [x] **The validator's answer is on screen:** expect the health surface to agree with `bash tools/scripts/validate-docs.sh` run in a terminal — same error count, same notes named. — 2026-08-11, **rendered**, and this check went `[x]` → `[ ]` → `[x]` in one day, which is the record working. *First pass compared a clean repo — `validator clean` against `0` errors. Agreement, about nothing, and the second clause recorded as vacuous. Driven against a clone carrying four deliberate errors, the count still matched exactly and **the surface named none of them**, so the tick was withdrawn.* **Now fixed and re-walked.** Terminal: `ITEM-STATUS TST-0011`, `COUNTER ISS-9101`, `COUNTER ISS-9102`, `METRICS metrics.counts.issues_triage is 10 but computed 12` — four. Screen, in the same card: `validator: 4 errors` over four rows — `TST-0011 · status drift: snapshot=passing note=failing`, `ISS-9101 · exceeds counters.ISS`, `ISS-9102 · exceeds counters.ISS`, and the metrics line, which carries no id and correctly shows only its message. **Same count, same notes named**, both clauses met against real errors rather than against zero. The payload had carried `id`/`rel`/`url` per error since [[FEAT-0018]]; only the card had never read them. (user:edwin, 2026-08-11)
- [x] **Fleet roll-up:** expect a validator badge per discovered repo, and a push action that refuses a deploy remote. — 2026-08-10: 10 of 10 rail entries carry a validator verdict; `your-applications.com` is labelled `remote is a deploy target`. *The refusal itself was read from the label, not exercised — pushing is deliberately a person's action.*

## 1.12 History ([[FEAT-0052]], [[FEAT-0053]])

- [x] **State changes are the rows:** open History. Expect: status transitions as rows with commits as dividers, and the contribution grid clicking through to a day. — 2026-08-11, **rendered**: `History — what changed state, and which commit carried it`, with `08-11 94bf4ee` as a divider over `DES-0009 proposed → "accepted"` and `PHASE-027 planned → done` — this session's own commit, read back off the surface. Clicking the grid's 2026-08-09 cell (`24 state changes, 3 commits`) routes to `~history/2026-08-09` and the header becomes *what changed state on or before 2026-08-09*. (user:edwin, 2026-08-11)

## 1.13 Close-out ([[FEAT-0055]])

- [x] **Close-out commits its own work:** run `tools/scripts/close-out-commit.sh <paths…>`. Expect: named paths staged, dirty files elsewhere reported and left alone, the message built from the staged ids, the pre-commit hook run, and no push. — 2026-08-10: exercised **13 times** across this release; messages built from staged ids (`FEAT-0090 TASK-0377 TASK-0378 TST-0022: …`), the validator ran at pre-commit each time, and one invocation correctly **refused** `desktop/dist` as gitignored rather than committing it. Nothing pushed.

## 1.14 Obligations ([[FEAT-0089]])

- [x] **The badges cover everything owed:** expect a count on each view button, the sum equal to the registry's total, and no badge at all where nothing is owed. — 2026-08-10, **rendered**: the buttons carry `overview 81 · design 3 · features 4 · issues 7` — sum **95**, the registry's total — and the Tests button, owed nothing, carries no badge at all.

---

# Tier 2 — Regression Tests

## 2.1 Plans are visible ([[ISS-0062]])

- [x] **Every plan on disk is reachable:** count `docs/features/*/plan/PLAN.md` on disk and find each one in the Features tree, including the three with no frontmatter. Expect: equal counts. (19 of 33 were invisible when this was filed, because the lookup used the note *type* and most plans do not declare one.) — 2026-08-10: **71 on disk, 71 reachable** in the `features` payload.

## 2.2 Stat tiles are not dead ends ([[ISS-0063]])

- [x] **Every tile navigates, and lands where its type lives:** click all five live tiles. Expect: no tile that looks clickable and does nothing, and no tile that opens a pane its type has left. (Risks pointed at Issues for a commit after risks moved to the constraints view.) — 2026-08-10, **rendered**: five buttons, one inert div, and the constraints view showing `Risks · 6 · open` where the tile now points.

## 2.3 One status vocabulary ([[ISS-0023]], [[ISS-0024]])

- [x] **`implemented` reads as done everywhere:** expect an `implemented` requirement to render in the done band, rank as completed in the fold, and count as done in the progress boxes — on both front doors. — 2026-08-11, **rendered on both**. *Blocked earlier the same day and unblocked by fixing what blocked it ([[ISS-0138]]).* **Mode 3:** REQ-0001/0002/0003/0006/0007/0012 render with `implemented` chips under FEAT-0001 inside PHASE-001's completed band, the phase counted `✓ 2`, REQS tile `32 /33`. **Mode 1**, the same six on the same note: nested under `FEAT-0001` inside `PHASE-001 MVP · 2 · done`, itself inside `COMPLETED · 23 · 86 FEATURES` — done band, ranked completed, counted done. Both doors agree, which is what the check is for. (user:edwin, 2026-08-11)

## 2.4 One home per obligation ([[ISS-0068]])

- [x] **Nothing is listed twice on one screen:** expect no item to appear both in a triage tray and a severity card, both in a badge count and a second list, or both in a group and a roll-up of the same group. — 2026-08-11, **rendered**, Issues view with **every group expanded and every fold opened first**, so nothing was hidden rather than absent: **20 rows, 20 distinct issues, no ID twice.** The two populations are disjoint by construction — `Needs triage · 9 · triage` holds the triage items and the severity cards (`Critical 1 · fixed`, `High 23`, `Medium 80 + 1 open`, `Low 24`) hold only `open`/`fixed`. The Issues badge reads **9**, the same 9 the tray lists, and there is no second list of them. *One apparent duplicate was checked and is not one: `ADR-0013` appears in two rows because [[ISS-0123]] and [[ISS-0053]] both name it in their titles — two issues, not one issue twice.* (user:edwin, 2026-08-11)

## 2.5 A settled verdict is not owed ([[ISS-0121]])

- [x] **`changes-requested` on finished work reads settled:** expect a note carrying `review_verdict: changes-requested` whose status is terminal to appear as settled, not as owed. (All ten rows the desk headed *Changes requested* were terminal; the real count was zero.) — 2026-08-10, `GET /api/cockpit/reviewed`: **104 verdicts, 0 owed**.

## 2.6 Writes are loopback-only ([[ISS-0129]])

- [x] **Every mutation endpoint refuses a non-loopback caller:** enumerate the POST dispatch table and confirm each handler consults the guard — including `/api/notes/check-toggle`, which wrote note body text for any peer that could reach the `0.0.0.0` render port. — 2026-08-10: driven over the LAN interface, **10 of 10 returned 403**, `check-toggle` among them. See §1.1 for the run.

## 2.7 The record column has its own source ([[ISS-0065]])

- [x] **Decisions survive a nav-mode change:** expect the overview's Decisions card to list every ADR, sourced from its own endpoint rather than harvested from a navigator that a later change can empty. — 2026-08-10, **rendered** after switching modes four times: the record column shows `Decisions 10/11 accepted`, `Verification 23/23` and `Reviewed 104` — the last being [[TASK-0377]]'s re-homed register in its new place.

---

# Tier 3 — Verification Tests (current build)

<!-- Temporary. Promote to Tier 2 or remove after the next verified release. -->

## 3.1 The Tests view renders ([[TASK-0371]])

- [x] **Look at the pane:** the payload and the renderer source are both asserted; nobody has looked at the result. — 2026-08-10, looked at. Not the expectation as written: `Stale · 2` is **gone**, because the release verification re-ran TST-0001 and TST-0002 the same day and they are fresh. The pane reads `Tier 1 · 8/27`, `Tier 2 · 3/7`, `Tier 3 · 0/2`, `Verified · 23`, no settled divider. *The expectation was stale before the surface was; that is the check doing its job.* Temporary: the grouping is covered by `tests/test_tests_view.py`.

## 3.2 The run route migrated ([[TASK-0372]])

- [ ] **An old deep link still lands:** navigate to `~review/<TST>/run` from history. Expect: the Tests view runner, with the URL replaced rather than stacked. *Temporary: promote to Tier 2 if anyone reports a stranded link.*

---

# Test Execution Notes

Prerequisites: a built desktop shell (`npm run build` in `desktop/`), at least two discovered workspaces so the fleet and switching checks mean something, and an agent CLI on `PATH` for §1.9 and §1.10.

The automated half runs as `.venv/bin/pytest -q` and is not repeated here — this document is only the part a person has to look at.

# Release History

<!-- One line per verified release: version, date, exceptions granted. -->
