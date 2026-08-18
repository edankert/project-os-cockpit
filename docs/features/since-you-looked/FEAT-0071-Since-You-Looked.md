---
type: "[[feature]]"
id: FEAT-0071
aliases: ["FEAT-0071"]
title: "Since you looked — a per-workspace watermark, a digest of what happened behind it, and a Caught-up that means it"
status: done
phase: "[[PHASE-026-The-Returning-Human]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-10
source: ["[[DES-0008-The-Returning-Human]]"]
goal: "A server-side watermark moved only by an explicit action; the landing card says since-when and how-many; the overview carries the digest band with needs-you items lifted; all of it derived from history_payload and the registers that already exist."
requirements: []
tasks:
  - "[[TASK-0312-The-Watermark]]"
  - "[[TASK-0313-The-Landing-Line]]"
  - "[[TASK-0314-The-Digest-Band]]"
release: ""
related: ["[[FEAT-0052-History-Timeline]]"]

---

# Since you looked

## Goal

See [[DES-0008]]. No new data is computed — `history_payload` already yields transitions since a point, the registers already know what needs a human. The feature is a watermark file, two placements, and the discipline that presence is not attention: only **Caught up** moves the mark.

## Out of Scope

- Notifications, badges, or anything pushed. Pulled on arrival, always.
- Per-person watermarks — one human per cockpit today.

## Acceptance

Written at close-out, because this feature carried none — the goal line and [[DES-0008]] were the spec, and the tasks each carried their own DoD. Ticked against what shipped.

- [x] A watermark that only an explicit action moves — `.cockpit/last-seen.json`, temp-file-and-replace, corrupt reads to unset; `POST /api/cockpit/caught-up` is the only writer, loopback-guarded ([[TASK-0312]])
- [x] The landing card says since-when and how-many — `since Thu · 14 transitions · 2 need you`, one line per workspace, absent rather than zero ([[TASK-0313]])
- [x] The overview carries the digest band with needs-you lifted, and `Caught up` at its end ([[TASK-0314]])
- [x] No new data is computed — `history_payload` supplies the transitions and [[FEAT-0089]]'s registry the obligations
- [x] Nothing is pushed; everything is pulled on arrival, rate-limited to once every 30 seconds
- [x] Presence is not attention — nothing but the button moves the mark, and it records `computed_at` rather than the moment of the click

## Closed 2026-08-10

**Three findings, and the first is the one worth keeping.**

1. **"One line per workspace" looked impossible and was not.** The digest is served per-sidecar, so only the active workspace seemed reachable — until it turned out the shell announces a URL for *every* workspace and the renderer's `ready` handler discarded all but the active one, in its first line, as a side effect of a guard written for something else. Two lines to keep them.
2. **The cards knew only about terminals.** `needs-input` and `waiting` are both properties of a terminal, so a repo with eleven things needing a human and a quiet terminal looked exactly like a repo with nothing to do. That was [[DES-0008]]'s complaint verbatim, and it took a third kind rather than a wider predicate.
3. **The `DIGEST_NEEDS_YOU` list had already drifted.** Six types, written before [[FEAT-0089]]; it omitted `change` (81 owed here) and `feature`, and could not express the `test` predicate's manual-only clause. A digest built from it would have told the returning human that 8 things needed them while the badges said 96. It reads the registry now, and a test pins the two together.

The band summarises rather than duplicating History: eight rows a half, then a count. An epoch watermark on this repo yields 440 transitions and 93 owed items, which is a page nobody reads.
