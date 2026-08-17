---
type: "[[issue]]"
id: ISS-0187
aliases: ["ISS-0187"]
title: "Marking a check scrolls you back to the top, a server refusal is swallowed silently, and the dialog commits on the option click so there is no Save"
status: "fixed"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
owner: user:edwin
created: 2026-08-17
updated: "2026-08-17"
source: ["Edwin 2026-08-17, from use: 'the file seems to be reloaded after the change from the dialog which means that it scrolls away from the change' / 'I tried using [-] with a comment and don't see this information in the file' / 'The dialog when I select [-] and do not provide a comment requires you to add a comment (which is correct) but it keeps the original [-] selected making me look for a done button instead of clicking the [-] button again'"]
severity: high
component: desktop-renderer
parent: ""
related: ["[[ISS-0185-The-Mark-Control-Sits-Inside-Tasklists-Leftover-Box-And-The-Cycle-Makes-You-Walk-Past-States]]", "[[ISS-0186-The-Mark-Glyphs-Are-Decorative-And-The-Dialog-Is-Too-Narrow-For-Six-Options]]", "[[ADR-0029-The-Acceptance-Mark-Vocabulary-Is-Minimals]]"]
tests: []
---

# Three reports, and the middle one is a symptom of the third

## 1. The repaint loses your place

`cycleAcceptanceMark` calls `repaintDoc()`, which is `navigateTo(currentRel, {replace: true})`. That replaces `innerHTML`, and `applyScrollTarget` restores a saved scroll position **only when the navigation came from history** — so a repaint lands the reader at the top of a 579-row document, away from the row they just marked. Which is the one row they wanted to watch change.

The mechanism to fix it already exists twice over: `scrollPositions` holds a position per path, and the History page already brackets its own repaint with `const scroll = docView.scrollTop` / `docView.scrollTop = scroll`.

## 2. "I don't see this information in the file"

**The write path is not at fault**, and this was checked twice rather than argued: `POST /api/notes/mark-check` with `verdict: excused` against a throwaway suite produces

```
- [-] **Walk me:** open it and look. **Blocked 2026-08-17** — no trainer available this week
```

on disk, and the rendered document carries the reason immediately afterwards. Edwin independently confirmed the same from the other end — the suite's mtime showed **no write at all had happened**.

**So nothing was written, and issue 3 is why.** He typed the comment, hit the reason refusal, and went looking for a way to commit. The second click on `[-]` — the only thing that would have committed it — never happened, because nothing indicated it was needed.

**A real defect did hide underneath it, though**, and would have made a genuine failure equally invisible:

```ts
const res = await postJson(…);
if (!res?.ok) { showStatus(…); }
```

`postJson` **throws** on refusal; it does not return `{ok: false}`. So that branch is unreachable, and a real refusal — a reason citing an `ISS-` that does not resolve, an `mtime` conflict, a suite that moved — became an unhandled rejection with no toast and no explanation. Two failures that look identical from the outside, and only one of them was happening.

## 3. The dialog commits on the option click

Options wrote immediately when clicked. A `[-]` with no reason showed an error and returned, so the **same button had to be clicked again** to commit — while still wearing the `is-current` outline it had for a different reason (it was already the row's mark). Nothing distinguished *"this is the state you are in"* from *"this is the state you have chosen"*, and nothing said a second click would commit.

Looking for a Done button is the correct instinct. There should be one.

## Expected

1. The repaint holds the scroll position.
2. A refusal is caught and shown, with the server's own message.
3. **Select, then Save.** Clicking an option selects it; `Save` commits and is inert until a mark is chosen and any required reason is given. `is-current` (the file's state) and `is-picked` (this dialog's) look different.

## Fixed 2026-08-17

**1. The repaint holds the scroll.** `const held = docView.scrollTop` before, restore after — the same bracket the History page already used. A guard pins the ordering too, because restoring *before* the re-render is the plausible wrong version and it looks identical in a diff.

**2. A refusal is caught and shown**, with the server's own message and six seconds to read it. Verified against a live sidecar: a reason citing `ISS-9999` returns *"ISS-9999 is not in the record — a reason must not cite a note that does not exist"* and HTTP 400, which the toast now carries. That path was reachable and silent.

**3. Select, then Save.** Clicking an option selects it; `Save` commits and is inert until a mark is chosen and any required reason is given. `is-current` is a dashed outline (the mark the file holds); `is-picked` is a solid accent outline with a tint (what Save will write). Cmd/Ctrl+Enter saves; Escape cancels.

All six verdicts walked end to end against a throwaway suite, in sequence on one row, with the neighbouring row untouched throughout:

```
pass      - [x] … ✅ (saw it work)
partial   - [/] … **Partial pass 2026-08-17** — only en-GB, see [[ISS-0277]]
excused   - [-] … **Blocked 2026-08-17** — no trainer this week
failed    - [!] … **FAILS 2026-08-17** — crashes on open
question  - [?] … **Open 2026-08-17** — what is a slot?
clear     - [ ] …
```

Six mutations, all killed. **Two of them survived first time and both were my guards rather than the code** — one compared two CSS rules *including their selectors*, so they always differed and a mutation making the declarations identical passed; the other grepped for a string that this issue's own prose also contains. A guard that can pass for a reason unrelated to the thing it names is not a guard.

## What this round says about the previous two

Three rounds of feedback on one control, and the middle report of this round — *"I don't see this information in the file"* — was a **consequence of the third**, not a bug of its own. It was worth reproducing anyway: the write path was proved correct twice, and the exercise turned up the silent-refusal defect, which nobody had reported because it had not yet fired.

The pattern across all three rounds is that the affordance was designed from the write path outward — what the file needs — and each report came from the other end, where a person is looking for a way to say what they mean.
