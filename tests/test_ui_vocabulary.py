"""No user-visible string says *run* or *walk* (TASK-0572).

Edwin, 2026-08-19: *"stop calling it walking"*, then *"Don't use run either"*,
then *"complete is also an option"* — the verbs are **do, execute, check,
complete**. And on the scope: *"You can leave run in the docs but don't use it
in the UI."*

**This is a guard because the rule has already failed twice without one.**
DES-0012 D5 retired *walk* in favour of `Run`; the word came back in the nav,
in the generated page's tally, and — on 2026-08-19 — eighteen times into two
brand-new decision records, one of them in the title. A vocabulary rule with no
check is a preference.

Deliberately narrow, and the narrowness is the point:

* **Identifiers are untouched.** `run-tests.py`, `last_run:`, the `test-run`
  endpoint, `runner`, `rerun` as a mark value — these are names in a contract,
  and renaming a schema field to fix a label is a much larger change than the
  one Edwin asked for.
* **Documents are untouched.** 1016 occurrences in `docs/` stay, by his
  instruction. What a note says about a run is not what a button says.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from project_os_cockpit.index import Index
from project_os_cockpit import cockpit

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS = REPO_ROOT / "docs"

_BANNED = re.compile(r"\b(run|runs|running|re-?run|walk|walks|walked|walking)\b", re.I)

#: A label carrying a project-os id was composed with a note's own title.
_NAMES_A_NOTE = re.compile(r"\b(FEAT|ISS|TASK|REQ|TST|PHASE|ADR|CHG|DES|REL|RISK)-\d+")

#: **Chrome, not content.** The keys the PRODUCT writes — a group heading, a
#: band name, a tally. Everything else in a payload is a note's own words:
#: `title` is the author's, and so is `subtitle`, which carries issue prose
#: like *"a check leaves the manual walk for three reasons"* straight from
#: ISS-0238. Renaming what the product says is Edwin's instruction; rewriting
#: what a note says is not, and 1016 occurrences in `docs/` stay by his
#: explicit decision.
_CHROME_KEYS = frozenset({"label", "heading", "band", "caption", "empty", "hint"})


def _labels(node, *, path="") -> list[tuple[str, str]]:
    """Every string the product itself authored, with where it came from."""
    out: list[tuple[str, str]] = []
    if isinstance(node, dict):
        for key, value in node.items():
            if key in _CHROME_KEYS and isinstance(value, str):
                out.append((f"{path}.{key}", value))
            else:
                out.extend(_labels(value, path=f"{path}.{key}"))
    elif isinstance(node, list):
        for i, value in enumerate(node):
            out.extend(_labels(value, path=f"{path}[{i}]"))
    return out


@pytest.fixture(scope="module")
def index() -> Index:
    return Index.build(DOCS)


@pytest.mark.parametrize("mode", ["tests", "publication", "features", "issues"])
def test_no_nav_label_says_run_or_walk(index: Index, mode: str) -> None:
    payload = cockpit.nav_payload(index, mode=mode)
    labels = _labels(payload)
    assert labels, f"no chrome reached the {mode} payload — this would pass vacuously"
    offenders = [
        (path, text) for path, text in labels
        # **A label that NAMES a note carries that note's words.** The phase
        # groups render as `PHASE-027 · <the phase's own title>`, and
        # PHASE-027's title contains *"a project runs without its human"* —
        # the author's sentence, reached through a chrome key. Rewriting it
        # would be editing the record to satisfy a UI rule.
        if not _NAMES_A_NOTE.search(text) and _BANNED.search(text)
    ]
    assert not offenders, offenders


def test_the_group_that_asks_is_called_needs_you(index: Index) -> None:
    """The name every other view uses (ADR-0025), and no verb at all.

    `Needs a run` was the one place the Tests view differed, and it differed
    because a more specific name *"says more than needs you"* — which Edwin
    overruled in favour of consistency.
    """
    labels = {g["label"] for g in cockpit.nav_payload(index, mode="tests")["groups"]}
    assert not any("Needs a run" in x for x in labels)
    groups = cockpit._tests_groups(index)
    keys = {g["key"] for g in groups}
    assert "needs-run" not in keys


def test_the_mark_vocabulary_reads_re_check(index: Index) -> None:
    from project_os_cockpit import acceptance
    assert acceptance.MARK_MEANING["rerun"] == "needs re-check"
    # The mark VALUE is untouched: it is a contract with every note in the
    # fleet, and renaming it to fix a label is a migration, not a label change.
    assert "rerun" in acceptance.MARK_MEANING
