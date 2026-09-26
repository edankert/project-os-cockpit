---
type: "[[task]]"
id: TASK-0297
aliases: ["TASK-0297"]
title: "Capture lands in the repo and serves back"
status: done
phase: "[[PHASE-024-Acceptance-Witnessed]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[FEAT-0066-Visual-Evidence]]"]
parent: "[[FEAT-0066-Visual-Evidence]]"
effort: M
depends: []
blocks: []
related: []
tests: []
---

# Capture lands in the repo and serves back

## Definition of Done

- Shell IPC captures the chosen surface to `docs/attachments/<note-id>/<date>-<n>.png`; sidecar serves attachments; markdown image links render in the note view.
- Captures are committed files — evidence is record; the attachments dir joins the docs contract, not gitignore.

## Done — 2026-08-11

`POST /api/notes/attach` → `docs/attachments/<NOTE-ID>/<date>-<n>.png`, returning the Markdown that cites it.

**No new read path was needed.** `/docs/<path>` already serves anything under `docs/`, and `ImageSourceTreeprocessor` already rewrites Markdown image sources to `/docs/…` URLs — so a capture renders in the note view the moment it lands. That is why evidence belongs *here* rather than beside the design artifacts, which needed their own route.

**Under `docs/`, and committed, on purpose.** `inbox/` is gitignored staging for material nobody has decided about; a screenshot proving a criterion is the opposite of that. Evidence that lives only on one machine is the chat-transcript problem [[REQ-0028]] exists to prevent, one layer down: a witness with no artifact.

Five refusals, each with a test: an unknown note id (evidence for an id nobody allocated creates a directory the record cannot explain — and it must not leave the directory behind), a non-PNG (the renderer emits an `<img>` for whatever is stored, so serving arbitrary bytes out of the docs tree is a different feature with a different threat model), malformed base64, anything over 8 MB (**git history cannot forget a large blob** by deleting the file later), and an id containing `../`.

A `data:` prefix is accepted because the capture bridge returns one, and making each call site strip it is the kind of detail that gets got wrong once per call site.

**One thing this broke and fixed:** `validate_docs_bundled.py` is a *verbatim* copy of `tools/scripts/validate-docs.py`, and adding `ACCEPT-STALE` to the canonical one drifted them. `test_bundled_validator_matches_the_canonical_one` caught it — the guard that exists because the bundle once fell behind ADR-0007 and would have accepted a retired status. Re-copied.
