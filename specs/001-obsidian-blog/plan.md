# Implementation Plan: Obsidian-Vault-Driven Blog

**Branch**: `001-obsidian-blog` | **Date**: 2026-06-27 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-obsidian-blog/spec.md`

## Summary

Add a static blog to the existing GitHub-Pages site. The author writes one Obsidian markdown
note (YAML frontmatter + markdown body, optional related links at the end) and commits it; a
deterministic build-time generator renders that note — and a blog index — into the **existing
blog design**, producing real static HTML (content in the initial markup), per-page SEO/GEO
metadata, and an updated sitemap. The build runs in GitHub Actions on push and deploys the
assembled static site to GitHub Pages. The existing portfolio (`index.html`) and its SEO files
are copied verbatim and never modified.

Technical approach: the existing design (`Ehsan Koolivand - Blog.html`) is a client-rendered
"dc-runtime" bundle (React fills an `<x-dc>` template with `{{ }}`/`<sc-if>`/`<sc-for>`
placeholders). We **extract that design once into committed, clean templates and assets**
(HTML shells + CSS + self-hosted fonts + a vanilla progressive-enhancement script that
reproduces the bundle's interactions), then a small Python generator fills those templates at
build time. This converts the client-only design into SEO-correct static pages with byte-level
visual fidelity.

## Technical Context

**Language/Version**: Python 3.11+ (pre-installed on GitHub Actions `ubuntu-latest`).

**Primary Dependencies**: `PyYAML` (frontmatter) only — pinned in `requirements.txt`.
Markdown is rendered by an in-house, stdlib-only module (`scripts/blog/markdown_render.py`)
keyed to the design's fixed block vocabulary; no Markdown library is used. Everything else
uses the Python standard library (`pathlib`, `html`, `re`, `datetime`, `json`, `xml`,
`unicodedata`, `struct`).

**Storage**: Filesystem only. Source content in `content/blog/`; generated site in `_site/`
(a build artifact, git-ignored). No database.

**Testing**: `scripts/verify_build.py` — a post-build smoke verifier asserting content + SEO
tags are in the static HTML, exactly one `<h1>` per page, no unresolved template tokens, the
sitemap lists every published post, and the portfolio `index.html` is byte-identical to the
repo copy outside the managed "Field notes" region (the `<!--LATEST-NOTES:*-->` markers, which
the build regenerates). (Spec marks unit tests optional; this verification is the
Definition-of-Done gate.)

**Target Platform**: Static web on GitHub Pages; modern browsers; must be fully readable by
non-JavaScript crawlers and AI assistants.

**Project Type**: Static site generator (single project; build tooling + templates + content).

**Performance Goals**: Build completes in a few seconds for tens–hundreds of posts. Pages keep
good Core Web Vitals: CSS + self-hosted fonts only as render-affecting resources, JS deferred
and non-essential, images/covers carry explicit dimensions (no CLS), animations compositor-only
and gated by `prefers-reduced-motion`.

**Constraints**: No backend, database, server runtime, or paid service. Deterministic output
(same content in → same HTML out). Design reproduced exactly (no restyling). Post content and
metadata present in served HTML. Existing portfolio and its SEO work untouched. One absolute
site URL (`https://ehsankolivand.github.io/`).

**Scale/Scope**: Personal blog. Dozens of posts initially; architecture scales to hundreds
without change. Initial categories: Compose, Architecture, Tooling, Crypto (+ All), author-driven.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Principle | How this plan complies | Status |
|---|-----------|------------------------|--------|
| I | SEO-Correct Static Generation | Generator renders full post bodies, titles, excerpts, links, and metadata into static HTML at build time. JS (`blog.js`) is progressive enhancement only (animations, filtering, reading progress); it renders **no** content. Post links and category nav are real `<a>` anchors. | ✅ PASS |
| II | GitHub Pages Only (static, CI, no backend) | Output is static files; build runs in GitHub Actions (`deploy.yml`) and deploys via official Pages actions; `.nojekyll` emitted; only free pure-Python deps. | ✅ PASS |
| III | Design Fidelity | Design extracted verbatim from the bundle into `templates/blog/` (markup + inline styles + `blog.css` + 15 self-hosted woff2 + `blog.js` reproducing every bundle interaction). No new styling invented. | ✅ PASS |
| IV | Obsidian As Single Content Source | Author edits only `content/blog/*.md` (+ `categories.yml`, + images). Generated HTML is never hand-edited and is git-ignored. Category set declared in `content/blog/categories.yml`. Related posts resolved from end-of-post links. | ✅ PASS |
| V | Per-Page SEO/GEO Completeness | Every post page gets title, meta description, canonical, OG, Twitter, and Article/BlogPosting JSON-LD from frontmatter; every post added to a regenerated `sitemap.xml`; existing robots/manifest/favicons reused; one absolute URL; identity = "Ehsan Kolivand". | ✅ PASS |
| VI | Accessibility & Core Web Vitals | One `<h1>` per page; `header`/`nav`/`main` landmarks; mascots `aria-hidden`; real focusable links; explicit media dimensions; compositor-only animations honoring reduced-motion. | ✅ PASS |
| VII | Non-Destructive To Portfolio | Build copies `index.html` and root companion files verbatim into `_site/`; only the deployed `index.html`'s managed "Field notes" region (`<!--LATEST-NOTES:*-->`) is deterministically regenerated, the repo source is never edited; blog lives under `/blog/`; verifier asserts `index.html` is byte-identical outside that region. | ✅ PASS |

**Initial gate: PASS** (no violations). **Post-design re-check (after Phase 1): PASS** — the
data model, contracts, and quickstart introduce no deviation from the principles. Complexity
Tracking is therefore empty.

## Project Structure

### Documentation (this feature)

```text
specs/001-obsidian-blog/
├── plan.md              # This file
├── spec.md              # Feature spec (with Clarifications)
├── research.md          # Phase 0 output (decisions + rationale)
├── data-model.md        # Phase 1 output (entities, fields, validation)
├── quickstart.md        # Phase 1 output (run + validate guide)
├── contracts/           # Phase 1 output
│   ├── frontmatter.schema.md     # Post frontmatter contract
│   ├── categories.schema.md      # categories.yml contract
│   ├── build-cli.md              # Build/verify CLI + I/O contract
│   └── template-contract.md      # Template placeholders <-> data mapping
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 output (/speckit-tasks)
```

### Source Code (repository root)

```text
content/blog/                 # AUTHOR SURFACE (the Obsidian vault content)
├── categories.yml            # ordered canonical category set: [{name,label}]
├── <slug-or-title>.md        # one Obsidian note per post (frontmatter + markdown)
└── assets/                   # author images referenced by posts (![alt](assets/x.png))

templates/blog/               # DESIGN, extracted once from the bundle (source of truth)
├── base.html                 # <head> (SEO slots) + body shell (ambient/cursor/reactor/header/nav) + {{MAIN}} + deferred script
├── index.html                # index <main>: hero, featured, post grid
├── article.html              # article <main>: header, author, cover, body, end, more-notes
└── assets/
    ├── blog.css              # extracted CSS (2 style blocks) with @font-face URLs -> /blog/assets/fonts/
    ├── blog.js               # vanilla progressive enhancement (ports dc-script interactions)
    └── fonts/                # 15 self-hosted woff2 (JetBrains Mono, Manrope, Space Grotesk)

scripts/
├── build_blog.py            # entry point: content + templates -> _site/
├── verify_build.py          # post-build smoke verification (DoD gate)
└── blog/                    # generator modules
    ├── __init__.py
    ├── config.py            # site URL, author identity, paths
    ├── content.py           # load posts + categories; validate frontmatter; slugs; read time
    ├── markdown_render.py   # in-house stdlib renderer -> design body-block HTML
    ├── render.py            # fill base/index/article templates
    ├── seo.py               # title/meta/canonical/OG/Twitter/JSON-LD builders
    └── sitemap.py           # regenerate sitemap.xml (home + index + posts)

.github/workflows/
└── deploy.yml               # build _site/ in CI and deploy to GitHub Pages

requirements.txt             # PyYAML (pinned) — no Markdown library (in-house renderer)
.gitignore                   # add _site/

# Generated build artifact (NOT committed):
_site/
├── index.html               # portfolio, copied verbatim
├── robots.txt site.webmanifest llms.txt favicon* icon* apple-touch-icon.png og-image.png .nojekyll  # copied verbatim
├── sitemap.xml              # REGENERATED (home + /blog/ + each post)
└── blog/
    ├── index.html           # blog index (static)
    ├── assets/{blog.css,blog.js,fonts/*,media/*}
    └── <slug>/index.html    # one static page per post
```

**Structure Decision**: Single-project static-site generator. Three concern boundaries:
(1) `content/blog/` is the only author surface; (2) `templates/blog/` holds the design extracted
verbatim from the bundle; (3) `scripts/` holds the deterministic generator. CI assembles
`_site/` (verbatim portfolio + root companions + generated blog + regenerated sitemap) and
deploys it. Generated output is never committed (Principle IV).

## Complexity Tracking

> No Constitution Check violations — this section is intentionally empty.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none)    | —          | —                                   |
