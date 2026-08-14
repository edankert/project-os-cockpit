"""Documentation history (FEAT-0052 / TASK-0255).

The overview's history band answered one question three ways — a weekly
edit count, the change notes, and the git log with notes as chips — and
all three read git or the filesystem as the *subject*. This payload
inverts it: the row is a note's **status transition** and the commit is
a **divider**.

Two properties carry the whole design and are asserted here rather than
described:

1. **A transition is not a touch.** Measured on this repo's phase-hygiene
   commit: 20 notes touched, 4 statuses changed. A touch-based list makes
   bookkeeping the largest event of the day.
2. **A commit with no transitions still appears.** It is the one a naive
   implementation drops for having no rows, and the one that most needs
   to be seen — code moved with nothing recording why (FEAT-0022).

The parser is exercised directly on log text rather than through a
fixture repo per case. Parsing is where this can be wrong, and a repo per
case would make the suite slow enough that nobody adds cases.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from project_os_cockpit import cockpit
from project_os_cockpit.cockpit import _parse_history_log, history_payload
from project_os_cockpit.index import Index

REPO_ROOT = Path(__file__).resolve().parents[1]
SEP = "\x01"


class _Rec:
    """Minimal stand-in for an index record."""

    def __init__(self, note_id: str, note_type: str = "task") -> None:
        self.note_id = note_id
        self.note_type = note_type
        self.title = f"{note_id} title"
        self.rel_path = f"tasks/{note_id}.md"
        self.status = "done"


def _resolve(path: str):  # type: ignore[no-untyped-def]
    name = path.rsplit("/", 1)[-1]
    return _Rec(name.split("-")[0] + "-" + name.split("-")[1]) if "-" in name else None


def _log(*commits: str) -> str:
    return "".join(commits)


def _commit(sha: str, subject: str, body: str = "") -> str:
    return f"{SEP}{sha}\t{sha}0000\t2026-07-30T10:00:00+00:00\tEdwin\t{subject}\n{body}"


def _file_diff(path: str, minus: str | None, plus: str | None) -> str:
    out = f"--- a/{path}\n+++ b/{path}\n@@ -6 +6 @@\n"
    if minus is not None:
        out += f"-status: {minus}\n"
    if plus is not None:
        out += f"+status: {plus}\n"
    return out


# ---- the parser -------------------------------------------------------

def test_a_moved_status_is_a_transition_with_both_ends() -> None:
    text = _log(_commit("aaa111", "close it",
                        _file_diff("docs/tasks/TASK-0001-X.md", "doing", "done")))
    commits = _parse_history_log(text, _resolve)
    assert len(commits) == 1
    t = commits[0]["transitions"][0]
    assert (t["from"], t["to"]) == ("doing", "done")
    assert t["created"] is False


def test_a_created_note_is_not_rendered_as_a_journey() -> None:
    """`+status: done` with no `-status:` means the note was BORN done.

    Most notes in a busy commit are written and closed in one pass, and
    an arrow would imply a history they never had.
    """
    text = _log(_commit("bbb222", "add it",
                        _file_diff("docs/tasks/TASK-0002-Y.md", None, "done")))
    t = _parse_history_log(text, _resolve)[0]["transitions"][0]
    assert t["created"] is True
    assert t["from"] is None
    assert t["to"] == "done"


def test_a_touch_that_changes_no_status_is_not_a_row() -> None:
    """The design's central claim, in miniature.

    A note whose `phase:` was corrected is not an event. Sixteen of the
    twenty notes in this repo's phase-hygiene commit were exactly that.
    """
    body = ("--- a/docs/tasks/TASK-0003-Z.md\n+++ b/docs/tasks/TASK-0003-Z.md\n"
            "@@ -7 +7 @@\n-phase: \"[[PHASE-999-Future]]\"\n"
            "+phase: \"[[PHASE-011-Unproven-Claims]]\"\n")
    commits = _parse_history_log(_log(_commit("ccc333", "re-home", body)), _resolve)
    assert commits[0]["transitions"] == []
    assert commits[0]["undocumented"] is True, (
        "a commit with no transitions must be reported, not dropped"
    )


def test_a_commit_with_no_transitions_is_still_returned() -> None:
    """The trap. A naive transition-based list drops it for having no
    rows — and a commit that moved code with nothing recording why is
    precisely the one worth seeing (FEAT-0022's guardrail)."""
    text = _log(
        _commit("ddd444", "code only", ""),
        _commit("eee555", "close it",
                _file_diff("docs/tasks/TASK-0004-W.md", "doing", "done")),
    )
    commits = _parse_history_log(text, _resolve)
    assert [c["sha"] for c in commits] == ["ddd444", "eee555"]
    assert commits[0]["undocumented"] is True
    assert commits[1]["undocumented"] is False


def test_one_commit_can_carry_several_transitions_one_per_file() -> None:
    body = (_file_diff("docs/tasks/TASK-0005-A.md", "doing", "done")
            + _file_diff("docs/tasks/TASK-0006-B.md", None, "backlog"))
    t = _parse_history_log(_log(_commit("fff666", "two", body)), _resolve)[0]
    assert len(t["transitions"]) == 2
    assert {x["to"] for x in t["transitions"]} == {"done", "backlog"}


def test_a_status_line_outside_any_file_is_ignored() -> None:
    """A commit *message* containing `+status: done` must not become a row."""
    text = _log(_commit("999zzz", "subject", "+status: done\n"))
    assert _parse_history_log(text, _resolve)[0]["transitions"] == []


def test_a_malformed_record_line_does_not_take_the_batch_down() -> None:
    text = f"{SEP}broken\n" + _commit(
        "aaa999", "ok", _file_diff("docs/tasks/TASK-0007-C.md", "doing", "done"))
    commits = _parse_history_log(text, _resolve)
    assert [c["sha"] for c in commits] == ["aaa999"]


# ---- against the real repository --------------------------------------

def test_the_payload_runs_on_this_repo_and_resolves_ids() -> None:
    index = Index.build(REPO_ROOT / "docs")
    payload = history_payload(REPO_ROOT, index, limit=10)
    assert payload["available"] is True
    assert payload["commits"], "this repo has history"
    ids = [t["id"] for c in payload["commits"] for t in c["transitions"]]
    assert any(i and i.startswith(("FEAT-", "TASK-", "ISS-", "PHASE-")) for i in ids), (
        "transitions resolve to note IDs, not bare paths"
    )


def test_transitions_are_fewer_than_touches_on_a_bookkeeping_commit() -> None:
    """The measurement the design rests on, asserted against real history.

    `cebee80` re-homed sixteen notes' `phase:` field and closed four
    things. The old commits tile shows 20 items for it; this shows 4.
    Skipped if that commit is not reachable (shallow clone, rewritten
    history) rather than asserted into a false failure.
    """
    probe = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "cat-file", "-e", "cebee80^{commit}"],
        capture_output=True, check=False,
    )
    if probe.returncode != 0:
        pytest.skip("cebee80 not in this clone's history")

    index = Index.build(REPO_ROOT / "docs")
    touched = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "show", "--name-only", "--format=", "cebee80"],
        capture_output=True, text=True, check=False,
    ).stdout.split()
    touched_notes = [p for p in touched if p.endswith(".md") and p.startswith("docs/")]

    payload = history_payload(REPO_ROOT, index, limit=40)
    match = [c for c in payload["commits"] if c["sha"].startswith("cebee80")]
    if not match:
        pytest.skip("cebee80 outside the fetched window")
    transitions = match[0]["transitions"]

    assert len(transitions) < len(touched_notes), (
        f"{len(transitions)} transitions vs {len(touched_notes)} notes touched — "
        "if these are equal the payload is counting touches, which is the "
        "thing this design replaced"
    )


def test_unavailable_rather_than_raising_outside_a_repo(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    payload = history_payload(tmp_path, Index.build(tmp_path / "docs"))
    assert payload["available"] is False
    assert payload["commits"] == [] and payload["uncommitted"] == []


def test_the_uncommitted_band_reflects_the_working_tree(tmp_path: Path) -> None:
    """"Not saved yet" is the half git history cannot answer."""
    repo = tmp_path / "r"
    (repo / "docs").mkdir(parents=True)
    (repo / "SNAPSHOT.yaml").write_text("counters: {}\n", encoding="utf-8")
    run = lambda *a: subprocess.run(  # noqa: E731
        ["git", "-C", str(repo), *a], capture_output=True, check=False)
    run("init", "-q")
    run("config", "user.email", "t@e.st")
    run("config", "user.name", "T")
    (repo / "docs" / "a.md").write_text("---\nstatus: doing\n---\n", encoding="utf-8")
    run("add", "-A")
    run("commit", "-qm", "first")

    index = Index.build(repo / "docs")
    assert history_payload(repo, index)["uncommitted"] == [], "clean tree, empty band"

    (repo / "docs" / "b.md").write_text("---\nstatus: done\n---\n", encoding="utf-8")
    band = history_payload(repo, index)["uncommitted"]
    assert [row["path"] for row in band] == ["docs/b.md"]


# ---- the contribution grid's payload (FEAT-0053 / TASK-0258) ----------

def test_activity_counts_transitions_per_day_on_this_repo() -> None:
    from project_os_cockpit.cockpit import activity_payload

    index = Index.build(REPO_ROOT / "docs")
    payload = activity_payload(REPO_ROOT, index)
    assert payload["available"] is True
    assert payload["days"], "this repo has history"
    assert payload["first_commit"] <= payload["last_commit"]
    for day, counts in payload["days"].items():
        assert len(day) == 10 and day[4] == "-", day
        assert counts["commits"] >= 1, "a day in the map had a commit"
        assert counts["transitions"] >= 0


def test_buckets_come_from_active_days_only() -> None:
    """Including the zero days puts every threshold at 0.

    Measured on this repo: 16 days carry any activity across 12 weeks.
    A scale computed over the calendar would place every lit cell in the
    top step — the saturation the relative scale exists to avoid.
    """
    from project_os_cockpit.cockpit import _quartile_buckets

    assert _quartile_buckets([]) == []
    cuts = _quartile_buckets(sorted([1, 6, 13, 29, 32, 38, 46, 64, 80, 89, 199]))
    assert len(cuts) == 3
    assert cuts[0] < cuts[1] < cuts[2], "the steps must be strictly increasing"
    assert cuts[2] < 199, "the busiest day must land above the top cut, not on it"


def test_buckets_stay_distinct_on_a_flat_distribution() -> None:
    """Four identical days would collapse three quartiles onto one value,
    leaving fewer than four usable steps."""
    from project_os_cockpit.cockpit import _quartile_buckets

    cuts = _quartile_buckets([5, 5, 5, 5])
    assert cuts[0] < cuts[1] < cuts[2], cuts


def test_activity_is_unavailable_outside_a_repo(tmp_path: Path) -> None:
    from project_os_cockpit.cockpit import activity_payload

    (tmp_path / "docs").mkdir()
    payload = activity_payload(tmp_path, Index.build(tmp_path / "docs"))
    assert payload["available"] is False
    assert payload["days"] == {}


def test_the_busiest_day_is_a_transition_count_not_a_commit_count() -> None:
    """The grid's unit is what got finished, not how often it was saved.

    Both are carried — commits go in the tooltip — but the intensity is
    transitions, so the darkest day is the day most things were done.
    """
    from project_os_cockpit.cockpit import activity_payload

    index = Index.build(REPO_ROOT / "docs")
    days = activity_payload(REPO_ROOT, index)["days"]
    busiest_t = max(days.values(), key=lambda d: d["transitions"])
    assert busiest_t["transitions"] > busiest_t["commits"], (
        "on this corpus the busiest day carries far more transitions than "
        "commits; if these are equal the payload is counting the wrong thing"
    )


def test_an_anchored_window_ends_at_the_requested_date() -> None:
    """TASK-0259's live-pass bug, guarded.

    The grid spans the whole history; a page shows 60 commits. Clicking
    2026-05-07 navigated to `~history` and scrolled — and landed on
    2026-07-28, the oldest commit that happened to be loaded, with
    nothing indicating anything had gone wrong.

    Anchoring the window at the date makes the day loaded by
    construction, so the scroll cannot miss.
    """
    from project_os_cockpit.cockpit import history_payload

    index = Index.build(REPO_ROOT / "docs")
    anchored = history_payload(REPO_ROOT, index, limit=5, until="2026-05-07")
    assert anchored["anchored_at"] == "2026-05-07"
    assert anchored["commits"], "the window should reach that date"
    assert all(c["date"] <= "2026-05-07" for c in anchored["commits"]), (
        "an anchored window must not contain commits after its date"
    )

    unanchored = history_payload(REPO_ROOT, index, limit=5)
    assert unanchored["anchored_at"] is None
    assert unanchored["commits"][0]["date"] > "2026-05-07", (
        "the default window is still the recent one"
    )


def test_an_anchored_window_suppresses_the_uncommitted_band() -> None:
    """Work in flight belongs to now.

    Showing today's unsaved edits above a window that ends in May would
    place them inside May — the same class of error as attributing a
    transition to the wrong commit.
    """
    from project_os_cockpit.cockpit import history_payload

    index = Index.build(REPO_ROOT / "docs")
    assert history_payload(REPO_ROOT, index, limit=3, until="2026-05-07")["uncommitted"] == []


def test_a_malformed_until_is_ignored_rather_than_passed_to_git() -> None:
    """`until` is the only caller-supplied value that reaches the argv."""
    from project_os_cockpit.cockpit import history_payload

    index = Index.build(REPO_ROOT / "docs")
    for bad in ("; rm -rf /", "yesterday", "2026-13-99x", ""):
        payload = history_payload(REPO_ROOT, index, limit=3, until=bad)
        assert payload["available"] is True, bad
        assert payload["anchored_at"] is None, bad


# ---- the unpublished run (FEAT-0100 / TASK-0418) ----------------------

def test_unpublished_commits_are_marked_by_identity_not_by_position(
    tmp_path: Path,
) -> None:
    """The middle rung of the ladder: saved, not published.

    Marked from the sha set rather than from the count. A surface given only
    "N are unpushed" would infer *the first N in the list*, which is true only
    while nothing filters or reorders the list — an assumption that costs
    nothing to avoid and is silently wrong the day it breaks.
    """
    from project_os_cockpit import git_state

    bare = tmp_path / "bare"
    bare.mkdir()
    subprocess.run(["git", "-C", str(bare), "init", "-q", "--bare",
                    "--initial-branch=main", "."], check=False)
    repo = tmp_path / "r"
    (repo / "docs").mkdir(parents=True)
    (repo / "SNAPSHOT.yaml").write_text("counters: {}\n", encoding="utf-8")
    run = lambda *a: subprocess.run(  # noqa: E731
        ["git", "-C", str(repo), *a], capture_output=True, check=False)
    run("init", "-q", "--initial-branch=main")
    run("config", "user.email", "t@e.st")
    run("config", "user.name", "T")
    run("config", "commit.gpgsign", "false")
    (repo / "docs" / "a.md").write_text("---\nstatus: doing\n---\n", encoding="utf-8")
    run("add", "-A")
    run("commit", "-qm", "published one")
    run("remote", "add", "origin", str(bare))
    run("push", "-q", "-u", "origin", "main")

    # …then two commits nobody has sent.
    for name in ("b", "c"):
        (repo / "docs" / f"{name}.md").write_text(
            "---\nstatus: done\n---\n", encoding="utf-8")
        run("add", "-A")
        run("commit", "-qm", f"unpublished {name}")

    git_state.clear_cache()
    index = Index.build(repo / "docs")
    payload = history_payload(repo, index)

    marked = [c["subject"] for c in payload["commits"] if c.get("unpublished")]
    assert marked == ["unpublished c", "unpublished b"], payload["commits"]
    published = [c["subject"] for c in payload["commits"] if not c.get("unpublished")]
    assert published == ["published one"]
    # A local path is not a forge, so it classifies as a deploy target — the
    # safe default for "I do not recognise this" — and the surface must be
    # told which, because one offers a button and the other refuses.
    assert payload["remote_kind"] == "deploy"


def test_a_repo_with_nothing_unpublished_marks_nothing(tmp_path: Path) -> None:
    """Absent, never a flag reading `false` on every row."""
    from project_os_cockpit import git_state

    repo = tmp_path / "r"
    (repo / "docs").mkdir(parents=True)
    (repo / "SNAPSHOT.yaml").write_text("counters: {}\n", encoding="utf-8")
    run = lambda *a: subprocess.run(  # noqa: E731
        ["git", "-C", str(repo), *a], capture_output=True, check=False)
    run("init", "-q", "--initial-branch=main")
    run("config", "user.email", "t@e.st")
    run("config", "user.name", "T")
    (repo / "docs" / "a.md").write_text("---\nstatus: doing\n---\n", encoding="utf-8")
    run("add", "-A")
    run("commit", "-qm", "only")

    git_state.clear_cache()
    payload = history_payload(repo, Index.build(repo / "docs"))
    assert all("unpublished" not in c for c in payload["commits"])
    # No remote at all: a different and worse fact than "nothing to publish".
    assert payload["remote_kind"] == "none"


def test_the_unpublished_total_is_not_the_windows_marks(tmp_path: Path) -> None:
    """The count a push button may legally show.

    A push publishes the whole run, so a label counted from the commits a
    window happens to have loaded is a button that offers less than it does —
    measured live at 6 against 7 on the overview tile, whose window is a
    handful.
    """
    from project_os_cockpit import git_state

    bare = tmp_path / "bare"
    bare.mkdir()
    subprocess.run(["git", "-C", str(bare), "init", "-q", "--bare",
                    "--initial-branch=main", "."], check=False)
    repo = tmp_path / "r"
    (repo / "docs").mkdir(parents=True)
    (repo / "SNAPSHOT.yaml").write_text("counters: {}\n", encoding="utf-8")
    run = lambda *a: subprocess.run(  # noqa: E731
        ["git", "-C", str(repo), *a], capture_output=True, check=False)
    run("init", "-q", "--initial-branch=main")
    run("config", "user.email", "t@e.st")
    run("config", "user.name", "T")
    (repo / "docs" / "a.md").write_text("---\nstatus: doing\n---\n", encoding="utf-8")
    run("add", "-A")
    run("commit", "-qm", "base")
    run("remote", "add", "origin", str(bare))
    run("push", "-q", "-u", "origin", "main")
    for i in range(5):
        (repo / "docs" / f"n{i}.md").write_text(
            "---\nstatus: done\n---\n", encoding="utf-8")
        run("add", "-A")
        run("commit", "-qm", f"unpublished {i}")

    git_state.clear_cache()
    index = Index.build(repo / "docs")
    window = history_payload(repo, index, limit=2)
    assert len([c for c in window["commits"] if c.get("unpublished")]) == 2
    assert window["unpublished_count"] == 5, (
        "the total is the run's, not the window's"
    )


def test_an_unknown_publication_count_is_not_reported_as_zero(tmp_path: Path) -> None:
    """ADR-0027's fourth admission test, on the obligation that shipped without it.

    A branch with no upstream makes `git rev-list @{u}..HEAD` fail, so `ahead`
    is None — the count could not be taken. Every surface turned that into 0:
    the registry emitted no rows, `history_payload` returned `unpublished_count:
    0`, and the attention card coerced `null ?? 0` and skipped. Three silent
    zeros on a repo whose commits had nowhere to go.

    TASK-0415's opening paragraph names this very test as the obligation's gate,
    and independent review demonstrated the failure on 2026-08-14 against a real
    repo with a real remote and no upstream.

    Unknown is not zero, and the difference is the whole point of the registry:
    zero means nothing needs you, unknown means nobody can tell.
    """
    from project_os_cockpit import git_state, obligations

    repo = tmp_path / "r"
    (repo / "docs").mkdir(parents=True)
    (repo / "SNAPSHOT.yaml").write_text("counters: {}\n", encoding="utf-8")
    run = lambda *a: subprocess.run(  # noqa: E731
        ["git", "-C", str(repo), *a], capture_output=True, check=False)
    run("init", "-q", "--initial-branch=feature-x")
    run("config", "user.email", "t@e.st")
    run("config", "user.name", "T")
    run("config", "commit.gpgsign", "false")
    # A real remote, so `kind` resolves — but the branch tracks nothing.
    run("remote", "add", "origin", "git@github.com:someone/thing.git")
    (repo / "docs" / "a.md").write_text("---\nstatus: doing\n---\n", encoding="utf-8")
    run("add", "-A")
    run("commit", "-qm", "one")

    git_state.clear_cache()
    state = git_state.read(repo)
    assert state.kind == "backup", "the remote should still be classified"
    assert state.ahead is None, (
        "this fixture is meant to produce an UNKNOWN count; if git now answers "
        "for a branch with no upstream, the test no longer probes what it says"
    )

    index = Index.build(repo / "docs")

    # 1. The registry counts it as something a person must resolve.
    assert obligations.counts(index).get("overview", 0) >= 1, (
        "an unknown publication state produced no obligation, so the badge "
        "reads the same as a repo with nothing to push"
    )
    rows = [r for rows in obligations.owed_items(index).values() for r in rows
            if "commit" in str(r.get("type", ""))]
    assert rows and rows[0]["detail"] == "unknown", (
        "the row must say the count is unknown rather than assert a number"
    )

    # 2. History reports the absence of a count, not a count of zero.
    payload = history_payload(repo, index)
    assert payload["unpublished_count"] is None
    assert payload["publication_known"] is False

    # 3. A KNOWN zero still reports zero — the guard must not make every repo
    #    unknown, which would be the same failure wearing the other hat.
    bare = tmp_path / "bare"
    bare.mkdir()
    subprocess.run(["git", "-C", str(bare), "init", "-q", "--bare",
                    "--initial-branch=feature-x", "."], check=False)
    run("remote", "set-url", "origin", str(bare))
    run("push", "-q", "-u", "origin", "feature-x")
    # The reading is cached for CACHE_SECONDS, so without this the second half
    # of the test would re-read the first half's answer and pass for the wrong
    # reason — asserting the cache rather than the code.
    git_state.clear_cache()
    known = history_payload(repo, Index.build(repo / "docs"))
    assert known["publication_known"] is True
    assert known["unpublished_count"] == 0
