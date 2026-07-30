// Native text context menu (FEAT-0037 / TASK-0166 + TASK-0168).
//
// Electron ships no default text menu, so right-click is dead in inputs
// and text unless we build one. A single webContents "context-menu"
// handler covers everywhere: role-based Cut/Copy/Paste/Select All when
// the target is editable, and Copy + doc extras when there's a plain
// selection. Non-editable, no-selection right-clicks (nav rows, cards,
// the terminal) yield no items here, so the renderer's own menus keep
// priority uncontested.

import { BrowserWindow, Menu, clipboard, shell } from 'electron';
import type { MenuItemConstructorOptions } from 'electron';

/** A `/docs/...` link — the renderer owns the menu for these. */
function isDocsLink(url: string): boolean {
  try {
    const u = new URL(url, 'file:///');
    return u.pathname.startsWith('/docs/') && u.pathname.endsWith('.md');
  } catch {
    return false;
  }
}

/** `FEAT-0028` out of `/docs/features/fleet-health/FEAT-0028-Fleet-Health-Surface.md`. */
function idFromLink(url: string): string {
  const name = url.split('/').pop() || '';
  const m = name.match(/^((?:TASK|ISS|FEAT|REQ|PHASE|RISK|CHG|ADR|TST|DES|REL|WF)-[\w-]*?\d+)/i);
  return m ? m[1].toUpperCase() : '';
}

export function attachContextMenu(win: BrowserWindow): void {
  win.webContents.on('context-menu', (_e, params) => {
    const items: MenuItemConstructorOptions[] = [];

    // A right-click on a docs link belongs to the RENDERER's menu
    // (`doc-link`), which already offers Open / Copy ID / Copy path /
    // Copy link plus the agent verbs. Both handlers fire for the same
    // click — `preventDefault()` on the DOM event does not suppress this
    // one — so without yielding here two menus race and this one wins,
    // showing Copy / "Dispatch selection as prompt" for the word
    // Chromium auto-selected under the cursor. That is precisely what
    // FEAT-0054 was reported for: right-clicking a feature link offered
    // to dispatch a word fragment and said nothing about the feature.
    if (params.linkURL && isDocsLink(params.linkURL)) return;

    // A NON-docs link (http/https, or a docs path the renderer declines)
    // gets link actions here, because nothing else offers any.
    if (params.linkURL) {
      const url = params.linkURL;
      const id = idFromLink(url);
      items.push({ label: 'Open link', click: () => { void shell.openExternal(url); } });
      items.push({ label: 'Copy link', click: () => clipboard.writeText(url) });
      if (id) {
        items.push({ label: `Copy ${id}`, click: () => clipboard.writeText(id) });
        items.push({
          label: `Dispatch ${id} as prompt…`,
          click: () => win.webContents.send('menu:dispatch-selection', id),
        });
      }
      if (params.linkText && params.linkText !== url) {
        items.push({ label: 'Copy link text', click: () => clipboard.writeText(params.linkText) });
      }
      items.push({ type: 'separator' });
    }

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
