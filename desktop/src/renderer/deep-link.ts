// What a `cockpit://` link asks the window to open, as a pure function
// (ISS-0293), and where a link that names a note's ID lands (REQ-0062).
//
// A link is `cockpit://<project>/<target>`. The project is a project id
// (`your-health`, what a `[[project#ID]]` link names) or the shell's own
// workspace id. The target is optional: a note ID (`FEAT-0107`), located the
// way a cross-repo link is, or a path under `docs/`, opened as it stands.
//
// A note ID that names a design with something to show opens the design
// bench (`~design/<ID>`) instead of the note (`designBenchTarget`, below).
// The project's design register decides that, not the `DES-` prefix.
//
// Split out of renderer.ts so the parsing can be tested without a window,
// the same arrangement as `cache-temperature.ts`. Like that file, this one
// declares no imports and no exports: it is loaded as a plain `<script>`
// before renderer.js, so `parseCockpitLink` and `designBenchTarget` become
// globals. The node suite reads the built file and evaluates it.

interface CockpitLink {
  /** The host as written. Matched case-insensitively against both ids. */
  project: string;
  target:
    | { kind: 'none' }
    | { kind: 'note'; id: string }
    | { kind: 'path'; rel: string };
}

/** Null for anything that is not a well-formed cockpit link, and for a path
 *  with a `.` or `..` segment in it.
 *
 *  Parsed by hand, not with `URL`. The renderer's Chromium 128 reads no host
 *  from a URL whose scheme is not a web one: `new URL('cockpit://your-health/x')`
 *  gives an empty `host` and a `pathname` of `//your-health/x`. Node's `URL`
 *  gets it right, so a parser built on `URL` passed its node tests and returned
 *  null for every link in the window (ISS-0293). The handler this replaced read
 *  `u.host` the same way, so it had never switched a project either. */
function parseCockpitLink(url: string): CockpitLink | null {
  const scheme = 'cockpit://';
  if (typeof url !== 'string' || url.slice(0, scheme.length).toLowerCase() !== scheme) {
    return null;
  }
  let rest = url.slice(scheme.length);
  const query = rest.indexOf('?');
  const hash = rest.indexOf('#');
  // A fragment is kept and handed on: the doc pane scrolls to it.
  const fragment = hash >= 0 ? rest.slice(hash) : '';
  const cut = [query, hash].filter((i) => i >= 0);
  if (cut.length) rest = rest.slice(0, Math.min(...cut));
  const slash = rest.indexOf('/');
  const project = slash < 0 ? rest : rest.slice(0, slash);
  if (!project) return null;
  let path: string;
  try { path = decodeURIComponent(slash < 0 ? '' : rest.slice(slash + 1)); } catch { return null; }
  path = path.replace(/^\/+/, '').replace(/\/+$/, '');
  if (!path) return { project, target: { kind: 'none' } };
  if (/^[A-Za-z]+-\d+$/.test(path)) {
    return { project, target: { kind: 'note', id: path.toUpperCase() } };
  }
  if (path.split('/').some((segment) => segment === '..' || segment === '.')) return null;
  return { project, target: { kind: 'path', rel: path + fragment } };
}

/** The three fields of a design register entry (`GET /api/cockpit/designs`)
 *  the rule reads. The renderer's full `DesignRecord` lives in renderer.ts and
 *  is not visible to a plain script. */
interface DesignBenchEntry {
  id: string;
  asset?: string;
  variants?: ReadonlyArray<unknown>;
}

/** Where a link that names `noteId` should land, when that ID is a design
 *  (REQ-0062). `~design/<ID>`, spelled as the register spells it, when the
 *  design declares an `asset:` or at least one variant. Null otherwise, and
 *  null means "locate the note and open it, as before".
 *
 *  The register decides, not the `DES-` prefix. It lists the notes whose type
 *  is `[[design]]`, and it is the only source that also says whether the bench
 *  has anything to show. A design with neither asset nor variants would show
 *  "nothing to render" and a button back to the note, so it opens the note.
 *
 *  `asset`, not `has_asset`: the register sets `has_asset` only when the file
 *  exists. A declared asset whose file is missing still opens the bench,
 *  because the bench's "Artifact not found" message is how the tool reports
 *  a broken path. */
function designBenchTarget(
  noteId: string,
  designs: ReadonlyArray<DesignBenchEntry>,
): string | null {
  if (typeof noteId !== 'string' || !noteId || !Array.isArray(designs)) return null;
  const wanted = noteId.toUpperCase();
  const design = designs.find((d) =>
    d && typeof d.id === 'string' && d.id.toUpperCase() === wanted);
  if (!design) return null;
  const hasAsset = typeof design.asset === 'string' && design.asset.trim() !== '';
  const hasVariants = Array.isArray(design.variants) && design.variants.length > 0;
  return hasAsset || hasVariants ? `~design/${design.id}` : null;
}
