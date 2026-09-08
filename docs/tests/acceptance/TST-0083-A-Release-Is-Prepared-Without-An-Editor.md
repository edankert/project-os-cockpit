---
type: "[[test]]"
id: TST-0083
aliases: ["TST-0083"]
title: "A release is prepared without an editor"
status: active
owner: user:edwin
created: 2026-09-08
updated: 2026-09-08
tier: 1
area: "Publication"
covers: ["[[FEAT-0145-Preparing-A-Release-Is-One-Workflow]]"]
related: ["[[ADR-0041-A-Release-May-Settle-A-Check-It-May-Never-Pass-One]]", "[[TST-0082-A-Release-Is-Prepared-Through-One-Workflow]]"]
level: acceptance
---

# A release is prepared without an editor

Open `~release/next` in a repo that keeps at least one ledger, and prepare a release from end to end without opening a text editor once. That sentence is the whole check: [[FEAT-0145]] exists because on 2026-09-08 the same walk needed an editor at every step.

Expect, in order:

1. **Naming a version offers a platform beside it.** The picker lists the platforms this repo has evidence for — the ones with a ledger, the ones its notes tag — and *every platform* first. It never offers a value with a space or a capital in it.
2. **The release note the tool writes carries `platform:`**, and its working ledger exists on disk immediately.
3. **Changing the platform moves the gate count on screen, without a reload.** On a two-ledger repo the number falls from the union to that platform's ledger. No check note changes.
4. **Settle what this release owes** lists the blocking checks grouped by area, each showing its own procedure text, with **N/A**, **Excuse** and **Blocked** — and nothing that says pass, partial, fail or question. Picking one opens the check's whole rendered procedure and refuses to save until a reason is written.
5. **Excusing a check drops it out of the owed list; marking one blocked does not** — the blocked row stays, with its reason showing beside it.
6. **Selecting several rows and settling them together** writes one reason onto all of them and reports how many were written.
7. **Coverage** names the features this release carries that no check covers. **Commission checks** dispatches an agent; nothing is written into the gate by pressing it.
8. **Abandon** takes a reason inline — no dialog — leaves the note on disk at `status: abandoned` with its reason in the body, and drops the release out of the open-release count. Creating a release with the same version number afterwards is refused, and the refusal names the abandoned note.

**What must not be there:** any control on this page that marks a check `pass`, `partial`, `fail` or `question`. That is [[ADR-0035]] as narrowed by [[ADR-0041]], and it is the one thing on this list a reader should check by looking for its absence.

Automated coverage of the write paths is [[TST-0082]]; this check is the walk the source-text guards cannot perform.
