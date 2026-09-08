---
type: "[[feature]]"
id: FEAT-0145
aliases: ["FEAT-0145"]
title: "Preparing a release is one workflow: name the version, say which platform, settle the checks it owes — instead of four endpoints, a hand-written note and a rule nobody can see"
status: backlog
owner: user:edwin
created: 2026-09-08
updated: 2026-09-08
phase: ""
source: ["Edwin, 2026-09-08, after preparing your-trainer's 2.2.0 by hand: 'suggest how the creation of releases can be made a little easier in the tool. I think it should probably be a new workflow: Create Release (Update and delete release should also be possible) — set the version — select: android or iOS — uncheck the required acceptance-tests for the release and add new checks if required (these might be LLM/Human actions?)'"]
goal: "A person who has decided to ship names a version and a platform, sees exactly which acceptance checks that release owes, settles the ones that do not apply, and commissions the ones that are missing — in one place, with every step recorded as an event that says who decided and why."
requirements: []
tasks: []
release: ""
acceptance_exception: ""
acceptance: ""
design: ""
related: ["[[ISS-0288-The-Release-Gate-Ignores-The-Release-Platform]]", "[[ADR-0040-A-Release-Selects-Its-Features-Not-Its-Excuses]]", "[[ADR-0037-A-Verdict-Is-An-Event]]", "[[FEAT-0142-A-Release-Says-What-Is-In-It]]", "[[DES-0012-Tests-In-Two-Flows]]"]
tags: [feature, publication, release, workflow]
---

# Preparing a release is one workflow

## What happened, and it is the whole argument

On 2026-09-08 Edwin prepared `your-trainer` v2.2.0. Every step was a hand-edit or a diagnosis:

1. The release page offered no acceptance checks, because a release carries *done-but-unshipped* features and five implemented features had been left at `backlog`. Nothing said so; the list was simply empty.
2. The release note itself was written by hand — version, platform, the five features, four held-back entries with their reasons.
3. The gate then reported **635 checks owed** on a repo with 67, because the page never told the gate which platform the release ships ([[ISS-0288-The-Release-Gate-Ignores-The-Release-Platform]]).

Three different surfaces, none of which said what was wrong. The tool has the pieces — `release-prepare`, `release-contents`, `release-verified`, `release-mark-released`, the ledger, the owed list — and no workflow that walks a person through them in the order a release actually happens.

## The shape Edwin asked for

> Create Release (Update and delete release should also be possible) — set the version — select: android or iOS — uncheck the required acceptance-tests for the release and add new checks if required (these might be LLM/Human actions?)

Read straight, that is four steps and a lifecycle. Below is what each costs against what exists today.

## Step 1 — Create, update, delete

**Create exists** (`POST /api/notes/release-prepare`) and already refuses the two things worth refusing: a second open release, and a version at or below the newest shipped one.

**Update is partial.** `release-contents` adds and removes features and makes a removal state its reason. Nothing sets the **version** or the **platform** after creation, and the platform is the field [[ISS-0288-The-Release-Gate-Ignores-The-Release-Platform]] just proved the gate depends on. Both need a write path with the same refusals as create.

**Delete does not exist at all, and should not be a delete.** `your-trainer`'s REL-0013 is the precedent: v2.1.7 was prepared, never shipped, and is still `draft` with `superseded_by: [[REL-0016-v2.1.8]]`. That is the right record — a release that was prepared and abandoned is a fact about the project, and erasing the file erases why the version number was skipped. So: **Abandon**, which sets a terminal status and requires a reason, and a true delete only for a note created minutes ago with nothing pointing at it.

## Step 2 — The platform is a choice, not a text field

`platform:` is free text today, and `_ships_on` already knows five spellings of "all platforms" because the corpus holds four of them. The workflow should offer the platforms **this repo has evidence for** — the ledger platforms plus the platforms its notes actually use — and let the answer be one of them or *every platform*, which is the union rule [[DES-0012-Tests-In-Two-Flows]] D4 already implements.

Naming the platform must immediately change the number on screen. That is [[ISS-0288-The-Release-Gate-Ignores-The-Release-Platform]]'s fix, and this workflow is the surface that makes the consequence visible: pick `android` and the gate falls from the union to the Android ledger, in front of the person who picked it.

## Step 3 — Settling the checks the release owes

This is the step with a real design question in it, and the answer is **not** a checkbox list.

**Today, "required" is derived, not authored.** A check is owed when it covers a feature the release carries and the ledger has not cleared it. [[ADR-0040-A-Release-Selects-Its-Features-Not-Its-Excuses]] chose that deliberately: a release selects its *features*, and the check set follows by subtraction, so nobody can quietly shrink the gate by unticking rows.

**"Unchecking a check for this release" already has a vocabulary** — the ledger's, from [[ADR-0037-A-Verdict-Is-An-Event]]. Three of its seven marks are exactly this, and the distinction between them is the thing a checkbox would destroy:

| mark | means | lifetime |
| --- | --- | --- |
| `na` | cannot apply on this platform, ever | permanent |
| `excused` | not walked this cycle, by decision | **this release only** |
| `blocked` | could not be run — the rig was down | still blocks, deliberately |

So the workflow does not need a new storage shape. It needs to put those three actions on the owed list, in bulk, each with the reason the write path already demands. "Uncheck this for 2.2.0" is `excused` with a reason; "this bike can never do ERG" is `na`; "the trainer is in the loft" is `blocked` and stays on the list, which is the point.

**What is genuinely missing is the walk itself being one screen** — the owed list, grouped by area, with the check's procedure readable beside the buttons, on the release page rather than a separate Tests view that has forgotten which release it is grading.

## Step 4 — "add new checks if required (LLM/Human actions?)"

Yes, and this is where an agent earns its place, because the question *"is anything this release ships not covered by a check?"* is exactly the sweep a person skips. `your-trainer` again: three of PHASE-021's claims — the per-rider preferences, the power source in History, the Pro grant a data-only bike does not earn — had no check, and only a deliberate read of thirty task notes against nine checks found them.

The honest split:

- **The tool computes the gap mechanically**: features the release carries whose `covers:` set is empty, and requirements with unticked criteria. Both are already in the index and neither needs a model.
- **An agent proposes checks for what is left**, drafting `TST-*` notes at `mark: todo` from the feature and task notes, in the repo's own voice.
- **A person accepts, edits or rejects each one.** A check nobody read is a check nobody will walk, and a generated suite that grows on its own is worse than a short one somebody meant.

Every proposal arrives as a note in the working tree, reviewed as a diff. Nothing is written into a release's gate without a person's yes.

## Not in scope

- **Cutting the build.** `release.sh` in the downstream repo owns `versionCode`/`versionName` and the artifact, and it must stay owned there.
- **A second store for "required checks".** The derivation plus the ledger is the store; a per-release list of check ids would be the hand-maintained second copy [[ADR-0032-The-Verification-Link-Has-One-Direction]] exists to prevent.
- **Deleting shipped releases.** A released note is the record.

## Acceptance (sketch, for whoever picks this up)

- Creating a release from the workflow produces the same note a hand-write does, including `platform:`, and the gate on the next screen is scoped to it.
- Changing the platform of an open release changes the owed count without touching any check.
- Abandoning a draft leaves the note, its reason and its `superseded_by:`; the version it held is not silently reusable.
- Marking `excused` from the release page writes a ledger event with a reason and clears only this release.
- The coverage sweep names at least the features carrying no check, on a repo where that is true.
