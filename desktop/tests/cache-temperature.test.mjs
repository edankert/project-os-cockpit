// Behavioural guards for session temperature (FEAT-0081 / TASK-0346, ISS-0105).
//
// Runs against the BUILT file, evaluated the way the renderer loads it —
// a plain script defining a global, like `health-marks.js`.
//
// The thing worth guarding is a TRANSITION: amber before the TTL, grey
// after it. A guard shaped like `assert 'cold' in source` passes just as
// happily when the boundary is off by an order of magnitude or the tick
// that drives it never fires, which is exactly the defect ISS-0105
// records. So every case here crosses the boundary with an injected
// clock.

import { test, before } from 'node:test';
import assert from 'node:assert/strict';
import * as fs from 'node:fs/promises';
import * as path from 'node:path';
import * as vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const built = path.join(here, '..', 'dist', 'renderer', 'cache-temperature.js');

let cacheTemperature;
before(async () => {
  await fs.access(built);            // fail loudly rather than skip silently
  const src = await fs.readFile(built, 'utf-8');
  const ctx = vm.createContext({});
  vm.runInContext(`${src}\n;globalThis.__t = cacheTemperature;`, ctx);
  cacheTemperature = ctx.__t;
  assert.equal(typeof cacheTemperature, 'function',
    'cache-temperature.js must define a global `cacheTemperature`');
});

const HOUR = 60 * 60 * 1000;
const T0 = Date.parse('2026-08-06T12:00:00Z');
const at = (ms) => T0 + ms;
const waiting = { ts: '2026-08-06T12:00:00Z', state: 'waiting' };

// ---- the transition -------------------------------------------------

test('warm before the TTL, cold after it', () => {
  assert.equal(cacheTemperature(waiting, at(59 * 60 * 1000)), 'warm');
  assert.equal(cacheTemperature(waiting, at(61 * 60 * 1000)), 'cold');
});

test('the boundary is exactly one hour, not ten minutes or ten hours', () => {
  // Guards the magnitude: an off-by-60x error passes a "does it ever go
  // cold" test but makes the feature either useless or constant noise.
  assert.equal(cacheTemperature(waiting, at(HOUR - 1000)), 'warm');
  assert.equal(cacheTemperature(waiting, at(HOUR)), 'cold');
  assert.equal(cacheTemperature(waiting, at(10 * 60 * 1000)), 'warm');
});

test('stays cold as it ages — the 211-hour case from ISS-0105', () => {
  assert.equal(cacheTemperature(waiting, at(211 * HOUR)), 'cold');
});

test('a custom TTL moves the boundary with it', () => {
  assert.equal(cacheTemperature(waiting, at(6 * 60 * 1000), 5 * 60 * 1000), 'cold');
  assert.equal(cacheTemperature(waiting, at(4 * 60 * 1000), 5 * 60 * 1000), 'warm');
});

// ---- what must never go cold ----------------------------------------

test('a busy session is never cold, however stale its timestamp', () => {
  // `ts` records the last state CHANGE. An agent that has been busy for
  // three hours has published nothing since, but its cache is being read
  // and re-written on every turn.
  const busy = { ts: '2026-08-06T12:00:00Z', state: 'busy' };
  assert.equal(cacheTemperature(busy, at(3 * HOUR)), 'warm');
});

// ---- absence is not a state -----------------------------------------

test('no timestamp is unknown, not cold', () => {
  // ISS-0065: absence must not render as a confident state. `unknown`
  // leaves the square alone; `cold` would grey out a workspace whose age
  // was never measured.
  for (const input of [null, undefined, {}, { state: 'waiting' },
                       { ts: null, state: 'waiting' }]) {
    assert.equal(cacheTemperature(input, at(99 * HOUR)), 'unknown',
      `expected unknown for ${JSON.stringify(input)}`);
  }
});

test('an unparseable timestamp is unknown, not cold', () => {
  assert.equal(cacheTemperature({ ts: 'not a date', state: 'waiting' }, at(99 * HOUR)),
    'unknown');
});

test('a future timestamp is warm, not cold', () => {
  // Clock disagreement between the sidecar and the renderer must not
  // grey out a live workspace.
  assert.equal(cacheTemperature({ ts: '2026-08-06T13:00:00Z', state: 'waiting' }, T0),
    'warm');
});

// ---- the states the rail actually paints -----------------------------

test('needs-input goes cold too — one rule, per Edwin', () => {
  const needs = { ts: '2026-08-06T12:00:00Z', state: 'needs-input' };
  assert.equal(cacheTemperature(needs, at(30 * 60 * 1000)), 'warm');
  assert.equal(cacheTemperature(needs, at(2 * HOUR)), 'cold');
});

// ---- railKey / attentionIds / cacheBadge (ISS-0110) -------------------
//
// `cacheTemperature` guarded the decision; the three call sites and the
// strip renderer could all be deleted with a green suite. Their judgment
// now lives here, so these cases guard the behaviour rather than the
// reasoning behind it.

let railKey, attentionIds, cacheBadge;
before(async () => {
  const src = await fs.readFile(built, 'utf-8');
  const ctx = vm.createContext({});
  vm.runInContext(`${src}\n;Object.assign(globalThis, {railKey, attentionIds, cacheBadge});`, ctx);
  ({ railKey, attentionIds, cacheBadge } = ctx);
});

test('railKey: cold demotes to the grey idle dot, warm keeps its state', () => {
  assert.equal(railKey(waiting, at(30 * 60 * 1000)), 'waiting');
  assert.equal(railKey(waiting, at(2 * HOUR)), 'idle');
  const needs = { ts: '2026-08-06T12:00:00Z', state: 'needs-input' };
  assert.equal(railKey(needs, at(30 * 60 * 1000)), 'needs-input');
  assert.equal(railKey(needs, at(2 * HOUR)), 'idle');
});

test('railKey: busy stays busy; decayed is idle; absent is null', () => {
  assert.equal(railKey({ ts: '2026-08-06T12:00:00Z', state: 'busy' }, at(5 * HOUR)), 'busy');
  assert.equal(railKey({ ts: '2026-08-06T12:00:00Z', state: 'waiting', decayed_from: 'busy' }, T0), 'idle');
  assert.equal(railKey(null, T0), null);
  assert.equal(railKey({}, T0), null);
});

test('railKey: no timestamp keeps the state rather than greying it', () => {
  // unknown is not cold — greying here would assert an unmeasured age.
  assert.equal(railKey({ state: 'waiting' }, at(99 * HOUR)), 'waiting');
});

test('attentionIds: only waiting/needs-input, and only while warm', () => {
  const states = [
    ['fresh-wait', { ts: '2026-08-06T12:00:00Z', state: 'waiting' }],
    ['fresh-needs', { ts: '2026-08-06T12:00:00Z', state: 'needs-input' }],
    ['busy', { ts: '2026-08-06T12:00:00Z', state: 'busy' }],
    ['idle', { ts: '2026-08-06T12:00:00Z', state: 'idle' }],
    ['decayed', { ts: '2026-08-06T12:00:00Z', state: 'waiting', decayed_from: 'busy' }],
  ];
  assert.deepEqual(Array.from(attentionIds(states, at(30 * 60 * 1000))), ['fresh-wait', 'fresh-needs']);
  // The transition: same input, one hour later, the list is empty.
  assert.deepEqual(Array.from(attentionIds(states, at(61 * 60 * 1000))), []);
});

test('attentionIds: the 211-hour entries from ISS-0105 are gone', () => {
  const states = [
    ['recent', { ts: '2026-08-06T12:00:00Z', state: 'waiting' }],
    ['stale', { ts: '2026-07-28T13:00:00Z', state: 'waiting' }],
  ];
  assert.deepEqual(Array.from(attentionIds(states, at(60 * 1000))), ['recent']);
});

const baseBadge = {
  prefix_tokens: 612_000, state: 'warm', resume_cost_usd: 6.12,
  warm_cost_usd: 0.31, ttl_seconds: 3600, age_seconds: 120,
};

test('cacheBadge: nothing to say without a prefix', () => {
  assert.equal(cacheBadge(null), null);
  assert.equal(cacheBadge({ ...baseBadge, prefix_tokens: 0 }), null);
});

test('cacheBadge: each state gets its own label and its own tone', () => {
  assert.equal(cacheBadge(baseBadge).label, 'warm');
  assert.equal(cacheBadge(baseBadge).tone, 'warm');
  assert.equal(cacheBadge(baseBadge).weight, '612k');

  const cold = cacheBadge({ ...baseBadge, state: 'cold', age_seconds: 7200 });
  assert.equal(cold.label, 'cold · ~$6.12');
  assert.equal(cold.tone, 'cold');
  assert.match(cold.title, /Starting a fresh session costs neither/);

  const cooling = cacheBadge({ ...baseBadge, state: 'cooling', cooling_minutes_left: 11 });
  assert.equal(cooling.label, 'cooling 11m');
  assert.equal(cooling.tone, 'cooling');
});

test('cacheBadge: a switch never borrows cold\'s colour (ISS-0107)', () => {
  const sw = { from: 'claude-opus-5', to: 'claude-opus-4-8', discarded_tokens: 612_000, cost_usd: 6.12 };
  const warm = cacheBadge({ ...baseBadge, model_switch: sw });
  assert.equal(warm.label, 'model switch · ~$6.12');
  assert.equal(warm.tone, 'warm', 'tone must follow the real temperature');
  assert.equal(warm.switch, true);
  assert.match(warm.title, /The cache is warm now/);

  const cold = cacheBadge({ ...baseBadge, state: 'cold', model_switch: sw });
  assert.equal(cold.tone, 'cold');
});

test('cacheBadge: weight formatting across magnitudes', () => {
  const w = (n) => cacheBadge({ ...baseBadge, prefix_tokens: n }).weight;
  assert.equal(w(612), '612');
  assert.equal(w(9_400), '9k');
  assert.equal(w(612_000), '612k');
  assert.equal(w(1_250_000), '1.3M');
  assert.equal(w(12_000_000), '12M');
});

test('cacheBadge: costs read as estimates, never as billing', () => {
  const cold = cacheBadge({ ...baseBadge, state: 'cold' });
  assert.match(cold.label, /~\$/);
  assert.ok(!/\$\d+\.\d{3}/.test(cold.title), 'no false precision');
});
