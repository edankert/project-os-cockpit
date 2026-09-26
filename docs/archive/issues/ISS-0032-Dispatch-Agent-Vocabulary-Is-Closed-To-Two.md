---
type: "[[issue]]"
id: ISS-0032
aliases: ["ISS-0032"]
title: "The dispatch agent vocabulary is a closed two-value union restated across nine sites; a third agent is dropped from the persisted queue and coerced in two preference paths"
status: fixed
severity: medium
owner: user:edwin
created: 2026-07-27
updated: 2026-07-27
component: desktop
source: ["session:2026-07-27 external-review design"]
phase: "[[PHASE-007-Agent-Instrumentation]]"
related: [ISS-0023, FEAT-0024, FEAT-0025]
tests: []
fixed_by: "[[TASK-0213]]"
---

# Adding a third agent breaks the dispatch queue

## Correction (2026-07-27, before any fix)

This note was filed from a `grep -n "=== 'codex' ?"` that returned three hits, which I read as three coercions. **Two of the three are the first line of a two-line narrowing** that correctly falls through to `undefined`, and the consequence I asserted — "the session record says Claude did work Claude did not do" — is false: both record paths preserve whatever agent string they are given.

Corrected below before fixing, because fixing from the original diagnosis would have hardened the wrong thing. Same failure as [[ISS-0011]]..[[ISS-0015]]: a claim written wider than the code, from a grep whose shape I did not check.

## Problem

The agent vocabulary `claude | codex` is declared across nine sites that do not agree on being a set. Sorted by what actually goes wrong:

### Real defect — a third agent is silently dropped from the persisted queue

`desktop/src/ipc/dispatch-queue.ts:70`:

```ts
&& (it.agent === 'claude' || it.agent === 'codex');
```

This is the validator for queue items read back from disk. An item whose agent is anything else fails validation and is **discarded without a message**. FEAT-0025's whole promise is that a queue survives a restart; for a third agent it would not, and nothing would say so.

### Coercions — wrong value, no error

| Site | Effect |
|---|---|
| `renderer.ts:5989` (`agent-set`) | an unrecognised agent from IPC is saved as the user's `claude` preference |
| `main.ts:232` (`currentAgent`) | the radio menu shows Claude checked for any unrecognised agent |
| `renderer.ts:7308` (`loadDispatchAgent`) | a stored preference for a third agent reverts to `claude` on read |

The third is defensible on its own — it reads a preference, and defaulting an unreadable preference is reasonable — but combined with the first two it means a third agent cannot be selected and cannot stay selected.

### Closed type declarations

`renderer.ts:60`, `renderer.ts:7255` (`type DispatchAgent`), `ipc/dispatch-queue.ts:31`, and `cli.py:382` (`choices=["claude","codex"]`). Four independent statements of the same set.

### Hardcoded surfaces

`main.ts:239-244` builds the agent radio menu as two literal entries. `ipc/app-settings.ts:163` writes `"agent": "claude"` as a literal.

### Correct as they stand — recorded so a fix does not "helpfully" break them

- `renderer.ts:5983-5984` and `renderer.ts:7467-7468` narrow properly to `undefined`.
- `agent_hooks.py:313` and `server.py:1106` **preserve** any non-empty agent string, defaulting only when it is missing. The ingestion side is already freeform and already correct.
- `ipc/agent-instrument.ts:183-184` defines a shell wrapper per agent, and `ipc/terminal.ts:121` handles a Claude-specific session-id field. Those are legitimately per-agent; they are an extension point, not drift.

## Inconsistent already

`cli.py:367` documents the `signal` path's agent argument as **"Agent name (e.g. claude, codex, aider). Freeform."** So the ingestion side is already open-ended while the dispatch side is closed to two, and nothing reconciles them. A signal from `aider` is accepted and stored; a dispatch to `aider` is impossible, and a *record* of one would read as `claude`.

## How this surfaced

Designing the external-review runner (project-os-dev FEAT-0018), which needs a non-Claude model to satisfy `QUALITY.md`'s different-family gate. Kimi Code CLI turns out to fit the cockpit unusually well — its hook events (`PreToolUse`, `PostToolUse`, `SessionStart`, `Stop`, `UserPromptSubmit`) carry the same names Claude Code uses and pass JSON on stdin, so FEAT-0019's ingestion is close to drop-in. But adding it as a dispatch target lands on the queue validator on day one — its queued work would vanish on the first restart.

## Expected

One declaration of the agent set, consumed by every surface, with an unknown value handled explicitly — rejected, or preserved and rendered as unknown — never coerced to a sibling.

## Actual

Nine declarations. One drops a third agent's queued work on restart, two coerce it to `claude`, four are independent closed type unions, and two are hardcoded surfaces. No test asserts that any agent value survives a round trip.

## Repro

Queue drop (the real one) — an item with a third agent does not survive a round trip through the persisted queue:

```
node -e "const v=(it)=>typeof it.id==='string'&&typeof it.rel==='string'&&typeof it.prompt==='string'&&it.prompt.length>0&&(it.agent==='claude'||it.agent==='codex');
console.log('kimi item valid:', v({id:'TASK-1',rel:'a.md',prompt:'p',agent:'kimi'}))"
```

prints `kimi item valid: false`, so `dispatch-queue.ts` discards it on load.

Coercion:

```
grep -n "'codex' as const : 'claude' as const\|=== 'codex' ? 'codex' : 'claude'" \
  desktop/src/renderer/renderer.ts desktop/src/main.ts
```

returns exactly two sites — `renderer.ts:5989` and `main.ts:232` — not the three this note originally claimed.

(The obvious form of that grep, without the `as const` alternative, silently misses the renderer site and returns one. Recorded because it is the third time in this note's short life that a grep's shape, not the code, produced the wrong answer.)

## Next Actions

- [x] Declare the agent set once in the sidecar (`agents.py`, mirroring `statuses.py`) and serve it, so the renderer consumes the vocabulary instead of restating it — the [[ISS-0023]] remedy, applied to the same class of problem
- [x] Open the queue validator so a third agent survives a restart
- [x] Replace the two coercions with explicit handling of an unrecognised agent
- [x] Reconcile the `signal` path's freeform agent with the dispatch path's closed set, in whichever direction is chosen
- [x] Add a parity test in the shape of TST-0019: one vocabulary, asserted across every surface that restates it
- [x] Only then add a third agent

## Notes

Filed before adding Kimi rather than after, because the whole point of [[ISS-0023]] was that this class of drift is cheap to prevent and expensive to find. Adding the third value first would have turned a latent queue-validation bug into silent loss of the user's queued work.

The correction at the top is the more useful half of this note. The original diagnosis was plausible, specific, and wrong, and it would have produced a fix that hardened two sites which were already correct while leaving the one real defect in place.

## Resolution

Fixed 2026-07-27 in [[TASK-0213]].

`agents.py` is now the single declaration, served at `GET /api/cockpit/agents` and consumed by the renderer and main process — the [[ISS-0023]] remedy (`statuses.py` + a served payload + a parity suite) applied to the same class of problem.

The real defect is closed: `dispatch-queue.ts` validates shape only, so a third agent's queued work survives a restart. The two coercions reject or preserve instead of relabelling. The radio menu is built from the payload. `cli.py` reads `AGENT_IDS`.

**What was deliberately left alone**: `agent_hooks.py` and `server.py` still preserve any agent string, and `test_ingestion_paths_do_not_gate_on_dispatchability` asserts neither imports `is_dispatchable`. Dispatchable is closed; recordable is open. Tidying the ingestion path into the closed set would have discarded legitimate external-terminal history — and it was the tempting "consistency" fix.

Adequacy verified by inversion: all six fixes reverted one at a time, each caught by the matching test.

`tests/test_agent_vocabulary.py`, 16 tests. Suite 330 passed / 1 skipped, `tsc` clean, bundle rebuilt.
