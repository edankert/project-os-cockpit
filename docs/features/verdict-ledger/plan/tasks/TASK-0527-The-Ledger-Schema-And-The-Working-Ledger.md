---
type: "[[task]]"
id: TASK-0527
aliases: ["TASK-0527"]
title: "Define the ledger file — schema, the working ledger per platform, and sealing at release cut"
status: backlog
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
parent: "[[FEAT-0133-The-Ledger-Is-The-Only-Place-A-Verdict-Lives]]"
phase: "[[PHASE-038-A-Verdict-Is-An-Event]]"
tags: [task]
---

# The ledger file

`docs/releases/ledgers/REL-####-<platform>.yaml`, open one at `WORKING-<platform>.yaml`.

## Definition of Done

- [ ] File schema documented: `release`, `version`, `platform`, `sealed`, `entries[]`.
- [ ] Entry schema documented: `check`, `mark`, `date`, `by`, `method`, `reason`; or `check`, `invalidated_by`, `date`.
- [ ] Exactly one open ledger per platform, created on demand.
- [ ] Sealing is a single operation: stamp `release`/`version`/`sealed`, rename, start a fresh working ledger.
- [ ] `docs/releases/ledgers/README.md` explains the working-to-sealed lifecycle for a human opening the directory.

## Notes

**Plain YAML, not a note, and the distinction matters.** [[ADR-0030]] rejected [[FEAT-0112]]'s JSON for inverting the notes-are-the-source rule — but that file was a *projection* of state the notes already held, which is what made the tool mandatory. This holds state that exists nowhere else. The line is derived-versus-authored, not YAML-versus-frontmatter.

**It lives with its subject** ([[ADR-0020]]). A ledger is about a release.

**Sealing is what assigns an event to a release**, which answers [[ISS-0206]]'s third question without adding a field to anything.
