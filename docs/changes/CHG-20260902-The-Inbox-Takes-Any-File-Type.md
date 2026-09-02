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
reviewed_by: "model:claude-opus-5"
review_date: 2026-09-02
review_verdict: changes-requested
review_response: >-
  All six findings applied, none deferred.
  F1 was a real defect and is fixed with a test: `header_filename` collapsed a
  leading non-ASCII run to a dash and then stripped the dot with it, so a name
  like the Chinese-titled .docx in the finding was served as filename="docx".
  F2, F3 and F4 were false or falsified comments, corrected in place —
  including the one crediting `resolve_item` with a traversal check that cannot
  fire for any string.
  F5 was right that nothing had been observed: `sandbox` is now scoped to
  scriptable suffixes, and the browser behaviour was MEASURED in Chrome — the
  same SVG served without the policy sets document.title to SCRIPT-RAN and with
  it does not, and a PDF renders under default-src 'none'.
  F6 was the sharpest and is fixed: /api/inbox and /_inbox/ are loopback-only
  now, matching the store endpoint beside them.
  Three new tests, each mutation-checked; the guard-site census moved 28 to 30.
review_response_date: 2026-09-02
related: ["[[TASK-0233-Drop-And-Paste-Into-The-Inbox]]"]
---

# The inbox takes any file type

## Summary

Dragging a `.zip`, a `.docx`, a `.mov` or a file with no extension onto the cockpit used to fail with *"is not a storable name"*. It works now. The per-item cap goes from 25 MB to 250 MB, so a screen recording fits too.

The seventeen-suffix allow-list on the write path is gone. It read like a security control and was not one, so removing it makes the drop **safer**, not laxer — the property it was gesturing at now exists for the first time, and applies to every type rather than the sixteen it happened to name.

## What changed

**`inbox.safe_name` accepts any type.** The suffix now goes through the same `_SAFE` substitution the stem already used — lowercased, non-`[A-Za-z0-9._-]` replaced with `-`, capped at 16 characters — instead of being matched against a fixed set. An empty suffix is legal, so `Makefile` and `README` are droppable. A name with no file in it (empty, `.`, `..`) is still refused.

**`_serve_inbox_item` decides what a type means.** A suffix outside `INLINE_SUFFIXES` comes back as `application/octet-stream` with `Content-Disposition: attachment`, so the browser saves it instead of interpreting it. Every response carries `Content-Security-Policy: default-src 'none'`, and `sandbox` is added for the suffixes that can execute — `SCRIPTABLE_SUFFIXES`, currently `.svg` — plus anything already going out as an attachment.

`sandbox` was on every response in the first version. It is also the usual way to make Chrome download a PDF rather than render it, so a blanket policy would have broken PDF preview to protect a format that cannot script. Independent review raised it; scoping it is the fix.

**`/api/inbox` and `/_inbox/` are loopback-only.** The store endpoint always was; these two never were, while `--bind 0.0.0.0` is supported — so anyone on the same Wi-Fi could list the inbox and download any item in it. The bargain that bind makes is scoped to *notes*, a tablet reading the documentation. The inbox is not notes. Nothing is lost: the tray lives in the Electron renderer, which reaches the sidecar over 127.0.0.1, and no web template renders an inbox surface.

**`inbox.header_filename` is new.** `Content-Disposition` needs a filename, and `cp` into `inbox/` is a supported way to add an item — so the serve path sees names `safe_name` never built. What keeps those inside the inbox is `resolve_item`'s `relative_to` containment check; nothing there looks at a quote or a newline, and macOS permits both. Unescaped in a header value, either one is header injection.

*(This paragraph said `resolve_item` "rejects a separator and a traversal". The separator half is true; the traversal half is `".." in name.split(".")`, which cannot be true for any string, because `split(".")` never yields an element containing a dot. Independent review caught it — in a note whose subject is a guard that read as one and was not.)*

**It keeps the extension**, which took two goes. The first version was one `.strip("-.")` over the whole name, so a leading non-ASCII run collapsed to `-` and the strip took the dot behind it: `报告.docx` was served as `filename="docx"`. Every hostile name in the first round of tests began with an ASCII letter, so nothing caught it. Stem and suffix are sanitised separately now.

**`MAX_ITEM_BYTES` is 250 MB.** Its old comment justified 25 MB as *"a way to fill a disk from the LAN"*; `_serve_inbox_store` calls `_require_loopback()` first, so the LAN never reaches it. The comment now names the real ceiling: the renderer base64s the whole file into one JSON request, so both ends hold it in memory at once.

## Why the old list was not the guard

Four things, each checkable:

1. `../../.ssh/authorized_keys` is refused by the `_SAFE` substitution and again by the `relative_to` containment re-check. Both still refuse it with the list gone.
2. `write_bytes` does not set the execute bit and nothing in the cockpit runs a file out of `inbox/`.
3. `.svg` was **on** the list. An SVG can carry `<script>`, and `/_inbox/<name>` served it as `image/svg+xml` at the cockpit's own origin. `.zip` was **off** it, and a zip is bytes the server never opens.
4. `INBOX_READABLE` in `renderer.ts` already listed `.html`, `.css`, `.js`, `.ts`, `.py`, `.sh` and `.tsv` — seven types the server refused to store. The client half had been built for arbitrary types all along.

[[TASK-0233]] recorded that two guards in this same file could not fire, and named it the defect this codebase had found four times. The allow-list was a third one in the same file, and that note has been corrected to say so.

## Verification

`tests/test_inbox.py`, 31 tests, all passing. Seven are new: four cover the serve path, where the safety property now lives, and three came out of independent review.

**The SVG claim was measured, not argued** (2026-09-02, Chrome). The same file was served twice from `127.0.0.1`:

| served | tab title | drew |
| --- | --- | --- |
| with no policy header | `SCRIPT-RAN` | yes |
| with `default-src 'none'; sandbox` | the URL | yes |

The control is the part that matters. Without it, a policy that happened to change nothing would look exactly like one that closed a hole. A PDF was rendered in Chrome's viewer under `default-src 'none'` in the same session, which is what scoping `sandbox` bought.

Each new guard was checked by removing it and confirming a test goes red — the rule [[ISS-0056]] set for this file:

| Guard removed | Tests that fail |
| --- | --- |
| `inline = True` (serve everything with its own type) | `test_an_inert_type_is_served_as_an_attachment`, `test_a_hand_copied_name_cannot_inject_a_header` |
| `header_filename` returns its input | `test_header_filename_cannot_break_a_header`, `test_a_hand_copied_name_cannot_inject_a_header` |
| suffix not sanitised | `test_the_suffix_is_sanitised_like_the_stem` |
| inbox reads not loopback-guarded | `test_reading_the_inbox_is_loopback_only` |
| `sandbox` back on every response | `test_a_pdf_is_not_sandboxed_and_an_svg_is` |
| `header_filename` back to one strip | `test_the_header_name_keeps_the_extension` |

The oversize test now patches `MAX_ITEM_BYTES` down rather than posting a real body: at 250 MB it would allocate a third of a gigabyte again as base64 to prove a comparison.

## Released to the fleet

`tools/cockpit/` carried the old allow-list when this note was first written, because that tree is a delivery snapshot refreshed by a release rather than by hand. The release has since been run (Edwin, 2026-09-02) and **all twelve fleet repos now carry `cfae6b1`**, up from `afc4fa7b` — five weeks and 193 commits.

Two things the sweep found that nothing had been looking for:

- **`articles` had no `src/` at all.** Its `tools/cockpit` held four files — `CANONICAL_DATE`, `CANONICAL_SHA`, `pyproject.toml`, `run.sh` — and not the package `run.sh` exists to launch. Not gitignored; simply never committed. It was also stamped at a different release from the other eleven, so no comparison against a sibling had ever been made.
- **`validate_docs_bundled.py` differed between repos carrying the same `CANONICAL_SHA`** — 1969 lines in the four repos PHASE-041 migrated, ~1810 in the others. A delivery copy that varies at a fixed stamp is not a delivery copy, and the stamp was not enough to notice.

Each repo was committed path-scoped to `tools/cockpit`, so in-flight work elsewhere was left alone — 16 editorial files in `articles`, one gradle file in `your-trainer`. Every repo's validator passed. Nothing was pushed.

`renderer.ts` needs no change: unknown suffixes already fall through to a generic icon and a *"No in-app preview for this type — open it in Finder"* stage, which was written for types the server would not accept and is now reachable.

## Independent review, 2026-09-02 — changes-requested

Reviewed from this note, [[ISS-0274]], [[TASK-0233]] and `git show 3898d1f`, in a separate session that never saw the authoring conversation. Same model family as the author (`model:claude-opus-5`), which [[project-os-dev#ADR-0013]] says is not the gate; the fresh context is. Work was done in a detached worktree at 3898d1f, because the main tree was being edited by another session at the time.

**The central claim survives.** The old hole was real: before this change `/_inbox/x.svg` came back as `image/svg+xml` with no policy header, at the sidecar's HTTP origin, and every loopback-only write endpoint lives at that origin — so script in a navigated-to SVG could have written notes. `default-src 'none'; sandbox` closes it twice over: `sandbox` with no `allow-scripts` disables scripting and gives the document an opaque origin, and `default-src 'none'` blocks the inline script on its own. Keeping `.svg` inline for `<img>` is right, because a CSP on an image response does not govern the page that embedded it.

**The verification table reproduces exactly.** Sixteen mutations were applied to the worktree one at a time and `tests/test_inbox.py` run against each. All three rows in the table above are accurate down to the test names: `inline = True` fails `test_an_inert_type_is_served_as_an_attachment` and `test_a_hand_copied_name_cannot_inject_a_header`; `header_filename` returning its input fails `test_header_filename_cannot_break_a_header` and the same hand-copied test; an unsanitised suffix fails `test_the_suffix_is_sanitised_like_the_stem`. Twelve of the fourteen applicable mutants were caught. Also checked and clean: store → list → serve → discard round-trips for eighteen exotic names (CJK, RTL override, embedded NUL, `CON`, 200-character stems) with no item that can be created but not listed or deleted; the body-reader arithmetic `MAX_ITEM_BYTES * 4 // 3 + 4096` leaves 4093 bytes of slack over base64 of a full 250 MB item, which is enough for the JSON envelope; the full suite at 3898d1f fails exactly the same four tests as at 3cd44a8, so this change breaks nothing elsewhere; `validate-docs.sh` is OK.

Six findings.

**1. `header_filename` deletes the extension for the names it exists to handle** (`src/project_os_cockpit/inbox.py:106`, low-medium). `cleaned = _SAFE.sub("-", name).strip("-.")`. When a hand-copied name starts with a non-ASCII character, `_SAFE` collapses that run to one `-` and `strip("-.")` then eats the `-` **and the dot behind it**. Served live: `报告.docx` comes back as `attachment; filename="docx"` and `éé.zip` as `filename="zip"`. The download lands as a file called `docx` with no extension. Names over 76 characters lose the extension the other way, to the truncation at line 107. Neither case has a test — mutating line 107 to `return cleaned` leaves the suite green. `safe_name` output is immune because its ASCII timestamp prefix protects the leading edge, so this only bites the `cp`-into-`inbox/` door, which is the door the docstring says the function was written for.

**2. The endpoint docstring still describes the allow-list this commit deleted** (`src/project_os_cockpit/server.py:3721-3724`, medium). It reads "`inbox.safe_name` keeps only a sanitised stem and an allow-listed suffix". There is no allow-listed suffix any more and the code that removed it is fifteen lines below. A maintainer reading the endpoint top-down is told the guard is somewhere it is not.

**3. A new comment credits `resolve_item` with a check that cannot fire** (`src/project_os_cockpit/server.py:3838-3841`, medium). It says `resolve_item` "rejects a separator and a traversal". The traversal clause is `".." in name.split(".")` (`inbox.py:167`), and splitting a string on `"."` can never produce an element containing `"."` — brute-forcing every string up to length five over `{. a b /}` gives zero hits. Traversal is refused by the `relative_to` containment two lines further down, which is what the comment should credit. This is the only new prose in the diff that asserts an existing guard, and it is the same defect the change was written to fix.

**4. The change falsified a claim it left standing** (`src/project_os_cockpit/inbox.py:72-75`, and the same sentence in [[TASK-0233]], medium). Both still say the basename split is redundant and that "removing it leaves every test green". `test_a_name_with_nothing_in_it_is_still_refused` adds `"///"` to the refusal set, and with the split removed `safe_name("///")` returns `20260902-…-item` rather than `None` — the test goes red. The line the docstring calls decorative became load-bearing in this commit.

**5. Every browser claim is argued; none is observed** (medium). The safety property is now two response headers, and the four new serve-path tests assert only that those header strings are present. Nothing exercises a real Chromium. The claim I would not bet on is `.pdf` staying in `INLINE_SUFFIXES`: Chromium's PDF viewer needs scripting, and a response carrying `sandbox` without `allow-scripts` is the ordinary way to make Chrome download a PDF instead of rendering it — which would make `.pdf`'s membership do the opposite of its stated purpose. In-app nothing breaks, because `renderInboxItemView` sends PDFs to Finder rather than to an `<iframe>`; it would only show for someone opening `/_inbox/x.pdf` in a browser. This repo keeps a live acceptance-walk venue, and a note that asserts browser behaviour six times should have used it once.

**6. "Safer, not laxer" is argued against the browser and never against the LAN read** (medium; a gap in the reasoning, not a new hole). The note retires the old cap's rationale with "`_serve_inbox_store` calls `_require_loopback()` first, so the LAN never reaches it". True of the write. `_serve_inbox_item` and `GET /api/inbox` have no `_require_loopback` (`server.py:1167`, `server.py:1174`), and `--bind 0.0.0.0` is a supported mode whose bargain `server.py:1684` states as a tablet on the Wi-Fi being able to *read the notes*. The inbox is not notes — it is untriaged, gitignored external material — and after this change it takes every file type at ten times the size. Nothing in the diff makes that route wider than it already was, but a reader who takes "safer, not laxer" at face value will not learn from these notes that anything they drop is readable unauthenticated from the LAN whenever that mode is on.

Three smaller drifts, worth a sweep rather than separate findings: `server.py:1697` still says `MAX_ITEM_BYTES` "advertised 25 MB", so only one of the two comments about the cap was updated; `inbox.py:35-36` calls `INLINE_SUFFIXES` the suffixes served "with their own content type", which is false for `.yaml` and `.yml` — `mimetypes.guess_type` has no answer for either, so both come back `application/octet-stream` without the attachment disposition; and "28 tests… Four are new" reads as four new tests when nine are new, four of them on the serve path.

**Not a finding, checked and dropped:** `tests: []` on [[ISS-0274]]. [[FEAT-0045-Project-Inbox]] records that decision for this feature and a previous review accepted the reasoning.

No `ISS-*` notes were filed for the above. Another session was concurrently allocating IDs in `SNAPSHOT.yaml` during this review, and racing it for counters would have been worse than leaving the findings here.
