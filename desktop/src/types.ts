// Shared TypeScript types used across main, preload, and renderer.

export interface Workspace {
  /** SHA-1 of the absolute repo path; stable across rescans. */
  id: string;
  /** Absolute path to the repo root (the directory containing SNAPSHOT.yaml). */
  root: string;
  /** Auto-derived name — from SNAPSHOT.yaml `project.name`, fallback to dirname. */
  name: string;
  /** ISO timestamp of last open, or null if never opened. */
  lastOpened: string | null;
  /** True when the user has explicitly added or pinned this workspace. */
  pinned: boolean;
  /**
   * Optional `data:` URI of an auto-probed project icon (favicon /
   * logo / icon.png in the workspace root). Renderer falls back to
   * a colored letter initial when both this and userIcon are unset.
   */
  icon?: string;
  /** User-supplied display name. When set, overrides `name` everywhere. */
  userName?: string;
  /** User-picked icon `data:` URI. When set, takes top priority. */
  userIcon?: string;
  /** Single emoji used as the icon. Lower priority than userIcon. */
  userEmoji?: string;
  /** Hex / hsl colour for the identicon tint. */
  userColor?: string;
}

export interface SidecarReadyPayload {
  workspaceId: string;
  port: number;
  url: string;
}

export interface SidecarFailedPayload {
  workspaceId: string;
  reason: string;
  stderrTail?: string;
}

export interface SidecarExitedPayload {
  workspaceId: string;
  code: number | null;
  signal: NodeJS.Signals | null;
}
