"""Scoped palette parity (TASK-0219).

Narrow on purpose. An earlier draft of FEAT-0042 claimed this check justified
building the design bench at all; independent review refuted that, and the
evidence is in the founding artifact — DES-0001 names its tokens `--m-done` /
`--t-feature` against an implementation saying `--status-done` /
`--severity-critical`. A general token comparison would need a name mapping,
and a hand-maintained mapping is the drift surface one level up.

What survives is real: a design that declares status colours must agree with
`statuses.py`-derived CSS, with the implementation upstream.
"""

from __future__ import annotations

from pathlib import Path

from project_os_cockpit import design_tokens as dt

STATIC = Path(__file__).resolve().parents[1] / "src" / "project_os_cockpit" / "static"
DOCS = Path(__file__).resolve().parents[1] / "docs"

IMPL = """
:root {
  --status-done: hsl(160 28% 38%);
  --status-blocked: hsl(5 48% 46%);
  --severity-critical: hsl(5 60% 46%);
  --accent-link: hsl(212 48% 42%);
}
@media (prefers-color-scheme: dark) {
  :root { --status-done: hsl(160 28% 60%); }
}
"""


def test_first_declaration_wins_so_schemes_are_not_crossed() -> None:
    """A stylesheet declares each token once per scheme. Taking the last would
    compare a design's light palette against the implementation's dark one —
    the exact bug that shipped in the family-palette check earlier today and
    reported a divergence that did not exist."""
    tokens = dt.read_tokens(IMPL)
    assert tokens["--status-done"] == "hsl(160 28% 38%)", (
        "took the dark-scheme value; anyone following that would 'fix' the "
        "design to match the wrong scheme"
    )


def test_only_scoped_families_are_read() -> None:
    tokens = dt.read_tokens(IMPL)
    assert set(tokens) == {"--status-done", "--status-blocked", "--severity-critical"}
    assert "--accent-link" not in tokens, (
        "an accent is the project's business, not a shared vocabulary"
    )


def test_agreement_is_reported_as_agreement() -> None:
    design = ":root { --status-done: hsl(160 28% 38%); }"
    result = dt.compare(design, IMPL)
    assert result["agree"] == ["--status-done"]
    assert not result["diverged"] and not result["unknown"]


def test_a_drifted_value_is_caught() -> None:
    design = ":root { --status-done: hsl(160 28% 39%); }"
    result = dt.compare(design, IMPL)
    assert result["diverged"] == [{
        "token": "--status-done",
        "design": "hsl(160 28% 39%)",
        "implementation": "hsl(160 28% 38%)",
    }]


def test_whitespace_does_not_count_as_divergence() -> None:
    design = ":root { --status-done:   hsl(160  28%  38%) ; }"
    assert dt.compare(design, IMPL)["diverged"] == []


def test_a_different_colour_space_IS_reported() -> None:
    """Deliberately not normalised across spaces. A design in hex against an
    implementation in hsl means one was retyped from the other, which is the
    retyping this check exists to catch."""
    design = ":root { --status-done: #467A66; }"
    assert len(dt.compare(design, IMPL)["diverged"]) == 1


def test_a_token_the_implementation_lacks_is_unknown_not_diverged() -> None:
    """A design proposing a NEW status is a legitimate thing for a design to
    do; reporting it as a failure would punish the use case."""
    design = ":root { --status-experimental: hsl(300 40% 50%); }"
    result = dt.compare(design, IMPL)
    assert result["unknown"] == [{"token": "--status-experimental",
                                  "design": "hsl(300 40% 50%)"}]
    assert not result["diverged"]


def test_a_design_declaring_no_scoped_tokens_is_silent(tmp_path: Path) -> None:
    """Most designs specify a surface, not a palette. Demanding tokens from
    all of them would make this check noise."""
    docs = tmp_path / "docs" / "designs"
    docs.mkdir(parents=True)
    (docs / "a.html").write_text(":root{--m-done:#123456;--paper:#fff}", encoding="utf-8")
    assert dt.check_design_assets(tmp_path / "docs", STATIC) == {}


def test_the_real_implementation_is_self_consistent() -> None:
    """Against the shipped CSS, not a fixture: every scoped token the cockpit
    declares agrees with itself, which is what makes it usable as upstream."""
    impl = (STATIC / "base.css").read_text(encoding="utf-8")
    tokens = dt.read_tokens(impl)
    assert len(tokens) >= 11, "expected the status bands and severity steps"
    assert dt.compare(impl, impl)["diverged"] == []


def test_the_real_corpus_declares_no_scoped_tokens_yet() -> None:
    """Recorded as a fact rather than asserted as success. DES-0001 uses
    `--m-*`/`--t-*` names, so this check is silent on the only artifact in the
    repo — which is precisely the gap the authoring contract exists to close
    for the NEXT design, and why the parity claim was demoted from 'the reason
    to build this' to 'a real, narrow check'."""
    results = dt.check_design_assets(DOCS, STATIC)
    assert results == {}, (
        "a design now declares scoped tokens — good; update this test to "
        "assert it AGREES rather than that none exist"
    )
