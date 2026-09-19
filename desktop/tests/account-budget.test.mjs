import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import vm from 'node:vm';
const source = await readFile(new URL('../dist/renderer/renderer.js', import.meta.url), 'utf8');
const start = source.indexOf('let latestRateLimits');
const end = source.indexOf('/** Repaint the attention panel', start);
assert.ok(start > 0 && end > start);
class Element {
  children = []; style = {}; attributes = {}; className = ''; textContent = '';
  classList = { add: name => { this.className += ` ${name}`; } };
  append(...nodes) { this.children.push(...nodes); }
  appendChild(node) { this.append(node); }
  setAttribute(key, value) { this.attributes[key] = value; }
}
function harness() {
  const ctx = vm.createContext({ document: { createElement: () => new Element() }, localStorage: { getItem: () => null, setItem: () => {} }, window: { setInterval: () => {}, setTimeout: () => {} }, refreshAttention: () => {}, cockpitApi: { agents: {} } });
  vm.runInContext(source.slice(start, end), ctx);
  return { ctx, run: code => vm.runInContext(code, ctx) };
}
const all = el => el ? [el, ...el.children.flatMap(all)] : [];
const text = el => all(el).map(n => n.textContent).join(' ');
const rows = el => all(el).filter(n => n.className === 'ws-budget-row');

test('OpenAI renders without Claude and uses existing colour thresholds', () => {
  const h = harness();
  assert.equal(h.run('buildBudgetBlock()'), null);
  for (const [pct, tier] of [[42, ''], [60, ' warn'], [85, ' crit']]) {
    h.run(`openAIWeekly = { used_percentage: ${pct}, resets_at: '2026-09-23T12:00:00Z' }; openAIUsageAsOf = Date.now()`);
    const block = h.run('buildBudgetBlock()');
    assert.match(text(block), /OpenAI/);
    assert.doesNotMatch(text(block), /Claude/);
    assert.match(text(block), /7d resets/);
    assert.equal(rows(block).length, 1);
    const fill = all(block).find(n => n.className === `ws-budget-fill${tier}`);
    assert.equal(fill.style.width, `${pct}%`);
    assert.equal(all(block).find(n => n.attributes.role === 'progressbar').attributes['aria-valuenow'], String(pct));
  }
});

test('both providers retain independent readings and freshness', () => {
  const h = harness();
  h.run(`latestRateLimits = { five_hour: { used_percentage: 12 }, seven_day: { used_percentage: 65 } }; rateLimitsAsOf = Date.now(); openAIWeekly = { used_percentage: 42 }; openAIUsageAsOf = Date.now() - 20*60000;`);
  const block = h.run('buildBudgetBlock()');
  assert.equal(rows(block).length, 3);
  assert.match(text(block).replace(/\s+/g, ' '), /Claude just now 5h 12% 7d 65% OpenAI 20m ago 7d 42%/);
  assert.equal(all(block).filter(n => n.className.includes('stale')).length, 1);
});

test('failed refresh keeps timestamp; successful absent weekly quota clears old data', async () => {
  const h = harness();
  h.ctx.cockpitApi.agents.codexUsage = async () => ({ weekly: { used_percentage: 42 }, capturedAt: 1000 });
  await h.run('pollOpenAIUsage()');
  h.ctx.cockpitApi.agents.codexUsage = async () => null;
  await h.run('pollOpenAIUsage()');
  assert.equal(h.run('openAIUsageAsOf'), 1000);
  assert.equal(h.run('openAIWeekly.used_percentage'), 42);
  h.ctx.cockpitApi.agents.codexUsage = async () => ({ weekly: null, capturedAt: 2000 });
  await h.run('pollOpenAIUsage()');
  assert.equal(h.run('buildBudgetBlock()'), null);
});
