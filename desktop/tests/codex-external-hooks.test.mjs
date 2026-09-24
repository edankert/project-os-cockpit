import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as fs from 'node:fs';
import * as os from 'node:os';
import * as path from 'node:path';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const { configureCodexExternalHooks } = require('../dist/ipc/codex-external-hooks.js');

test('Codex opt-in preserves user handlers through enable, refresh and disable', () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'codex hooks '));
  try {
    const target = path.join(dir, 'hooks.json');
    const original = { description: 'my hooks', hooks: {
      Stop: [{ matcher: 'keep', hooks: [{ type: 'command', command: 'my-handler' }] }],
    } };
    fs.writeFileSync(target, JSON.stringify(original));
    fs.writeFileSync(path.join(dir, 'config.toml'), 'keep login configuration');
    const script = path.join(dir, "it's my hook.py");
    assert.equal(configureCodexExternalHooks(true, script, dir).ok, true);
    const installed = fs.readFileSync(target, 'utf8');
    const parsed = JSON.parse(installed);
    assert.equal(Object.keys(parsed.hooks).length, 10);
    const own = parsed.hooks.Stop[1].hooks[0];
    assert.match(own.command, /'\\''/);
    assert.match(own.command, / codex$/);
    assert.equal(own.timeout, 3);
    assert.equal(configureCodexExternalHooks(true, script, dir).ok, true);
    assert.equal(fs.readFileSync(target, 'utf8'), installed);
    assert.deepEqual(JSON.parse(fs.readFileSync(`${target}.cockpit-backup`, 'utf8')), original);
    // A user can regroup our handler beside their own; removal must keep theirs.
    parsed.hooks.Stop[0].hooks.push(own);
    parsed.hooks.Stop.pop();
    fs.writeFileSync(target, JSON.stringify(parsed));
    assert.equal(configureCodexExternalHooks(false, script, dir).ok, true);
    assert.deepEqual(JSON.parse(fs.readFileSync(target, 'utf8')), original);
    assert.equal(fs.readFileSync(path.join(dir, 'config.toml'), 'utf8'), 'keep login configuration');
  } finally { fs.rmSync(dir, { recursive: true, force: true }); }
});

test('malformed Codex configuration is refused without replacement', () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'codex-invalid-'));
  try {
    const target = path.join(dir, 'hooks.json');
    for (const invalid of ['{', '[]', '{"hooks":[]}', '{"hooks":{"Stop":{}}}', '{"hooks":{"Stop":[{"hooks":42}]}}']) {
      fs.writeFileSync(target, invalid);
      for (const enabled of [true, false]) {
        assert.equal(configureCodexExternalHooks(enabled, '/tmp/hook.py', dir).ok, false);
        assert.equal(fs.readFileSync(target, 'utf8'), invalid);
      }
    }
    assert.equal(fs.existsSync(`${target}.cockpit-backup`), false);
    assert.equal(configureCodexExternalHooks(false, '/tmp/hook.py', path.join(dir, 'absent')).ok, true);
    assert.equal(fs.existsSync(path.join(dir, 'absent')), false);
  } finally { fs.rmSync(dir, { recursive: true, force: true }); }
});
