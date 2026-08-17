# Plan — a machine-readable projection of the acceptance suite

Parked in [[PHASE-999]]. One task when it is picked up, and the reason it is one task is that the structure already exists: `acceptance.parse` computes every field the projection would expose.

1. **Serve the projection.** `GET /api/cockpit/acceptance.json` from `acceptance.parse`, with a reconciliation assertion against the rendered row count so two readers of one file cannot silently disagree ([[ISS-0175]]).

**Not in scope until a decision exists:** authoring the suite as JSON. That overturns [[ADR-0009]] for one corpus and wants an ADR, not a task. See [[FEAT-0112]]'s closing section for the trigger — per-check history.
