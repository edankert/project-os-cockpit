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
before(async () => {
  await fs.access(built);            // fail loudly rather than skip silently
  const src = await fs.readFile(built, 'utf-8');
  // No URL in this context, deliberately. The renderer's Chromium 128 reads no
  // host from a cockpit:// URL while Node's does, so a parser built on URL
  // passed here and failed in the window (ISS-0293). Without URL, a parser
  // that reaches for it throws here instead.
  const ctx = vm.createContext({});
  vm.runInContext(`${src}\n;globalThis.__p = parseCockpitLink;`, ctx);
  parse = (url) => JSON.parse(JSON.stringify(ctx.__p(url)));
  assert.equal(typeof ctx.__p, 'function', 'deep-link.js must define parseCockpitLink');
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

// The nine `designBenchTarget` cases that sat here went with the rule
// (FEAT-0148 / TASK-0614). A design ID opens its note, like every other ID,
// so there is nothing left in this file to decide about it. The record of the
// day it worked differently is REQ-0062 and FEAT-0146, both superseded.
