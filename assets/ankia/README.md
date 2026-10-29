# Blog static assets

`wenkai-1.7.0/` contains the unmodified LXGW WenKai Screen font CSS and the
97 WOFF2 subsets referenced by that CSS. Other font families in the package
are omitted. The font files are covered by the included OFL.txt; packaging
code is covered by LICENSE.

Source: https://github.com/chawyehsu/lxgw-wenkai-webfont

NPM tarball: https://registry.npmjs.org/lxgw-wenkai-screen-webfont/-/lxgw-wenkai-screen-webfont-1.7.0.tgz

NPM SHA-512 integrity:
`sha512-xvfF4V26Mb335xKg3uxljz+V2nq4F5ek0ku9pmyKgT0Dzo/d2rHi7WpnqgvM9mlXAcAKOrxrcDmUZiIs/ZQ9bQ==`

The CSS and fonts match the CDN version previously used by this blog byte for
byte. Files are self-hosted to remove the separate font CDN connection; this
does not reduce the number of Unicode subsets needed for a given page.

`background/313f0dfb2e700195.webp` is the blog's existing 2000×1000 background,
converted to WebP quality 82 without resizing. The original remains in Trilium.
Its original SHA-256 is recorded in `deploy/static-assets.json`; the output's
SHA-256 prefix is in the filename. No original image or user avatar is replaced.

The manifest records checksums for every deployed file. Do not mutate a
published versioned URL: publish a new version/digest and update the attributes.
