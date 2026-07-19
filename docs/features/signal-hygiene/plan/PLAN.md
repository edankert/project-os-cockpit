# Plan — FEAT-0033 Agent signal hygiene

Order: 0152 → 0153 → 0154 → 0155 (dedup first — it corrupts stored data today; the rest are independent).

1. **TASK-0152.** Ingestion dedup in `AgentSessionTracker.ingest()` + regression test seeded with the double-capture pattern from the live your-sudoku index.
2. **TASK-0153.** External hook: adopt the `notification_type` subtype gate (permission_prompt / idle_prompt / elicitation_dialog) before promoting to needs-input; extend TST-0015's extracted-script tests.
3. **TASK-0154.** One decay constant: sidecar exports it via `/api/cockpit/identity` or a shared env contract; poller + tracker read the same value; document in HOOKS.md.
4. **TASK-0155.** Surface rots: transcript path → reveal/open action; queue-chip tooltip wording; single "undocumented" label everywhere; sessions feed refetch on ~overview re-entry.
