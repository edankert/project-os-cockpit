# Plan — FEAT-0020 Agent activity surfaces

Depends on FEAT-0019 (consumes `cockpit:agent-activity` / extended `cockpit:agent-state` SSE events and the statusline data).

1. **Activity strip.** DOM + styles above the terminal pane; subscribe to activity SSE; prompt/tool/file display; cost + context meters; hidden when no instrumented session.
2. **Needs-input inbox.** Top-bar bell + popover; cross-workspace aggregation in the renderer (main process already fans agent-state to all windows); click-to-jump wiring.
3. **Live nav trail.** Attribution badges on nav/right-pane rows keyed by rel-path from tool events; decay timer; "files touched this session" list for non-docs paths.
4. **Rail dot vocabulary.** needs-input colour/shape distinct from busy/waiting; sync dock badge + notification copy.
