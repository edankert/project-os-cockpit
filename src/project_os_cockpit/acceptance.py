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
        ordinal += 1
        items.append(Item(
            tier=tier, section=section, area=area,
            name=name.strip(), text=detail.strip(),
            checked=mark in _CHECKED_MARKS,
            reconciled=mark in _RECONCILED_MARKS,
            excepted=mark in _EXCEPTED_MARKS,
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


def gate_payload(docs_root: Path) -> dict[str, Any]:
    """What blocks a release, in the template's own terms.

    The wording is the contract's, not this module's: *"A release is blocked
    while any Tier 1/Tier 2 test is unchecked (exceptions must be documented in
    the release note)."* A surface that paraphrased it would be a second
    statement of the rule, and the two would drift.
    """
    suite = load(docs_root)
    blocking = suite.blocking()
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
        "blocking": [
            {"tier": i.tier, "number": i.number, "section": i.section,
             "area": i.area, "name": i.name, "refs": list(i.refs),
             # The check's own words and its own address (FEAT-0103). Without
             # these the gate could only ever say how MANY, which is what
             # Edwin reported after the count shipped: *"I still don't seem to
             # be able to see and execute the current set."*
             "text": i.text, "anchor": i.anchor}
            for i in blocking
        ],
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
        raise LookupError(f"{number} does not resolve to a check in this suite")
    line_no, item = found
    if item.name != name:
        raise LookupError(
            f"{number} is now {item.name!r}, not {name!r} — the suite moved "
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
