"""A step tick records a check's verdict, and nothing about the ledger changes.

[[TASK-0624]]. The renderer holds a step's mark in the browser until every
step citing a check has one, then writes that check's verdict through the same
POST the row's mark button uses. Two things have to be true on this side of
that for the phase's first exit criterion to hold, and both are asserted here:

1. **The ledger's event shape is unchanged.** A verdict that arrived from a
   step is a verdict, indistinguishable in the file from one that arrived from
   a row — one event per check ([[ADR-0037]]), the same keys, the same
   validation. A step tick that quietly introduced a field would be the format
   change this phase put out of scope.
2. **A check's parts are the steps a procedure must cite**, and the page reads
   them from the bundled module rather than counting them itself. The
   renderer's holding rule — no verdict until every citing step is ticked — is
   only as correct as that set.

The equivalence itself (walking a sitting step by step writes the same events
as ticking its checks one by one) is asserted in
`desktop/tests/walk-page.test.mjs`, where the code that combines the marks
lives. It runs both paths against one stubbed POST and compares the bodies.
"""

from __future__ import annotations

import json
from pathlib import Path

from project_os_cockpit import acceptance, ledger


def _check(docs: Path, tid: str, *, area: str, body: str) -> None:
    (docs / "tests" / "acceptance").mkdir(parents=True, exist_ok=True)
    (docs / "tests" / "acceptance" / f"{tid}.md").write_text(
        f'---\ntype: "[[test]]"\nid: {tid}\ntitle: "{tid}"\n'
        f'level: acceptance\nstatus: active\narea: "{area}"\nmark: todo\n'
        f"---\n\n# {tid}\n\n{body}\n", encoding="utf-8")


def _working(docs: Path, platform: str) -> dict:
    path = docs / "releases" / "ledgers" / f"WORKING-{platform}.json"
    return json.loads(path.read_text(encoding="utf-8"))


# ------------------------------------------------------ the event is unchanged

def test_a_verdict_from_a_step_has_the_same_keys_as_one_from_a_row(
        tmp_path: Path) -> None:
    """The keys, pinned. A step tick adds none and drops none.

    `append` is the one write path, and the renderer reaches it through
    `/api/notes/mark-check` whether the walker ticked a row or a step. So the
    thing worth pinning is the event this produces: if a later change adds a
    field naming the step a verdict came from, this fails and somebody has to
    decide whether the ledger format is changing.
    """
    docs = tmp_path / "docs"
    (docs / "releases" / "ledgers").mkdir(parents=True, exist_ok=True)
    ledger.append(docs, "android", check="TST-0001", mark="pass",
                  by="user:edwin", method="manual", when="2026-09-14")
    ledger.append(docs, "android", check="TST-0002", mark="fail",
                  by="user:edwin", method="manual", when="2026-09-14",
                  reason="Step 3: the back gesture closed the app")

    entries = _working(docs, "android")["entries"]
    assert [sorted(e) for e in entries] == [
        ["by", "check", "date", "mark", "method"],
        ["by", "check", "date", "mark", "method", "reason"],
    ]
    #: One event per check, and the reason a failing step gave travels with
    #: the check's own verdict. The step number is IN the reason text, which
    #: is prose — not a field, which would be a format change.
    assert entries[1]["mark"] == "fail"
    assert entries[1]["reason"].startswith("Step 3:")


def test_a_failing_step_cannot_write_a_verdict_with_no_reason(
        tmp_path: Path) -> None:
    """`NEEDS_REASON` is the ledger's rule and the step path does not escape it.

    The renderer asks a failing step for its reason once and prefixes it to
    every check that step cites. If that ever stopped happening the write is
    refused here rather than landing a `fail` nobody can read back.
    """
    docs = tmp_path / "docs"
    (docs / "releases" / "ledgers").mkdir(parents=True, exist_ok=True)
    for mark in sorted(ledger.NEEDS_REASON):
        try:
            ledger.append(docs, "android", check="TST-0001", mark=mark,
                          by="user:edwin", method="manual", when="2026-09-14")
        except ledger.LedgerError as err:
            assert "needs a reason" in str(err)
        else:                                        # pragma: no cover
            raise AssertionError(f"a {mark} with no reason was accepted")


# ------------------------------------------- the parts a step tick settles

def test_a_checks_owed_parts_are_its_numbered_steps(tmp_path: Path) -> None:
    """What the renderer's holding rule counts, read from the bundled module.

    A check with numbered steps owes one part per step, so its verdict waits
    for every step citing one of them. A check whose procedure is an unheaded
    paragraph owes exactly one part, cited by its bare id — which is the shape
    most of `your-trainer`'s corpus is in.
    """
    walk = acceptance._walk_module()
    docs = tmp_path / "docs"
    _check(docs, "TST-0001", area="Bench",
           body="## Setup\nThe bench.\n\n## Steps\n1. Open it.\n2. Close it.\n\n"
                "## Expect\n- It opens.\n- It closes.")
    _check(docs, "TST-0002", area="Bench",
           body="Open the app and look at the splash screen.")
    checks = walk.load_checks(docs, None, tmp_path)

    assert walk.parts_of(checks["TST-0001"]) == [("TST-0001", "1"),
                                                 ("TST-0001", "2")]
    assert walk.parts_of(checks["TST-0002"]) == [("TST-0002", "")]


def test_one_owed_part_is_cited_by_exactly_one_step(tmp_path: Path) -> None:
    """The guarantee the renderer's `citing` map depends on.

    A part cited by two steps would leave the page with two ticks for one
    verdict and no rule about which wins. The module refuses such a procedure,
    and the page falls back to per-check rows — so this is the assertion that
    says the fallback is the only way that state can be reached.
    """
    walk = acceptance._walk_module()
    docs = tmp_path / "docs"
    _check(docs, "TST-0001", area="Bench",
           body="## Setup\nThe bench.\n\n## Steps\n1. Open it.\n\n"
                "## Expect\n- It opens.")
    (docs / "tests" / "acceptance" / "walk").mkdir(parents=True, exist_ok=True)
    (docs / "tests" / "acceptance" / "walk" / "bench.md").write_text(
        '---\ntype: "[[reference]]"\ntitle: "Procedure — The bench"\n'
        'status: active\nowner: user:fixture\nsitting: "The bench"\n---\n\n'
        "# Procedure — The bench\n\n## Setup\n\nThe bench powered.\n\n"
        "## Steps\n\n1. **Bench.** Open it.\n   - It opens. `TST-0001.1`\n"
        "2. **Bench.** Open it again.\n   - It opens. `TST-0001.1`\n",
        encoding="utf-8")
    (docs / "releases" / "ledgers").mkdir(parents=True, exist_ok=True)
    (docs / "releases" / "ledgers" / "WORKING-android.json").write_text(
        json.dumps({"platform": "android", "entries": []}), encoding="utf-8")
    (docs / "tests" / "acceptance" / "WALK.md").write_text(
        '---\ntype: "[[reference]]"\ntitle: "Walk order"\nstatus: active\n'
        'owner: user:fixture\n---\n\n# Walk order\n\n### The bench\n\n'
        '```yaml\nsurfaces: ["Bench"]\nstate: "The bench."\n```\n',
        encoding="utf-8")

    from project_os_cockpit.index import Index
    payload = acceptance.walk_payload(docs, Index.build(docs),
                                      platform="android")
    procedure = payload["sittings"][0]["procedure"]
    assert procedure["problems"], "two steps citing one part were accepted"
    assert "cited by steps 1, 2" in procedure["problems"][0]
