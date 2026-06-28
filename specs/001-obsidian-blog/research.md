# Phase 0 Research: Obsidian-Vault-Driven Blog

All decisions below resolve the Technical Context and the spec's Clarifications. No
`NEEDS CLARIFICATION` markers remain.

## R1. Design source format — what we are extracting

**Finding**: `Ehsan Koolivand - Blog.html` is a self-unpacking "dc-runtime" bundle (the same
family as the portfolio `index.html`). It contains:

- A `<script type="__bundler/manifest">` (base64+gzip assets: one 58 KB JS runtime + 15 woff2
  fonts) and a `<script type="__bundler/template">` (a JSON-encoded HTML string).
- The decoded template is an `<x-dc>` element holding the **entire blog design as static markup
  with inline styles**, plus two `<style>` blocks (21 KB CSS: 54 `@font-face`, 18 `@keyframes`,
  media queries) and a `<script type="text/x-dc" data-dc-script>` carrying the design's own
  interaction logic and demo `POSTS` data.
- The design declares **two views** via `<sc-if value="{{ isIndex }}">` and
  `<sc-if value="{{ isArticle }}">`, with `<sc-for>` loops and `{{ }}` interpolation.

**Decision**: Extract the design **once** into clean committed files: `templates/blog/base.html`
(head + shell + `{{MAIN}}`), `templates/blog/index.html` (index `<main>`), and
`templates/blog/article.html` (article `<main>`), preserving all inline styles verbatim;
`templates/blog/assets/blog.css` (the two `<style>` blocks merged); the 15 fonts to
`templates/blog/assets/fonts/`; and a hand-ported `templates/blog/assets/blog.js`.

**Rationale**: Parsing the live bundle at every build is fragile (it is a runtime artifact).
Extracting to clean templates makes the design the committed source of truth, the build
deterministic, and Principle III auditable.

**Alternatives considered**: (a) Run the React bundle headless and snapshot the DOM at build
time — rejected: requires a browser engine in CI, is non-deterministic, and re-introduces the
client-render coupling we are removing. (b) Re-implement the design from scratch — rejected:
violates Principle III (design fidelity) and risks drift.

## R2. Generator language & dependencies

**Decision**: Python 3.11+ with `PyYAML` (frontmatter) pinned in `requirements.txt`; Markdown
rendered by an **in-house, stdlib-only** module keyed to the design's fixed block vocabulary;
standard library for everything else.

**Rationale**: Python 3 is pre-installed on `ubuntu-latest`. The design supports a *closed* set
of block types (paragraph, heading, code+caption, quote, list, image) and a small inline set
(bold, italic, inline code, links). A focused in-house renderer maps Markdown directly to the
design's exact block HTML, gives full control over escaping, is fully deterministic, and removes
all Markdown-library version fragility (the available `mistune` is 2.0.4, whose AST API differs
from 3.x). Net dependency surface: PyYAML only.

**Alternatives considered**: `mistune` 3.x AST — rejected during implementation because the
runner ships 2.0.4 with an incompatible AST API, adding version risk for no benefit given the
closed block vocabulary. Node/Eleventy/Astro — heavier toolchains whose default templating would
fight the bundle-derived inline-style design.

## R3. Markdown → design block mapping

The design article body supports exactly these block types (from the `<sc-for current.blocks>`
loop): paragraph (`p`), section heading (`h2`), code-with-caption (`code`), blockquote
(`quote`), list (`list`), image/figure (`img`). Mapping from the parsed Markdown blocks:

| Markdown | Design block | Notes |
|----------|--------------|-------|
| paragraph | `p` | inline rendering (em/strong/links/code spans) preserved; styled span for the design |
| heading (any level in body) | `h2` | body uses a single visual heading level; the post title is the page `<h1>` |
| fenced code block | `code` | **caption = the fence info string** (e.g. ```` ```// wallet-topup.feature.yaml ````); no syntax highlighting (per Clarification) |
| blockquote | `quote` | left-accent rule style |
| list (ul/ol) | `list` | each item rendered with the design's bullet marker |
| image `![alt](src)` | `img` | a real `<img>` (with width/height + alt) placed inside the design's image-block container; `alt` doubles as caption |
| thematic break / other | mapped to nearest supported block or paragraph | keeps output within the design vocabulary |

**Decision**: Implement an in-house, stdlib-only block mapper (`scripts/blog/markdown_render.py`)
that scans the Markdown line-by-line and emits the design block HTML directly, escaping all
text/attributes — consistent with R2 (no Markdown library). **Rationale**: full control + design
fidelity + correct escaping + determinism, with PyYAML as the only dependency.
**Alternatives**: a `mistune`/Python-Markdown AST walker — rejected (see R2) because the runner's
`mistune` is 2.0.4 with an incompatible AST API, adding version risk for no benefit given the
closed block vocabulary.

## R4. Cover handling (code-style vs image) — per Clarification

**Decision**: `cover.type: code` (default) renders the design's code-card cover from
`cover.glyph` + `cover.caption`. `cover.type: image` renders a real `<img>` (copied to
`/blog/assets/media/`) with explicit `width`/`height` + `alt` inside the cover slot, and is
used for OG/Twitter/JSON-LD `image`. When no image cover exists, OG/JSON-LD `image` falls back
to the site `og-image.png`. **Rationale**: matches the design default while supporting real
cover images without layout shift (Principle VI) and giving social/structured data an image.

## R5. Slug, permalink & dates — per Clarification

**Decision**: `slug = frontmatter.slug || kebab-case(title)`; permalink `/blog/<slug>/`
(clean URL via `<slug>/index.html`); duplicate slugs are a hard build error. `date` →
`datePublished`; `updated` → `dateModified` (falls back to `date`); sitemap `lastmod =
updated || date`. **Rationale**: stable, human-readable URLs decoupled from title edits;
unambiguous, reviewable date semantics.

## R6. Read time

**Decision**: Use frontmatter `readTime` verbatim when present; otherwise compute
`ceil(words / 220)` minutes from the rendered body text (min 1), formatted `"N min"` to match
the design. **Rationale**: 200–230 wpm is the standard reading-speed range; deterministic.

## R7. Related "More notes" resolution — per spec US3

**Decision**: Scan the **tail** of the post body for links — Obsidian wikilinks `[[slug]]` /
`[[slug|label]]` and markdown links to `/blog/<slug>/` or `<slug>.md`. Resolve each against the
post set by slug (and by title as a fallback). Render resolved targets as the design's
more-notes cards in author order. Unresolved links emit a build **warning** (not a broken card).
With no links, the section is omitted with valid markup. **Rationale**: matches the authoring
flow ("link a few posts at the bottom") and Principle I (real anchors), failing loud not silent.

## R8. Category source — per Clarification

**Decision**: `content/blog/categories.yml` is an ordered list of `{ name, label }`. The index
nav renders "All" first, then each category in file order using its label; post chips and
`articleSection` use the category's label; a post whose `category` is not in the set is a build
error. **Rationale**: single author-owned declaration drives nav, chips, and metadata
(Principle IV); ordering and labels are data, not code.

## R9. Category filtering as progressive enhancement — per spec US2/FR-009

**Decision**: All cards render in static HTML as real `<a>` links carrying a `data-cat`
attribute. `blog.js` toggles visibility on category click (and reflects the active chip),
mirroring the bundle's filter behavior, with no effect on crawlability. **Rationale**: links
exist without JS (Principle I); filtering is pure enhancement.

## R10. Interactions ported to vanilla JS

The bundle's `data-dc-script` drives, via `data-*` hooks, all interactions: ink ripple
(`[data-ripple]`), magnetic cursor, scroll reveals (`[data-reveal]`), magnetic pull
(`[data-magnetic]`) + card hover (`[data-card]`), category active state (`[data-cat]`),
reading-progress bar, the scroll-reactor companion (`[data-reactor]`), the "Bit" companion
(`[data-companion]`), and the logo party easter egg (`[data-logo]`). All operate on the DOM and
honor `prefers-reduced-motion`/touch.

**Decision**: Port these behaviors to a standalone, dependency-free `blog.js` (no React) that
runs on `DOMContentLoaded` against the static DOM; replace SPA `setState` view-switching with
real page navigation (cards are `<a href>`) and replace `setFilter` with show/hide filtering.
**Rationale**: preserves the exact look/feel (Principle III) while keeping JS strictly
enhancement (Principle I) and removing the React runtime + content rendering.

## R11. Fonts

**Decision**: Self-host the 15 extracted woff2 under `/blog/assets/fonts/`; rewrite the
`@font-face` `src` URLs in `blog.css` from bundle UUIDs to those paths; keep `font-display: swap`.
**Rationale**: no external/Google-Fonts request (privacy, CWV, offline-faithful), exact design
typography (JetBrains Mono, Manrope, Space Grotesk).

## R12. Deployment model

**Decision**: Build in GitHub Actions and deploy with the official Pages actions
(`actions/configure-pages`, `actions/upload-pages-artifact`, `actions/deploy-pages`). The
workflow runs `build_blog.py` to assemble `_site/` (portfolio + root companions copied verbatim,
blog generated, sitemap regenerated, `.nojekyll` present) then deploys that artifact. Generated
output is **not** committed.

**Manual one-time step (owner)**: set repo Settings → Pages → Source = "GitHub Actions".

**Rationale**: the modern, recommended Pages flow; keeps generated HTML out of git (Principle
IV); a single artifact guarantees one consistent absolute URL and that the portfolio ships
unchanged. **Alternatives**: "deploy from branch" with committed `/blog/` output + CI commit-back
— rejected: commits generated artifacts (violates Principle IV) and CI write-back is fragile.

## R13. Sitemap strategy

**Decision**: Regenerate `sitemap.xml` in `_site/` from a known URL set: homepage `/`, blog
index `/blog/`, and each non-draft post `/blog/<slug>/` with `lastmod = updated || date`. The
committed root `sitemap.xml` remains as the branch-deploy fallback; the artifact's regenerated
sitemap is authoritative. **Rationale**: every post must appear with a correct `lastmod`
(FR-019) and the homepage must remain listed (reuse existing infra, FR-020).

## R14. Identity consistency

**Decision**: Author identity is "Ehsan Kolivand", Senior Android Engineer, Istanbul — matching
the deployed portfolio and SEO files (the design bundle's placeholder "Koolivand" is corrected).
One absolute base URL `https://ehsankolivand.github.io/` everywhere. **Rationale**: Principle V
(consistent identity + single absolute URL); this changes data/content, not the visual design.

## R15. Validation / Definition of Done

**Decision**: `verify_build.py` asserts, on the generated `_site/`: every post page contains its
title (single `<h1>`), body text, category, date, read time, canonical, OG, Twitter, and valid
Article/BlogPosting JSON-LD; the index lists every published post as a real anchor; the sitemap
lists every published post; no unresolved `{{ }}`/`sc-if`/`sc-for` tokens remain; and
`_site/index.html` is byte-identical to the repo `index.html` outside the managed "Field notes"
region (the `<!--LATEST-NOTES:*-->` markers, which the build regenerates). **Rationale**: turns the success
criteria into an automated gate (Principle I/V/VII) runnable locally and in CI.
