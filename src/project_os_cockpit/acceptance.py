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
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

#: Where the suite lives. TESTING.md names this path; it is not configurable,
#: for the same reason `SNAPSHOT.yaml` is not — a checklist the gate cannot
#: find is a gate that silently passes.
SUITE_REL = "tests/ACCEPTANCE_TESTS.md"

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
_RECONCILED_MARKS = frozenset({"~"})
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
_EXCEPTED_MARKS = frozenset({"!"})
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
_FAILED_MARKS = frozenset({"F"})
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
class Item:
    """One checkbox — the unit the gate reads."""

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
    #: Walked and failed, with the failure tracked on the line (TASK-0454).
    #: Blocking — `settled` deliberately does not consult this — and named so a
    #: surface can distinguish *"nobody has walked this"* from *"somebody
    #: walked it and it failed"*, which are the same colour today.
    failed: bool = False
    #: `RE-RUN (TASK-####: reason)` — the reason verbatim, or `""`.
    #: Meaningful on a **ticked** row, where it means the tick is stale
    #: (TASK-0448).
    rerun: str = ""
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
    def settled(self) -> bool:
        """What the gate reads — walked, reconciled, or excepted.

        Not "done": a reconciled item was never performed and an excepted one
        is being shipped undone, and the tier counts say so separately.
        """
        return self.checked or self.reconciled or self.excepted

    @property
    def stale(self) -> bool:
        """Ticked, but the line says the evidence no longer holds.

        Neither blocking nor satisfied — a third thing, and saying so is the
        point. An **unticked** annotated row is already blocking and must not
        be counted here as well, which is what the `checked` conjunct buys.
        """
        return self.checked and bool(self.rerun)

    @property
    def number(self) -> str:
        return f"{self.section}.{self.ordinal}"

    @property
    def key(self) -> str:
        return f"{self.number} {self.name}"


@dataclass
class Suite:
    path: Path | None = None
    items: list[Item] = field(default_factory=list)

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
            rerun=rerun.group(1).strip() if rerun else "",
            refs=refs, ordinal=ordinal, heading=full_heading,
        ))
    return items



def load(docs_root: Path) -> Suite:
    """The suite, or an empty one when the repo has never instantiated it.

    **Absent is not passing.** A repo with no suite has no Tier 1/2 items, so
    `blocking()` is empty and the gate would report "clear" — which is exactly
    the state every repo was in before this existed, and exactly the state that
    made the gate look like it worked. `gate_payload` reports `exists` so a
    surface can say "never instantiated" instead of "nothing blocking".
    """
    path = docs_root / SUITE_REL
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return Suite()
    return Suite(path=path, items=parse(text))


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
    """
    from .git_state import _git_raw

    cache_key = (str(project_root), f"{ref}:{rel}")
    if cache_key in _at_ref:
        return _at_ref[cache_key]
    text = _git_raw(project_root, "show", f"{ref}:docs/{rel}")
    out = None if text is None else Suite(path=None, items=parse(text))
    _at_ref[cache_key] = out
    return out


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


def payload(docs_root: Path) -> dict[str, Any]:
    """The suite as data, for the Tests view's tier groups."""
    suite = load(docs_root)
    return {
        "exists": suite.exists,
        "rel": SUITE_REL if suite.exists else "",
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
    suite = load(docs_root)
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
        "rel": SUITE_REL if suite.exists else "",
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


# ----- addressing a check (FEAT-0103 / TASK-0430) ---------------------------
#
# The walker needs to WRITE a check, and the existing `check-toggle` endpoint
# addresses a checkbox by its **zero-based ordinal within the whole rendered
# file**. The suite has 542 of them. Any edit above a row shifts every index
# below it, so a walker built on that would write whatever is now at that
# position — silently, and to a check nobody was looking at. A walker that
# writes the wrong row is worse than one that writes nothing.
#
# `Item.number` (`1.25.3`) survives an edit elsewhere in the file, and when its
# own section changes it fails to RESOLVE rather than resolving to something
# else. That asymmetry is the whole reason it is the address.


def locate(text: str, number: str) -> tuple[int, Item] | None:
    """The 0-based source line of the check at ``number``, and the item.

    ``None`` when the address does not resolve — never a nearest match. The
    caller is about to write to this line.
    """
    body_offset = 0
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            body_offset = text[: len(text) - len(parts[2])].count("\n")

    items = parse(text)
    wanted = next((i for i in items if i.number == number), None)
    if wanted is None:
        return None

    # Walk the body the same way `parse` does and count to the same item, so
    # the line found is the line that produced it rather than the first line
    # that looks similar.
    lines = text.splitlines()
    tier = 0
    section = ""
    ordinal = 0
    in_fence = False
    for index in range(body_offset, len(lines)):
        line = lines[index]
        if _FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if _TIER_HEADING_RE.match(line):
            tier = int(_TIER_HEADING_RE.match(line).group(1))
            section, ordinal = "", 0
            continue
        sect = _SECTION_RE.match(line)
        if sect:
            section = sect.group(1)
            ordinal = 0
            continue
        if tier == 0 or not _ITEM_RE.match(line):
            continue
        ordinal += 1
        if f"{section}.{ordinal}" == number:
            return index, wanted
    return None                          # pragma: no cover — parse/walk agree


def rewrite_check(
    text: str, number: str, *, name: str, mark: str, note: str = "",
) -> str:
    """Return ``text`` with the check at ``number`` re-marked.

    ``name`` is compared against the item found: an address that resolves to a
    DIFFERENT check is refused rather than written, because the caller is
    acting on what it last read and the file may have moved underneath it.

    A ``- [~]`` row is refused outright. Reconciled means *settled by a
    decision recorded on its own line* (ISS-0141), and converting one into a
    walked check would erase the distinction the mark exists to make.
    """
    found = locate(text, number)
    if found is None:
        raise LookupError(f"{number} does not resolve to a check in the acceptance tests")
    line_no, item = found
    if item.name != name:
        raise LookupError(
            f"{number} is now {item.name!r}, not {name!r} — the acceptance tests moved "
            "underneath this walk",
        )
    if item.reconciled:
        raise LookupError(
            f"{number} is reconciled — settled by a decision rather than by "
            "being walked, and a walk must not overwrite that",
        )

    lines = text.splitlines(keepends=True)
    raw = lines[line_no]
    ending = "\n" if raw.endswith("\n") else ""
    stripped = raw[: len(raw) - len(ending)]
    match = _ITEM_RE.match(stripped)
    if match is None:                    # pragma: no cover — locate() found it
        raise LookupError(f"{number} is not a checkbox line")
    head = stripped[: stripped.index("[")]
    rest = stripped[stripped.index("]") + 1:]
    if note:
        rest = f"{rest.rstrip()} {note}"
    lines[line_no] = f"{head}[{mark}]{rest}{ending}"
    return "".join(lines)


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
VERDICTS: dict[str, str] = {
    "pass": "x",
    "partial": "~",
    "fail": "F",
}
#: Verdicts whose write is refused without a reason. This is the whole
#: difference between these marks and `[!]`: the mark and its justification are
#: one action, so a check cannot leave the gate silently.
VERDICTS_NEEDING_REASON: frozenset[str] = frozenset({"partial", "fail"})
#: Ids named in a reason, linkified on write and checked by the caller.
_REASON_ID_RE = re.compile(r"\b([A-Z]{2,6}-\d{3,4})\b")
#: How each reads in the record. `pass` uses the witness form; the other two
#: use the dated-verdict form.
_VERDICT_WORD: dict[str, str] = {"partial": "Partial pass", "fail": "FAILS"}


def verdict_note(verdict: str, *, date: str, reason: str = "") -> str:
    """The text appended to a check's line, in the corpus's own grammar.

    Escaped so a reason can never corrupt the row it lands on. A newline would
    end the list item and orphan everything after it; an unbalanced ``**``
    would swallow the rest of the line into bold; a ``|`` would open a new
    cell if the check ever sits in a table.
    """
    clean = _escape_reason(reason)
    if verdict == "pass":
        return f"✅ ({clean})" if clean else "✅"
    word = _VERDICT_WORD.get(verdict, verdict.upper())
    return f"**{word} {date}** — {clean}" if clean else f"**{word} {date}**"


def _escape_reason(reason: str) -> str:
    """One line, no metacharacter that can escape the row — then linkified.

    The order matters and is the whole subtlety. Brackets are stripped first,
    because a reason containing a stray `]` would otherwise close a wikilink
    it never opened; ids are linkified **after**, so the `[[ISS-0285]]` form
    the corpus uses is produced by this function rather than trusted from the
    caller. A reason that already said `[[ISS-0285]]` and one that said
    `ISS-0285` therefore write the identical line.
    """
    flat = " ".join((reason or "").split())
    flat = (
        flat.replace("\\", "")
            .replace("**", "")
            .replace("`", "")
            .replace("|", "/")
            .replace("[", "").replace("]", "")
    ).strip()
    return _REASON_ID_RE.sub(lambda m: f"[[{m.group(1)}]]", flat)


def issue_refs_in(reason: str) -> tuple[str, ...]:
    """Project-os ids a reason names, so the caller can check they resolve.

    Returned rather than linkified here: whether an id resolves is a question
    for the index, which this module deliberately does not import.
    """
    return tuple(dict.fromkeys(_REASON_ID_RE.findall(reason or "")))


def check_map(text: str) -> list[dict[str, Any]]:
    """Every checkbox in DOM order, with the suite address it corresponds to.

    The rendered document addresses a checkbox by its position among all
    ``input[type=checkbox]`` on the page; the suite addresses a check by
    section-and-ordinal (:func:`locate`). This is the mapping, computed here
    so the **client owns no rule** about the suite's shape — TASK-0357's rule,
    and the reason the obligation vocabulary ships from the server.

    **It deliberately carries no DOM index.** The obvious mapping — the Nth
    rendered checkbox is the Nth parsed check — is FALSE on a real suite, and
    measurably so: `your-trainer` parses 579 checks and renders 542 inputs, so
    the correspondence drifts by 37 and everything after the first divergence
    is attributed to the wrong row. `_annotate_checkbox_source` already makes
    exactly that assumption for `data-raw`, and 285 of the 542 rendered rows
    carry text that is not their own (ISS-0175).

    So this returns addresses only. Wiring it to the DOM waits on that bug,
    because a control that writes to the wrong check is worse than no control.
    """
    return [
        {
            "number": item.number,
            "name": item.name,
            "mark": (
                "x" if item.checked
                else "~" if item.reconciled
                else "!" if item.excepted
                else " "
            ),
            "tier": item.tier,
            "gating": item.tier in GATING_TIERS,
        }
        for item in parse(text)
    ]
