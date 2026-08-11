---
type: "[[design]]"
id: DES-0009
aliases: ["DES-0009"]
title: "The standing worker — the loop, the lease, the policy it consults, and what the human reads afterwards"
role: proposal
status: "accepted"
phase: "[[PHASE-027-The-Standing-Worker]]"
owner: user:edwin
created: 2026-08-03
updated: "2026-08-11"
source: ["[[ADR-0009-The-Principal-Is-A-Role]]", "Edwin 2026-08-03: full maintenance independent of a human"]
asset: "DES-0009-standing-worker.html"
implements: []
supersedes: ""
superseded_by: ""
reviewed_by: "user:edwin"
review_date: "2026-08-11"
review_verdict: "approved"
related: ["[[FEAT-0074-The-Standing-Worker]]", "[[FEAT-0075-The-Delegation-Policy]]", "[[FEAT-0076-Escalation-With-Defaults]]", "[[FEAT-0077-The-Intent-Charter]]", "[[RISK-0006-The-Unattended-Worker]]"]
design_revision: "31eac79"
---

# The standing worker

## The loop, in one paragraph

The driver runs beside the sidecar it already knows: **acquire the lease → select → dispatch a session → watch → record → release → next**, until a stop condition. Selection is LIFECYCLE step 2 as code — the focus item if workable, else backlog by phase order, severity, and the dependency graph — and every choice writes a one-line *reason* into the dispatch ledger, because an unattended system's first duty is to be explainable afterwards. Sessions are the same instrumented terminals the shell runs today; the driver is a caller of existing machinery, not a second agent runtime.

## The lease

`focus` in SNAPSHOT.yaml stays what ADR-0009 left it — the *statement* of what is being worked. The **claim** is operational, not documentation: `.cockpit/lease.json` (worker id, item, acquired, heartbeat), refused while live, expiring loudly when a heartbeat lapses — the expiry is an escalation event, never a silent takeover. Two workers on one repo is thereby a refusal, not a race. The lease never enters git; a claim is state, not record.

## The policy the actuators consult

A per-repo **delegation policy note** (`docs/DELEGATION.md`, principal-approved through the actuator row, so the policy itself passes through the gate it configures). Shape:

```
delegate:
  triage:      { to: "agent:principal", up_to_severity: medium }
  req-approve: { to: "agent:principal", when: "feature effort ≤ M" }
  acceptance:  { to: "agent:principal", charter: "[[INTENT]]" }
escalate:
  question:    { after: 48h, then: proceed-on-assumption }
  triage-high: { after: 0,  then: wait }   # severities above the line always wait
```

PHASE-023's `GET /api/notes/actions` gains a caller identity: for `agent:principal` it answers from this table — an action outside policy is simply not offered, and the endpoint refuses it if asked (REQ-0030's two layers, same pattern as REQ-0026). Every write a delegate performs carries `(agent:principal, delegation: DELEGATION.md@<sha>)` — [[REQ-0029]]: the audit can always answer *who decided, under what authority, as the policy stood when*.

## Open question, raised before the lease is built (2026-08-05)

The lease above makes a second worker a **refusal**. The t3.codes comparison offers the other answer: a **git worktree per thread**, so parallel agents are isolated rather than excluded — T3 runs many agents on one repo this way, each in its own working tree, and the glossary makes the worktree a first-class concept of a thread.

Both are defensible and they are not compatible:

| | refuse (this design) | isolate (worktree per worker) |
|---|---|---|
| second worker | told who holds the lease | works in its own tree |
| `focus` | one item, one statement | several in flight, focus means less |
| close-out | commits the repo it read | commits a tree that must be merged |
| failure mode | idle capacity | merge conflicts, and a validator run per tree |

**Refusing is right if the constraint is judgment**, which is where this phase places it — one principal, one intent, sequential attention. **Isolating is right if the constraint is throughput.** The autonomy case argues for judgment: a worker outrunning its supervisor's ability to read the digest is not a throughput win.

Recommendation: **ship the lease as designed, and keep worktrees for the day the digest is boring** — the cheaper path is reversible and the expensive one is not. Recorded on [[TASK-0324]] so the decision is made rather than defaulted.

## Escalation that degrades instead of stalls

Each queue kind carries a timeout and a default from the policy. A question passing its timeout **proceeds on a recorded assumption**: the assumption is written as the question's resolution, the affected work is tagged with it, and the digest lifts it to needs-you — the human reads what was assumed, not what was hidden. Kinds with no default (high-severity triage, anything touching publish) **wait and alarm**: past 2× timeout they join the landing's NEEDS-YOU. Nothing in the system can wait silently forever — that is the invariant, tested by drill.

## Stop conditions ([[REQ-0031]])

Budget (sessions and wall-clock per day), failure backoff (two consecutive failed close-outs on one item parks it with an issue; three parked items halts the worker), validator red beyond its own session, and the human's stop switch on the landing card. Halting files what it was doing and why into the queue. **The default state of an unconfigured repo is: no worker.** Autonomy is opted into per repo by the existence of an approved DELEGATION.md — there is no global switch.

## What the human reads afterwards

No new surfaces. The week lands in what PHASE-024/026 already build: the digest (with assumed-answers lifted), the acceptance queue (what the delegate accepted, spot-checkable), the debt card, the ledger. Supervision is reading, and the reading was already designed.

## Rejected alternatives

- **A cron-style scheduler config.** The policy note is the configuration; a second config file would split authority from record.
- **Silent takeover of stale leases.** An expired lease means something went wrong; wrongness escalates.
- **A global autonomy switch.** Per-repo opt-in by approved policy keeps the blast radius the size of one repo's DELEGATION.md.

## Offered for review — 2026-08-11

I moved this `draft → proposed` while working [[REL-0001]]'s leg 2, and **the validator refused it**:

> `ERROR [DESIGN-ASSET] DES-0009 is 'proposed' and declares no asset:; a design offered for review needs a rendered artifact (draft is exempt)`

Correct, and the rule is right: offering a design for review means asking somebody to look at something, and a note with no artifact gives them prose to read rather than a shape to judge. `draft` is exempt precisely so a design can be written before it can be seen.

Reverted to `draft`. **What this note needs before it can be offered is an artifact**, not a status change — [[FEAT-0067]]'s `## Variant <name>` sections now make that cheap, and this design (the loop, the lease, the policy) has at least the ledger view and the escalation states to show.

Offering is an agent's act and accepting is not — `note_writes.HUMAN_TRANSITIONS` lists `design: proposed → accepted` as human-owned and the server refuses it to an agent ([[REQ-0026]]). So the sequence is: an artifact, then `proposed`, then Edwin. [[PHASE-027]] waits on all three, since [[FEAT-0074]]–[[FEAT-0076]] build the loop this note shapes.

## Variant Worker states

```html
<div style="font:13px/1.5 system-ui;display:flex;gap:10px;flex-wrap:wrap">
  <div style="border:1px solid #3a3f45;border-radius:6px;padding:10px 12px;min-width:150px">
    <div style="font-weight:600">idle</div>
    <div style="opacity:.7;font-size:11.5px">no workable item — a stop condition, not a busy-wait</div>
  </div>
  <div style="border:1px solid #3a3f45;border-radius:6px;padding:10px 12px;min-width:150px">
    <div style="font-weight:600">working</div>
    <div style="opacity:.7;font-size:11.5px">lease held · budget counting · one item</div>
  </div>
  <div style="border:1px solid #7a5a2a;border-radius:6px;padding:10px 12px;min-width:150px">
    <div style="font-weight:600">escalated</div>
    <div style="opacity:.7;font-size:11.5px">waiting on a person — lapses to an assumption, or alarms</div>
  </div>
  <div style="border:1px solid #7a3a3a;border-radius:6px;padding:10px 12px;min-width:150px">
    <div style="font-weight:600">halted</div>
    <div style="opacity:.7;font-size:11.5px">files what and why — an obligation on the desk, not an absence</div>
  </div>
</div>
```

## Variant The six halt reasons

```html
<div style="font:13px/1.5 system-ui">
  <table style="border-collapse:collapse;width:100%">
    <tr><td style="padding:4px 8px;font-weight:600">stop-switch</td>
        <td style="padding:4px 8px;opacity:.75">a human asked — outranks every computed halt</td></tr>
    <tr><td style="padding:4px 8px;font-weight:600">no-delegation</td>
        <td style="padding:4px 8px;opacity:.75">the default: no approved policy, no worker</td></tr>
    <tr><td style="padding:4px 8px;font-weight:600">validator-red</td>
        <td style="padding:4px 8px;opacity:.75">working on a broken record compounds it</td></tr>
    <tr><td style="padding:4px 8px;font-weight:600">parked-items</td>
        <td style="padding:4px 8px;opacity:.75">three parked — failure is compounding, not clearing</td></tr>
    <tr><td style="padding:4px 8px;font-weight:600">session-budget</td>
        <td style="padding:4px 8px;opacity:.75">sessions per day</td></tr>
    <tr><td style="padding:4px 8px;font-weight:600">wall-clock</td>
        <td style="padding:4px 8px;opacity:.75">minutes in one session</td></tr>
  </table>
</div>
```

*Both variants render what this note already specifies — they are the shape a reviewer judges, not a new proposal. Added by [[TASK-0332]]: the validator refuses a `proposed` design that declares no artifact, and correctly, because offering a design for review means asking somebody to look at something.*


**Now offered.** `DES-0009-standing-worker.html` renders one turn, the four states, every halt reason, what a selection records, and what is never delegated — all of it what this note already specifies, drawn so a reviewer judges a *shape* rather than reads prose. `draft → proposed` is an agent's act; **accepting it is not** — `HUMAN_TRANSITIONS` puts `design: proposed → accepted` with the principal, and the server refuses it to an agent ([[REQ-0026]]).

Every mechanism drawn here exists and is tested: the six halts drilled in `tests/test_worker.py`, the lease, the policy defaulting closed, the escalation clock, and the selection ledger. So this is a design offered *after* its subject was built rather than before — unusual, and worth saying plainly: what it documents is real, and what it asks is whether the shape is right.

## Accepted — 2026-08-11

**Edwin, in session: *"I accept DES-0009."*** Recorded through `/api/design/verdict` with `reviewer: user:edwin`, `verdict: approved`, pinned to revision `31eac79` — the artifact's only committed revision and the one that was on screen. Not a status hand-edited into the frontmatter: the same write the actuator row's Accept performs, so the revision check, the dirty-artifact refusal and the `design_revision` stamp all applied exactly as they would have.

**The instruction arrived in chat rather than through the button, and that is worth stating plainly rather than smoothing over.** [[REQ-0026]] reserves `design: proposed → accepted` for the principal; what it reserves is the *judgment*, not the keystroke. The judgment is Edwin's, given in his own words, and `reviewed_by` names him because he is who decided. What the record does **not** claim is that he clicked — hence this paragraph, so a reader who later wonders why there is no click in the session log has the answer in the note rather than in a transcript.

The guard held for the eleven hours it mattered: an agent asked for this transition and was refused, and it was only ever going to move when the principal said so.
