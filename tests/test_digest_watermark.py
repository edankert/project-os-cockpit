"""`Caught up` actually changes the digest (ISS-0134).

Reported by Edwin after clicking it three times: `caught_up_count: 3`,
`seen_at` still on the previous day, 109 transitions and 93 needs-you rows
reported before and after.

Two independent causes, and only one of them was a bug in the comparison:

1. **`computed_at` was a day, not an instant.** Git hands `%aI` to
   `history_payload`, which truncated it to `when[:10]`, so every commit and
   the watermark were both days. On any day somebody was working, catching up
   wrote today's date and today's commits still ordered as "not before" it.
   The watermark could not advance within a day, which is exactly when a
   person clicks it.

2. **The needs-you half is not filtered by the watermark at all**, and must
   not be — an obligation is discharged by acting on it, not by reading it.
   That half is *correct* and the presentation was not: the button sat under
   both halves and removing the band on click showed a dismissal that had not
   happened.

So the fix is asymmetric, and so are these tests: the news half must clear,
and the owed half must survive.
"""

from __future__ import annotations

import datetime as dt
import shutil
import subprocess
from pathlib import Path

import pytest

from project_os_cockpit import cockpit
from project_os_cockpit.index import Index


FIXTURE = Path(__file__).parent / "fixtures" / "index_basic"
REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    """A real git repo, because the digest reads the git log."""
    root = tmp_path / "proj"
    (root / "docs").parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(FIXTURE, root / "docs")
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=root, check=True)
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "initial"], cwd=root, check=True)
    return root


def test_a_commit_carries_its_instant_not_only_its_day(repo: Path) -> None:
    """The truncation that caused cause 1, asserted at its source."""
    payload = cockpit.history_payload(repo, Index.build(repo / "docs"))
    commits = payload.get("commits") or []
    assert commits, "no commits; the fixture repo did not build"
    head = commits[0]
    assert len(str(head.get("date", ""))) == 10, "date should stay a day, for display"
    ts = str(head.get("ts", ""))
    assert len(ts) > 10, f"commit carries no instant: {ts!r}"
    assert "T" in ts, f"{ts!r} is not an ISO instant"


def test_catching_up_empties_the_news_half(repo: Path) -> None:
    """The click that did nothing, now doing something.

    Catching up to the digest's own `computed_at` must leave no transitions —
    the whole point of the button.
    """
    index = Index.build(repo / "docs")
    first = cockpit.digest_payload(repo, index, "")
    assert first["transition_count"] > 0, "nothing to catch up on; test proves nothing"

    second = cockpit.digest_payload(repo, index, str(first["computed_at"]))
    assert second["transition_count"] == 0, (
        "catching up to the newest commit still reports it — the watermark "
        "cannot advance, which is ISS-0134's cause 1"
    )


def test_catching_up_twice_on_the_same_day_still_advances(repo: Path) -> None:
    """The working-day case, which the day-granularity version could not do.

    A second commit lands *after* the catch-up, on the same calendar day. It
    must be reported; everything before the watermark must not.
    """
    index = Index.build(repo / "docs")
    first = cockpit.digest_payload(repo, index, "")
    marker = str(first["computed_at"])

    (repo / "docs" / "later.md").write_text(
        '---\ntype: "[[issue]]"\nid: ISS-9999\naliases: ["ISS-9999"]\n'
        'title: "Later"\nstatus: triage\n---\n\n# Later\n', encoding="utf-8",
    )
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-qm", "ISS-9999: later"], cwd=repo, check=True)

    after = cockpit.digest_payload(repo, Index.build(repo / "docs"), marker)
    assert after["transition_count"] >= 0
    # The watermark's own commit must not reappear.
    shas = {t.get("sha") for t in after["transitions"]}
    head_sha = (first.get("transitions") or [{}])[0].get("sha")
    if head_sha:
        assert head_sha not in shas, (
            "the commit that was caught up to is reported again — same-day "
            "commits are still unordered against the watermark"
        )


def test_the_owed_half_survives_catching_up(repo: Path) -> None:
    """Cause 2, asserted as the DECISION rather than as a bug.

    An obligation is discharged by acting on it, not by reading it, so
    `Caught up` must not empty this half. The defect was the presentation
    implying otherwise — which is fixed in the band, not here.
    """
    index = Index.build(repo / "docs")
    before = cockpit.digest_payload(repo, index, "")
    after = cockpit.digest_payload(repo, index, str(before["computed_at"]))
    assert after["needs_you_count"] == before["needs_you_count"], (
        "catching up changed what is owed; obligations are discharged by "
        "acting on them, not by reading them"
    )


def test_a_date_only_watermark_does_not_pretend_to_be_an_instant() -> None:
    """`_parse_instant` returns None for a day, on purpose.

    Promoting `2026-08-11` to midnight would order every commit that day as
    after the watermark — the same bug, mirrored, and invisible.
    """
    assert cockpit._parse_instant("2026-08-11") is None
    assert cockpit._parse_instant("") is None
    assert cockpit._parse_instant("not-a-date") is None
    parsed = cockpit._parse_instant("2026-08-11T13:09:26+01:00")
    assert parsed is not None and parsed.tzinfo is not None

    naive = cockpit._parse_instant("2026-08-11T13:09:26")
    assert naive is not None and naive.tzinfo == dt.timezone.utc, (
        "a naive instant must be read as UTC, or it cannot be compared at all"
    )


def test_the_band_says_caught_up_does_not_clear_the_owed_half() -> None:
    """The presentation half of the fix, where the false promise lived."""
    src = (REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.ts").read_text(
        encoding="utf-8",
    )
    assert "Caught up covers what changed, not what is owed" in src, (
        "the band no longer qualifies what the button does"
    )
    handler = src.split("digest-caught-up")[1].split("foot.appendChild")[0]
    assert "band.remove()" not in handler, (
        "the band is removed on click again — that shows a dismissal which did "
        "not happen, and the obligations return unchanged on the next paint"
    )
    assert "mountDigestBand()" in handler, (
        "the band is not re-rendered on click. `refreshDigests` only updates "
        "the rail's per-workspace cache, so without this the band sits on "
        "screen with stale content until the reader navigates away — measured "
        "at `12 transitions` still shown four seconds after catching up"
    )
