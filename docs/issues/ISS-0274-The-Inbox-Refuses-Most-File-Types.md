---
type: "[[issue]]"
id: ISS-0274
aliases: ["ISS-0274"]
title: "The inbox refuses every file type outside a seventeen-suffix list, and that list is not what makes the drop safe"
status: fixed
owner: user:edwin
created: 2026-09-02
updated: "2026-09-02"
severity: medium
component: cockpit
phase:
source: ["Edwin, 2026-09-02: \"I want to be able to drag any file type there, not sure why we have that limitation?\""]
related: ["[[FEAT-0045-Project-Inbox]]", "[[TASK-0233-Drop-And-Paste-Into-The-Inbox]]", "[[CHG-20260902-The-Inbox-Takes-Any-File-Type]]"]
tests: []
---

# The inbox refuses most file types

## Problem

Dragging a `.zip`, a `.docx`, a `.mov`, a `.html` export or a file with no extension at all onto the cockpit gets *"is not a storable name"*. `inbox.ALLOWED_SUFFIXES` lists seventeen suffixes and `safe_name` returns `None` for everything else, so the drop never reaches disk.

That is a real block. The inbox exists to take whatever has just arrived and let an agent decide about it, and "whatever has just arrived" is regularly a zip from a colleague or an export from a web app.

## The list is not the guard

Three things are true of the current code, and together they say the suffix list is protecting almost nothing.

**It is not what stops a hostile filename.** `../../.ssh/authorized_keys` is refused by the `_SAFE` substitution, which turns every separator into `-`, and again by the `relative_to` containment re-check at the write. Both still refuse it with the suffix list gone. `TASK-0233` already recorded this about two *other* guards in the same file — that a check which cannot fire, under a comment implying it protects something, is the defect this codebase has found four times.

**It is not what stops execution.** `write_bytes` does not set the execute bit, and nothing in the cockpit runs a file out of `inbox/`.

**It admits the one genuinely dangerous type and refuses the inert ones.** `.svg` is on the list. An SVG can carry `<script>`, and `/_inbox/<name>` serves it back with `image/svg+xml` at the cockpit's own origin, so navigating to one runs script beside the cockpit's session. `.zip` is not on the list, and a zip is a bag of bytes the server never opens.

**The client half was already written for arbitrary types.** `INBOX_READABLE` in `renderer.ts:4956` lists `.html`, `.css`, `.js`, `.ts`, `.py`, `.sh` and `.tsv` — seven types the server refuses to store. The unknown-suffix path falls back to a generic file icon and a *"No in-app preview for this type — open it in Finder"* stage, which is exactly right and currently unreachable for anything new.

## The size cap, and its stale reason

`MAX_ITEM_BYTES` is 25 MB, and its comment justifies the number as *"an unbounded write endpoint on a server that binds 0.0.0.0 is a way to fill a disk from the LAN"*. `_serve_inbox_store` calls `_require_loopback()` first, so the LAN cannot reach it at all. The reason on the constant describes a threat the endpoint had already closed.

The cap should still exist, for a different and honest reason: the whole file is base64'd into one JSON request by the renderer, so the ceiling is about what the browser and the server will hold in memory at once, not about disk.

## Expected

Drop any file. The name is sanitised, the bytes are stored, and what the item *is* stops being a question the write path answers.

## Fix

1. Drop the write-side suffix allow-list. Sanitise the suffix the same way the stem is already sanitised — `_SAFE`, lowercased, length-capped — and accept an empty suffix so `Makefile` and `README` can be dropped.
2. Move the safety property to the read, where it belongs. `/_inbox/<name>` serves an inline content type only for images, PDF and text; everything else becomes `application/octet-stream` with `Content-Disposition: attachment`. Every response carries `Content-Security-Policy: default-src 'none'; sandbox`, which closes the SVG hole the allow-list left open while leaving `<img>` thumbnails working.
3. Raise `MAX_ITEM_BYTES` to 250 MB (Edwin, 2026-09-02) and rewrite the comment to name the real limit.

## Next Actions

- [x] Widen `safe_name`, add suffix sanitising
- [x] Harden `_serve_inbox_item`
- [x] Raise the cap
- [x] Tests
