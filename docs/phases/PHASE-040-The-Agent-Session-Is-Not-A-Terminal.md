---
type: "[[phase]]"
id: PHASE-040
aliases: ["PHASE-040"]
title: "An agent session is not a terminal — a purpose-built control plane owns the process, and the cockpit reads it instead of hosting it"
status: planned
order: 40
owner: user:edwin
created: 2026-08-20
updated: "2026-08-20"
goal: "Move ownership of agent sessions off a terminal multiplexer and onto a control plane designed for them, so a session survives the app that started it, is reachable from a device that is not this Mac, and reports its state from one place rather than three."
features: []
requirements: []
tasks: []
issues: []
related: ["[[FEAT-0003-Embedded-Terminal]]", "[[FEAT-0013-Agent-State]]", "[[FEAT-0025-Dispatch-Ledger]]", "[[ISS-0008-Terminals-Die-With-The-App]]", "[[REQ-0005-Terminal-Local-Only]]", "[[REQ-0034-A-Non-Loopback-Write-Is-Authenticated]]", "[[PHASE-029-One-Tool-Two-Front-Doors]]", "[[PHASE-033-The-Workspace-Is-Not-Always-Local]]", "[[ADR-0010-What-The-Browser-Cockpit-Is-For]]"]
tags: [phase, agents, terminals]

---

# An agent session is not a terminal

## Goal

A running agent is a **process with a lifecycle**, and the cockpit currently models it as *a terminal that happens to have something in it*. Everything awkward about the current design follows from that one substitution.

This phase adopts [T3 Code](https://github.com/pingdotgg/t3code)'s server as the owner of agent sessions — Edwin's **option A**, decided 2026-08-20 — and reduces the cockpit's role to reading and linking. The record engine is untouched.

## What tmux is doing today, exactly

`desktop/src/ipc/terminal.ts`: when tmux ≥ 3.2 is present the PTY is a **tmux client** attached to a named session on a dedicated socket (`-L cockpit`), so the tmux server owns the shell and the session survives the Electron app closing ([[ISS-0008]] / TASK-0144). Without tmux it falls back to a direct spawn and the PTY dies with the app.

That is the **whole** of what tmux provides here: survivability. Not orchestration, not state, not remote access. It is a correct solution to a smaller problem than the one we have.

## Why a control plane instead

T3 Code is MIT-licensed and its server is an **event-sourced orchestration engine**. Providers are registered drivers — each declares a `driverKind`, a `configSchema` and a `create` function; adapters conform to `ProviderAdapter.ts` and live in `apps/server/src/provider/Layers/`; `ProviderInstanceRegistry` keys configured instances by `ProviderInstanceId`. **Session state persists through the orchestration layer — events and checkpoints — rather than inside the driver.**

That is a materially stronger guarantee than a multiplexer. tmux keeps a *shell* alive; an event log lets a session be **reconstructed**, inspected, and resumed on a different client.

Five adapters ship already: Claude Code, Codex, Cursor, Grok, OpenCode.

## The framing correction that makes this proposal small

The first analysis of this option described it as *"a Node service in a Python + Electron fleet"*, as though Node were a foreign runtime being introduced. **It is not.** Measured 2026-08-20:

| | lines |
|---|---|
| Python source (`src/project_os_cockpit`) | 33,509 |
| **TypeScript (`desktop/src`)** | **24,240** |

Electron *is* Node. The cockpit already ships a Node runtime, and terminals and PTYs already live in that half — `terminal.ts` is the file this phase changes. So this is not "adopt a second language". It is **"replace a multiplexer with a better-engineered implementation, inside the process that already owns terminals."**

## Scope

**In:**

- T3's server running beside the cockpit on the same machine, owning agent processes
- `terminal.ts`'s tmux backing retired in favour of T3 session handles
- The cockpit's agent surfaces reading T3's event stream instead of maintaining a parallel model
- Reuse of T3's **web client** for agent interaction, including from a phone browser

**Out:**

- **The record engine.** Index, acceptance, obligations, publication, `note_writes`, the ledger — all Python, all untouched. None of it is agent-session code, and rewriting it to gain a terminal feature is the wrong trade.
- **Any conversion of the fleet's tooling.** `tools/scripts/*.py` is **template-owned**, synced from upstream `project-os`, used by all twelve repos. The cockpit does not own it. There is also a hard constraint in the other direction: `validate_docs_bundled.py` must stay **byte-identical** to `tools/scripts/validate-docs.py`, and a `diff -q` in the suite enforces it — a guarantee that exists *because* they are the same language.
- **Remote shell access.** See the terminal decision below.
- **Hosting the cockpit itself.** That is a separate question; see [[reference/HOSTED-COCKPIT]].

## The terminal question, decided separately

[[FEAT-0003]]'s `ttyd` pane is a **shell**, not an agent, and binds `127.0.0.1` by [[REQ-0005]]. It solves a different problem and this phase does not fold it in.

**Default: `ttyd` stays local-only and is simply absent from any remote surface.** Folding shells into a remotely-reachable control plane means a command prompt on the machine holding twelve repos — one of which has a live website as its only remote. Every other decision here is about *writing notes*; that one is about *running arbitrary commands*, and it needs its own risk note and its own decision, not a side effect of this phase.

## What is given up

Stated plainly, because it is not nothing:

- The cockpit stops being the thing that *hosts* agents and becomes the thing that *reports on* them.
- `/api/cockpit/agent-state`, `/api/agent-hook`, `/api/cockpit/dispatch` and `/api/cockpit/focus` either remap onto T3's event stream or retire. Note that these are **exactly the routes that are not loopback-guarded** — so this touches the authorisation surface and cannot be done casually.
- **Two panes of glass** is the main risk: T3's UI for agents, the cockpit's for the record. Unless the boundary is deliberate and legible, this trades one awkwardness for another.

## Exit criteria

- [ ] An agent session survives the desktop app closing **without tmux**, and is resumable from a different client
- [ ] The cockpit's agent state has **one** source of truth, not a parallel model kept in sync
- [ ] An agent session is reachable from a phone browser **without a shell being exposed**
- [ ] The boundary between "T3 shows the agent" and "the cockpit shows the record" is something a person can state in a sentence
- [ ] `validate_docs_bundled.py` and `tools/scripts/validate-docs.py` are still byte-identical, and the fleet's Python tooling is unchanged

## Open questions — must be answered before any task is written

Three things were **not** determinable from public documentation on 2026-08-20, and each can invalidate part of the plan:

1. **Is T3 Connect self-hostable?** Its author describes it as an open-source tunnel layer and community docs say fork/self-host is possible, but the official `docs/user/remote-access.md` does not confirm it. **Tailscale is a first-class alternative** and sidesteps the question entirely — that may be the answer.
2. **Can their clients point at an arbitrary backend?** If the web client is coupled to their server's RPC schema, "reuse their client" means adopting their whole server contract rather than a panel.
3. **What exactly persists a session?** Documented as events and checkpoints in the orchestration layer, but the mechanism (PTY? daemon?) is not stated. Until it is, the claim *"stronger than tmux"* is inference rather than measurement.

Answering these means reading `apps/server` and `packages/client-runtime` **source**, not docs. That is the first task this phase should mint, and nothing else should start before it.

## A correction already on the record

An earlier summary in this session said T3 has **native iOS and Android apps**. It does not — that came from marketing copy and was repeated without checking. It is a **web app in a mobile browser**, reached over Tailscale or a tunnel. This matters because "we get mobile apps for free" would be a false premise for the phase.
