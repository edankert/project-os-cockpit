// Copy renderer HTML + CSS + third-party UMD bundles into dist/.
//
// tsc only emits JavaScript for our own .ts sources. The renderer needs
// HTML / CSS / xterm.js (UMD) / addon-fit.js (UMD) / xterm.css alongside
// the compiled renderer.js, so this script copies them after tsc finishes.
//
// We use the UMD builds of xterm + addon-fit (not their ES modules)
// because the renderer is loaded as a plain `<script>` rather than an
// ES module — see the explanatory note at the top of renderer.ts.

import { cp, mkdir } from 'node:fs/promises';
import * as path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..');
const repoRoot = path.resolve(root, '..');
const rendererSrc = path.join(root, 'src', 'renderer');
const rendererDst = path.join(root, 'dist', 'renderer');
const nodeModules = path.join(root, 'node_modules');

await mkdir(rendererDst, { recursive: true });

// Our own renderer assets.
for (const file of ['index.html', 'renderer.css']) {
  await cp(path.join(rendererSrc, file), path.join(rendererDst, file));
}

// Cockpit's content + shell CSS — single source of truth in the
// Python package, copied here at build time so the mounted Markdown
// HTML inherits the same styling mode 1 uses. `base.css` holds the
// `--surface`, `--text`, status / severity, font, and metadata-strip
// styles; `cockpit.css` layers cockpit-specific chrome on top.
// (FEAT-0009 may later split this further; for now we ship both.)
const staticDir = path.join(repoRoot, 'src', 'project_os_cockpit', 'static');
for (const file of ['base.css', 'cockpit.css']) {
  await cp(path.join(staticDir, file), path.join(rendererDst, file));
}

// Third-party UMD bundles (loaded via `<script>` tags in index.html).
const vendored = [
  ['@xterm/xterm/lib/xterm.js',         'xterm.js'],
  ['@xterm/xterm/css/xterm.css',        'xterm.css'],
  ['@xterm/addon-fit/lib/addon-fit.js', 'addon-fit.js'],
];
for (const [src, dst] of vendored) {
  await cp(path.join(nodeModules, src), path.join(rendererDst, dst));
}

console.log(`copy-assets: ${rendererSrc} (+ vendored xterm) → ${rendererDst}`);
