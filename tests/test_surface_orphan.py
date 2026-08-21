"""`SURFACE-ORPHAN` — a check names a surface that does not exist ([[ISS-0250]]).

`surface_coverage()` joins a surface to its checks on the **lower-cased,
stripped title**. No link, no id, no reverse check. So editing a surface's
`title:` moves its count to zero and moves nothing else — and the two states
render identically: a surface with genuinely no checks and a surface whose 91
checks were orphaned by a rename both read *"no checks"*.

**The rename is constructed here and the check is watched firing**, which is
[[ISS-0250]]'s own second Next Action: *"an orphan reading as an honest zero is
the failure this phase has met eight times."*
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools" / "scripts" / "validate-docs.py"
BUNDLED = ROOT / "src" / "project_os_cockpit" / "validate_docs_bundled.py"

SNAPSHOT = (
    'version: 1\nupdated: "2026-08-21"\ncounters:\n  TST: 3\n  SUR: 1\n'
    'focus:\n  task: ""\nitems:\n  tests: {}\n'
)
#: The em dash is the point, not decoration: 8 of `your-trainer`'s 15 surface
#: titles contain one, and every one is otherwise ordinary words a person
#: would retype.
TITLE = "Riding — routes"


def _repo(tmp: Path, *, surface_title: str | None = TITLE,
          areas: list[str] | None = None) -> Path:
    docs = tmp / "docs"
    (docs / "surfaces").mkdir(parents=True, exist_ok=True)
    (docs / "tests" / "acceptance").mkdir(parents=True, exist_ok=True)
    (tmp / "SNAPSHOT.yaml").write_text(SNAPSHOT, encoding="utf-8")
    if surface_title is not None:
        (docs / "surfaces" / "SUR-0001-Riding.md").write_text(
            f'---\ntype: "[[surface]]"\nid: SUR-0001\n'
            f'title: "{surface_title}"\nstatus: active\n---\n\n# S\n',
            encoding="utf-8")
    for n, area in enumerate(areas if areas is not None else [TITLE] * 3,
                             start=1):
        (docs / "tests" / "acceptance" / f"TST-000{n}-C.md").write_text(
            f'---\ntype: "[[test]]"\nid: TST-000{n}\ntitle: "Check {n}"\n'
            f'level: acceptance\nstatus: active\nmark: todo\n'
            f'area: "{area}"\ncovers: ["[[FEAT-0001]]"]\n---\n\n# C\n',
            encoding="utf-8")
    return docs


def _findings(tmp: Path) -> list[str]:
    out = subprocess.run(
        [sys.executable, str(VALIDATOR), "--repo-root", str(tmp)],
        capture_output=True, text=True)
    return [ln for ln in out.stdout.splitlines() if "SURFACE-ORPHAN" in ln]


# ---- the rename, constructed and watched ---------------------------------

def test_a_renamed_surface_orphans_its_checks_and_the_rule_says_so(
        tmp_path: Path) -> None:
    """**The repro from the issue, executed.** One em dash retyped as a hyphen
    — the edit that took `your-trainer`'s SUR-0011 from 91 checks to 0 with no
    validator error and no test failure."""
    _repo(tmp_path)
    assert _findings(tmp_path) == [], "a matching surface must say nothing"

    #: The rename. Nothing else in the corpus moves.
    (tmp_path / "docs" / "surfaces" / "SUR-0001-Riding.md").write_text(
        '---\ntype: "[[surface]]"\nid: SUR-0001\n'
        'title: "Riding - routes"\nstatus: active\n---\n\n# S\n',
        encoding="utf-8")
    found = _findings(tmp_path)
    assert len(found) == 1, found
    assert "Riding — routes" in found[0], found[0]
    assert "3 check(s)" in found[0], found[0]


def test_one_finding_per_orphaned_name_not_per_check(tmp_path: Path) -> None:
    """A rename orphans every check on the surface at once. 91 identical
    errors describe one edit, and a person reading them cannot tell how many
    surfaces are broken."""
    _repo(tmp_path, surface_title="Something else",
          areas=["Riding — routes", "Riding — routes", "Workouts — authoring"])
    found = _findings(tmp_path)
    assert len(found) == 2, found
    assert any("2 check(s)" in ln and "Riding — routes" in ln for ln in found)
    assert any("1 check(s)" in ln and "Workouts — authoring" in ln for ln in found)


# ---- what the join tolerates, the rule must tolerate ---------------------

def test_case_and_surrounding_whitespace_survive_both(tmp_path: Path) -> None:
    """Reproduced by independent review on the real corpus: `Riding — Routes`,
    `RIDING — ROUTES` and `␠␠Riding — routes␠␠` all still resolve to 91. A
    rule stricter than the join would report an orphan that is not one."""
    for variant in ("Riding — Routes", "RIDING — ROUTES", "  Riding — routes  "):
        docs = _repo(tmp_path / variant.strip().lower().replace(" ", "_"),
                     areas=[variant])
        assert _findings(docs.parent) == [], variant


def test_the_rule_and_the_join_agree_on_normalisation(tmp_path: Path) -> None:
    """**The second implementation is forced and therefore guarded.** The
    validator is stdlib-only and standalone — it cannot import
    `cockpit.surface_coverage` — so the join exists twice, which is
    [[REQ-0059]]'s forbidden shape unless something pins the two together.

    Both are **driven over the same strings**, and neither is matched as text:
    a text assertion passes on a rule that reads `.strip().lower()` in a
    comment, which is this repo's own recorded mutation-testing pitfall.
    """
    from project_os_cockpit import cockpit, validate_docs_bundled as v
    from project_os_cockpit.index import Index

    variants = [
        ("Riding — routes", True),         # identical
        ("Riding — Routes", True),         # case
        ("RIDING — ROUTES", True),         # case
        ("  Riding — routes  ", True),     # surrounding whitespace
        ("Riding - routes", False),        # em dash retyped as a hyphen
        ("Riding  —  routes", False),      # internal double-spacing
        ("Riding — routes & free ride", False),
    ]
    for area, joins in variants:
        docs = _repo(tmp_path / str(abs(hash(area))), areas=[area])
        #: The JOIN's answer: does this surface count the check?
        counts = cockpit.surface_coverage(Index.build(docs))
        joined = counts.get("SUR-0001", 0) > 0
        #: The RULE's answer: is the area an orphan?
        orphan = v.surface_key(area) != v.surface_key(TITLE)
        assert joined == joins, f"the join changed for {area!r}"
        assert orphan != joined, (
            f"the rule and the join disagree about {area!r}: joined={joined}, "
            f"orphan={orphan} — the rule would report an orphan the join "
            f"resolves, or miss one it does not"
        )


# ---- what must stay silent -----------------------------------------------

def test_a_repo_with_no_surfaces_is_silent(tmp_path: Path) -> None:
    """Eleven of twelve fleet repos hold no `SUR-*` note. A rule that fires on
    every check in a repo that never opted into the type is a rule people turn
    off."""
    _repo(tmp_path, surface_title=None, areas=["Anything at all"])
    assert _findings(tmp_path) == []


def test_an_empty_area_is_not_an_orphan(tmp_path: Path) -> None:
    """The un-placed check, not the orphaned one — `TST-0015` and `TST-0018`
    in `your-trainer` are exactly that, and reporting them would make the
    rule's first run mostly noise."""
    _repo(tmp_path, areas=["", "   ", TITLE])
    assert _findings(tmp_path) == []


def test_a_surface_no_check_names_is_not_reported(tmp_path: Path) -> None:
    """That is the row [[FEAT-0130]] built the type to produce: *a place in the
    product nobody has tested.* Reporting it as a defect would make the type's
    own purpose an error."""
    _repo(tmp_path, areas=[])
    assert _findings(tmp_path) == []


# ---- it warns, and it says when it stops ---------------------------------

def test_it_warns_rather_than_erroring_on_day_one(tmp_path: Path) -> None:
    """21 distinct names over 34 checks in this repo at introduction, because
    only `SUR-0001` was ever written. That is one `SUR-*` note per surface to
    clear — TASK-0515's shape, a body of work rather than a line edit — so
    ADR-0011 clause 3 forbids erroring over it."""
    _repo(tmp_path, surface_title="Something else")
    found = _findings(tmp_path)
    assert found and all(ln.startswith("WARN") for ln in found), found


def test_the_promotion_is_dated_rather_than_permanent() -> None:
    """A warning with no cutover is a rule that never arrives."""
    src = VALIDATOR.read_text(encoding="utf-8")
    i = src.index('"SURFACE-ORPHAN": "')
    assert src[i:i + 40].split('"')[3][:4].isdigit()


def test_the_bundled_copy_carries_the_rule() -> None:
    """The two are byte-identical: `validate-docs.py` is what the pre-commit
    hook executes and the bundled copy is what the cockpit imports."""
    assert BUNDLED.read_text(encoding="utf-8") == VALIDATOR.read_text(encoding="utf-8")
