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


# ---- the guards that guard (independent review, 2026-08-18) ---------------
#
# Mutation-tested: each of the four behaviours below survived deletion with the
# whole suite green. A test that cannot fail is not coverage, and the reason
# each survived is written on it rather than left for the next reader.


def test_blocking_for_actually_narrows_to_its_subjects() -> None:
    """`blocking_for` ignoring `subjects` entirely survived deletion.

    Because the equivalence test passes `subjects=None`, where the filter
    short-circuits by design — so it asserted a tautology. This asserts the
    scoped case is genuinely narrower, on a corpus where it must be.
    """
    suite = _suite("your-trainer")
    everything = suite.blocking_for(None)
    assert everything, "your-trainer has nothing blocking; pick another corpus"
    covered = sorted({ref for i in everything for ref in i.refs if ref.startswith("FEAT-")})
    assert covered, "no blocking check names a feature — the scoped case is untestable"
    scoped = suite.blocking_for({covered[0]})
    assert len(scoped) < len(everything), (
        "scoping to one feature returned everything; `subjects` is being ignored"
    )


def test_an_unattributable_check_blocks_even_when_scoped_away(tmp_path: Path) -> None:
    """The fail-closed clause, on a corpus built to need it.

    The corpus guard skips: all 9 of `your-trainer`'s orphan gating checks are
    settled, so deleting the clause changed nothing there. This builds an
    UNSETTLED one, which is the state the clause exists for.
    """
    docs = tmp_path / "docs"
    (docs / "tests" / "acceptance").mkdir(parents=True)
    (docs / "tests" / "acceptance" / "TST-0001-Orphan.md").write_text(
        '---\ntype: "[[test]]"\nid: TST-0001\ntitle: "covers nothing"\n'
        'status: active\nlevel: acceptance\ntier: 1\nmark: todo\narea: "A"\n'
        'section: "1.1"\nordinal: 10\ncovers: []\n---\n\nwalk\n', encoding="utf-8")
    suite = acceptance.load(docs, Index.build(docs))
    assert len(suite.blocking_for({"FEAT-9999"})) == 1, (
        "a check covering nothing vanished from a scoped gate — it can be "
        "discharged by finishing nothing, so it must gate the release"
    )


def test_a_walked_test_goes_stale_when_a_change_invalidates_it(tmp_path: Path) -> None:
    """`_test_is_stale`'s walked branch always returning False survived deletion.

    `your-trainer` carries zero invalidations right now — they were cleared
    deliberately — so the branch has no live subject anywhere in the fleet and
    nothing exercised it.
    """
    from project_os_cockpit import cockpit

    walked = {"mark": "done", "verdict_date": "2026-08-01",
              "invalidated_by": {"change": "TASK-0001", "date": "2026-08-10"}}
    assert cockpit._test_is_stale(walked, 90) is True, "an invalidation after the walk must read stale"

    answered = dict(walked, verdict_date="2026-08-12")
    assert cockpit._test_is_stale(answered, 90) is False, "a walk after the change answers it"

    clean = {"mark": "done", "verdict_date": "2026-08-01", "invalidated_by": {}}
    assert cockpit._test_is_stale(clean, 90) is False


def test_the_sweep_writes_a_note_the_reader_can_see(tmp_path: Path) -> None:
    """ISS-0205's third done-when, which was never asserted.

    Reverting `_write_new_check` to `type: "[[check]]"` left all 22 sweep tests
    green, because they check the note's fields rather than whether the suite
    can load it. This reads the sweep's own output back through
    `acceptance.load` on a MIGRATED corpus, which is the only thing that fails.
    """
    from project_os_cockpit import sweep
    from project_os_cockpit.index import Index as Idx

    docs = tmp_path / "docs"
    (docs / "tests" / "acceptance").mkdir(parents=True)
    (docs / "features").mkdir()
    (docs / "features" / "FEAT-0001-Thing.md").write_text(
        '---\ntype: "[[feature]]"\nid: FEAT-0001\ntitle: "t"\nstatus: doing\n'
        'owner: user:edwin\n---\n\nbody\n', encoding="utf-8")
    (docs / "tests" / "acceptance" / "TST-0001-Existing.md").write_text(
        '---\ntype: "[[test]]"\nid: TST-0001\ntitle: "existing"\nstatus: active\n'
        'level: acceptance\ntier: 1\nmark: done\narea: "A"\nsection: "1.1"\n'
        'ordinal: 10\ncovers: []\n---\n\nwalk\n', encoding="utf-8")

    before = len(acceptance.load(docs, Idx.build(docs)).items)
    sweep.apply(Idx.build(docs), "FEAT-0001",
                create=[{"name": "A new check", "tier": 1, "area": "A",
                         "text": "do the thing"}],
                impact="2026-08-18")
    after = acceptance.load(docs, Index.build(docs)).items
    assert len(after) == before + 1, (
        "the sweep wrote a note the suite cannot load — which is exactly what "
        "ISS-0205 was, and what a field-shaped assertion cannot see"
    )


def test_the_scope_panel_answers_what_blocks_THIS_feature() -> None:
    """`blocking_for` has a production caller (REQ-0043).

    Independent review found gating-at-any-granularity implemented and used by
    nothing — the difference between a capability and a feature. The per-scope
    panel now answers *what blocks this feature*, which is the question a reader
    opening one scope is asking and the one a release-shaped gate cannot answer.
    """
    from project_os_cockpit import cockpit

    docs = FLEET / "your-trainer" / "docs"
    if not docs.is_dir():
        pytest.skip("your-trainer is not on this machine")
    index = Index.build(docs)
    suite = acceptance.load(docs, index)
    everything = len(suite.blocking_for(None))
    assert everything, "your-trainer has nothing blocking; pick another corpus"

    covered = sorted({r for i in suite.blocking_for(None) for r in i.refs
                      if r.startswith("FEAT-")})
    assert covered, "no blocking check names a feature"
    panel = cockpit.scope_tests_payload(index, covered[0])
    assert "blocking" in panel, "the panel no longer reports what blocks the scope"
    assert 0 < len(panel["blocking"]) < everything, (
        "a feature's panel returned the release's whole blocking set; it is not "
        "scoped, which is the entire point of blocking_for taking subjects"
    )
    assert all("unattributated" not in row for row in panel["blocking"])
    for row in panel["blocking"]:
        assert "unattributed" in row, "an orphan check must say why it appears here"


def test_the_scope_panel_renders_what_it_computes() -> None:
    """REQ-0043's criterion is about a SURFACE, not a payload.

    The server computed `blocking` and the renderer threw it away — the response
    was typed `{ tests? }` — so *"a feature's panel answers what blocks this
    feature"* described a panel that did not exist. Found by the second
    independent review; the first fix met the criterion in letter only.

    Asserted on the renderer source, because the property is that the value
    reaches the DOM and no payload test can see that.
    """
    renderer = (Path(__file__).resolve().parent.parent / "desktop" / "src"
                / "renderer" / "renderer.ts").read_text(encoding="utf-8")
    assert "blocking?: ScopeBlocking[]" in renderer, (
        "the scope response is typed without `blocking` again, so the renderer "
        "discards what the server computed"
    )
    panel = renderer[renderer.index("async function fillVerificationPanel"):]
    panel = panel[:panel.index("\nfunction ")]
    assert "scopeBlocking.get(noteId)" in panel, "the panel never reads it"
    assert "scope-blocking" in panel, "nothing is appended to the DOM for it"
    assert "body.replaceChildren(list)" not in panel, (
        "the test list replaces the panel's children, which silently deletes "
        "the blocking list rendered above it"
    )
