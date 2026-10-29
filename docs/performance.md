# Performance and deployment

## Theme behavior

- Cover cards reserve image dimensions, decode asynchronously and lazily load
  images after the first two cards. Failed covers collapse instead of leaving
  broken image placeholders.
- Prism resources load only on pages containing a `pre` block.
- Twikoo loads with `defer`; its callers wait for `DOMContentLoaded`. Pages
  without `showComments` do not initialize a hidden comment form. Latest
  comments remain independent and hide their panel on an empty result or error.
- The font stylesheet directly loads the LXGW WenKai Screen family used by the
  theme, avoiding the umbrella stylesheet and its unused Screen R family.
- `bloggerAvatarUrl` optionally overrides the original avatar. Use a small
  optimized image; image dimensions in HTML alone do not reduce download size.

The template also includes compact cards, a collapsible mobile article index,
anchor scroll offsets, and wrapping article metadata and inline code.

## Release order

1. Modify and validate source files in this repository.
2. Commit and push the source and any deployment configuration to GitHub.
3. Back up the corresponding live Trilium notes or server configuration.
4. Apply the exact committed version to Trilium or the server.
5. Check the homepage, mobile article navigation, a code article and an enabled
   comment form. Check network failures and browser errors.

`src/Ankia-Theme.ejs` maps to the live `shareTemplate` note. CSS and JavaScript
changes also need their source/minified files and the respective Trilium
`shareCss`/`shareJs` notes synchronized. Do not overwrite the whole blog or
import a full theme archive merely to update the template.

Avatar URLs/data URIs, service endpoints and other site-specific values stay
in Trilium attributes rather than being hard-coded into the shared template.
Remove `bloggerAvatarUrl` to restore the original avatar relation.

## Server-side caching

HTML compression and browser resource caching are separate optimizations.
If the reverse proxy returns `no-store` for theme CSS/JS, template changes
cannot override that header. Before deploying cache rules, verify the real
public sharing routes and use an explicit asset allowlist. Never cache all
Trilium `/api/*` routes or authenticated responses. Mutable asset URLs need a
short TTL or a tested versioning/invalidation mechanism, not an unconditional
one-year immutable policy.

### This blog's Caddy rule

`deploy/caddy/theme-assets.caddy` allowlists the four public theme/Prism download
IDs for this installation, including the `/share`-prefixed paths used by the
proxy rewrite. Anonymous GET/HEAD responses with status 200 and CSS/JavaScript
content types receive `Cache-Control: private, max-age=300`. Requests carrying
Cookie or Authorization, other notes/APIs, HTML and error responses keep their
existing policy. This enables browser caching, not a shared proxy cache.
Theme edits may take up to five minutes to appear on a returning visitor's
browser; use a forced reload to check an immediate deployment.

### Poto responsive covers

After verifying the Poto `?w=160`, `?w=320` and `?w=640` endpoints, set
`#potoThumbnailOrigin = https://poto.tsaitang.workers.dev` on the blog root.
The theme then uses these variants for raster cover URLs under that exact
origin's `/files/` path. `sizes` matches the CSS: 88px up to 600px viewport
width, 144px otherwise. The browser chooses a variant for its pixel density.
Existing lazy/eager loading and reserved layout dimensions remain in effect.

Other origins, SVG files and URLs with existing query strings/fragments are
left unchanged. A network/decode error retries the original cover once, then
collapses the image box if that also fails. Poto's own successful original-image
fallback continues to work. Remove the label to disable thumbnail requests;
the original article `headerImage` values are never rewritten.

### Same-origin font and background assets

The optional blog-root attributes `fontStylesheetUrl` and
`homepageBackgroundUrl` select optimized assets without changing the original
Trilium relations. If absent, the existing font CDN and background relation
continue to work. Background images decode asynchronously and use low fetch
priority so they do not compete with foreground covers and stylesheets.

The current release's URLs and checksums are in `deploy/static-assets.json`.
After committing and pushing the release, stage the repository on the Caddy
host. Validate first, then apply:

```sh
sudo python3 deploy/caddy/install-static-assets.py
sudo python3 deploy/caddy/install-static-assets.py --apply
```

The installer verifies asset checksums, refuses to replace different bytes at
an immutable URL, installs only manifest files under `/var/www/ankia-assets`,
and adds a public `/assets/ankia/*` file route excluded from `/share` rewrites.
Only successful static responses receive a one-year immutable browser cache.
Other routes retain their previous behavior. The complete Caddyfile is backed
up before reload and restored if reload fails.

Verify the font CSS, a referenced WOFF2 and background URL before setting the
two attributes to the manifest's URLs. This order prevents broken asset links.
To roll back, remove the attribute overrides before restoring the Caddyfile.
The font bytes are unchanged, including Unicode ranges and `font-display: swap`.
The old background is preserved, while the WebP keeps its 2000×1000 dimensions.

After committing and pushing these files, stage the exact committed files on
the Caddy host in the same directory. Validate without changing live config:

```sh
sudo python3 deploy/caddy/apply-theme-cache.py
```

Then apply that same version:

```sh
sudo python3 deploy/caddy/apply-theme-cache.py --apply
```

The script backs up the complete Caddyfile, preserves other sites and reloads
Caddy. A failed reload restores the previous file and reloads it. It refuses
to overwrite an existing managed block; inspect and review subsequent updates.
The rule is site-specific: replace the host and asset IDs when deploying it
elsewhere. Verify headers on CSS, JS, HTML and a non-allowlisted API route,
plus authenticated requests, before declaring the rollout successful.
