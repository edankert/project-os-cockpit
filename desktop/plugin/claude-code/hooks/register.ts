// project-os-cockpit plugin for Claude Code (FEAT-0156 / TASK-0649).
//
// A Claude session started in a cockpit terminal reports to that
// workspace's sidecar through this module. The shell puts this folder on
// CLAUDE_CODE_PLUGIN_DIRS (desktop/src/ipc/agent-instrument.ts); nothing is
// written under ~/.claude (RISK-0004).
//
// It replaces the generated claude-settings.json, hook-forward.sh and
// statusline.sh, and posts what they posted to /api/agent-hook:
//
//   * nine hook events, as the JSON a command hook reads on stdin: eight
//     through `forward`, and SessionEnd, which waits for its post. Claude
//     Code raises `classic.<Event>` wherever it would run a settings hook,
//     with that same JSON, so they are forwarded unchanged.
//   * PreToolUse, rebuilt: `classic.PreToolUse` hands over the tool call
//     itself (`tool` and the tool's arguments), not the stdin shape.
//   * the cockpit's own `Statusline` event, rebuilt from `session.measure`
//     into the shape statusline.sh forwarded, so the sidecar and the
//     renderer read cost, context and rate limits as before.
//
// Every hook passes its event on unchanged. A post is never awaited by the
// hook (SessionEnd excepted, for at most a second) and its failure is
// swallowed, so a stalled or missing sidecar never slows a tool call.
//
// The sidecar's address is read from $COCKPIT_INSTRUMENT_DIR/hook-env on
// every post, because the sidecar can respawn on a new port and the shell
// rewrites that file when it does. COCKPIT_NO_INSTRUMENT set to anything
// turns every post off, as it did for the scripts.
//
// The event mapping, and what the status line carried that this cannot, is
// in docs/features/cockpit-plugin/plan/PLAN.md.
//
// It also delivers prompts dispatched from the cockpit (FEAT-0158). Once a
// second it asks the sidecar for deliveries addressed to its own session.
// While no main-loop turn runs, it claims the oldest waiting one, submits it
// with `$.prompt.submit` as the person's own words, and reports the turn that
// starts with it. Nothing is typed into the terminal. The states and routes
// are in docs/features/submitted-dispatch/plan/PLAN.md.

import type { EngineInterface, Register, SessionMeasureInput, Timer } from 'claude-code'

/** How long SessionEnd may hold the exiting session for its post. */
const SESSION_END_WAIT_MS = 1000

/** Marks a post as this plugin's; the sidecar then ignores a second,
 *  unmarked capture of the same session (FEAT-0156, open question 1). */
const MARK = '_cockpit_plugin'

type Payload = Record<string, unknown>

/** The sidecar's base URL, or undefined when nothing should be posted. */
async function sidecarUrl($: EngineInterface): Promise<string | undefined> {
  if (await $.env.get('COCKPIT_NO_INSTRUMENT')) return undefined
  const dir = await $.env.get('COCKPIT_INSTRUMENT_DIR')
  if (!dir) return undefined
  let text: string
  try {
    text = String(await $.fs.read(`${dir}/hook-env`))
  } catch {
    return undefined
  }
  const match = /^COCKPIT_HOOK_URL="?([^"\n]+)"?\s*$/m.exec(text)
  const url = match?.[1]
  // The shell only ever writes a loopback sidecar here; anything else is
  // not ours to post a session's prompts and file paths to.
  if (!url || !/^http:\/\/(127\.0\.0\.1|localhost)(:\d+)?\/?$/.test(url)) return undefined
  return url.replace(/\/$/, '')
}

/** One request to a sidecar route; its JSON body, or undefined on any failure. */
async function sidecarCall(
  $: EngineInterface, path: string, body?: Payload,
): Promise<{ status: number; json: Payload } | undefined> {
  try {
    const url = await sidecarUrl($)
    if (!url) return undefined
    const response = await $.http.fetch(`${url}${path}`, body === undefined
      ? { method: 'GET' }
      : { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
    return { status: response.status, json: JSON.parse(response.text || '{}') as Payload }
  } catch {
    return undefined
  }
}

/** POST one payload to the sidecar. Resolves either way; never throws. */
async function post($: EngineInterface, body: Payload): Promise<void> {
  try {
    const url = await sidecarUrl($)
    if (!url) return
    await $.http.fetch(`${url}/api/agent-hook`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...body, agent: 'claude', [MARK]: true }),
    })
  } catch {
    // The sidecar is gone or refused the post: drop the event, as curl -s did.
  }
}

/** Waits for a post, but no longer than `ms`. */
async function postWithin($: EngineInterface, body: Payload, ms: number): Promise<void> {
  const timer = new AbortController()
  const posting = post($, body)
  // A sleep that fails, or cannot start, ends the wait at once: an exiting
  // session is never held past `ms`, even when that drops its last post.
  let limit: Promise<void>
  try {
    limit = $.clock.sleep(ms, { signal: timer.signal }).then(() => undefined, () => undefined)
  } catch {
    limit = Promise.resolve()
  }
  await Promise.race([posting, limit])
  timer.abort()
}

/** session.measure's figures in the shape statusline.sh forwarded. */
export function statuslinePayload(
  e: Pick<SessionMeasureInput, 'context' | 'rateLimits' | 'cost'>,
  extra: { sessionId: string; cwd: string; startedAt?: number; now?: number },
): Payload {
  const cost: Payload = {}
  if (typeof e.cost?.usd === 'number') cost.total_cost_usd = e.cost.usd
  if (typeof extra.startedAt === 'number' && typeof extra.now === 'number') {
    cost.total_duration_ms = Math.max(0, extra.now - extra.startedAt)
  }
  const contextWindow: Payload = { context_window_size: e.context.window }
  if (typeof e.context.percent === 'number') contextWindow.used_percentage = e.context.percent
  const rateLimits: Payload = {}
  for (const limit of e.rateLimits) {
    rateLimits[limit.kind] = { used_percentage: limit.percentUsed, resets_at: limit.resetsAt }
  }
  return {
    hook_event_name: 'Statusline',
    session_id: extra.sessionId,
    cwd: extra.cwd,
    cost,
    context_window: contextWindow,
    rate_limits: rateLimits,
  }
}

/** Starts the post of a hook's stdin JSON and passes the event on. */
const forward = <E, R>($: EngineInterface, e: E, next: (e: E) => R): R => {
  void post($, e as unknown as Payload)
  return next(e)
}

/** PreToolUse in the stdin shape, from the tool call `classic.PreToolUse` hands over. */
async function preToolUsePayload($: EngineInterface, e: Payload): Promise<Payload> {
  const { tool, tool_use_id: toolUseId, ...input } = e
  return {
    hook_event_name: 'PreToolUse',
    session_id: await $.session.id(),
    cwd: await $.session.cwd(),
    tool_name: tool,
    tool_use_id: toolUseId,
    tool_input: input,
  }
}

/** How often the plugin asks the sidecar for prompts addressed to its session. */
const DELIVERY_POLL_MS = 1000

/** A delivery as the sidecar lists it; only what the plugin reads. */
type Delivery = { did: string; prompt: string; state: string }

/** The prompt between its claim and the report of its turn's start. */
type Sending = { did: string; text: string; candidateTurn?: string; reported: boolean; resolved: boolean }

const isoNow = async ($: EngineInterface): Promise<string> => new Date(await $.clock.now()).toISOString()

/** The session's delivery state; one Claude session per load. */
type DeliveryState = {
  poll?: Timer
  mainTurnRunning: boolean
  /** The person stopped the last main-loop turn with Esc. Claude Code then
   *  refuses a plugin's prompt until the person sends input, so a waiting
   *  prompt is held until their next turn has run (TST-0095, 2026-10-14). */
  interrupted: boolean
  polling: boolean
  sending?: Sending
}

/** How often the plugin tries to report a turn's start when the sidecar
 *  does not answer (TASK-0662): a report lost to a sidecar restart left the
 *  prompt "being submitted" with its turn unrecorded. */
const STARTED_REPORT_TRIES = 3

/** Tell the sidecar the prompt's turn started, once. An answer, a refusal
 *  included, is final; no answer is tried again a second later. */
function reportStarted($: EngineInterface, st: DeliveryState, s: Sending, turnId: string): void {
  if (s.reported) return
  s.reported = true
  void (async () => {
    const startedAt = await isoNow($)
    for (let attempt = 1; attempt <= STARTED_REPORT_TRIES; attempt++) {
      const answer = await sidecarCall($, '/api/cockpit/deliveries/started', { did: s.did, turn_id: turnId, started_at: startedAt })
      if (answer || attempt === STARTED_REPORT_TRIES) return
      await $.clock.sleep(1000).catch(() => undefined)
    }
  })()
    .catch(() => undefined)
    .finally(() => { if (st.sending === s) st.sending = undefined })
}

/** One look at the sidecar: claim and submit the oldest waiting prompt. */
async function deliverOne($: EngineInterface, st: DeliveryState): Promise<void> {
  if (st.polling || st.mainTurnRunning || st.interrupted || st.sending) return
  st.polling = true
  try {
    const sessionId = await $.session.id()
    const listed = await sidecarCall($, `/api/cockpit/deliveries?session=${encodeURIComponent(sessionId)}`)
    const deliveries = (listed?.json.deliveries ?? []) as Delivery[]
    const next = deliveries.find(d => d.state === 'waiting')
    if (!next || st.mainTurnRunning || st.interrupted) return
    const claim = await sidecarCall($, '/api/cockpit/deliveries/claim', { did: next.did })
    // A refused claim means something else moved it first, a cancel among them.
    if (!claim || claim.status !== 200) return
    const s: Sending = { did: next.did, text: next.prompt, reported: false, resolved: false }
    st.sending = s
    const result = await $.prompt.submit({ text: next.prompt, asUser: true })
    s.resolved = true
    if (result.drop !== undefined) {
      st.sending = undefined
      await sidecarCall($, '/api/cockpit/deliveries/dropped', { did: s.did, reason: String(result.drop) })
      return
    }
    // The submit resolves once its turn started. A turn heard while it ran
    // whose text did not match is still the likeliest one; without any, the
    // next main-loop turn is reported (turn.start below).
    if (!s.reported && s.candidateTurn) reportStarted($, st, s, s.candidateTurn)
  } catch {
    // The sidecar is gone or the session refused: try again next tick.
  } finally {
    st.polling = false
  }
}

/** Tell the sidecar the person stopped the turn: the `Interrupt` event a
 *  Codex session already sends. The session then shows as waiting for the
 *  person until their next prompt. */
async function reportInterrupt($: EngineInterface): Promise<void> {
  try {
    await post($, { hook_event_name: 'Interrupt', session_id: await $.session.id(), cwd: await $.session.cwd() })
  } catch {
    // No session id: nothing to say it about.
  }
}

/** Starts the poll once. A plugin reloaded mid-session hears no
 *  session.start, so the end of a main-loop turn starts it too. */
function ensurePoll($: EngineInterface, st: DeliveryState): void {
  if (!st.poll) st.poll = $.clock.every(DELIVERY_POLL_MS, () => { void deliverOne($, st) })
}

export const register: Register = on => {
  const st: DeliveryState = { mainTurnRunning: false, interrupted: false, polling: false }

  on('session.start', ($, e, next) => {
    ensurePoll($, st)
    return next(e)
  })

  on('turn.start', ($, e, next) => {
    // A subagent's turn runs inside the main loop's and says nothing about
    // whether the session is idle.
    if (e.agentId === undefined) {
      st.mainTurnRunning = true
      // A turn the plugin did not start is the person's input: after an
      // interruption, that is what lets a plugin's prompt in again.
      if (!st.sending) st.interrupted = false
      const s = st.sending
      if (s && !s.reported) {
        if (e.text === s.text || s.resolved) reportStarted($, st, s, e.turnId)
        else s.candidateTurn ??= e.turnId
      }
    }
    return next(e)
  })

  on('turn.complete', ($, e, next) => {
    if (e.agentId === undefined) {
      st.mainTurnRunning = false
      if (e.isAborted) {
        st.interrupted = true
        // Claude Code fires no Stop hook for a turn stopped with Esc, so
        // without this the cockpit shows the session busy (TASK-0659).
        void reportInterrupt($)
      }
      ensurePoll($, st)
    }
    return next(e)
  })


  // Eight of the nine events whose input is already the stdin JSON;
  // SessionEnd, the ninth, is below. The engine reads each event name only
  // as a literal at the call site.
  on('classic.SessionStart', forward)
  on('classic.UserPromptSubmit', forward)
  on('classic.PostToolUse', forward)
  on('classic.Notification', forward)
  on('classic.PermissionRequest', forward)
  on('classic.Stop', forward)
  on('classic.SubagentStart', forward)
  on('classic.SubagentStop', forward)

  on('classic.PreToolUse', ($, e, next) => {
    void preToolUsePayload($, e as unknown as Payload)
      .then(body => post($, body))
      .catch(() => undefined)
    return next(e)
  })

  on('classic.SessionEnd', async ($, e, next) => {
    await postWithin($, e as unknown as Payload, SESSION_END_WAIT_MS)
    return next(e)
  })

  on('session.measure', ($, e, next) => {
    void (async () => {
      try {
        const [sessionId, cwd, usage, now] = await Promise.all([
          $.session.id(), $.session.cwd(), $.session.usage(), $.clock.now(),
        ])
        await post($, statuslinePayload(e, { sessionId, cwd, startedAt: usage.startedAt, now }))
      } catch {
        // A reading the session could not give: skip this one.
      }
    })()
    return next(e)
  })
}
