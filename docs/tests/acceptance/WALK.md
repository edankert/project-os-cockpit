---
type: "[[reference]]"
title: "Walk order — the sittings this cockpit's releases are walked in"
status: active
owner: user:edwin
created: 2026-09-13
updated: 2026-09-13
gallery: ""
---

# Walk order

The order a release of this cockpit is walked in. It is the only place that order is written down, and both the walk page (`~walk/macos`) and `tools/scripts/walk-sheet.py` read it. What the sheet and the page do with it is stated once in `tools/instructions/TESTING.md`, "The walk".

**Why this order and not the areas in alphabetical order.** The cockpit is one Electron shell hosting one Python sidecar per repo, and almost everything on a surface depends on a workspace being open and its index being built. So the sittings climb: the server on its own first, because a browser tab needs nothing else; then the shell that discovers repos and spawns sidecars; then the panes inside one workspace, which is where most of the suite lives; then the surfaces that read several repos at once, which need more than one workspace open; then the things that write — marks, close-out, the terminal — which change the corpus underneath everything above and so go last.

**No durations anywhere**, including in `state:` — the page counts rows and prints no minutes ("The walk", rule 8).

**No commas inside a `bench:` entry.** The walk order is read as inline lists and the reader splits on every comma, quoted or not, so `["a phone, charged"]` becomes two bench items. Filed upstream as [[ISS-0304-The-Walk-Order-Reader-Splits-Inside-A-Quoted-String]]; until it is fixed, write the entry without one.

### The server, in a browser

```yaml
surfaces: ["Render server and the browser front door", "The note page", "notes and attachments", "the viewer"]
state: "A sidecar started from a terminal on this repo's docs, opened in a browser rather than in the shell. Nothing about the desktop app is needed for these."
bench: ["A second device on the same Wi-Fi (the tablet row needs it)"]
```

### The shell finds the repos

```yaml
surfaces: ["Desktop shell and workspaces", "The navigator"]
state: "The desktop app started fresh, with ~/Dev/repos/ as it stands. Restart it rather than reusing a window that has been open for days: half of what this sitting checks happens at startup."
bench: []
```

### One workspace, its panes

```yaml
surfaces: ["The overview", "Issues and capture", "Plans are visible", "Stat tiles are not dead ends", "One home per obligation", "Obligations", "The record column has its own source", "History", "Design and the constraints view", "One status vocabulary"]
state: "One workspace open on this repo, with its index built and no filter set. Most of the suite is here."
bench: []
```

### Across the fleet

```yaml
surfaces: ["Verification health and the fleet", "Publication", "A settled verdict is not owed", "Tests"]
state: "At least three workspaces open, including one with an open release and one that is behind upstream. The rows here are about repos seen together, so one workspace cannot answer them."
bench: []
```

### Writing, last

```yaml
surfaces: ["Agents and sessions", "The embedded terminal", "Close-out", "Writes are loopback-only", "the walk"]
state: "Everything above walked. These rows record verdicts, run close-out and drive a terminal, so they change the corpus the earlier sittings read — walking them first makes every count above a moving target."
bench: []
```
