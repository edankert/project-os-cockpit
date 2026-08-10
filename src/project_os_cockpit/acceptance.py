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

_TIER_HEADING_RE = re.compile(r"^#\s+Tier\s+(\d)\s*[—-]\s*(.+?)\s*$", re.M)
_SECTION_RE = re.compile(r"^##\s+(\d+\.\d+)\s+(.*?)\s*$")
_ITEM_RE = re.compile(r"^-\s+\[( |x|X)\]\s+(.*?)\s*$")
_NAME_RE = re.compile(r"^\*\*(.+?):?\*\*:?\s*(.*)$")
_ID_RE = re.compile(r"\[\[([A-Z]+-[0-9A-Za-z-]+?)(?:\|[^\]]*)?\]\]")


@dataclass(frozen=True)
class Item:
    """One checkbox — the unit the gate reads."""

    tier: int
    section: str          # "1.3"
    area: str             # "The navigator"
    name: str
    text: str
    checked: bool
    #: 1-based position within its section, so every item has a unique number
    #: (`1.3.2`). Two items in one section otherwise share the section's id,
    #: and a navigator that keys rows on it would address the wrong one.
    ordinal: int = 1
    #: Project-os ids named by the section heading. Tier 1 sections name their
    #: features; Tier 2 sections name the `ISS-*` that created the test, which
    #: TESTING.md requires and `missing_issue_refs` enforces.
    refs: tuple[str, ...] = ()

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
        """Unchecked Tier 1/2 items — what stops a release."""
        return [i for i in self.items if i.tier in GATING_TIERS and not i.checked]

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
    refs: tuple[str, ...] = ()
    ordinal = 0

    for line in body.splitlines():
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
            refs = tuple(_ID_RE.findall(heading))
            # The heading minus its id list — "The navigator ([[FEAT-0010]], …)"
            area = re.sub(r"\s*\((?:[^()]*)\)\s*$", "", heading).strip()
            continue
        if tier == 0:
            continue
        item = _ITEM_RE.match(line)
        if not item:
            continue
        checked = item.group(1).lower() == "x"
        rest = item.group(2)
        named = _NAME_RE.match(rest)
        name, detail = (named.group(1), named.group(2)) if named else (rest, "")
        ordinal += 1
        items.append(Item(
            tier=tier, section=section, area=area,
            name=name.strip(), text=detail.strip(),
            checked=checked, refs=refs, ordinal=ordinal,
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
                "gating": n in GATING_TIERS,
                "items": [
                    {
                        "key": i.key, "number": i.number,
                        "section": i.section, "area": i.area,
                        "name": i.name, "text": i.text, "checked": i.checked,
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
        "blocking": [
            {"tier": i.tier, "number": i.number, "section": i.section,
             "area": i.area, "name": i.name, "refs": list(i.refs)}
            for i in blocking
        ],
        "counts": {
            f"tier{n}": {
                "total": len(suite.tier(n)),
                "unchecked": sum(1 for i in suite.tier(n) if not i.checked),
            }
            for n in GATING_TIERS
        },
    }
