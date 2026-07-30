"""Validate repos with no running sidecar (FEAT-0028 / TASK-0249).

``python -m project_os_cockpit.fleet_validate <repo> [<repo> ...]``

Prints one JSON object per line — ``{root, state, errors, warnings,
checked_at, detail?}`` — where ``errors``/``warnings`` are counts, not
lists: the fleet badge and roll-up need a number and a state, and
shipping every violation for ten repos across a pipe would be a lot of
bytes nobody reads. Opening a workspace gets you the full report from
its own sidecar.

**Whose validator runs: the repo's own.** ``ValidationRunner``'s locate
order picked that in FEAT-0018 and said why — a repo's own copy honours
its own ``STATUSES.md``, and a repo that has deliberately pinned an
older template should not be marked drifting against a rule it has not
adopted. ``tools/scripts/validate-fleet.sh`` chooses the other way
("uses THIS repo's validate-docs.py for uniform semantics"), which is
right for a manual diagnostic where comparability is the point and
wrong for a badge, where a red mark the repo's own CI would not raise
is a false positive. This module deliberately reuses the runner rather
than re-deciding.

Serial by design. Ten validators at once is a visible stall on the
machine the user is working on, and these are repos nobody is looking
at — there is nothing to be gained by finishing sooner.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from .validation import validate_repo


def summarise(project_root: Path) -> dict[str, object]:
    """One repo's validator state, counts only.

    Carries **which** validator produced it. The per-repo choice above is
    only defensible if the reader can see it was made: without this, a
    fleet of mixed template versions looks uniform, which is the
    assumption ISS-0026 was filed for (a bundled validator copy drifting
    silently from the template). `"repo"` means that repo's own
    `tools/scripts/validate-docs.py`; `"bundled"` means the cockpit's
    fallback, used for a repo that predates the validator.
    """
    from .validation import BUNDLED_VALIDATOR, ValidationRunner

    located = ValidationRunner(project_root).locate_validator()
    which = (None if located is None
             else "bundled" if located == BUNDLED_VALIDATOR else "repo")
    report = validate_repo(project_root)
    return {
        "validator": which,
        "root": str(project_root),
        "state": report.get("state"),
        "errors": len(report.get("errors") or []),
        "warnings": len(report.get("warnings") or []),
        "checked_at": report.get("checked_at"),
        **({"detail": report["detail"]} if report.get("detail") else {}),
    }


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        print("usage: python -m project_os_cockpit.fleet_validate <repo> [...]",
              file=sys.stderr)
        return 2
    for raw in args:
        root = Path(raw).expanduser()
        try:
            line = summarise(root)
        except Exception as exc:  # never let one bad repo kill the batch
            line = {"root": str(root), "state": "unavailable",
                    "errors": 0, "warnings": 0, "checked_at": None,
                    "detail": f"{type(exc).__name__}: {exc}"}
        print(json.dumps(line), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
