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
//
// And it lets the person answer a permission prompt from the cockpit
// (FEAT-0159). When Claude Code's own rules, mode and PreToolUse hooks answer
// `ask`, the plugin offers the call to the sidecar and waits for the
// workspace's wait (5 s unless set) for a click. A grant or a denial there is
// the answer; otherwise the terminal shows its own prompt as before. An
// `allow` or a `deny` from beneath is never changed. The plugin never holds
// the shell's secret: it offers and reads, it does not answer. The flow is in
// docs/features/answerable-approvals/plan/PLAN.md.

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
  noteMode(e)
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

/** How often the plugin reads an offered approval while it waits. */
const APPROVAL_POLL_MS = 250

/** Tools whose ask a hook can only tighten: a question put to the person and
 *  a plan to approve. A hook's allow does not dismiss their dialog, so they
 *  are never offered to the cockpit. */
const PERSON_ONLY = new Set(['AskUserQuestion', 'ExitPlanMode'])

type Verdict = { decision: 'allow' | 'ask' | 'deny'; reason?: string; decider?: string }

/** The answer a person gave in the cockpit, or undefined while there is none. */
export function cockpitVerdict(record: unknown): Verdict | undefined {
  const r = (record ?? {}) as { status?: unknown; decided_by?: unknown }
  const who = typeof r.decided_by === 'string' && r.decided_by ? r.decided_by : 'a person'
  if (r.status === 'granted') return { decision: 'allow', reason: `Approved in the cockpit by ${who}.` }
  if (r.status === 'denied') return { decision: 'deny', reason: `Denied in the cockpit by ${who}.` }
  return undefined
}

/** The permission modes in which an ask is put to the person in the
 *  terminal. In `auto` the classifier settles it, in `dontAsk` nobody is
 *  asked, and in `plan` a hook can only tighten; offering those would make
 *  every such call wait for nothing (live run, 2026-10-14). */
const PERSON_ASKED_MODES = new Set(['default', 'acceptEdits'])

/** The session's permission mode, from the last classic event that carried
 *  one. Unknown until the first, and an unknown mode offers nothing. */
const session: { mode?: string } = {}

/** Remember the mode a classic event reports. */
function noteMode(e: unknown): void {
  const mode = (e as { permission_mode?: unknown } | null)?.permission_mode
  if (typeof mode === 'string' && mode) session.mode = mode
}

/** Whether an ask from beneath may be offered to the cockpit at all. */
export function offerable(
  e: { tool: string; tool_use_id?: string; ceiling?: string }, asked: Verdict, mode: string | undefined,
): boolean {
  if (asked.decision !== 'ask') return false
  if (!mode || !PERSON_ASKED_MODES.has(mode)) return false
  // A `$.tool.check` query has no call to wait on.
  if (!e.tool_use_id) return false
  if (PERSON_ONLY.has(e.tool)) return false
  // The organization's ceiling is ask: an allow from a hook cannot stand.
  if (e.ceiling === 'ask') return false
  // A hosted session's program answers its asks, not a dialog here.
  if (asked.decider === 'host') return false
  return true
}

/** Offer the call, wait for a click, and hand it back when none comes.
 *  Returns the cockpit's answer, or `asked` unchanged. */
async function askCockpit(
  $: EngineInterface,
  e: { tool: string; input: unknown; tool_use_id?: string; agentId?: string },
  asked: Verdict,
  signal: AbortSignal,
): Promise<Verdict> {
  const offer = await sidecarCall($, '/api/cockpit/approvals/ask', {
    session_id: await $.session.id(),
    tool: e.tool,
    input: e.input,
    tool_use_id: e.tool_use_id,
    agent_id: e.agentId,
  })
  const id = offer?.status === 200 ? offer.json.approval_id : undefined
  const waitMs = Number(offer?.json.wait_ms ?? 0)
  if (typeof id !== 'string' || !id || !(waitMs > 0)) return asked
  try {
    const until = (await $.clock.now()) + waitMs
    while ((await $.clock.now()) < until) {
      await $.clock.sleep(APPROVAL_POLL_MS, { signal })
      const read = await sidecarCall($, `/api/cockpit/approvals?approval_id=${encodeURIComponent(id)}`)
      const answer = cockpitVerdict(read?.json.approval)
      if (answer) return answer
    }
  } catch {
    // Interrupted, or the clock failed: fall through and give it back.
  }
  // The sidecar decides under its lock: a click that landed first comes back
  // as the answer; an approval still open goes to the terminal.
  const back = await sidecarCall($, '/api/cockpit/approvals/handed-back', { approval_id: id })
  return cockpitVerdict(back?.json.approval) ?? asked
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

// ---------------------------------------------------------------------------
// The cockpit's facts on the project line (FEAT-0157).
//
// project-os draws one line above the prompt (its plugin, ADAPTER.md "The
// project line"). This plugin adds a segment keyed `segment:cockpit` to the
// end of it: how many things need the person here, how many in the other
// projects, and an Open in cockpit button. The two plugins never call each
// other; whichever hook is outer joins the two. The facts are read in the
// background; drawing never asks the sidecar anything. A number that could
// not be read is left out, never shown as zero. The plan, with the sources
// and the rules for each number, is docs/features/session-band/plan/PLAN.md.

/** How often the line's facts are read again. */
const LINE_POLL_MS = 10_000
/** The other projects' file is ignored once the shell stops refreshing it. */
const ELSEWHERE_FRESH_MS = 2 * 60_000
/** A project's own count is too old to add up after a day. */
const COUNT_FRESH_MS = 24 * 60 * 60_000

export const SEGMENT_KEY = 'segment:cockpit'
export const OPEN_KEY = 'cockpit:open'
const PROJECT_LINE_KEY = 'project-os:line'

/** What `GET /api/cockpit/line` answers. */
export type LineAnswer = {
  needs_you: { total: number; kinds: { kind: string; count: number; verb: string; noun: string }[] }
  open_target: string | null
}

/** What the shell writes in `needs-elsewhere.json`. */
export type Elsewhere = {
  written_at: string
  workspace_id: string
  projects: { project: string; workspace_id: string; count: number | null; as_of: string | null; source: string }[]
}

/** The segment's facts; each is absent when it could not be read. */
export type SegmentFacts = { here?: string; others?: string; url?: string }

/** The line route's answer, or undefined when it did not answer as promised. */
export function lineAnswer(json: unknown): LineAnswer | undefined {
  const j = json as Partial<LineAnswer> | undefined
  const total = j?.needs_you?.total
  if (typeof total !== 'number' || !Number.isFinite(total) || !Array.isArray(j?.needs_you?.kinds)) return undefined
  return { needs_you: j!.needs_you!, open_target: typeof j!.open_target === 'string' ? j!.open_target : null }
}

const WORKSPACE_ID = /^[A-Za-z0-9_-]{1,64}$/
const NOTE_ID = /^[A-Z]+-[0-9]+$/

/** The button's link, or undefined when either part fails its pattern. */
export function openUrl(workspaceId: unknown, target: string | null): string | undefined {
  if (typeof workspaceId !== 'string' || !WORKSPACE_ID.test(workspaceId)) return undefined
  if (target === null) return `cockpit://${workspaceId}`
  return NOTE_ID.test(target) ? `cockpit://${workspaceId}/${target}` : undefined
}

/** The workspace this session's terminal belongs to: the shell names each
 *  workspace's instrument folder after its ID (`instrument/<ws>`). */
export function workspaceOf(instrumentDir: string | undefined): string | undefined {
  const name = instrumentDir?.replace(/\/+$/, '').split('/').pop()
  return name || undefined
}

/** The segment's facts from what was read, by the plan's rules. The button's
 *  workspace is the instrument folder's, so it does not wait for the shell's
 *  first `needs-elsewhere.json` (FEAT-0157 review, round 1). */
export function segmentFacts(
  answer: LineAnswer | undefined, elsewhere: Elsewhere | undefined, now: number, workspaceId?: string,
): SegmentFacts {
  const facts: SegmentFacts = {}
  const total = answer?.needs_you.total ?? 0
  if (total > 0) facts.here = `${total} ${total === 1 ? 'needs' : 'need'} you`
  const written = elsewhere ? Date.parse(elsewhere.written_at) : NaN
  if (elsewhere && Array.isArray(elsewhere.projects) && Number.isFinite(written) && now - written <= ELSEWHERE_FRESH_MS) {
    let sum = 0
    let partial = false
    for (const p of elsewhere.projects) {
      const at = p.as_of ? Date.parse(p.as_of) : NaN
      if (typeof p.count === 'number' && Number.isFinite(at) && now - at < COUNT_FRESH_MS) sum += p.count
      else partial = true
    }
    if (sum > 0) facts.others = `${sum}${partial ? '+' : ''} in other projects`
  }
  if (answer) {
    const url = openUrl(workspaceId, answer.open_target)
    if (url) facts.url = url
  }
  return facts
}

/** What the segment says, as text: what decides whether to redraw. */
export function segmentText(f: SegmentFacts): string {
  return [f.here, f.others, f.url ? `[Open in cockpit]` : undefined].filter(Boolean).join(' · ')
}

/** The line's state; one Claude session per load. */
const line: { answer?: LineAnswer; elsewhere?: Elsewhere; facts: SegmentFacts; text: string; poll?: Timer; reading?: boolean; commands?: boolean } = {
  facts: {}, text: '',
}

/** The shell's `needs-elsewhere.json`, or undefined when there is none. */
async function readElsewhere($: EngineInterface): Promise<Elsewhere | undefined> {
  try {
    if (await $.env.get('COCKPIT_NO_INSTRUMENT')) return undefined
    const dir = await $.env.get('COCKPIT_INSTRUMENT_DIR')
    if (!dir) return undefined
    return JSON.parse(String(await $.fs.read(`${dir}/needs-elsewhere.json`))) as Elsewhere
  } catch {
    return undefined
  }
}

/** Reads both sources and redraws when the segment's text changed. */
async function readLine($: EngineInterface): Promise<void> {
  if (line.reading) return
  line.reading = true
  try {
    const reply = await sidecarCall($, '/api/cockpit/line')
    line.answer = reply?.status === 200 ? lineAnswer(reply.json) : undefined
    line.elsewhere = await readElsewhere($)
    const dir = (await $.env.get('COCKPIT_INSTRUMENT_DIR')) || undefined
    line.facts = segmentFacts(line.answer, line.elsewhere, await $.clock.now(), workspaceOf(dir))
    const text = segmentText(line.facts)
    if (text !== line.text) {
      line.text = text
      $.ui.invalidate('ui.render')
    }
  } catch {
    // Whatever failed, the segment keeps what it last read.
  } finally {
    line.reading = false
  }
}

/** Starts the line's poll once, with a first read now. */
function ensureLinePoll($: EngineInterface): void {
  if (line.poll) return
  line.poll = $.clock.every(LINE_POLL_MS, () => { void readLine($) })
  void readLine($)
}

type Node = { type?: string; props?: Record<string, unknown>; children?: unknown[] }

/** The tree beneath with `segment` appended to the element keyed
 *  `project-os:line`, or undefined when there is no such element. The tree
 *  from next(e) is frozen, so the path to it is rebuilt from copies. */
export function joinToLine(tree: unknown, segment: unknown): unknown | undefined {
  if (!tree || typeof tree !== 'object') return undefined
  const n = tree as Node
  if (n.props?.key === PROJECT_LINE_KEY) return { ...n, children: [...(n.children ?? []), segment] }
  if (!Array.isArray(n.children)) return undefined
  for (let i = 0; i < n.children.length; i++) {
    const joined = joinToLine(n.children[i], segment)
    if (joined !== undefined) return { ...n, children: n.children.map((c, j) => (j === i ? joined : c)) }
  }
  return undefined
}

/** Brings the cockpit forward on this project's focus item. */
async function openCockpit($: EngineInterface): Promise<void> {
  const url = line.facts.url
  if (!url) return
  try {
    const r = await $.process.run(['open', url])
    if (r.exitCode !== 0) throw new Error(r.stderr)
  } catch {
    $.ui.toast('Could not open the cockpit')
  }
}

/** "counted 3h ago", "live" or "not read", for one other project's count. */
export function countSource(p: Elsewhere['projects'][number], now: number): string {
  if (p.count === null || p.source === 'unknown') return 'not read'
  if (p.source === 'live') return 'live'
  const at = p.as_of ? Date.parse(p.as_of) : NaN
  if (!Number.isFinite(at)) return 'not read'
  const mins = Math.max(0, Math.round((now - at) / 60_000))
  const ago = mins < 60 ? `${mins}m` : mins < 48 * 60 ? `${Math.round(mins / 60)}h` : `${Math.round(mins / 1440)}d`
  return `counted ${ago} ago`
}

export const NOT_ANSWERING = 'The cockpit is not answering for this project'
export const NO_ELSEWHERE = "The cockpit shell has not written the other projects' counts"

/** /cockpit-needs's rows: this project's kinds, then each other project. */
export function needsRows(answer: LineAnswer | undefined, elsewhere: Elsewhere | undefined, now: number): { text: string; dim?: boolean; head?: boolean }[] {
  if (!answer) return [{ text: NOT_ANSWERING }]
  const rows: { text: string; dim?: boolean; head?: boolean }[] = [{ text: 'This project', head: true }]
  if (!answer.needs_you.kinds.length) rows.push({ text: 'Nothing needs you here.', dim: true })
  for (const k of answer.needs_you.kinds) rows.push({ text: `${k.count} ${k.noun} to ${k.verb.toLowerCase()}` })
  rows.push({ text: 'Other projects', head: true })
  if (!elsewhere || !Array.isArray(elsewhere.projects)) {
    rows.push({ text: NO_ELSEWHERE })
    return rows
  }
  const owing = elsewhere.projects.filter(p => p.count === null || p.count > 0)
    .sort((a, b) => (b.count ?? -1) - (a.count ?? -1) || a.project.localeCompare(b.project))
  const none = elsewhere.projects.filter(p => p.count === 0).sort((a, b) => a.project.localeCompare(b.project))
  for (const p of owing) rows.push({ text: `${p.project}: ${p.count === null ? '?' : p.count} · ${countSource(p, now)}` })
  for (const p of none) rows.push({ text: `${p.project}: 0 · ${countSource(p, now)}`, dim: true })
  return rows
}

/** /cockpit-release's rows, from `GET /api/cockpit/release`. */
export function releaseRows(release: Record<string, unknown> | undefined): { text: string; dim?: boolean; head?: boolean }[] {
  if (!release) return [{ text: NOT_ANSWERING }]
  const rows: { text: string; dim?: boolean; head?: boolean }[] = []
  const title = String(release.version || release.title || 'Next release')
  const state = release.preparing ? 'being prepared' : release.exists ? String(release.status || 'recorded') : 'not prepared yet'
  rows.push({ text: `${title}: ${state}`, head: true })
  const contents = release.contents as { count?: number; since?: string } | undefined
  if (typeof contents?.count === 'number') {
    rows.push({ text: `${contents.count} item${contents.count === 1 ? '' : 's'}${contents.since ? ` since ${contents.since}` : ''}` })
  }
  // The gate's own list: it counts every unsettled check in the repo, which
  // is what blocks. `open_tests` is narrower (the checks for this release's
  // contents), so it is not the blocked count (FEAT-0157 review, round 1).
  const gate = release.gate as { blocked?: boolean; blocking?: unknown[]; rule?: string } | undefined
  const blocking = Array.isArray(gate?.blocking) ? gate!.blocking!.length : undefined
  if (gate?.blocked) {
    rows.push({ text: blocking === undefined
      ? 'Blocked: manual checks not settled'
      : `Blocked: ${blocking} manual check${blocking === 1 ? '' : 's'} not settled` })
  }
  else if (gate) rows.push({ text: 'Nothing blocks it' })
  const owed = Array.isArray(release.still_owed) ? release.still_owed as { id?: string; title?: string }[] : []
  if (owed.length) {
    rows.push({ text: 'Still owed before it ships', head: true })
    for (const o of owed.slice(0, 8)) rows.push({ text: `${o.id ?? ''} ${o.title ?? ''}`.trim() })
    if (owed.length > 8) rows.push({ text: `and ${owed.length - 8} more`, dim: true })
  }
  return rows
}

/** What the two command panes draw, set when a command runs. */
const panes: { needs?: ReturnType<typeof needsRows>; release?: ReturnType<typeof releaseRows> } = {}

export const NEEDS_PANE = 'cockpit-needs'
export const RELEASE_PANE = 'cockpit-release'

/** Declares the two commands once per session. */
async function registerCommands($: EngineInterface): Promise<void> {
  if (line.commands) return
  line.commands = true
  try {
    await $.command.register({ name: NEEDS_PANE, description: 'What needs you, here and in the other projects (from the cockpit)', immediate: true })
    await $.command.register({ name: RELEASE_PANE, description: "Where this project's next release stands (from the cockpit)", immediate: true })
  } catch {
    line.commands = false
  }
}

async function runNeeds($: EngineInterface): Promise<void> {
  const reply = await sidecarCall($, '/api/cockpit/line')
  const answer = reply?.status === 200 ? lineAnswer(reply.json) : undefined
  panes.needs = needsRows(answer, answer ? await readElsewhere($) : undefined, await $.clock.now())
  await $.ui.open({ id: NEEDS_PANE, title: 'Needs you', focus: true, closeOnEscape: true })
  $.ui.invalidate('ui.render')
}

async function runRelease($: EngineInterface): Promise<void> {
  const reply = await sidecarCall($, '/api/cockpit/release')
  panes.release = releaseRows(reply?.status === 200 ? reply.json : undefined)
  await $.ui.open({ id: RELEASE_PANE, title: 'Release', focus: true, closeOnEscape: true })
  $.ui.invalidate('ui.render')
}

export const register: Register = on => {
  const st: DeliveryState = { mainTurnRunning: false, interrupted: false, polling: false }

  on('session.start', ($, e, next) => {
    ensurePoll($, st)
    ensureLinePoll($)
    void registerCommands($)
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
      // A turn can change what is owed: read the line's facts again now.
      ensureLinePoll($)
      void readLine($)
      void registerCommands($)
    }
    return next(e)
  })

  // The cockpit's segment on the project line (FEAT-0157 / TASK-0673), by
  // the rules in project-os's ADAPTER.md, "The project line".
  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const beneath = await next(e)
    if (e.props.hasSurvey) return beneath
    // A plugin reloaded mid-session hears no session.start.
    ensureLinePoll($)
    const f = line.facts
    if (!f.here && !f.others && !f.url) return beneath
    const { Box, Text, Button } = $.ui.resolve(e)
    const words = [f.here, f.others].filter(Boolean).join(' · ')
    // When the band is too narrow, the segment gives way before project-os's
    // facts do (ADAPTER.md "The project line", rule 1): it shrinks first.
    const segment = h(Box, { key: SEGMENT_KEY, flexDirection: 'row', flexShrink: 1000 },
      h(Text, { wrap: 'truncate-end' }, words ? ` · ${words} ` : ' · '),
      // The press is answered by the ui.press hook below, by key, without
      // next(): a Button must carry an onPress, and this one never runs.
      f.url ? h(Button, { key: OPEN_KEY, label: 'Open in cockpit', onPress: () => undefined }) : null)
    const joined = joinToLine(beneath, segment)
    if (joined !== undefined) return joined as typeof beneath
    return h(Box, { flexDirection: 'column' }, beneath, segment) as typeof beneath
  })

  // The button answers by key, wherever project-os has moved it (TASK-0674).
  on('ui.press', { plugin: 'project-os-cockpit', element: OPEN_KEY }, async ($, e) => {
    await openCockpit($)
    return { element: e.element }
  })

  // /cockpit-needs and /cockpit-release: a pane, and no Claude turn (TASK-0675).
  on('command.run', { command: NEEDS_PANE }, async ($) => {
    await runNeeds($).catch(() => undefined)
    return {}
  })
  on('command.run', { command: RELEASE_PANE }, async ($) => {
    await runRelease($).catch(() => undefined)
    return {}
  })
  on('ui.render', { component: 'Pane' }, async ($, e, next) => {
    const rows = e.requestId === NEEDS_PANE ? panes.needs : e.requestId === RELEASE_PANE ? panes.release : undefined
    if (!rows) return next(e)
    const { Box, Text } = $.ui.resolve(e)
    return h(Box, { flexDirection: 'column' },
      ...rows.map(r => h(Text, r.head ? { bold: true } : r.dim ? { dimColor: true } : {}, r.text)))
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
    noteMode(e)
    await postWithin($, e as unknown as Payload, SESSION_END_WAIT_MS)
    return next(e)
  })

  // A permission ask, offered to the cockpit before the terminal (FEAT-0159).
  // Claude Code's own verdict comes first; only its `ask` is ever replaced,
  // and only by the person's answer. A fault anywhere returns that verdict.
  on('tool.check', async ($, e, next) => {
    const asked = await next(e)
    if (!offerable(e, asked, session.mode)) return asked
    try {
      return await askCockpit($, e, asked, next.signal)
    } catch {
      return asked
    }
  }).catch(($, e, next) => next(e))

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
