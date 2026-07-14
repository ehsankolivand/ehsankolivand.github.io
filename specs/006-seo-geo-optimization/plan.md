# Implementation Plan: SEO / GEO-AEO Optimization Refinement (Portfolio + Blog)

**Branch**: `006-seo-geo-optimization` (work stays on `main`) | **Date**: 2026-07-14 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/006-seo-geo-optimization/spec.md`

## Summary

Close the small, specific gaps between the current site output and the two re-verified research
briefs, without a rebuild. Five bounded changes, each through the generator/templates/config, the
committed `robots.txt`, or additive/design-neutral portfolio-head edits:

1. **Blog byline → real author anchor** (`templates/blog/article.html`): wrap the visible byline name
   in `<a href="/">` so every post has a crawlable link to the author/entity page (E-E-A-T +
   internal linking; Principle I), appearance unchanged.
2. **`WebSite` node on every post** (`scripts/blog/seo.py`): emit a `WebSite` JSON-LD node
   (`@id = #website`, `publisher = #person`) as a standalone script AFTER the `BlogPosting` (which
   stays first) so each crawlable post URL carries the unified single-entity graph (Principle VIII).
3. **Portfolio head completeness** (`index.html`, additive): Atom feed autodiscovery `<link>`,
   `<meta name="robots" content="index, follow, max-image-preview:large">`, and ProfilePage
   `dateCreated`/`dateModified` from a fixed date constant.
4. **Remove dead resource hints** (`index.html`): delete the two `preconnect` links to
   `fonts.googleapis.com`/`fonts.gstatic.com` (nothing loads from Google; fonts are self-hosted and
   inlined) — a Core-Web-Vitals + privacy cleanup.
5. **`robots.txt`**: add the confirmed-live `Applebot` search crawler; keep the sitemap declaration
   and every existing search/AI-citation token.

Approach is deterministic and additive; it changes no identity fact, so `config.py` and the portfolio
JSON-LD stay in sync automatically. The Definition-of-Done verifier is the acceptance gate.

## Technical Context

**Language/Version**: Python 3 (stdlib only) for the generator; static HTML/CSS/JS output.

**Primary Dependencies**: PyYAML (only build-time dependency; unchanged). No new dependency added.

**Storage**: None — flat files; Obsidian Markdown (`content/blog/**`) is the single content source.

**Testing**: `python -m unittest discover -s tests` (107 renderer/generator unit tests) +
`python scripts/verify_build.py --out _site` (594-check Definition-of-Done verifier).

**Target Platform**: GitHub Pages (static file hosting, `.nojekyll`), served at
`https://ehsankolivand.github.io/`.

**Project Type**: Static-site generator (single Python project) with a hand-authored portfolio page.

**Performance Goals**: Core Web Vitals "good" at p75 — LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1
(re-verified against primary Google sources 2026-07-14; unchanged). Removing dead preconnects reduces
unused connection overhead; no change may regress CLS/INP.

**Constraints**: No backend/DB/runtime; no new build/CI/runtime dependency; deterministic build
(same inputs → byte-identical output); no new `@font-face` family or color system; no
client-rendered content; portfolio non-marker regions + both marker zones intact; identity `@id`s
unified across surfaces; verifier gates unmodified.

**Scale/Scope**: 6 published posts + 1 portfolio page + 1 blog index; well below any crawl-budget
concern (< a few thousand URLs). Five focused edits across 3 files (`article.html`, `seo.py`,
`index.html`) plus `robots.txt`.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Evaluated against constitution v1.5.0 (Principles I–VIII). This feature is a discoverability
refinement that lives inside the SEO/GEO principles; it introduces no design change requiring a
bounded exception.

| Principle | Compliance |
|---|---|
| **I. SEO-Correct Static Generation** | ADVANCES it. The byline becomes a real crawlable `<a>` anchor (server-rendered). No new client-only content. |
| **II. GitHub Pages Only** | PASS. No backend, no new dependency, no runtime. Pure static output. |
| **III. Design Fidelity** | PASS. The byline anchor inherits existing styling (no new color/font/restyle); no page chrome/layout/cover/card change. No new `@font-face` or color system. Removing dead preconnects is non-visual. |
| **IV. Obsidian Single Source** | PASS. No generated HTML is hand-edited; all blog changes flow through templates/config. Posts still come only from `content/blog/**`. |
| **V. Per-Page SEO/GEO Completeness** | ADVANCES it. Portfolio gains robots meta + feed autodiscovery + ProfilePage dates at parity with blog pages; posts gain the `WebSite` entity node. Identity stays unified via `@id`. |
| **VI. Accessibility & Core Web Vitals** | ADVANCES it. Removing dead Google-Fonts connections trims unused overhead; a named author link improves the accessibility tree; compositor-only motion and `prefers-reduced-motion` untouched; one `<h1>` preserved. |
| **VII. Non-Destructive To The Portfolio** | PASS. Portfolio edits are additive SEO head items + a dead-hint removal; both marker zones stay present/paired-once; canonical `#person`/`#website` `@id` identity, single `<h1>`, and robot hooks stay intact. The build still copies `index.html` verbatim (only the LATEST-NOTES region is regenerated), so the verifier's "unchanged outside the managed notes region" comparison holds. |
| **VIII. Machine-Readable Discovery & Unified Identity** | ADVANCES it. Every post carries the `WebSite` node keyed to `#website`; the portfolio gains feed autodiscovery; `robots.txt` adds a confirmed crawler and keeps the sitemap declaration. No dangling links introduced. |

**Gate result: PASS — no violations, no bounded exception invoked, Complexity Tracking not required.**
Identity synchronization is preserved by construction (no identity fact changes; the post `WebSite`
node reuses the existing `#website`/`#person` `@id`s from `config.py`, which already equal the
portfolio's).

## Project Structure

### Documentation (this feature)

```text
specs/006-seo-geo-optimization/
├── plan.md              # This file
├── spec.md              # Feature spec (/speckit-specify)
├── research.md          # Phase 0 output (decisions + volatile-fact verification)
├── data-model.md        # Phase 1 output (entities: identity, per-post graph, discovery surfaces)
├── quickstart.md        # Phase 1 output (validation guide)
├── contracts/
│   └── output-contracts.md   # Per-surface output assertions (verifiable against _site/)
├── checklists/
│   └── requirements.md  # Spec quality checklist (/speckit-specify)
└── tasks.md             # Phase 2 output (/speckit-tasks)
```

### Source Code (repository root)

```text
index.html                      # Portfolio (hand-authored): + feed autodiscovery, robots meta,
                                #   ProfilePage dates; − dead Google-Fonts preconnects
robots.txt                      # + Applebot; keep sitemap + all existing tokens
templates/blog/article.html     # Byline name → <a href="/"> author anchor (appearance unchanged)
scripts/blog/seo.py             # head_for_post(): + standalone WebSite JSON-LD node (after BlogPosting)
scripts/blog/config.py          # Identity constants (UNCHANGED this cycle; already == portfolio)
scripts/build_blog.py           # Build pipeline (UNCHANGED)
scripts/verify_build.py         # Definition-of-Done verifier (UNCHANGED — the gate)
tests/                          # Unit tests (may add coverage for the WebSite node / byline anchor)
```

**Structure Decision**: Single static-site-generator project. Changes are surgical edits to four
existing files (one portfolio page, one root companion, one template, one generator module), plus
optional test coverage. No new modules, directories, or dependencies.

## Complexity Tracking

> No Constitution Check violations — this section is intentionally empty.

Not applicable: the plan invokes no bounded exception and adds no complexity requiring justification.
