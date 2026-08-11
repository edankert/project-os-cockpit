"""A feature's acceptance criteria, as data the runner can walk (TASK-0287).

**The rule this module exists to keep**: *a criterion the validator counts is a
criterion the runner walks, always.* REQ-BOXES is what blocks a requirement
from going terminal with an unticked box; if the runner walked a different set,
a person could complete a run and still be refused at close-out — or worse, tick
their way past a criterion the gate never saw.

So the parse is deliberately a **restatement of the validator's**, and
`tests/test_criteria.py` proves them identical over the whole corpus rather
than trusting the restatement. The validator lives in `tools/scripts/` (a
standalone script with no package imports, so CI can run it from a bare
checkout) and importing it here would invert that; matching it, and asserting
the match, is the affordable version of sharing it.

Three states, and the third is not decoration:

* ``open``       ``- [ ]``  — owed
* ``ticked``     ``- [x]``  — delivered, with evidence after the em dash
* ``reconciled`` ``- [~]``  — deliberately not delivered, with the reason

`STATUSES.md` defines the gate as *"ticked-with-evidence OR reconciled"*, so a
runner that offered only pass/fail would have no way to record the honest third
answer and would push people to tick things they did not do.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .index import Index, NoteRecord

#: The validator's three, character for character (`validate-docs.py`).
UNCHECKED_RE = re.compile(r"^\s*[-*+]\s*\[ \]")
CHECKED_RE = re.compile(r"^\s*[-*+]\s*\[[xX]\]")
RECONCILED_RE = re.compile(r"^\s*[-*+]\s*\[~\]")
FENCE_RE = re.compile(r"^\s*(```|~~~)")

#: REQ-BOXES' default: `Acceptance\b`, matching `## Acceptance` and
#: `## Acceptance Criteria` alike, and NOT `require_heading` — so a note with
#: no such heading is scanned whole, exactly as the validator scans it.
HEADING = r"Acceptance\b"

_STATE_RES = (
    ("open", UNCHECKED_RE),
    ("ticked", CHECKED_RE),
    ("reconciled", RECONCILED_RE),
)


def _strip_frontmatter(text: str) -> str:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4:]
    return text


def _section(text: str) -> list[str]:
    """The criteria section, or the whole body when there is no heading.

    Mirrors `count_acceptance_boxes` including the fence handling: a `- [ ]`
    inside a code fence is an example, not a criterion, and a `#` inside one is
    not a heading that ends the section.
    """
    section: list[str] = []
    body: list[str] = []
    seen_section = False
    in_fence = False
    for line in _strip_frontmatter(text).splitlines():
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        body.append(line)
        if re.match(r"^#{1,6}\s", line):
            if re.match(r"^#{1,6}\s+%s" % HEADING, line, re.IGNORECASE):
                seen_section, section = True, []
                continue
            if seen_section:
                break
        if seen_section:
            section.append(line)
    return section if seen_section else body


def _split_evidence(text: str) -> tuple[str, str]:
    """Criterion text and its evidence pointer.

    The corpus's convention is `<criterion> — <evidence>`. Split on the LAST em
    dash: criteria routinely contain one mid-sentence, and splitting on the
    first would file half the criterion as its own evidence.
    """
    if "—" not in text:
        return text.strip(), ""
    head, _, tail = text.rpartition("—")
    return head.strip(), tail.strip()


def parse_criteria(text: str) -> list[dict[str, Any]]:
    """Every acceptance checkbox in a note, in document order."""
    out: list[dict[str, Any]] = []
    for line in _section(text):
        for state, pattern in _STATE_RES:
            if not pattern.match(line):
                continue
            raw = re.sub(r"^\s*[-*+]\s*\[[ xX~]\]\s*", "", line).rstrip()
            witness, when = "", ""
            m = WITNESS_RE.search(raw)
            if m and state != "open":
                witness, when = m.group(1).strip(), m.group(2)
            body, evidence = _split_evidence(raw)
            out.append({
                "index": len(out),
                "text": body,
                "raw": raw,
                "state": state,
                # Evidence only means something on a settled criterion. On an
                # open one an em dash is just punctuation.
                "evidence": evidence if state != "open" else "",
                # REQ-0028: acceptance evidence names its witness. Read back
                # here so a re-run shows who settled a criterion and when,
                # rather than presenting it as anonymous.
                "witness": witness,
                "witness_date": when,
            })
            break
    return out


def _requirements_of(index: Index, feature_id: str) -> list[NoteRecord]:
    """Requirements constraining a feature — `implements:` **and** `specifies:`.

    Both are in use and they mean different things: `implements:` names the one
    feature that owns the requirement (ADR-0007 caps it at one, REQ-OWNER
    enforces it), while `specifies:` names every feature it constrains and is
    routinely plural — REQ-0026 specifies FEAT-0059 and FEAT-0060.

    Accepting a feature means walking everything that constrains it, so both
    directions count. Reading from the requirement rather than the feature's
    `requirements:` list keeps the claim with the note that owns it.
    """
    wanted = (feature_id or "").strip().upper()
    if not wanted:
        return []
    out: list[NoteRecord] = []
    for record in index.notes_by_type("requirement"):
        if record.rel_path.startswith("__templates__/"):
            continue
        for field in ("implements", "specifies"):
            raw = record.frontmatter.get(field)
            items = raw if isinstance(raw, list) else [raw]
            if any(wanted in str(item or "").upper() for item in items):
                out.append(record)
                break
    out.sort(key=lambda r: str(r.note_id or ""))
    return out


#: `(user:edwin, 2026-08-10)` at the end of a ticked criterion.
WITNESS_RE = re.compile(r"\(([^()]*?),\s*(\d{4}-\d{2}-\d{2})\)\s*$")


def _declared_criteria(record: NoteRecord) -> list[str]:
    """The `acceptance:` list in frontmatter — the criteria OF RECORD.

    Distinct from the body's checkboxes, which are the VERIFICATION record.
    REQ-BOXES compares the two: criteria with no boxes is "no verification
    record", and that is the state a runner exists to move out of.
    """
    raw = record.frontmatter.get("acceptance")
    if isinstance(raw, list):
        return [str(x).strip() for x in raw if str(x).strip()]
    return []


def payload(index: Index, feature_id: str) -> dict[str, Any]:
    """`GET /api/notes/acceptance?id=FEAT-…` — the runner's whole input.

    A feature with no criteria returns `nothing_to_accept`, which is a real
    answer rather than an error: FEAT-0065 counts exactly that as debt, and
    an empty runner screen would say the same thing far less usefully.
    """
    feature = None
    for record in index.notes_by_type("feature"):
        if (record.note_id or "").upper() == (feature_id or "").upper():
            feature = record
            break
    if feature is None:
        return {"error": f"{feature_id} is not a feature in this corpus"}

    requirements: list[dict[str, Any]] = []
    totals = {"open": 0, "ticked": 0, "reconciled": 0}
    for req in _requirements_of(index, feature_id):
        try:
            criteria = parse_criteria(req.path.read_text(encoding="utf-8"))
        except OSError:
            criteria = []
        declared = _declared_criteria(req)
        # Criteria of record with NO verification record: REQ-BOXES' second
        # error, and precisely the state a runner exists to move out of. The
        # declared text is surfaced as `open` so the walk has something to
        # walk — otherwise a requirement with four criteria and no boxes
        # presents as nothing to accept, which is the opposite of the truth.
        if declared and not criteria:
            criteria = [
                {"index": i, "text": text, "raw": text, "state": "open",
                 "evidence": "", "witness": "", "witness_date": "",
                 "from_frontmatter": True}
                for i, text in enumerate(declared)
            ]
        for criterion in criteria:
            totals[criterion["state"]] += 1
        requirements.append({
            "id": req.note_id or "",
            "title": req.title or "",
            "rel": req.rel_path,
            "status": req.status or "",
            "declared": len(declared),
            "criteria": criteria,
        })

    total = sum(totals.values())
    return {
        "id": feature.note_id or "",
        "title": feature.title or "",
        "rel": feature.rel_path,
        "requirements": requirements,
        "totals": totals,
        "total": total,
        "nothing_to_accept": total == 0,
    }
