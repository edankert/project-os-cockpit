"""FEAT-0092 — every view lands on what it owes.

Two observations with one cause (Edwin, 2026-08-11): four of the six view
buttons left the centre pane on whatever you were last reading, and the badges
counted things the view never gathered. *"These items need to be immediately
visible so the user can resolve them."*

The property that matters most here is not that a page exists. It is that the
page and the button that opens it are **one computation** — a landing whose
number disagreed with its own badge would be the exact failure FEAT-0089 was
built to prevent, and it is the cheapest thing to get wrong.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

import pytest

from project_os_cockpit import cockpit, obligations
from project_os_cockpit.index import Index

REPO_ROOT = Path(__file__).resolve().parent.parent
REPO_DOCS = REPO_ROOT / "docs"
RENDERER = REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.ts"


@pytest.fixture(scope="module")
def repo_index() -> Index:
    return Index.build(REPO_DOCS)


def test_the_page_and_the_badge_are_one_computation(repo_index: Index) -> None:
    """The whole point. Both must come from the same walk of the same
    predicate, or the button says 8 and the page it opens shows 7."""
    badges = obligations.counts(repo_index)
    for view in sorted(obligations.VIEWS):
        landing = cockpit.landing_payload(repo_index, view)
        assert landing["known"] is True, view
        assert landing["total"] == badges[view], view
        # …and the groups sum to it, so a kind cannot go missing between the
        # total and the rows the reader actually sees.
        assert sum(g["count"] for g in landing["groups"]) == badges[view], view


@pytest.mark.parametrize("corpus", ["repo_index", "owed_corpus"])
def test_every_row_carries_its_verb_and_a_destination(corpus: str, request) -> None:
    """A row that names no verb is the "N items" phrasing the registry
    replaced; a row with nowhere to go is a dead click.

    The destination is a `rel` **or** a `url` (TASK-0416). A note-backed row
    points at its file; a note-less one carries its own route — `~root/<file>`
    for a standing document that lives beside the docs tree, `~history` for an
    unpublished commit — because `/docs/<rel>` addresses neither. What is being
    protected is "no dead click", which both shapes satisfy; requiring `rel`
    specifically was the note-typed assumption this task removed.
    """
    index = request.getfixturevalue(corpus)
    for view in sorted(obligations.VIEWS):
        for group in cockpit.landing_payload(index, view)["groups"]:
            assert group["verb"], (view, group["kind"])
            assert group["noun"] and "item" not in group["label"].lower()
            for row in group["items"]:
                assert row["rel"] or row.get("url"), row
                if row["rel"]:
                    assert not row["rel"].startswith("/"), row
                assert row["id"] and row["verb"], row


def test_no_counted_group_is_left_without_its_rows(owed_corpus: Index) -> None:
    """A group with a number and an empty list looks like a bug from the
    outside, and for one kind it *was* one.

    This assertion used to be the opposite: a rowless counted group was legal
    so long as it was the standing-document kind, whose subject is a manifest
    entry rather than a note. TASK-0416 removed the carve-out by giving
    note-less obligations the same declared path — one walk yielding a count
    **and** its rows — so the exception has nothing left to describe.

    Run against `owed_corpus` deliberately: this repo's own standing set is
    currently clean, and a corpus that owes nothing cannot fail this.
    """
    rowless = [
        (view, g["kind"], g["count"])
        for view in sorted(obligations.VIEWS)
        for g in cockpit.landing_payload(owed_corpus, view)["groups"]
        if g["count"] and not g["items"]
    ]
    assert rowless == [], rowless


def test_the_standing_kind_now_carries_rows(owed_corpus: Index) -> None:
    """The kind that used to be counted-but-rowless brings its subjects.

    `owed_corpus` constructs a stub GLOSSARY, so the count is non-zero and the
    assertion is not vacuous — a test that waits for neglect fails when the
    project stops being neglectful, which is why the corpus manufactures it.
    """
    rows = obligations.owed_items(owed_corpus)[obligations.STANDING_OBLIGATION.view]
    standing = [r for r in rows if r["type"] == obligations.STANDING_OBLIGATION_KIND]
    assert standing, "the standing obligation must now produce rows"
    for row in standing:
        assert row["id"] and row["verb"], row
        # Its own route: a standing document may live beside the docs tree,
        # where `/docs/<rel>` addresses nothing (ISS-0037).
        assert row["url"], row


def test_an_unknown_view_is_reported_as_unknown(repo_index: Index) -> None:
    """`known: false`, never an empty landing — a view that does not exist and
    a view that owes nothing must not render the same way."""
    payload = cockpit.landing_payload(repo_index, "wibble")
    assert payload["known"] is False and payload["groups"] == []


@pytest.mark.parametrize("corpus", ["repo_index", "owed_corpus"])
def test_owed_items_and_counts_agree_kind_by_kind(corpus: str, request) -> None:
    """The two functions in `obligations` that walk the predicate.

    They are separate calls and could drift. There used to be one legitimate
    difference — the standing kind, counted but never enumerated — and that
    exception is exactly where they *did* drift, by five against three. It is
    gone: every kind agrees, with no carve-out to hide behind.

    Both corpora, because the repo's own is currently clean of the note-less
    kind and would not exercise the case that broke.
    """
    index = request.getfixturevalue(corpus)
    rows = obligations.owed_items(index)
    counts = obligations.counts_by_kind(index)
    for view in sorted(obligations.VIEWS):
        by_kind: dict[str, int] = {}
        for row in rows[view]:
            by_kind[row["type"]] = by_kind.get(row["type"], 0) + 1
        assert by_kind == counts[view], view


def test_every_note_less_source_is_declared_and_enumerable(owed_corpus: Index) -> None:
    """The completeness burden the note-typed side already carries.

    `OBLIGATIONS` fails a test when a note type in the corpus has no
    declaration — the corpus supplies the checklist. A note-less source has no
    corpus to supply it, so the guard is the other way round: everything
    declared must name a noun, a verb, a view the badges know, and must
    actually enumerate. A source that ships without rows would produce a badge
    nobody could explain, which is the defect this path was built to end.
    """
    assert obligations.NOTE_LESS, "at least one note-less source is declared"
    for kind, source in obligations.note_less_sources().items():
        assert kind == source.kind
        assert source.view in obligations.VIEWS, kind
        assert source.verb, kind
        assert kind in obligations.KIND_NOUNS, f"{kind} has no noun for the badge"
        rows = source.rows(owed_corpus)
        assert isinstance(rows, list), kind
        for row in rows:
            assert row["type"] == kind, row
            assert row["id"] and row["verb"] and row["url"], row
    # And the payload the renderer reads carries every one of their verbs.
    verbs = obligations.badges_payload(owed_corpus)["verbs"]
    for kind, source in obligations.NOTE_LESS.items():
        assert verbs.get(kind) == source.verb, kind


# ---- the renderer half ---------------------------------------------------


def _renderer() -> str:
    return RENDERER.read_text(encoding="utf-8")


def test_the_three_views_gained_a_landing_and_library_did_not() -> None:
    """Library is excluded deliberately: it owes nothing and is a file
    browser, so a summary in front of the tree is the thing people open the
    tree to avoid. Asserted so the exclusion is a decision, not an omission."""
    src = _renderer()
    landing = re.search(
        r"MODES_WITH_VIRTUAL_LANDING: ReadonlySet<string> = new Set\(\[(.*?)\]\)",
        src, re.S,
    )
    assert landing
    modes = set(re.findall(r"'([a-z]+)'", landing.group(1)))
    assert {"overview", "intent", "features", "issues", "tests"} <= modes
    assert "library" not in modes


def test_a_view_that_owes_nothing_says_so_in_its_own_words() -> None:
    """FEAT-0073's rule, applied to a surface built after it: never a `0`,
    never an empty panel, and never the same sentence under every view.

    Four since ISS-0167, not three: Intent joined the landings, so it owes its
    own sentence like the rest. Its `note` is deliberately empty — the other
    three say what the pane is FOR because when they are quiet the page is
    otherwise blank, and Intent's is not — so only `head` is required to be
    distinct.
    """
    src = _renderer()
    quiet = re.search(r"const LANDING_QUIET[^=]*= \{(.*?)\n\};", src, re.S)
    assert quiet
    heads = re.findall(r"head: '([^']+)'", quiet.group(1))
    assert len(heads) == 4 and len(set(heads)) == 4, heads


def test_the_landing_reads_the_top_bars_own_labels() -> None:
    """One name per view. A page that restated the button's label would be the
    second vocabulary this codebase keeps being bitten by.

    Intent is the reason this is now asserted at the USE site too (ISS-0167).
    `VIEW_LABELS` existed and was read by three landings; the fourth hardcoded
    `h.textContent = 'Designs'`, so the page and the button disagreed — the
    button says *Intent* — which is exactly what this test's own docstring
    said could not happen.
    """
    src = _renderer()
    assert "const VIEW_LABELS" in src
    assert "top-bar-btn[data-mode]" in src.split("const VIEW_LABELS")[1][:400]
    # One builder puts the head on a landing, and it reads VIEW_LABELS.
    head_fn = re.search(
        r"function buildLandingHead\(view: string\): HTMLHeadingElement \{(.*?)\n\}",
        src, re.S,
    )
    assert head_fn, "buildLandingHead is gone; the head has grown a second source"
    assert "VIEW_LABELS[view]" in head_fn.group(1)
    # One definition and two call sites: `renderViewLanding` serves all three
    # of features/issues/tests, and the Intent landing is the second caller.
    assert src.count("buildLandingHead(") == 3, (
        "a landing is building its own heading again instead of calling "
        "buildLandingHead"
    )
    # The page head has exactly one author. `'Designs'` still appears in the
    # source and legitimately so — it is the register's SECTION head, a
    # category inside Intent — so the string is not the thing to forbid; a
    # second thing calling itself the page's title is.
    assert _code(src).count("'view-landing-head'") == 1, (
        "something other than buildLandingHead is titling a landing; the "
        "Intent page called itself 'Designs' while its button said 'Intent'"
    )


def _code(src: str) -> str:
    """`src` with comments removed.

    Written because the first draft of `test_one_row_grammar_across_every_landing`
    passed against its own explanatory comment: the prose above the function
    contained `document.createElement('a')` while describing the thing it was
    forbidding. A guard a comment can satisfy is a guard that survives the
    mutation it exists to catch.
    """
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    return re.sub(r"^\s*//.*$", "", src, flags=re.M)


def test_one_row_grammar_across_every_landing() -> None:
    """ISS-0167. The three view landings and the Intent register rendered the
    same object — an id, a title, a status — in two different sets of elements,
    and the register's lost `statusChip()` entirely: `accepted` and
    `superseded` came out as grey text beside a `·`.

    ISS-0023 is the standing lesson about a vocabulary living in more than one
    place. This asserts there is one row builder and that every landing list
    goes through it.
    """
    code = _code(_renderer())
    assert code.count("function buildLandingRow(") == 1
    # The old grammar, by its own class names and its own element choice.
    for gone in (
        "'design-row'", "'design-row-title'", "'design-row-meta'",
    ):
        assert gone not in code, f"the second row grammar is back: {gone}"
    # Rows are buttons. An `<a href="#">` that preventDefaults is a button
    # wearing an anchor, and it was the register's.
    body = re.search(
        r"function buildLandingRow\(spec: LandingRowSpec\): HTMLLIElement \{(.*?)\n\}",
        code, re.S,
    )
    assert body
    assert "createElement('button')" in body.group(1)
    assert "statusChip(spec.status)" in body.group(1)
    # Every list on a landing is built by the shared builder, so a new one
    # cannot quietly arrive with its own `<ul>` and its own row markup.
    assert code.count("'view-landing-list'") == 1, (
        "a landing is building its own list element instead of buildLandingList()"
    )


def test_the_register_is_not_split_by_role() -> None:
    """ISS-0089 removed the `system`/`proposal` split from this view in
    TASK-0275 — one note in a section of its own, three designs across two
    headings, for a frontmatter field the reader never asked about — and named
    the replacement: *"the live and completed split the navigator already
    applies is the one that matters here."*

    ISS-0167's first proposed shape was `Design system · Live · Settled`,
    which would have put it straight back. This fails if it returns, in a
    heading or as a word on every row.
    """
    code = _code(_renderer())
    register = re.search(
        r"function buildDesignRegisterList\((.*?)function designIsSettled\(",
        code, re.S,
    )
    assert register, "buildDesignRegisterList moved; re-anchor this guard"
    body = register.group(1)
    assert "d.role" not in body and "role ===" not in body, (
        "the register is reading `role:` again — ISS-0089 removed that split"
    )
    for gone in ("'Design system'", "'design system'", "'proposal'", "'system'"):
        assert gone not in body, f"the role split is back as a label: {gone}"
    # The split that IS wanted, through the shared vocabulary rather than a
    # second status list (ISS-0023 again).
    assert "designIsSettled(d)" in body
    settled = re.search(
        r"function designIsSettled\(d: DesignRecord\): boolean \{(.*?)\n\}",
        code, re.S,
    )
    assert settled and "groupIsSettled(" in settled.group(1), (
        "designIsSettled has grown its own status list; it must route through "
        "completed-work.ts, which test_status_vocabulary.py checks against "
        "statuses.py"
    )


def test_the_intent_landing_leads_with_what_its_badge_counts() -> None:
    """ISS-0167's measurable half. Intent owed 1 and its page showed eleven
    designs and never named it.

    The property asserted is structural, not cosmetic: the Intent landing must
    render the SAME obligation block, from the SAME payload, as the other
    three — so the page and the badge cannot come to disagree, which is the
    failure FEAT-0089 exists to prevent and the one this landing was outside
    of.
    """
    code = _code(_renderer())
    # Anchored inside `renderDesignPage` — `if (!target) {` alone matches an
    # earlier, unrelated branch, and a guard that reads the wrong function is
    # a guard that passes for the wrong reason.
    page = re.search(
        r"async function renderDesignPage\(target: string\): Promise<boolean> \{"
        r"(.*?)\n  const d = designs\.find\(",
        code, re.S,
    )
    assert page, "renderDesignPage moved; re-anchor this guard"
    landing = re.search(r"if \(!target\) \{(.*)", page.group(1), re.S)
    assert landing, "the Intent landing branch is gone"
    body = landing.group(1)
    assert "fetchLandingPayload('intent')" in body, (
        "the Intent landing is not reading the obligation payload"
    )
    for shared in ("buildLandingHead('intent')", "buildLandingLead('intent'",
                   "buildLandingObligations(data)"):
        assert shared in body, f"the Intent landing stopped using {shared}"
    # Obligations ABOVE identity (DES-0008: a reader who stops halfway should
    # have seen the obligations, not the news).
    assert body.index("buildLandingObligations(data)") < body.index(
        "buildIdentityBand(brief)"
    ), "the identity band is back above what needs a person"
    # One payload feeds both the block and the register's destinations, so the
    # owed predicate is never restated in TypeScript (TASK-0357's rule).
    assert "'proposed'" not in body, (
        "the Intent landing is deciding what is owed for itself instead of "
        "reading the registry's answer"
    )
    assert "buildDesignRegisterList(designs, owedIds)" in body


def test_an_owed_design_opens_its_note_and_the_rest_open_the_bench() -> None:
    """FEAT-0092's criterion — *"every owed row navigates to the note that
    carries its actuator, so the verb named on the page is the verb available
    when you arrive"* — applied to the view it was not applied to.

    `Accept` lives on the note's actuator row (`mountActuatorRow`, reached only
    from `loadDoc`); the bench offers `Ask for review` and no status
    transition. So an owed design that opened the bench would name a verb the
    destination does not have. Asserted rather than walked because no design in
    this corpus is `proposed` today — which is exactly when a path rots.
    """
    code = _code(_renderer())
    register = re.search(
        r"const row = \(d: DesignRecord\): HTMLLIElement => buildLandingRow\(\{(.*?)\}\);",
        code, re.S,
    )
    assert register, "the register's row builder moved; re-anchor this guard"
    assert "owed.has(d.id) ? d.rel : `~design/${d.id}`" in register.group(1), (
        "an owed design no longer opens its note, or a settled one no longer "
        "opens the bench"
    )


def test_the_landing_unhides_the_stage_it_renders_into() -> None:
    """Both bugs this feature shipped with were invisible to DOM assertions.

    The section rendered correctly into `#doc-view` — present, populated,
    right content — while the stage still had it `hidden`, so the pane was
    **blank**. Every query-based check passed; a screenshot did not. Every
    other virtual page sets the pair, and the landing did not.
    """
    fn = re.search(
        r"async function renderViewLanding\(.*?\n\}\n", _renderer(), re.S,
    )
    assert fn, "renderViewLanding is gone"
    body = fn.group(0)
    assert "docView.hidden = false" in body
    assert "placeholder.hidden = true" in body


def test_no_landing_rel_is_claimed_by_an_earlier_route() -> None:
    """The second bug, and the more dangerous shape.

    `~tests` was already a route: *"bare `~tests` has no page of its own"*, it
    called `setNavMode('tests')` and returned. With a landing, `setNavMode`
    calls `loadWsNav`, which navigates to `~tests`, which reached that branch
    and called `setNavMode` again — **an infinite loop that froze the
    renderer**, a hundred lines above the branch that should have handled it.

    A route claimed twice does not error. It takes whichever claim is written
    first, so this asserts the earlier claims are gone rather than that the
    later one exists.
    """
    src = _renderer()
    for rel in ("~features", "~issues", "~tests"):
        assert f"normalised === '{rel}'" not in src, (
            f"{rel} is claimed by a second route branch; whichever is written "
            "first wins and the landing may never run"
        )
    assert "VIEW_LANDING_RELS.has(normalised)" in src


def test_no_document_appears_twice_on_the_intent_view(repo_index: Index) -> None:
    """ISS-0068's rule — one item, one home — enforced on **rel path**.

    All eight standing documents were listed twice on this view for a
    fortnight: once from the manifest and once in `Reference`. The id-based
    guard saw nothing, because the two name the same file differently —
    `ARCHITECTURE`/`ARCH`, `README`/`DOCS-README`, `STYLEGUIDE`/`STYLE`.

    **A duplicate that renames itself is invisible to a check that compares
    names.** So this compares paths, which cannot be forged.
    """
    groups = cockpit.nav_payload(repo_index, mode="intent")["groups"]
    seen: dict[str, str] = {}
    for group in groups:
        # **The one exception, stated rather than implied** (ADR-0025). The
        # leading `Needs you` group is a shortcut list: its rows also keep
        # their structural place, marked, because a decision that vanished
        # from Decisions *because* it needs deciding would make that list
        # answer a different question than the one it is labelled with.
        #
        # Written as an exemption here rather than by loosening the check,
        # because a rule narrowed in silence is a rule abandoned. Everything
        # outside this group still obeys ISS-0068 on rel path.
        if group.get("key") == "needs-you":
            continue
        for item in group.get("items") or []:
            url = str(item.get("url") or "")
            if not url:
                continue
            rel = url.split("/docs/", 1)[-1] if "/docs/" in url else url
            if not rel.endswith(".md"):
                continue          # virtual routes (~design/DES-0001) are not files
            assert rel not in seen, (
                f"{rel} is in both '{seen[rel]}' and '{group['key']}'"
            )
            seen[rel] = str(group["key"])
    # Vacuity guard: the view must actually carry file-backed rows, or the
    # loop above asserts nothing.
    assert len(seen) >= 8, sorted(seen)


def test_the_ready_path_refreshes_the_badges() -> None:
    """ISS-0149. `refreshObligationBadges` returns early without a sidecar, and
    on a fresh window `setNavMode` runs from stored state before one exists —
    so the badges stayed bare until the first mode click.

    The `ready` block already refreshes seven surfaces and carries ISS-0040's
    guard for this same class of omission. Membership is asserted rather than
    left to a reviewer noticing the eighth, and it matters more since
    FEAT-0092: the badge is now the way into each view's landing page, so a
    blank one hides the list of what a person owes at the moment they open the
    app to ask.
    """
    src = _renderer()
    ready = src.split("case 'ready': {", 1)[1].split("case 'failed'", 1)[0]
    assert "refreshObligationBadges()" in ready, (
        "a freshly launched window shows no obligation badges until the first "
        "mode click"
    )


def test_the_brief_section_arrives_rendered(repo_index: Index) -> None:
    """ISS-0151. The Intent band printed the brief's markdown as `textContent`
    under `white-space: pre-wrap`, so the file's own newlines showed as hard
    breaks and its syntax showed as syntax — a symptom that reads exactly like
    a hard-wrapped source file. The file was never wrapped: measured across
    twelve repos, zero.
    """
    from project_os_cockpit.cockpit import brief_payload
    payload = brief_payload(REPO_DOCS.parent)
    section = next(s for s in payload["sections"] if "What it is for" in s["heading"])
    assert section["body_html"].startswith("<"), "the section is not rendered"
    assert "<li>" in section["body_html"], "its list is still plain text"
    assert section["body"], "the source is gone; a caller wanting it must not unparse HTML"

    css = (REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.css").read_text()
    rule = css.split(".design-identity-for {", 1)[1].split("}", 1)[0]
    assert "pre-wrap" not in rule, (
        "the compensation is back; it re-breaks the lines the fix un-breaks"
    )
    src = RENDERER.read_text(encoding="utf-8")
    fn = re.search(r"function buildIdentityBand\(.*?\n\}", src, re.S)
    assert fn, "the identity band is gone"
    assert "forSection.body_html" in fn.group(0)
    assert "textContent = forSection.body;" not in src


# ---- FEAT-0094: needs you leads every view --------------------------------


def test_the_needs_you_group_equals_the_badge_in_every_view(repo_index: Index) -> None:
    """Three surfaces, one walk. The group, the badge and the landing page all
    read `obligations.owed_items`, so a view whose group disagreed with its own
    button would be the failure FEAT-0089 exists to prevent, reintroduced one
    pane to the left.

    Intent is the case that made this necessary: its group came out 3 against a
    badge of 5, because two of the five are standing documents whose subject is
    a manifest entry rather than a note.
    """
    counts = obligations.counts(repo_index)
    for view in ("features", "intent"):
        first = cockpit.nav_payload(repo_index, mode=view)["groups"][0]
        if counts[view] == 0:
            assert first["key"] != "needs-you", "a zero group is showing"
            continue
        assert first["key"] == "needs-you", f"{view} does not lead with what it owes"
        assert first["needs_human"] is True
        assert len(first["items"]) == counts[view], view
        assert all(i["owed"] and i["owed_verb"] for i in first["items"])


def test_the_views_that_already_gather_get_no_second_group(repo_index: Index) -> None:
    """ADR-0025 permits the duplication and does not require it. `Needs triage`
    and `Needs a run` already gather the same set under names that say more, so
    a shared group there would duplicate where it buys nothing."""
    for view in ("issues", "tests"):
        keys = [g["key"] for g in cockpit.nav_payload(repo_index, mode=view)["groups"]]
        assert "needs-you" not in keys, view
    # …and Issues still leads with its own, or the uniformity claim is false.
    if obligations.counts(repo_index)["issues"]:
        first = cockpit.nav_payload(repo_index, mode="issues")["groups"][0]
        assert first["needs_human"] is True


def test_the_structural_copy_is_marked(repo_index: Index) -> None:
    """ADR-0025's condition for permitting the copy: a row met in the tree is
    visibly the same one gathered above. Unmarked, the reader has no way to
    know why it appears twice."""
    owed_ids = {r["id"] for r in obligations.owed_items(repo_index)["features"]}
    assert owed_ids, "no owed feature-view rows; this asserts nothing"
    seen: dict[str, bool] = {}

    def walk(items: list) -> None:
        for item in items:
            if item.get("id") in owed_ids:
                seen[item["id"]] = bool(item.get("owed") and item.get("owed_verb"))
            walk(item.get("children") or [])

    for group in cockpit.nav_payload(repo_index, mode="features")["groups"]:
        if group["key"] == "needs-you":
            continue
        walk(group.get("items") or [])
    assert seen and all(seen.values()), seen


def test_the_needs_you_group_sits_above_the_open_split() -> None:
    """FEAT-0094, corrected. It rendered **under** the `Open · N` heading,
    because the navigator splits groups into live and settled and a group with
    open items is live by definition.

    That heading is about work in flight, and what needs a person is not a kind
    of open work — it is the reason to be looking at the pane. Under it, the
    group read as one more phase. So it is lifted out of the split before the
    split happens, and its count is rendered in the badge's own shape rather
    than as a number the reader is left to connect.
    """
    src = RENDERER.read_text(encoding="utf-8")
    fn = src.split("function renderWsNav(", 1)[1].split("\nfunction ", 1)[0]
    assert "const owedGroup = groups.find((g) => g.key === 'needs-you')" in fn
    # Lifted BEFORE the live/settled split, or it lands under `Open` again.
    assert fn.index("const owedGroup") < fn.index("const live: NavGroupData[]")
    assert "for (const group of rest)" in fn, (
        "the split still walks every group, so the owed group is in it twice"
    )
    assert fn.index("nav-needs-you") < fn.index("`Open · ${live.length}`")
    # …and it says whose count it is.
    assert "mode-badge nav-needs-you-count" in fn


# ---- ISS-0153: the stub check reads code as template ---------------------


@pytest.mark.parametrize("doc,notation", [
    # The tokens are re-picked when a document is rewritten — ARCHITECTURE.md
    # was, on 2026-08-12, and the vacuity guard caught it immediately, which
    # is the guard doing its job rather than the test being brittle.
    ("ARCHITECTURE.md", ["`python -m project_os_cockpit <repo>/docs`"]),
    ("OWNERSHIP.md", ["`user:<handle>`", "`group:<name>`", "`system:<name>`"]),
])
def test_technical_notation_is_not_a_template_placeholder(doc, notation) -> None:
    """Both were reported as *"still holds its template"* while being fully
    written — `ARCHITECTURE.md` carries an architecture diagram — because
    `<[A-Za-z]…>` matches an angle-bracket token and technical prose is full of
    legitimate ones. All of them are correctly inside backticks.

    Named individually so a future tightening of the regex cannot quietly
    re-break the two documents that exposed it.
    """
    from project_os_cockpit import standing
    text = (REPO_DOCS / doc).read_text(encoding="utf-8")
    for token in notation:
        assert token in text, f"{doc} no longer contains {token}; this asserts nothing"
    kinds = {f.kind for f in standing.check(REPO_DOCS) if f.document == doc.split(".")[0]}
    assert "stub" not in kinds, f"{doc} is reported as a template stub"


def test_a_document_that_really_holds_its_template_is_still_a_stub(tmp_path: Path) -> None:
    """The vacuity guard. Without it the fix is indistinguishable from
    deleting the check."""
    from project_os_cockpit import standing
    docs = tmp_path / "docs"
    shutil.copytree(REPO_DOCS, docs)
    (docs / "GLOSSARY.md").write_text(
        '---\ntype: "[[reference]]"\nid: GLOSSARY\nupdated: 2026-08-12\n---\n\n'
        "# Glossary\n\n- <Term>: <what it means>\n- <Another term>: <what it means>\n",
        encoding="utf-8",
    )
    kinds = {f.document: f.kind for f in standing.check(docs)}
    assert kinds.get("GLOSSARY") == "stub", kinds


def test_each_owed_kind_names_its_own_verb() -> None:
    """`Confirm` was the label on every kind, and it fits only the one that is
    deliberately not owed: you cannot confirm a document nobody has written."""
    from project_os_cockpit import obligations
    assert obligations.STANDING_VERBS["missing"] == "Create"
    assert obligations.STANDING_VERBS["stub"] == "Write"
    assert obligations.STANDING_VERBS["ambiguous"] == "Resolve"
    assert obligations.STANDING_VERBS["stale"] == "Confirm"
    assert set(obligations.STANDING_OWED_KINDS) <= set(obligations.STANDING_VERBS)


# ---- FEAT-0098: unpushed work, where you work ----------------------------


def test_the_overview_band_is_retired_and_history_says_it_instead() -> None:
    """Retired 2026-08-13 (TASK-0418), in two steps, and the second is Edwin's.

    The band was built when nothing on the surface a person lands on said that
    work was unpublished. History says it now, beside the commits it publishes
    — an obligation surfacing where its subject lives (ADR-0020) — and keeping
    the band as well put the same sentence and a second Push button on one
    page. It was narrowed to its no-remote half first; then: *"reuse the same
    place for other messages if no remote has been configured for instance,
    this should not be displayed in a different place."*

    Two places for one subject is the thing that gets answered twice and then
    differently, which is why this is asserted rather than remembered.
    """
    src = RENDERER.read_text(encoding="utf-8")
    assert "mountUnpushedBand" not in src, (
        "the band is back; History owns everything this surface says about "
        "publication, including having nowhere to publish to"
    )
    fn = re.search(r"function buildPublicationBlock\(opts: \{.*?\n\}\n", src, re.S).group(0)
    assert "nothing here is backed up" in fn, (
        "the no-remote message must live in the SAME place as the count"
    )
    assert "not deployed" in fn and "not pushed" in fn, (
        "all three states share one block: pushable, deploy-only, no remote"
    )


def test_the_push_has_exactly_one_implementation() -> None:
    """The deploy-remote refusal is the one rule in this app that stops a click
    from publishing a live website.

    Two surfaces offer a push — the fleet screen and the unpublished run in
    History — so the rule is written **once**, in `buildPushControl`, and
    rendered in both. The attention card deliberately offers none: it says the
    fact and takes you to where it is acted on (Edwin, 2026-08-13). `git.ts` re-derives the
    classification and refuses regardless, because a UI state is not a guard;
    this is the other half, so a deploy remote is never *offered* in the first
    place, identically, wherever it appears.
    """
    src = RENDERER.read_text(encoding="utf-8")
    assert src.count("'deploy remote'") == 1, (
        "the deploy refusal is written twice; one of them will drift"
    )
    assert src.count("is a deployment target, not a backup") == 1, (
        "the refusal SENTENCE is written twice; the two will drift apart"
    )
    # Every surface builds its control through the one function rather than
    # assembling a button and deciding for itself whether to disable it.
    assert src.count("buildPushControl({") == 2, (
        "a surface is offering a push without going through buildPushControl"
    )
    assert "ws-attention-push" not in src, (
        "the attention card has grown a push button again; the push lives in "
        "History, beside the commits it publishes"
    )
    assert src.count("function buildPushControl(") == 1


def test_the_publication_surfaces_repaint_when_the_git_state_lands() -> None:
    """Git state is probed asynchronously, so on a fresh window the fleet row
    exists with no `ahead` at all — the surface correctly renders nothing, and
    then nothing ever re-renders it.

    **Third time in one day for this shape.** The obligation badges (ISS-0149)
    and the cross-repo jump both failed the same way: data arriving after the
    surface that needs it has already painted. The surface that depends on it
    is now the attention panel — History reads `unpublished` from the sidecar's
    own payload and is correct at fetch time — so the assertion moved with it
    rather than being dropped when the band was retired.
    """
    src = RENDERER.read_text(encoding="utf-8")
    apply_fn = re.search(
        r"function applyFleetHealthPayload\(payload: unknown\): void \{.*?\n\}",
        src, re.S,
    ).group(0)
    assert "refreshAttention()" in apply_fn, (
        "the cards are built once and never rebuilt; on a fresh window they "
        "show nothing however many commits are unpushed"
    )


# ---- the terminal keeps the keyboard across a switch (ISS-0154) ----------

def test_every_terminal_attach_restores_the_keyboard() -> None:
    """A workspace switch used to attach the console and never focus it.

    `showTerminal` and `restartTerminal` both scheduled `term.focus()` after
    their attach; `openWorkspace` — the path a SWITCH takes — did not. So a
    freshly opened console took keys and the same console after A→B→A did not,
    which is exactly the difference reported: *"a newly created terminal
    accepts input at first, then fails after leaving and returning."*

    The repair is one helper rather than three call sites remembering, so the
    assertion is that nothing calls the bare attach.
    """
    src = RENDERER.read_text(encoding="utf-8")
    assert "async function attachAndFocusTerminal(" in src
    # Comments are stripped before counting, and that is not tidiness.
    # Independent review (2026-08-14) found this assertion satisfied by prose:
    # one of the two matches was `// This line used to be `void
    # attachTerminalTo(id)``, so deleting that comment while reintroducing a
    # real bare call kept the count at 2 and the suite green. A guard a comment
    # can satisfy is measuring the file, not the behaviour.
    code = re.sub(r"//[^\n]*", "", src)
    bare = re.findall(r"(?<!async function )attachTerminalTo\(", code)
    assert len(bare) == 1, (
        "attachTerminalTo is called outside attachAndFocusTerminal; that call "
        "site will attach the console without giving it back the keyboard"
    )
    helper = re.search(
        r"async function attachAndFocusTerminal\(.*?\n\}", src, re.S).group(0)
    assert "term?.focus()" in helper
    assert "activeId !== workspaceId" in helper and "terminalPane.hidden" in helper, (
        "a slow attach must not steal focus back for a workspace the reader "
        "has already left, or into a pane they have closed"
    )


def test_the_terminal_attach_cannot_replay_a_stale_backlog() -> None:
    """`attachedTerminalId` is set synchronously and the attach is awaited, so
    A→B→A could let B's backlog land in the terminal now showing A.

    Same family as TASK-0187's PTY identity guard and ISS-0158's duplicated
    band: an async step between deciding and doing.
    """
    src = RENDERER.read_text(encoding="utf-8")
    fn = re.search(r"async function attachTerminalTo\(.*?\n\}\n", src, re.S).group(0)
    assert "terminalAttachGeneration" in fn

    # Each awaited step is named and checked individually, rather than counted.
    #
    # This assertion used to read `count(...) >= 2`, which was true when written
    # and stopped guarding when ISS-0161 added a third occurrence: deleting the
    # check after `terminal.attach` — the exact mutation this test's evidence
    # row claims to catch — left two behind and the suite green. Independent
    # review found it on 2026-08-14. A threshold cannot notice that the thing
    # protecting one await now protects a different one.
    #
    # The two `await new Promise(...)` steps of the backlog replay deliberately
    # share the single check that follows them: nothing between the two touches
    # state, so re-checking twice would assert a property the code does not owe.
    # The window matters: the check must appear before the NEXT await, not
    # merely somewhere later in the function. The first repair of this test
    # searched the whole remainder and still passed its own mutation, because
    # deleting the check after `terminal.attach` left the *backlog replay's*
    # check downstream to satisfy the search. A guard that accepts another
    # step's protection as its own is the same error one layer up.
    check = r"if \(generation !== terminalAttachGeneration\) return;"
    for label, awaited in (
        ("spawn", r"await cockpitApi\.terminal\.spawn\("),
        ("attach", r"await cockpitApi\.terminal\.attach\("),
        ("backlog replay", r"requestAnimationFrame\("),
    ):
        parts = re.split(awaited, fn)
        assert len(parts) > 1, f"the {label} step has gone; this guard now checks nothing"
        window = re.split(r"\bawait ", parts[-1])[0]
        assert re.search(check, window), (
            f"the {label} await is not followed by a generation re-check before "
            "the next await; an unguarded await is the whole defect — B's "
            "backlog lands in the terminal now showing A"
        )


def test_the_digest_never_under_reports_what_the_badges_show(owed_corpus: Index) -> None:
    """One walk, so the card and the badges cannot disagree (ISS-0159).

    The digest built its own pass over the corpus and asked the registry's
    predicate per record — the right rule, the wrong walk, because a walk over
    notes cannot see an obligation whose subject is not a note. Measured on
    2026-08-13 it said 13 where the badges said 14, and the difference *was*
    the note-less count.

    The digest is legitimately a superset: it also carries notes whose
    `review_verdict` still owes work, which the registry does not count. So the
    assertion is `>=` and the excess is enumerable, never a silent shortfall.
    """
    from project_os_cockpit.watermark import Watermark

    root = owed_corpus.docs_root.parent
    digest = cockpit.digest_payload(root, owed_corpus, Watermark(root).seen_at)
    registry = sum(obligations.counts(owed_corpus).values())
    assert registry > 0, "fixture owes nothing — the assertion would be vacuous"
    assert digest["needs_you_count"] >= registry, (
        f"the digest under-reports: {digest['needs_you_count']} against the "
        f"badges' {registry}; a note-less obligation is invisible to it again"
    )
    # And every kind the registry counts is actually present by id, not merely
    # covered by the total.
    owed_ids = {
        r["id"] for rows in obligations.owed_items(owed_corpus).values() for r in rows
    }
    digest_ids = {str(i.get("id") or "") for i in digest["needs_you"]}
    assert owed_ids <= digest_ids, sorted(owed_ids - digest_ids)


def test_the_terminal_never_re_asserts_a_mouse_mode(tmp_path: Path = None) -> None:
    """Mouse tracking is the app's business (ISS-0160).

    Re-asserting a saved mode wrote `\\e[<35;col;row M` into the PTY on every
    mouse movement — 84 such sequences in one recorded session. An app no
    longer in mouse mode sees ESC and then letters, and an ESC into a vi-mode
    readline switches it to command mode, which is why `g` and `l` stopped
    being letters while the arrow keys still worked.

    ISS-0016 accepted that in writing — *"recoverable, and rare"* — and it was
    neither. The snapshot went with it: once nothing re-asserted, the map was
    written on every switch and read by nothing.
    """
    src = RENDERER.read_text(encoding="utf-8")
    assert "MOUSE_TRACK_DECSET" not in src, (
        "the DECSET table is back; something is re-enabling mouse tracking on "
        "the app's behalf, and the app is the only party that knows"
    )
    assert "workspaceMouseMode" not in src, (
        "the per-workspace mouse-mode snapshot is back; it exists only to feed "
        "a re-assert, so its return means the re-assert has returned too"
    )
    fn = re.search(r"async function attachTerminalTo\(.*?\n\}\n", src, re.S).group(0)
    assert "\\x1b[?" not in fn, (
        f"the attach writes a DEC private mode into the terminal: {fn}"
    )


# ---- Active mode counts work, not statuses (ISS-0122) --------------------

def test_the_doing_column_names_only_work_somebody_is_doing(repo_index: Index) -> None:
    """`_active_groups` bucketed by status alone, and `active` is what a plan
    carries while its parent feature is open, what a reference carries while it
    is current, and what a glossary carries permanently.

    Measured before the fix: `Doing` held 27 items, of which 24 were `reference`
    and `plan`, against one feature, one task and one phase anybody was working
    — and 44:1 noise when the issue was filed. After: three items, all work.

    This matters where nobody looks: `active` lost its top-bar button, but
    `buildNowBoard` — the overview for a phase-less project — is built from it,
    so the defect is latent here and live in any repo without phases.
    """
    groups = {g["label"]: g for g in cockpit.nav_payload(repo_index, mode="active")["groups"]}
    for label in ("Doing", "Next"):
        group = groups.get(label)
        if not group:
            continue
        offenders = [
            (i.get("id"), i.get("type")) for i in group["items"]
            if i.get("type") in cockpit._ACTIVE_NON_WORK_TYPES
        ]
        assert not offenders, (
            f"{label} lists notes whose status is not about work: {offenders}"
        )


def test_an_accepted_decision_is_not_upcoming_work(repo_index: Index) -> None:
    """An accepted ADR is a decision that HAS been made (ISS-0122).

    It put 14 settled items into a column of 45. The work an accepted decision
    implies is the feature or task implementing it, and those carry their own
    status — so the column reads them instead.
    """
    assert "accepted" not in cockpit._ACTIVE_NEXT
    groups = {g["label"]: g for g in cockpit.nav_payload(repo_index, mode="active")["groups"]}
    nxt = groups.get("Next")
    if nxt:
        assert not [i for i in nxt["items"] if i.get("status") == "accepted"], (
            "settled decisions are listed as upcoming work"
        )
