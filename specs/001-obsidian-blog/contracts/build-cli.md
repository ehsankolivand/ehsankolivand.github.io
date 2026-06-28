# Contract: Build & Verify CLI

## `scripts/build_blog.py`

Deterministic generator. Reads content + templates, writes the full site to an output dir.

```
python scripts/build_blog.py [--out _site] [--base-url https://ehsankolivand.github.io/] [--drafts]
```

| Flag | Default | Meaning |
|------|---------|---------|
| `--out` | `_site` | output directory (assembled, deployable site) |
| `--base-url` | `https://ehsankolivand.github.io/` | absolute site URL used in canonical/OG/sitemap/JSON-LD |
| `--drafts` | off | include `draft: true` posts (local preview only; CI never sets this) |

### Inputs (read-only)

- `content/blog/categories.yml`, `content/blog/*.md`, `content/blog/assets/**`
- `templates/blog/{base,index,article}.html`, `templates/blog/assets/**`
- Repo root companion files (allowlist): `index.html`, `robots.txt`, `site.webmanifest`,
  `llms.txt`, `favicon.ico`, `favicon.svg`, `apple-touch-icon.png`, `icon-192.png`,
  `icon-512.png`, `og-image.png`, `.nojekyll`

### Outputs (written under `--out`)

- `index.html` and the root companion files — **copied verbatim**, then the deployed
  `index.html` has only its managed "Field notes" region (between the `<!--LATEST-NOTES:START-->`
  / `<!--LATEST-NOTES:END-->` markers) deterministically regenerated from the latest posts;
  the portfolio is byte-identical to source everywhere outside that region, and the repo source
  file is never modified.
- `sitemap.xml` — **regenerated** (home `/`, `/blog/`, each published post with `lastmod`).
- `blog/index.html` — the static blog index.
- `blog/<slug>/index.html` — one static page per published post.
- `blog/assets/{blog.css, blog.js, fonts/*, media/*}` — design assets + copied image covers.
- `.nojekyll` present at output root.

### Behavior / exit codes

- `0` success. Non-zero on validation failure with a clear message identifying the file:
  missing required frontmatter, unknown `category`, duplicate `slug`, bad date, missing image
  `alt`. Unresolved related links print a `WARNING:` line but do not fail the build.
- MUST be deterministic: same inputs → byte-identical outputs (stable ordering, no timestamps
  except dates derived from frontmatter).
- MUST NOT write anywhere except `--out`. MUST NOT modify repo source files.

## `scripts/verify_build.py`

Post-build Definition-of-Done gate.

```
python scripts/verify_build.py [--out _site] [--repo-root .]
```

Asserts on the generated site (exit non-zero with a report on any failure):

1. Each published post page contains: its title in exactly one `<h1>`, its rendered body text,
   the category chip, the date, and the read time — in the static HTML.
2. Each post page contains `<title>`, `<meta name="description">`, `<link rel="canonical">`,
   `og:*`, `twitter:*`, and a valid `Article`/`BlogPosting` JSON-LD block (parses as JSON; has
   headline, author, datePublished, articleSection).
3. `blog/index.html` lists every published post as a real `<a href="/blog/<slug>/">`.
4. `sitemap.xml` contains every published post URL and the homepage.
5. No unresolved `{{ }}`, `<sc-if`, or `<sc-for` tokens remain in any output HTML.
6. `out/index.html` is byte-identical to repo-root `index.html` **outside** the managed
   "Field notes" region (the `<!--LATEST-NOTES:*-->` markers); inside that region the latest
   posts and a `/blog/` link are present. (The repo source `index.html` is never modified;
   the verifier strips the managed region before comparing.)
