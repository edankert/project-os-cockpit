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
