# Plan — FEAT-0022 Session insight and traceability

Depends on FEAT-0019 (session ids, tool events, transcript paths, cost feed).

1. **Session index.** Persist per-session metadata under `.cockpit/` as hook events arrive; defensive transcript parsing behind a metadata-only fallback.
2. **History browser.** Sessions list + detail view (prompt summary, duration, cost, files touched); read-only surface in the shell.
3. **Undocumented-work badge.** Live per-session rule (src-edits without docs-note edits) → rail + activity-strip badge; clear conditions.
4. **CHG linking.** Correlate CHG note creation with the live session; render "produced by" metadata cockpit-side without touching the note file.
