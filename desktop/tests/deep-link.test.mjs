// What a cockpit:// link opens (ISS-0293).
//
// Runs against the BUILT file, evaluated the way the renderer loads it: a
// plain script defining a global, like `cache-temperature.js`.
//
// The defect was that the target half of the link was never read. So every
// case here asserts the target, not only that a link parses.

import { test, before } from 'node:test';
import assert from 'node:assert/strict';
import * as fs from 'node:fs/promises';
import * as path from 'node:path';
import * as vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const built = path.join(here, '..', 'dist', 'renderer', 'deep-link.js');

let parse;
let bench;
before(async () => {
  await fs.access(built);            // fail loudly rather than skip silently
  const src = await fs.readFile(built, 'utf-8');
  // No URL in this context, deliberately. The renderer's Chromium 128 reads no
  // host from a cockpit:// URL while Node's does, so a parser built on URL
  // passed here and failed in the window (ISS-0293). Without URL, a parser
  // that reaches for it throws here instead.
  const ctx = vm.createContext({});
  vm.runInContext(
    `${src}\n;globalThis.__p = parseCockpitLink; globalThis.__b = designBenchTarget;`, ctx);
  parse = (url) => JSON.parse(JSON.stringify(ctx.__p(url)));
  bench = (id, designs) => ctx.__b(id, designs);
  assert.equal(typeof ctx.__p, 'function', 'deep-link.js must define parseCockpitLink');
  assert.equal(typeof ctx.__b, 'function', 'deep-link.js must define designBenchTarget');
});

test('a path is opened as the path the link names', () => {
  assert.deepEqual(
    parse('cockpit://your-health/docs/design/recovery-and-food-feedback/README.md'),
    { project: 'your-health',
      target: { kind: 'path', rel: 'docs/design/recovery-and-food-feedback/README.md' } });
});

test('a note ID is located rather than opened as a path', () => {
  assert.deepEqual(parse('cockpit://your-health/FEAT-0107'),
    { project: 'your-health', target: { kind: 'note', id: 'FEAT-0107' } });
  // Written in lower case it is still an ID, and is looked up in upper case.
  assert.deepEqual(parse('cockpit://your-health/iss-0293'),
    { project: 'your-health', target: { kind: 'note', id: 'ISS-0293' } });
});

test('a link with no target switches project only', () => {
  for (const url of ['cockpit://your-health', 'cockpit://your-health/']) {
    assert.deepEqual(parse(url), { project: 'your-health', target: { kind: 'none' } }, url);
  }
});

test('the workspace id the shell has always accepted still parses', () => {
  assert.deepEqual(parse('cockpit://1992b48aeaa2a9be/docs/README.md'),
    { project: '1992b48aeaa2a9be', target: { kind: 'path', rel: 'docs/README.md' } });
});

test('an encoded path is decoded, so a file name with a space opens', () => {
  assert.deepEqual(parse('cockpit://your-health/docs/design/a%20b.md').target,
    { kind: 'path', rel: 'docs/design/a b.md' });
});

test('a virtual page is passed through as a path', () => {
  assert.deepEqual(parse('cockpit://your-health/~overview').target,
    { kind: 'path', rel: '~overview' });
});

test('anything that is not a cockpit link is refused', () => {
  for (const url of [
    'https://your-health/docs/README.md',   // another scheme
    'cockpit:///docs/README.md',            // no project
    'not a url',
    'cockpit://your-health/docs/%E0%A4%A',  // a malformed escape
  ]) {
    assert.equal(parse(url), null, url);
  }
});

test('a path with a dot segment is refused, however it is written', () => {
  for (const url of [
    'cockpit://your-health/docs/../../etc/passwd',
    'cockpit://your-health/docs/%2E%2E/secret.md',
    'cockpit://your-health/docs%2F..%2F..%2Fsecret.md',
    'cockpit://your-health/./docs/README.md',
  ]) {
    assert.equal(parse(url), null, url);
  }
});

test('a fragment is kept, so the page opens at that heading', () => {
  assert.deepEqual(parse('cockpit://your-health/docs/design/README.md#conventions').target,
    { kind: 'path', rel: 'docs/design/README.md#conventions' });
});

test('a query is dropped rather than read as part of the path', () => {
  assert.deepEqual(parse('cockpit://your-health/docs/README.md?from=deck').target,
    { kind: 'path', rel: 'docs/README.md' });
});

test('the scheme is matched whatever its case', () => {
  assert.equal(parse('COCKPIT://your-health/FEAT-0107').target.id, 'FEAT-0107');
});

// ---- Where a link that names an ID lands (REQ-0062 / TASK-0606) ----------
//
// A hand-written design register, shaped like `GET /api/cockpit/designs`. The
// rule reads `id`, `asset` and `variants`; the other fields are there so the
// entries look like the real thing, and `has_asset` is there to show it is
// NOT what the rule reads.

const REGISTER = [
  { id: 'DES-0002', title: 'Recovery and food', rel: 'designs/DES-0002-Recovery-And-Food.md',
    asset: 'designs/DES-0002/index.html', has_asset: true, variants: [] },
  { id: 'DES-0003', title: 'Nothing drawn yet', rel: 'designs/DES-0003-Plain.md',
    asset: '', has_asset: false, variants: [] },
  { id: 'DES-0004', title: 'Only variants', rel: 'designs/DES-0004-Variants.md',
    asset: '', has_asset: false, variants: [{ name: 'A', html: '<p>a</p>' }] },
  { id: 'DES-0005', title: 'Asset path is wrong', rel: 'designs/DES-0005-Broken.md',
    asset: 'designs/DES-0005/missing.html', has_asset: false, variants: [] },
  { id: 'UX-0001', title: 'A design with another prefix', rel: 'ux/UX-0001-Other.md',
    asset: 'ux/UX-0001/index.html', has_asset: true, variants: [] },
];

test('a design with an asset opens the bench', () => {
  assert.equal(bench('DES-0002', REGISTER), '~design/DES-0002');
});

test('the ID matches whatever its case, and the bench uses the register spelling', () => {
  assert.equal(bench('des-0002', REGISTER), '~design/DES-0002');
  assert.equal(bench('ux-0001', REGISTER), '~design/UX-0001');
});

test('a design with variants and no asset opens the bench', () => {
  assert.equal(bench('DES-0004', REGISTER), '~design/DES-0004');
});

test('a declared asset whose file is missing opens the bench, which reports it', () => {
  // has_asset is false here: the rule reads whether an asset is DECLARED.
  assert.equal(bench('DES-0005', REGISTER), '~design/DES-0005');
});

test('a design with no asset and no variants opens its note', () => {
  assert.equal(bench('DES-0003', REGISTER), null);
});

test('a DES- ID the register does not list opens its note: the prefix does not decide', () => {
  assert.equal(bench('DES-0099', REGISTER), null);
});

test('a design whose ID has no DES- prefix opens the bench: the register decides', () => {
  assert.equal(bench('UX-0001', REGISTER), '~design/UX-0001');
});

test('any other ID opens its note, and so does every ID against an empty register', () => {
  assert.equal(bench('FEAT-0107', REGISTER), null);
  for (const id of ['DES-0002', 'FEAT-0107', 'UX-0001']) {
    assert.equal(bench(id, []), null, id);
  }
});

test('a register that is not a list opens the note rather than throwing', () => {
  for (const designs of [null, undefined, {}, 'DES-0002']) {
    assert.equal(bench('DES-0002', designs), null, String(designs));
  }
});
