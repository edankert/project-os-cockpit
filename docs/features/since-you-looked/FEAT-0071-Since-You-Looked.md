---
type: "[[feature]]"
id: FEAT-0071
aliases: ["FEAT-0071"]
title: "Since you looked — a per-workspace watermark, a digest of what happened behind it, and a Caught-up that means it"
status: planned
phase: "[[PHASE-026-The-Returning-Human]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["[[DES-0008-The-Returning-Human]]"]
goal: "A server-side watermark moved only by an explicit action; the landing card says since-when and how-many; the overview carries the digest band with needs-you items lifted; all of it derived from history_payload and the registers that already exist."
requirements: []
tasks:
  - "[[TASK-0312-The-Watermark]]"
  - "[[TASK-0313-The-Landing-Line]]"
  - "[[TASK-0314-The-Digest-Band]]"
release: ""
related: ["[[FEAT-0052-History-Timeline]]"]
tests: []
---

# Since you looked

## Goal

See [[DES-0008]]. No new data is computed — `history_payload` already yields transitions since a point, the registers already know what needs a human. The feature is a watermark file, two placements, and the discipline that presence is not attention: only **Caught up** moves the mark.

## Out of Scope

- Notifications, badges, or anything pushed. Pulled on arrival, always.
- Per-person watermarks — one human per cockpit today.
