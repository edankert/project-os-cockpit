"""The fleet's publication pass — one walk, one implementation (TASK-0422).

[[ISS-0165]]: *"one walk, so two surfaces cannot disagree"* was
[[FEAT-0100]]'s claim and false of the code. The badge and History read
``git_state.py``; the shell's attention card and fleet roll-up read an
independent TypeScript implementation on its own clock; ``fleet_validate``
carried a third that nobody read. This module is what the shell calls now, and
these are the tests that keep it the only walk.

Real repositories, no mocks — the same reason ``desktop/tests/git-state.test
.mjs`` uses real git: the defect was invisible to every existing test because
nothing asserted the property, and a mock would have been written by whoever
misunderstood it.
"""

from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _code_only(path: Path) -> str:
    """A module's code with its comments and docstrings removed.

    Written because the structural guard below failed against the very change
    it was written for: `fleet_git.py`'s own docstring explains that it does
    not run `git rev-list`, and *naming the command satisfied the search for
    it*. The same trap caught the TypeScript twin of this guard an hour
    earlier, in the opposite direction.

    A guard that a comment can satisfy — or break — is measuring prose. Real
    string literals survive, because `"--porcelain"` in an argv is exactly
    what these assertions are looking for.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if not isinstance(body, list) or not body:
            continue
        if not isinstance(node, (ast.Module, ast.ClassDef,
                                 ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        first = body[0]
        if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) \
                and isinstance(first.value.value, str):
            body.pop(0)
    return ast.unparse(tree)


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True, text=True, check=True,
    ).stdout.strip()


def _init(repo: Path) -> None:
    repo.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", "--initial-branch=main", str(repo)], check=True)
    for key, value in (("user.email", "t@e.st"), ("user.name", "T"),
                       ("commit.gpgsign", "false")):
        _git(repo, "config", key, value)


def _commit(repo: Path, rel: str, text: str) -> None:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", f"add {rel}")


def _tracked_repo(tmp_path: Path, name: str, *, ahead: int = 0) -> Path:
    bare = tmp_path / f"{name}.git"
    repo = tmp_path / name
    subprocess.run(["git", "init", "-q", "--bare", str(bare)], check=True)
    _init(repo)
    _commit(repo, "SNAPSHOT.yaml", "project:\n  name: t\n")
    _git(repo, "remote", "add", "origin", str(bare))
    _git(repo, "push", "-q", "-u", "origin", "main")
    for i in range(ahead):
        _commit(repo, f"docs/c{i}.md", f"# {i}\n")
    return repo


def test_one_json_line_per_repo(tmp_path: Path, capsys) -> None:
    """The wire format the shell parses, and the shape it keys on."""
    from project_os_cockpit import fleet_git

    a = _tracked_repo(tmp_path, "a", ahead=2)
    b = _tracked_repo(tmp_path, "b")

    assert fleet_git.main([str(a), str(b)]) == 0
    lines = [json.loads(x) for x in capsys.readouterr().out.splitlines() if x.strip()]

    assert [line["root"] for line in lines] == [str(a), str(b)]
    assert lines[0]["ahead"] == 2
    assert lines[1]["ahead"] == 0
    assert lines[0]["remote_kind"] == "deploy", "a local bare path is not a forge"


def test_an_unreadable_repo_does_not_kill_the_batch(tmp_path: Path, capsys) -> None:
    """A fleet is other people's repositories and one is always mid-something."""
    from project_os_cockpit import fleet_git

    good = _tracked_repo(tmp_path, "good", ahead=1)

    assert fleet_git.main([str(tmp_path / "nope"), str(good)]) == 0
    lines = [json.loads(x) for x in capsys.readouterr().out.splitlines() if x.strip()]

    assert len(lines) == 2, "the missing repo still gets a line — silence would "\
                            "drop it from the fleet without saying so"
    assert lines[0]["ahead"] is None
    assert lines[1]["ahead"] == 1


def test_no_upstream_is_null_not_zero(tmp_path: Path, capsys) -> None:
    """ADR-0027's fourth admission test, at the source of the number.

    A real remote and a branch tracking nothing: `rev-list @{u}..HEAD` cannot
    run. `0` here would mean "nothing to publish" — the one thing that is not
    known — and it is what reached the shell's card until 2026-08-14.
    """
    from project_os_cockpit import fleet_git

    repo = tmp_path / "loose"
    _init(repo)
    _commit(repo, "SNAPSHOT.yaml", "project:\n  name: t\n")
    _git(repo, "remote", "add", "origin", "https://github.com/example/x.git")

    assert fleet_git.main([str(repo)]) == 0
    row = json.loads(capsys.readouterr().out.strip())

    assert row["remote_kind"] == "backup", "the remote is real and classifiable"
    assert row["ahead"] is None


def test_dirty_is_the_record_scope(tmp_path: Path, capsys) -> None:
    """`docs/` and `SNAPSHOT.yaml`, because History's band counts exactly that.

    Two numbers behind one word on two surfaces describing one project is the
    defect FEAT-0100 kept finding; the scope is part of the shared walk now
    rather than repeated at each caller.
    """
    from project_os_cockpit import fleet_git

    repo = _tracked_repo(tmp_path, "flight")
    (repo / "docs").mkdir(exist_ok=True)
    (repo / "docs" / "note.md").write_text("# wip\n", encoding="utf-8")
    (repo / "src").mkdir(exist_ok=True)
    (repo / "src" / "app.py").write_text("x = 1\n", encoding="utf-8")

    assert fleet_git.main([str(repo)]) == 0
    row = json.loads(capsys.readouterr().out.strip())

    assert row["dirty"] == 1, "code outside the record is somebody else's count"


def test_the_shell_and_the_badge_read_the_same_module() -> None:
    """Not "the numbers match" — the same call, asserted structurally.

    Two implementations agree until one of them changes, and on 2026-08-14 one
    did: the unknown-count repair landed in `git_state.py` and the shell went
    on rendering a count nobody could take as nothing owed. So what is checked
    here is that there is nothing left to diverge.
    """
    from project_os_cockpit import fleet_git, fleet_validate, git_state, obligations

    src = _code_only(REPO_ROOT / "src" / "project_os_cockpit" / "fleet_git.py")
    assert "rev-list" not in src and "porcelain" not in src, (
        "fleet_git walks git itself — it must ask git_state, which is the "
        "module the badge reads"
    )
    assert fleet_validate.remote_kind is git_state.remote_kind, (
        "fleet_validate carries its own copy of the classification again"
    )
    validate_src = _code_only(
        REPO_ROOT / "src" / "project_os_cockpit" / "fleet_validate.py")
    assert "rev-list" not in validate_src, (
        "fleet_validate counts commits again — that was the third "
        "implementation, and the one nobody read"
    )
    # And the badge's own path is unchanged: `_publication_rows` reads
    # `git_state` directly.
    assert "git_state" in (
        REPO_ROOT / "src" / "project_os_cockpit" / "obligations.py"
    ).read_text()
    assert obligations.PUSH_OBLIGATION_KIND in obligations.KIND_NOUNS
    assert fleet_git.git_state is git_state


def _renderer_code_only() -> str:
    """`renderer.ts` with its comments removed — see :func:`_code_only`."""
    raw = (REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.ts").read_text(
        encoding="utf-8")
    import re

    without_blocks = re.sub(r"/\*[\s\S]*?\*/", "", raw)
    return "\n".join(
        line for line in without_blocks.split("\n")
        if not line.strip().startswith("//")
    )


def test_the_renderer_never_turns_an_unknown_count_into_a_zero() -> None:
    """TASK-0421 — the half of ISS-0165 that was already visibly wrong.

    `git_state.py` and the badge were repaired on 2026-08-14 to emit an
    explicit *publication state unknown* row. Both renderer surfaces coerced
    the same null to `0` and then dropped it for being `<= 0`, so a repo with
    a real remote and no upstream counted one obligation on the badge and
    appeared nowhere on the card or the roll-up.

    A source guard because these are DOM builders with no test seam, and the
    property is *the coercion does not exist* — which no behavioural test can
    state. The node suite covers the payload that feeds them.
    """
    code = _renderer_code_only()

    assert "typeof row.ahead === 'number' ? row.ahead : 0" not in code, (
        "the attention card coerces an unknown count to zero again — the "
        "ADR-0027 admission-test-4 failure ISS-0165 names"
    )
    assert "publish?: { ahead: number | null;" in code, (
        "the card's publication type must carry the unknown, not a number"
    )
    fn = code.split("function publicationText(")[1].split("\n}")[0]
    assert "ahead === null" in fn, (
        "publicationText must have a sentence for the count nobody can take; "
        "it is the one place a count becomes words"
    )
    assert "unknownAhead" in code, (
        "the fleet roll-up must list repos with a remote and no upstream — "
        "they fall between `behind` (needs a number) and `noRemote` (needs "
        "no remote), so without this they render as nothing at all"
    )


def test_the_entrypoint_runs_as_a_subprocess(tmp_path: Path) -> None:
    """`python -m project_os_cockpit.fleet_git` is how the shell spawns it."""
    repo = _tracked_repo(tmp_path, "sub", ahead=3)

    proc = subprocess.run(
        [sys.executable, "-m", "project_os_cockpit.fleet_git", str(repo)],
        capture_output=True, text=True, timeout=120, cwd=str(REPO_ROOT),
    )

    assert proc.returncode == 0, proc.stderr
    row = json.loads(proc.stdout.strip().splitlines()[0])
    assert row["root"] == str(repo)
    assert row["ahead"] == 3


def test_no_arguments_is_an_error_not_an_empty_success() -> None:
    """An empty fleet and a mis-spawned pass must not look alike."""
    from project_os_cockpit import fleet_git

    assert fleet_git.main([]) == 2


def test_the_pass_is_read_only(tmp_path: Path, capsys) -> None:
    """It runs inside repositories this app does not own.

    Asserted rather than promised: the shell spawns this for every discovered
    workspace, and `fleet_validate` carries the same guard for the same
    reason.
    """
    from project_os_cockpit import fleet_git

    repo = _tracked_repo(tmp_path, "readonly", ahead=1)
    before = _git(repo, "rev-parse", "HEAD")
    (repo / "docs").mkdir(exist_ok=True)
    (repo / "docs" / "wip.md").write_text("# wip\n", encoding="utf-8")
    status_before = _git(repo, "status", "--porcelain")

    assert fleet_git.main([str(repo)]) == 0
    capsys.readouterr()

    assert _git(repo, "rev-parse", "HEAD") == before
    assert _git(repo, "status", "--porcelain") == status_before

    src = _code_only(REPO_ROOT / "src" / "project_os_cockpit" / "fleet_git.py")
    for writing in ("commit", "push", "checkout", "reset", "clean", "stash"):
        assert f"'{writing}'" not in src, f"fleet_git names `git {writing}`"
