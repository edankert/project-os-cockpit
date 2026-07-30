// One clipboard path (FEAT-0054 / TASK-0261).
//
// The renderer used `navigator.clipboard` for the terminal and Electron
// menu *roles* for the doc pane — two stacks with different constraints,
// which is why one worked and the other did not:
//
//   navigator.clipboard.writeText  throws NotAllowedError unless the
//                                  document is focused
//   navigator.clipboard.readText   additionally needs the clipboard-read
//                                  permission
//   Electron's main-process module needs neither
//
// Every failure reported in the FEAT-0054 review traced to one of those
// two constraints or to a bare `catch`. Routing through main removes the
// class rather than the instances.
//
// Both handlers return a result rather than throwing: the renderer's job
// is to TELL THE USER when a copy did not happen, and it cannot do that
// if the failure arrives as a rejected promise nobody awaited.

import { clipboard, ipcMain } from 'electron';

export interface ClipboardResult {
  ok: boolean;
  text?: string;
  error?: string;
}

export function registerClipboardIpc(): void {
  ipcMain.handle('clipboard:write', (_evt, text: unknown): ClipboardResult => {
    if (typeof text !== 'string') {
      return { ok: false, error: 'nothing to copy' };
    }
    try {
      clipboard.writeText(text);
      // Read back rather than trusting the write. A silent no-op is the
      // failure mode this whole task exists to remove, and on macOS a
      // clipboard owned by another process can reject a write without
      // raising.
      return clipboard.readText() === text
        ? { ok: true }
        : { ok: false, error: 'the clipboard did not accept the text' };
    } catch (err) {
      return { ok: false, error: String(err) };
    }
  });

  ipcMain.handle('clipboard:read', (): ClipboardResult => {
    try {
      return { ok: true, text: clipboard.readText() };
    } catch (err) {
      return { ok: false, error: String(err) };
    }
  });
}
