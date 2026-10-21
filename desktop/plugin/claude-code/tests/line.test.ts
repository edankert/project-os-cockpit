// The cockpit's facts on the project line, the Open in cockpit button, and
// the two commands that answer in a pane (FEAT-0157, TASK-0673 to TASK-0675).
//
// Run with `claude plugin test desktop/plugin/claude-code`. The test's own
// hooks stand for the world beneath the plugin: `fs.read` answers the
// workspace's hook-env and needs-elsewhere.json, `http.fetch` is the sidecar,
// `process.run` records what the button would run, and `ui.render` beneath
// is either nothing (the engine's own) or project-os's line.

import type { On } from 'claude-code'
import { describe, expect, mock, test } from 'claude-code/testing'
import { lineAnswer, needsRows, openUrl, releaseRows, segmentFacts, workspaceOf, NOT_ANSWERING, NO_ELSEWHERE } from '../hooks/register.ts'

const DIR = '/instrument/ws-7'
const NOW = Date.UTC(2026, 9, 14, 21, 30)
const iso = (msAgo: number) => new Date(NOW - msAgo).toISOString()

const LINE = { schema_version: 1, needs_you: { total: 3, kinds: [{ kind: 'feature', count: 2, verb: 'Review', noun: 'features' }, { kind: 'requirement', count: 1, verb: 'Approve', noun: 'requirement' }] }, open_target: 'FEAT-0157' }
const ELSEWHERE = {
  schema_version: 1, written_at: iso(5_000), workspace_id: 'ws-7',
  projects: [
    { project: 'your-health', workspace_id: 'ws-1', count: 4, as_of: iso(5_000), source: 'live' },
    { project: 'your-trainer', workspace_id: 'ws-2', count: 1, as_of: iso(3 * 3600_000), source: 'cold' },
    { project: 'project-os-deck', workspace_id: 'ws-3', count: 0, as_of: iso(5_000), source: 'live' },
  ],
}

type World = { line: unknown; lineStatus: number; elsewhere: unknown; release: unknown; runs: string[][]; opened: string[]; submitted: string[]; projectLine: boolean }

function world(on: On, w: Partial<World> = {}): World {
  const s: World = { line: LINE, lineStatus: 200, elsewhere: ELSEWHERE, release: undefined, runs: [], opened: [], submitted: [], projectLine: false, ...w }
  mock.env(on, { COCKPIT_INSTRUMENT_DIR: DIR })
  mock.clock(on, { now: NOW })
  on('fs.read', ($, e, next) => {
    if (e.path === `${DIR}/hook-env`) return { value: 'COCKPIT_HOOK_URL="http://127.0.0.1:8766"\n' }
    if (e.path === `${DIR}/needs-elsewhere.json`) {
      if (s.elsewhere === undefined) throw new Error('ENOENT')
      return { value: JSON.stringify(s.elsewhere) }
    }
    return next(e)
  })
  on('http.fetch', ($, e) => {
    const path = e.url.replace('http://127.0.0.1:8766', '')
    if (path === '/api/cockpit/line') return { value: { status: s.lineStatus, ok: s.lineStatus === 200, headers: {}, text: JSON.stringify(s.line ?? { ok: false }) } }
    if (path === '/api/cockpit/release' && s.release) return { value: { status: 200, ok: true, headers: {}, text: JSON.stringify(s.release) } }
    if (path === '/api/cockpit/release') throw new Error('connection refused')
    return { value: { status: 200, ok: true, headers: {}, text: '{"deliveries":[]}' } }
  })
  on('process.run', ($, e) => {
    s.runs.push([...e.argv])
    return { value: { exitCode: 0, stdout: '', stderr: '', isStdoutTruncated: false, isStderrTruncated: false } }
  })
  on('ui.open', ($, e) => { s.opened.push(e.id); return { value: { isPlaced: true } } as any })
  on('prompt.submit', ($, e) => { s.submitted.push(e.text); return { text: e.text } })
  on('command.register', ($, e) => ({ value: { command: e.name } } as any))
  on('session.id', () => ({ value: 's-1' }))
  on('session.start', ($, e) => ({ cwd: e.cwd }))
  on('ui.render', { component: 'AbovePrompt' }, ($, e) => {
    const { Box, Text } = $.ui.resolve(e)
    return s.projectLine
      ? h(Box, { flexDirection: 'column' }, h(Box, { key: 'project-os:line', flexDirection: 'row' }, h(Text, {}, 'FEAT-0157 doing · PHASE-046')))
      : h(Box, {})
  })
  return s
}

const BAND = {
  component: 'AbovePrompt' as const,
  props: { hasSurvey: false, isWorking: false, maxRows: 10, bodyColumns: 160, scroll: { bodyRows: 9, offset: 0 }, view: {} } as any,
}

/** Lets the plugin's first background read finish. */
const settle = () => new Promise(r => setTimeout(r, 30))

async function started($: any): Promise<void> {
  await $.session.start({ cwd: '/repo', surface: null, isInteractive: true })
  await settle()
}

describe("the segment's facts (TASK-0673)", () => {
  test('this project, the other projects, and the button', () => {
    expect(segmentFacts(lineAnswer(LINE), ELSEWHERE as any, NOW, 'ws-7')).toEqual({
      here: '3 need you', others: '5 in other projects', url: 'cockpit://ws-7/FEAT-0157',
    })
  })

  test('one thing owed reads "1 needs you"', () => {
    const one = lineAnswer({ ...LINE, needs_you: { total: 1, kinds: [LINE.needs_you.kinds[1]] } })
    expect(segmentFacts(one, undefined, NOW, 'ws-7').here).toBe('1 needs you')
  })

  test("the button's workspace is the instrument folder's, with or without the other projects' file", () => {
    expect(workspaceOf('/instrument/ws-7')).toBe('ws-7')
    expect(workspaceOf('/instrument/ws-7/')).toBe('ws-7')
    expect(workspaceOf(undefined)).toBeUndefined()
    expect(segmentFacts(lineAnswer(LINE), undefined, NOW, 'ws-7').url).toBe('cockpit://ws-7/FEAT-0157')
    // The file's own workspace field is not where it comes from.
    expect(segmentFacts(lineAnswer(LINE), { ...ELSEWHERE, workspace_id: 'ws-other' } as any, NOW, 'ws-7').url).toBe('cockpit://ws-7/FEAT-0157')
  })

  test('zero here draws no count, and the button stays', () => {
    const f = segmentFacts(lineAnswer({ ...LINE, needs_you: { total: 0, kinds: [] } }), ELSEWHERE as any, NOW, 'ws-7')
    expect(f.here).toBeUndefined()
    expect(f.url).toBe('cockpit://ws-7/FEAT-0157')
  })

  test('no file draws no other-projects count', () => {
    expect(segmentFacts(lineAnswer(LINE), undefined, NOW).others).toBeUndefined()
  })

  test('a file the shell stopped refreshing draws no other-projects count', () => {
    const stale = { ...ELSEWHERE, written_at: iso(3 * 60_000) }
    expect(segmentFacts(lineAnswer(LINE), stale as any, NOW).others).toBeUndefined()
  })

  test('an unknown or day-old project adds a plus, and a sum of zero draws nothing', () => {
    const unknown = { ...ELSEWHERE, projects: [...ELSEWHERE.projects, { project: 'x', workspace_id: 'ws-9', count: null, as_of: null, source: 'unknown' }] }
    expect(segmentFacts(lineAnswer(LINE), unknown as any, NOW).others).toBe('5+ in other projects')
    const old = { ...ELSEWHERE, projects: [{ project: 'y', workspace_id: 'ws-8', count: 9, as_of: iso(25 * 3600_000), source: 'cold' }] }
    expect(segmentFacts(lineAnswer(LINE), old as any, NOW).others).toBeUndefined()
  })

  test('a failed line route draws no count and no button', () => {
    expect(lineAnswer({ ok: false, error: 'line not computed' })).toBeUndefined()
    const f = segmentFacts(undefined, ELSEWHERE as any, NOW, 'ws-7')
    expect(f.here).toBeUndefined()
    expect(f.url).toBeUndefined()
    expect(f.others).toBe('5 in other projects')
  })
})

describe('the segment on the band (TASK-0673)', () => {
  test("it joins the end of project-os's line when that is beneath", async ($, on) => {
    world(on, { projectLine: true })
    await started($)
    const ui = await $.ui.mount({ plugin: 'project-os-cockpit', surface: 'terminal', ...BAND })
    const lineEl = await ui.find({ key: 'project-os:line' })
    expect(lineEl!.text).toMatch(/^FEAT-0157 doing · PHASE-046 · 3 need you · 5 in other projects/)
    expect(await ui.find({ key: 'cockpit:open' })).toBeDefined()
    // One segment, inside the line: the cockpit draws no line of its own.
    expect(await ui.findAll({ key: 'segment:cockpit' })).toHaveLength(1)
    expect(lineEl!.text).toContain('Open in cockpit')
  })

  test('with nothing beneath it is drawn on its own', async ($, on) => {
    world(on)
    await started($)
    const ui = await $.ui.mount({ plugin: 'project-os-cockpit', surface: 'terminal', ...BAND })
    expect(await ui.find({ key: 'project-os:line' })).toBeUndefined()
    expect((await ui.find({ key: 'segment:cockpit' }))!.text).toContain('3 need you · 5 in other projects')
  })

  test('a survey passes through untouched', async ($, on) => {
    world(on)
    await started($)
    const ui = await $.ui.mount({ plugin: 'project-os-cockpit', surface: 'terminal', ...BAND, props: { ...BAND.props, hasSurvey: true } })
    expect(await ui.find({ key: 'segment:cockpit' })).toBeUndefined()
  })

  test('a failed line route draws no count and no button on the band', async ($, on) => {
    world(on, { lineStatus: 500, line: { ok: false } })
    await started($)
    const ui = await $.ui.mount({ plugin: 'project-os-cockpit', surface: 'terminal', ...BAND })
    expect(await ui.find({ key: 'cockpit:open' })).toBeUndefined()
    const seg = await ui.find({ key: 'segment:cockpit' })
    expect(seg?.text ?? '').not.toContain('need you')
  })
})

describe('Open in cockpit (TASK-0674)', () => {
  test('the link names the workspace and the focus item, or only the workspace', () => {
    expect(openUrl('ws-7', 'FEAT-0157')).toBe('cockpit://ws-7/FEAT-0157')
    expect(openUrl('ws-7', null)).toBe('cockpit://ws-7')
  })

  test('a malformed workspace or target gives no link', () => {
    expect(openUrl('ws 7; rm -rf ~', 'FEAT-0157')).toBeUndefined()
    expect(openUrl('ws-7', 'FEAT-0157/../../x')).toBeUndefined()
    expect(openUrl(undefined, 'FEAT-0157')).toBeUndefined()
  })

  test('a press runs open with the link as one argument', async ($, on) => {
    const w = world(on)
    await started($)
    const ui = await $.ui.mount({ plugin: 'project-os-cockpit', surface: 'terminal', ...BAND })
    await ui.press({ key: 'cockpit:open' })
    expect(w.runs).toEqual([['open', 'cockpit://ws-7/FEAT-0157']])
  })

  test('a malformed folder name draws no button', () => {
    expect(segmentFacts(lineAnswer(LINE), ELSEWHERE as any, NOW, workspaceOf('/instrument/ws 7')).url).toBeUndefined()
    expect(segmentFacts(lineAnswer(LINE), ELSEWHERE as any, NOW, workspaceOf('/instrument/..')).url).toBeUndefined()
  })

  test("before the shell has written the other projects' file, the button is there and works", async ($, on) => {
    const w = world(on, { elsewhere: undefined })
    await started($)
    const ui = await $.ui.mount({ plugin: 'project-os-cockpit', surface: 'terminal', ...BAND })
    const seg = await ui.find({ key: 'segment:cockpit' })
    expect(seg!.text).not.toContain('in other projects')
    await ui.press({ key: 'cockpit:open' })
    expect(w.runs).toEqual([['open', 'cockpit://ws-7/FEAT-0157']])
  })
})

describe('/cockpit-needs and /cockpit-release (TASK-0675)', () => {
  test("the needs pane lists this project's kinds, then the other projects, the empty ones last", () => {
    const rows = needsRows(lineAnswer(LINE), ELSEWHERE as any, NOW).map(r => r.text)
    expect(rows).toEqual([
      'This project', '2 features to review', '1 requirement to approve',
      'Other projects', 'your-health: 4 · live', 'your-trainer: 1 · counted 3h ago', 'project-os-deck: 0 · live',
    ])
  })

  test('the panes say when the cockpit or the shell is not answering', () => {
    expect(needsRows(undefined, ELSEWHERE as any, NOW).map(r => r.text)).toEqual([NOT_ANSWERING])
    expect(needsRows(lineAnswer(LINE), undefined, NOW).map(r => r.text)).toContain(NO_ELSEWHERE)
    expect(releaseRows(undefined).map(r => r.text)).toEqual([NOT_ANSWERING])
  })

  test('the release pane says where the release stands', () => {
    // The gate blocks on 3 checks across the repo; 2 of them are for what this
    // release carries. The blocked count is the gate's.
    const rows = releaseRows({ title: 'Next release', exists: false, preparing: false, contents: { count: 119, since: 'REL-0001' }, gate: { blocked: true, blocking: [{}, {}, {}] }, open_tests: [{}, {}], still_owed: [] }).map(r => r.text)
    expect(rows).toEqual(['Next release: not prepared yet', '119 items since REL-0001', 'Blocked: 3 manual checks not settled'])
  })

  test('each command opens its pane and starts no turn', async ($, on) => {
    const w = world(on, { release: { title: 'Next release', exists: false, contents: { count: 1 }, gate: { blocked: false }, open_tests: [] } })
    await started($)
    const needs = await $.command.run({ command: 'cockpit-needs' } as any)
    const release = await $.command.run({ command: 'cockpit-release' } as any)
    expect(needs.text).toBeUndefined()
    expect(release.text).toBeUndefined()
    expect(w.opened).toEqual(['cockpit-needs', 'cockpit-release'])
    expect(w.submitted).toEqual([])
    const pane = await $.ui.mount({ plugin: 'project-os-cockpit', surface: 'terminal', component: 'Pane', requestId: 'cockpit-needs', props: {} as any })
    expect(await pane.find({ type: 'Text', text: '2 features to review' })).toBeDefined()
  })
})
