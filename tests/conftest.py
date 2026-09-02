"""Fixtures shared across the suite.

`owed_corpus` moved here from `test_tests_view.py` on 2026-08-13 (TASK-0416),
when a second module needed it. Copying it would have been the same mistake
that task exists to remove from the production code: two derivations of one
thing, agreeing by coincidence until they stop.
"""

from __future__ import annotations

import datetime as _dt
import re as _re
import shutil
from pathlib import Path

import pytest

from project_os_cockpit.index import Index

REPO_ROOT = Path(__file__).resolve().parent.parent
REPO_DOCS = REPO_ROOT / "docs"


def js_function_body(src: str, signature: str) -> str:
    """The source of one JS function, bounded by its OWN closing brace.

    Shared here because the alternative — `src[i:i + 2600]` — has now failed in
    both directions in this suite, and 21 more call sites still use it.

    * **Too short.** `test_the_address_still_wins_on_navigation` asserted over
      3000 characters of `renderChecksPage`; the guard it checks for sits at
      offset 3002. The function grew by two characters and a green test went
      red with the behaviour untouched ([[ISS-0275]]).
    * **Too long.** `test_release_held_back.py` records the same window
      spilling 469,293 characters past its anchor — independent review put a
      live `askForMark` call at anchor + 2621 and the test still passed.

    A window is a guess about a distance. This counts braces, which is the
    boundary the language actually has.

    **The body opens after the parameter list, not at the first `{`.**
    `test_release_page._body_of` takes the first `{` following the signature,
    and this was lifted from it. That is wrong for a destructured parameter:
    `renderChecksPage(tier, area, { keepFilters = false } = {})` opens and
    closes a brace before the body starts, so the "body" came back 84
    characters long and the test still failed — for a new reason, wearing the
    old one's message. Found by rerunning rather than by reading. The parameter
    list is walked by paren depth first, and only then is a brace the body's.
    """
    start = src.index(signature)
    paren = src.index("(", start)
    depth = 0
    for i in range(paren, len(src)):
        if src[i] == "(":
            depth += 1
        elif src[i] == ")":
            depth -= 1
            if depth == 0:
                paren = i
                break
    else:
        raise AssertionError("%s: parameter list never closes" % signature)

    depth = 0
    for i in range(src.index("{", paren), len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                return src[start:i + 1]
    raise AssertionError("%s never closes" % signature)


#: A corpus with a real stub and a real proposed ADR, built rather than
#: borrowed. Five tests once asserted the live corpus's *state* — "ARCHITECTURE
#: holds its template", "some ADR is proposed" — and all five broke on
#: 2026-08-12 for reasons that were not defects: Edwin decided three ADRs in
#: the app, and ISS-0153 fixed a false stub. **A vacuity guard against a live
#: corpus is a test that expires when the project makes progress.**
@pytest.fixture()
def owed_corpus(tmp_path: Path) -> Index:
    docs = tmp_path / "docs"
    shutil.copytree(REPO_DOCS, docs)
    (tmp_path / "SNAPSHOT.yaml").write_text("project:\n  name: probe\n", encoding="utf-8")
    # A document that really does hold its template.
    (docs / "GLOSSARY.md").write_text(
        '---\ntype: "[[reference]]"\nid: GLOSSARY\nupdated: 2026-08-12\n---\n\n'
        "# Glossary\n\n- <Term>: <what it means>\n- <Another>: <what it means>\n",
        encoding="utf-8",
    )
    # …a document nobody has confirmed in a long time — constructed, because
    # on 2026-08-12 the corpus stopped having one: every standing document was
    # brought current, and a test that waits for neglect fails when the
    # project stops being neglectful.
    old_day = (_dt.date.today() - _dt.timedelta(days=400)).isoformat()
    styleguide = docs / "STYLEGUIDE.md"
    styleguide.write_text(
        _re.sub(r"^updated: .*$", f"updated: {old_day}",
                styleguide.read_text(encoding="utf-8"), count=1, flags=_re.M),
        encoding="utf-8",
    )
    # …and a decision still awaiting one.
    (docs / "decisions" / "ADR-9002-Probe.md").write_text(
        '---\ntype: "[[adr]]"\nid: ADR-9002\naliases: ["ADR-9002"]\n'
        'title: "A probe decision awaiting a human"\nstatus: "proposed"\n'
        "owner: user:edwin\ncreated: 2026-08-12\nupdated: 2026-08-12\n---\n\n"
        "# A probe decision\n\nIt awaits a person.\n",
        encoding="utf-8",
    )
    return Index.build(docs)
