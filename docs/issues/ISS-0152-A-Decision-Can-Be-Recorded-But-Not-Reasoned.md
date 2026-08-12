---
type: "[[issue]]"
id: ISS-0152
aliases: ["ISS-0152"]
title: "A human can record that they decided and never why — every write path carries a verdict or a vocabulary, and only the criterion tick carries the person's own words"
status: triage
severity: medium
owner: user:edwin
created: 2026-08-12
updated: 2026-08-12
phase: "[[PHASE-999-Future]]"
features: ["[[FEAT-0060-Transitions-And-Ticks-On-The-Note]]"]
tasks: []
related: ["[[ADR-0010]]", "[[ISS-0126]]", "[[DES-0005-The-Actuator-Grammar]]", "[[ADR-0007-Planning-Artifact-Approval-Gate]]"]
tags: [issue, actuators, review]
---

# A decision can be recorded but not reasoned

## What was found

Edwin, 2026-08-12, opening [[ADR-0010]] to decide it: *"this is not as straight forward as simply accepting, it asks questions but I cannot answer these or provide additional comments in the tool."*

He is right, and the note is the honest evidence. `GET /api/notes/actions?id=ADR-0010` answers with exactly two verbs and no fields:

```json
{"verb": "Accept", "to": "accepted", "endpoint": ""}
{"verb": "Supersede", "to": "superseded", "confirm": true, "endpoint": ""}
```

**But ADR-0010 is not a yes/no.** It lays out three options, proposes the third, and leaves live questions inside its own consequences — the read-only digest deferred to a later feature, and `Recent`'s fate settled *"by the same rule"* rather than decided. Accepting it stamps all five consequences and both open threads at once. There is nowhere to say *"yes to option 3, but not consequence 3 as written"*, and no way to ask the question the ADR provoked.

## The gap, measured across every write path

| endpoint | what it accepts | the person's own words? |
|---|---|---|
| `notes/transition` | `id, to, actor, mtime, severity` | **no** |
| `notes/review` | `id, reviewer, verdict, status, mtime` | **no** |
| `design/verdict` | + `design_revision` | **no** |
| `notes/decide` | `id, reviewer, accept, mtime` | **no** |
| `notes/test-run` | `id, outcome, steps, runner…` | steps only |
| **`notes/tick`** | `id, criterion, evidence, reason…` | **yes** |

**One path in six carries prose, and it can only attach it to a checkbox line.** [[DES-0005]] made that deliberate — *"a tick carries evidence, a reconcile carries a reason"* — and the pattern was simply never extended to the verbs that decide a whole note.

## Why the existing question mechanism does not cover it

`review.py` has a `question` kind, described as *"the agent asking the human something and blocking on the answer"*, and `resolve()` takes a note that becomes `resolution_note`. That is the **opposite direction**: agent → human. There has never been a human → record path for prose.

And [[ISS-0126]] cancelled [[FEAT-0062]], which would have built the answering half — correctly, on measurement: **0** ledger entries of kind `question` and **0** genuine `changes-requested` obligations. That decision does not cover this case. It retired a queue nobody was filling; this is a person, at a decision, with something to say and nowhere to put it.

## A second gap the same note exposes

The `adr` vocabulary is `Accept` or `Supersede`. **There is no way to say "not as written".** Superseding requires a successor note to exist, so the only recorded form of "no" is writing the replacement first. `changes-requested` exists as a verdict in the review vocabulary and is unreachable from an ADR.

## Options

1. **A transition carries an optional note.** `TRANSITION_REQUEST_KEYS` gains `note`; it is appended to the note under a dated, attributed heading. Mirrors the tick exactly, lands in the durable record where the decision lives, and makes *every* human verb able to say why — not just this one.
2. **A `Comment` verb that changes no status.** Records prose against a note without deciding it. The risk is a third state — commented-but-undecided — that nothing reads, which is the shape [[ISS-0126]] cancelled a feature for.
3. **Open questions become criteria on the note.** A decision note carrying its unresolved questions as acceptance criteria makes them tickable *today*, one at a time, with evidence text, through machinery that already exists and is already guarded. No new write path.
4. **Add `Request changes` to the ADR vocabulary**, writing `review_verdict: changes-requested` without a status move, so "no, not as written" is recordable at all.

**Recommended: 3 then 1**, and not 2. Option 3 costs nothing and answers ADR-0010 specifically — its open threads become answerable this afternoon. Option 1 is the general fix and is small, and prose beside a verdict is a pattern this codebase already has rather than one it would be inventing. Option 4 is worth doing with 1, since they are the same shape: a verb that records a judgment other than yes.

Filed at `triage`: which of these to build is Edwin's, and the ADR it blocks is his to decide either way.
