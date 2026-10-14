// A prompt dispatched from the cockpit is submitted, not typed (FEAT-0158,
// TASK-0655).
//
// Run with `claude plugin test desktop/plugin/claude-code`. The test's own
// hooks stand for the world beneath the plugin: the sidecar answers the
// delivery list and records each claim and report, and `prompt.submit` holds
// each submission until the test lets it enter. A hook cannot raise
// `turn.start` itself, so the test raises it, as the engine would, before it
// lets the submission enter. The clock is `mock.clock`, so the plugin's
// one-second poll runs only when a test advances it.

import type { On } from 'claude-code'
import { describe, expect, mock, test } from 'claude-code/testing'

const DIR = '/instrument/ws'
const SESSION = 's-d'

type Call = { method: string; path: string; body: Record<string, unknown> }
type Listed = { did: string; prompt: string; state: string }

type World = {
  calls: Call[]
  submitted: string[]
  posts: (path: string) => Record<string, unknown>[]
  /** Lets the held submission enter, as the engine does once its turn started. */
  enter: () => void
}

/** The sidecar and the engine beneath the plugin. */
function world(on: On, options: {
  deliveries?: Listed[]
  claimStatus?: number
  /** What `prompt.submit` answers beneath instead of holding, e.g. a drop. */
  submit?: (e: { text: string }) => unknown
} = {}): World {
  const calls: Call[] = []
  const submitted: string[] = []
  const deliveries = options.deliveries ?? [{ did: 'd-1', prompt: 'implement TASK-0001', state: 'waiting' }]
  on('fs.read', ($, e, next) =>
    e.path === `${DIR}/hook-env` ? { value: 'COCKPIT_HOOK_URL="http://127.0.0.1:8766"\n' } : next(e))
  on('http.fetch', ($, e) => {
    const path = e.url.replace('http://127.0.0.1:8766', '')
    const body = JSON.parse(e.init?.body ?? '{}')
    calls.push({ method: e.init?.method ?? 'GET', path, body })
    let status = 200
    let text = '{"ok":true}'
    if (path.startsWith('/api/cockpit/deliveries?session=')) {
      text = JSON.stringify({ deliveries: deliveries.filter(d => d.state !== 'started') })
    } else if (path === '/api/cockpit/deliveries/claim') {
      status = options.claimStatus ?? 200
      const d = deliveries.find(x => x.did === body.did)
      if (status === 200 && d) d.state = 'sending'
    } else if (path === '/api/cockpit/deliveries/started') {
      const d = deliveries.find(x => x.did === body.did)
      if (d) d.state = 'started'
    }
    return { value: { status, ok: status === 200, headers: {}, text } }
  })
  on('session.id', () => ({ value: SESSION }))
  on('session.start', ($, e) => ({ cwd: e.cwd }))
  on('turn.start', ($, e) => ({ turnId: e.turnId }))
  on('turn.complete', ($, e) => ({ text: e.answer }))
  const held: (() => void)[] = []
  on('prompt.submit', async ($, e) => {
    submitted.push(e.text)
    if (options.submit) return options.submit(e)
    await new Promise<void>(resolve => { held.push(resolve) })
    return { text: e.text }
  })
  return {
    calls,
    submitted,
    enter: () => { for (const resolve of held.splice(0)) resolve() },
    posts: (path: string) => calls.filter(c => c.method === 'POST' && c.path === path).map(c => c.body),
  }
}

/** Starts the session, so the plugin starts its poll. */
async function startSession($: any): Promise<void> {
  await $.session.start({ cwd: '/repo', surface: null, isInteractive: true })
}

describe('a waiting prompt is submitted while the session is idle', () => {
  test('it is claimed, submitted as the person\'s words, and its turn reported', async ($, on) => {
    mock.env(on, { COCKPIT_INSTRUMENT_DIR: DIR })
    const clock = mock.clock(on, { now: Date.UTC(2026, 9, 14, 14, 2) })
    const w = world(on)
    await startSession($)
    await clock.advance(1000)
    expect(w.posts('/api/cockpit/deliveries/claim')).toEqual([{ did: 'd-1' }])
    expect(w.submitted).toEqual(['implement TASK-0001'])
    await $.turn.start({ text: 'implement TASK-0001', turnId: 'turn-1' })
    w.enter()
    await clock.advance(0)
    expect(w.posts('/api/cockpit/deliveries/started')).toEqual([
      { did: 'd-1', turn_id: 'turn-1', started_at: '2026-10-14T14:02:01.000Z' },
    ])
    // The next tick finds nothing waiting and submits nothing more.
    await clock.advance(1000)
    expect(w.submitted.length).toBe(1)
  })

  test('nothing is submitted while a main-loop turn runs, and it is once the turn ends', async ($, on) => {
    mock.env(on, { COCKPIT_INSTRUMENT_DIR: DIR })
    const clock = mock.clock(on, { now: 0 })
    const w = world(on)
    await startSession($)
    // The person's own turn is running.
    await $.turn.start({ text: 'their own work', turnId: 'turn-0' })
    await clock.advance(3000)
    expect(w.posts('/api/cockpit/deliveries/claim')).toEqual([])
    expect(w.submitted).toEqual([])
    await $.turn.complete({ answer: 'done', durationMs: 5, isAborted: false, turnId: 'turn-0', reason: 'completed' } as any)
    await clock.advance(1000)
    expect(w.submitted).toEqual(['implement TASK-0001'])
  })

  test('a subagent\'s turn neither blocks the poll nor is taken for the prompt\'s', async ($, on) => {
    mock.env(on, { COCKPIT_INSTRUMENT_DIR: DIR })
    const clock = mock.clock(on, { now: 0 })
    const w = world(on)
    await startSession($)
    await $.turn.start({ text: 'explore', turnId: 'turn-sub', agentId: 'agent-1' })
    await clock.advance(1000)
    expect(w.submitted).toEqual(['implement TASK-0001'])
    // While the submission is held, a subagent's turn starts, then the prompt's own.
    await $.turn.start({ text: 'explore more', turnId: 'turn-sub-2', agentId: 'agent-1' })
    expect(w.posts('/api/cockpit/deliveries/started')).toEqual([])
    await $.turn.start({ text: 'implement TASK-0001', turnId: 'turn-main' })
    w.enter()
    await clock.advance(0)
    expect(w.posts('/api/cockpit/deliveries/started').map(b => b.turn_id)).toEqual(['turn-main'])
  })
})

describe('what is not submitted', () => {
  test('a refused claim submits nothing', async ($, on) => {
    mock.env(on, { COCKPIT_INSTRUMENT_DIR: DIR })
    const clock = mock.clock(on, { now: 0 })
    const w = world(on, { claimStatus: 409 })
    await startSession($)
    await clock.advance(1000)
    expect(w.posts('/api/cockpit/deliveries/claim')).toEqual([{ did: 'd-1' }])
    expect(w.submitted).toEqual([])
    expect(w.posts('/api/cockpit/deliveries/started')).toEqual([])
  })

  test('COCKPIT_NO_INSTRUMENT asks the sidecar nothing and submits nothing', async ($, on) => {
    mock.env(on, { COCKPIT_INSTRUMENT_DIR: DIR, COCKPIT_NO_INSTRUMENT: '1' })
    const clock = mock.clock(on, { now: 0 })
    const w = world(on)
    await startSession($)
    await clock.advance(3000)
    expect(w.calls).toEqual([])
    expect(w.submitted).toEqual([])
  })

  test('the turn is not reported before it starts', async ($, on) => {
    mock.env(on, { COCKPIT_INSTRUMENT_DIR: DIR })
    const clock = mock.clock(on, { now: 0 })
    const w = world(on)
    await startSession($)
    await clock.advance(1000)
    expect(w.submitted).toEqual(['implement TASK-0001'])
    await clock.advance(5000)
    expect(w.posts('/api/cockpit/deliveries/started')).toEqual([])
    await $.turn.start({ text: 'implement TASK-0001', turnId: 'turn-late' })
    w.enter()
    await clock.advance(0)
    expect(w.posts('/api/cockpit/deliveries/started').map(b => b.turn_id)).toEqual(['turn-late'])
  })

  test('a prompt the session refuses is reported as dropped, with the reason', async ($, on) => {
    mock.env(on, { COCKPIT_INSTRUMENT_DIR: DIR })
    const clock = mock.clock(on, { now: 0 })
    const w = world(on, { submit: () => ({ drop: 'blocked by a UserPromptSubmit hook' }) })
    await startSession($)
    await clock.advance(1000)
    expect(w.posts('/api/cockpit/deliveries/dropped')).toEqual([
      { did: 'd-1', reason: 'blocked by a UserPromptSubmit hook' },
    ])
    expect(w.posts('/api/cockpit/deliveries/started')).toEqual([])
  })
})
