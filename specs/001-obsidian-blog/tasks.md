---
description: "Task list for Obsidian-Vault-Driven Blog implementation"
---

# Tasks: Obsidian-Vault-Driven Blog

**Input**: Design documents from `specs/001-obsidian-blog/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Unit tests are OPTIONAL (not requested in the spec). The required quality gate is
`scripts/verify_build.py` (the Definition-of-Done verifier), included as a foundational task.

**Organization**: Tasks are grouped by user story. Phase 2 (Foundational) builds the shared
design-extraction + generator engine that all stories depend on.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1–US4 from spec.md; Setup/Foundational/Polish carry no story label
- File paths are repo-relative

## Path Conventions

Single-project static-site generator: `content/blog/` (author surface), `templates/blog/`
(extracted design), `scripts/` (generator), `_site/` (build artifact), `.github/workflows/` (CI).

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project skeleton and dependencies

- [x] T001 Create directory tree: `content/blog/assets/`, `templates/blog/assets/fonts/`, `scripts/blog/`, `.github/workflows/`
- [x] T002 [P] Create `requirements.txt` pinning `PyYAML` (Markdown is rendered in-house, stdlib-only — see research R2)
- [x] T003 [P] Add `_site/` to `.gitignore`
- [x] T004 [P] Create `scripts/blog/__init__.py` and `scripts/blog/config.py` (baseUrl, blogBase, author identity "Ehsan Kolivand", siteName, defaultOgImage, paths) per data-model.md

**Checkpoint**: Skeleton + config exist.

---

## Phase 2: Foundational (Design extraction + generator engine — BLOCKS all stories)

**⚠️ CRITICAL**: No user story can be completed until this phase is done.

### Design extraction (from `Ehsan Koolivand - Blog.html`, verbatim — Principle III)

- [x] T005 Extract the design shell into `templates/blog/base.html`: doctype + `<head>` with SEO slot tokens (`{{HEAD_*}}`), the body shell (ambient background, custom cursor, scroll-reactor, `header` with `Ehsan.kolivand` wordmark + `nav data-topcats`), a `{{MAIN}}` slot, and a deferred `<script src="/blog/assets/blog.js">`. Preserve all inline styles. Remove the dc-runtime script + `data-dc-script`.
- [x] T006 [P] Extract the index `<main>` (hero, featured `sc-if`, grid `sc-for`) into `templates/blog/index.html` with generator tokens, styles verbatim
- [x] T007 [P] Extract the article `<main>` (back link, header, author block, cover, body `sc-for`, end signature, more-notes `sc-for`) into `templates/blog/article.html` with generator tokens, styles verbatim
- [x] T008 [P] Extract the two `<style>` blocks into `templates/blog/assets/blog.css`; rewrite every `@font-face` `src` UUID to `/blog/assets/fonts/<uuid>.woff2`; keep `font-display: swap`
- [x] T009 [P] Extract the 15 woff2 assets into `templates/blog/assets/fonts/` (filenames = bundle UUIDs)
- [x] T010 [P] Port the bundle interactions into a dependency-free `templates/blog/assets/blog.js` (ripple, magnetic cursor, scroll reveals, magnetic pull + card hover, category active-state + show/hide filtering, reading-progress bar, scroll-reactor companion, Bit companion, logo party) honoring `prefers-reduced-motion`/touch; no React; no content rendering

### Generator engine

- [x] T011 Create starter `content/blog/categories.yml` (Compose, Architecture, Tooling, Crypto) per contracts/categories.schema.md
- [x] T012 Implement `scripts/blog/content.py`: parse YAML frontmatter + markdown body, validate required fields, compute slug (`slug||kebab(title)`) with duplicate detection, parse dates (`date`/`updated`), compute read time (R6), load+validate `categories.yml`, enforce `category ∈ categories`
- [x] T013 [P] Implement `scripts/blog/markdown_render.py`: in-house stdlib renderer → design body blocks (p, h2, code+caption-from-info-string, quote, list, img→figure) with full HTML escaping (research R3)
- [x] T014 [P] Implement `scripts/blog/seo.py`: build `<head>` meta (title, description, canonical, OG, Twitter) and BlogPosting/Blog JSON-LD per contracts/template-contract.md
- [x] T015 [P] Implement `scripts/blog/sitemap.py`: regenerate `sitemap.xml` (home `/`, `/blog/`, each published post with `lastmod = updated||date`)
- [x] T016 Implement `scripts/blog/render.py`: load templates, fill `base.html` head+shell, build category nav from categories.yml as real `<a data-cat>` anchors, expose helpers to assemble index and article `<main>` (used by US phases)
- [x] T017 Implement `scripts/build_blog.py`: CLI (`--out`, `--base-url`, `--drafts`), discover posts, copy root companion allowlist verbatim into `_site/`, copy `templates/blog/assets/**` → `_site/blog/assets/`, copy image covers → `_site/blog/assets/media/`, write `.nojekyll`, orchestrate index + post rendering + sitemap; fail loud on validation errors (data-model.md §validation)
- [x] T018 Implement `scripts/verify_build.py` (DoD gate) per contracts/build-cli.md: content+SEO present in static HTML, single `<h1>`, JSON-LD valid, index links + sitemap complete, no template tokens, `_site/index.html` byte-identical to repo `index.html`

**Checkpoint**: `python scripts/build_blog.py` runs and produces `_site/` with the design assets;
engine ready for story-specific rendering.

---

## Phase 3: User Story 1 - Publish a post from one Obsidian note (Priority: P1) 🎯 MVP

**Goal**: One markdown note → one static, SEO-complete post page in the existing design, listed
in the sitemap.

**Independent Test**: Add one valid note, build, and confirm `_site/blog/<slug>/index.html`
contains the title (single `<h1>`), body, category, date, read time, and full SEO tags in the
raw HTML, and that it appears in `_site/sitemap.xml`.

- [x] T019 [US1] Implement article `<main>` assembly in `scripts/blog/render.py`: category chip + date + read time, `<h1>` title, dek/excerpt, author block ("Ehsan Kolivand · Senior Android Engineer · Istanbul"), cover (code glyph+caption OR image `<img>` with width/height+alt), rendered body blocks, end signature
- [x] T020 [US1] Wire per-post SEO into the page head via `seo.py` (title, meta description, canonical, OG `article`, Twitter, BlogPosting JSON-LD with headline/author/datePublished/dateModified/image/articleSection/keywords)
- [x] T021 [US1] Ensure published posts are emitted to `sitemap.xml` and excluded when `draft: true`
- [x] T022 [US1] Author the example post `content/blog/spec-driven-android.md` (real Obsidian note: full frontmatter incl. code cover, markdown body with headings/code/quote/list/image)
- [x] T023 [US1] Build + run `verify_build.py`; confirm the example post page is static, SEO-complete, in the sitemap, and design-faithful

**Checkpoint**: MVP works — an author can publish a post; it is a real static SEO page.

---

## Phase 4: User Story 2 - Browse and filter the index by category (Priority: P2)

**Goal**: A blog index with a featured post + grid (cover, category, title, excerpt, date, read
time), crawlable links, and category filtering as progressive enhancement.

**Independent Test**: With several posts across categories, build and confirm the index's raw
HTML lists every published post as a real `<a href>`, shows featured + grid, and that selecting a
category narrows visible cards while "All" restores them.

- [x] T024 [US2] Implement index `<main>` assembly in `scripts/blog/render.py`: hero (verbatim), featured card (most recent post) as `<a href="/blog/<slug>/">`, and grid cards (remaining posts) each as `<a href>` with `data-cat="<category>"`, filling cover/tag/title/dek/date/read time
- [x] T025 [US2] Render the category nav (`nav data-topcats`) as "All" + one `<a data-cat="<name>">` per categories.yml entry in order (real anchors present in static HTML)
- [x] T026 [US2] Implement category show/hide filtering + active-chip sync in `templates/blog/assets/blog.js` (no effect on crawlability)
- [x] T027 [P] [US2] Author 2–3 more example posts across categories (`content/blog/*.md`) to populate the grid (e.g., Compose, Architecture, Crypto)
- [x] T028 [US2] Build + verify the index lists all posts as real anchors and filtering works

**Checkpoint**: Index browse + filter works; all links crawlable.

---

## Phase 5: User Story 3 - Related "More notes" from author-placed links (Priority: P3)

**Goal**: End-of-post links resolve to related posts rendered as more-notes cards; graceful when
absent; warning when unresolved.

**Independent Test**: A post linking two existing posts at its end shows exactly those two as
more-notes cards; removing the links degrades the section gracefully with valid markup.

- [x] T029 [US3] Implement related-link extraction in `scripts/blog/content.py`: detect wikilinks `[[slug]]`/`[[slug|label]]` and markdown links to `/blog/<slug>/` or `<slug>.md` at the body tail
- [x] T030 [US3] Resolve links to posts and render the more-notes `sc-for` cards in `scripts/blog/render.py` (author order, real `<a href>`); omit the section with valid markup when none; emit a `WARNING:` for unresolved links (no broken card)
- [x] T031 [US3] Add related links to the example posts and build + verify the more-notes section resolves correctly and degrades when removed

**Checkpoint**: Related posts resolve from author links.

---

## Phase 6: User Story 4 - Author-defined categories (Priority: P3)

**Goal**: The categories.yml declaration drives nav order/labels, post chips, and
`articleSection`; unknown categories fail the build.

**Independent Test**: Reorder/relabel/add a category in categories.yml, build, and confirm the
nav and chips update with no code change; a post with an unknown category fails with a clear error.

- [x] T032 [US4] Wire category `label` through render (nav + post chip) and `seo.py` (`articleSection` uses the category label) so categories.yml is the single source
- [x] T033 [US4] Enforce unknown-category build error in `scripts/blog/content.py` with a clear, file-identifying message; confirm add/reorder/relabel reflect on next build (SC-007)

**Checkpoint**: Category set is fully author-driven from the vault.

---

## Phase 7: Polish & Cross-Cutting Concerns

- [x] T034 Create `.github/workflows/deploy.yml`: on push to `main`, set up Python, `pip install -r requirements.txt`, run `build_blog.py` + `verify_build.py`, upload `_site/` via `actions/upload-pages-artifact`, deploy via `actions/deploy-pages`
- [x] T035 [P] Accessibility & CWV pass: verify single `<h1>` per page, `header`/`nav`/`main` landmarks, mascots `aria-hidden`, image dimensions present, animations gated by `prefers-reduced-motion`
- [x] T036 [P] Add `content/blog/README.md` — "How to publish a post from Obsidian" author guide (frontmatter fields, categories, related links, draft flag)
- [x] T037 Determinism check: build twice into separate dirs and diff (must be byte-identical); confirm portfolio `index.html` and root SEO files unchanged
- [x] T038 Final full build + `verify_build.py` green; record results; confirm one consistent absolute site URL across canonical/OG/sitemap/JSON-LD

---

## Dependencies & Execution Order

- **Setup (P1)**: T001–T004 — start immediately.
- **Foundational (P2)**: T005–T018 — depends on Setup; **BLOCKS all user stories**. Within it:
  design-extraction T005–T010 and engine modules T011–T018 ([P] where different files).
- **US1 (P3 phase)**: T019–T023 — depends on Foundational. **MVP**.
- **US2**: T024–T028 — depends on Foundational; independently testable (uses engine + index render).
- **US3**: T029–T031 — depends on Foundational; builds on posts existing (US1 content helpful).
- **US4**: T032–T033 — depends on Foundational; refines category wiring.
- **Polish (P7)**: T034–T038 — after desired stories complete.

### Parallel Opportunities

- Setup: T002, T003, T004 in parallel.
- Foundational design-extraction: T006, T007, T008, T009, T010 in parallel (different files);
  engine T013, T014, T015 in parallel after T012.
- US2 content authoring T027 parallel with index render work.
- Polish T035, T036 in parallel.

## Implementation Strategy

1. Setup + Foundational → engine + extracted design ready.
2. US1 → **STOP & VALIDATE** (MVP: a real static SEO post page). Deployable.
3. US2 → index browse + filter. US3 → more-notes. US4 → author-driven categories.
4. Polish → CI deploy workflow, a11y/CWV, determinism, final verification.

## Notes

- [P] = different files, no dependencies.
- Generated HTML is never committed or hand-edited (Principle IV).
- Every task ends green only when the build + verifier pass for its slice.
