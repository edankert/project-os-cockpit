"""The fleet drift check fails when the fleet falls behind (TST-0081).

`tools/scripts/fleet-drift.py` exists because PHASE-041's whole subject is a
check that reported success while it could not see the problem: routine
`sync-project-os.sh` runs classified each fleet validator as DIVERGED, skipped
it, and printed "Sync complete" for months while the divergence grew ~93 lines
per eleven days.

So the assertions here are about the branches that are easy to leave untested:

  - the FAILING one, and its exact boundary;
  - "no validator" and "no upstream", which must be their own outcomes and must
    never be reported as a divergence of zero;
  - that a repo is judged on the RULES it runs, not on how many lines it differs
    by -- the metric that lets a repo be 1105 lines from upstream and ahead of it.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


drift = _load("_fleet_drift", REPO / "tools" / "scripts" / "fleet-drift.py")


#: Deliberately carries every CALL SHAPE upstream's validator actually uses, not
#: just the convenient one. `RULE_RE` has two sub-patterns that the first fixture
#: exercised neither of, and each blinds the check to real rules:
#:
#:   `\s*` spanning a newline   -- 10 of upstream's 52 codes are emitted from a
#:                                 wrapped call, VERIFY-ACCEPTANCE among them
#:   `(?:report,\s*)?`          -- 3 more, VERIFY-ACCEPTANCE again
#:
#: A code the regex cannot see is subtracted from BOTH sides, so a repo genuinely
#: missing it reports `ok` -- this phase's own failure shape, inside the guard it
#: left behind. So ECHO and FOXTROT below are load-bearing punctuation.
UPSTREAM_VALIDATOR = '''
def go(report, emit_for):
    report.error("ALPHA", "a")
    report.warn("BRAVO", "b")
    emit = emit_for("CHARLIE", "x")
    emit("CHARLIE", "c")
    if _acceptance_is_settled(t, i) and _acceptance_is_settled(u, i):
        report.error("DELTA", "d")
    promotion_emit(
        report, "ECHO", grandfathered, item_id)("ECHO", "e")
    report.warn(
        "FOXTROT",
        "f %s" % x)
'''

CHECK_NOTE = '''---
type: "[[test]]"
id: TST-0001
level: acceptance
status: active
---

# A check
'''


def make_repo(root: Path, name: str, *, validator: str | None, checks: int = 0,
              extra_note_padding: int = 0):
    repo = root / name
    (repo / "tools" / "scripts").mkdir(parents=True)
    (repo / "SNAPSHOT.yaml").write_text("version: 1\n", encoding="utf-8")
    if validator is not None:
        (repo / "tools" / "scripts" / "validate-docs.py").write_text(validator, encoding="utf-8")
    docs = repo / "docs"
    docs.mkdir(exist_ok=True)
    for n in range(checks):
        pad = ("padding: \"%s\"\n" % ("x" * extra_note_padding)) if extra_note_padding else ""
        docs.joinpath("TST-%04d.md" % (n + 1)).write_text(
            CHECK_NOTE.replace("id: TST-0001", "id: TST-%04d" % (n + 1)).replace(
                "level: acceptance", pad + "level: acceptance"),
            encoding="utf-8")
    return repo


@pytest.fixture
def fleet(tmp_path):
    up = tmp_path / "upstream"
    (up / "tools" / "scripts").mkdir(parents=True)
    (up / "tools" / "scripts" / "validate-docs.py").write_text(UPSTREAM_VALIDATOR, encoding="utf-8")
    root = tmp_path / "fleet"
    root.mkdir()
    return root, up


def run(root, up, *extra):
    return drift.main([str(root), "--upstream", str(up), *extra])


# ------------------------------------------------------------------ it fails

def test_a_gated_repo_missing_a_rule_fails(fleet, capsys):
    root, up = fleet
    make_repo(root, "behind", validator=UPSTREAM_VALIDATOR.replace(
        'report.error("DELTA", "d")', "pass"), checks=1)
    assert run(root, up) == 1
    assert "missing 1 upstream rule(s): DELTA" in capsys.readouterr().err


def test_the_threshold_boundary_is_exact(fleet):
    """Off by one on a threshold turns a guard into noise, or into nothing."""
    root, up = fleet
    make_repo(root, "behind", validator=UPSTREAM_VALIDATOR.replace(
        'report.error("DELTA", "d")', "pass"), checks=1)
    assert run(root, up, "--threshold", "0") == 1
    assert run(root, up, "--threshold", "1") == 0


def test_a_repo_running_every_rule_passes(fleet):
    root, up = fleet
    make_repo(root, "current", validator=UPSTREAM_VALIDATOR, checks=1)
    assert run(root, up) == 0


# ------------------------------------------------- absence is not agreement

def test_a_gated_repo_with_no_validator_is_its_own_outcome(fleet, capsys):
    root, up = fleet
    make_repo(root, "gateless", validator=None, checks=3)
    assert run(root, up) == 2, "must not be reported as zero drift"
    err = capsys.readouterr().err
    assert "gateless holds 3 acceptance check(s) and has no" in err


def test_a_missing_upstream_is_not_a_clean_fleet(fleet, capsys):
    root, up = fleet
    make_repo(root, "current", validator=UPSTREAM_VALIDATOR, checks=1)
    assert drift.main([str(root), "--upstream", str(up.parent / "nowhere")]) == 2
    assert "cannot compare, which is not the same as no drift" in capsys.readouterr().err


def test_an_absent_validator_reports_no_line_count_rather_than_zero(fleet):
    root, up = fleet
    make_repo(root, "gateless", validator=None)
    _codes, rows = drift.survey(root, up)
    row = next(r for r in rows if r["repo"] == "gateless")
    assert row["status"] == drift.ABSENT
    assert row["missing_lines"] is None and row["gate"] is None


# ------------------------------------------------------- rules, not lines

def test_a_repo_far_ahead_of_upstream_is_not_behind(fleet):
    """`project-os-cockpit` is 1105 lines from upstream and AHEAD of it -- new
    rules are authored there and upstreamed. A line-count guard would fail the
    one repo that is doing the right thing, and be turned off within a week."""
    root, up = fleet
    ahead = UPSTREAM_VALIDATOR + '\n'.join(
        '    report.error("EXTRA%d", "e")' % n for n in range(400))
    repo = make_repo(root, "ahead", validator=ahead, checks=1)
    _codes, rows = drift.survey(root, up)
    row = next(r for r in rows if r["repo"] == "ahead")
    assert row["status"] == drift.OK and row["missing_rules"] == []
    assert run(root, up) == 0


def test_an_ungated_repo_that_is_behind_is_reported_and_not_failed(fleet, capsys):
    """ADR-0011 clause 3: promoting a check over existing debt fails every build
    on the day it ships. Six repos hold no acceptance checks and are each 10
    rules behind -- reported loudly, not fatal, and `--gate-all` says otherwise."""
    root, up = fleet
    make_repo(root, "nochecks", validator=UPSTREAM_VALIDATOR.replace(
        'report.error("DELTA", "d")', "pass"), checks=0)
    assert run(root, up) == 0
    assert "NOT GATED but behind -- nochecks (1 rules" in capsys.readouterr().out
    assert run(root, up, "--gate-all") == 1


def test_the_gate_is_counted_per_repo(fleet):
    root, up = fleet
    make_repo(root, "gated", validator=UPSTREAM_VALIDATOR, checks=1)
    make_repo(root, "ungated", validator=UPSTREAM_VALIDATOR.replace(
        "_acceptance_is_settled(t, i) and _acceptance_is_settled(u, i)", "True"), checks=1)
    _codes, rows = drift.survey(root, up)
    by = {r["repo"]: r for r in rows}
    assert by["gated"]["gate"] == 2 and by["ungated"]["gate"] == 0
    # Small line divergence must not launder a missing gate into "fine".
    assert by["ungated"]["missing_lines"] <= 1


# ------------------------------------------------------------- the counter

def test_a_long_frontmatter_still_counts_as_a_check(fleet):
    """The counter read a fixed 2000-character head and was right only by luck;
    under-counting checks silently un-gates a repo."""
    root, up = fleet
    make_repo(root, "verbose", validator=UPSTREAM_VALIDATOR.replace(
        'report.error("DELTA", "d")', "pass"), checks=1, extra_note_padding=4000)
    _codes, rows = drift.survey(root, up)
    assert next(r for r in rows if r["repo"] == "verbose")["checks"] == 1
    assert run(root, up) == 1, "a repo whose checks went uncounted would pass"


def test_a_body_mention_of_level_acceptance_is_not_a_check(fleet):
    root, up = fleet
    repo = make_repo(root, "prose", validator=UPSTREAM_VALIDATOR, checks=0)
    (repo / "docs" / "note.md").write_text(
        "---\ntype: \"[[issue]]\"\nid: ISS-0001\n---\n\nlevel: acceptance\n", encoding="utf-8")
    _codes, rows = drift.survey(root, up)
    assert next(r for r in rows if r["repo"] == "prose")["checks"] == 0


def test_json_output_is_a_document_and_nothing_else(fleet, capsys):
    """Both an ungated-behind repo AND a gated one, because with only the gated
    one the human summary line never prints and the parse trivially succeeds --
    which is how this shipped broken: `--json | json.load` raised `Extra data`
    on the very first real run."""
    import json
    root, up = fleet
    stale = UPSTREAM_VALIDATOR.replace('report.error("DELTA", "d")', "pass")
    make_repo(root, "behind", validator=stale, checks=1)
    make_repo(root, "nochecks", validator=stale, checks=0)
    assert run(root, up, "--json") == 1
    out = capsys.readouterr()
    data = json.loads(out.out)
    by = {r["repo"]: r for r in data["repos"]}
    assert by["behind"]["missing_rules"] == ["DELTA"] and by["behind"]["gated"] is True
    assert by["nochecks"]["gated"] is False
    assert "NOT GATED but behind" in out.err


def test_every_call_shape_upstream_uses_is_seen(validator_path_not_used=None):
    """Drives `rule_codes` over the fixture and over UPSTREAM ITSELF.

    The fixture half kills the two regex mutants; the upstream half is the one
    that keeps mattering, because it fails the day somebody adds a rule with a
    call shape nobody anticipated -- which is exactly how this guard would go
    quietly blind.
    """
    from pathlib import Path
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "v.py"
        f.write_text(UPSTREAM_VALIDATOR, encoding="utf-8")
        assert drift.rule_codes(f) == {"ALPHA", "BRAVO", "CHARLIE", "DELTA", "ECHO", "FOXTROT"}

    up = Path.home() / "Dev" / "repos" / "project-os" / "tools" / "scripts" / "validate-docs.py"
    if not up.is_file():
        pytest.skip("no sibling project-os checkout")
    codes = drift.rule_codes(up)
    # Named explicitly rather than counted: a count passes while the SET rots,
    # and these three are the ones the two regex mutants drop.
    for code in ("VERIFY-ACCEPTANCE", "PARENT-BACKLINK", "SNAPSHOT-MEMBERSHIP",
                 "TEST-ENTRYPOINT", "PLAN-UNTYPED", "FEATURE-UNCOVERED"):
        assert code in codes, code
    assert len(codes) >= 50


def test_a_rule_the_regex_cannot_see_would_be_invisible_on_both_sides(fleet):
    """Why the fixture's call shapes matter, stated as behaviour.

    A repo missing ONLY a rule emitted from a wrapped call must still be
    reported behind -- if the regex cannot read that shape, the code is
    subtracted from upstream too and the repo reports `ok`.
    """
    root, up = fleet
    only_foxtrot_missing = UPSTREAM_VALIDATOR.replace(
        '    report.warn(\n        "FOXTROT",\n        "f %s" % x)', "    pass")
    make_repo(root, "wrapped", validator=only_foxtrot_missing, checks=1)
    _codes, rows = drift.survey(root, up)
    assert next(r for r in rows if r["repo"] == "wrapped")["missing_rules"] == ["FOXTROT"]
    assert run(root, up) == 1
