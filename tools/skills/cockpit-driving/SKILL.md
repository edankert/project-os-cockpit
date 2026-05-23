# Skill: Cockpit driving

**When this applies:** any task / change / feature / issue / requirement
work where a `project-os-cockpit` server might be running for the
project. Whether the user said "work on FEAT-0006" or you picked up an
item from SNAPSHOT.yaml's `next` queue.

**Trigger phrases:** "work on X", "pick up X", "fix X", "close out X",
"look at X", "start X".

See also: [`tools/instructions/COCKPIT.md`](../../instructions/COCKPIT.md)
for the always-on rules of the road.

## Pattern

A typical task threads three focus calls — one on **start**, optional
ones on **material progress**, one on **close-out**.

### Start

After preflight (SNAPSHOT.yaml updated, item note created/updated):

```bash
cockpit focus <id>   # e.g. cockpit focus TASK-0030
```

Brings the item the user can now watch you work on into the centre
pane.

### Material progress

If you create a new artefact mid-task (a child task, a sample HTML
preview, a draft ADR, etc.) and want the user to see it:

```bash
cockpit focus <new-id>
```

Don't fire on every edit — only when the new artefact is a meaningful
addition the user would want to look at.

### Close-out

After writing the CHG note and updating statuses:

```bash
cockpit focus <CHG-id>   # e.g. cockpit focus CHG-20260523-Foo
```

Surfaces the change record so the user can review what you delivered.

## When the cockpit isn't running

The CLI errors with a clear message. Don't ask the user to start the
cockpit — proceed with the work. The focus calls are an ambient
ergonomics signal, not a hard dependency.

## Don't

- Don't announce focus calls in your response text ("I focused on
  TASK-0030"). The user sees the cockpit move; saying it duplicates.
- Don't focus on files you're only reading for context. Focus is for
  what the user should be looking at, not what you're looking at.
- Don't loop focus calls inside a multi-file edit batch. Wait for the
  batch to settle, then one focus.

## Implementation notes

`cockpit focus <target>` accepts:
- bare note IDs (resolved via the index)
- docs-relative paths (`features/cockpit/FEAT-0006-Cockpit-Layout.md`)
- full URLs (`/docs/...`)
- top-level project files (`README.md`)

Exit code 0 on success, non-zero on failure (unresolved, no cockpit
found, server error). The output is a single line: `cockpit -> <url>`.
