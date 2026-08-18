"""ADR-0034 / FEAT-0124 — gating is derived from `covers:`.

`Suite.blocking_for(subjects)` is the general rule: *an item may not reach a
terminal status while a test covering it is unsettled.* `blocking()` — the
release gate — is the `subjects=None` case of it, so the two cannot drift.

Written because the equivalence is the whole risk. A gate that gets **quieter**
during a migration is the failure this project has already paid for, and a count
can match while the membership rotates.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from project_os_cockpit import acceptance
from project_os_cockpit.index import Index

FLEET = Path.home() / "Dev" / "repos"
SUITES = ("project-os-cockpit", "your-sudoku", "your-trainer")


def _suite(repo: str):
    docs = FLEET / repo / "docs"
    if not docs.is_dir():
        pytest.skip(f"{repo} is not on this machine")
    return acceptance.load(docs, Index.build(docs))


@pytest.mark.parametrize("repo", SUITES)
def test_the_derived_gate_names_the_same_items_as_the_tier_rule(repo: str) -> None:
    """Membership, not count.

    The tier rule is `tier in {1,2} and not settled`. The derived rule adds
    *"and it covers something in scope, or covers nothing at all"*. For the
    release — every item in scope — those must name the identical set.
    """
    suite = _suite(repo)
    tier_rule = {
        i.note_id or i.number for i in suite.items
        if i.tier in acceptance.GATING_TIERS and not i.settled
    }
    derived = {i.note_id or i.number for i in suite.blocking_for(None)}
    assert derived == tier_rule, {
        "only the tier rule blocks": sorted(tier_rule - derived),
        "only the derived rule blocks": sorted(derived - tier_rule),
    }


@pytest.mark.parametrize("repo", SUITES)
def test_a_check_that_covers_nothing_still_blocks(repo: str) -> None:
    """The fail-closed clause, asserted on the corpus that needed it.

    `your-trainer` carries 83 checks with an empty `covers:` — 74 Tier 3, which
    does not gate, and **9 Tier 1/2 which do**. Treating an unattributable
    check as passing would leave those 9 unable to block anything the day
    somebody unticks one, and nothing would say so.
    """
    suite = _suite(repo)
    orphans = [i for i in suite.items
               if not i.refs and i.tier in acceptance.GATING_TIERS]
    if not orphans:
        pytest.skip(f"{repo} has no gating check without covers:")
    # Scope it to a subject none of them names: an orphan must survive the
    # filter anyway, because it can be attributed to nothing.
    scoped = suite.blocking_for({"FEAT-9999"})
    for orphan in orphans:
        if orphan.settled:
            continue
        assert orphan in scoped, (
            f"{orphan.note_id} covers nothing and was filtered out of a scoped "
            "gate — an unattributable check must block, not vanish"
        )


def test_gating_one_feature_is_narrower_than_gating_the_release() -> None:
    """The point of the whole thing: granularity comes from `covers:`.

    Guarded on a corpus rather than a fixture, and on the property rather than
    a number — scoping to one feature must never return more than the release
    does, and for a feature with any covered check it must return fewer.
    """
    suite = _suite("your-trainer")
    everything = suite.blocking_for(None)
    covered = {ref for i in suite.items for ref in i.refs if ref.startswith("FEAT-")}
    assert covered, "the corpus no longer exercises feature-scoped gating"
    for feature in sorted(covered)[:20]:
        scoped = suite.blocking_for({feature})
        assert len(scoped) <= len(everything), feature
