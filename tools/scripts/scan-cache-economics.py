#!/usr/bin/env python3
"""Fleet-wide prompt-cache accounting over Claude Code transcripts.

The measurement behind FEAT-0081. It exists as a script because the first
version of it did not: the figures were quoted in five notes as prose,
and when the independent review re-derived them two had *fallen* — which
counts of past events cannot do. The originals had been produced by
throwaway logic that never shipped, so nobody, including their author,
could reproduce them (ISS-0111).

This imports the **shipped** `session_cache` module rather than
reimplementing the parse, so the numbers in the notes and the numbers in
the product cannot drift apart again.

    python3 tools/scripts/scan-cache-economics.py
    python3 tools/scripts/scan-cache-economics.py --json
    python3 tools/scripts/scan-cache-economics.py --root ~/.claude/projects

Not the same thing as `GET /api/cockpit/session-cache`, which answers the
same question for **one workspace** from the transcripts that workspace's
tracker knows about. This walks every transcript on the machine.

Costs are estimates: the token counts are exact, the dollars come from a
per-family price table that drifts. On a subscription they are not
dollars at all — the same tokens land as usage-limit consumption.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from project_os_cockpit import session_cache as sc  # noqa: E402

DEFAULT_ROOT = "~/.claude/projects"


def scan(root: str) -> dict[str, Any]:
    paths = sorted(glob.glob(os.path.join(os.path.expanduser(root), "*", "*.jsonl")))
    totals = {
        "transcripts": 0, "turns": 0,
        "read_tokens": 0, "write_tokens": 0,
        "read_cost_usd": 0.0, "write_cost_usd": 0.0,
    }
    buckets: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"count": 0, "tokens": 0, "cost_usd": 0.0}
    )
    for path in paths:
        hist = sc.history(path)
        if hist is None:
            continue
        totals["transcripts"] += 1
        totals["turns"] += hist.turns
        totals["read_tokens"] += hist.read_tokens
        totals["write_tokens"] += hist.write_tokens
        totals["read_cost_usd"] += hist.read_cost_usd
        totals["write_cost_usd"] += hist.write_cost_usd
        for cause, agg in hist.buckets().items():
            dst = buckets[cause]
            dst["count"] += agg["count"]
            dst["tokens"] += agg["tokens"]
            dst["cost_usd"] += agg["cost_usd"]

    input_cost = totals["read_cost_usd"] + totals["write_cost_usd"]
    # "Staleness" means TTL expiry — the cache lapsing on its own clock.
    # A model switch is invalidation, not staleness. The two were once
    # quoted under one word with the ratio of only one of them (ISS-0111),
    # so they are named separately here and everywhere downstream.
    stale = buckets.get(sc.CAUSE_TTL_EXPIRY, {}).get("cost_usd", 0.0)
    avoidable = sum(
        agg["cost_usd"] for cause, agg in buckets.items()
        if cause != sc.CAUSE_SESSION_START
    )
    return {
        **{k: (round(v, 2) if isinstance(v, float) else v) for k, v in totals.items()},
        "input_cost_usd": round(input_cost, 2),
        "rewrites": {k: {**v, "cost_usd": round(v["cost_usd"], 2)}
                     for k, v in sorted(buckets.items())},
        "staleness_cost_usd": round(stale, 2),
        "staleness_pct": round(stale / input_cost * 100, 1) if input_cost else 0.0,
        "avoidable_cost_usd": round(avoidable, 2),
        "avoidable_pct": round(avoidable / input_cost * 100, 1) if input_cost else 0.0,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=DEFAULT_ROOT)
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    out = scan(args.root)
    if args.json:
        print(json.dumps(out, indent=2))
        return 0

    print(f"transcripts        {out['transcripts']:>12,}")
    print(f"assistant turns    {out['turns']:>12,}   (deduplicated; API-error placeholders excluded)")
    print()
    print(f"cache reads        {out['read_tokens'] / 1e6:>11,.0f}M   ~${out['read_cost_usd']:>10,.2f}")
    print(f"cache writes       {out['write_tokens'] / 1e6:>11,.0f}M   ~${out['write_cost_usd']:>10,.2f}")
    print(f"input-side total                 ~${out['input_cost_usd']:>10,.2f}")
    print()
    print("full-prefix re-writes, by cause:")
    for cause, agg in out["rewrites"].items():
        print(f"  {cause:<16} n={agg['count']:<4} {agg['tokens'] / 1e6:>6.1f}M   ~${agg['cost_usd']:>9,.2f}")
    print()
    print(f"staleness (TTL expiry only)      ~${out['staleness_cost_usd']:>10,.2f}   {out['staleness_pct']}% of input")
    print(f"all avoidable re-writes          ~${out['avoidable_cost_usd']:>10,.2f}   {out['avoidable_pct']}% of input")
    print()
    print("Estimates: token counts exact, dollars from a per-family price table that")
    print("drifts. On a subscription these land as usage-limit consumption, not money.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
