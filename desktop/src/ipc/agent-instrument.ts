// Agent instrumentation at PTY spawn (FEAT-0019 / TASK-0115..0117).
//
// The embedded terminal auto-instruments Claude Code and Codex CLI
// sessions launched inside it, so agent lifecycle events flow to the
// workspace sidecar's `/api/agent-hook` endpoint with zero voluntary
// `cockpit signal` calls.
//
// Mechanism — per-workspace generated files under the app's own state
// dir (NEVER the user's ~/.claude or ~/.codex — RISK-0004):
//
//   instrument/<ws>/zdotdir/.zshrc     sources the user's real ~/.zshrc,
//                                      then wraps `claude` / `codex` in
//                                      shell functions that add per-spawn
//                                      config flags.
//   instrument/<ws>/claude-settings.json  command hooks (curl → sidecar)
//                                      for the lifecycle events + a
//                                      statusline forwarder.
//   instrument/<ws>/hook-forward.sh    stdin JSON → POST /api/agent-hook
//   instrument/<ws>/statusline.sh      statusline JSON → POST (debounced)
//                                      + echoes a short status string.
//   instrument/<ws>/codex-notify.sh    Codex notify argv[1] JSON → POST
//                                      with ?event= mapping.
//   instrument/<ws>/hook-env           COCKPIT_HOOK_URL=<sidecar url>;
//                                      rewritten whenever the sidecar
//                                      (re)spawns, so scripts always hit
//                                      the live port.
//
// Kill switch: COCKPIT_NO_INSTRUMENT=1 in the app's environment skips
// injection entirely; the scripts also honour it at runtime.

import { app } from 'electron';
import * as fs from 'node:fs';
import * as path from 'node:path';

const CLAUDE_HOOK_EVENTS = [
  'SessionStart',
  'UserPromptSubmit',
  'PreToolUse',
  'PostToolUse',
  'Notification',
  'PermissionRequest',
  'Stop',
  'SubagentStart',
  'SubagentStop',
  'SessionEnd',
] as const;

export function instrumentationDisabled(): boolean {
  return process.env.COCKPIT_NO_INSTRUMENT === '1';
}

function safeDirName(workspaceId: string): string {
  return workspaceId.replace(/[^a-zA-Z0-9_-]/g, '_');
}

function instrumentDirFor(workspaceId: string): string {
  return path.join(app.getPath('userData'), 'instrument', safeDirName(workspaceId));
}

function writeExecutable(filePath: string, content: string): void {
  fs.writeFileSync(filePath, content, { encoding: 'utf-8', mode: 0o755 });
}

function hookForwardScript(): string {
  return `#!/bin/sh
# project-os-cockpit (FEAT-0019): forward a Claude Code hook JSON blob
# (stdin) to the workspace sidecar. Never blocks the agent, never fails
# the hook — worst case the event is dropped.
DIR="$(cd "$(dirname "$0")" && pwd)"
[ -f "$DIR/hook-env" ] && . "$DIR/hook-env"
if [ -z "$COCKPIT_HOOK_URL" ] || [ -n "$COCKPIT_NO_INSTRUMENT" ]; then
  cat >/dev/null 2>&1
  exit 0
fi
curl -s -m 2 -X POST -H 'Content-Type: application/json' \\
  --data-binary @- "$COCKPIT_HOOK_URL/api/agent-hook" >/dev/null 2>&1
exit 0
`;
}

function statuslineScript(): string {
  return `#!/bin/sh
# project-os-cockpit (TASK-0117): forward the Claude Code statusline
# JSON (cost / context / rate limits) to the sidecar, debounced to one
# POST per 5s, and echo a short human status back for the terminal.
DIR="$(cd "$(dirname "$0")" && pwd)"
json="$(cat)"
[ -f "$DIR/hook-env" ] && . "$DIR/hook-env"
if [ -n "$COCKPIT_HOOK_URL" ] && [ -z "$COCKPIT_NO_INSTRUMENT" ]; then
  stamp="$DIR/.statusline-stamp"
  now=$(date +%s)
  last=$(cat "$stamp" 2>/dev/null || echo 0)
  if [ $((now - last)) -ge 5 ]; then
    echo "$now" > "$stamp"
    printf '%s' "$json" | curl -s -m 2 -X POST -H 'Content-Type: application/json' \\
      --data-binary @- "$COCKPIT_HOOK_URL/api/agent-hook?event=Statusline" >/dev/null 2>&1 &
  fi
fi
model=$(printf '%s' "$json" | sed -n 's/.*"display_name" *: *"\\([^"]*\\)".*/\\1/p' | head -1)
cost=$(printf '%s' "$json" | sed -n 's/.*"total_cost_usd" *: *\\([0-9][0-9.]*\\).*/\\1/p' | head -1)
out="\${model:-claude}"
[ -n "$cost" ] && out="$out · \\$\${cost}"
printf '%s' "$out"
`;
}

function codexNotifyScript(): string {
  return `#!/bin/sh
# project-os-cockpit (TASK-0116): Codex CLI notify forwarder. Codex
# invokes this with the notification JSON as argv[1]; map its event
# types onto the cockpit hook vocabulary and forward.
DIR="$(cd "$(dirname "$0")" && pwd)"
[ -f "$DIR/hook-env" ] && . "$DIR/hook-env"
if [ -z "$COCKPIT_HOOK_URL" ] || [ -n "$COCKPIT_NO_INSTRUMENT" ]; then
  exit 0
fi
payload="$1"
case "$payload" in
  *agent-turn-complete*) event="Stop" ;;
  *approval-requested*) event="PermissionRequest" ;;
  *) event="Notification" ;;
esac
printf '%s' "$payload" | curl -s -m 2 -X POST -H 'Content-Type: application/json' \\
  --data-binary @- "$COCKPIT_HOOK_URL/api/agent-hook?event=$event&agent=codex" >/dev/null 2>&1
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

function claudeSettings(dir: string): string {
  const forward = shellQuotePath(path.join(dir, 'hook-forward.sh'));
  const hooks: Record<string, unknown[]> = {};
  for (const event of CLAUDE_HOOK_EVENTS) {
    hooks[event] = [
      {
        hooks: [
          {
            type: 'command',
            command: forward,
            async: true,
            timeout: 5,
          },
        ],
      },
    ];
  }
  return JSON.stringify(
    {
      hooks,
      statusLine: {
        type: 'command',
        command: shellQuotePath(path.join(dir, 'statusline.sh')),
      },
    },
    null,
    2,
  );
}

function zshrc(dir: string): string {
  return `# project-os-cockpit instrumented shell (FEAT-0019).
# Sources your real zsh config first; the only additions are the
# claude/codex wrapper functions below. Disable with
# COCKPIT_NO_INSTRUMENT=1.
[ -f "$HOME/.zshrc" ] && source "$HOME/.zshrc"
if [ -z "$COCKPIT_NO_INSTRUMENT" ]; then
  # If your zshrc aliases claude/codex (ISS-0002): the names below are
  # QUOTED because zsh alias-expands unquoted names while parsing this
  # block — before the unalias ever runs — which is a parse error; and
  # the unalias is still required because zsh resolves aliases before
  # functions at invocation time. Net effect: inside the cockpit
  # terminal your claude/codex aliases give way to the instrumented
  # wrappers; outside it nothing changes.
  unalias claude 2>/dev/null
  unalias codex 2>/dev/null
  'claude'() { command claude --settings ${JSON.stringify(path.join(dir, 'claude-settings.json'))} "$@"; }
  'codex'() { command codex -c "notify=[${JSON.stringify(path.join(dir, 'codex-notify.sh')).replace(/"/g, '\\"')}]" "$@"; }
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
    writeExecutable(path.join(dir, 'hook-forward.sh'), hookForwardScript());
    writeExecutable(path.join(dir, 'statusline.sh'), statuslineScript());
    writeExecutable(path.join(dir, 'codex-notify.sh'), codexNotifyScript());
    fs.writeFileSync(
      path.join(dir, 'claude-settings.json'), claudeSettings(dir), 'utf-8',
    );
    // hook-env is owned by setSidecarUrl; create an empty placeholder
    // so the scripts' `. hook-env` never trips before the sidecar is up.
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
    fs.writeFileSync(path.join(zdotdir, '.zshrc'), zshrc(dir), 'utf-8');
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
 * Publish the live sidecar URL for a workspace. The generated scripts
 * source this file on every invocation, so a sidecar restart on a new
 * port transparently redirects the feed.
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
