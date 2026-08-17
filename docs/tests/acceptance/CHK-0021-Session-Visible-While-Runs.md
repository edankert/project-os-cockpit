---
type: "[[check]]"
id: CHK-0021
aliases: ["CHK-0021"]
title: "A session is visible while it runs"
status: active
owner: user:edwin
created: 2026-08-17
updated: 2026-08-17
tier: 1
area: "Agents and sessions"
section: "1.10"
ordinal: 10
mark: "x"
verdict_date: ""
verdict_reason: ""
invalidated_by: {}
automation: manual
covered_by: []
covers: ["[[FEAT-0019]]", "[[FEAT-0020]]", "[[FEAT-0032]]"]
burden: []
evidence: []
migrated_from: "tests/ACCEPTANCE_TESTS.md#1.10.1 @ 7de1a86"
related: []
---

# A session is visible while it runs

start an agent in the terminal. Expect: the workspace dot tracks its state, the activity strip fills, and the notes it touches show the agent chip. — **2026-08-11, all three clauses, on current code.** *Clause 1 first, because the entry below never stated it and independent review had to establish it from the process tree: **the agent was in the cockpit's own embedded terminal** — the walking session's shell is a child of `tmux -L cockpit` under `project-os-cockpit-desktop/instrument/`, and its session id is the `728aaf53…` that appears in the payload evidence below. The clause was carried silently from the struck-through original, which is not the same as carrying it.* Venue: `desktop/harness/live-harness.html` in front of a sidecar started from this working tree, one origin via a local proxy — chosen over Edwin's window because the requirement was never *a relaunched shell*, it was **a current renderer against a current sidecar**, and the harness supplies both without restarting anybody. Currency is not assumed: [[ISS-0140]]'s own `GET /api/cockpit/runtime` answers `sidecar_stale: false`, its first use. **Baseline first** — 482 nav rows in the Features tree, **0** `nav-agent-chip`, and `/api/cockpit/state` reporting this session (`728aaf53…`) with `work_notes: []`. Then one real edit, to `docs/issues/ISS-0140-…md`; the payload gained `work_notes: ["issues/ISS-0140-The-Shell-Goes-Stale-Silently.md"]`. On the next nav build: **exactly one chip in 141 rows**, on ISS-0140 and nowhere else, reading `agent`, titled *"A live agent session is working on this"*. Nothing else moved. The other two clauses stand on the same build: `ws-square active state-busy`, tooltip `agent: busy`; strip `claude working — mcp__claude-in-chrome__javascript_tool · ctx 10% · 123k warm · $2.04`. **And the observation this check was held open for was not a defect.** `.cockpit/sessions.json` records the 2026-08-11 session (`cedfddb4…`) with FEAT-0087 and TASK-0385 in its own `work_notes` — it *had* touched both, earlier in its life. The chips were right; the reader took *"the notes it touches"* to mean *since the current prompt* and read a correct surface as a wrong one. Held open for a stale renderer, closed by finding the surface had been telling the truth. (user:edwin, 2026-08-11) *The original entry, kept because what it got wrong is the point:* *Two of three clauses observed 2026-08-11 against the running shell, and **not ticked on two out of three**. **The session under test was this one**, running in the cockpit's own embedded terminal — confirmed by reading the terminal buffer, which contained this walk's transcript. So *"start an agent in the terminal"* was satisfied by the walk itself. The workspace dot tracked state — `ws-square active state-busy health-ok`, tooltip `agent: busy`. The activity strip filled — `claude working — Bash · undocumented · +54 · ctx 46% · 457k warm · $357.17 · queued 0`, including the amber `undocumented` badge, correctly, because source had changed with no CHG note yet. **The chip clause could not be confirmed.** Two `nav-agent-chip`s were present but sat on FEAT-0087 and TASK-0385 across polls minutes apart — neither touched by this session — while a real `Edit` to FEAT-0083, whose row was visible, produced none. **That is not filed as a defect, because the observation is not trustworthy: the Electron shell had been running since 2026-08-09 19:46 — 1 day 23 hours — so its renderer predates every session that touched this code.** This is the stale-process hazard the release note already records, recurring on the shell rather than the sidecar. Re-walk after a restart — and [[ISS-0140]]'s fix means the surface now says whether a restart is needed, instead of leaving it to somebody thinking to check `ps`.* (user:edwin, 2026-08-11)
