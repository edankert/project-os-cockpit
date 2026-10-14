// Agent instrumentation at PTY spawn (FEAT-0019 / TASK-0115..0117,
// FEAT-0156 / TASK-0650).
//
// The embedded terminal auto-instruments Claude Code and Codex CLI
// sessions launched inside it, so agent lifecycle events flow to the
// workspace sidecar's `/api/agent-hook` endpoint with zero voluntary
// `cockpit signal` calls.
//
// Claude Code reports through the cockpit plugin, `desktop/plugin/
// claude-code/`, which Claude Code loads from CLAUDE_CODE_PLUGIN_DIRS.
// The generated .zshrc appends the plugin's folder to that variable;
// nothing else is generated for Claude, and the user's own status line
// is left alone. Codex keeps the generated files below.
//
// Mechanism — per-workspace generated files under the app's own state
// dir (NEVER the user's ~/.claude or ~/.codex — RISK-0004):
//
//   instrument/<ws>/zdotdir/.zshrc     sources the user's real ~/.zshrc,
//                                      then puts the plugin on
//                                      CLAUDE_CODE_PLUGIN_DIRS and wraps
//                                      `codex` in a shell function that
//                                      adds per-spawn config flags.
//   instrument/<ws>/codex-hook-forward.sh  Codex hook stdin JSON → POST.
//   instrument/<ws>/codex-launch.sh    per-launch Codex flags; regenerated
//                                      when the app attaches to the workspace.
//   instrument/<ws>/hook-env           COCKPIT_HOOK_URL=<sidecar url>;
//                                      rewritten whenever the sidecar
//                                      (re)spawns, so the scripts and the
//                                      plugin always hit the live port.
//
// An earlier version also wrote claude-settings.json, hook-forward.sh and
// statusline.sh here. They are no longer written, and deliberately not
// deleted: a terminal opened before the update still runs
// `claude --settings <that file>`, and Claude Code refuses to start when
// the file is missing. Closing that terminal retires them.
//
// Kill switch: COCKPIT_NO_INSTRUMENT=1 in the app's environment skips
// injection entirely; the scripts and the plugin also honour it at
// runtime.

import { app } from 'electron';
import * as fs from 'node:fs';
import * as path from 'node:path';

export const CODEX_HOOK_EVENTS = [
  'SessionStart',
  'UserPromptSubmit',
  'PreToolUse',
  'PostToolUse',
  'PermissionRequest',
  'SubagentStart',
  'SubagentStop',
  'Interrupt',
  'Stop',
  'SessionEnd',
] as const;

export function instrumentationDisabled(): boolean {
  return process.env.COCKPIT_NO_INSTRUMENT === '1';
}

function safeDirName(workspaceId: string): string {
  return workspaceId.replace(/[^a-zA-Z0-9_-]/g, '_');
}

function instrumentRoot(): string {
  return path.join(app.getPath('userData'), 'instrument');
}

function instrumentDirFor(workspaceId: string): string {
  return path.join(instrumentRoot(), safeDirName(workspaceId));
}

/** The workspace's instrument folder when it exists, else null. It exists
 *  once a terminal in that workspace has been opened; a file meant for that
 *  terminal's agents is pointless before then (FEAT-0157). */
export function existingInstrumentDir(workspaceId: string): string | null {
  const dir = instrumentDirFor(workspaceId);
  try {
    return fs.statSync(dir).isDirectory() ? dir : null;
  } catch {
    return null;
  }
}

function writeExecutable(filePath: string, content: string): void {
  fs.writeFileSync(filePath, content, { encoding: 'utf-8', mode: 0o755 });
}

/**
 * The cockpit plugin's folder (FEAT-0156). The app runs from `desktop/`,
 * so the plugin is `<app path>/plugin/claude-code`. A packaged build keeps
 * app files inside `app.asar`, which Claude Code cannot read; the folder
 * would have to be unpacked, and this maps the path there. Undefined when
 * the folder is missing, so a broken checkout loads nothing.
 */
export function claudePluginDir(): string | undefined {
  const dir = path
    .join(app.getAppPath(), 'plugin', 'claude-code')
    .replace(`${path.sep}app.asar${path.sep}`, `${path.sep}app.asar.unpacked${path.sep}`);
  return fs.existsSync(path.join(dir, '.claude-plugin', 'plugin.json')) ? dir : undefined;
}

/** One forwarder for every project (TASK-0661). Codex trusts a hook by a
 *  hash of its command but keeps one trust entry per event, so a command that
 *  named each project's own folder was trusted in one project at a time
 *  (ISS-0322). The project is found from the terminal's environment instead:
 *  Codex hands a hook its session's environment, and every cockpit terminal
 *  sets COCKPIT_INSTRUMENT_DIR. */
function codexHookForwardScript(): string {
  return `#!/bin/sh
# project-os-cockpit (FEAT-0019, TASK-0661): forward an agent hook JSON
# blob (stdin) to the sidecar of the project whose terminal runs Codex.
# Never blocks the agent, never fails the hook — worst case the event is
# dropped.
COCKPIT_HOOK_URL=""
[ -n "$COCKPIT_INSTRUMENT_DIR" ] && [ -f "$COCKPIT_INSTRUMENT_DIR/hook-env" ] && . "$COCKPIT_INSTRUMENT_DIR/hook-env"
if [ -z "$COCKPIT_HOOK_URL" ] || [ -n "$COCKPIT_NO_INSTRUMENT" ]; then
  cat >/dev/null 2>&1
  printf '{}\\n'
  exit 0
fi
curl -s -m 2 -X POST -H 'Content-Type: application/json' \\
  --data-binary @- "$COCKPIT_HOOK_URL/api/agent-hook?agent=codex" >/dev/null 2>&1
printf '{}\\n'
exit 0
`;
}

// Hook commands run through a shell — the userData path contains a
// space ("Application Support"), so unquoted paths execute
// `/Users/…/Library/Application` and every hook fails silently
// (ISS-0003). Single-quote with '\'' splicing.
function shellQuotePath(p: string): string {
  return `'${p.replace(/'/g, `'\\''`)}'`;
}

function codexHookArgs(): string {
  // The same command in every project, so one trust covers them all.
  const forward = path.join(instrumentRoot(), 'codex-hook-forward.sh');
  // Codex's session-flag layer adds these hooks alongside user and project
  // layers. One handler per event avoids copying and double-running either.
  // Keep commands stable so Codex's normal hook trust review can remember them.
  return CODEX_HOOK_EVENTS.map((event) => {
    // TOML quotes delimit the value; the hook runner still passes the
    // decoded command to a shell. Quote the path a second time for that
    // shell because userData contains "Application Support" on macOS.
    const value = `hooks.${event}=[{hooks=[{type="command",command=${JSON.stringify(shellQuotePath(forward))},timeout=3}]}]`;
    return `-c ${shellQuotePath(value)}`;
  }).join(' ');
}

function codexLaunchScript(): string {
  return `#!/bin/sh
# The parent zsh can outlive a cockpit rebuild in tmux. Keep its function
# stable and load fresh Codex flags from this regenerated file each launch.
exec codex --no-alt-screen ${codexHookArgs()} "$@"
`;
}

function zshrc(dir: string, pluginDir: string | undefined): string {
  const plugin = pluginDir ? shellQuotePath(pluginDir) : '';
  // Appended, never assigned: a value you set in your zshrc, or that an
  // outer cockpit shell already set, is kept, and the folder is added once.
  const loadPlugin = pluginDir
    ? `  # Claude Code loads the cockpit plugin from here (FEAT-0156); it
  # reports this terminal's Claude sessions to the cockpit.
  case ":$CLAUDE_CODE_PLUGIN_DIRS:" in
    *:${plugin}:*) ;;
    *) export CLAUDE_CODE_PLUGIN_DIRS="\${CLAUDE_CODE_PLUGIN_DIRS:+$CLAUDE_CODE_PLUGIN_DIRS:}"${plugin} ;;
  esac
`
    : '';
  return `# project-os-cockpit instrumented shell (FEAT-0019, FEAT-0156).
# Sources your real zsh config first; the only additions are the cockpit
# plugin on CLAUDE_CODE_PLUGIN_DIRS and the codex wrapper function below.
# Disable with COCKPIT_NO_INSTRUMENT=1.
[ -f "$HOME/.zshrc" ] && source "$HOME/.zshrc"
if [ -z "$COCKPIT_NO_INSTRUMENT" ]; then
${loadPlugin}  # If your zshrc aliases codex (ISS-0002): the name below is QUOTED
  # because zsh alias-expands unquoted names while parsing this block —
  # before the unalias ever runs — which is a parse error; and the
  # unalias is still required because zsh resolves aliases before
  # functions at invocation time. Net effect: inside the cockpit
  # terminal your codex alias gives way to the instrumented wrapper;
  # outside it nothing changes. A claude alias is left alone.
  unalias codex 2>/dev/null
  'codex'() { ${shellQuotePath(path.join(dir, 'codex-launch.sh'))} "$@"; }
fi
`;
}

/**
 * Generate (or refresh) the instrumentation files for a workspace and
 * return the extra environment for the PTY spawn. Returns null when
 * instrumentation is disabled or unsupported on this platform.
 */
export function ensureInstrumentation(
  workspaceId: string,
): { env: Record<string, string>; zdotdir: string } | null {
  if (instrumentationDisabled()) return null;
  if (process.platform === 'win32') return null; // POSIX shells only in v1
  try {
    const dir = instrumentDirFor(workspaceId);
    const zdotdir = path.join(dir, 'zdotdir');
    fs.mkdirSync(zdotdir, { recursive: true });
    writeExecutable(path.join(instrumentRoot(), 'codex-hook-forward.sh'), codexHookForwardScript());
    writeExecutable(path.join(dir, 'codex-launch.sh'), codexLaunchScript());
    // hook-env is owned by setSidecarUrl; create an empty placeholder
    // so the scripts' `. hook-env` never trips before the sidecar is up,
    // and the plugin finds no address rather than a missing file.
    const hookEnv = path.join(dir, 'hook-env');
    if (!fs.existsSync(hookEnv)) fs.writeFileSync(hookEnv, '', 'utf-8');
    // zsh startup chain: source the user's real dotfiles, then wrap.
    fs.writeFileSync(
      path.join(zdotdir, '.zshenv'),
      '[ -f "$HOME/.zshenv" ] && source "$HOME/.zshenv"\n',
      'utf-8',
    );
    fs.writeFileSync(
      path.join(zdotdir, '.zprofile'),
      '[ -f "$HOME/.zprofile" ] && source "$HOME/.zprofile"\n',
      'utf-8',
    );
    const pluginDir = claudePluginDir();
    if (!pluginDir) console.error('[agent-instrument] cockpit plugin folder missing; Claude sessions will not report');
    fs.writeFileSync(path.join(zdotdir, '.zshrc'), zshrc(dir, pluginDir), 'utf-8');
    return {
      zdotdir,
      env: {
        ZDOTDIR: zdotdir,
        COCKPIT_INSTRUMENT_DIR: dir,
      },
    };
  } catch (err) {
    console.error('[agent-instrument] setup failed:', err);
    return null;
  }
}

/**
 * Rewrite the shared Codex forwarder and every project's `codex-launch.sh`,
 * at app start. A launcher is otherwise written only when the cockpit opens a
 * new terminal, so a tmux shell that outlived an update kept starting Codex
 * with the old hook command, and Codex asked for its review again in that
 * project (TASK-0661, found in TST-0095). The launcher is the same in every
 * project, so rewriting one that belongs to no open project is harmless.
 */
export function refreshCodexLaunchers(): void {
  if (instrumentationDisabled()) return;
  if (process.platform === 'win32') return;
  try {
    const root = instrumentRoot();
    if (!fs.existsSync(root)) return;
    writeExecutable(path.join(root, 'codex-hook-forward.sh'), codexHookForwardScript());
    for (const entry of fs.readdirSync(root, { withFileTypes: true })) {
      const launcher = path.join(root, entry.name, 'codex-launch.sh');
      if (entry.isDirectory() && fs.existsSync(launcher)) writeExecutable(launcher, codexLaunchScript());
    }
  } catch (err) {
    console.error('[agent-instrument] Codex launcher refresh failed:', err);
  }
}

/**
 * Publish the live sidecar URL for a workspace. The generated scripts
 * source this file, and the Claude plugin reads it, on every event, so a
 * sidecar restart on a new port transparently redirects the feed.
 */
export function setSidecarUrl(workspaceId: string, url: string | null): void {
  if (instrumentationDisabled()) return;
  try {
    const dir = instrumentDirFor(workspaceId);
    fs.mkdirSync(dir, { recursive: true });
    const content = url ? `COCKPIT_HOOK_URL=${JSON.stringify(url)}\n` : '';
    fs.writeFileSync(path.join(dir, 'hook-env'), content, 'utf-8');
  } catch (err) {
    console.error('[agent-instrument] hook-env write failed:', err);
  }
}
