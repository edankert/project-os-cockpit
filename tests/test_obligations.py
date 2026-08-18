"""TASK-0369 — the obligation registry, enumerated by note type.

The point of these is that the **corpus supplies the checklist**. A list of
obligation kinds written by hand was wrong three times in one day; a list
checked against the types the notes actually use cannot be.
"""

from __future__ import annotations

from pathlib import Path

from project_os_cockpit import obligations, statuses
from project_os_cockpit.index import Index

REPO = Path(__file__).resolve().parents[1]


def _corpus_types() -> set[str]:
    index = Index.build(REPO / "docs")
    return {
        r.note_type for p in index.paths()
        if (r := index.get(p)) and r.note_type
        and not r.rel_path.startswith("__templates__/")
    }


def test_every_type_in_the_corpus_is_declared() -> None:
    """**The completeness guarantee.**

    This is what would have caught `change`, `release`, `risk`, `workflow` and
    `phase` without anyone asking. A type present in the notes with no entry
    is a failure here rather than something somebody has to notice.
    """
    undeclared = _corpus_types() - obligations.declared_types()
    assert not undeclared, (
        f"types in the corpus with no obligation declaration: {sorted(undeclared)}"
    )


def test_every_none_carries_its_reason() -> None:
    """An unexplained absence is exactly what an omission looks like.

    `task` (381 notes) and `plan` (52) owe nothing, correctly — and that is
    indistinguishable from a forgotten entry unless the reason is written.
    """
    for note_type, ob in obligations.OBLIGATIONS.items():
        if ob.owed:
            continue
        assert ob.reason.strip(), f"{note_type} declares `none` without a reason"
        assert len(ob.reason) > 40, (
            f"{note_type}'s reason is too thin to be checkable: {ob.reason!r}"
        )


def test_every_owed_kind_names_one_view_and_a_verb() -> None:
    """One type, one owning view — otherwise the badges count it twice."""
    for note_type, ob in obligations.owed_kinds().items():
        assert ob.view in obligations.VIEWS, f"{note_type} names view {ob.view!r}"
        assert ob.verb, f"{note_type} owes something with no verb a human can read"
        assert ob.states or ob.predicate, (
            f"{note_type} owes something but says nothing about when"
        )


def test_no_state_is_outside_the_status_vocabulary() -> None:
    """The ISS-0023 rule, applied to a third table."""
    for note_type, ob in obligations.OBLIGATIONS.items():
        for state in ob.states:
            assert state in statuses.VOCABULARY, (
                f"{note_type} is owed at {state!r}, which is not a status"
            )


def test_no_close_out_status_makes_something_owed() -> None:
    """A terminal note owes nobody anything, by construction."""
    for note_type, ob in obligations.OBLIGATIONS.items():
        for state in ob.states:
            assert not statuses.is_completed(state), (
                f"{note_type} is owed at the terminal status {state!r}"
            )


def test_the_four_ISS_0128_answers_are_recorded() -> None:
    """Each was a decision a test could not make, so the test asserts they
    were made — and that the reasoning survived, not just the verdict."""
    reg = obligations.OBLIGATIONS
    assert not reg["risk"].owed and reg["risk"].view == obligations.VIEW_INTENT
    assert "resting state" in reg["risk"].reason
    assert not reg["workflow"].owed and "TOOLING" in reg["workflow"].reason
    assert not reg["phase"].owed and "PROCEDURE" in reg["phase"].reason
    for note_type in ("risk", "workflow", "phase"):
        assert "ISS-0128" in reg[note_type].reason, (
            f"{note_type}'s reason does not cite where it was decided"
        )


def test_the_payload_carries_no_vocabulary_a_renderer_must_restate() -> None:
    p = obligations.payload()
    assert p["kinds"] and p["none"]
    for kind in p["kinds"]:
        assert kind["verb"] and kind["view"]
    for none in p["none"]:
        assert none["reason"]


def test_removing_a_kind_removes_it_from_every_view() -> None:
    """Nothing downstream keeps its own list."""
    before = set(obligations.views_owed()["issues"])
    assert "issue" in before
    saved = obligations.OBLIGATIONS["issue"]
    try:
        obligations.OBLIGATIONS["issue"] = obligations.NONE(
            "temporarily removed by a test to prove nothing else remembers it",
            obligations.VIEW_ISSUES,
        )
        assert "issue" not in obligations.views_owed()["issues"]
        assert "issue" not in obligations.owed_kinds()
    finally:
        obligations.OBLIGATIONS["issue"] = saved


# ---- the badges (TASK-0370) -------------------------------------------


def test_the_badges_sum_to_the_registry_total() -> None:
    """ADR-0020 decision 3: the badges must cover **every** kind.

    A total that disagrees with the sum is exactly how a kind goes missing
    without anyone noticing — which is the defect this whole feature exists
    to remove, so it is asserted rather than assumed.
    """
    index = Index.build(REPO / "docs")
    payload = obligations.badges_payload(index)
    assert payload["total"] == sum(payload["views"].values())


def test_every_owed_note_lands_in_exactly_one_view() -> None:
    """One type, one view. Counting a note twice is as wrong as missing it."""
    index = Index.build(REPO / "docs")
    seen: dict[str, str] = {}
    for path in index.paths():
        record = index.get(path)
        if record is None or not record.note_type:
            continue
        if record.rel_path.startswith("__templates__/"):
            continue
        ob = obligations.for_type(record.note_type)
        if ob is None or not obligations._is_owed(record, ob):
            continue
        key = record.note_id or record.rel_path
        assert key not in seen, f"{key} counted in two views"
        seen[key] = ob.view


def test_nothing_owed_by_a_type_declaring_none() -> None:
    """The `none` entries must not leak into a count through the predicate."""
    index = Index.build(REPO / "docs")
    for path in index.paths():
        record = index.get(path)
        if record is None or not record.note_type:
            continue
        ob = obligations.for_type(record.note_type)
        if ob is not None and not ob.owed:
            assert not obligations._is_owed(record, ob), (
                f"{record.note_id} owes something despite {record.note_type} "
                "declaring none"
            )


def test_the_renderer_reads_the_count_and_declares_no_kinds() -> None:
    """No vocabulary in TypeScript — the badge draws what it is sent.

    And it must not clamp: the change badge reads 81 in this corpus, which is
    real debt with a deadline. Hiding it in the renderer would be a display
    lying about a gate (ADR-0020 leaves the cutoff open as a parameter).
    """
    src = (
        REPO / "desktop" / "src" / "renderer" / "renderer.ts"
    ).read_text(encoding="utf-8")
    body = src[src.index("async function refreshObligationBadges"):]
    body = body[:body.index("\nfunction ")]
    assert "/api/cockpit/obligations" in body
    assert "n <= 0) return" in body, "the badge renders a zero"
    for clamp in ("Math.min(", "> 99", "'99+'"):
        assert clamp not in body, f"the badge clamps the count with {clamp}"
    for kind in ("triage", "draft", "proposed", "changes-requested"):
        assert f"'{kind}'" not in body, f"the renderer names the state {kind!r}"


def test_the_features_tree_marks_owed_rows_from_the_registry() -> None:
    """TASK-0376: the row says it is owed, and says so in the registry's word.

    Read from `obligations`, never re-derived — a row that decided for itself
    would drift from the badge counting it, which is one number disagreeing
    with itself on one screen.
    """
    from project_os_cockpit import cockpit

    index = Index.build(REPO / "docs")
    rows = []
    for group in cockpit.nav_payload(index, mode="features")["groups"]:
        for item in group["items"]:
            rows.append(item)
            rows.extend(item.get("children") or [])
    owed = [r for r in rows if r.get("owed")]
    assert owed, "nothing in the features tree is marked owed"
    for row in owed:
        assert row.get("owed_verb"), f"{row['id']} is owed with no verb"
        # **Either registry.** The features view carries a note-less obligation
        # too since TASK-0468 put the acceptance sweep there — a subject that
        # IS a note, but whose obligation is keyed on a MISSING field, which
        # the per-type table cannot express because a feature already has an
        # entry and one type carries one. Reading only `for_type` was not a
        # narrower assertion, it was an assumption about which view holds
        # which registry, and it expired the first time that changed.
        ob = obligations.for_type(row["type"])
        source = obligations.note_less_sources().get(row["type"])
        assert ob is not None or source is not None, (
            f"{row['id']} is owed as a {row['type']!r} — a kind declared in "
            "neither registry, so nothing validates its verb"
        )
        # **A verb the registry declares** — not necessarily the one keyed by
        # this row's TYPE. A feature can be owed two different things: `Accept`
        # under its own entry, and `Sweep` from the note-less source that asks
        # whether its acceptance impact was considered. The row shows one, and
        # which one is decided by `_owed_flag` (the type's first) — so the
        # property this can honestly assert is that the word came from the
        # registry rather than from the surface, which is TASK-0357's rule and
        # the whole reason the verb is not a string in the renderer.
        declared = {s.verb for s in obligations.note_less_sources().values()}
        declared |= {o.verb for o in obligations.OBLIGATIONS.values() if o.verb}
        # …plus the per-row verbs a note-less source may substitute (the
        # standing documents do: you cannot *confirm* a document nobody has
        # written — ISS-0153).
        declared |= set(obligations.STANDING_VERBS.values())
        assert row["owed_verb"] in declared, (row["id"], row["owed_verb"])


def test_the_badge_counts_notes_while_the_tree_counts_rows() -> None:
    """A requirement nests under **every** feature it specifies, so one owed
    note can be several rows. That is the pre-existing many-to-many edge, not
    a duplicate — and the badge counts notes, which is what "how many things
    do I have to do" means.

    Asserted because the two numbers differing looks like a bug until you know
    why, and the next person to see `5` beside eight highlighted rows deserves
    the explanation in a test rather than in a guess.
    """
    from project_os_cockpit import cockpit

    index = Index.build(REPO / "docs")
    rows = []
    for group in cockpit.nav_payload(index, mode="features")["groups"]:
        for item in group["items"]:
            rows.append(item)
            rows.extend(item.get("children") or [])
    owed_rows = [r for r in rows if r.get("owed")]
    distinct = {r["id"] for r in owed_rows}
    badge = obligations.badges_payload(index)["views"]["features"]
    assert badge == len(distinct), (
        f"badge {badge} disagrees with {len(distinct)} distinct owed notes"
    )
    assert len(owed_rows) >= len(distinct)


def test_the_breakdown_explains_the_badge_and_sums_to_it() -> None:
    """ISS-0133: the badge says WHAT it counts, and cannot contradict itself.

    The badge showed a bare number whose only gloss was `N items here need a
    person` — the same sentence under every view, naming no kind. The kinds
    have been registry data since this module replaced a hand-written list, so
    the breakdown is the badge's own explanation rather than a second source.

    Which makes the sum the thing to guard. A breakdown that disagrees with
    the count is worse than no breakdown: it is one number contradicting
    itself on one screen, the exact failure `badges_payload` exists to prevent
    (ADR-0020 decision 3).
    """
    index = Index.build(REPO / "docs")
    payload = obligations.badges_payload(index)
    views, breakdown = payload["views"], payload["breakdown"]

    for view, kinds in breakdown.items():
        assert sum(kinds.values()) == views[view], (
            f"{view}: breakdown {kinds} sums to {sum(kinds.values())}, "
            f"badge says {views[view]}"
        )
    # A view absent from the breakdown owes nothing — silence and zero agree.
    for view, count in views.items():
        if view not in breakdown:
            assert count == 0, f"{view} shows {count} with no breakdown to explain it"
    assert sum(sum(k.values()) for k in breakdown.values()) == payload["total"]


def test_every_owed_kind_can_name_itself_and_its_verb() -> None:
    """The sentence the badge builds needs both halves, for every kind.

    A kind reaching a badge with no noun renders as its raw type, and one with
    no verb renders as a count with no action — both are the old "items"
    problem wearing a narrower hat. Asserted over the registry rather than
    over today's corpus, so a kind added later fails here and not on screen.
    """
    payload = obligations.badges_payload(Index.build(REPO / "docs"))
    nouns, verbs = payload["nouns"], payload["verbs"]

    for kind in obligations.owed_kinds():
        assert kind in nouns, f"owed kind {kind!r} has no noun for the badge to say"
        singular, plural = nouns[kind]
        assert singular and plural, f"{kind!r} has an empty noun"
        assert kind in verbs and verbs[kind], f"owed kind {kind!r} has no verb"

    standing = obligations.STANDING_OBLIGATION_KIND
    assert standing in nouns and standing in verbs, (
        "the standing obligation is the one whose subject is not a note, so it "
        "is the one most likely to be left out of a per-kind vocabulary"
    )


def test_the_note_less_memo_cannot_outlive_its_corpus(tmp_path) -> None:
    """The memo lives on the index, never in a module dict keyed by `id()`.

    It was keyed `(id(index), generation)`. CPython reuses an address once the
    object at it is collected, and a freshly built index is always at
    generation 0 — so a freed index and a new one in its place would share a
    key, and one corpus would be served another's owed rows. Hung off the
    object, that is unrepresentable rather than unlikely.

    Driven over two corpora that disagree, with the first dropped in between,
    so a module-level cache surviving the object would show up as the wrong
    answer rather than as a slow one.

    **Driven through the release gate since [[ADR-0036]].** The worked example
    was the acceptance sweep — the note-less obligation whose subject was a
    feature — and it is withdrawn. The property is about the memo, not about
    which obligation exercises it, so it moves to one that still exists rather
    than being deleted with the one that does not.
    """
    import gc

    from project_os_cockpit.index import Index

    def corpus(name: str, mark: str) -> Index:
        root = tmp_path / name / "docs"
        (root / "tests" / "acceptance").mkdir(parents=True)
        (root / "releases").mkdir(parents=True)
        (root / "releases" / "REL-9001-V1.md").write_text(
            '---\ntype: "[[release]]"\nid: REL-9001\ntitle: "v1"\n'
            'status: draft\nversion: "1.0.0"\npreparing: "2026-08-18"\n'
            "owner: user:edwin\ncreated: 2026-08-01\nupdated: 2026-08-01\n"
            "---\n\n# v1\n", encoding="utf-8")
        (root / "tests" / "acceptance" / "TST-9001-C.md").write_text(
            '---\ntype: "[[test]]"\nid: TST-9001\ntitle: "C"\n'
            "level: acceptance\nstatus: active\ntier: 1\n"
            f'number: "1.1.10"\narea: "A"\nmark: {mark}\n---\n\n# C\n',
            encoding="utf-8")
        return Index.build(root)

    owing = corpus("a", "todo")            # unsettled — the gate is blocked
    assert obligations.note_less_row_for(owing, "REL-9001") is not None
    del owing
    gc.collect()

    settled = corpus("b", "done")          # settled — the gate is clear
    assert obligations.note_less_row_for(settled, "REL-9001") is None, (
        "a second corpus was served the first one's owed rows"
    )


def test_one_verb_names_the_human_act_across_every_owed_kind(tmp_path: Path) -> None:
    """TASK-0495, and the guard it went four commits without.

    The registry carried two verbs for one act — *"Run 5 tests"* beside *"Walk
    1 release gate"*. TASK-0495 unified on `Walk`; **TASK-0521 reversed it to
    `Run`** after DES-0012 D2 made `command:` the single answer to who runs a
    test, which removed the premise the first change argued from.

    The property under test is unchanged by that reversal: **one verb**. Only
    which word it is moved, which is why this guard was inverted rather than
    rewritten — a guard that has to be rebuilt every time a value changes is
    asserting the value, not the property.

    **Asserted on `badges_payload`, because the payload is what the badge
    renders.** The first version of this test said exactly that in its docstring
    and then asserted `OBLIGATIONS[...].verb` — the constant. The fourth
    independent review mutated `badges_payload` to emit `Run` for the `test`
    kind while leaving the registry at `Walk`, ran the full suite, and got
    **1698 passed, zero failures**: the badge said *"Run 5 tests"*, the defect
    this task exists to remove, and nothing noticed.

    That is the same failure the task itself documents — a description written
    ahead of the code — reproduced inside the guard against it. The payload is
    the surface's only source for this string (`obligations.py`: *"The verb is
    the registry's, never the surface's"*), so it is the assertion that has
    teeth.
    """
    docs = tmp_path / "docs"
    docs.mkdir()
    payload = obligations.badges_payload(Index.build(docs))

    assert payload["verbs"]["test"] == "Run", (
        "the badge renders this string, and one verb covers both populations "
        "since DES-0012 D2: a test with a `command:` is run by a runner, one "
        "without is run by a person"
    )
    assert "Walk" not in set(payload["verbs"].values()), (
        "no badge may say `Walk` (TASK-0521). Edwin: 'can you stop talking "
        "about walking.' The guard is INVERTED rather than deleted — the "
        "property that matters is one verb, and it survived the reversal"
    )
    # The registry is the payload's only source, so a divergence between them
    # is itself a defect — this is what makes asserting the payload strictly
    # stronger than asserting the constant rather than merely different.
    assert payload["verbs"]["test"] == obligations.OBLIGATIONS["test"].verb
