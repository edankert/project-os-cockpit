// A permission ask is offered to the cockpit before the terminal, and only
// an ask (FEAT-0159, TASK-0665).
//
// Run with `claude plugin test desktop/plugin/claude-code`. The test's own
// `tool.check` hook stands for Claude Code beneath the plugin: its rules,
// mode and PreToolUse hooks, answering allow, ask or deny. Its `http.fetch`
// hook is the sidecar, holding one approval whose status the test sets. The
// clock is `mock.clock`, so the plugin's wait passes only as a test advances.

import type { On } from 'claude-code'
import { describe, expect, mock, test } from 'claude-code/testing'

const DIR = '/instrument/ws'

type Call = { method: string; path: string; body: Record<string, unknown> }
type Beneath = { decision: 'allow' | 'ask' | 'deny'; reason?: string; hook?: string; decider?: 'host' }

type Sidecar = {
  calls: Call[]
  /** The approval's status as the sidecar would report it now. */
  status: string
  /** What handed-back finds when it runs: a click may land first. */
  statusAtHandBack?: string
  waitMs: number
  unreachable: boolean
}

function world(on: On, beneath: Beneath, sidecar: Partial<Sidecar> = {}): Sidecar {
  const s: Sidecar = { calls: [], status: 'open', waitMs: 5000, unreachable: false, ...sidecar }
  on('fs.read', ($, e, next) =>
    e.path === `${DIR}/hook-env` ? { value: 'COCKPIT_HOOK_URL="http://127.0.0.1:8766"\n' } : next(e))
  on('http.fetch', ($, e) => {
    const path = e.url.replace('http://127.0.0.1:8766', '')
    const body = JSON.parse(e.init?.body ?? '{}')
    s.calls.push({ method: e.init?.method ?? 'GET', path, body })
    if (s.unreachable) throw new Error('connection refused')
    const record = () => ({ approval_id: 'a-1', status: s.status, decided_by: 'user:edwin' })
    let text = '{"ok":true}'
    if (path === '/api/cockpit/approvals/ask') {
      text = JSON.stringify({ ok: true, approval_id: s.waitMs > 0 ? 'a-1' : null, wait_ms: s.waitMs })
    } else if (path.startsWith('/api/cockpit/approvals?approval_id=')) {
      text = JSON.stringify({ ok: true, approval: record() })
    } else if (path === '/api/cockpit/approvals/handed-back') {
      if (s.statusAtHandBack) s.status = s.statusAtHandBack
      else if (s.status === 'open') s.status = 'handed-to-terminal'
      text = JSON.stringify({ ok: true, approval: record() })
    }
    return { value: { status: 200, ok: true, headers: {}, text } }
  })
  on('session.id', () => ({ value: 's-1' }))
  on('classic.UserPromptSubmit', () => ({}))
  on('tool.check', () => beneath)
  return s
}

const call = { tool: 'Bash', input: { command: 'rm -rf build' }, tool_use_id: 'toolu_1' }

/** Runs a check while the clock passes `ms`, a poll's worth at a time. */
async function checkOver($: any, clock: { advance: (ms: number) => Promise<void> }, e: unknown, ms = 6000) {
  let settled = false
  const result = $.tool.check(e).finally(() => { settled = true })
  for (let t = 0; t < ms && !settled; t += 250) await clock.advance(250)
  return result
}

const posted = (s: Sidecar, path: string) => s.calls.filter(c => c.path === path)

/** The calls about approvals; the prompt event also posts to /api/agent-hook. */
const approvalCalls = (s: Sidecar) => s.calls.filter(c => c.path.startsWith('/api/cockpit/approvals'))

/** The person's prompt, which tells the plugin the session's permission mode. */
async function inMode($: any, mode: string): Promise<void> {
  await $.classic.UserPromptSubmit({ prompt: 'go', permission_mode: mode })
}

describe('what the plugin never changes', () => {
  test('an allow from beneath is returned as it is, and nothing is offered', async ($, on) => {
    mock.env(on, { COCKPIT_INSTRUMENT_DIR: DIR })
    const clock = mock.clock(on, { now: 0 })
    const s = world(on, { decision: 'allow', reason: 'rule' }, { status: 'denied' })
    await inMode($, 'default')
    expect(await checkOver($, clock, call)).toEqual({ decision: 'allow', reason: 'rule' })
    expect(approvalCalls(s)).toEqual([])
  })

  test('a deny from a PreToolUse hook survives a cockpit that would grant', async ($, on) => {
    mock.env(on, { COCKPIT_INSTRUMENT_DIR: DIR })
    const clock = mock.clock(on, { now: 0 })
    const s = world(on, { decision: 'deny', reason: 'blocked by policy', hook: 'PreToolUse' }, { status: 'granted' })
    await inMode($, 'default')
    expect(await checkOver($, clock, call)).toEqual({ decision: 'deny', reason: 'blocked by policy', hook: 'PreToolUse' })
    expect(approvalCalls(s)).toEqual([])
  })
})

describe('an ask that is not offered', () => {
  const cases: [string, Record<string, unknown>, Beneath][] = [
    ['a query, which has no tool call', { tool: 'Bash', input: { command: 'ls' } }, { decision: 'ask' }],
    ['a question put to the person', { ...call, tool: 'AskUserQuestion' }, { decision: 'ask' }],
    ['a plan to approve', { ...call, tool: 'ExitPlanMode' }, { decision: 'ask' }],
    ['a tool whose ceiling is ask', { ...call, ceiling: 'ask' }, { decision: 'ask' }],
    ['an ask a hosted program answers', call, { decision: 'ask', decider: 'host' }],
  ]
  for (const [name, e, beneath] of cases) {
    test(name, async ($, on) => {
      mock.env(on, { COCKPIT_INSTRUMENT_DIR: DIR })
      const clock = mock.clock(on, { now: 0 })
      const s = world(on, beneath, { status: 'granted' })
      await inMode($, 'default')
      // The engine adds the tool's ceiling to the verdict it reports.
      expect(await checkOver($, clock, e)).toEqual({ ...beneath, ...('ceiling' in e ? { ceiling: e.ceiling } : {}) })
      expect(posted(s, '/api/cockpit/approvals/ask')).toEqual([])
    })
  }

  test('with the kill switch on', async ($, on) => {
    mock.env(on, { COCKPIT_INSTRUMENT_DIR: DIR, COCKPIT_NO_INSTRUMENT: '1' })
    const clock = mock.clock(on, { now: 0 })
    const s = world(on, { decision: 'ask' }, { status: 'granted' })
    await inMode($, 'default')
    expect(await checkOver($, clock, call)).toEqual({ decision: 'ask' })
    expect(approvalCalls(s)).toEqual([])
  })

  test('when the workspace turned cockpit answers off', async ($, on) => {
    mock.env(on, { COCKPIT_INSTRUMENT_DIR: DIR })
    const clock = mock.clock(on, { now: 0 })
    const s = world(on, { decision: 'ask' }, { waitMs: 0, status: 'granted' })
    await inMode($, 'default')
    expect(await checkOver($, clock, call)).toEqual({ decision: 'ask' })
    expect(approvalCalls(s).map(c => c.path)).toEqual(['/api/cockpit/approvals/ask'])
  })
})

describe('a permission mode in which nobody is asked in the terminal', () => {
  for (const mode of ['auto', 'dontAsk', 'plan', 'bypassPermissions']) {
    test(`${mode}: the ask is not offered`, async ($, on) => {
      mock.env(on, { COCKPIT_INSTRUMENT_DIR: DIR })
      const clock = mock.clock(on, { now: 0 })
      const s = world(on, { decision: 'ask' }, { status: 'granted' })
      await inMode($, mode)
      expect(await checkOver($, clock, call)).toEqual({ decision: 'ask' })
      expect(posted(s, '/api/cockpit/approvals/ask')).toEqual([])
    })
  }

  test('before any event has said the mode, nothing is offered', async ($, on) => {
    mock.env(on, { COCKPIT_INSTRUMENT_DIR: DIR })
    const clock = mock.clock(on, { now: 0 })
    const s = world(on, { decision: 'ask' }, { status: 'granted' })
    expect(await checkOver($, clock, call)).toEqual({ decision: 'ask' })
    expect(posted(s, '/api/cockpit/approvals/ask')).toEqual([])
  })

  test('acceptEdits asks the person, so its asks are offered', async ($, on) => {
    mock.env(on, { COCKPIT_INSTRUMENT_DIR: DIR })
    const clock = mock.clock(on, { now: 0 })
    world(on, { decision: 'ask' }, { status: 'granted' })
    await inMode($, 'acceptEdits')
    expect((await checkOver($, clock, call)).decision).toBe('allow')
  })
})

describe('an ask offered to the cockpit', () => {
  test('it carries the call, and a grant within the wait is an allow', async ($, on) => {
    mock.env(on, { COCKPIT_INSTRUMENT_DIR: DIR })
    const clock = mock.clock(on, { now: 0 })
    const s = world(on, { decision: 'ask' })
    await inMode($, 'default')
    let settled = false
    const result = $.tool.check(call).finally(() => { settled = true })
    await clock.advance(1000)
    expect(settled).toBe(false)
    s.status = 'granted'
    await clock.advance(250)
    expect(await result).toEqual({ decision: 'allow', reason: 'Approved in the cockpit by user:edwin.' })
    expect(posted(s, '/api/cockpit/approvals/ask')[0].body).toEqual({
      session_id: 's-1', tool: 'Bash', input: { command: 'rm -rf build' }, tool_use_id: 'toolu_1',
    })
    expect(posted(s, '/api/cockpit/approvals/handed-back')).toEqual([])
  })

  test('a denial within the wait is a deny the model reads', async ($, on) => {
    mock.env(on, { COCKPIT_INSTRUMENT_DIR: DIR })
    const clock = mock.clock(on, { now: 0 })
    world(on, { decision: 'ask' }, { status: 'denied' })
    await inMode($, 'default')
    expect(await checkOver($, clock, call)).toEqual({ decision: 'deny', reason: 'Denied in the cockpit by user:edwin.' })
  })

  test('when the wait runs out it is handed back and the terminal asks', async ($, on) => {
    mock.env(on, { COCKPIT_INSTRUMENT_DIR: DIR })
    const clock = mock.clock(on, { now: 0 })
    const beneath: Beneath = { decision: 'ask', reason: 'Bash needs permission' }
    const s = world(on, beneath)
    await inMode($, 'default')
    expect(await checkOver($, clock, call, 8000)).toEqual(beneath)
    expect(posted(s, '/api/cockpit/approvals/handed-back').map(c => c.body)).toEqual([{ approval_id: 'a-1' }])
    // About 5 s of polling, at 250 ms each.
    const polls = s.calls.filter(c => c.path.startsWith('/api/cockpit/approvals?')).length
    expect(polls >= 18 && polls <= 21).toBe(true)
  })

  test('a click that lands as the wait runs out still answers', async ($, on) => {
    mock.env(on, { COCKPIT_INSTRUMENT_DIR: DIR })
    const clock = mock.clock(on, { now: 0 })
    world(on, { decision: 'ask' }, { statusAtHandBack: 'granted' })
    await inMode($, 'default')
    expect(await checkOver($, clock, call, 8000)).toEqual({ decision: 'allow', reason: 'Approved in the cockpit by user:edwin.' })
  })

  test('an unreachable sidecar leaves the ask as it was', async ($, on) => {
    mock.env(on, { COCKPIT_INSTRUMENT_DIR: DIR })
    const clock = mock.clock(on, { now: 0 })
    world(on, { decision: 'ask', reason: 'Bash needs permission' }, { unreachable: true })
    await inMode($, 'default')
    expect(await checkOver($, clock, call)).toEqual({ decision: 'ask', reason: 'Bash needs permission' })
  })
})
