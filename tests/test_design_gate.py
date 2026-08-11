"""DESIGN-GATE: a feature past planning whose design was never accepted.

*Design before code* is PHASE-025's title, and this is the only mechanical part
of it. A **warning**, on the same reasoning as ACCEPT-STALE and independent
review: the judgment being gated — *is this design right?* — cannot be
automated, and a blocking gate on it gets cleared to unblock the build rather
than because somebody looked.

The satisfied set is the interesting part. The first cut required exactly
`accepted` and fired **five false positives on the live corpus immediately**,
every one a design that had progressed to `implemented`. A nag that fires
wrongly teaches people to ignore it — which is the whole reason this warns
instead of blocking, so getting it wrong here would have been self-defeating.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
VALIDATOR = REPO / "tools" / "scripts" / "validate-docs.py"


def _run(root: Path) -> str:
    proc = subprocess.run(
        [sys.executable, str(VALIDATOR), "--repo-root", str(root)],
        capture_output=True, text=True, check=False,
    )
    return proc.stdout + proc.stderr


def _corpus(root: Path, *, feature_status: str, design_status: str) -> None:
    (root / "docs" / "features" / "thing").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "designs").mkdir(parents=True, exist_ok=True)
    (root / "SNAPSHOT.yaml").write_text(
        "project:\n  name: demo\nitems:\n  features:\n    FEAT-9001:\n"
        f'      status: {feature_status}\n', encoding="utf-8",
    )
    (root / "docs" / "features" / "thing" / "FEAT-9001-Thing.md").write_text(
        f'---\ntype: "[[feature]]"\nid: FEAT-9001\naliases: ["FEAT-9001"]\n'
        f'title: "Thing"\nstatus: {feature_status}\ndesign: "[[DES-9001]]"\n'
        f"---\n\n# Thing\n", encoding="utf-8",
    )
    (root / "docs" / "designs" / "DES-9001-Shape.md").write_text(
        f'---\ntype: "[[design]]"\nid: DES-9001\naliases: ["DES-9001"]\n'
        f'title: "Shape"\nstatus: {design_status}\n---\n\n# Shape\n',
        encoding="utf-8",
    )


@pytest.mark.parametrize("design_status", ["draft", "proposed", "cancelled"])
def test_it_warns_when_the_design_was_never_accepted(tmp_path: Path, design_status: str) -> None:
    _corpus(tmp_path, feature_status="doing", design_status=design_status)
    out = _run(tmp_path)
    assert "DESIGN-GATE" in out, out
    assert "FEAT-9001" in out


@pytest.mark.parametrize("design_status", ["accepted", "implemented", "superseded"])
def test_it_is_silent_once_the_design_was_accepted(tmp_path: Path, design_status: str) -> None:
    """`accepted -> implemented` is the normal progression and `superseded`
    means a later design replaced one that had been accepted. Requiring exactly
    `accepted` produced five false positives on the live corpus."""
    _corpus(tmp_path, feature_status="doing", design_status=design_status)
    assert "DESIGN-GATE" not in _run(tmp_path)


@pytest.mark.parametrize("feature_status", ["backlog", "planned", "deferred"])
def test_a_pending_feature_is_not_gated(tmp_path: Path, feature_status: str) -> None:
    """Naming a design you have not accepted yet is the normal state of
    planning; warning about it would fire on every feature as it was written."""
    _corpus(tmp_path, feature_status=feature_status, design_status="draft")
    assert "DESIGN-GATE" not in _run(tmp_path)


def test_a_design_that_is_not_in_the_corpus_is_reported(tmp_path: Path) -> None:
    """A dangling `design:` is worse than an unaccepted one — nothing to read."""
    _corpus(tmp_path, feature_status="doing", design_status="accepted")
    (tmp_path / "docs" / "designs" / "DES-9001-Shape.md").unlink()
    out = _run(tmp_path)
    assert "DESIGN-GATE" in out and "not in the corpus" in out


def test_the_live_corpus_is_quiet() -> None:
    """Zero is the assertion. The first cut warned five times here, and a
    warning that fires wrongly is the failure this whole gate is shaped to
    avoid."""
    out = _run(REPO)
    hits = [ln for ln in out.splitlines() if "DESIGN-GATE" in ln]
    assert not hits, "DESIGN-GATE fires on the live corpus:\n  " + "\n  ".join(hits)


# ---------------------------------------------------------------------------
# TASK-0310 — deriving requirements from an accepted design
# ---------------------------------------------------------------------------


def test_derive_is_offered_only_on_an_accepted_design() -> None:
    """An unaccepted design has nothing to derive FROM.

    Offering it earlier invites deriving requirements from a shape nobody
    agreed to — which is the failure `design before code` exists to prevent,
    arrived at from the other direction.
    """
    from project_os_cockpit import agent_actions

    verbs = agent_actions.DEFAULT_ACTIONS["design"]
    derive = next(v for v in verbs if v["key"] == "derive")
    # `when` is the gate the renderer filters on — asserted as data rather
    # than by calling a resolver, because the registry IS the contract.
    assert derive["when"] == ["accepted"], derive["when"]


def test_derive_dispatches_and_never_writes_requirement_text() -> None:
    """FEAT-0051's rule: no REQ text is generated without the dispatch.

    The cockpit's job here is to compose a prompt and hand it to an agent. If
    this verb ever grew a code path that wrote requirement prose directly, the
    tool would be authoring the specification it is meant to render.
    """
    from project_os_cockpit import agent_actions

    derive = next(
        v for v in agent_actions.DEFAULT_ACTIONS["design"] if v["key"] == "derive"
    )
    prompt = derive["prompt"]
    assert "impact-analysis" in prompt and "feature-scaffold" in prompt, prompt
    assert "status: draft" in prompt or "`status: draft`" in prompt
    # And it must forbid self-approval explicitly — a requirement the tool
    # approved for itself is not one anybody agreed to.
    assert "Do NOT approve" in prompt, prompt
