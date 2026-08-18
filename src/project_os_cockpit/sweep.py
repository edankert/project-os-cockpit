"""The acceptance sweep at close-out (FEAT-0115 / TASK-0467).

**The benchmark is the corpus's own hand commit.** `a4577c01` in
`../your-trainer` — *"cover TASK-0383..0387 + uncheck overlapping rows"* — six
checks added, three invalidated, **one commit**. Somebody did that by hand, and
the model works. What does not work is the half of it that has no tooling: 54
rows across the fleet carry a hand-written `RE-RUN (…)` annotation and **all 54
are still ticked**, because unticking destroyed the only record that the check
had ever passed and there was nowhere to say why.

So this module reproduces that commit's shape with tooling. One Save writes N
new `CHK-*` notes, M invalidations, and one line on the feature — and commits
them together, because a sweep split across three commits is three chances to
stop halfway.

**What it must never do** is make a check owed. ADR-0030 forbids per-check
obligations outright; the feature owes the sweep, the checks owe nothing, and
`acceptance_impact:` is the one line that discharges it.
"""

from __future__ import annotations

import datetime as _dt
import re
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, Any

from . import acceptance
from .note_writes import WriteError, resolve_note

if TYPE_CHECKING:  # pragma: no cover
    from .index import Index

#: The three states `acceptance_impact:` may hold, as a pattern. A date, or
#: `none` with a reason. Anything else is refused rather than written: the
#: whole value of three states over a boolean is that each one says something,
#: and `none` with no reason says exactly what a boolean said.
_IMPACT_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_IMPACT_NONE_RE = re.compile(r"^none\s*[—–-]\s*(.+)$", re.I)


def impact_state(value: str) -> str:
    """`swept` / `none` / `owed` — the three states, named.

    Read from one place so a surface, the obligation and the refusal cannot
    each decide for themselves what an authored line means.
    """
    text = (value or "").strip()
    if not text:
        return "owed"
    if _IMPACT_DATE_RE.match(text):
        return "swept"
    if _IMPACT_NONE_RE.match(text):
        return "none"
    return "owed"


def _today() -> str:
    return _dt.date.today().isoformat()


def _feature(index: "Index", feature_id: str) -> Any:
    path = resolve_note(index, feature_id)
    record = index.get(path)
    if record is None or (record.note_type or "") != "feature":
        raise WriteError(
            f"{feature_id} is a {(record.note_type if record else None) or 'note'}, "
            "not a feature — the acceptance sweep is scoped to a feature",
            status=409,
        )
    return record


def _subject_ids(index: "Index", record: Any) -> set[str]:
    """The feature, plus every task and issue it owns.

    An invalidation names *the change*, and Edwin's own correction is that the
    coupling runs through invalidation rather than naming: a check is rarely
    invalidated by "the feature" and usually by one of its tasks. The corpus
    agrees — of the fleet's 54 annotations, 39 name a `TASK-*` and 8 a `FEAT-*`.
    """
    ids = {record.note_id or ""}
    for field in ("tasks", "fixes", "issues"):
        raw = record.frontmatter.get(field) or []
        values = raw if isinstance(raw, (list, tuple)) else [raw]
        for value in values:
            for found in re.findall(r"\b([A-Z]{2,6}-\d{3,4})\b", str(value)):
                ids.add(found)
    return {i for i in ids if i}


def candidates(index: "Index", feature_id: str) -> dict[str, Any]:
    """What the sweep offers, in three lists — and why they are three.

    **originated** — checks whose `covers:` names this feature. These are the
    ones the feature is directly answerable for.

    **invalidated** — checks already carrying an `invalidated_by:` naming this
    feature or one of its tasks. Shown so a second sweep does not re-invalidate
    what the first one already did, and so the record of the first is visible.

    **in areas** — checks sharing an area with an originated check. This is the
    overlap TESTING.md rule 3 is actually about (*"unchecks all tests whose
    scope overlaps"*), and it is deliberately a HEURISTIC offered to a person
    rather than an inference acted on: nothing here is invalidated unless
    somebody ticks it.

    A feature with all three empty is the normal case and not a failure — Edwin:
    *"not all features might need acceptance tests."* The surface says so in
    words rather than rendering an empty page.
    """
    record = _feature(index, feature_id)
    suite = acceptance.load(index.docs_root, index)
    subjects = _subject_ids(index, record)

    originated = [i for i in suite.items if feature_id in i.refs]
    invalidated = [
        i for i in suite.items
        if i.invalidated.change and i.invalidated.change in subjects
        and i not in originated
    ]
    areas = {i.area for i in originated if i.area}
    seen = {id(i) for i in originated} | {id(i) for i in invalidated}
    in_areas = [i for i in suite.items if i.area in areas and id(i) not in seen]

    return {
        "feature": {
            "id": record.note_id or feature_id,
            "title": record.title or "",
            "status": record.status or "",
            "rel": record.rel_path,
            "acceptance_impact": str(
                record.frontmatter.get("acceptance_impact") or "").strip(),
            "impact_state": impact_state(
                str(record.frontmatter.get("acceptance_impact") or "")),
        },
        "subjects": sorted(subjects),
        "exists": suite.exists,
        "shape": suite.shape,
        "originated": [acceptance._row(i) for i in originated],
        "invalidated": [acceptance._row(i) for i in invalidated],
        "in_areas": [acceptance._row(i) for i in in_areas],
        # Every area in the suite, so a new check can be filed under one that
        # already exists rather than minting a fourteenth spelling of "The
        # navigator". Ordered by the suite, not alphabetically: the order a
        # walker reads them in is the order they should be offered in.
        "areas": _areas(suite),
    }


def _areas(suite: acceptance.Suite) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in suite.items:
        key = (item.tier, item.section, item.area)
        if any((a["tier"], a["section"], a["area"]) == key for a in out):
            continue
        out.append({"tier": item.tier, "section": item.section,
                    "area": item.area})
    return out


def apply(
    index: "Index",
    feature_id: str,
    *,
    invalidate: "list[dict[str, Any]] | None" = None,
    create: "list[dict[str, Any]] | None" = None,
    impact: str = "",
    commit: bool = True,
) -> dict[str, Any]:
    """One Save: N new checks, M invalidations, one line on the feature.

    **Everything is validated before anything is written.** A sweep that
    created four checks and then refused the fifth would leave a corpus half
    swept and a feature saying nothing — which is worse than refusing, because
    the record would look complete.

    The commit is the second half of the benchmark's shape and stages **only
    the paths this wrote** — the same discipline `close-out-commit.sh` enforces
    by refusing an empty path list, and for the same measured reason: `git add
    -A` puts somebody else's afternoon in your commit.
    """
    record = _feature(index, feature_id)
    invalidate = list(invalidate or [])
    create = list(create or [])
    today = _today()

    # ---- validate ------------------------------------------------------
    suite = acceptance.load(index.docs_root, index)
    by_id = {i.note_id: i for i in suite.items if i.note_id}
    for entry in invalidate:
        check_id = str(entry.get("id") or "").strip()
        if check_id not in by_id:
            raise WriteError(
                f"{check_id or '(none)'} is not an acceptance check in this "
                "repo — a sweep must not invalidate something it cannot see",
                status=409,
            )
        change = str(entry.get("change") or feature_id).strip()
        if index.by_id(change) is None:
            raise WriteError(
                f"{change} is not in the record — an invalidation must name a "
                "change somebody can open",
                status=400,
            )
    for entry in create:
        if not str(entry.get("name") or "").strip():
            raise WriteError("a new check needs a name", status=400)
        try:
            tier = int(entry.get("tier") or 0)
        except (TypeError, ValueError):
            tier = 0
        if tier not in (1, 2, 3):
            raise WriteError(
                f"a new check needs a tier of 1, 2 or 3, not {entry.get('tier')!r}",
                status=400,
            )

    impact = (impact or "").strip()
    if not impact:
        # Derived only when the sweep DID something. A sweep that touched
        # nothing and wrote today's date would be recording that somebody
        # looked, which is exactly what `none — <reason>` is for and exactly
        # what a date must not be allowed to mean.
        if not (invalidate or create):
            raise WriteError(
                "a sweep that changes nothing must say why — write "
                "`none — <reason>`, which discharges permanently, rather than "
                "a date, which would claim work that did not happen",
                status=400,
            )
        impact = today
    if impact_state(impact) == "owed":
        raise WriteError(
            f"{impact!r} is not an acceptance impact — write a date, or "
            "`none — <reason>`",
            status=400,
        )

    # ---- write ---------------------------------------------------------
    from . import note_writes

    touched: list[Path] = []
    created: list[str] = []
    # The suite as it stands PLUS what this loop has already written. Without
    # feeding it forward, two new checks in one section compute the same
    # `ordinal` from the same starting state — sparse numbering does not help
    # if both inserts read the same maximum.
    working = list(suite.items)
    for entry in create:
        path, check_id, item = _write_new_check(
            index, record, entry, working, today)
        working.append(item)
        touched.append(path)
        created.append(check_id)

    for entry in invalidate:
        check_id = str(entry["id"]).strip()
        note_writes.invalidate_check(
            index, check_id=check_id,
            change=str(entry.get("change") or feature_id).strip(),
            reason=str(entry.get("reason") or "").strip(),
        )
        path = index.by_id(check_id)
        if path is not None:
            touched.append(path)

    feature_path = resolve_note(index, feature_id)
    _set_impact(feature_path, impact, today)
    touched.append(feature_path)

    result: dict[str, Any] = {
        "feature": feature_id, "created": created,
        "invalidated": [str(e["id"]) for e in invalidate],
        "acceptance_impact": impact, "sha": "",
    }
    if commit:
        result["sha"] = _commit(
            Path(str(index.docs_root)).parent, touched,
            f"{feature_id}: acceptance sweep — {len(created)} added, "
            f"{len(invalidate)} invalidated",
        )
    return result


def _write_new_check(
    index: "Index", feature: Any, entry: dict[str, Any],
    existing: "list[acceptance.Item]", today: str,
) -> "tuple[Path, str, acceptance.Item]":
    """One authored check. The marginal cost is a line in a form.

    That is the regression the review said tooling had to prevent: adding a
    check used to be one line in a file, and if the note form made it a
    five-field ceremony people would stop adding them — which is the failure
    mode this whole surface exists to avoid.
    """
    tier = int(entry.get("tier") or 1)
    area = str(entry.get("area") or "").strip()
    section = str(entry.get("section") or "").strip()
    if not section:
        section = next(
            (i.section for i in existing
             if i.tier == tier and i.area == area and i.section), "")
    # Sparse, and after everything already in this section — an insert takes a
    # number between two others and moves nothing, which is what retires the
    # shifting address the old suite addressed rows by.
    ordinal = max(
        [i.ordinal for i in existing
         if i.tier == tier and i.section == section] or [0]) + 10
    check_id = _next_id(index, existing)
    name = str(entry["name"]).strip()
    slug = _slug(name)
    path = index.docs_root / acceptance.CHECKS_REL / f"{check_id}-{slug}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():                                # pragma: no cover
        raise WriteError(f"{path.name} already exists", status=409)
    covers = [feature.note_id] if feature.note_id else []
    for extra in re.findall(r"\b([A-Z]{2,6}-\d{3,4})\b",
                            str(entry.get("covers") or "")):
        if extra not in covers:
            covers.append(extra)
    body = str(entry.get("text") or "").strip()
    path.write_text(
        "---\n"
        # ADR-0031: an acceptance check IS a test at `level: acceptance`.
        # This wrote `type: "[[check]]"` until 2026-08-18 (ISS-0205), and in a
        # migrated repo `acceptance.load` reads
        # `[tests at level: acceptance] or notes_by_type("check")` -- the `or`
        # never evaluates, so a swept check was written to disk and then
        # counted by nothing, rendered by nothing and gated by nothing.
        'type: "[[test]]"\n'
        f"id: {check_id}\n"
        f'aliases: ["{check_id}"]\n'
        f"title: {_yaml(name)}\n"
        "status: active\n"
        f"owner: {feature.frontmatter.get('owner') or 'user:edwin'}\n"
        f"created: {today}\n"
        f"updated: {today}\n"
        "level: acceptance\n"
        f"tier: {tier}\n"
        f"area: {_yaml(area)}\n"
        f"section: {_yaml(section)}\n"
        f"ordinal: {ordinal}\n"
        # Unwalked, always. A check authored as passed would be the assertion
        # problem ADR-0010 removed from tests, arriving on the population that
        # gates releases.
        "mark: todo\n"
        'verdict_date: ""\n'
        'verdict_reason: ""\n'
        "invalidated_by: {}\n"
        f"automation: {_yaml(str(entry.get('automation') or 'manual'))}\n"
        "covered_by: []\n"
        f"covers: [{', '.join(f'\"[[{c}]]\"' for c in covers)}]\n"
        "burden: []\n"
        "evidence: []\n"
        'migrated_from: ""\n'
        "related: []\n"
        "---\n"
        "\n"
        f"# {name}\n"
        "\n"
        f"{body}\n",
        encoding="utf-8",
    )
    index.invalidate(path)
    return path, check_id, acceptance.Item(
        tier=tier, section=section, area=area, name=name, text=body,
        checked=False, mark=" ", ordinal=ordinal, note_id=check_id,
        refs=tuple(covers),
    )


def _next_id(index: "Index", pending: "list[acceptance.Item]") -> str:
    """The next `TST-####`, from the corpus rather than from the counter.

    `counters.TST` is derived at pre-commit by `sync-snapshot.py`, so between a
    sweep and a commit it is behind by exactly the checks this sweep is
    writing. Reading the notes is the answer that is true at the moment of
    writing — and counters only ever rise, so the two converge.

    **Every test, not just the acceptance ones** (ISS-0205). The two
    populations share the `TST-*` space since ADR-0031, so allocating from the
    acceptance half alone would collide with an executable test.
    """
    top = 0
    ids = [str(r.note_id or "") for r in index.notes_by_type("test")]
    ids += [str(r.note_id or "") for r in index.notes_by_type("check")]
    ids += [i.note_id for i in pending if i.note_id]
    for note_id in ids:
        found = re.match(r"^TST-(\d+)$", note_id)
        if found:
            top = max(top, int(found.group(1)))
    return f"TST-{top + 1:04d}"


_STOPWORDS = {"a", "an", "the", "and", "or", "of", "to", "in", "on", "is", "it"}


def _slug(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9 ]+", " ", name or "")
    parts = [w for w in cleaned.split() if w]
    kept = [w for w in parts if w.lower() not in _STOPWORDS] or parts
    return "-".join(w[:1].upper() + w[1:] for w in kept[:6]) or "Check"


def _yaml(value: str) -> str:
    return '"' + str(value or "").replace("\\", "\\\\").replace('"', '\\"') + '"'


def _set_impact(path: Path, impact: str, today: str) -> None:
    """The feature's one line. It authors THAT the sweep happened, never what
    it did — the checks author that, and neither restates the other's fact."""
    from . import note_writes

    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:                            # pragma: no cover
        raise WriteError(f"cannot read {path.name}: {exc}", status=500) from None
    fm_lines, body = note_writes._split_frontmatter(raw)
    fm_lines = note_writes._set_field(fm_lines, "acceptance_impact", impact)
    fm_lines = note_writes._set_field(fm_lines, "updated", today)
    note_writes._write(path, fm_lines, body)


def _commit(repo: Path, paths: "list[Path]", message: str) -> str:
    """Stage exactly what was written, commit, return the sha — or `""`.

    **Named paths only.** `git add -A` wearing a different name is what
    `close-out-commit.sh` refuses, on a measurement: `your-trainer` carried 44
    uncommitted files and `your-health` 8, none of them the work in hand.

    A repo without git, or a commit that fails, returns `""` rather than
    raising: the notes are already written and correct, and reporting the whole
    sweep as failed because the commit did not happen would be a lie about the
    part that did.
    """
    unique = sorted({str(p) for p in paths if p})
    if not unique:                                    # pragma: no cover
        return ""
    try:
        subprocess.run(["git", "-C", str(repo), "add", "--", *unique],
                       capture_output=True, text=True, timeout=20, check=True)
        # **Never `--no-verify`.** The pre-commit hook is the gate — it runs
        # the validator and raises `counters.CHK` for the checks this sweep
        # just wrote, which is precisely the bookkeeping a sweep must not skip.
        subprocess.run(["git", "-C", str(repo), "commit", "-m", message],
                       capture_output=True, text=True, timeout=120, check=True)
        sha = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                             capture_output=True, text=True, timeout=10,
                             check=True).stdout.strip()
    except (subprocess.SubprocessError, OSError):
        return ""
    return sha[:7]
