# Plan — FEAT-0031 Ambient status consolidation

1. **TASK-0148.** Delete the footer agent dot (`#sf-agent`, `refreshFooterAgent`, CSS); shrink `buildNowSection()` to the one-liner. Pure removal + demotion — do after FEAT-0030 so attention has its richer home first.
2. **TASK-0149.** Rate-limit pip in the agent strip: render `five_hour.used_percentage` (+ reset time in the title tooltip), `.meter-hot` ≥ 80%. Data already flows via `/api/cockpit/state` snapshot cost block.
