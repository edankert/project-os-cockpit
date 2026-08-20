"""`FEATURE-UNCOVERED` — a finished feature that nothing verifies ([[TASK-0523]]).

Built on constructed corpora rather than on this repo's, because the live
number is exactly the kind of figure that drifts under every commit — and a
guard that pins it would be edited, not obeyed. Measured per commit with each
commit's own validator: **88** when the rule landed, **92**, then **94** — and
nobody touched the rule. (**93 appears in no commit.** It was written here from
a mid-session working tree with one of two features already flipped to `done`,
and independent review caught it: a number the corpus never held, in the
docstring explaining that the number moves.)
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools" / "scripts" / "validate-docs.py"
BUNDLED = ROOT / "src" / "project_os_cockpit" / "validate_docs_bundled.py"


def _repo(tmp: Path, *, suite: bool, status: str, exception: str = "",
          covers: str = "") -> Path:
    """A minimal repo: one feature, and optionally one acceptance check.

    `covers` is what the acceptance check names. It defaults to nothing, which
    is the fixture every case here used until 2026-08-20 — and that is exactly
    why the rule's POSITIVE half went unguarded: no test ever built a feature
    that WAS covered, so `_features_covered_by_acceptance` returning the empty
    set passed all of them.
    """
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
            f'covers: [{covers}]\n---\n\n# C\n', encoding="utf-8")
    return tmp


def _findings(repo: Path) -> int:
    out = subprocess.run(
        [sys.executable, str(VALIDATOR), "--repo-root", str(repo)],
        capture_output=True, text=True).stdout
    return out.count("FEATURE-UNCOVERED")


def test_it_fires_on_a_done_feature_nothing_covers(tmp_path: Path) -> None:
    assert _findings(_repo(tmp_path, suite=True, status="done")) == 1


def test_a_covered_feature_is_quiet(tmp_path: Path) -> None:
    """**The rule's positive half, and until 2026-08-20 nothing guarded it.**

    Every other case here builds a check that covers NOTHING, so coverage was
    only ever exercised as the empty set. Executed: replacing
    `_features_covered_by_acceptance`'s body with `return covered` immediately
    after `covered = set()` — so a covered feature is never recognised — passed
    **all fourteen** tests in this file, in both validator copies and upstream,
    while taking this repo from 94 warnings to **125**.

    A rule that reports on everything is as useless as one that reports on
    nothing, and it is the failure mode a suite full of negative cases cannot
    see. This is the case that fires.
    """
    repo = _repo(tmp_path, suite=True, status="done", covers='"[[FEAT-0001]]"')
    assert _findings(repo) == 0, (
        "a feature covered by an acceptance check is still being reported; "
        "the coverage half of the rule is not running"
    )


def test_coverage_is_matched_on_the_id_not_the_whole_link(tmp_path: Path) -> None:
    r"""`[[FEAT-0001-Thing]]` and a bare `FEAT-0001` name one feature.

    The reverse index reads `FEAT-\d+` out of each `covers:` entry, so the slug
    is display and the id is the member. A match on the whole wikilink would
    quietly fail against the slugged form, which is what most real notes carry.
    """
    repo = _repo(tmp_path, suite=True, status="done",
                 covers='"[[FEAT-0001-Thing]]"')
    assert _findings(repo) == 0


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
    there would scold them for not using a mechanism they never adopted.
    Re-measured 2026-08-20 across the twelve `SNAPSHOT.yaml` repos: **225**
    fleet-wide against **139** in the three that hold a suite, under the rule
    as it ships (`done` alone) — so **86** of the findings are in repos with
    nothing to cover with. (It was 220/134 earlier the same day; the whole
    delta is this repo's own close-outs. **86 does not move**, because the
    nine no-suite repos did not.) The 236/147 pair is a wider terminal set and
    is NOT this rule's number.
    """
    assert _findings(_repo(tmp_path, suite=False, status="done")) == 0


def test_it_warns_and_never_errors(tmp_path: Path) -> None:
    """**Undated, deliberately** ([[ADR-0011]] clause 3). The debt is **139**
    in suite-bearing repos under the rule as it ships (2026-08-20). A date would either fail
    every build on arrival or be moved when it did, and a promotion nobody
    intends to honour teaches people to ignore the table.
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
        "the rule has been dated; 139 outstanding findings is not a promise"
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


# ---- the rule is a LIFECYCLE rule, so it lives upstream (REQ-0051 c5) -----

UPSTREAM = Path.home() / "Dev" / "repos" / "project-os"
UPSTREAM_VALIDATOR = UPSTREAM / "tools" / "scripts" / "validate-docs.py"


def _upstream_findings(repo: Path) -> int:
    out = subprocess.run(
        [sys.executable, str(UPSTREAM_VALIDATOR), "--repo-root", str(repo)],
        capture_output=True, text=True).stdout
    return out.count("FEATURE-UNCOVERED")


def test_the_rule_runs_in_the_template_repo_and_not_only_here(tmp_path: Path) -> None:
    """[[REQ-0051]] criterion 5: *"the rule lands upstream in project-os, not
    only here — it is a lifecycle rule for every repo."*

    **Asserted by EXECUTION, not by grep.** A substring search for
    `FEATURE-UNCOVERED` in upstream's validator would be satisfied by a comment
    mentioning it — the over-broad text match that has bitten this phase seven
    times. So this drives upstream's validator over a constructed corpus and
    reads what it reports.

    `tools/scripts/` is `template`-owned in `tools/sync/MANIFEST.yaml`, so a
    fleet repo whose validator still matches the baseline receives this on its
    next sync; a diverged copy (this repo's, 720 lines ahead) is skipped and
    reported for hand-merge rather than clobbered.
    """
    if not UPSTREAM_VALIDATOR.is_file():                  # pragma: no cover
        raise AssertionError(
            "no upstream validator at %s — the rule cannot have landed there"
            % UPSTREAM_VALIDATOR)
    assert _upstream_findings(_repo(tmp_path, suite=True, status="done")) == 1


def test_upstream_recognises_coverage_too(tmp_path: Path) -> None:
    """The positive half, upstream. Case 5 of the six-case domain
    [[TASK-0523]] tabulates — measured when the port was written and asserted
    by nothing, in the note that called the domain *"enumerated rather than
    sampled"*. Enumerating a domain and guarding it are two different acts.
    """
    repo = _repo(tmp_path, suite=True, status="done", covers='"[[FEAT-0001]]"')
    assert _upstream_findings(repo) == 0


def test_upstream_is_silent_where_there_is_nothing_to_cover_with(tmp_path: Path) -> None:
    """The other half of the same claim, and the half a rule that fires
    unconditionally would still pass: nine of the twelve fleet repos hold no
    acceptance check, and upstream itself is one of them — it reports **zero**
    against its own docs.
    """
    assert _upstream_findings(_repo(tmp_path, suite=False, status="done")) == 0


def test_the_escape_is_the_same_field_upstream(tmp_path: Path) -> None:
    """A rule whose escape differs between repos is an escape nobody can use.
    Executed rather than grepped, for the same reason as above.
    """
    repo = _repo(tmp_path, suite=True, status="done",
                 exception="a phase of work, not a user-facing surface")
    assert _upstream_findings(repo) == 0


def test_the_upstream_template_and_schema_carry_the_escape() -> None:
    """The field has to be scaffolded and *documented* upstream, or the rule
    names a field a downstream author cannot find. `SCHEMAS.md` is the file the
    author reads; the template is the file they get.
    """
    fm = (UPSTREAM / "docs" / "__templates__" / "feature.md").read_text(encoding="utf-8")
    assert 'acceptance_exception: ""' in fm
    schemas = (UPSTREAM / "docs" / "__templates__" / "SCHEMAS.md").read_text(encoding="utf-8")
    feature_section = schemas[schemas.index("## `feature.md`"):]
    feature_section = feature_section[:feature_section.index("\n## ")]
    assert "acceptance_exception" in feature_section, (
        "the escape is not documented in the feature section of upstream's "
        "SCHEMAS.md, so the rule names a field the schema does not"
    )


# ---- the scaffold end of the same rule (TASK-0522) ------------------------

SCAFFOLD = ROOT / "tools" / "skills" / "feature-scaffold" / "SKILL.md"
FEATURE_TEMPLATE = ROOT / "docs" / "__templates__" / "feature.md"


def test_the_scaffold_emits_a_check_by_rule_not_by_judgement() -> None:
    """[[TASK-0522]]. Step 9 read *"if the feature requires verification"* — a
    judgement made per feature, at the end, by whoever was tired.

    Measured across the twelve project-os repos on 2026-08-20: **225 features
    reached `done` with no acceptance check covering them** (220 earlier the
    same day, before this phase's own close-outs). A rule applied when somebody remembers is not a rule.
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


def test_a_non_acceptance_test_is_not_coverage(tmp_path: Path) -> None:
    """`_features_covered_by_acceptance` must read `level: acceptance` only.

    **Proved by mutant, by independent review**: dropping the level filter
    passes every other test in this file and **silences 29 findings in this
    repo** — re-measured 2026-08-20 at 94 findings against 65, still exactly
    29, so the figure is stable while the base is not — — a non-acceptance `TST-*` naming a terminal feature would count
    as coverage, and the rule would report silence on features nothing verifies
    in the sense it means.

    No fixture constructed this before, which is why the hole survived: every
    other case here uses an acceptance note or none at all.
    """
    docs = tmp_path / "docs"
    (docs / "features" / "f").mkdir(parents=True)
    (docs / "tests" / "acceptance").mkdir(parents=True)
    (tmp_path / "SNAPSHOT.yaml").write_text(
        'version: 1\nproject:\n  name: "t"\n  repo_root: "."\n'
        "counters:\n  FEAT: 1\n  TST: 2\nitems: {}\n", encoding="utf-8")
    (docs / "features" / "f" / "FEAT-0001-Thing.md").write_text(
        '---\ntype: "[[feature]]"\nid: FEAT-0001\ntitle: "Thing"\n'
        'status: done\n---\n\n# Thing\n', encoding="utf-8")
    #: The suite exists, so the rule is switched on…
    (docs / "tests" / "acceptance" / "TST-0002-Other.md").write_text(
        '---\ntype: "[[test]]"\nid: TST-0002\ntitle: "Other"\n'
        'level: acceptance\nstatus: active\narea: "A"\nmark: todo\n'
        'covers: []\n---\n\n# Other\n', encoding="utf-8")
    #: …and this covers the feature but is NOT an acceptance check.
    (docs / "tests").joinpath("TST-0001-Unit.md").write_text(
        '---\ntype: "[[test]]"\nid: TST-0001\ntitle: "Unit"\n'
        'status: passing\ncommand: "pytest -q"\n'
        'covers: ["[[FEAT-0001]]"]\n---\n\n# Unit\n', encoding="utf-8")

    assert _findings(tmp_path) == 1, (
        "a non-acceptance test is being counted as acceptance coverage, so "
        "FEATURE-UNCOVERED reports silence on a feature nothing verifies in "
        "the sense the rule means"
    )
