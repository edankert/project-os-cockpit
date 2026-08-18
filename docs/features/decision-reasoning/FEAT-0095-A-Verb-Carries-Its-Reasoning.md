---
type: "[[feature]]"
id: FEAT-0095
aliases: ["FEAT-0095"]
title: "A human verb carries its reasoning — an optional note on any transition, appended to the decided note as a dated callout the cockpit renders"
status: done
phase: "[[PHASE-032-The-Reasoning-Is-Recorded]]"
owner: user:edwin
created: 2026-08-12
updated: 2026-08-12
source: ["Edwin 2026-08-12 on ADR-0010: 'it asks questions but I cannot answer these or provide additional comments in the tool'", "Edwin 2026-08-12: 'dated and added to the end in its own notes section maybe we can use the callout notation from obsidian for this?'"]
goal: "Any human-owned transition may carry a note; it is appended to the note being decided as a dated, attributed Obsidian callout, and the cockpit renders callouts."
requirements: []
tasks:
  - "[[TASK-0396-The-Note-On-A-Transition]]"
  - "[[TASK-0397-Callouts-Render]]"
  - "[[TASK-0398-The-Field-On-The-Actuator-Row]]"
related: ["[[ISS-0152]]", "[[DES-0005-The-Actuator-Grammar]]", "[[FEAT-0060-Transitions-And-Ticks-On-The-Note]]"]

---

# A verb carries its reasoning

## Goal

`TRANSITION_REQUEST_KEYS` is `{id, to, actor, mtime, severity}`. It gains `note`, and what the person wrote is appended to the note they decided.

**Where, precisely** — Edwin's question, and his answer: *"included in the note being reviewed/decided/agreed, dated and added to the end in its own notes section, maybe we can use the callout notation from Obsidian."* Yes, and the callout is the right call for a reason worth stating: it is **one syntax with two readers**. Obsidian renders `> [!note]` natively, and the cockpit will — so the record does not acquire a form that only the tool understands, which is the failure mode every convention here is written to avoid.

## Out of scope

- **A `Comment` verb** that records prose without deciding ([[ISS-0152]] option 2). It creates a commented-but-undecided state nothing reads.
- **Editing an existing note block.** These append. A decision record that can be rewritten is not one.
- **`Request changes` on the ADR vocabulary.** Same shape, deliberately deferred to keep this pass to one mechanism.

## Acceptance

- [x] `notes/transition` accepts an optional `note`; omitting it leaves the note byte-identical to today's behaviour.
- [x] The note is appended under one `## Decision record` heading as an Obsidian callout carrying **verb, date and actor** — `> [!note] Accepted — 2026-08-12 (user:edwin)`.
- [x] It **appends**; a second decision adds a second callout and never edits the first.
- [x] The cockpit renders callouts — type, title and body — for `note`, `question`, `warning`, `info` and `tip` at minimum, and degrades to a plain blockquote for a type it does not know rather than printing `[!whatever]`.
- [x] The actuator row offers a field before it acts, in the shape the criterion tick already uses, and the verb still works with the field empty.
- [x] Prose is escaped, never interpreted as frontmatter, and a note containing `---` or a `> [!` cannot corrupt the file it is appended to.


## Evidence — 2026-08-12

Driven against a clone of this corpus: accepting `ADR-0022` with a note appended

```markdown
## Decision record

> [!note] Accept — 2026-08-12 (user:edwin)
> Option 3, but consequence 3 is not settled.
```

and accepting **without** one left the body byte-identical to before. A second decision adds a second callout under the same heading and never edits the first. Hostile prose — `---`, a heading, a nested callout — comes back quoted line by line and inert.

Callouts render in **both front doors**: the shell and mode 1 carry the same rules, because a decision record legible in the shell and not on the tablet is the divergence [[ADR-0010]] is about. An unknown type keeps its title and takes the default palette rather than printing `[!whatever]` at the reader.
