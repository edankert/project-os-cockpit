"""`FEATURE-UNCOVERED` — a finished feature that nothing verifies ([[TASK-0523]]).

Built on constructed corpora rather than on this repo's, because the live
number (88) is exactly the kind of figure that drifts under every commit — and
a guard that pins it would be edited, not obeyed.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools" / "scripts" / "validate-docs.py"
BUNDLED = ROOT / "src" / "project_os_cockpit" / "validate_docs_bundled.py"


def _repo(tmp: Path, *, suite: bool, status: str, exception: str = "") -> Path:
    """A minimal repo: one feature, and optionally one acceptance check."""
    docs = tmp / "docs"
    (docs / "features" / "f").mkdir(parents=True)
    (tmp / "SNAPSHOT.yaml").write_text(
        'version: 1\nproject:\n  name: "t"\n  repo_root: "."\n'
        "counters:\n  FEAT: 1\n  TST: 1\nitems: {}\n", encoding="utf-8")
    extra = f'acceptance_exception: "{exception}"\n' if exception else ""
    (docs / "features" / "f" / "FEAT-0001-Thing.md").write_text(
        f'---\ntype: "[[feature]]"\nid: FEAT-0001\ntitle: "Thing"\n'
        f'status: {status}\n{extra}---\n\n# Thing\n', encoding="utf-8")
    if suite:
        (docs / "tests" / "acceptance").mkdir(parents=True)
        (docs / "tests" / "acceptance" / "TST-0001-C.md").write_text(
            '---\ntype: "[[test]]"\nid: TST-0001\ntitle: "C"\n'
            'level: acceptance\nstatus: active\narea: "A"\nmark: todo\n'
            'covers: []\n---\n\n# C\n', encoding="utf-8")
    return tmp


def _findings(repo: Path) -> int:
    out = subprocess.run(
        [sys.executable, str(VALIDATOR), "--repo-root", str(repo)],
        capture_output=True, text=True).stdout
    return out.count("FEATURE-UNCOVERED")


def test_it_fires_on_a_done_feature_nothing_covers(tmp_path: Path) -> None:
    assert _findings(_repo(tmp_path, suite=True, status="done")) == 1


def test_it_is_silent_while_the_feature_is_unfinished(tmp_path: Path) -> None:
    """The subject is *shipped and unverified*, not *not yet verified*."""
    assert _findings(_repo(tmp_path, suite=True, status="doing")) == 0


def test_an_exception_silences_it(tmp_path: Path) -> None:
    """**The escape is what makes the rule honest.** Without a way to say once,
    in the note, that a feature can never have a check — an engine with no
    rider-facing surface, a phase of work — this is a rule people disable
    rather than satisfy.
    """
    repo = _repo(tmp_path, suite=True, status="done",
                 exception="engine with no rider-facing surface")
    assert _findings(repo) == 0


def test_it_says_nothing_in_a_repo_with_no_suite(tmp_path: Path) -> None:
    """Nine of the twelve fleet repos hold no acceptance check at all. Firing
    there would scold them for not using a mechanism they never adopted —
    236 findings fleet-wide against 147 in the three that have a suite.
    """
    assert _findings(_repo(tmp_path, suite=False, status="done")) == 0


def test_it_warns_and_never_errors(tmp_path: Path) -> None:
    """**Undated, deliberately** ([[ADR-0011]] clause 3). The debt is 147 in
    suite-bearing repos, 88 of them in this one. A date would either fail every
    build on arrival or be moved when it did, and a promotion nobody intends to
    honour teaches people to ignore the table.
    """
    repo = _repo(tmp_path, suite=True, status="done")
    out = subprocess.run(
        [sys.executable, str(VALIDATOR), "--repo-root", str(repo)],
        capture_output=True, text=True)
    assert "WARN  [FEATURE-UNCOVERED]" in out.stdout, out.stdout[-400:]
    assert "ERROR [FEATURE-UNCOVERED]" not in out.stdout
    #: And it is not in the promotions table, which is what a date would mean.
    src = VALIDATOR.read_text(encoding="utf-8")
    table = src[src.index("PROMOTIONS = {"):]
    table = table[:table.index("}")]
    assert "FEATURE-UNCOVERED" not in table, (
        "the rule has been dated; 147 outstanding findings is not a promise"
    )


def test_the_two_validator_copies_stay_identical() -> None:
    """`tools/scripts/validate-docs.py` ships downstream and
    `validate_docs_bundled.py` is the package's copy. They are **byte-identical
    at HEAD**, and adding this rule to only one of them is exactly what
    happened first: the rule was written, measured 88 in the corpus, and
    reported **zero** — because `validate-docs.sh` runs the other file.

    Nothing in the suite caught that. This does.
    """
    assert BUNDLED.read_bytes() == VALIDATOR.read_bytes(), (
        "the two validator copies have diverged — a rule added to one of them "
        "silently does not run in the other, and `validate-docs.sh` runs "
        "`tools/scripts/validate-docs.py`"
    )


# ---- the scaffold end of the same rule (TASK-0522) ------------------------

SCAFFOLD = ROOT / "tools" / "skills" / "feature-scaffold" / "SKILL.md"
FEATURE_TEMPLATE = ROOT / "docs" / "__templates__" / "feature.md"


def test_the_scaffold_emits_a_check_by_rule_not_by_judgement() -> None:
    """[[TASK-0522]]. Step 9 read *"if the feature requires verification"* — a
    judgement made per feature, at the end, by whoever was tired.

    Measured across the twelve project-os repos on 2026-08-20: **236 features
    reached a terminal status with no acceptance check covering them.** A rule
    applied when somebody remembers is not a rule.
    """
    src = SCAFFOLD.read_text(encoding="utf-8")
    assert "plan/tests/TST-####-*.md" in src, (
        "the scaffold's Outputs no longer name the acceptance check"
    )
    step = src[src.index("9. **Emit one acceptance check"):]
    step = step[:step.index("\n10.")] if "\n10." in step else step
    assert "This is not conditional" in step
    #: **The old wording is QUOTED in the new step**, so a bare substring
    #: search matches the explanation and fails — the over-broad text match
    #: that has now bitten four guards in this phase. What must not come back
    #: is the wording as a live INSTRUCTION, which is a step line beginning
    #: with it rather than a quotation inside one.
    live = [ln for ln in src.splitlines()
            if ln.lstrip().startswith(("9.", "- If the feature requires"))
            and "if the feature requires verification" in ln.lower()
            and "*" not in ln]
    assert not live, f"the conditional wording is back as an instruction: {live}"
    #: The escape is named at the scaffold end too, or the rule is one people
    #: disable rather than satisfy.
    assert "acceptance_exception" in step


def test_the_feature_template_carries_the_escape() -> None:
    """Said once, in the note, **at scaffold time when the reason is known** —
    not at close-out. The field has to exist in the template or the scaffold
    step points at nothing.
    """
    fm = FEATURE_TEMPLATE.read_text(encoding="utf-8")
    assert "acceptance_exception:" in fm
    #: Empty by default: filling it is the exception, and a template that
    #: pre-fills it would make the exception the default.
    assert 'acceptance_exception: ""' in fm


def test_the_scaffold_and_the_validator_ask_one_question() -> None:
    """The two ends of the work: the scaffold emits or excepts, and
    `FEATURE-UNCOVERED` warns at close-out for anything that is neither. If
    they named different fields, a feature could satisfy one and fail the
    other — [[REQ-0059]]'s shape across a skill and a validator.
    """
    scaffold = SCAFFOLD.read_text(encoding="utf-8")
    validator = VALIDATOR.read_text(encoding="utf-8")
    assert "FEATURE-UNCOVERED" in scaffold, (
        "the scaffold does not tell the author what will check this"
    )
    assert "acceptance_exception" in validator
    assert "acceptance_exception" in scaffold
