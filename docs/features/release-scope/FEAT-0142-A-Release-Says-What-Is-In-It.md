---
type: "[[feature]]"
id: FEAT-0142
aliases: ["FEAT-0142"]
title: "A release says what is in it — the derived set becomes an editable scope, so a feature can be held back without hand-writing the note's frontmatter"
status: backlog
owner: user:edwin
created: 2026-08-20
updated: "2026-08-20"
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: approved
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
source: ["user:edwin"]
goal: "A person preparing a release can move a feature out of it, or hold one for the next one, from the release page — and the record says which features were CHOSEN rather than which happened to be finished."
requirements: []
tasks: []
release: ""
acceptance: ""
design: ""
related: ["[[ADR-0040-A-Release-Selects-Its-Features-Not-Its-Excuses]]", "[[ISS-0181-Four-Things-The-Release-Surface-Cannot-Do]]", "[[ISS-0206-A-Check-Cannot-Belong-To-A-Release]]", "[[FEAT-0072-The-Release-Surface]]", "[[ADR-0035-A-Release-Page-Reports-It-Does-Not-Record]]", "[[ADR-0028-Publication-Is-The-Third-Phase]]"]
tags: [feature]
---

# A release names its contents by choice, not by timing

## Goal

Edwin, 2026-08-20: *"we still have not implemented a way to include/exclude features in a release."*

Confirmed absent. `publication.py` has exactly two modes and no third:

| release state | contents | who chose |
|---|---|---|
| unreleased | `kind: "derived"` — every unshipped feature since the last tag (`unreleased_payload`) | **nobody** |
| released | `kind: "frozen"` — the note's own `features:` list | whoever hand-wrote the frontmatter |

So the only way a feature leaves a release is for a person to open the note and edit YAML, and the only moment the choice is recorded is the moment the release ships. Before that, *"what is in it"* is a statement about **when work finished**, not about what anybody decided.

## Why this is a feature and not an issue

Nothing is broken. The derived set is the right default and should stay the default — it is what makes a release page useful in a repo where nobody has curated anything. What is missing is the **act of deciding**, and there is no note for it anywhere: [[ISS-0181]] covers four other things the release surface cannot do, [[ISS-0206]] is about checks rather than features, and the release-surface feature was scoped to reporting.

## Scope

**In:**

- Hold a feature back from the release being prepared, and put a held one back in.
- Persist the decision where it survives a re-render and a restart — the release note is the obvious home, since that is already the frozen record.
- The page distinguishes **derived** rows from **chosen** rows, so a reader can tell a default from a decision.
- A held-back feature has somewhere to go: the next release, or explicitly nowhere yet.

**Out:**

- Anything that writes an acceptance verdict. [[ADR-0035]] holds: a release page reports, it does not record — and this feature must not become the exception that reopens it. Scope selection is a fact about the *release*, which the release note already owns; a check's verdict is a fact about a check.
- Reordering, grouping or annotating the contents list.
- Issues and requirements. Features first; the same mechanism can widen later if it earns it.

## The mechanism (Edwin, 2026-08-20)

> *"If we can just have all the features available for the release in the release document at first with a checkbox all new features checked and then the user can uncheck/check some of them if they need to be included, the acceptance tests for the release can then be adjusted based on the selected features."*

**A checkbox list in the release document.** Every available feature is a row; a new one arrives checked; a person unchecks what is not going in.

This fits the grain of the system better than a control that lives only in the UI. [[ADR-0009]] makes notes the authored source of state, this codebase already parses checkboxes out of note bodies — phase exit criteria, and the release note's own *still owed* boxes — and a list in the document renders in Obsidian **and** the cockpit, is hand-editable, and shows up in a diff. Defaulting new features to checked also makes the whole feature additive: a repo that never touches it keeps exactly today's behaviour.

Two properties it must have, or it rots into the thing it replaced:

- **Reconciled on render, never written once.** A feature completed after the list was authored appears on it, checked, without anybody re-running anything; an unchecked one is never silently dropped. The release note in this fleet has already drifted once for exactly this reason — it was hand-maintained and nothing reconciled it.
- **One source, not two.** `publication.py` reads `features:` from frontmatter for a shipped release. The checkbox list is the **working** state; `features:` is written **at the seal**. Two live representations of one fact is how two surfaces come to disagree, and [[ADR-0035]]'s frozen-record guarantee depends on the frozen one having a single moment of authorship.

> **Basis of every `your-trainer` figure in this note: its WORKING TREE on 2026-08-20, not `HEAD`.** Corrected after independent review, which caught the phase's own recorded lesson being repeated. The difference is not a rounding: at `HEAD` that repo has **581 items, 68 blocking, and ZERO command-bearing checks** — so there is **no automated section there at all**, and the 89 checks, their empty `evidence:`, the nine at `mark: todo` and the shared 22-character command prefix exist only in the 591-file working tree. Its Feature tests head reads `65 of 507 outstanding` at `HEAD` against `49 of 411` in the tree.
>
> **The findings do not depend on the basis; the numbers do.** A head that miscounts, a percentage over checks with no result, and a uniform glyph are defects of the code, reproducible on any corpus that has the shape. What the working tree supplies is the *scale*.

## The three open questions, answered

**Q1 — where does the decision live before the release ships?** *Answered:* in the release document, as the checkbox list above, with `features:` written at the seal.

**Q3 — does excluding a feature change the gate?** *Answered by [[ADR-0040]], and not with a plain yes.* **Selection subtracts; it never divides.** Every check gates except one whose `covers:` names *only* deselected features. A check covering both a selected and a deselected feature still gates. A check with no `covers:`, or covering only an `ISS`/`REQ`/`PHASE`, is untouched by selection.

The measurement is why. in `your-trainer`'s **working tree** (not `HEAD` — see the basis note above), 2026-08-20 — 59 blocking checks: 39 cover a `FEAT`, 18 cover only `ISS`/`PHASE`, 2 carry no `covers:` at all. The 39 land on **nine** features, and **six of those nine (36 checks) are not in this release's 32-feature derived contents**. Scoping the gate *to* the selection would take it from 59 to about 23 on the first render, by nobody's decision, and would empty the `chronic` bucket whose whole purpose is to keep long-carried debt visible.

**Q2 — what does holding back mean when the feature is already `done`?** *Answered, and it is the sharpest constraint here.* Five of those six out-of-scope carriers are `done` — merged, in the binary, shipping regardless of what any list says. **A checkbox controls what a release is accountable for, never what it contains.** Dropping the checks of a `done` feature is shipping unverified code, not deferring code. Legitimate behind a flag or as accepted risk; an illegitimate convenience otherwise — so the page must distinguish *held for a later release* from *in the build, not verified here*.

## What this feature is NOT for

Edwin, same day: *"these are open because of multiple of reasons and happy to re-evaluate them for each release to see if we can resolve them but more than likely they will stay open for this release as well. (for instance I don't have the hardware to test those corner cases)"*

**That is not a scope decision and must not be expressed as one.** [[ADR-0037]] already built it, in the ledger's outcome vocabulary:

| outcome | clears | survives the seal | for |
|---|---|---|---|
| `na` | yes | **yes** | the check can never apply here — *no such surface on this platform* |
| `excused` | yes | **no** | not done this cycle, by decision — **owed again after the seal** |
| `blocked` | **no** | — | temporarily impossible by accident; blocks deliberately |

`excused` **is** re-evaluate-every-release, by construction. Using deselection for a hardware gap would put a fact about a check into a list about features, lose the reason, and make it permanent — the exact property `excused` was designed not to have.

**And it cannot be used in the repo that needs it.** `your-trainer` has **no `docs/releases/ledgers/` directory at all** — not one recorded verdict — and its checks still carry `mark:` in frontmatter. So its 59 blockers are unticked notes rather than considered decisions, and the tool has never had anywhere to put the reason. **That is a prerequisite for this feature being useful**, and it belongs to [[ISS-0209]].

## Acceptance

- A feature can be unchecked in the release being prepared and re-checked, with no hand-editing of frontmatter, and the list is reconciled against the live derived set on every render.
- The choice survives a reload and a restart, and a feature completed after the list was authored appears on it, checked, without intervention.
- Unchecking a feature removes **only** checks whose `covers:` names no selected feature; a check with no `covers:` or covering an `ISS`/`REQ`/`PHASE` is unaffected. Guarded by a test built on the mixed case — a check covering one selected and one deselected feature — because that is the cell a subtraction rule gets wrong.
- Every exclusion carries a reason, and the page reads `N features held back · M checks no longer gating`. A total that fell says why it fell.
- `chronic` still counts an excluded check. It stops blocking; it does not stop being counted.
- A shipped release's contents remain frozen — [[ADR-0035]] is not weakened, and no write path to a check appears on the release page.
- Nothing ships before [[ADR-0040]] is accepted.

## Links

- Plan: `plan/PLAN.md`
- Server: `src/project_os_cockpit/publication.py` (`kind: "derived"` / `kind: "frozen"`)
- Client: `desktop/src/renderer/renderer.ts`, the release contents section

## Independent review — 2026-08-20

Fresh-context pass, separate session, `model:claude-opus-5`. Started from the notes and the diff `222e19e..6cc7f72`; the author's reasoning trace was not available to it. Verdict: **changes-requested**.

Scope, mechanism and the three answered questions are consistent with `ADR-0040` and with the code: `publication.release_payload` really does have exactly two modes and no third, and the `derived` contents count is 32 as stated. The acceptance criterion naming the mixed case — *a check covering one selected and one deselected feature* — is the right cell to guard, and the `excused`-not-deselected split is argued from `ADR-0037`'s actual vocabulary rather than asserted.

**Same single correction as `ADR-0040`**: *"On `your-trainer` at HEAD, 2026-08-20 — 59 blocking checks: 39 / 18 / 2 … six of those nine (36 checks)"* is a working-tree measurement. At HEAD it is 68 / 43 / 17 / 8, ten features, 40 out of scope. The conclusion is unaffected.

One live inconsistency to resolve before anything is built: the criterion *"Nothing ships before ADR-0040 is accepted"* now points at a note whose frontmatter says `accepted` and whose body says `Proposed`.

## Independent review — second pass, 2026-08-20

**This supersedes the first-pass verdict above. Current verdict: approved.** Same reviewer, same conditions — fresh context, separate session, `model:claude-opus-5` — re-run against the working tree after the first pass's findings were acted on. Every claim below was re-measured or re-executed rather than read.

Basis blockquote present and its figures re-verified. The measurement it rests on reproduces exactly at the stated basis (59 / 39 / 18 / 2, nine features, 3-in / 6-out, `FEAT-0074` `backlog` with 20 = the whole `quiet` bucket, five of six `done`, ledgers in one of twelve repos), and the conclusion holds at HEAD too (40 of 43). Nothing further from me.
