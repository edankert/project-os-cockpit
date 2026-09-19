// The built Electron terminal routes a wheel gesture using tmux's inner pane
// state. Keep the pane in history for Codex and a shell, and keep arrow-key
// scrolling for an alternate-screen program such as Claude.

import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as fs from 'node:fs/promises';
import * as os from 'node:os';
import * as path from 'node:path';
import * as vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const built = path.join(here, '..', 'dist', 'ipc', 'terminal.js');

async function terminalHarness() {
  const source = await fs.readFile(built, 'utf-8');
  const handlers = new Map();
  const commands = [];
  const events = [];
  let quitCalls = 0;
  let ptyExit;
  const window = { id: 7, isDestroyed: () => false,
    webContents: { send: (channel, payload) => events.push({ channel, payload }) } };
  let paneState = '0 0 ';
  let mouseFlag = '0';
  const tmux = '/opt/homebrew/bin/tmux';
  const fakeRequire = (name) => {
    if (name === 'electron') return {
      app: { getPath: () => '/private/tmp/terminal-history-test', quit: () => { quitCalls++; } },
      BrowserWindow: {
        fromWebContents: (sender) => sender === 'owner' ? window : null,
        fromId: () => window,
      },
      ipcMain: {
        handle: (channel, handler) => handlers.set(channel, handler),
        on() {},
      },
    };
    if (name === 'node:child_process') return {
      execFileSync: () => 'tmux 3.7b',
      execFile: (_binary, args, _options, callback) => {
        commands.push([...args]);
        queueMicrotask(() => callback(null,
          args.includes('display-message')
            ? `${args.at(-1) === '#{mouse_any_flag}' ? mouseFlag : paneState}\n`
            : '', ''));
      },
    };
    if (name === 'node:fs') return {
      existsSync: (file) => file === tmux,
      mkdirSync() {},
      writeFileSync() {},
    };
    if (name === 'node:os') return os;
    if (name === 'node:path') return path;
    if (name === 'node-pty') return {
      spawn: () => ({ onData() {}, onExit(cb) { ptyExit = cb; }, write() {}, resize() {}, kill() {} }),
    };
    if (name === './agent-instrument') return { ensureInstrumentation: () => null };
    throw new Error(`Unexpected import: ${name}`);
  };
  const module = { exports: {} };
  vm.runInNewContext(source, {
    module,
    exports: module.exports,
    require: fakeRequire,
    process: { env: { SHELL: '/bin/zsh' }, platform: 'darwin' },
    console,
    setTimeout,
  }, { filename: built });
  module.exports.registerTerminalIpc({ getActiveWindow: () => window });
  const spawn = handlers.get('terminal:spawn')(
    { sender: 'owner' }, { workspaceId: 'test-workspace', cwd: '/private/tmp' });
  assert.equal(spawn.ok, true);
  assert.equal(spawn.viaTmux, true);
  return {
    commands,
    events,
    handlers,
    exitPty: (info) => ptyExit(info),
    quitCalls: () => quitCalls,
    setPaneState: (state) => { paneState = state; },
    setMouseFlag: (flag) => { mouseFlag = flag; },
    call: (channel, payload) => handlers.get(channel)(
      { sender: 'owner' }, { workspaceId: 'test-workspace', ...payload }),
  };
}

test('a terminal child exit notifies the pane without quitting Electron', async () => {
  const h = await terminalHarness();
  h.exitPty({ exitCode: 17, signal: 0 });
  assert.equal(h.quitCalls(), 0);
  assert.deepEqual(JSON.parse(JSON.stringify(h.events)), [{
    channel: 'terminal:exit',
    payload: { workspaceId: 'test-workspace', exitCode: 17, signal: 0 },
  }]);
});

test('Codex and a shell scroll tmux history while an alternate-screen program keeps arrow scrolling', async () => {
  const h = await terminalHarness();

  h.setPaneState('0 0 ');
  assert.equal((await h.call('terminal:scroll-history', { lines: -5 })).ok, true);
  assert.match(h.commands.at(-1).join(' '),
    /copy-mode -e -t cockpit-test-workspace ; send-keys -X -t cockpit-test-workspace -N 5 scroll-up$/);

  h.setPaneState('1 1 ');
  assert.equal((await h.call('terminal:scroll-history', { lines: -3 })).ok, true);
  assert.match(h.commands.at(-1).join(' '), /send-keys -t cockpit-test-workspace -N 3 Up$/);
  assert.equal(h.commands.at(-1).includes('copy-mode'), false);

  h.setPaneState('1 1 copy-mode');
  assert.equal((await h.call('terminal:scroll-history', { lines: 2 })).ok, true);
  assert.match(h.commands.at(-1).join(' '), /-N 2 scroll-down$/);
});

test('History remains available when an app owns mouse input, and invalid wheel amounts never reach tmux', async () => {
  const h = await terminalHarness();
  h.setPaneState('1 1 ');
  assert.equal((await h.call('terminal:history', {})).ok, true);
  assert.match(h.commands.at(-1).join(' '), /copy-mode -e -t cockpit-test-workspace$/);

  const before = h.commands.length;
  for (const lines of [0, 61, -61, 1.5]) {
    assert.equal((await h.call('terminal:scroll-history', { lines })).ok, false);
  }
  assert.equal(h.commands.length, before);
  assert.equal((await h.handlers.get('terminal:history')(
    { sender: 'different-window' }, { workspaceId: 'test-workspace' })).ok, false);
});

test('reattach reports the inner pane mouse state so the renderer can clear a stale mode', async () => {
  const h = await terminalHarness();
  h.setMouseFlag('0');
  assert.equal((await h.call('terminal:attach', {})).mouseRequested, false);
  h.setMouseFlag('1');
  assert.equal((await h.call('terminal:attach', {})).mouseRequested, true);
  h.setMouseFlag('unexpected');
  assert.equal((await h.call('terminal:attach', {})).mouseRequested, null);
});
