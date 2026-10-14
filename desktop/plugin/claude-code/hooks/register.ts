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

import type { EngineInterface, Register, SessionMeasureInput } from 'claude-code'

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

export const register: Register = on => {
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
