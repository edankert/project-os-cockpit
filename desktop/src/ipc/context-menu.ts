// Native text context menu (FEAT-0037 / TASK-0166 + TASK-0168).
//
// Electron ships no default text menu, so right-click is dead in inputs
// and text unless we build one. A single webContents "context-menu"
// handler covers everywhere: role-based Cut/Copy/Paste/Select All when
// the target is editable, and Copy + doc extras when there's a plain
// selection. Non-editable, no-selection right-clicks (nav rows, cards,
// the terminal) yield no items here, so the renderer's own menus keep
// priority uncontested.

import { BrowserWindow, Menu, clipboard } from 'electron';
import type { MenuItemConstructorOptions } from 'electron';

export function attachContextMenu(win: BrowserWindow): void {
  win.webContents.on('context-menu', (_e, params) => {
    const items: MenuItemConstructorOptions[] = [];

    // Spellcheck suggestions (macOS gives these for free on editable text).
    if (params.misspelledWord && params.dictionarySuggestions.length > 0) {
      for (const s of params.dictionarySuggestions.slice(0, 5)) {
        items.push({ label: s, click: () => win.webContents.replaceMisspelling(s) });
      }
      items.push({ type: 'separator' });
    }

    if (params.isEditable) {
      items.push(
        { role: 'cut', enabled: params.editFlags.canCut },
        { role: 'copy', enabled: params.editFlags.canCopy },
        { role: 'paste', enabled: params.editFlags.canPaste },
        { type: 'separator' },
        { role: 'selectAll' },
      );
    } else if (params.selectionText && params.selectionText.trim()) {
      const sel = params.selectionText;
      items.push({ role: 'copy' });
      items.push({
        label: 'Copy as Markdown quote',
        click: () => clipboard.writeText(sel.split('\n').map((l) => `> ${l}`).join('\n')),
      });
      items.push({ type: 'separator' });
      // Doc-pane glue (TASK-0168): send the selection to the renderer to
      // dispatch as an agent prompt for the current note.
      items.push({
        label: 'Dispatch selection as prompt…',
        click: () => win.webContents.send('menu:dispatch-selection', sel),
      });
      items.push({ type: 'separator' });
      items.push({ role: 'selectAll' });
    }

    if (items.length > 0) {
      Menu.buildFromTemplate(items).popup({ window: win });
    }
  });
}
