---
type: "[[feature]]"
id: FEAT-0029
aliases: ["FEAT-0029"]
title: "Cockpit MCP server — expose the cockpit HTTP API to MCP-capable agents"
status: backlog
phase: "[[PHASE-999-Future]]"
owner: user:edwin
created: 2026-07-17
updated: 2026-07-17
source: []
goal: "Expose the cockpit's documented HTTP API (COCKPIT-API.md, schema v3) as an MCP server, so any MCP-capable agent can query docs state — nav, note render, relationships, stats, validation health, agent state — as first-class tools instead of shelling out to curl."
requirements: []
tasks: []
release: ""
related: ["[[COCKPIT-API]]", "[[FEAT-0008-Cockpit-API-Hardening]]", "[[FEAT-0018-Verification-Health-Surface]]"]
tests: []
---

# Cockpit MCP server

## Goal
The cockpit already has a stable, schema-versioned JSON contract (docs/references/COCKPIT-API.md, `X-Cockpit-Schema: 3`) that agents currently reach via the `cockpit` CLI or raw HTTP. MCP-capable agents (Claude Code, desktop clients, other MCP hosts) should be able to consume the same surface as typed MCP tools/resources: "what's in focus", "render this note", "what links here", "is the docs system drifting", "what is the agent state" — without bespoke shell plumbing per agent.

## Brief plan
1. **Thin adapter, no logic:** an MCP server module (stdio transport first) that maps MCP tool calls 1:1 onto the existing HTTP endpoints of a running cockpit — discovery via the `.cockpit/url` walk-up the CLI already uses. The HTTP API remains the single contract; the MCP layer translates only.
2. **Tool surface (read-only first):** `get_state`, `get_nav`, `get_context`, `render_note`, `get_stats`, `get_validation` (FEAT-0018), `list_sessions`. Mutating verbs (`focus`, `signal`, `dispatch`) gated behind a second milestone once the read path proves out.
3. **Schema discipline:** tool results embed `schema_version` passthrough; the MCP server refuses to start against a cockpit whose `X-Cockpit-Schema` it does not know, mirroring the JS client rule.
4. **Packaging:** ship inside `project_os_cockpit` (e.g. `python -m project_os_cockpit.mcp`) so downstream repos get it via the existing sync; zero new runtime dependencies is the target, which likely means implementing the (JSON-RPC over stdio) MCP framing with stdlib only — evaluate before committing.

## Scope
- In: read-only MCP tools over the documented v3 endpoints; stdio transport; `.cockpit/url` discovery.
- Out (initially): write verbs, HTTP/SSE MCP transports, multi-workspace fan-out (pairs with [[FEAT-0028-Fleet-Health-Surface]] later), auth.

## Acceptance
- An MCP-capable agent configured with the cockpit MCP server can list tools, fetch the current focus/state, render a note by ID, and read validation health — all against a live cockpit, with values identical to the raw HTTP responses.
- The MCP layer contains no docs-system logic of its own (pure translation), and refuses cleanly (clear error) when no cockpit is discoverable.

## Links
- Contract: [[COCKPIT-API]] (docs/references/COCKPIT-API.md, schema v3).
- Builds on: [[FEAT-0008-Cockpit-API-Hardening]] (schema rule), [[FEAT-0018-Verification-Health-Surface]] (`/api/cockpit/validation`).
