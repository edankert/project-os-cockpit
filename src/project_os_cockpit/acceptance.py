"""The acceptance-test suite and the release gate it makes possible (TASK-0373).

`tools/instructions/TESTING.md` has described Tier 1 / Tier 2 / Tier 3, the
re-run rule and *"a release is blocked while any Tier 1/Tier 2 test is
unchecked"* since the template was written. **No repo had ever instantiated
it.** Measured 2026-08-10 across the twelve the cockpit renders: 92 ``TST-*``
notes, zero tier classification, and a gate that had never been able to fire.

This module reads ``docs/tests/ACCEPTANCE_TESTS.md`` and answers two questions:
what the tiers hold, and what is blocking a release.

**Why parse a checklist rather than read frontmatter.** Tier is a property of a
*checkbox*, not of a note — Tier 1 is "one or more per feature" covering
user-visible behaviour, while a ``TST-*`` is usually one pytest module covering
an internal contract. TESTING.md is explicit that the two systems coexist. A
``tier:`` field on the notes would tier the wrong objects and leave the box the
gate actually reads with nowhere to live.

The format is the template's own, so nothing here invents a convention:

    # Tier 1 — Feature Tests
    ## 1.1 Some area ([[FEAT-0001]], [[FEAT-0002]])
    - [ ] **Name:** procedure and expected result.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, replace, field
from pathlib import Path
from typing import Any

#: Where the suite lives. TESTING.md names this path; it is not configurable,
#: for the same reason `SNAPSHOT.yaml` is not — a checklist the gate cannot
#: find is a gate that silently passes.
SUITE_REL = "tests/ACCEPTANCE_TESTS.md"

#: Where checks live once they are notes ([[ADR-0030]]). The sibling of
#: `SUITE_REL`, and **never both**: a repo that migrates deletes the file in
#: the migration commit, because a left-behind copy is the dual-source trap
#: this project has paid for twice. `load()` below reads whichever exists and
#: says which shape it found, so the two can coexist across the fleet — which
#: they must, since the repos migrate one at a time.
CHECKS_REL = "tests/acceptance"

#: Tiers that block a release. Tier 3 is a verification aid, not a requirement
#: — TESTING.md's release-gating section says so in as many words.
GATING_TIERS: tuple[int, ...] = (1, 2)

#: A `- [ ]` inside a code fence is an *example* of a checkbox, not one. Found
#: by re-review (ISS-0141): `criteria.py` and the validator's box counter both
#: skip fences deliberately and this module did not, so a documentation example
#: in the suite would have been a real, blocking, unwalkable gating item — and
#: the raw-line guard could not have seen it, because raw and parsed would both
#: have counted it. Same regex as `criteria.FENCE_RE`, restated rather than
#: imported to keep this module free of a dependency it otherwise has no use
#: for; `test_a_checkbox_inside_a_code_fence_is_an_example` pins the pair.
_FENCE_RE = re.compile(r"^\s*(```|~~~)")
_TIER_HEADING_RE = re.compile(r"^#\s+Tier\s+(\d)\s*[—-]\s*(.+?)\s*$", re.M)
_SECTION_RE = re.compile(r"^##\s+(\d+\.\d+)\s+(.*?)\s*$")
#: **Any** bullet, **any** mark, decided below rather than filtered here
#: (ISS-0141). The first version matched `^-\s+\[( |x|X)\]`, which gave the
#: parser a way to say nothing: `- [~]` — the record's own mark for a check
#: settled by decision — was dropped from the suite entirely, along with any
#: typo. A checklist that silently loses lines reports a fuller bar than the
#: document holds, and it feeds a release gate.
#:
#: **The first fix widened the mark and left the line shape alone**, which
#: independent review caught by pointing at ISS-0141's own list of examples:
#: `- [v]` and `- [-]` blocked afterwards, but `- [ x]` — two characters —
#: still vanished, as did an indented `  - [ ]` and a `* [ ]` bullet. Widening
#: one axis of a silent-drop bug leaves the bug. Both axes are open now, and
#: the mark is classified **without stripping**, so `[ x]` is an unrecognised
#: mark (owed, blocking) rather than a line that was never there.
#:
#: *This sentence said "classified after stripping" until the re-review caught
#: it — describing, in the first place a future cleanup reads, precisely the
#: inversion the code below refuses to make. `" x".strip()` is `"x"`, so a
#: parser written from that comment would read a typo as a walked check.*
_ITEM_RE = re.compile(r"^\s*[-*+]\s+\[([^\]]*)\]\s+(.*?)\s*$")
#: Walked. `X` is Markdown-legal and appears in the wild.
_CHECKED_MARKS = frozenset({"x", "X"})
#: Settled by a decision rather than by being walked — the check describes a
#: surface that was retired, or asks for a precondition that cannot be made.
#: It does not block; it is counted and named, which is the difference between
#: reconciling something and losing it.
#: `[/]` is Minimal's *incomplete*; `[~]` is the legacy alias, read forever and
#: never written. Every one of `../your-trainer`'s seven `~` rows says
#: *"Partial pass"*, which is why `~` aliases `/` and not `-` — an earlier
#: draft had it the other way and the rows corrected it (ADR-0029).
_RECONCILED_MARKS = frozenset({"/", "~"})
#: **Shipping anyway** (FEAT-0104). A check that is not done, on a release
#: somebody has decided to ship regardless. `TESTING.md` line 113 has always
#: allowed this — *"A test may be marked as a release exception if it cannot
#: be completed … Exceptions must be documented in the release note with
#: justification"* — and nothing has ever implemented it.
#:
#: Reported SEPARATELY from `~`, never folded into it. Both are non-blocking,
#: and there the resemblance stops: `~` is permanent and says the check no
#: longer applies; `!` is **per-release** and says the check still applies and
#: was not done. Conflating them would lose exactly the difference ISS-0141
#: exists to protect, and would make an exception look settled forever when it
#: expires with its release.
#: `[-]` is Minimal's *canceled*, and is where the release exception moved
#: (ADR-0029). The concept is unchanged — a check that will not be done and is
#: not holding the release — and it keeps its field and its separate count.
#: Only the character changed, from the `[!]` this project minted and which was
#: written in zero suites fleet-wide.
_EXCEPTED_MARKS = frozenset({"-"})
#: **Failed, and tracked** (TASK-0454). `../your-trainer`'s own suites use this
#: with a dated verdict and a linked issue — *"`[F]` … **FAILS 2026-06-07** —
#: collapse state is stored globally … Tracked as [[ISS-0285]]"*.
#:
#: It is named here **without** being added to any non-blocking set, because
#: the parser already reads an unrecognised mark as blocking and for a
#: failed-and-tracked check that is the right answer. Naming it changes only
#: what the surface can SAY — `failed`, rather than a shrug — and the mark's
#: effect on the gate is deliberately identical to what it was before.
#:
#: Recorded so nobody later reads `[F]`-is-blocking as a parser gap and
#: "fixes" it into a pass. A check that failed is not a check that passed.
#: `[!]` is Minimal's *important*; `[F]` is the legacy alias.
#:
#: **`[!]` REVERSES MEANING HERE** (ADR-0029). It was a release exception and
#: did not block; it is *failed* and does. Safe only because the mark is
#: written in zero suites across twelve repos, verified before the decision
#: rather than after — any `[!]` authored in the one day it meant the opposite
#: would silently begin blocking a release.
_FAILED_MARKS = frozenset({"!", "F"})
#: `[?]` is Minimal's *question* — the walker read the check and cannot tell
#: what it is asking. **Blocks**, and it is a third blocking mark that means a
#: third thing: `[ ]` nobody looked, `[!]` somebody looked and it broke, `[?]`
#: somebody looked and could not tell. Collapsing any pair loses the
#: distinction the vocabulary exists for.
_QUESTION_MARKS = frozenset({"?"})
#: A check that is ticked but whose evidence was invalidated by a later change.
#: `TESTING.md` rule 2 says a code change unchecks the tests it overlaps; the
#: practice in `../your-trainer` is softer — the tick stays and the row gains
#: `RE-RUN (TASK-0385: AddUserScreen replaced by inline dialog)`.
#:
#: **54 rows carry one and 53 are still ticked**, so the gate counts 53 rows as
#: passed on evidence their own line says is stale, and the honest blocking
#: number is 113 rather than 60 (TASK-0448).
#:
#: The parenthetical is REQUIRED by this pattern, which is what keeps the
#: suite's own `## Rules` line — *"After a verified release: Tier 3 tests are
#: removed, RE-RUN annotations are cleared"* — from being read as an
#: annotation. That line is also outside any tier heading, so it is skipped
#: twice over; belt and braces, because a rule that swept up its own
#: description would be silently self-referential.
_RERUN_RE = re.compile(r"\bRE-RUN\s*\(([^)]*)\)")
#: **Burden tags are deliberately not parsed here** (TASK-0449, resolved `[~]`).
#:
#: The plan was to order the gate's rows by what a walker needs at hand, using
#: the tags `../your-trainer`'s `TST-0013` puts on all 107 of its rows —
#: `[App]` 98, `[Trainer]` 21, `[Strava]` 8, `[icu]` 6, and so on. Two
#: measurements killed it, both taken before any of it shipped:
#:
#: 1. **`ACCEPTANCE_TESTS.md` carries none.** The document the gate actually
#:    reads has zero burden tags in every repo in the fleet. A scanner written
#:    for it found six, and **all six were false positives** — `[Debug]` from
#:    inside a quoted workout name, *"verify no workouts with `[Debug]` prefix
#:    appear"*. A 6-of-6 false-positive rate on the only corpus it would run
#:    against is not a heuristic that needs tuning; it is the wrong idea.
#: 2. **`TST-0013` is not a suite.** It has no `# Tier N` heading, so `parse`
#:    yields **0 items** for it. The one document carrying real tags is a
#:    `TST-*` read by `manual_test_steps`, which this module never sees.
#:
#: The task's own scope note said a heuristic inferring burden from prose was
#: out of scope because *"it would be wrong quietly"*. It would have been.
#:
#: The **purpose** — do not make someone stand a trainer up twice — is already
#: served: FEAT-0102 groups the gate by section, and section is the sitting.
_NAME_RE = re.compile(r"^\*\*(.+?):?\*\*:?\s*(.*)$")
_ID_RE = re.compile(r"\[\[([A-Z]+-[0-9A-Za-z-]+?)(?:\|[^\]]*)?\]\]")
#: Bare `FEAT-0104`, which is how every suite in the fleet actually writes it
#: (ISS-0173). Wikilink form was the only form read, and **not one heading in
#: `your-trainer`'s 1082-line suite uses it** — 72 of its 82 section headings
#: name a feature or issue and the parser found zero. Two things went wrong at
#: once: `missing_issue_refs` reported **158 of 158** Tier 2 items as
#: violating TESTING.md's rule (a check nothing consumed, which is why it went
#: unnoticed), and the row -> subject link a scoped gate needs did not exist as
#: far as any code could tell. The same shape as ISS-0162's 48 bare ADR
#: citations: the record said the right thing in a form the reader refused.
_BARE_ID_RE = re.compile(r"\b([A-Z]{2,6}-\d{3,4})\b")
#: **Only** the trailing parenthetical, so a heading mentioning an id in prose
#: — *"Handles TASK-0132-style imports"* — does not acquire a false subject.
#: Not a guess about where authors put them: measured across every suite in the
#: fleet on 2026-08-16, **114 of 114** id-bearing headings put all of theirs
#: here, and `area` below already strips exactly this span for the same reason.
_TRAILING_PAREN_RE = re.compile(r"\(([^()]*)\)\s*$")


def heading_refs(heading: str) -> tuple[str, ...]:
    """Project-os ids a section heading names, in document order.

    Wikilinked ids anywhere; bare ids in the trailing parenthetical only.
    """
    refs: list[str] = list(_ID_RE.findall(heading))
    tail = _TRAILING_PAREN_RE.search(heading)
    if tail:
        for note_id in _BARE_ID_RE.findall(tail.group(1)):
            if note_id not in refs:
                refs.append(note_id)
    return tuple(refs)


@dataclass(frozen=True)
class Invalidation:
    """`RE-RUN (TASK-####: reason)`, structured — TESTING.md rule 3 as a field.

    The annotation is the corpus's own invention, hand-written 54 times in
    `../your-trainer` and read by nothing until [[TASK-0448]]. Structuring it is
    half of what [[ADR-0030]] buys: `change` is resolvable through the index,
    `date` makes staleness arithmetic, and `raw` keeps the annotation's exact
    inner text so a migration can be proved lossless rather than assumed to be.

    **`raw` is not redundant with the other three.** 26 of the 54 annotations
    put the id somewhere the `ID: reason` shape does not describe, and a
    structured triple that silently dropped their wording would lose the only
    account of why a tick stopped being trustworthy.
    """

    change: str = ""
    reason: str = ""
    date: str = ""
    #: The annotation's inner text verbatim, exactly as `rerun` has always
    #: reported it. Every existing consumer reads this and is unaffected.
    raw: str = ""

    def __bool__(self) -> bool:
        return bool(self.raw or self.change or self.reason)


#: The empty invalidation, so `Item`'s default is one shared frozen instance
#: rather than a factory nobody would notice was being called 579 times.
_NOT_INVALIDATED = Invalidation()


@dataclass(frozen=True)
class Item:
    """One checkbox — the unit the gate reads.

    **Two storage shapes, one class** ([[ADR-0030]]): a row parsed out of
    `ACCEPTANCE_TESTS.md`, or a `CHK-*` note. Every consumer — the gate, the
    delta, the Tests view, the release page — reads this and cannot tell,
    which is what let the migration land without a second renderer. The
    note-shape fields below default to empty, so a file-shape item is exactly
    what it always was.
    """

    tier: int
    section: str          # "1.3"
    area: str             # "The navigator"
    name: str
    text: str
    #: Walked, with evidence on the line.
    checked: bool
    #: Settled by a decision instead (ISS-0141). Never both — a mark is one
    #: thing — and anything the parser cannot classify is neither, so it is
    #: owed and blocks. That is the direction that fails safely.
    reconciled: bool = False
    #: A release exception: not done, and shipping anyway (FEAT-0104).
    excepted: bool = False
    #: The check was read and is not understood (`[?]`). Blocking, and
    #: distinct from unwalked: somebody looked.
    question: bool = False
    #: Walked and failed, with the failure tracked on the line (TASK-0454).
    #: Blocking — `settled` deliberately does not consult this — and named so a
    #: surface can distinguish *"nobody has walked this"* from *"somebody
    #: walked it and it failed"*, which are the same colour today.
    failed: bool = False
    #: The invalidation, structured. `rerun` below is the string every existing
    #: caller already reads, kept as a property so the two cannot disagree —
    #: which they would within a week if both were fields set side by side.
    invalidated: Invalidation = _NOT_INVALIDATED
    #: The mark character exactly as the file writes it — `" "`, `"x"`, `"/"`,
    #: `"~"`, `"-"`, `"!"`, `"F"`, `"?"`, or whatever nobody recognises.
    #:
    #: The five booleans above are *classifications* of this, and they are
    #: lossy on purpose: `x` and `X` are one thing to the gate, and so are `/`
    #: and `~`. A surface that DRAWS the mark needs the character back, and
    #: until [[ISS-0190]] it could not have it — `parse` read the mark,
    #: derived five flags from it and dropped it on the floor.
    mark: str = " "
    #: 1-based position within its section, so every item has a unique number
    #: (`1.3.2`). Two items in one section otherwise share the section's id,
    #: and a navigator that keys rows on it would address the wrong one.
    ordinal: int = 1
    #: Project-os ids named by the section heading. Tier 1 sections name their
    #: features; Tier 2 sections name the `ISS-*` that created the test, which
    #: TESTING.md requires and `missing_issue_refs` enforces.
    refs: tuple[str, ...] = ()
    #: The section heading VERBATIM, so a link can slugify exactly what the
    #: renderer slugified (FEAT-0103). Reconstructing it from `section` and
    #: `area` does not work — `area` has the id parenthetical stripped and the
    #: rendered anchor keeps it, so the two differ by precisely the part that
    #: makes the link land.
    heading: str = ""

    # ----- note shape only (ADR-0030). Empty on a row parsed from a file. ---
    #: `CHK-0001`, so a surface can address the check itself rather than a
    #: position in a document. The whole point of the migration: `number` is an
    #: address that MOVES, and this one does not.
    note_id: str = ""
    #: The note's docs-relative path, so a row can open it.
    rel: str = ""
    #: `draft` / `active` / `retired` — the LIFECYCLE. Never the verdict.
    status: str = ""
    #: When the current `mark` was recorded, and why. `verdict_reason` is
    #: required for `/`, `-`, `!` and `?`; the write path refuses without one.
    verdict_date: str = ""
    verdict_reason: str = ""
    #: `full` / `partial` / `manual`, and what supplies the coverage. Rolled up
    #: as a release's *confidence*, which is why it is a check property and not
    #: — as first proposed — a feature stat.
    automation: str = ""
    covered_by: tuple[str, ...] = ()
    #: The status of each test named in `covered_by:`, resolved through the
    #: index when one is available. This is what makes automating a check PAY
    #: (ADR-0031 / REQ-0039): a `passing` covering test settles this one with no
    #: human mark. Empty when the suite was loaded without an index — a
    #: directory read cannot resolve an id — so `settled` falls back to the mark
    #: alone, which is the safe direction: it can only ever under-settle.
    covered_by_status: tuple[str, ...] = ()
    #: What the walker must have to hand. TASK-0449 was cancelled for the
    #: absence of exactly this field, on the finding that inferring it from
    #: prose was 6-of-6 false positives.
    burden: tuple[str, ...] = ()
    #: Paths, screenshots and log excerpts behind the current verdict.
    evidence: tuple[str, ...] = ()
    #: The pre-migration address (`#section.ordinal`) and the sha the file held
    #: at the cut. Blame does not cross the migration commit (~2% similarity),
    #: so traceability is preserved BY THE RECORD rather than by git plumbing.
    migrated_from: str = ""

    @property
    def rerun(self) -> str:
        """The invalidation annotation's inner text — what `rerun` always was.

        A property rather than a second field: the structured triple and the
        string are one fact, and two fields holding one fact is the shape this
        project keeps paying for.
        """
        return self.invalidated.raw

    @property
    def anchor(self) -> str:
        """The rendered heading's id, so a row can reach its own section.

        Slugified with **markdown's own** function rather than a lookalike.
        These anchors have existed since the suite was first rendered and
        nothing has ever used one; a link that is a single character off lands
        at the top of a 1082-line file, which is the behaviour it replaces.
        """
        from markdown.extensions.toc import slugify

        return slugify(self.heading, "-") if self.heading else ""

    @property
    def covered_by_passing(self) -> bool:
        """A machine already answers this check, and it currently passes.

        The whole return on ADR-0031. Before it, `automation:` and `covered_by:`
        were read by one facet and one release stat and by nothing that could
        discharge anything — so 15 of the 60 checks blocking `your-trainer` said
        in their own bodies that a test already covered them, and blocked the
        release anyway.

        **`passing`, not "not failing".** An unrun covering test settles
        nothing: `ready` means defined and never executed, which is exactly the
        state that must not clear a gate.
        """
        # **ALL, not ANY** — and the difference is a check that clears a gate
        # on partial evidence. Two covers, one passing and one failing, settled
        # under `any`, which contradicts the sentence every note about this
        # feature carries: *a failing covering test un-settles the check*.
        # Found by independent review, unguarded until now.
        #
        # An empty tuple is not coverage: `all([])` is True, so the emptiness
        # check comes first. That is the same fail-closed direction as the
        # missing-index case.
        return bool(self.covered_by_status) and all(
            s == "passing" for s in self.covered_by_status)

    @property
    def settled(self) -> bool:
        """What the gate reads — walked, reconciled, excepted, or **covered**.

        Not "done": a reconciled item was never performed and an excepted one
        is being shipped undone, and the tier counts say so separately.

        The fourth clause is ADR-0031's: a `passing` test named in
        `covered_by:` settles this check without a human mark. The direction is
        what keeps it safe — a machine's exit code discharges a person's
        checkbox, never the reverse — so ADR-0010's runner-only rule is
        untouched.

        **And a covering test that FAILS un-settles it**, because this reads the
        live status rather than a remembered one. That is a real consequence and
        it was decided rather than discovered: it puts a machine-driven
        population into the release gate, which is the gate and not a badge, so
        ADR-0027 is untouched too.
        """
        return (self.checked or self.reconciled or self.excepted
                or self.covered_by_passing)

    @property
    def stale(self) -> bool:
        """Ticked, but the record says the evidence no longer holds.

        Neither blocking nor satisfied — a third thing, and saying so is the
        point. An **unticked** annotated row is already blocking and must not
        be counted here as well, which is what the `checked` conjunct buys.

        **Dates refine this; they do not replace it** (TASK-0466). Once both
        `verdict_date` and `invalidated.date` are known, staleness is
        arithmetic: a pass recorded AFTER the invalidating change answers it,
        and the row stops being stale without anybody clearing an annotation by
        hand — which is TESTING.md rule 3's second half finally being
        performable. Where either date is missing the older rule stands, and
        that is not a fallback for tidiness: **not one** of the 54 annotations
        in the fleet carries a date, so keying staleness on dates alone would
        have reported zero stale rows the day the migration landed and called
        it an improvement.
        """
        if not (self.checked and self.invalidated):
            return False
        if self.verdict_date and self.invalidated.date:
            return self.verdict_date < self.invalidated.date
        return True

    @property
    def number(self) -> str:
        return f"{self.section}.{self.ordinal}"

    @property
    def key(self) -> str:
        return f"{self.number} {self.name}"


#: How a suite is stored. Three values because a surface has three different
#: things to say: `notes` is post-migration, `file` is pre-migration, and
#: `absent` is the state nine of the twelve fleet repos are in and must never
#: be reported as *"nothing blocking"*.
SHAPE_NOTES = "notes"
SHAPE_FILE = "file"
SHAPE_ABSENT = "absent"


@dataclass
class Suite:
    path: Path | None = None
    items: list[Item] = field(default_factory=list)
    #: Which storage answered. Carried rather than inferred from `path`: a
    #: caller that has to look at a filename to know whether it may write row
    #: grammar is a caller that will one day get it wrong.
    shape: str = SHAPE_ABSENT

    @property
    def exists(self) -> bool:
        return self.path is not None

    def tier(self, n: int) -> list[Item]:
        return [i for i in self.items if i.tier == n]

    def blocking(self) -> list[Item]:
        """Unsettled Tier 1/2 items — what stops a release.

        `settled`, not `checked`: a reconciled item is a decision the release
        note carries, and blocking on it would make the mark meaningless. An
        item with a mark nobody recognises is neither, so it lands here.
        """
        return [i for i in self.items if i.tier in GATING_TIERS and not i.settled]

    def missing_issue_refs(self) -> list[Item]:
        """Tier 2 items whose section names no ``ISS-*``.

        TESTING.md: *"Each references the `ISS-*` that created it."* A
        regression test that cannot say what it regressed against is a Tier 1
        test filed in the wrong place.
        """
        return [
            i for i in self.tier(2)
            if not any(r.startswith("ISS-") for r in i.refs)
        ]


def _split_frontmatter(text: str) -> str:
    if not text.startswith("---"):
        return text
    parts = text.split("---", 2)
    return parts[2] if len(parts) == 3 else text


def parse(text: str) -> list[Item]:
    """Items in document order. Anything outside a tier heading is ignored —
    the template's own preamble is prose, and the Rules section is a numbered
    list that must not be mistaken for tests."""
    body = _split_frontmatter(text)
    items: list[Item] = []
    tier = 0
    section = ""
    area = ""
    full_heading = ""
    refs: tuple[str, ...] = ()
    ordinal = 0

    in_fence = False
    for line in body.splitlines():
        if _FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        tier_head = _TIER_HEADING_RE.match(line)
        if tier_head:
            tier = int(tier_head.group(1))
            section, area, refs = "", "", ()
            continue
        sect = _SECTION_RE.match(line)
        if sect:
            section = sect.group(1)
            ordinal = 0
            heading = sect.group(2)
            refs = heading_refs(heading)
            # The heading minus its id list — "The navigator ([[FEAT-0010]], …)"
            area = re.sub(r"\s*\((?:[^()]*)\)\s*$", "", heading).strip()
            full_heading = f"{section} {heading}".strip()
            continue
        if tier == 0:
            continue
        item = _ITEM_RE.match(line)
        if not item:
            continue
        # NOT stripped before comparing: `[ ]` and `[]` are both the plain
        # unchecked box, but `[ x]` is a two-character mark nobody recognises,
        # and stripping it into `x` would silently promote a typo to a walked
        # check — the failure this whole regex exists to stop, inverted.
        mark = item.group(1)
        rest = item.group(2)
        named = _NAME_RE.match(rest)
        name, detail = (named.group(1), named.group(2)) if named else (rest, "")
        detail = detail.strip()
        rerun = _RERUN_RE.search(detail)
        ordinal += 1
        items.append(Item(
            tier=tier, section=section, area=area,
            name=name.strip(), text=detail,
            checked=mark in _CHECKED_MARKS,
            reconciled=mark in _RECONCILED_MARKS,
            excepted=mark in _EXCEPTED_MARKS,
            failed=mark in _FAILED_MARKS,
            question=mark in _QUESTION_MARKS,
            invalidated=split_rerun(rerun.group(1)) if rerun else _NOT_INVALIDATED,
            mark=mark,
            refs=refs, ordinal=ordinal, heading=full_heading,
        ))
    return items


#: `TASK-0385: AddUserScreen replaced by inline dialog` — the shape 28 of the
#: fleet's 54 annotations use. The other 26 do not, and this deliberately does
#: not try harder: `raw` keeps every one of them verbatim, so the id is
#: extracted where it is unambiguous and nothing is invented where it is not.
_RERUN_SPLIT_RE = re.compile(r"^\s*([A-Z]{2,6}-\d{3,4})\s*[:—-]\s*(.*)$", re.S)


def split_rerun(raw: str) -> Invalidation:
    """One `RE-RUN (…)` annotation, structured as far as it honestly goes."""
    text = (raw or "").strip()
    found = _RERUN_SPLIT_RE.match(text)
    if found:
        return Invalidation(
            change=found.group(1), reason=found.group(2).strip(), raw=text)
    # No id, or one written in a shape this does not describe. The annotation
    # survives whole; what is not claimed is the structure.
    bare = _BARE_ID_RE.search(text)
    return Invalidation(change=bare.group(1) if bare else "", reason=text, raw=text)


# ----- the note shape (ADR-0030 / FEAT-0113) --------------------------------
#
# The inversion, in ADR-0009's own language: notes are the authored source of
# state and the tool derives. Until this, the acceptance suite was the one
# surface in the system where the stored artifact WAS the display — which is
# why four rounds of marks-control work (ISS-0185..0189) were spent teaching a
# rendered document to behave like a control surface.
#
# Everything below produces the same `Item` the row parser produces. That is
# the whole migration strategy: one model, two readers, and no consumer that
# has to know which one answered.


def _as_tuple(raw: Any) -> tuple[str, ...]:
    """A frontmatter list as strings, tolerating the scalar form authors write."""
    if raw is None or raw == "":
        return ()
    if isinstance(raw, (list, tuple)):
        return tuple(str(x).strip() for x in raw if str(x).strip())
    return (str(raw).strip(),)


def _wikilink_ids(values: tuple[str, ...]) -> tuple[str, ...]:
    """Ids out of `covers:`, in either the `[[FEAT-0001]]` or bare form.

    Both, because the corpus writes both — ISS-0173 is the whole record of what
    reading only one of them costs: 72 of 82 headings named a feature and the
    parser found zero.
    """
    out: list[str] = []
    for value in values:
        for note_id in _ID_RE.findall(value) or _BARE_ID_RE.findall(value):
            if note_id not in out:
                out.append(note_id)
    return tuple(out)


def check_prose(body: str) -> str:
    """A check note's own words — its body with the `# Title` heading removed.

    The prose lives in the BODY, not in frontmatter, and that is the whole
    reason this type is worth having: a person opens `CHK-0412-First-Run.md` in
    Obsidian and reads a sentence, then a procedure. A 2,000-character `text:`
    field would have been the JSON objection ([[FEAT-0112]]) arriving through
    the back door — machine-shaped storage a human cannot comfortably edit.
    """
    lines = (body or "").strip().splitlines()
    if lines and lines[0].lstrip().startswith("# "):
        lines = lines[1:]
    return "\n".join(lines).strip()


def item_from_note(
    frontmatter: dict[str, Any], *, rel: str = "", body: str = "",
) -> Item | None:
    """One `CHK-*` note as an `Item`, or `None` if it is not one.

    Returns `None` only for a note that is not a check at all. A malformed
    check is **not** dropped: it lands in Tier 1 and blocks.

    That is the same direction the row parser fails in — *"anything the parser
    cannot classify is neither, so it is owed and blocks"* — and getting it
    wrong here is worse than there, because a whole note is at stake rather
    than one character. The first cut returned `None` on an unreadable tier
    under a comment claiming that dropping it kept the gate honest. It does
    not: a dropped check and a Tier 3 check both fail to block, so both let a
    release through on a check nobody can read. **A mutation setting the
    fallback to Tier 3 survived the suite**, which is how the reasoning came to
    be checked rather than admired.
    """
    fm = frontmatter or {}
    if not str(fm.get("id", "") or "").strip():
        return None
    try:
        tier = int(str(fm.get("tier", "")).strip() or 0)
    except (TypeError, ValueError):
        tier = 0
    if tier not in (1, 2, 3):
        tier = 1
    mark = str(fm.get("mark", " ") or " ")
    # A YAML scalar cannot hold a bare space, so `mark: " "` round-trips as the
    # empty string through some writers. Both mean unwalked; nothing else is
    # normalised, because `[ x]` staying unrecognised is the point of the
    # row parser's own refusal to strip (ISS-0141).
    if mark == "":
        mark = " "
    raw_invalid = fm.get("invalidated_by") or {}
    if isinstance(raw_invalid, dict):
        invalid = Invalidation(
            change=str(raw_invalid.get("change", "") or "").strip(),
            reason=str(raw_invalid.get("reason", "") or "").strip(),
            date=str(raw_invalid.get("date", "") or "").strip(),
            raw=str(raw_invalid.get("raw", "") or "").strip(),
        )
        if invalid.change and not invalid.raw:
            invalid = Invalidation(
                invalid.change, invalid.reason, invalid.date,
                f"{invalid.change}: {invalid.reason}" if invalid.reason
                else invalid.change,
            )
        elif invalid.reason and not invalid.raw:
            invalid = Invalidation(
                invalid.change, invalid.reason, invalid.date, invalid.reason)
    else:
        invalid = split_rerun(str(raw_invalid))
    section = str(fm.get("section", "") or "").strip()
    try:
        ordinal = int(str(fm.get("ordinal", "") or 0))
    except (TypeError, ValueError):
        ordinal = 0
    return Item(
        tier=tier,
        section=section,
        area=str(fm.get("area", "") or "").strip(),
        name=str(fm.get("title", "") or "").strip(),
        text=check_prose(body) or str(fm.get("text", "") or "").strip(),
        checked=mark in _CHECKED_MARKS,
        reconciled=mark in _RECONCILED_MARKS,
        excepted=mark in _EXCEPTED_MARKS,
        failed=mark in _FAILED_MARKS,
        question=mark in _QUESTION_MARKS,
        invalidated=invalid,
        mark=mark,
        ordinal=ordinal,
        refs=_wikilink_ids(_as_tuple(fm.get("covers"))),
        heading=f"{section} {fm.get('area', '')}".strip(),
        note_id=str(fm.get("id", "") or "").strip(),
        rel=rel,
        status=str(fm.get("status", "") or "").strip(),
        verdict_date=str(fm.get("verdict_date", "") or "").strip(),
        verdict_reason=str(fm.get("verdict_reason", "") or "").strip(),
        automation=str(fm.get("automation", "") or "").strip(),
        covered_by=_as_tuple(fm.get("covered_by")),
        burden=_as_tuple(fm.get("burden")),
        evidence=_as_tuple(fm.get("evidence")),
        migrated_from=str(fm.get("migrated_from", "") or "").strip(),
    )


def _section_key(section: str) -> tuple[int, ...]:
    """`"1.12"` sorts after `"1.2"`. String order does not, and the suite has
    fourteen sections in tier 1 alone."""
    out: list[int] = []
    for part in (section or "").split("."):
        try:
            out.append(int(part))
        except ValueError:
            out.append(0)
    return tuple(out)


def sort_items(items: list[Item]) -> list[Item]:
    """Suite order: tier, then section, then `ordinal`, then id.

    `ordinal` is sparse and display-only, which is what retires the shifting
    section-ordinal address for good — an insert between two checks takes a
    number between theirs and moves nothing. `note_id` breaks the tie so the
    order is total, because a view that reorders itself between renders is a
    view a reader cannot walk.
    """
    return sorted(items, key=lambda i: (
        i.tier, _section_key(i.section), i.ordinal, i.note_id))


def load_notes(checks_dir: Path) -> list[Item]:
    """Every acceptance note under ``checks_dir``, in suite order.

    `TST-*` since ADR-0031, `CHK-*` in a repo that has not run the merge
    migration. Never both: the migration renames in place, so a directory
    holding one shape has finished and a directory holding the other has not
    started.

    Reads the directory directly rather than through the index, so the
    migration script and the tests can use it without building one. Live
    surfaces pass an `Index` to :func:`load` instead — 579 YAML parses per page
    render is not a thing to do twice.
    """
    import frontmatter as _fm

    items: list[Item] = []
    paths = sorted(checks_dir.glob("TST-*.md")) or sorted(checks_dir.glob("CHK-*.md"))
    for path in paths:
        try:
            post = _fm.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError, UnicodeDecodeError):
            continue
        item = item_from_note(dict(post.metadata), body=post.content,
                              rel=f"{CHECKS_REL}/{path.name}")
        if item is not None:
            items.append(item)
    return sort_items(items)



def _resolve_coverage(items: "list[Item]", index: "Any") -> "list[Item]":
    """Fill `covered_by_status` from the index (REQ-0039).

    Resolved at LOAD rather than stored on the note, and that is the whole
    design: a remembered status is a claim about a run that happened once, and
    what the gate needs to know is whether the covering test passes **now**. It
    is also why a failing covering test un-settles the check it covers -- the
    same read, in the other direction.

    Only an index can do this, so a directory read leaves the tuple empty and
    `settled` falls back to the mark alone. That direction is deliberate: it can
    only ever under-settle, which fails a gate closed rather than open.
    """
    out: list[Item] = []
    for item in items:
        if not item.covered_by:
            out.append(item)
            continue
        statuses: list[str] = []
        for ref in item.covered_by:
            # `[[TST-0016-Seat-Resolution]]`, `TST-0016`, or a bare module name.
            # Only the id form resolves; anything else is a claim the gate
            # cannot check, which is why the write path refuses it.
            match = re.search(r"([A-Z]+-\d{2,})", str(ref))
            path = index.by_id(match.group(1)) if match else None
            record = index.get(path) if path is not None else None
            # **Only an EXECUTABLE test counts as coverage.** A manual test at
            # `passing` is a person's own walk, so accepting it would let one
            # hand-walked note discharge another -- a walk laundered into
            # automation, which is the opposite of what REQ-0039 buys. The
            # covering test must declare a `command:`, which is the same bar
            # the write path is required to enforce (TASK-0483).
            status = ""
            if record is not None:
                if str(record.frontmatter.get("command") or "").strip():
                    status = str(record.status or "").strip().lower()
                else:
                    status = "not-executable"
            statuses.append(status)
        out.append(replace(item, covered_by_status=tuple(statuses)))
    return out


def load(docs_root: Path, index: "Any | None" = None) -> Suite:
    """The suite, or an empty one when the repo has never instantiated it.

    **Absent is not passing.** A repo with no suite has no Tier 1/2 items, so
    `blocking()` is empty and the gate would report "clear" — which is exactly
    the state every repo was in before this existed, and exactly the state that
    made the gate look like it worked. `gate_payload` reports `exists` so a
    surface can say "never instantiated" instead of "nothing blocking".

    **Notes win where both exist.** They should never both exist — the
    migration deletes the file in its own commit — but if a stray copy is ever
    restored, reading the notes is the answer that matches every write path.
    The alternative would be a surface that displays one store and writes the
    other.
    """
    checks_dir = docs_root / CHECKS_REL
    if index is not None:
        # ADR-0031: an acceptance check is a `[[test]]` at `level: acceptance`.
        # The retired `check` type is still read, because eight of the twelve
        # repos this cockpit renders are upstream-behind and a repo that has
        # not run the merge migration must keep its suite rather than losing
        # it silently -- which is what reading only the new shape would do.
        records = [
            r for r in index.notes_by_type("test")
            if str(r.frontmatter.get("level", "") or "").strip().lower() == "acceptance"
        ] or list(index.notes_by_type("check"))
        items = [
            item for record in records
            if (item := item_from_note(record.frontmatter, body=record.body,
                                       rel=record.rel_path))
            is not None
        ]
        if items:
            items = _resolve_coverage(items, index)
            return Suite(path=checks_dir, items=sort_items(items),
                         shape=SHAPE_NOTES)
    elif checks_dir.is_dir():
        items = load_notes(checks_dir)
        if items:
            return Suite(path=checks_dir, items=items, shape=SHAPE_NOTES)
    path = docs_root / SUITE_REL
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return Suite()
    return Suite(path=path, items=parse(text), shape=SHAPE_FILE)


# ----- the gate as a delta (FEAT-0108 / TASK-0446) --------------------------
#
# The gate has reported one number since it shipped, and against `your-trainer`
# that number has been *"a release is blocked"* at **all twelve tags**: 1, 15,
# 85, 130, 22, 47, 47, 47, and 60 at HEAD. It is the steady state, not news,
# and today's 60 is not even elevated — v1.1.55 shipped at 130.
#
# A sentence that has been true and ignored twelve times is one the reader has
# learned to skip. What has never been said is which of the sixty arrived since
# the last release, and that is a number a person can act on today.
#
# The baseline needs no new storage: `git show <tag>:docs/tests/…` reconstructs
# the suite exactly as it stood, and `parse` reads it unchanged.


#: Diffed on `Item.name` within tier, never on `Item.number`. Numbers shift
#: when a section is inserted above — the same asymmetry `locate()` relies on,
#: pointing the other way: there it makes a stale address FAIL rather than
#: resolve to the wrong row; here it would make an unchanged row look new.
def _delta_key(item: "Item") -> tuple[int, str]:
    return (item.tier, item.name.strip().casefold())


#: One `git show` + parse per (repo, ref), for the life of the process. A tag's
#: content does not change, and the alternative is 12 subprocesses and 12
#: parses of a 1082-line file **per page render** — the gate is on a page
#: somebody clicks repeatedly. A moved tag goes stale here until restart, which
#: is the right trade for a ref that is by convention immutable.
_at_ref: dict[tuple[str, str], "Suite | None"] = {}


def suite_at(project_root: Path, ref: str, rel: str = SUITE_REL) -> Suite | None:
    """The suite as it stood at ``ref``, or ``None`` if it cannot be read.

    ``None`` is a real answer and is distinct from an empty suite: a tag from
    before the file existed, a ref that does not resolve, and a file that is
    present but empty are three different situations, and only the last one
    means *"the suite had no items then"*.

    **Two shapes, split by TIME rather than maintained in parallel**
    (TASK-0462). Every ref before a repo's migration commit holds the file —
    that is all twelve of `../your-trainer`'s current tags, so the delta at
    every historical tag is computed by exactly the code that always computed
    it. Refs after the cut hold notes, and are read with **two** subprocesses
    rather than N: `git ls-tree` for the paths, `git cat-file --batch` for
    their contents in one stream. The branch is permanent and that is not a
    defect — a tag is immutable, so the shape a tag holds is a fact about the
    past that will never stop being true.
    """
    cache_key = (str(project_root), f"{ref}:{rel}")
    if cache_key in _at_ref:
        return _at_ref[cache_key]
    out = _suite_at_uncached(project_root, ref, rel)
    _at_ref[cache_key] = out
    return out


def _suite_at_uncached(project_root: Path, ref: str, rel: str) -> Suite | None:
    from .git_state import _git_raw

    text = _git_raw(project_root, "show", f"{ref}:docs/{rel}")
    if text is not None:
        return Suite(path=None, items=parse(text), shape=SHAPE_FILE)
    if rel != SUITE_REL:
        # An explicit non-default path was asked for and is not there. Answering
        # with the note shape would be answering a different question.
        return None
    items = _notes_at(project_root, ref)
    if items is None:
        return None
    return Suite(path=None, items=items, shape=SHAPE_NOTES)


def _notes_at(project_root: Path, ref: str) -> list[Item] | None:
    """Every `CHK-*` note at ``ref``, or ``None`` when the directory is absent.

    Two subprocesses regardless of how many checks there are. `ls-tree` names
    the blobs; `cat-file --batch` streams all of them through one pipe, which
    is the difference between 2 processes and 579 at every tag on a cold delta.
    """
    import subprocess

    from .git_state import _git_raw

    listing = _git_raw(project_root, "ls-tree", "-r", "-z", ref, f"docs/{CHECKS_REL}/")
    if not listing:
        return None
    shas: list[str] = []
    for entry in listing.split("\0"):
        if not entry.strip():
            continue
        # `<mode> <type> <sha>\t<path>`
        meta, _, path = entry.partition("\t")
        parts = meta.split()
        if len(parts) < 3 or parts[1] != "blob":
            continue
        if not path.rsplit("/", 1)[-1].startswith("CHK-") or not path.endswith(".md"):
            continue
        shas.append(parts[2])
    if not shas:
        return None
    try:
        done = subprocess.run(
            ["git", "cat-file", "--batch"],
            cwd=str(project_root), input=("\n".join(shas) + "\n").encode(),
            capture_output=True, timeout=30, check=False,
        )
    except (OSError, subprocess.SubprocessError):     # pragma: no cover
        return None
    if done.returncode != 0:
        return None                                  # pragma: no cover
    items: list[Item] = []
    for blob in _split_batch(done.stdout):
        item = _item_from_note_text(blob)
        if item is not None:
            items.append(item)
    return sort_items(items) if items else None


def _split_batch(stream: bytes) -> list[str]:
    """`git cat-file --batch` output as a list of blob bodies.

    The format is `<sha> <type> <size>\\n<contents>\\n` per object, and the
    **size is authoritative** — a note whose body happens to contain a line
    looking like a header would otherwise split an object in two, and half a
    frontmatter block parses as a check with no tier.

    **`size` is in BYTES, so this walks bytes.** The first version took the
    same slices out of a *decoded string*, which is the same thing only for
    pure ASCII. Measured on `../your-trainer` the hour it migrated: 503,860
    bytes of notes decoding to 501,153 characters, so the walk drifted by one
    position per non-ASCII byte — em-dashes, `✅`, the arrows in the prose —
    reached a header it could not parse, and stopped. It returned **314 of
    579 checks, with no error**, and the gate at every post-migration ref
    would have read 20 blocking where the truth is 60: the direction that
    lets a release through.

    The docstring above was already right and the code did not follow it.
    Found by measuring the delta at real tags, not by reading it.
    """
    out: list[str] = []
    pos = 0
    while pos < len(stream):
        newline = stream.find(b"\n", pos)
        if newline == -1:
            break
        header = stream[pos:newline].split()
        if len(header) != 3 or not header[2].isdigit():
            break                                    # pragma: no cover
        size = int(header[2])
        start = newline + 1
        out.append(stream[start:start + size].decode("utf-8", "replace"))
        pos = start + size + 1                       # the trailing newline
    return out


def _item_from_note_text(text: str) -> Item | None:
    import frontmatter as _fm

    try:
        post = _fm.loads(text)
    except (ValueError, UnicodeDecodeError):         # pragma: no cover
        return None
    return item_from_note(dict(post.metadata), body=post.content)


def ages(
    project_root: Path, items: list["Item"], tags: list[str],
) -> dict[str, str]:
    """For each chronic row, the oldest tag at which it was already unsettled.

    ``tags`` oldest-first. The answer is *"this has been open since here"*,
    which is what turns 47 into *"25 since v2.0.5, 14 since v2.0.0, one since
    v1.1.0"* — the difference between a backlog and a five-month-old one.

    A row absent from every tag gets no entry rather than a wrong one. Rows are
    keyed by `Item.key`, so the caller can look one up without re-diffing.
    """
    if not tags:
        return {}
    snapshots: list[tuple[str, set[tuple[int, str]]]] = []
    for tag in tags:
        suite = suite_at(project_root, tag)
        if suite is None:
            continue
        snapshots.append((tag, {
            _delta_key(i) for i in suite.items
            if i.tier in GATING_TIERS and not i.settled
        }))
    out: dict[str, str] = {}
    for item in items:
        key = _delta_key(item)
        for tag, unsettled in snapshots:     # oldest first — first hit wins
            if key in unsettled:
                out[item.key] = tag
                break
    return out


def delta(current: Suite, baseline: Suite | None) -> dict[str, Any]:
    """Today's blocking rows split into new / chronic / regressed.

    ``baseline`` of ``None`` — no tags, no previous release, the file absent at
    the tag — yields every blocking row as ``chronic`` with ``comparable``
    false, so a caller renders the census it rendered before rather than
    claiming everything is new. **That is the common case**: eleven of the
    twelve repos the cockpit discovers have no release tags at all.
    """
    blocking = current.blocking()
    if baseline is None:
        return {
            "comparable": False,
            "new": [], "chronic": list(blocking), "regressed": [],
        }
    was_settled = {
        _delta_key(i) for i in baseline.items
        if i.tier in GATING_TIERS and i.settled
    }
    was_present = {
        _delta_key(i) for i in baseline.items if i.tier in GATING_TIERS
    }
    new, chronic, regressed = [], [], []
    for item in blocking:
        key = _delta_key(item)
        if key not in was_present:
            new.append(item)
        elif key in was_settled:
            regressed.append(item)
        else:
            chronic.append(item)
    return {
        "comparable": True,
        "new": new, "chronic": chronic, "regressed": regressed,
    }


def suite_rel(suite: Suite) -> str:
    """What a surface should open to SEE this suite.

    The file, when the file is the suite. The generated view, when the notes
    are — because in note shape there is no document to open, and a link to a
    directory is a 404 dressed as a row.
    """
    if not suite.exists:
        return ""
    return CHECKS_REL if suite.shape == SHAPE_NOTES else SUITE_REL


#: How each tier reads on the view. The template's own words; TESTING.md is the
#: contract and this must not paraphrase it into a second one.
TIER_LABELS: dict[int, str] = {
    1: "Tier 1 — feature tests",
    2: "Tier 2 — regression tests",
    3: "Tier 3 — verification tests",
}


def view_payload(docs_root: Path, index: "Any | None" = None) -> dict[str, Any]:
    """The suite as a **list somebody walks** (FEAT-0114 / TASK-0464).

    Edwin's contract, verbatim: *"We can then present them still as the same
    list with the same tick options for me to go through before a release."* So
    the shape is the shape a reader already knows — tier, then area, then rows
    in order — and the marks are the same six.

    What changes is where it comes from. The document was the display, which is
    why four rounds of work (ISS-0185..0189) went into teaching a rendered
    Markdown file to behave like a control surface. This is a projection over
    frontmatter, like every other view in the cockpit.

    **The facets are derived, never authored.** Every filter here is a field —
    mark, tier, area, `covers:`, `automation:` — which is the concrete thing
    the migration bought: the old suite could only be filtered by whatever a
    section heading happened to say, and `missing_issue_refs` reported 158 of
    158 because it could not read the form the headings were written in.
    """
    suite = load(docs_root, index)
    tiers: list[dict[str, Any]] = []
    for n in (1, 2, 3):
        items = suite.tier(n)
        if not items:
            continue
        areas: list[dict[str, Any]] = []
        for item in items:
            key = (item.section, item.area)
            if not areas or (areas[-1]["section"], areas[-1]["area"]) != key:
                areas.append({
                    "section": item.section, "area": item.area,
                    "refs": list(item.refs), "items": [],
                })
            areas[-1]["items"].append(_row(item))
        tiers.append({
            "tier": n,
            "label": TIER_LABELS.get(n, f"Tier {n}"),
            "gating": n in GATING_TIERS,
            "total": len(items),
            "checked": sum(1 for i in items if i.checked),
            "reconciled": sum(1 for i in items if i.reconciled),
            "excepted": sum(1 for i in items if i.excepted),
            "unsettled": sum(1 for i in items if not i.settled),
            "stale": sum(1 for i in items if i.stale),
            "areas": areas,
        })
    return {
        "exists": suite.exists,
        "shape": suite.shape,
        "rel": suite_rel(suite),
        # The rules preamble, as a row rather than as re-rendered prose: the
        # README holds it verbatim and is one click away. Re-rendering it into
        # the header would make this view a second publisher of the document's
        # own words, which is the drift the migration exists to remove.
        "readme": (f"{CHECKS_REL}/README.md"
                   if suite.shape == SHAPE_NOTES else suite_rel(suite)),
        "tiers": tiers,
        "facets": _facets(suite),
        "blocking": len(suite.blocking()),
        "total": len(suite.items),
        "settled": sum(1 for i in suite.items if i.settled),
    }


def _facets(suite: Suite) -> dict[str, list[dict[str, Any]]]:
    """Every filter the view offers, with its count, derived from the fields.

    A facet with a zero count is omitted rather than shown greyed: a filter
    that can only ever return nothing is a control that wastes a click, and on
    a 579-row suite there would be a dozen of them.
    """
    def tally(values: "list[tuple[str, str]]") -> list[dict[str, Any]]:
        counts: dict[tuple[str, str], int] = {}
        for value in values:
            counts[value] = counts.get(value, 0) + 1
        return [
            {"value": value, "label": label, "count": count}
            for (value, label), count in sorted(
                counts.items(), key=lambda kv: (-kv[1], kv[0][1]))
        ]

    marks: list[tuple[str, str]] = []
    for item in suite.items:
        marks.append((item.mark, MARK_MEANING.get(item.mark, "unrecognised")))
    return {
        "marks": tally(marks),
        "tiers": tally([(str(i.tier), TIER_LABELS.get(i.tier, f"Tier {i.tier}"))
                        for i in suite.items]),
        "areas": tally([(i.area, i.area) for i in suite.items if i.area]),
        "covers": tally([(ref, ref) for i in suite.items for ref in i.refs]),
        "automation": tally([(i.automation, i.automation)
                             for i in suite.items if i.automation]),
    }


#: What each mark MEANS, in one word a filter chip can carry. The table in the
#: module docstring above is the long form; this is the label, and the two are
#: kept beside each other deliberately — a vocabulary explained in one place
#: and displayed from another is how `[!]` came to mean two things.
MARK_MEANING: dict[str, str] = {
    " ": "unwalked", "x": "passed", "X": "passed",
    "/": "partial", "~": "partial", "-": "canceled",
    "!": "failed", "F": "failed", "?": "unclear",
}


def payload(docs_root: Path, index: "Any | None" = None) -> dict[str, Any]:
    """The suite as data, for the Tests view's tier groups."""
    suite = load(docs_root, index)
    return {
        "exists": suite.exists,
        "shape": suite.shape,
        "rel": suite_rel(suite),
        "tiers": [
            {
                "tier": n,
                "total": len(suite.tier(n)),
                "checked": sum(1 for i in suite.tier(n) if i.checked),
                # Reported beside `checked` rather than folded into it: the two
                # are different claims, and a suite that showed 27/27 for 26
                # walked and 1 reconciled would be the drop this replaced,
                # rounded up instead of down (ISS-0141).
                "reconciled": sum(1 for i in suite.tier(n) if i.reconciled),
                "excepted": sum(1 for i in suite.tier(n) if i.excepted),
                "gating": n in GATING_TIERS,
                "items": [
                    {
                        "key": i.key, "number": i.number,
                        "section": i.section, "area": i.area,
                        "name": i.name, "text": i.text, "checked": i.checked,
                        "reconciled": i.reconciled,
                        "excepted": i.excepted,
                        "refs": list(i.refs),
                        # The note's own id and path, so a row can BE the
                        # check rather than a position in a document. Empty in
                        # file shape, which is how a caller tells which
                        # address it may trust.
                        "id": i.note_id, "rel": i.rel,
                        "mark": i.mark, "automation": i.automation,
                        "stale": i.stale,
                    }
                    for i in suite.tier(n)
                ],
            }
            for n in (1, 2, 3)
        ],
    }


def _releases_since(tag: str, tags: list[str]) -> int:
    """How many tags were cut after ``tag``. ``tags`` oldest-first.

    ``0`` when the tag is unknown — never a guess, and never the total, which
    would report a row nobody can date as the oldest debt in the project.
    """
    if not tag or tag not in tags:
        return 0
    return len(tags) - tags.index(tag) - 1


def _summary(tags: list[str], suites: dict[str, int], today: int) -> str:
    """The one line that lets a reader judge whether today is unusual.

    *"Twelve releases, median 26 blocking at ship. This is 60."* Without it,
    60 is a number with nothing to compare against — which is exactly how it
    came to be ignored twelve times. Computed, never written down, so it
    cannot drift from the tags it describes.
    """
    counts = sorted(suites[t] for t in tags if t in suites)
    if not counts:
        return ""
    middle = len(counts) // 2
    median = (counts[middle] if len(counts) % 2
              else (counts[middle - 1] + counts[middle]) // 2)
    return (f"{len(counts)} release{'s' if len(counts) != 1 else ''}, "
            f"median {median} blocking at ship. This is {today}.")


def _row(item: "Item", **extra: Any) -> dict[str, Any]:
    """One gate row. Every group emits this shape, so the client has one
    renderer rather than four that drift."""
    out: dict[str, Any] = {
        "tier": item.tier, "number": item.number, "section": item.section,
        "area": item.area, "name": item.name, "refs": list(item.refs),
        # The check's own words and its own address (FEAT-0103). Without these
        # the gate could only ever say how MANY, which is what Edwin reported
        # after the count shipped: *"I still don't seem to be able to see and
        # execute the current set."*
        "text": item.text, "anchor": item.anchor,
        "failed": item.failed, "rerun": item.rerun,
        # The note shape's address (ADR-0030). `number` still ships beside it
        # and still shifts; `id` does not, which is what every write path
        # prefers once a repo has migrated. Empty on a file-shape row, so a
        # client can tell which address it may trust without being told.
        "id": item.note_id, "rel": item.rel,
        "verdict_date": item.verdict_date,
        "verdict_reason": item.verdict_reason,
        "automation": item.automation,
        "invalidated_by": {
            "change": item.invalidated.change,
            "reason": item.invalidated.reason,
            "date": item.invalidated.date,
        } if item.invalidated else {},
        "stale": item.stale,
        # The mark the file holds, so the row can DRAW it (ISS-0190). The gate
        # row and the document row are the same check and now wear the same
        # control; one of them reading its state from `data-mark` and the other
        # inferring it from booleans is how the two would come to disagree.
        "mark": item.mark,
    }
    out.update(extra)
    return out


def gate_payload(
    docs_root: Path,
    index: "Any | None" = None,
    project_root: Path | None = None,
    baseline_ref: str = "",
    tags: "list[str] | None" = None,
) -> dict[str, Any]:
    """What blocks a release, in the template's own terms.

    The wording is the contract's, not this module's: *"A release is blocked
    while any Tier 1/Tier 2 test is unchecked (exceptions must be documented in
    the release note)."* A surface that paraphrased it would be a second
    statement of the rule, and the two would drift.

    **`blocking` keeps its old meaning and its old membership.** Every argument
    after `docs_root` is optional and additive: without them this returns what
    it always returned, which is what keeps the Tests view and every existing
    caller working while the Publication page asks for more.
    """
    suite = load(docs_root, index)
    blocking = suite.blocking()

    # --- quiet: the subject is not in flight (TASK-0447) ------------------
    #
    # ADR-0028 decision 3, finally reaching the population the ADR was written
    # about. Measured on `your-trainer`: 20 of the 60 are section 1.25, whose
    # FEAT-0074 is `backlog` — checks describing a screen that does not exist.
    quiet_rows: list[dict[str, Any]] = []
    live: list[Item] = list(blocking)
    if index is not None:
        from . import obligations

        quiet = [i for i in blocking
                 if obligations.ids_are_unbuilt(i.refs, index)]
        quiet_keys = {i.key for i in quiet}
        live = [i for i in blocking if i.key not in quiet_keys]
        quiet_rows = [
            _row(i, subjects=obligations.resting_reason(i.refs, index))
            for i in quiet
        ]

    # --- stale: ticked, but the row says the evidence no longer holds -----
    stale = [i for i in suite.items if i.tier in GATING_TIERS and i.stale]

    # --- the delta (TASK-0446) --------------------------------------------
    baseline = (
        suite_at(project_root, baseline_ref)
        if project_root is not None and baseline_ref else None
    )
    split = delta(suite, baseline)
    live_keys = {i.key for i in live}
    # The delta is computed over ALL blocking rows and then intersected with
    # the live ones, rather than over `live` directly. A quiet row is still
    # new or chronic — it is just not being asked about — and computing the
    # split on the filtered set would make the numbers depend on the order the
    # two rules were applied.
    groups = {
        name: [i for i in split[name] if i.key in live_keys]
        for name in ("new", "chronic", "regressed")
    }
    age_by_key = (
        ages(project_root, groups["chronic"], tags or [])
        if project_root is not None and tags else {}
    )
    # The historical line. Every tag is already parsed and cached by `ages`,
    # so this costs a dict comprehension rather than a second walk.
    history: dict[str, int] = {}
    if project_root is not None and tags:
        for tag in tags:
            at = suite_at(project_root, tag)
            if at is not None:
                history[tag] = len(at.blocking())

    return {
        "exists": suite.exists,
        "shape": suite.shape,
        "rel": suite_rel(suite),
        "blocked": bool(blocking),
        "rule": "A release is blocked while any Tier 1/Tier 2 test is "
                "unchecked (exceptions must be documented in the release "
                "note).",
        # The contract's sentence is quoted verbatim above and must stay that
        # way — a paraphrase becomes a second statement of the rule and the two
        # drift. But this repo now clears a check by a second mechanism the
        # contract does not name, and a gate that quotes one rule while
        # implementing another is that same drift wearing the quote as cover.
        # So the extension is stated beside it rather than folded into it, and
        # `TESTING.md` is owed the change upstream (ISS-0141). Found by
        # independent review.
        "local_rule": "This repo also settles a check by reconciliation — a "
                      "`- [~]` mark, meaning the check was closed by a "
                      "decision recorded on its own line rather than by being "
                      "walked. Reconciled checks do not block and are counted "
                      "separately; they are not release exceptions.",
        "blocking": [_row(i) for i in blocking],
        # --- the delta, additive to `blocking` above ----------------------
        #
        # `comparable` false means there was no baseline to diff against —
        # eleven of the twelve repos the cockpit discovers have no release tag
        # at all. The client renders the census it always rendered and says
        # why, rather than calling 60 rows "new".
        "delta": {
            "comparable": bool(split["comparable"]),
            "baseline": baseline_ref if split["comparable"] else "",
            "new": [_row(i) for i in groups["new"]],
            "chronic": [
                _row(i, since=age_by_key.get(i.key, ""),
                     # Not decoration. "Open since v2.0.5" is a fact; "open
                     # since v2.0.5, and you have shipped four releases over
                     # it" is the sentence that makes it a decision.
                     releases_since=_releases_since(
                         age_by_key.get(i.key, ""), tags or []))
                for i in groups["chronic"]
            ],
            "regressed": [_row(i) for i in groups["regressed"]],
            "summary": _summary(tags or [], history, len(blocking)),
        },
        # Quiet rows carry the reason, per ADR-0028 decision 5 — a collapsed
        # group that cannot name its subject is indistinguishable from one
        # that lost the row.
        "quiet": quiet_rows,
        # Neither blocking nor satisfied. 53 of `your-trainer`'s ticked rows
        # are here, which is why its honest blocking number is 113 and its
        # reported one is 60. Whether these should BLOCK is a change to what
        # shipping means and is deliberately not decided by a payload.
        "stale": [_row(i) for i in stale],
        "counts": {
            f"tier{n}": {
                "total": len(suite.tier(n)),
                "unchecked": sum(1 for i in suite.tier(n) if not i.settled),
                "reconciled": sum(1 for i in suite.tier(n) if i.reconciled),
                "excepted": sum(1 for i in suite.tier(n) if i.excepted),
            }
            for n in GATING_TIERS
        },
    }


# ----- addressing a check ---------------------------------------------------
#
# **A check is addressed by its id.** `locate()` and `rewrite_check()` lived
# here and wrote row grammar into `ACCEPTANCE_TESTS.md` by section-and-ordinal,
# because that was the only address a line in a document had. Deleted with the
# document surface (ISS-0192): every write now targets a `CHK-*` note's
# frontmatter, and `CHK-0412` survives an edit anywhere else in the corpus,
# which is what the whole migration bought.
#
# `parse()` above is NOT part of that and stays forever: `suite_at` reads the
# file shape at every pre-migration ref, which is all twelve of
# `../your-trainer`'s tags, and the release-gate delta depends on it.


# ----- the marks the record already uses (FEAT-0111 / TASK-0455) ------------
#
# ISS-0181 items 1 and 2 read as a design problem — no way to mark a check
# intentionally left open, no way to attach text. Both already exist, in
# `../your-trainer`'s own suites, used consistently with a grammar:
#
#     - [F] **Per-rider collapse persistence:** … **FAILS 2026-06-07** —
#       collapse state is stored globally … Tracked as [[ISS-0285]] …
#     - [~] **AI Workout Builder … :** … **Partial pass 2026-06-06**: English
#       prompts come back in English … (see [[ISS-0277]] …)
#     - [x] **[BOTH]** **ISS-0343 HRM reconnects …** ✅ (Claude, tablet:
#       address rotated 7F:D5:… → 73:DD:…; reconnected by name-match)
#
# This repo invented `[!]` for the same purpose in a form no suite writes, and
# shipped its permissive half without the half that asks for a reason
# (ISS-0177). Nothing here needed designing; the vocabulary was invented in
# the wrong place.

#: What a control may write, and what each writes. `[!]` is deliberately
#: absent: it stays READABLE (`_EXCEPTED_MARKS`) so a suite already using it
#: keeps working, and is never OFFERED, because offering it would re-open
#: ISS-0177's gap — an exception that drops a check with no justification.
#: Four marks, and the vocabulary is settled by measurement rather than taste.
#: Across every acceptance suite in the fleet on 2026-08-17: `x` 851, blank
#: 152, `~` 7, `F` 1, and **`!` zero**. `[!]` was minted in this repo and
#: written nowhere, so it stays READABLE and is never offered — Edwin, asked
#: directly: *"I have no problem using ~ instead."*
#:
#: ===========  ========  ==========================================  ========
#: mark         walked?   means                                       blocks
#: ===========  ========  ==========================================  ========
#: ``[ ]``      no        nobody has done it                          yes
#: ``[x]``      yes       passed                                      no
#: ``[~]``      no        could not be run, and is not holding the    no
#:                        release — Edwin 2026-08-17
#: ``[F]``      yes       walked and failed, tracked                  yes
#: ===========  ========  ==========================================  ========
#:
#: `[ ]` and `[F]` both block and mean **opposite** things about whether the
#: work was done, which is why `F` earns a mark rather than collapsing into
#: blank. `[~]` and `[x]` both pass the gate and mean opposite things about
#: whether anything was verified — which is why `[~]` cannot be written
#: without a reason.
VERDICTS: dict[str, str] = {
    "pass": "x",         # Minimal: done
    "partial": "/",      # Minimal: incomplete
    "excused": "-",      # Minimal: canceled
    "failed": "!",       # Minimal: important
    "question": "?",     # Minimal: question
    "clear": " ",        # Minimal: to-do
}
#: The legacy marks, read forever and never written (ADR-0029).
LEGACY_MARKS: dict[str, str] = {"~": "/", "F": "!", "X": "x"}
#: Refused without a reason. The mark and its justification are one action, so
#: a check cannot leave the gate silently — the whole gap [[ISS-0177]] records
#: for `[!]`, which shipped its permissive half with no way to ask why.
VERDICTS_NEEDING_REASON: frozenset[str] = frozenset({
    "partial", "excused", "failed", "question",
})
#: Ids named in a reason, linkified on write and checked by the caller.
_REASON_ID_RE = re.compile(r"\b([A-Z]{2,6}-\d{3,4})\b")
# `_escape_reason` lived here and went with the row grammar (ISS-0192). It
# flattened a reason to one line, stripped every metacharacter that could
# escape a list item, and linkified any id it found — all of which mattered
# because the reason was appended to a Markdown row. A `verdict_reason:` field
# is a YAML scalar, so `note_writes._yaml_safe` does the flattening and the
# quote-escaping that matter there, and nothing linkifies: the field is text.
#
# `_REASON_ID_RE` stays for `issue_refs_in` below, which is the half that was
# never about rendering — it tells the caller which ids a reason names so the
# write can be REFUSED when one of them resolves to nothing.


def issue_refs_in(reason: str) -> tuple[str, ...]:
    """Project-os ids a reason names, so the caller can check they resolve.

    Returned rather than linkified here: whether an id resolves is a question
    for the index, which this module deliberately does not import.
    """
    return tuple(dict.fromkeys(_REASON_ID_RE.findall(reason or "")))
