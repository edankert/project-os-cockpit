---
type: "[[change]]"
id: CHG-20260813-Four-Bugs-From-The-Suggested-List
title: "Four bugs from the suggested list"
status: draft
owner: user:edwin
created: 2026-08-13
updated: 2026-08-13
source: ["Edwin 2026-08-13: 'Suggest which bugs to fix.' → 'Fix the suggested bugs!'"]
commit: ""
pr: ""
impacts: ["the console's keyboard after a workspace switch", "what the digest reports as needing you", "the severity two validator gates are tested at"]
issues: ["[[ISS-0154-Existing-Terminals-Lose-Keyboard-Input-After-Workspace-Switch]]", "[[ISS-0159-The-Digest-Walks-The-Corpus-Instead-Of-Reading-The-Registry]]", "[[ISS-0120-The-Gates-Own-Severity-Is-Untested]]", "[[ISS-0139-The-Changes-Tile-Is-Orphaned-Code]]", "[[ISS-0147-The-Template-Ships-Three-Workflow-Stubs-Into-Every-Repo]]"]
features: []
related: ["[[PHASE-030-Obligations-Go-Home]]", "[[TASK-0187]]", "[[ISS-0158]]"]
---

# Four bugs from the suggested list

## Summary

Four fixed, one checked and left open with the reason.

- **[[ISS-0154]]** (high) — the console kept its keyboard. Two defects: `openWorkspace` attached the terminal without restoring focus, where `showTerminal` and `restartTerminal` both did; and the attach could replay a stale backlog into the wrong workspace.
- **[[ISS-0159]]** (new, found in [[PHASE-030]]'s close-out) — the digest counted what needs you with its own walk, so it could not see an obligation whose subject is not a note. **13 → 14** against a registry total of 14.
- **[[ISS-0120]]** — a gate demoted from error to warning left every test green. The synthetic cases now assert the tier.
- **[[ISS-0139]]** — 57 lines of dead Changes-tile code removed; the endpoint and its type stay, because they have a live consumer 2,700 lines away.
- **[[ISS-0147]]** — no code change. Its downstream half was already done; the rest is an upstream template proposal and stays open as its tracker.

## Behaviour that changed

- **A workspace switch with the console open now returns the keyboard to it.** Long-running agents stop looking frozen after A→B→A.
- **The since-you-looked count no longer under-reports.** It was short by exactly the note-less obligations — one on this repo today, thirty-eight on a repo with stale standing documents and unpushed work.
- Nothing about what may write, what may push, or what is refused.

## Documentation Coverage (All Types Considered)

- features: not-applicable
- requirements: not-applicable
- tasks: not-applicable
- issues: updated
- tests: not-applicable
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new
- snapshot: updated

## Evidence

Every fix is mutation-checked rather than asserted — each new guard was run against the defect it describes and fails:

| guard | mutation | result |
|---|---|---|
| `test_every_terminal_attach_restores_the_keyboard` | switch calls the bare attach again | fails |
| `test_the_terminal_attach_cannot_replay_a_stale_backlog` | the backlog await loses its guard | fails |
| `test_the_digest_never_under_reports_what_the_badges_show` | note-less rows dropped again | fails |
| `tests/test_parent_backlink.py` (11 cases) | `SNAPSHOT-MEMBERSHIP` demoted to `warn` | 2 fail |
| `tests/test_parent_backlink.py` (11 cases) | `PARENT-BACKLINK` demoted to `warn` | 3 fail |

The last two are [[ISS-0120]]'s own repro, which used to report `11 passed`.

## Follow-ups

- [ ] [[ISS-0147]]'s upstream proposal — stop shipping `WF-0001..0003` into every repo.
- [ ] [[FEAT-0100]] still owes the independent review pass `QUALITY.md` asks for on a feature reaching `done`.
