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


def test_every_row_carries_its_verb_and_a_destination(repo_index: Index) -> None:
    """A row that names no verb is the "N items" phrasing the registry
    replaced; a row with no rel is a dead click."""
    for view in sorted(obligations.VIEWS):
        for group in cockpit.landing_payload(repo_index, view)["groups"]:
            assert group["verb"], (view, group["kind"])
            assert group["noun"] and "item" not in group["label"].lower()
            for row in group["items"]:
                assert row["rel"] and not row["rel"].startswith("/"), row
                assert row["id"] and row["verb"], row


def test_the_counted_group_with_no_rows_is_the_standing_one(repo_index: Index) -> None:
    """The one obligation whose subject is not a note keeps its count and has
    no rows — asserted rather than left as a surprise, because a group with a
    number and an empty list looks like a bug from the outside."""
    rowless = [
        (view, g["kind"])
        for view in sorted(obligations.VIEWS)
        for g in cockpit.landing_payload(repo_index, view)["groups"]
        if g["count"] and not g["items"]
    ]
    assert all(k == obligations.STANDING_OBLIGATION_KIND for _, k in rowless), rowless


def test_an_unknown_view_is_reported_as_unknown(repo_index: Index) -> None:
    """`known: false`, never an empty landing — a view that does not exist and
    a view that owes nothing must not render the same way."""
    payload = cockpit.landing_payload(repo_index, "wibble")
    assert payload["known"] is False and payload["groups"] == []


def test_owed_items_and_counts_agree_kind_by_kind(repo_index: Index) -> None:
    """The two functions in `obligations` that walk the predicate. They are
    separate calls and could drift; the standing kind is the one legitimate
    difference, because its subject is a manifest entry rather than a note."""
    rows = obligations.owed_items(repo_index)
    counts = obligations.counts_by_kind(repo_index)
    for view in sorted(obligations.VIEWS):
        by_kind: dict[str, int] = {}
        for row in rows[view]:
            by_kind[row["type"]] = by_kind.get(row["type"], 0) + 1
        expected = {
            k: v for k, v in counts[view].items()
            if k != obligations.STANDING_OBLIGATION_KIND
        }
        assert by_kind == expected, view


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
    never an empty panel, and never the same sentence under every view."""
    src = _renderer()
    quiet = re.search(r"const LANDING_QUIET[^=]*= \{(.*?)\n\};", src, re.S)
    assert quiet
    heads = re.findall(r"head: '([^']+)'", quiet.group(1))
    assert len(heads) == 3 and len(set(heads)) == 3, heads


def test_the_landing_reads_the_top_bars_own_labels() -> None:
    """One name per view. A page that restated the button's label would be the
    second vocabulary this codebase keeps being bitten by."""
    src = _renderer()
    assert "const VIEW_LABELS" in src
    assert "top-bar-btn[data-mode]" in src.split("const VIEW_LABELS")[1][:400]


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
    ("ARCHITECTURE.md", ["`GET /index/<type>`", "<repo>", "<path>"]),
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


def test_the_overview_says_when_this_workspace_is_unpushed() -> None:
    """Both halves existed before this — FEAT-0055 built the count and the push
    — on the `~agents` fleet screen, plus one line inside a rail-square
    tooltip. Nothing on the surface a person lands on.

    ADR-0022 changed what that costs: the delegate may push to non-deploy
    remotes, and where it does not, the human has to be told.
    """
    src = RENDERER.read_text(encoding="utf-8")
    assert "mountUnpushedBand" in src
    fn = re.search(r"async function mountUnpushedBand\(\).*?\n\}", src, re.S).group(0)
    assert "if (ahead <= 0 && !noRemote) return;" in fn, (
        "an up-to-date workspace would render a permanent 'nothing to push'"
    )
    assert "remoteKind === 'none'" in fn, (
        "no remote at all is a different fact from nothing unpushed, and the "
        "worse one"
    )


def test_the_push_has_exactly_one_implementation() -> None:
    """The deploy-remote refusal is the one rule in this app that stops a
    click from publishing a live website. It lives in `buildBehindRow`, and
    the overview renders **that** rather than its own row — a second copy is
    how one of them comes to disagree."""
    src = RENDERER.read_text(encoding="utf-8")
    fn = re.search(r"async function mountUnpushedBand\(\).*?\n\}", src, re.S).group(0)
    assert "buildBehindRow(mine)" in fn
    assert src.count("'deploy remote'") == 1, (
        "the deploy refusal is written twice; one of them will drift"
    )
