"""Getting to the walk, and the guard rails on the way ([[TASK-0619]], [[TASK-0621]]).

A page nobody can reach is a page nobody walks. Three surfaces point at it —
the release rung in the publication ladder, the release page's gate section and
the checks page's header — and each one offers the link only while there is a
walk to do, because a permanent blank button is the failure [[FEAT-0102]]
records the rule about twice.

The behavioural assertions about the page itself live in
`desktop/tests/walk-page.test.mjs`, which runs the real builders. What is here
is the part a Python test can hold honestly: what the payloads say, and the two
source guards that are claims about the *whole* of a function rather than about
a value it returns.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from project_os_cockpit import acceptance, cockpit
from project_os_cockpit.index import Index

REPO_ROOT = Path(__file__).resolve().parent.parent
RENDERER = REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.ts"


def _repo(tmp_path: Path, *, preparing: bool = True,
          platform: str = "android", walked: bool = False) -> Path:
    docs = tmp_path / "docs"
    (docs / "tests" / "acceptance").mkdir(parents=True)
    (docs / "releases" / "ledgers").mkdir(parents=True)
    (docs / "features").mkdir(parents=True)
    (docs / "features" / "FEAT-0001-Thing.md").write_text(
        '---\ntype: "[[feature]]"\nid: FEAT-0001\ntitle: "Thing"\n'
        'status: done\n---\n\n# Thing\n', encoding="utf-8")
    (docs / "tests" / "acceptance" / "TST-0001-C.md").write_text(
        '---\ntype: "[[test]]"\nid: TST-0001\ntitle: "C"\n'
        'level: acceptance\nstatus: active\narea: "Profile"\nmark: todo\n'
        'covers: ["[[FEAT-0001]]"]\n---\n\n# C\n', encoding="utf-8")
    (docs / "releases" / "REL-0001-R.md").write_text(
        '---\ntype: "[[release]]"\nid: REL-0001\ntitle: "R"\n'
        f'status: {"draft" if preparing else "released"}\nversion: "1.1.0"\n'
        f'platform: "{platform}"\npreparing: {str(preparing).lower()}\n'
        'features: ["[[FEAT-0001]]"]\nupdated: "2026-09-13"\n'
        f'{"date: 2026-09-13" if not preparing else ""}\n---\n\n# R\n',
        encoding="utf-8")
    entries = []
    if walked:
        entries.append({"check": "TST-0001", "date": "2026-09-13",
                        "mark": "pass", "by": "user:edwin", "method": "manual"})
    (docs / "releases" / "ledgers" / f"WORKING-{platform}.json").write_text(
        json.dumps({"platform": platform, "entries": entries}), encoding="utf-8")
    return docs


def _walk_rows(docs: Path) -> list[dict]:
    groups = cockpit._publication_groups(Index.build(docs), docs.parent)
    out = []
    for group in groups:
        for sub in group.get("subgroups") or []:
            for item in sub.get("items") or []:
                if str(item.get("url") or "").startswith("~walk"):
                    out.append(item)
    return out


# ------------------------------------------------------- the publication ladder

def test_the_release_rung_points_at_the_walk_while_a_release_is_draft(
        tmp_path: Path) -> None:
    rows = _walk_rows(_repo(tmp_path))
    assert len(rows) == 1
    assert rows[0]["url"] == "~walk/android"
    assert "1 owed on android" in rows[0]["subtitle"]


def test_nothing_owed_offers_no_walk(tmp_path: Path) -> None:
    """A link to an empty walk is the blank button, one surface down."""
    assert _walk_rows(_repo(tmp_path, walked=True)) == []


def test_a_shipped_release_offers_no_walk(tmp_path: Path) -> None:
    """The gate asks only while a release is in preparation ([[ADR-0028]])."""
    assert _walk_rows(_repo(tmp_path, preparing=False)) == []


def test_a_release_on_a_platform_with_no_ledger_offers_no_walk(
        tmp_path: Path) -> None:
    """A walk read for a platform with no ledger reads no verdicts, so it
    reports every check in the repo as owed. The route refuses that; the
    ladder does not offer it in the first place."""
    docs = _repo(tmp_path, platform="ios")
    #: The release says it ships Android; the only ledger is the iOS one.
    (docs / "releases" / "REL-0001-R.md").write_text(
        (docs / "releases" / "REL-0001-R.md").read_text(encoding="utf-8")
        .replace('platform: "ios"', 'platform: "android"'), encoding="utf-8")
    assert _walk_rows(docs) == []


def test_the_rung_count_is_the_walks_count_not_the_union(tmp_path: Path) -> None:
    """The row says *N owed on <platform>*, and the walk page must render N
    rows. `unchecked` in that function is the union over every ledger — 327 on
    `your-trainer`, whose open Android release owes 39 — so reading it would
    put two answers to one question a click apart ([[ISS-0289]])."""
    docs = _repo(tmp_path)
    #: A second platform that owes the check too. The union is 1 either way on
    #: this fixture, so the assertion is made on the computation: the row's
    #: number equals what the walk payload returns for that platform.
    (docs / "releases" / "ledgers" / "WORKING-ios.json").write_text(
        json.dumps({"platform": "ios", "entries": []}), encoding="utf-8")
    row = _walk_rows(docs)[0]
    payload = acceptance.walk_payload(docs, Index.build(docs), platform="android")
    found = re.search(r"^(\d+) owed", row["subtitle"])
    assert found and int(found.group(1)) == payload["counts"]["owed"]


# ------------------------------------------------------------- the checks page

def test_the_checks_payload_names_the_platform_the_header_links_for(
        tmp_path: Path) -> None:
    """The header offers the walk only when the payload named a platform.
    `All` means the union, a union has no walk, and the route refuses one — so
    without this field the link would be a button that opens a refusal."""
    docs = _repo(tmp_path)
    view = acceptance.view_payload(docs, Index.build(docs), platform="android")
    assert view["platform"] == "android"
    assert acceptance.view_payload(
        docs, Index.build(docs), platform="")["platform"] == ""


# ------------------------------------------------------------- source guards

def _function_body(name: str) -> str:
    """One renderer function, bounded by the next top-level declaration.

    The same bounding `test_release_held_back` uses, and for the reason its
    docstring gives: a character window is a guess about a distance, and this
    suite has had one fail in both directions.
    """
    src = RENDERER.read_text(encoding="utf-8")
    decls = [(m.start(), m.group(1))
             for m in re.finditer(r"^(?:async )?function (\w+)", src, re.M)]
    for n, (start, found) in enumerate(decls):
        if found != name:
            continue
        end = decls[n + 1][0] if n + 1 < len(decls) else len(src)
        return src[start:end]
    raise AssertionError(f"{name}() is not in the renderer")


def _code_only(region: str) -> str:
    """The function with its comments removed.

    Necessary rather than tidy: the rule against printing a time is stated in
    a comment beside the code that obeys it — *"no minutes, no estimate, no
    schedule"* — so a guard reading the raw text fails on the sentence that
    explains why it exists.
    """
    region = re.sub(r"/\*.*?\*/", " ", region, flags=re.S)
    return "\n".join(
        line for line in region.splitlines()
        if not line.lstrip().startswith(("//", "*", "/*"))
    )


#: Every function that draws or drives the walk page. Named rather than
#: discovered by prefix: `walkOneCheck` is the checks page's writer and shares
#: the prefix, and a guard that swept it in would be asserting about the wrong
#: surface.
WALK_FUNCTIONS = (
    "renderWalkPage", "buildWalkPage", "buildSurveySection",
    "buildSittingSection", "buildWalkRow", "walkBlock", "walkNotice",
    "buildWalkRefusal", "markWalkRow", "repaintWalkRow", "walkLink",
    "walkRowId", "saveWalkPlace", "loadWalkPlace",
)


def test_the_walk_page_prints_no_time_estimate() -> None:
    """[[TASK-0449]]'s guard rail, which outlived that task: *"No time
    estimates. Order, not schedule."* Counts of rows are the only numbers on
    this page.

    Checked over whole functions rather than by a grep of the file, so a
    minute added to the walk fails here and a minute somewhere else in a
    20,000-line renderer does not.
    """
    banned = re.compile(r"\b(minutes?|durations?|estimates?|eta|hours?)\b", re.I)
    for name in WALK_FUNCTIONS:
        found = banned.search(_code_only(_function_body(name)))
        assert not found, (
            f"{name}() mentions {found.group(0)!r} — the walk carries an "
            "order, never a schedule (TASK-0449)"
        )


def test_the_walk_is_reachable_from_the_address_bar() -> None:
    """`~walk/<platform>` is a route, so it can be linked, reopened by
    back/forward and restored on return — the three things a filter living in
    a click cannot do ([[ISS-0203]])."""
    src = RENDERER.read_text(encoding="utf-8")
    assert "normalised.startsWith('~walk/')" in src
    assert "renderWalkPage(platform)" in src


def test_the_publication_view_owns_the_walk() -> None:
    """Without this, reselecting Publication mid-walk lands on
    `~release/next`, which is not a landing but an eviction ([[ISS-0263]])."""
    src = RENDERER.read_text(encoding="utf-8")
    owned = re.search(r"VIEW_OWNED_PAGES[^=]*=\s*\{(.*?)\n\};", src, re.S)
    assert owned and "'~walk'" in owned.group(1)


def test_the_two_renderer_links_require_a_ledger_to_walk_against() -> None:
    """**A link to a refusal is worse than no link** (independent review,
    2026-09-13).

    The ladder's row has always checked `ledger.platforms`; the release page's
    button and the checks header did not, so both rendered on any repo with a
    draft release and no ledger — which is every repo before its first
    recorded mark — and opened the route's 400.

    A source guard rather than a rendered one because both conditions are
    single expressions inside functions the node suite does not build: what is
    asserted is that the ledger is consulted at all, and the wording of each
    is pinned so a rename fails here.
    """
    gate = _function_body("buildGateSection")
    assert "p.id === d.platform && p.ledger" in _code_only(gate), (
        "the release page offers the walk without checking the repo keeps a "
        "ledger for that platform"
    )
    checks = _function_body("buildChecksPage")
    assert "ledgerPlatforms.includes(v.platform)" in _code_only(checks), (
        "the checks header offers the walk without checking the repo keeps a "
        "ledger for that platform"
    )


def test_the_three_links_build_one_address() -> None:
    """`walkLink` is the only place a walk address is spelled, so the rung,
    the release page and the checks page cannot come to disagree about it."""
    src = RENDERER.read_text(encoding="utf-8")
    #: The route branch parses the address; every other mention must be
    #: through the helper. A `~walk/${…}` template literal anywhere but inside
    #: `walkLink` is a second spelling of one address.
    assert src.count("function walkLink(") == 1
    built = [m.start() for m in re.finditer(r"`~walk/\$\{", src)]
    assert len(built) == 1, "a walk address is built in more than one place"
    body = _function_body("walkLink")
    assert "`~walk/${" in body, "walkLink() no longer builds the address"
