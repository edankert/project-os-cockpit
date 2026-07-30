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
    """ISS-0069, with the context split ISS-0071 found unenforced.

    The first version checked the **union** of the two vocabularies, so it never
    enforced the split it claimed to: stamping a CHG close-out note
    `review_verdict: "accepted"` passed. The split is the whole point — ADR-0007
    made the desk's values distinct precisely so a plan-acceptance stamp cannot
    satisfy the close-out gate, and a check over the union re-merges them.

    So: desk values are legal only where desk acceptance happens. Today that is
    `[[design]]` notes (DES-0002 and DES-0004 carry `accepted`). If a FEAT or
    TASK ever gains one this fails — correctly, because that is the case
    ADR-0007 warns about and it deserves a decision, not a silent pass.
    """
    from project_os_cockpit.index import Index

    idx = Index.build(DOCS)
    offenders: list[tuple[str, str, str]] = []
    for r in idx.iter_records():
        value = r.frontmatter.get("review_verdict")
        if not isinstance(value, str) or not value.strip():
            continue                      # empty means unreviewed; ADR-0011 covers it
        value = value.strip()
        note_type = (r.note_type or "").lower()
        allowed = (ALLOWED_VERDICTS if note_type == "design" else CLOSE_OUT_VERDICTS)
        if value not in allowed:
            offenders.append((r.note_id or r.rel_path, note_type, value))
    assert not offenders, (
        "review_verdict values outside the vocabulary for their context — "
        f"close-out notes allow {sorted(CLOSE_OUT_VERDICTS)}, `design` notes "
        f"also allow {sorted(DESK_VERDICTS)}: {offenders}"
    )


def test_the_two_verdict_vocabularies_stay_disjoint() -> None:
    """ADR-0007's guarantee is that the sets do not overlap: if a value were in
    both, the desk could stamp something the close-out gate then accepted, which
    is the failure the ADR built two vocabularies to prevent."""
    assert not (CLOSE_OUT_VERDICTS & DESK_VERDICTS), (
        "the close-out and desk verdict vocabularies now share a value, so a "
        "plan-acceptance stamp could satisfy a close-out gate (ADR-0007)"
    )


# ---- ISS-0071: snapshot/note agreement the sync script does not cover -------


def test_the_snapshot_phase_matches_the_note() -> None:
    """`sync-snapshot.py` propagates `status`, `counters` and `metrics.counts`
    (ADR-0009) — **not `phase:`** — and the validator does not compare it. So a
    note re-phased by hand leaves the snapshot pointing at the old phase, and
    nothing notices.

    Found in review: five items said PHASE-999-Future in the snapshot while
    their notes said PHASE-011/012/013. Same class as the dangling
    `PHASE-999-Unscheduled` link (ISS-0070's neighbour) — a phase reference
    nothing checks.

    The fix cannot go in the sync script: that is template-owned with a bundled
    byte-identical copy (ISS-0026). So it is asserted here instead.
    """
    import re as _re

    from project_os_cockpit.index import Index

    idx = Index.build(DOCS)
    snap = (ROOT / "SNAPSHOT.yaml").read_text(encoding="utf-8")
    drift: list[tuple[str, str, str]] = []
    for m in _re.finditer(r"^    ([A-Z]+-\d{4}):\n((?:      .*\n)+)", snap, _re.M):
        note_id, block = m.group(1), m.group(2)
        sm = _re.search(r'^      phase: *"?\[\[([^\]"]+)\]\]"?', block, _re.M)
        if not sm:
            continue
        path = idx.by_id(note_id)
        record = idx.get(path) if path else None
        if record is None:
            continue
        raw = str(record.frontmatter.get("phase") or "").strip().strip('"')
        note_phase = _re.sub(r"^\[\[|\]\]$", "", raw)
        if not note_phase:
            continue
        # `PHASE-011` and `PHASE-011-Unproven-Claims` both name the same phase.
        if sm.group(1).split("-")[:2] != note_phase.split("-")[:2]:
            drift.append((note_id, sm.group(1), note_phase))
    assert not drift, (
        "SNAPSHOT.yaml disagrees with the notes about which phase these belong "
        f"to (snapshot, note): {drift}"
    )


def test_every_docs_note_is_tracked_by_git() -> None:
    """ISS-0070's missing check, and the one that would have caught it years
    earlier than a reviewer did.

    An unanchored `inbox/` in `.gitignore` matched `docs/features/inbox/`, so
    FEAT-0045, its PLAN and three tasks were never in the repository. Everything
    local stayed green — `sync-snapshot.py` reads the filesystem, so the metrics
    counted notes a clone could not see — and a fresh clone of `main` failed
    `validate-docs.py` with four METRICS errors.

    Cheaper than cloning: ask git whether it is ignoring anything under `docs/`.
    A note the repository cannot see is not documentation, and it cannot be
    independently reviewed, which is what made this worse than a lost file.
    """
    import subprocess

    result = subprocess.run(
        ["git", "ls-files", "--others", "--ignored", "--exclude-standard", "docs/"],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        pytest.skip("not a git work tree")
    ignored = [line for line in result.stdout.splitlines() if line.strip()]
    assert not ignored, (
        "git is ignoring files under docs/ — they are not in the repository, so "
        "a clone cannot validate and they cannot be reviewed:\n  "
        + "\n  ".join(ignored[:20])
    )

    # Disclosed limit: this sees ignored-AND-UNTRACKED files, which is exactly
    # ISS-0070's shape (the notes were never added). It will NOT fire for a file
    # already tracked when a pattern starts matching it, because git keeps
    # tracking those. Verified by probe: un-anchoring the pattern with the notes
    # already committed does not trip this; un-anchoring plus a new note does.
    # The residual risk is therefore new notes only, which is the risk that
    # matters — an existing note cannot silently leave the repository.
