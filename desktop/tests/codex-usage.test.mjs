import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, writeFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { weeklyQuota, readCodexUsage } from '../dist/ipc/codex-usage.js';

const weekly = { usedPercent: 42, windowDurationMins: 10080, resetsAt: 1790154327 };
const general = (primary, secondary = null) => ({ rateLimits: { limitId: 'codex', primary, secondary } });

test('weekly-only and two-window plans report percent used and Unix reset seconds', () => {
  for (const value of [general(weekly), general({ ...weekly, windowDurationMins: 300 }, weekly)]) {
    assert.deepEqual(weeklyQuota(value), { used_percentage: 42, resets_at: new Date(weekly.resetsAt * 1000).toISOString() });
  }
  assert.deepEqual(weeklyQuota(general({ ...weekly, usedPercent: 0 })), { used_percentage: 0, resets_at: new Date(weekly.resetsAt * 1000).toISOString() });
});

test('general bucket wins; model-specific quota is never substituted', () => {
  const spark = { limitId: 'codex_spark', primary: { ...weekly, usedPercent: 99 } };
  assert.equal(weeklyQuota({ rateLimits: spark }), null);
  assert.equal(weeklyQuota({ ...general(weekly), rateLimitsByLimitId: { codex_spark: spark } }), null);
  assert.equal(weeklyQuota({ rateLimits: spark, rateLimitsByLimitId: { codex: general(weekly).rateLimits, codex_spark: spark } }).used_percentage, 42);
});

test('missing or malformed windows never become zero usage', () => {
  for (const value of [null, {}, [], general(null), general({ ...weekly, windowDurationMins: 300 }), ...[NaN, Infinity, -1, 101, '42'].map(usedPercent => general({ ...weekly, usedPercent }))]) {
    assert.equal(weeklyQuota(value), null);
  }
  assert.deepEqual(weeklyQuota(general({ ...weekly, resetsAt: 1e30 })), { used_percentage: 42 });
});

async function withServer(body, run) {
  const dir = await mkdtemp(join(tmpdir(), 'cockpit-quota-test-'));
  const command = join(dir, 'codex');
  await writeFile(command, `#!${process.execPath}\n${body}`, { mode: 0o700 });
  try { await run(command); } finally { await rm(dir, { recursive: true, force: true }); }
}

test('protocol waits for initialization, handles split lines, and returns only normalized quota', async () => {
  await withServer(`
const rl = require('node:readline').createInterface({ input: process.stdin });
let initialized = false;
rl.on('line', line => {
 const m = JSON.parse(line);
 if (m.method === 'initialize') process.stdout.write(JSON.stringify({id:1,result:{}})+'\\n');
 else if (m.method === 'initialized') initialized = true;
 else if (m.method === 'account/rateLimits/read' && initialized) {
  const reply = JSON.stringify({id:2,result:${JSON.stringify(general(weekly))}})+'\\n';
  process.stdout.write(reply.slice(0,13)); setTimeout(() => process.stdout.write(reply.slice(13)), 5);
 } else process.exit(2);
});`, async command => {
    const before = Date.now();
    const reading = await readCodexUsage(command);
    assert.equal(reading.weekly.used_percentage, 42);
    assert.ok(reading.capturedAt >= before);
    assert.deepEqual(Object.keys(reading).sort(), ['capturedAt', 'weekly']);
  });
});

test('absent executable, early exit, RPC error, and timeout settle without throwing', async () => {
  assert.equal(await readCodexUsage('/nonexistent/cockpit-codex-test'), null);
  await withServer('process.exit(1);', async command => assert.equal(await readCodexUsage(command), null));
  await withServer(`process.stdout.write(JSON.stringify({id:1,error:{message:'not signed in'}})+'\\n');setInterval(()=>{},1000);`, async command => assert.equal(await readCodexUsage(command), null));
  await withServer('setInterval(()=>{},1000);', async command => {
    const start = Date.now();
    assert.equal(await readCodexUsage(command, 150), null);
    assert.ok(Date.now() - start < 1500);
  });
});
