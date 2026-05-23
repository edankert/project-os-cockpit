# Cockpit driving (LLM directives)

When a `project-os-cockpit` server is running for this project, you can
drive what the user sees in the cockpit UI from any terminal — including
this one — by calling the `cockpit` CLI. Use it to bring your current
work into the user's view at **meaningful context changes** (start of a
task, after creating a note, after closing out). Treat it as an ambient
signal, not a chatty one.

## Discovery

You do not need to know the cockpit's URL. The CLI auto-discovers it in
this order:

1. `COCKPIT_URL` env var — set automatically when the cockpit's embedded
   ttyd spawns its shell.
2. `<ancestor>/.cockpit/url` — written by the cockpit server at startup
   in the project root. The CLI walks up from CWD looking for it.

If neither is found, the CLI errors clearly. Don't ask the user to start
the cockpit — proceed without focus calls. The work matters more than
the UI hint.

## Commands

### `cockpit focus <target>`

Navigate every connected cockpit tab (that has "Following" on) to a
target.

`<target>` can be:
- a note ID (`FEAT-0006`, `TASK-0030`, `CHG-20260522-Foo`)
- a docs-relative path (`features/cockpit/FEAT-0006-Cockpit-Layout.md`)
- a full cockpit URL (`/docs/changes/CHG-...md`)
- a top-level project file (`README.md`, `ROADMAP.md`, `SECURITY.md`)

Output is one line: `cockpit -> <resolved-url>`. Non-zero exit on
failure (unresolved target, no cockpit running, server error).

### `cockpit state` and `cockpit history`

Read where the user is currently looking. `cockpit state` prints a
compact summary; add `--json` for machine-parseable output. `cockpit
history` shows recent navigation events (default 10, `--limit N` to
override), interleaving your own `cockpit focus` calls (`source:
agent`) with the user's manual nav (`source: user`).

These are read-only — no side effects on the cockpit. Use them to
align with the user's context, not to broadcast anything.

Example `state` output:

```
agent focus : TASK-0053  (/docs/.../TASK-0053-Cockpit-State-Endpoint.md)  @ 2026-05-23T10:45:10+00:00
user view   : /docs/features/cockpit/FEAT-0006-Cockpit-Layout.md         @ 2026-05-23T10:46:02+00:00
tabs        : 2 live
  - 7a3f1c9a  follow  /docs/.../FEAT-0006-Cockpit-Layout.md  @ 2026-05-23T10:46:02+00:00
  - 9b8d2e44  manual  /docs/changes/CHG-...md                 @ 2026-05-23T10:45:30+00:00
history     : 14 events (showing 5)
  - agent  /docs/.../TASK-0053-Cockpit-State-Endpoint.md  [TASK-0053]
  - user   /docs/features/cockpit/FEAT-0006-Cockpit-Layout.md
  ...
```

## When to focus

Focus on **context changes**, not file accesses:

- ✅ User asks you to work on `<id>` → `cockpit focus <id>`.
- ✅ You just created a new TASK / CHG / FEAT note → `cockpit focus <new-id>`.
- ✅ You finished a chunk of work and wrote a CHG note → `cockpit focus <CHG-id>`.
- ✅ You're switching to a different feature / phase → `cockpit focus
  <new-target>`.
- ❌ Don't focus for every file you open to read.
- ❌ Don't focus for every line edit.
- ❌ Don't focus multiple times within seconds.

Rough cadence: **2–5 focus calls per task** is the right shape.

## The follow toggle

Each cockpit tab has a "Following" / "Manual" pill in its header. When
OFF, focus events from your CLI are ignored for that tab. The user
controls this — your CLI doesn't.

If the user has set tabs to Manual, your `cockpit focus` calls still
succeed (the server still emits the SSE event), they just don't move
that tab. That's the user's choice; respect it. If you suspect noisy
focus calls drove them to Manual, back off and continue without the UI
hint.

## Multi-tab fan-out

A single `cockpit focus` call drives every tab connected to the same
server (laptop + iPad + …). Useful for pair-programming and demos.

## Reading the user's view

`cockpit focus` is one half of the loop; `cockpit state` is the other.
The agent both drives and reads the cockpit, so you can stay aligned
with the user instead of working in the dark.

**When to read state:**

- ✅ Before significant work — `cockpit state`, then decide:
  - User is on the same item you're about to work on → no orientation
    needed; just proceed.
  - User is on a related item (same feature, parent / child) → mention
    it ("you're on FEAT-0006; I'll work on its TASK-0030").
  - User is on something unrelated → describe what you're about to do in
    text rather than silently jumping their view.
- ✅ After a long-running step — re-check; they may have moved on while
  you were running tests or building.
- ✅ When the user says "what about this?" or "look at that" without a
  noun — `cockpit state` resolves the ambiguity (their current view is
  almost always the referent).
- ❌ Don't poll. Once per meaningful checkpoint is plenty.
- ❌ Don't read state mid-batch (e.g., inside a multi-file edit loop).

**Respect Following=OFF.** If a tab is in Manual mode the user has
explicitly opted out of your focus calls. You can still report state
in text ("I worked on TASK-0030; you've been on FEAT-0006") but don't
push them around.

**Don't over-react to user nav.** Seeing the user move to another note
isn't a request to abandon your work. It's context. Continue unless
the move + a verbal signal together indicate a redirect.

## Multi-project

Each running cockpit writes its own `.cockpit/url` in its project root.
The CLI's walk-up from CWD picks the closest one. So if you `cd` into a
different project's tree, `cockpit focus` drives that project's cockpit
automatically.

## Tone

Don't announce focus calls to the user. They see the cockpit move; you
don't need to say "I've focused on X". The exception is when a focus
call fails — surface that briefly so they know nothing is broken on
their end either.
