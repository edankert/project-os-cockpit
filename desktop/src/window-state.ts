// Tiny window-state persistence (TASK-0064).
//
// Saves `{x, y, width, height}` to `app.getPath('userData')/window-state.json`
// on close, restores on launch. App-wide (one window state across
// workspaces) — per-workspace persistence is a follow-up if it turns
// out to matter in practice.

import { BrowserWindow, app } from 'electron';
import * as fs from 'node:fs';
import * as path from 'node:path';

interface WindowState {
  x?: number;
  y?: number;
  width: number;
  height: number;
}

const DEFAULTS: WindowState = { width: 1400, height: 900 };

function storePath(): string {
  return path.join(app.getPath('userData'), 'window-state.json');
}

export function loadWindowState(): WindowState {
  try {
    const raw = fs.readFileSync(storePath(), 'utf-8');
    const data = JSON.parse(raw) as Partial<WindowState>;
    return {
      x: typeof data.x === 'number' ? data.x : undefined,
      y: typeof data.y === 'number' ? data.y : undefined,
      width: typeof data.width === 'number' && data.width >= 600 ? data.width : DEFAULTS.width,
      height: typeof data.height === 'number' && data.height >= 400 ? data.height : DEFAULTS.height,
    };
  } catch {
    return DEFAULTS;
  }
}

export function attachWindowStatePersistence(window: BrowserWindow): void {
  const save = (): void => {
    if (window.isDestroyed()) return;
    if (window.isMinimized() || window.isFullScreen()) return;
    const bounds = window.getBounds();
    try {
      fs.mkdirSync(path.dirname(storePath()), { recursive: true });
      fs.writeFileSync(
        storePath(),
        JSON.stringify(bounds, null, 2),
        'utf-8',
      );
    } catch {
      /* best-effort */
    }
  };
  // Debounce — close emits after the last resize.
  let timer: NodeJS.Timeout | null = null;
  const schedule = (): void => {
    if (timer) clearTimeout(timer);
    timer = setTimeout(save, 250);
  };
  window.on('resize', schedule);
  window.on('move', schedule);
  window.on('close', save);
}
