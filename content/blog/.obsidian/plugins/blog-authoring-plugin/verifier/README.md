# Vendored Verification Engine

This directory holds a **frozen, self-contained copy of the blog's real static-site generator**, used by
the plugin's publish gate to verify a post offline before committing/pushing. It is **data**, not plugin
source — the plugin never imports it; it shells out to it (see `src/verify/gate.ts`).

## Provenance

Extracted **verbatim** (copy-only, never edited) from the read-only website copy at
`site/personal site/` on 2026-06-29. The website copy is an extraction source only and is never modified,
built in place, or required at runtime (Constitution: Private-Only / Deterministic & Dependency-Light;
spec FR-022).

## Layout (`engine/`) — mirrors the real repo exactly

The generator computes its repo root as `scripts/blog/config.py → parents[2]`, so the engine MUST sit at
the root of a mini-repo with this shape:

```
engine/
  scripts/{build_blog.py, verify_build.py, blog/*.py}      # the generator
  templates/blog/{*.html, partials/*, assets/{blog.css,blog.js,fonts/*}}
  content/blog/{categories.yml, <3 sample posts>.md, README.md, assets/}
  assets/portfolio-fonts/index.baseline.html               # font-fidelity baseline (verifier reads it)
  index.html, llms.txt                                     # tolerated companions (portfolio comparison)
  robots.txt, site.webmanifest, favicon.ico, favicon.svg,  # ROOT_REQUIRED companions
  apple-touch-icon.png, icon-192.png, icon-512.png, og-image.png
  tests/                                                   # the generator's unittest suite (integrity proof)
  requirements.txt                                         # PyYAML==6.0.1 (only third-party dep)
```

The full set is included (incl. `index.html` + the font baseline) so the verifier's portfolio-comparison,
font-fidelity, dangling-link, identity, and feature-004 fixture checks **run** (not skip) — making a green
gate maximally predictive of the site's CI.

## Proven green offline (2026-06-29)

```bash
cd verifier/engine
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests        # 103 tests OK
PYTHONDONTWRITEBYTECODE=1 python3 scripts/build_blog.py  --out /tmp/eng_site
PYTHONDONTWRITEBYTECODE=1 python3 scripts/verify_build.py --out /tmp/eng_site
# → verify_build: 318 checks, 0 failure(s) ; exit 0 ; output byte-identical on repeat (deterministic)
```

Requires Python 3.12.x + `PyYAML==6.0.1` (matches the site's CI 3.12.7). No network access is used.

## How the publish gate uses it

`src/verify/gate.ts` does **not** run the engine in place. Per Publish/Verify it:
1. Creates an ephemeral OS-temp sandbox.
2. Copies the frozen engine's static parts (`scripts/`, `templates/`, root companions, `index.html`,
   `llms.txt`, `assets/portfolio-fonts/`, `tests/`, `requirements.txt`) into the sandbox.
3. Copies the **live** content folder (all posts + `categories.yml` + `assets/`) into `sandbox/content/blog/`
   — so cross-post invariants are checked against the true post universe (CI parity).
4. Runs `python scripts/build_blog.py --out _site` then `python scripts/verify_build.py --out _site`.
5. Parses the result; commits/pushes only on a green (exit 0) build **and** verify.

This keeps the engine frozen/offline while validating real content, and mutates neither the vault nor this
vendored tree.

## Re-vendoring (when the site's generator changes)

Re-run the copy from `site/personal site/` (scripts, templates, content, the ROOT_REQUIRED companions,
`index.html`, `llms.txt`, `assets/portfolio-fonts/index.baseline.html`, `requirements.txt`, `tests/`),
then re-run the proof above and confirm `0 failure(s)`. Exclude `__pycache__`. Do not edit the source.
