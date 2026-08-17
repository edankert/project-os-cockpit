---
type: "[[decision]]"
id: ADR-0030
aliases: ["ADR-0030"]
title: "Acceptance checks are notes — type `check`, id `CHK-*` — and the check type sits deliberately outside the test gates"
status: proposed
owner: user:edwin
created: 2026-08-17
updated: "2026-08-17"
decision_date:
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
related: ["[[project-os-dev#ADR-0009]]", "[[project-os-dev#ADR-0010]]", "[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]", "[[ADR-0028-Work-Has-Three-Phases]]", "[[ADR-0029-The-Acceptance-Mark-Vocabulary-Is-Minimals]]", "[[FEAT-0112-The-Acceptance-Suite-Gets-A-Machine-Readable-Projection]]", "[[FEAT-0113-The-Check-Type-And-The-Migration]]", "[[ISS-0173-The-Suites-Own-Ids-Are-Written-In-A-Form-Nothing-Reads]]", "[[ISS-0178-A-Test-Cannot-Be-Retired]]", "[[ISS-0181-Four-Things-The-Release-Surface-Cannot-Do]]"]
supersedes: []
tags: [acceptance, conventions, schema]
---

# Acceptance checks are notes, and the check type sits deliberately outside the test gates

## Status

**Proposed.** Acceptance is Edwin's. Nothing in [[PHASE-035-Acceptance-Checks-Are-Notes]] migrates, scaffolds or writes a `CHK-*` note until this is `accepted` — the phase is documented in full so the decision is being made about something concrete.

## Context

The acceptance suite is one Markdown document per repo (`docs/tests/ACCEPTANCE_TESTS.md` — three exist in the fleet: `your-trainer` 579 rows, `your-sudoku` 56, this repo 34; 669 rows total). Everything the cockpit knows about a check is parsed out of row grammar: the mark, the verdict date and reason, the `RE-RUN (TASK-####: reason)` invalidation annotation (57 rows, hand-written), the automation annotation (201 rows), and the refs a section heading carries. It works — but the suite is the **one surface in this system where the stored artifact is the display**. Everywhere else the cockpit is a projection over note frontmatter; here the file is the thing on screen, which is why four rounds of marks-control work ([[ISS-0185]]..[[ISS-0189]]) were spent teaching a rendered document to behave like a control surface.

Edwin, 2026-08-17, deciding the direction after a three-round independent review: *"I want to consider the TST note approach to capture acceptance tests, some of the issues you highlighted can be fixed by providing tooling, i.e. we don't need to show the acceptance tests the way they are stored on disk probably the same for normal tests and having this granularity should allow us to build a lot more functionality around these TST notes."*

The review's honest tally of what granularity buys: **genuinely unlocked** — per-check evidence attachments, resolvable coverage queries (`covers:` through the index instead of a heading heuristic), burden tags (TASK-0449 was cancelled for exactly this absence); **improved but available without migrating** — per-check history (`git log -L` already delivers it today), dicing by any axis (the parser already yields every field), structured `tests_verified`; **one trap** — per-check obligations, which must stay forbidden (see decision 3).

## Decision

One note per acceptance check.

1. **Type `[[check]]`, id `CHK-*`, at `docs/tests/acceptance/CHK-####-Slug.md`.** The TST *format* is reused; the TST *type* is not — every gate that would collide is keyed on `note_type == "test"` or the `tests` snapshot collection, so a sibling type makes the collisions vanish by construction rather than by exemption logic. A new prefix rather than shared TST-* ids: sharing would push `your-trainer`'s TST counter from 18 to ~600 and make the id stop telling you what a thing is, in a corpus where ids appear in prose everywhere.
2. **`status:` holds lifecycle; `mark:` holds verdict.** `status:` is `draft` / `active` / `retired` — it moves rarely, `retired` is terminal (TESTING.md: *"never removed, only deprecated"*), and checks therefore do not inherit [[ISS-0178]]'s no-terminal-status gap. `mark:` is the six-valued verdict of [[ADR-0029]] (`" "`, `x`, `/`, `-`, `!`, `?`), with `verdict_date:` and `verdict_reason:` beside it, `invalidated_by:` as the structured RE-RUN triple (change id, reason, date), and `automation:` (`full`/`partial`/`manual` + `covered_by:`). **Ticking never touches `status:`.**
3. **Three exemptions, each deliberate — they are the risk this ADR exists to record:**
   - **[[project-os-dev#ADR-0010]]'s runner-only rule never engages.** It governs test *status* (`passing`/`failing`); a check's verdict is `mark:`, human-written by design. No change to that rule's statement — this ADR is the clarifying companion.
   - **Out of the obligation registry.** `obligations.py` declares `"check"` as owed-nothing, forced by the completeness test that asserts every type is declared. [[ADR-0027]] called acceptance rows *"the most self-re-arming population in the corpus"*; the reasoning is unchanged and now applies to 669 addressable subjects instead of 669 rows. The release gate stays one campaign row. The granularity's most tempting use — per-check badges — is the one this decision forbids.
   - **Out of the independent-review gate.** QUALITY.md gates `TST-*` reaching `passing`; a check is not a TST and never reaches `passing`. The review of a check is the walk.
4. **The document becomes a view.** The suite renders as a generated list — tier → area → rows in `ordinal` order, rules preamble as header, the same mark dialog — and `ACCEPTANCE_TESTS.md` is **deleted at migration**, not tombstoned: a left-behind file is the dual-source trap this project has paid for twice, and git holds it at every pre-migration ref. `section:`/`area:`/`ordinal:` order the view; ordinal is display-only and sparse, so mid-section inserts stop shifting anything — which retires the shifting section-ordinal address for good.
5. **The per-release snapshot suites never migrate.** `ACCEPTANCE_TESTS_v2.1.0.md`, `ACCEPTANCE_CHECKLIST_v2.1.1.md` and the run plans are frozen records of what past releases were measured against; rewriting them would falsify history. Two shapes split by *time*, never maintained in parallel. New releases freeze a structured check-set instead.
6. **Upstream first.** The `check` type touches template-owned surfaces — TAXONOMY.md, STATUSES.md, QUALITY.md, SCHEMAS.md, `validate-docs.py` — and every one lands in `~/Dev/repos/project-os` and syncs down before any `CHK-*` note exists in any repo. Nothing carries locally as permanent divergence: `sync-project-os.sh` reports divergence, and a permanent report is a nag that teaches people to ignore it.

## Consequences

**The inversion, in [[project-os-dev#ADR-0009]]'s own language:** notes are the authored source of state and the tool derives. Today the suite is the single place where the artifact is the display; after this, checks are authored notes like everything else and the suite is derived. A person in Obsidian opens `CHK-0412-First-Run.md` and sees frontmatter plus a procedure — the same shape as any note, editable, greppable.

**Residuals, stated without softening:** hand-editing moves from one file to one note per check, and a sweep's diff is N files rather than N lines; reading the suite end to end means the view, not a file. Blame does not cross the migration commit (~2% similarity, rename detection will not fire) — traceability is preserved **by the record** (`migrated_from:` carries the old `#section.ordinal` address and the pre-migration sha, and a check's page can stitch its note history to `git log -L` on the old path) rather than by git plumbing. `suite_at` carries a permanent two-shape branch: file-shape at refs before the cut (all twelve of `your-trainer`'s current tags), note-shape after — the note-shape read is two subprocesses (`git ls-tree -r` piped to `git cat-file --batch`), not N. The measured price of the whole programme is ~9.5 days against ~1 day for the projection alternative; Edwin accepted it knowingly and it is on the record rather than discovered in week two.

## Alternatives considered

- **Single file plus richer row grammar** — the review's own prior recommendation, with the finding that `git log -L` already delivers per-check history, so [[FEAT-0112]]'s named reversal condition (per-check history) was satisfied all along without migrating. Rejected here because the granularity buys what grammar cannot: evidence attachments, coverage resolvable through the index, burden as a field. The finding stands on the record; it is why the *unlock* tally above is honest about which benefits did not require this decision.
- **JSON** — [[FEAT-0112]], analysed 2026-08-17 and parked. Rejected for inverting the notes-are-the-source rule: a tool-owned file makes the tool mandatory to edit a check. The note form keeps the corpus authored and human-editable, which is precisely why it survives the objection JSON did not.
- **Reusing the TST type directly** — Edwin's first framing, rejected by measurement: five independent collisions (review gate on `passing`, runner-only statuses, three-valued status vocabulary against six marks, the Run obligation admitting the self-re-arming population, and upstream blast radius without a new type to carry the differences). The sibling type is the version of this idea that survives its own consequences.
