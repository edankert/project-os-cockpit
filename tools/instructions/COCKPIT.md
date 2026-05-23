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
