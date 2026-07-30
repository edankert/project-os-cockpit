"""ISS-0066 — a TST note's prose must not name a test that does not exist.

`TST-*` notes cite test functions by name, in `## Coverage`, in `## Adequacy`,
and in the evidence pointers that requirement criteria are ticked against. None
of that was checked by anything, so a rename in `tests/` silently turned a
citation into a claim about nothing.

Not hypothetical. Found while writing this check: `TST-0019` cited
`test_implemented_status_sorts_after_backlog_but_stays_expanded`, which had been
renamed to `..._sorts_and_collapses_with_the_done_family`. The note cited a
non-existent test for however long since that rename, and 559 passing tests
coexisted with it — because the suite tests the code, and nothing tested the
notes *about* the code.

The check is deliberately one-directional; `test_enumeration_is_not_the_convention`
records the measurement that says why.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
TESTS_DIR = ROOT / "tests"
DOCS = ROOT / "docs"

#: A plausible test-function mention in prose. Four chars minimum after the
#: prefix so short noise does not match.
MENTION = re.compile(r"\btest_[a-z0-9_]{4,}\b")
DEFINITION = re.compile(r"^def (test_\w+)", re.M)


def _defined_tests() -> dict[str, str]:
    """Every test function in `tests/`, mapped to the file defining it."""
    out: dict[str, str] = {}
    for f in sorted(TESTS_DIR.glob("test_*.py")):
        for m in DEFINITION.finditer(f.read_text(encoding="utf-8")):
            out[m.group(1)] = f.name
    return out


def _module_names() -> set[str]:
    """Test *module* stems — `test_cockpit_state` from `test_cockpit_state.py`.

    Excluded from the mention check because notes legitimately cite whole
    files (`path: "tests/test_cockpit_state.py"`) and the regex cannot tell a
    module reference from a function reference.
    """
    return {f.stem for f in TESTS_DIR.glob("test_*.py")}


def _tst_notes() -> list[Path]:
    return sorted(p for p in DOCS.rglob("TST-*.md") if p.is_file())


def test_there_are_tst_notes_to_check() -> None:
    """Guards the guard: if the glob stops matching, every assertion below
    passes over an empty set and reports success by finding nothing — the
    failure mode TST-0019's own history is full of."""
    assert len(_tst_notes()) >= 20, f"expected the TST corpus, found {len(_tst_notes())}"
    assert len(_defined_tests()) >= 200


@pytest.mark.parametrize("note", _tst_notes(), ids=lambda p: p.stem[:30])
def test_every_test_named_in_a_note_exists(note: Path) -> None:
    """The drift that actually occurs: a test is renamed or moved and the note
    citing it is not updated, so a citation becomes a claim about nothing.

    Parametrised per note so a failure names the offending file rather than
    reporting one aggregate list.
    """
    defined = _defined_tests()
    modules = _module_names()
    text = note.read_text(encoding="utf-8")

    missing = sorted(
        name for name in set(MENTION.findall(text))
        if name not in defined and name not in modules
    )
    assert not missing, (
        f"{note.name} names {len(missing)} test(s) that do not exist: {missing}. "
        "Either the test was renamed and the note was not updated, or the note "
        "describes a test nobody wrote."
    )


def test_enumeration_is_not_the_convention() -> None:
    """Records, as a measurement rather than an aspiration, why the check above
    is one-directional.

    The independent review of PHASE-010 recommended the other direction too:
    every test in the `path:` file should be named in `## Coverage`. Measured
    across the corpus, notes name a small minority of their own tests —
    `TST-0021` names 4 of 37, `TST-0004` names 0 of 9 — because a Coverage item
    is a *theme* covering several tests, not a per-test entry.

    Enforcing completeness would therefore fail almost every note here, and
    "fixing" that would mean changing what a Coverage item is: from prose a
    human writes to a mapping a machine checks. That is a template-level
    convention change, not a check to bolt on, and inventing the requirement
    to satisfy a guard would be backwards.

    This fails if that stops being true — if the corpus does start enumerating,
    the stronger check becomes available and should be added.
    """
    ratios: list[float] = []
    for note in _tst_notes():
        text = note.read_text(encoding="utf-8")
        m = re.search(r'^path: *"?([^"\n]+)"?', text, re.M)
        path = (m.group(1).strip() if m else "")
        if not re.fullmatch(r"tests/[\w.]+\.py", path):
            continue            # multi-file or node-id paths are not comparable
        src = ROOT / path
        if not src.exists():
            continue
        defined = set(DEFINITION.findall(src.read_text(encoding="utf-8")))
        if not defined:
            continue
        named = set(MENTION.findall(text)) & defined
        ratios.append(len(named) / len(defined))

    assert ratios, "no TST note has a single-file path; the measurement is void"
    assert min(ratios) < 0.5, (
        "every TST note now names at least half its tests, so enumeration may "
        "have become the convention — reconsider enforcing completeness "
        "(ISS-0066's second half)"
    )


# ---- ISS-0069: the review-verdict vocabulary --------------------------------

#: Close-out independent review (QUALITY.md).
CLOSE_OUT_VERDICTS = {"approved", "changes-requested"}
#: Desk plan-acceptance (ADR-0007), deliberately distinct so a plan-acceptance
#: stamp can never satisfy the close-out gate.
DESK_VERDICTS = {"accepted", "accepted-amended", "rejected"}
ALLOWED_VERDICTS = CLOSE_OUT_VERDICTS | DESK_VERDICTS


def test_review_verdicts_use_a_defined_value() -> None:
    """ISS-0069. `review_verdict` had a second, undefined vocabulary: 10 notes
    carried `CLOSE`, and nothing rejected it.

    The validator checks *presence* (ADR-0011's REVIEW rule) and the literal
    string `changes-requested` (the close-out gate). An arbitrary value passes
    both — it is not absent and it is not `changes-requested` — so it read as a
    satisfied review. This is ISS-0024 §1 one level up: a second vocabulary
    drifting because nothing held it to its definition.

    Empty is allowed: it means unreviewed, which ADR-0011 already warns about on
    a terminal note. What is not allowed is a value nobody defined.

    Reads the **parsed** frontmatter rather than matching source. The first cut
    used a regex and reported a false positive on
    `review_verdict: approved  # feature rounds 1-3` — it swallowed the trailing
    YAML comment into the value. A check that matches the wrong thing is the
    class this whole file exists for, so it uses the parser that already exists.
    """
    from project_os_cockpit.index import Index

    idx = Index.build(DOCS)
    offenders = sorted(
        (r.note_id or r.rel_path, r.frontmatter["review_verdict"].strip())
        for r in idx.iter_records()
        if isinstance(r.frontmatter.get("review_verdict"), str)
        and r.frontmatter["review_verdict"].strip()
        and r.frontmatter["review_verdict"].strip() not in ALLOWED_VERDICTS
    )
    assert not offenders, (
        "undefined review_verdict values (QUALITY.md allows "
        f"{sorted(CLOSE_OUT_VERDICTS)}, ADR-0007 adds {sorted(DESK_VERDICTS)}): "
        f"{offenders}"
    )
