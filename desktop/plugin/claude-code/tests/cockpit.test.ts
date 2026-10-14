// What the cockpit plugin posts, and when it posts nothing (TASK-0649).
//
// Run with `claude plugin test desktop/plugin/claude-code`. The test's own
// hooks stand for the world beneath the plugin: `fs.read` answers the
// workspace's hook-env file, and `http.fetch` records each post instead of
// sending it. A post is not awaited by the hook that starts it, so each test
// waits a moment before it reads what was posted.

import type { On } from 'claude-code'
import { describe, expect, mock, test } from 'claude-code/testing'

type Post = { url: string; body: Record<string, unknown> }

const DIR = '/instrument/ws'
const HOOK_ENV = 'COCKPIT_HOOK_URL="http://127.0.0.1:8766"\n'

/** Stands in for the hook-env file and the sidecar; returns the posts. */
function sidecar(on: On, hookEnv: () => string = () => HOOK_ENV): Post[] {
  const posts: Post[] = []
  on('fs.read', ($, e, next) =>
    e.path === `${DIR}/hook-env` ? { value: hookEnv() } : next(e))
  on('http.fetch', ($, e) => {
    posts.push({ url: e.url, body: JSON.parse(e.init?.body ?? '{}') })
    return { value: { status: 200, ok: true, headers: {}, text: '{"ok":true}' } }
  })
  // Nothing stands beneath the plugin in a test: answer each event the
  // tests raise as the engine would, with no settings hook configured.
  on('classic.SessionStart', () => ({}))
  on('classic.UserPromptSubmit', () => ({}))
  on('classic.Stop', () => ({}))
  on('classic.SessionEnd', () => ({}))
  on('session.measure', ($, e) => ({ changed: e.changed }))
  return posts
}

/** Lets the posts a hook started without awaiting reach the stand-in sidecar. */
const settle = (_?: unknown) => new Promise<void>(resolve => setTimeout(resolve, 50))

describe('lifecycle events', () => {
  test('a Stop is posted as its stdin JSON, marked as the plugin\'s', async ($, on) => {
    mock.env(on, { COCKPIT_INSTRUMENT_DIR: DIR })
    const posts = sidecar(on)
    await $.classic.Stop({ session_id: 's-1', cwd: '/repo', stop_hook_active: false })
    await settle($)
    expect(posts.length).toBe(1)
    expect(posts[0]?.url).toBe('http://127.0.0.1:8766/api/agent-hook')
    expect(posts[0]?.body).toEqual(expect.objectContaining({
      hook_event_name: 'Stop', session_id: 's-1', cwd: '/repo',
      agent: 'claude', _cockpit_plugin: true,
    }))
  })

  test('a prompt and a session start are posted with what the sidecar reads', async ($, on) => {
    mock.env(on, { COCKPIT_INSTRUMENT_DIR: DIR })
    const posts = sidecar(on)
    await $.classic.SessionStart({ session_id: 's-2', source: 'startup' })
    await $.classic.UserPromptSubmit({ session_id: 's-2', prompt: 'fix the rail' })
    await settle($)
    const names = posts.map(p => p.body.hook_event_name).sort()
    expect(names).toEqual(['SessionStart', 'UserPromptSubmit'])
    const prompt = posts.find(p => p.body.hook_event_name === 'UserPromptSubmit')
    expect(prompt?.body.prompt).toBe('fix the rail')
  })

  test('SessionEnd is delivered before the hook returns', async ($, on) => {
    mock.env(on, { COCKPIT_INSTRUMENT_DIR: DIR })
    const posts = sidecar(on)
    await $.classic.SessionEnd({ session_id: 's-3', reason: 'prompt_input_exit' })
    expect(posts.map(p => p.body.hook_event_name)).toEqual(['SessionEnd'])
  })
})

describe('when nothing is posted', () => {
  test('COCKPIT_NO_INSTRUMENT turns every post off', async ($, on) => {
    mock.env(on, { COCKPIT_INSTRUMENT_DIR: DIR, COCKPIT_NO_INSTRUMENT: '1' })
    const posts = sidecar(on)
    await $.classic.Stop({ session_id: 's-4', stop_hook_active: false })
    await $.classic.SessionEnd({ session_id: 's-4', reason: 'other' })
    await settle($)
    expect(posts.length).toBe(0)
  })

  test('a session outside a cockpit terminal posts nothing', async ($, on) => {
    mock.env(on, {})
    const posts = sidecar(on)
    await $.classic.Stop({ session_id: 's-5', stop_hook_active: false })
    await settle($)
    expect(posts.length).toBe(0)
  })

  test('an address that is not this machine is refused', async ($, on) => {
    mock.env(on, { COCKPIT_INSTRUMENT_DIR: DIR })
    const posts = sidecar(on, () => 'COCKPIT_HOOK_URL="http://example.com:8766"\n')
    await $.classic.Stop({ session_id: 's-6', stop_hook_active: false })
    await settle($)
    expect(posts.length).toBe(0)
  })

  test('an empty hook-env, before the sidecar is up, posts nothing', async ($, on) => {
    mock.env(on, { COCKPIT_INSTRUMENT_DIR: DIR })
    const posts = sidecar(on, () => '')
    await $.classic.Stop({ session_id: 's-7', stop_hook_active: false })
    await settle($)
    expect(posts.length).toBe(0)
  })
})

test('the address is read again for every post, so a respawned sidecar is found', async ($, on) => {
  mock.env(on, { COCKPIT_INSTRUMENT_DIR: DIR })
  let port = 8766
  const posts = sidecar(on, () => `COCKPIT_HOOK_URL="http://127.0.0.1:${port}"\n`)
  await $.classic.Stop({ session_id: 's-8', stop_hook_active: false })
  await settle($)
  port = 9100
  await $.classic.Stop({ session_id: 's-8', stop_hook_active: true })
  await settle($)
  expect(posts.map(p => p.url)).toEqual([
    'http://127.0.0.1:8766/api/agent-hook',
    'http://127.0.0.1:9100/api/agent-hook',
  ])
})

test('cost, context and rate limits are posted in the status line\'s shape', async ($, on) => {
  mock.env(on, { COCKPIT_INSTRUMENT_DIR: DIR })
  mock.clock(on, { now: 1_000_000 + 90_000 })
  const posts = sidecar(on)
  on('session.id', () => ({ value: 's-9' }))
  on('session.cwd', () => ({ value: '/repo' }))
  on('session.usage', () => ({
    value: { startedAt: 1_000_000, context: { window: 200_000, percent: 42 }, rateLimits: [], cost: { usd: 1.5 } },
  }))
  await $.session.measure({
    context: { window: 200_000, tokens: 84_000, percent: 42 },
    rateLimits: [
      { kind: 'five_hour', percentUsed: 12, resetsAt: '2026-10-14T18:00:00Z' },
      { kind: 'seven_day', percentUsed: 30 },
    ],
    cost: { usd: 1.5 },
    changed: ['context', 'rateLimits', 'cost'],
  })
  await settle()
  expect(posts.length).toBe(1)
  expect(posts[0]?.body).toEqual(expect.objectContaining({
    hook_event_name: 'Statusline',
    session_id: 's-9',
    cwd: '/repo',
    cost: { total_cost_usd: 1.5, total_duration_ms: 90_000 },
    context_window: { used_percentage: 42, context_window_size: 200_000 },
    rate_limits: {
      five_hour: { used_percentage: 12, resets_at: '2026-10-14T18:00:00Z' },
      seven_day: { used_percentage: 30 },
    },
    _cockpit_plugin: true,
  }))
})

test('PreToolUse is rebuilt into the stdin shape, with the edited file', async ($, on) => {
  mock.env(on, { COCKPIT_INSTRUMENT_DIR: DIR })
  const posts = sidecar(on)
  on('session.id', () => ({ value: 's-10' }))
  on('session.cwd', () => ({ value: '/repo' }))
  on('tool.call', () => ({ result: 'edited' }))
  await $.tool.call({ tool: 'Edit', file_path: '/repo/docs/TASK-0001.md', old_string: 'a', new_string: 'b' })
  await settle()
  const pre = posts.find(p => p.body.hook_event_name === 'PreToolUse')
  expect(pre?.body).toEqual(expect.objectContaining({
    session_id: 's-10',
    cwd: '/repo',
    tool_name: 'Edit',
    tool_input: expect.objectContaining({ file_path: '/repo/docs/TASK-0001.md' }),
    _cockpit_plugin: true,
  }))
})
