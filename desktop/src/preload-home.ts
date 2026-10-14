// Preload for the draft home window (FEAT-0160).
//
// Deliberately its own file and deliberately small. The present window's
// preload exposes every write path the shell has; this window performs no
// act, so it is given three read calls and one "open that in the present
// window" call, and nothing else.

import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('cockpitHome', {
  /** What is owed, the phases and the release, per project. */
  data: (): Promise<unknown> => ipcRenderer.invoke('home:data'),
  /** One row per project with its agent's state (the ~agents payload). */
  fleet: (): Promise<unknown> => ipcRenderer.invoke('agents:fleet'),
  /** Open a note, or a project when `target` is empty, in the present window. */
  open: (target: { projectId: string; target: string }): Promise<boolean> =>
    ipcRenderer.invoke('home:open', target),
});
