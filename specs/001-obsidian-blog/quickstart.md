# Quickstart: Obsidian-Vault-Driven Blog

Run and validate the blog pipeline end-to-end. (Implementation details live in `tasks.md` and
the generator modules; this is a run/validate guide.)

## Prerequisites

- Python 3.11+
- `pip install -r requirements.txt` (PyYAML only — Markdown is rendered by an in-house, stdlib-only module)

## Build locally

```bash
# from repo root
pip install -r requirements.txt
python scripts/build_blog.py --out _site
```

Produces a complete, deployable site under `_site/` (portfolio copied verbatim, blog generated,
sitemap regenerated, `.nojekyll` present).

## Preview

```bash
python -m http.server -d _site 8080
# open http://localhost:8080/blog/  and a post at http://localhost:8080/blog/<slug>/
```

## Verify (Definition of Done)

```bash
python scripts/verify_build.py --out _site --repo-root .
```

Expected: exit `0` and a summary confirming, for the generated site:

- every published post page has its title (single `<h1>`), body text, category, date, read time
  in the static HTML;
- every post page has title/description/canonical/OG/Twitter + valid BlogPosting JSON-LD;
- the index lists every published post as a real `<a href>`;
- `sitemap.xml` lists the homepage and every published post;
- no unresolved template tokens remain;
- `_site/index.html` is byte-identical to the repo `index.html` outside the managed
  "Field notes" region (the `<!--LATEST-NOTES:*-->` markers, which the build regenerates).

## Prove the authoring flow (the core scenario)

1. Create `content/blog/hello-world.md` with valid frontmatter (see
   `contracts/frontmatter.schema.md`), a short markdown body, and 1–2 related links at the end.
2. `python scripts/build_blog.py && python scripts/verify_build.py`.
3. Confirm: `_site/blog/hello-world/index.html` exists with content + SEO in the raw HTML; the
   post appears on `_site/blog/index.html`; it is in `_site/sitemap.xml`; and its "More notes"
   shows the linked posts.

## Validate crawler-visibility (Principle I)

```bash
# Content must be present without running JS — grep the raw HTML:
grep -c "<h1" _site/blog/<slug>/index.html         # exactly 1
grep -o 'application/ld+json' _site/blog/<slug>/index.html
python - <<'PY'
import re,sys,pathlib
html=pathlib.Path("_site/blog/<slug>/index.html").read_text()
assert "{{" not in html and "<sc-" not in html, "unresolved template tokens"
print("OK: content + JSON-LD present, no template tokens")
PY
```

## Publish (CI)

Push to `main`. `.github/workflows/deploy.yml` installs deps, runs the build + verify, and
deploys `_site/` to GitHub Pages.

**One-time owner step**: GitHub → repo Settings → Pages → Source = **GitHub Actions**.

## How to publish a post from Obsidian (author loop)

1. In the vault's `content/blog/` folder, create one note; fill the YAML frontmatter
   (`title`, `date`, `category`, `excerpt`, optional `cover`/`tags`/`slug`).
2. Write the body in normal markdown; end with a few `[[wikilinks]]` to related posts.
3. Commit & push. The Action rebuilds: the new post appears on the index, gets its own static
   SEO-complete page in the existing design, lands in the sitemap, and shows its "More notes".
