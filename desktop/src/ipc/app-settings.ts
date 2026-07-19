// App settings + the external agent-state hook (FEAT-0027).
//
// One persisted settings object (userData/app-settings.json) behind
// `settings:get` / `settings:set` IPC. The only setting so far:
// `externalHook` — when the user flips it on, the cockpit installs a
// hook into ~/.claude/settings.json so Claude sessions in ANY terminal
// signal agent state; flipping it off removes exactly our entries.
//
// ~/.claude is user config — the app touches it ONLY through this
// explicit toggle (RISK-0004). The edit is surgical: entries are
// identified by the hook script's path (which lives under our own
// userData dir), a one-time backup is written beside the file, and
// uninstall filters only marker-matched entries, preserving formatting
// of everything else via a full JSON round-trip.
//
// The hook script itself is Python (stdlib-only): no-op outside
// project-os repos (SNAPSHOT.yaml walk-up); POSTs the raw payload to
// the sidecar named by `.cockpit/url` when present (full FEAT-0019
// pipeline); otherwise writes `.cockpit/agent-state.json` atomically.

import { app, ipcMain } from 'electron';
import * as fs from 'node:fs';
import * as os from 'node:os';
import * as path from 'node:path';

export interface AppSettings {
  externalHook: boolean;
}

const DEFAULTS: AppSettings = { externalHook: false };

const HOOK_EVENTS = [
  'UserPromptSubmit', 'PostToolUse', 'PermissionRequest',
  'Notification', 'Stop', 'SessionEnd',
] as const;

let settings: AppSettings = { ...DEFAULTS };

function settingsPath(): string {
  return path.join(app.getPath('userData'), 'app-settings.json');
}

function hookDir(): string {
  return path.join(app.getPath('userData'), 'external-hook');
}

function hookScriptPath(): string {
  return path.join(hookDir(), 'agent-state-hook.py');
}

function claudeSettingsPath(): string {
  return path.join(os.homedir(), '.claude', 'settings.json');
}

function loadSettings(): void {
  try {
    const raw = JSON.parse(fs.readFileSync(settingsPath(), 'utf-8'));
    if (raw && typeof raw === 'object') {
      settings = { ...DEFAULTS, ...(raw as Partial<AppSettings>) };
    }
  } catch { /* first run */ }
}

function persistSettings(): void {
  try {
    fs.writeFileSync(settingsPath(), JSON.stringify(settings, null, 2), 'utf-8');
  } catch (err) {
    console.error('[app-settings] persist failed:', err);
  }
}

function hookScript(): string {
  return `#!/usr/bin/env python3
"""project-os-cockpit external agent-state hook (FEAT-0027).

Installed into ~/.claude/settings.json by the cockpit's settings
toggle; remove it there (or flip the toggle off) to disable. Reads one
Claude Code hook payload from stdin. In project-os repos only:
forwards to the workspace's running cockpit when one is discoverable,
else writes .cockpit/agent-state.json so the desktop rail dot updates.
Never blocks, never fails the hook.
"""
import datetime
import json
import os
import sys
import urllib.request

STATE_BY_EVENT = {
    "UserPromptSubmit": "busy",
    "PostToolUse": "busy",
    "PermissionRequest": "needs-input",
    "Stop": "waiting",
    "SessionEnd": "idle",
}

# Notification is subtype-gated to match the sidecar tracker
# (TASK-0156/0153): only a mid-work block is the red needs-input tier;
# an idle_prompt (turn finished) is amber waiting; anything else is not
# an attention signal at all.
NEEDS_INPUT_NOTIFICATIONS = ("permission_prompt", "elicitation_dialog")
WAITING_NOTIFICATIONS = ("idle_prompt",)


def state_for(payload):
    event = payload.get("hook_event_name") or ""
    if event == "Notification":
        ntype = payload.get("notification_type")
        if ntype in NEEDS_INPUT_NOTIFICATIONS:
            return "needs-input"
        if ntype in WAITING_NOTIFICATIONS:
            return "waiting"
        return None
    return STATE_BY_EVENT.get(event)


def find_root(start):
    cur = os.path.abspath(start)
    for _ in range(12):
        if os.path.isfile(os.path.join(cur, "SNAPSHOT.yaml")):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            return None
        cur = parent
    return None


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    if not isinstance(payload, dict):
        return 0
    root = find_root(payload.get("cwd") or os.getcwd())
    if not root:
        return 0
    ck = os.path.join(root, ".cockpit")
    url_file = os.path.join(ck, "url")
    if os.path.isfile(url_file):
        try:
            base = open(url_file, encoding="utf-8").read().strip()
            if base.startswith("http://127.0.0.1") or base.startswith("http://localhost"):
                req = urllib.request.Request(
                    base + "/api/agent-hook",
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                )
                urllib.request.urlopen(req, timeout=2)
                return 0
        except Exception:
            pass  # cockpit gone or unreachable — fall back to the file
    state = state_for(payload)
    if not state:
        return 0
    try:
        os.makedirs(ck, exist_ok=True)
        ts = datetime.datetime.now(datetime.timezone.utc).isoformat(
            timespec="milliseconds")
        tmp = os.path.join(ck, "agent-state.json.tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"state": state, "ts": ts, "agent": "claude",
                       "source": "external-hook"}, f)
        os.replace(tmp, os.path.join(ck, "agent-state.json"))
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
`;
}

function hookCommand(): string {
  return `python3 '${hookScriptPath().replace(/'/g, `'\\''`)}'`;
}

function isOurEntry(entry: unknown): boolean {
  if (!entry || typeof entry !== 'object') return false;
  const hooks = (entry as { hooks?: unknown }).hooks;
  if (!Array.isArray(hooks)) return false;
  return hooks.some((h) =>
    h && typeof h === 'object'
    && typeof (h as { command?: unknown }).command === 'string'
    && ((h as { command: string }).command).includes('external-hook/agent-state-hook.py'));
}

export function installExternalHook(): { ok: boolean; error?: string } {
  try {
    fs.mkdirSync(hookDir(), { recursive: true });
    fs.writeFileSync(hookScriptPath(), hookScript(), { encoding: 'utf-8', mode: 0o755 });
    const target = claudeSettingsPath();
    let userSettings: Record<string, unknown> = {};
    if (fs.existsSync(target)) {
      try {
        userSettings = JSON.parse(fs.readFileSync(target, 'utf-8')) as Record<string, unknown>;
      } catch {
        return { ok: false, error: '~/.claude/settings.json is not valid JSON — not touching it' };
      }
      const backup = `${target}.cockpit-backup`;
      if (!fs.existsSync(backup)) fs.copyFileSync(target, backup);
    } else {
      fs.mkdirSync(path.dirname(target), { recursive: true });
    }
    const hooks = (userSettings.hooks && typeof userSettings.hooks === 'object')
      ? userSettings.hooks as Record<string, unknown[]> : {};
    for (const event of HOOK_EVENTS) {
      const entries = Array.isArray(hooks[event]) ? hooks[event] : [];
      const cleaned = entries.filter((e) => !isOurEntry(e));
      cleaned.push({
        hooks: [{ type: 'command', command: hookCommand(), async: true, timeout: 5 }],
      });
      hooks[event] = cleaned;
    }
    userSettings.hooks = hooks;
    fs.writeFileSync(target, JSON.stringify(userSettings, null, 2) + '\n', 'utf-8');
    return { ok: true };
  } catch (err) {
    return { ok: false, error: String(err) };
  }
}

export function uninstallExternalHook(): { ok: boolean; error?: string } {
  try {
    const target = claudeSettingsPath();
    if (!fs.existsSync(target)) return { ok: true };
    let userSettings: Record<string, unknown>;
    try {
      userSettings = JSON.parse(fs.readFileSync(target, 'utf-8')) as Record<string, unknown>;
    } catch {
      return { ok: false, error: '~/.claude/settings.json is not valid JSON — not touching it' };
    }
    const hooks = (userSettings.hooks && typeof userSettings.hooks === 'object')
      ? userSettings.hooks as Record<string, unknown[]> : null;
    if (hooks) {
      for (const event of Object.keys(hooks)) {
        if (!Array.isArray(hooks[event])) continue;
        hooks[event] = hooks[event].filter((e) => !isOurEntry(e));
        if (hooks[event].length === 0) delete hooks[event];
      }
      if (Object.keys(hooks).length === 0) delete userSettings.hooks;
      else userSettings.hooks = hooks;
    }
    fs.writeFileSync(target, JSON.stringify(userSettings, null, 2) + '\n', 'utf-8');
    return { ok: true };
  } catch (err) {
    return { ok: false, error: String(err) };
  }
}

export function getSettings(): AppSettings {
  return { ...settings };
}

export function registerSettingsIpc(): void {
  loadSettings();
  // Refresh the hook script on launch when enabled — the script's
  // content evolves with the app; the settings entry path is stable.
  if (settings.externalHook) {
    const res = installExternalHook();
    if (!res.ok) console.error('[app-settings] hook refresh failed:', res.error);
  }

  ipcMain.handle('settings:get', () => getSettings());

  ipcMain.handle(
    'settings:set',
    (_evt, patch: Partial<AppSettings>): { ok: boolean; error?: string; settings: AppSettings } => {
      if (patch && typeof patch === 'object' && 'externalHook' in patch) {
        const want = patch.externalHook === true;
        if (want !== settings.externalHook) {
          const res = want ? installExternalHook() : uninstallExternalHook();
          if (!res.ok) return { ok: false, error: res.error, settings: getSettings() };
          settings.externalHook = want;
          persistSettings();
        }
      }
      return { ok: true, settings: getSettings() };
    },
  );
}
