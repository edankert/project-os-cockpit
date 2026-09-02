---
type: "[[change]]"
id: CHG-20260902-The-Inbox-Takes-Any-File-Type
aliases: ["CHG-20260902-The-Inbox-Takes-Any-File-Type"]
title: "The inbox takes any file type, the per-item cap goes to 250 MB, and the judgement about what a file is moves from the write to the read"
status: merged
owner: user:edwin
created: 2026-09-02
updated: "2026-09-02"
source: ["Edwin, 2026-09-02"]
commit: ""
pr: ""
impacts: ["src/project_os_cockpit/inbox.py", "src/project_os_cockpit/server.py", "tests/test_inbox.py"]
issues: ["[[ISS-0274]]"]
features: ["[[FEAT-0045-Project-Inbox]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[TASK-0233-Drop-And-Paste-Into-The-Inbox]]"]
---

# The inbox takes any file type

## Summary

Dragging a `.zip`, a `.docx`, a `.mov` or a file with no extension onto the cockpit used to fail with *"is not a storable name"*. It works now. The per-item cap goes from 25 MB to 250 MB, so a screen recording fits too.

The seventeen-suffix allow-list on the write path is gone. It read like a security control and was not one, so removing it makes the drop **safer**, not laxer — the property it was gesturing at now exists for the first time, and applies to every type rather than the sixteen it happened to name.

## What changed

**`inbox.safe_name` accepts any type.** The suffix now goes through the same `_SAFE` substitution the stem already used — lowercased, non-`[A-Za-z0-9._-]` replaced with `-`, capped at 16 characters — instead of being matched against a fixed set. An empty suffix is legal, so `Makefile` and `README` are droppable. A name with no file in it (empty, `.`, `..`) is still refused.

**`_serve_inbox_item` decides what a type means.** A suffix outside `INLINE_SUFFIXES` comes back as `application/octet-stream` with `Content-Disposition: attachment`, so the browser saves it instead of interpreting it. Every response carries `Content-Security-Policy: default-src 'none'; sandbox`.

**`inbox.header_filename` is new.** `Content-Disposition` needs a filename, and `cp` into `inbox/` is a supported way to add an item — so the serve path sees names `safe_name` never built. `resolve_item` rejects a separator and a traversal but says nothing about a quote or a newline, and macOS permits both. Unescaped in a header value, either one is header injection.

**`MAX_ITEM_BYTES` is 250 MB.** Its old comment justified 25 MB as *"a way to fill a disk from the LAN"*; `_serve_inbox_store` calls `_require_loopback()` first, so the LAN never reaches it. The comment now names the real ceiling: the renderer base64s the whole file into one JSON request, so both ends hold it in memory at once.

## Why the old list was not the guard

Four things, each checkable:

1. `../../.ssh/authorized_keys` is refused by the `_SAFE` substitution and again by the `relative_to` containment re-check. Both still refuse it with the list gone.
2. `write_bytes` does not set the execute bit and nothing in the cockpit runs a file out of `inbox/`.
3. `.svg` was **on** the list. An SVG can carry `<script>`, and `/_inbox/<name>` served it as `image/svg+xml` at the cockpit's own origin. `.zip` was **off** it, and a zip is bytes the server never opens.
4. `INBOX_READABLE` in `renderer.ts` already listed `.html`, `.css`, `.js`, `.ts`, `.py`, `.sh` and `.tsv` — seven types the server refused to store. The client half had been built for arbitrary types all along.

[[TASK-0233]] recorded that two guards in this same file could not fire, and named it the defect this codebase had found four times. The allow-list was a third one in the same file, and that note has been corrected to say so.

## Verification

`tests/test_inbox.py`, 28 tests, all passing. Four are new and cover the serve path, which is where the safety property now lives.

Each new guard was checked by removing it and confirming a test goes red — the rule [[ISS-0056]] set for this file:

| Guard removed | Tests that fail |
| --- | --- |
| `inline = True` (serve everything with its own type) | `test_an_inert_type_is_served_as_an_attachment`, `test_a_hand_copied_name_cannot_inject_a_header` |
| `header_filename` returns its input | `test_header_filename_cannot_break_a_header`, `test_a_hand_copied_name_cannot_inject_a_header` |
| suffix not sanitised | `test_the_suffix_is_sanitised_like_the_stem` |

The oversize test now patches `MAX_ITEM_BYTES` down rather than posting a real body: at 250 MB it would allocate a third of a gigabyte again as base64 to prove a comparison.

## Not changed

`tools/cockpit/` still carries the old allow-list. That tree is the pinned release snapshot owned by `tools/scripts/release-to-project-os.sh` (`CANONICAL_SHA` 2026-07-28) and is refreshed by a release, not by hand.

`renderer.ts` needs no change: unknown suffixes already fall through to a generic icon and a *"No in-app preview for this type — open it in Finder"* stage, which was written for types the server would not accept and is now reachable.
