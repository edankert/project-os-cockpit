---
type: "[[change]]"
id: CHG-20260813-Four-Bugs-From-The-Suggested-List
title: "Four bugs from the suggested list"
status: merged
owner: user:edwin
created: 2026-08-13
updated: 2026-08-13
source: ["Edwin 2026-08-13: 'Suggest which bugs to fix.' → 'Fix the suggested bugs!'"]
commit: ""
pr: ""
impacts: ["the console's keyboard after a workspace switch", "what the digest reports as needing you", "the severity two validator gates are tested at"]
issues: ["[[ISS-0154-Existing-Terminals-Lose-Keyboard-Input-After-Workspace-Switch]]", "[[ISS-0159-The-Digest-Walks-The-Corpus-Instead-Of-Reading-The-Registry]]", "[[ISS-0120-The-Gates-Own-Severity-Is-Untested]]", "[[ISS-0139-The-Changes-Tile-Is-Orphaned-Code]]", "[[ISS-0147-The-Template-Ships-Three-Workflow-Stubs-Into-Every-Repo]]"]
features: []
reviewed_by: model:claude-opus-5
review_date: 2026-08-14
review_verdict: changes-requested
related: ["[[PHASE-030-Obligations-Go-Home]]", "[[TASK-0187]]", "[[ISS-0158]]"]
---

# Four bugs from the suggested list

## Summary

Four fixed, one checked and left open with the reason.

- **[[ISS-0154]]** (high) — the console kept its keyboard. Two defects: `openWorkspace` attached the terminal without restoring focus, where `showTerminal` and `restartTerminal` both did; and the attach could replay a stale backlog into the wrong workspace.
- **[[ISS-0159]]** (new, found in [[PHASE-030]]'s close-out) — the digest counted what needs you with its own walk, so it could not see an obligation whose subject is not a note. **13 → 14** against a registry total of 14.
- **[[ISS-0120]]** — a gate demoted from error to warning left every test green. The synthetic cases now assert the tier.
- **[[ISS-0139]]** — 50 lines of dead Changes-tile code removed; the endpoint and its type stay, because they have a live consumer 2,700 lines away. *(Corrected 2026-08-14: the figure was 57, which counted an unrelated deletion in the same commit. And the removal was **incomplete** — `buildChangeRow` and `buildChangeBucket` survived, each called only by the other. See [[CHG-20260814-The-Review-Findings]].)*
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

## Independent review — 2026-08-14, `changes-requested`

Fresh context, separate session, never saw the authoring reasoning; same model family as the author (`model:claude-opus-5`, recorded in `reviewed_by` per [[project-os-dev#ADR-0013]]). Every mutation in the Evidence table was re-applied to the working tree and the named test re-run.

**Three of the five Evidence rows reproduce exactly.** `SNAPSHOT-MEMBERSHIP → warn` fails 2 of 11 cases; `PARENT-BACKLINK → warn` fails 3 of 11; and running the *pre-fix* `tests/test_parent_backlink.py` (from `a83f5e8^`) under either mutation reports `11 passed`, which is [[ISS-0120]]'s repro reproduced verbatim. Reverting `digest_payload` to the pre-fix note walk fails both digest guards, on the live corpus as well as the fixture: today the pre-fix walk reads **6 against the badges' 12**, short by exactly the six note-less rows (unpushed commits).

**Finding 1 — `test_the_terminal_attach_cannot_replay_a_stale_backlog` no longer guards, and its Evidence row is not reproducible today.** Deleting the generation check after `cockpitApi.terminal.attach(workspaceId)` — the mutation this table names — leaves the suite **green**. The assertion is `fn.count("generation !== terminalAttachGeneration") >= 2` (`tests/test_view_landings.py:595`) and `attachTerminalTo` has carried **three** occurrences since [[ISS-0161]] added the `suppressTerminalWrites` block, so the count has a spare. Confirmed the claim was true when written: the same mutation applied at `a83f5e8` fails with `assert 1 >= 2`. A counting assertion decays the moment the thing it counts grows. Anchor the guard to its await instead — assert that the text between `terminal.attach(` and `term.write(res.backlog` contains the check.

**Finding 2 — `test_every_terminal_attach_restores_the_keyboard` counts a comment as a call site.** `assert len(bare) == 2` matches two occurrences of `attachTerminalTo(`: the real call inside `attachAndFocusTerminal`, and the prose at `renderer.ts:921` (*"This line used to be `void attachTerminalTo(id)`"*). Deleting that comment and reintroducing the exact [[ISS-0154]] defect in the same edit — `openWorkspace` calling the bare attach — leaves the suite **green**. Verified by mutation. A guard whose count is satisfied by documentation is one tidy-up away from silence.

**Finding 3 — [[ISS-0139]] removed the caller and left the callees.** `fillChanges` is gone, but `buildChangeRow` (`renderer.ts:8363`) and `buildChangeBucket` (`renderer.ts:8385`) survive with no external caller: `buildChangeBucket` is called only by itself and `buildChangeRow` only by `buildChangeBucket`, so the pair is a mutually-recursive dead island that `noUnusedLocals` cannot see. Forty-five more lines of exactly what this issue is about — *"dead code that still answers correctly is the expensive kind"* — left behind by the fix for it.

**Finding 4 — "57 lines" is not reproducible.** The commit deletes **50** lines in that region (41 for `fillChanges` and its trailing blank, 9 for the comment block); 58 is the whole file's deletion count including the [[ISS-0154]] edits. 57 appears to be [[ISS-0139]]'s own *"~50 lines"* estimate plus the comment, carried forward as a measurement.

**Not defects, recorded so the next reader does not re-derive them.** `13 → 14` is dated and the corpus has moved (12/12 today); the mechanism reproduces at magnitude 6, and one unpushed commit at the time of measurement is consistent with a shortfall of 1. *"thirty-eight on a repo with stale standing documents and unpushed work"* names no repo and cannot be re-measured from this note. [[ISS-0147]] is now `fixed` (2026-08-14, `90a74cb`) while this note's follow-up box for it is still open. [[FEAT-0100]] still carries no `reviewed_by`, so that follow-up is correctly outstanding. `status: draft` is outside `ALLOWED_STATUS["change"]` (`{merged, reverted}`) and nothing catches it, because `STATUS-VALUE` reads the snapshot and change notes are not snapshot items.

Reviewed the fix itself for correctness beyond the guards: `activeId = id` precedes the attach in `openWorkspace`, so the focus re-check is sound; `spawnPty` hands back an existing PTY, so the generation guard sitting above `liveTerminals.add` cannot orphan a shell — it only costs a backlog replay on the next attach, in a race that has already been lost once.
