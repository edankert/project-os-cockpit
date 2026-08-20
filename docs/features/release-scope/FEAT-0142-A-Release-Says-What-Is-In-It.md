---
type: "[[feature]]"
id: FEAT-0142
aliases: ["FEAT-0142"]
title: "A release says what is in it — the derived set becomes an editable scope, so a feature can be held back without hand-writing the note's frontmatter"
status: backlog
owner: user:edwin
created: 2026-08-20
updated: "2026-08-20"
phase: "[[PHASE-999-Future]]"
source: ["user:edwin"]
goal: "A person preparing a release can move a feature out of it, or hold one for the next one, from the release page — and the record says which features were CHOSEN rather than which happened to be finished."
requirements: []
tasks: []
release: ""
acceptance: ""
design: ""
related: ["[[ISS-0181-Four-Things-The-Release-Surface-Cannot-Do]]", "[[ISS-0206-A-Check-Cannot-Belong-To-A-Release]]", "[[FEAT-0072-The-Release-Surface]]", "[[ADR-0035-A-Release-Page-Reports-It-Does-Not-Record]]", "[[ADR-0028-Publication-Is-The-Third-Phase]]"]
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

## Open questions

1. **Where does the decision live before the release ships?** Writing `features:` early makes the note the source of truth and the derived set an initial suggestion — simple, and it means the file says what the page says. But it also means a half-prepared release has a frontmatter list that looks frozen and is not.
2. **What does holding back mean when the feature is already `done`?** It shipped in code and not in the release. That is a real and common state, and the record should be able to express it without lying in either direction.
3. **Does excluding a feature change the gate?** A check gates via `covers:`. If the feature it covers is not in this release, its check arguably should not block it — which is [[ISS-0206]]'s question arriving from the other side, and is the reason this feature is worth doing carefully rather than quickly.

## Acceptance

- A feature can be removed from the release being prepared and re-added, from the release page, with no hand-editing of frontmatter.
- The choice survives a reload and a restart.
- The page says which rows are derived and which were chosen.
- A shipped release's contents remain frozen and unaffected — [[ADR-0035]]'s guarantee is not weakened by the new write path.
- Question 3 is answered in the record before any gate behaviour changes.

## Links

- Plan: `plan/PLAN.md`
- Server: `src/project_os_cockpit/publication.py` (`kind: "derived"` / `kind: "frozen"`)
- Client: `desktop/src/renderer/renderer.ts`, the release contents section
