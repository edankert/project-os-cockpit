---
type: "[[task]]"
id: TASK-0455
aliases: ["TASK-0455"]
title: "A check carries its verdict and its witness — the mark and the reason are one action, in the grammar the record already uses"
status: backlog
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["[[FEAT-0111-The-Marks-The-Record-Already-Uses]]", "[[ISS-0181-Four-Things-The-Release-Surface-Cannot-Do]] item 2"]
parent: "[[FEAT-0111-The-Marks-The-Record-Already-Uses]]"
effort: M
depends: ["[[TASK-0454-Read-And-Write-The-Marks-Already-In-Use]]"]
blocks: []
related: ["[[ISS-0177-An-Exception-Mark-Drops-A-Check-With-No-Justification]]"]
tests: []
---

# A check carries its verdict and its witness

## Why

`TESTING.md` requires a justification for every exception and there has been nowhere to put one. The same gap stops a **passed** check recording what was actually observed.

The grammar exists, in `../your-trainer`, used consistently:

```
**FAILS 2026-06-07** — collapse state is stored globally in SharedPreferences,
not per-rider. Tracked as [[ISS-0285]] (medium severity) — defer to v2.1.1.

**Partial pass 2026-06-06**: English-looking prompts come back in English even
when the app locale is German (see [[ISS-0277]] — low severity, may not fix).
```

and the witness, 22 times in `ACCEPTANCE_CHECKLIST_v2.1.1.md`:

```
✅ (Claude, tablet: address rotated 7F:D5:FB:49:A4:DF → 73:DD:28:D6:8D:50;
    reconnected by name-match, slot shows Connected)
```

`rewrite_check()` already takes a `note` parameter and appends it. **The write path exists** — only the vocabulary was invented in the wrong place.

## What

| action | writes |
|---|---|
| pass | `- [x] … ✅ (<witness>, <date>: <observed>)` |
| partial | `- [~] … **Partial pass <date>** — <reason> [[ISS-…]]` |
| fail | `- [F] … **FAILS <date>** — <reason> [[ISS-…]]` |

**The mark and the text are one action.** A partial or a fail cannot be written without a reason — that is what makes this different from `[!]`, and it is the whole of [[ISS-0177]]. A pass may carry a witness and does not require one.

## Constraints

- The date is the write date, in the corpus's `YYYY-MM-DD` form.
- An `ISS-*` in a reason is written as a **wikilink** and must resolve; an id that resolves to nothing is refused at write time rather than written dead.
- Appended to the existing text, never replacing it.
- Text is escaped so a reason containing `**`, `[`, `|` or a newline cannot corrupt the row or the table it sits in.
- No `window.prompt` — [[ISS-0176]]; Electron 32 does not implement it. `askForText()` is the existing path.

## Done when

- [ ] each of the three actions writes the documented grammar, verbatim in shape
- [ ] partial and fail **refuse** an empty reason — the mutation that must fail is writing the mark alone
- [ ] a pass without a witness is valid and writes no empty parenthetical
- [ ] an unresolvable `ISS-*` is refused at write time
- [ ] a reason containing markdown metacharacters or a newline round-trips without corrupting the row
- [ ] round-trip: written rows parse back to the mark **and** the text they were given
- [ ] the seven rows already carrying this grammar in `../your-trainer` parse identically before and after
