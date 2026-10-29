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
