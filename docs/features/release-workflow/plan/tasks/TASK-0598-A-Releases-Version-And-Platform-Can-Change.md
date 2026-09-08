---
type: "[[task]]"
id: TASK-0598
aliases: ["TASK-0598"]
title: "A release's version and platform can be changed after it is created, with create's refusals and one it cannot make — the filename keeps the old version"
status: done
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
owner: user:edwin
created: 2026-09-08
updated: "2026-09-08"
source: ["[[FEAT-0145-Preparing-A-Release-Is-One-Workflow]]", "Edwin, 2026-09-08: 'Update and delete release should also be possible'"]
parent: "[[FEAT-0145-Preparing-A-Release-Is-One-Workflow]]"
effort: M
due: ""
depends: []
blocks: ["[[TASK-0600]]"]
related: ["[[REQ-0061-A-Release-Is-Written-Through-One-Workflow]]", "[[ADR-0035-A-Release-Page-Reports-It-Does-Not-Record]]", "[[ISS-0288-The-Release-Gate-Ignores-The-Release-Platform]]"]
tests: []
---

# A release's version and platform can change

`release-contents` can add and remove features. Nothing can set the **version** or the **platform** after a release is created — and the platform is the field [[ISS-0288-The-Release-Gate-Ignores-The-Release-Platform]] proved the gate depends on. Getting it wrong at creation currently means hand-editing frontmatter, which is the act this whole feature exists to remove.

## Definition of Done

- [x] `note_writes.update_release(index, release_id, *, version="", platform="", actor="", mtime=None)` writes whichever of the two fields it was given, and refuses to be called with neither.
- [x] **The refusals are `create_release`'s, reused and not re-derived**: the version shape; a version at or below the newest **released** one; and the platform-name shape `^[a-z0-9][a-z0-9_-]*$`, because it becomes a ledger filename.
- [x] **Setting a platform calls `_ensure_release_ledger`**, so the working ledger for the new platform exists the moment the field does. That is the other half of [[ISS-0290]]'s fix: `ledger.platforms()` reads the directory, so a platform with no ledger is invisible to every surface that counts platforms.
- [x] **A `released` release is refused**, with `release_contents`'s refusal 1 and its reason: what a shipped release contained, and shipped against, is a fact about the past ([[ADR-0035]]).
- [x] `POST /api/notes/release-update` exposes it, behind the same loopback and human-initiated guard every other note write sits behind.
- [x] **The response says the filename was not renamed** when the version changed, naming both the old stem and the new version.

## The limitation, stated rather than discovered

`REL-0013-v2.1.7.md` carries its version in the **filename stem**, and every `[[REL-0013-v2.1.7]]` in the corpus resolves by that stem. Renaming the file on a version change would break every one of those links in every repo that cites the release.

So the file is **not** renamed, the frontmatter `version:` is the authority, and the write reports the mismatch instead of hiding it. This is a real wart and it is cheaper than a corpus-wide link rewrite; whether that rewrite is worth building is a separate decision, recorded in `plan/PLAN.md` under Open questions.

## Steps

- [x] Factor `create_release`'s version-shape and version-ordering refusals into a helper both call. Two copies of a refusal is one refusal that will drift.
- [x] Write `update_release` beside `create_release` in `note_writes.py`.
- [x] Add the endpoint in `server.py` beside `/api/notes/release-prepare`.
- [x] Guard: changing the platform of an open release changes the owed set and leaves every check note's mtime untouched. The second half is [[REQ-0055]]'s rule applied to a field that is not a verdict.

## Notes

**Optimistic concurrency.** Every other note write in this module takes `mtime` and refuses a stale write; this one takes it for the same reason.
