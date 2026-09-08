---
type: "[[issue]]"
id: ISS-0290
aliases: ["ISS-0290"]
title: "A person walking a checklist cannot record a pass, because a verdict needs a platform, the client has none to send on a two-ledger repo, and the refusal is written for whoever is calling the API"
status: fixed
phase: ""
owner: user:edwin
created: 2026-09-08
updated: 2026-09-08
source: ["Edwin, 2026-09-08: 'Could not mark the test as passing because there was no ledger for it (this is the second time this happened, can you make sure this doesn't happen again and that when creating a new release that the ledger is automatically created and can accept the new verdicts?)'"]
severity: high
component: publication
parent: ""
related: ["ISS-0272", "[[ISS-0288-The-Release-Gate-Ignores-The-Release-Platform]]", "[[ISS-0289-An-Absent-Platform-Is-Read-As-Every-Platform]]", "[[ADR-0037-A-Verdict-Is-An-Event]]", "[[FEAT-0145-Preparing-A-Release-Is-One-Workflow]]"]
tests: []
---

# The second time, and the first fix only covered the easy half

## Problem

A verdict names the platform it was earned on — [[ADR-0037-A-Verdict-Is-An-Event]], and the refusal in `record_verdict` is right, because 579 of `../your-trainer`'s acceptance notes once recorded an Android result as a platform-free fact.

The client has to supply that platform, and on a repo with **two** ledgers it has nothing to supply. `verdictPlatform()` in the renderer returns the picker's value, or the sole ledger platform when there is exactly one, or `""`. `your-trainer` keeps `WORKING-android.json` and `WORKING-ios.json`, so it returns `""`, the mark routes to the pre-ledger writer, and that writer refuses.

Reproduced against a live sidecar on the real repo, 2026-09-08:

```
POST /api/notes/mark-check {"id": "TST-0648", "verdict": "pass"}
→ {"ok": false, "error": "this repo records verdicts in a ledger, so a mark
   cannot be written onto a note — a verdict is an event and needs the platform
   it was earned on (ADR-0037). Use the ledger write path and send `platform`."}
```

**Twice now, and the same person both times.** ISS-0272 is the first: *"My understanding of the functionality is that I update the notes and you then update the ledger, I do not update the ledger directly."* That is the right expectation — where a verdict is stored is the tool's business. ISS-0272 fixed the unambiguous case (one ledger platform, send it) and left the ambiguous one refusing, on the reasoning that guessing between two platforms is worse than asking. The reasoning holds. What it missed is that **nobody was asked**: the refusal is not a question a walker can answer, it is an error message about a write path.

## The declaration that was already in the record

An open release says which platform it ships. The release page has read that field since [[ISS-0288]] and the acceptance endpoint since [[ISS-0289]] — both landed the same day, both for the same reason. The write path was the third reader and was still asking the client.

A repo preparing an Android release is being walked on Android. That is not a guess; it is what the release note says.

## Fix

**`note_writes.verdict_platform(docs_root, index, given)`**, used by the mark route, resolving in this order:

1. what the caller sent — an explicit answer is never overridden;
2. the open release's `platform:`;
3. the only ledger platform, if there is exactly one (ISS-0272, unchanged);
4. nothing, and the refusal stands — two platforms and no open release is a real question.

**`create_release` takes a `platform:` and writes it**, which it never did: every release the tool drafted arrived platform-less, so all three readers above fell back to their fail-closed answers. Naming it also calls **`ledger.ensure_working`**, so the ledger the release will be walked against exists from the moment the release does.

**The refusal is rewritten for the person who meets it.** It now names the platforms the repo keeps ledgers for and says that opening a release with a `platform:` is what answers it.

## What this does not change

`record_verdict` still requires a platform and still refuses without one. The resolution happens at the front door, in a named function both front doors can call, rather than as a default inside the writer — a default there would put the platform-free verdict back with a friendlier interface.

`ledger.append` already created the file on its first write, so a missing ledger never blocked a verdict. What blocked it was having no platform to write against. `ensure_working` matters for the other half: `ledger.platforms()` reads the directory, so until a file exists the tool does not know the repo has that platform.

## Guard

`tests/test_verdict_platform_resolution.py`, ten cases: the resolution order including the two that must not fire, the refusal naming what would answer it, a created release making its ledger, an existing ledger never being overwritten, a platform that would escape the ledger directory being refused, and the end-to-end — create a release, then mark a check sending no platform at all. Three fail without the fix.
