---
type: "[[plan]]"
title: "Plan — FEAT-0102 Publication becomes a view"
status: done
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
source: []
implements: ["[[FEAT-0102-Publication-Becomes-A-View]]"]
related: ["[[ADR-0028-Work-Has-Three-Phases]]", "[[ISS-0173-The-Suites-Own-Ids-Are-Written-In-A-Form-Nothing-Reads]]", "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"]
---

# Plan — FEAT-0102 Publication becomes a view

## Delivery sequence

1. **[[TASK-0426]] — the ladder as data.** One payload, every rung, every repo. **First**, because the view's whole claim is that it is never empty, and that is a property of the data across twelve repos rather than of a renderer. Provable before anything is drawn.
2. **[[TASK-0427]] — the view.** The nav mode over that payload, with `~history` re-homed inside it rather than replaced.
3. **[[TASK-0428]] — the release rung.** `REL-*` notes and tags, which nothing reads today. Independent of 4 and can land alone: three repos gain a rung, nine correctly show it unreached.
4. **[[TASK-0429]] — the gate as a campaign.** The acceptance suite attached to the release rung, one obligation when a release is `draft` and zero otherwise.

4 needs 3 — the gate hangs on a rung that must exist first. 2 needs 1. 3 needs 1 and can run beside 2.

## Dependencies

[[ADR-0028]] accepted. [[ISS-0173]] should land before 4: without it every blocking row resolves to zero refs, and the gate would be designed against a corpus where no row can name its subject.

[[FEAT-0101]] is **not** a hard dependency, but the two meet at [[TASK-0429]] — a test's subject gains a second kind (a release) once this lands, which is why [[TASK-0424]]'s predicate takes a subject rather than a feature.

## The measurements this feature stands on

Taken 2026-08-16 across all twelve discovered repos. They are claims about the world, and if they have drifted by the time this is built, the design is re-checked rather than the numbers re-stated:

- rung coverage: commit 12/12, push 8, deploy 2, versioned release 3
- live: 7 unpushed commits across 4 repos; your-applications.com 34 undeployed; your-trainer 11 `REL-*` + 12 tags
- your-trainer's gate: 60 unchecked Tier 1/2 in 17 sections, top two carrying 33
- `edankert.com` — deploy remote, no upstream, `ahead is None`: the rung is reachable and its count is unknown, which must render as a row and not a zero

## How this is verified

[[TST-0027]] walks the ladder across every discovered repo and asserts non-emptiness and correct degradation — the claim that cannot be made from fixtures. [[TST-0028]] asserts the gate names its number, contributes one obligation while a release is `draft` and none otherwise, and that no path from this view can push a deploy remote.

---

## Round four, 2026-08-16 — what the functionality review opened

Four features, ten tasks, and they split cleanly by **which page they change**. That split is the plan: Edwin's own words on the third round were that he could not relate the proposals to the current functionality, and the answer was to stop describing capabilities and start describing the two pages he opens.

### Page 1 — "Next release"

[[FEAT-0108]]. The gate stops being a census.

1. **[[TASK-0446]] — the suite at the last tag.** First, because everything else on this page is a diff against it, and because the degradation paths are most of the work: eleven of twelve repos have no tags at all.
2. **[[TASK-0447]] — the in-flight rule reaches acceptance rows.** Independent of 1 and can land alone; it is finishing [[ADR-0028]] decision 3, not a new rule. Smallest change with the largest effect on the number: 60 → 40.
3. **[[TASK-0448]] — a ticked row annotated `RE-RUN` is not evidence.** Independent. Puts the missing 53 on the page without deciding whether they block.
4. **[[TASK-0449]] — order the walk by setup cost.** Last, needs 1, and the least certain: its schema exists in exactly one note.

### Page 2 — a shipped release

[[FEAT-0109]] and [[FEAT-0110]]. Both are reads of notes the page already opens.

5. **[[TASK-0450]] — grade the evidence behind `tests_verified`.** Twenty lines. Stops a heading asserting something false.
6. **[[TASK-0451]] — a published artifact is checkable.** Four lines of stdlib XML. Catches two corrupt files today.
7. **[[TASK-0452]] → [[TASK-0453]] — the post-release checklist, read then verified.** The only work here with a consequence outside the documentation system.

### The marks

[[FEAT-0111]]. **[[TASK-0454]] → [[TASK-0455]]**, in that order — read and write the marks, then attach the verdict and the witness. Closes [[ISS-0181]] items 1 and 2 only.

### Order

2, 3, 5, 6 are independent and small; any can land first. 1 gates 4; 7 is a pair; the marks are a pair. **Nothing here depends on anything in rounds one to three** beyond what already shipped.

### The measurements this round stands on

Taken 2026-08-16 against `../your-trainer` and its twelve tags. Claims about the world — if they have drifted when this is built, the design is re-checked rather than the numbers restated:

- twelve tags, twelve blocked ships; 1 → 130 → 60, median 26
- today's 60 = 13 new · 47 chronic · 0 regressed; 20 of them quiet under [[ADR-0028]] decision 3
- 54 `RE-RUN` annotations, 53 still ticked — honest blocking number 113
- `last_verified == created` in 15 of 16 TST notes; REL-0012 → TST-0011 at 0/18 walked, 0 evidence
- 2 of 7 store artifacts do not parse; 8 release notes, 37 unticked post-release boxes
- 6 `[~]` and 1 `[F]` already in use, 22 witnesses in the v2.1.1 checklist

### How this round is verified

Against `../your-trainer`'s **real tags and real notes**, not only fixtures. The central claims are about twelve actual releases and a fixture cannot carry them; fixtures cover the degradation paths the live repo does not exhibit — no tags, no previous release, a section inserted above a check, a malformed artifact, a lazy-continuation task list.

Mutations are named in each task **now**, before the guards are written, because this phase has already had guards mutation-tested with mutations their author had in mind while writing them.
