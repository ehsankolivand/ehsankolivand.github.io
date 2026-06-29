# Implementation Plan: Android-Engineer Positioning, Deep-Citability & Portfolio Performance

**Branch**: `003-positioning-geo-performance` | **Date**: 2026-06-29 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/003-positioning-geo-performance/spec.md`

## Summary

Build on the SEO/GEO/one-commit-publishing foundation (002) to (a) make the site read unambiguously
as a **Senior Android Engineer who builds code-generation tooling**, (b) make every post section-level
**deep-citable**, (c) **lighten the highest-traffic page**, and (d) close the gaps the 002 review left
open. All changes are build-time, deterministic, static, GitHub-Pages-only, design-faithful, and
grounded — no fabricated content, no new runtime/CI dependency, no restyle.

Technical approach (all build-time/offline, deterministic):

1. **Grounded identity enrichment** (`scripts/blog/config.py`, `scripts/blog/seo.py`): the blog's
   canonical author node already references the portfolio `#person` by `@id` and carries `jobTitle` +
   `sameAs`. Add a single grounded constant `AUTHOR_KNOWS_ABOUT` — the portfolio's `Person.knowsAbout`
   list copied **verbatim** — and emit it as `knowsAbout` on the blog's full author node (post pages +
   index `Blog.author`). This makes every post self-describe its author as a Senior Android Engineer
   whose expertise *includes* the developer-tooling/code-generation topics (the portfolio already
   lists "Spec-driven development" and "Agentic code generation" — the grounded bridge), so an engine
   reading a Python-tooling post in isolation still resolves an Android engineer, not a separate
   "Python developer". No new entity; no fabricated value.

2. **Section-level heading anchors** (`scripts/blog/markdown_render.py`, `templates/blog/partials/
   block-h2.html`): give every rendered body heading a deterministic, collision-free `id` (GitHub-
   style slug of the heading text + numeric suffix for repeats within a page; `section-<n>` fallback
   for symbol-only headings). The `id` is added to the existing heading partial as a new token — no
   visual change, no client JS, invisible by default (Clarification: no hover affordance).

3. **Portfolio font optimization (prove-or-defer)** (`index.html`, new committed baseline): wrap the
   inlined `@font-face` block in `<!--PORTFOLIO-FONTS:START/END-->` markers, snapshot the pre-change
   `index.html` to a committed baseline, then remove the 32 demonstrably-unused non-Latin `@font-face`
   rules (Cyrillic, Cyrillic-ext, Greek, Vietnamese — ~242 KB decoded / ~323 KB of base64 source),
   keeping Latin + Latin-ext (22 faces). Gated by a new offline verifier proof (glyph-coverage +
   outside-zone byte-equality). **Landed only if proven; otherwise deferred, fonts untouched.**

4. **Taxonomy readiness**: confirm (and assert) that declared empty categories (Compose, Architecture)
   already degrade gracefully through the existing nav/index/empty-grid paths; no code change beyond a
   verifier assertion is expected (the generator is already data-driven from `categories.yml`).

5. **Inherited fixes**: constitution finalized at **v1.3.0** (Principle VIII ratified, stale "I–VII"
   gate reference corrected, font exception added — done in the constitution phase); set 001/002 spec
   `Status` to implemented; this spec's `Status` progresses honestly.

6. **Verifier expansion** (`scripts/verify_build.py`): assert grounded identity signals
   (`knowsAbout`/jobTitle/`@id`, no fabricated value), `sameAs` exact-match vs the portfolio,
   author/locale consistency, per-post tag→keyword + `article:tag` presence, deterministic+unique
   heading anchors, empty-category graceful render, and (when applied) the font-fidelity proof.
   Coverage grows from the post-002 baseline of **163**.

## Technical Context

**Language/Version**: Python 3.11+ (CI pins 3.12.7); local 3.12.7.

**Primary Dependencies**: `PyYAML==6.0.1` only. All new code is **stdlib-only** (`html`, `json`, `re`,
`unicodedata`, `pathlib`). The font subset is performed with a one-off script in the sandbox that does
pure text deletion of whole `@font-face` blocks (no font-tooling library, nothing added to CI/runtime).

**Storage**: Filesystem only. Source in `content/blog/` + `index.html`; generated site in `_site/`
(git-ignored). One new committed reference file (the portfolio font baseline) under a non-served path.

**Testing**: `scripts/verify_build.py` (post-build Definition-of-Done verifier). Baseline: **163**
checks, 0 failures. This feature expands it. No unit-test framework is introduced (consistent with the
project; recorded in research.md).

**Target Platform**: Static web on GitHub Pages; fully readable by non-JS crawlers and AI assistants.

**Project Type**: Static site generator (single project: generator + templates + content + portfolio).

**Performance Goals**: Build stays a few seconds. Highest-traffic page (`index.html`) drops ~323 KB of
base64 font source (~30% of the file) when the font change lands, improving parse/transfer/LCP with
zero visual change. CWV otherwise preserved (no CLS, compositor-only animations, reduced-motion gated).

**Constraints**: No backend/DB/server/paid service; deterministic (no `today()`); design reproduced
exactly (heading anchors are invisible; font change is non-visual); portfolio untouched outside its
two sanctioned regions (managed Field-notes region + the new `PORTFOLIO-FONTS` zone); one absolute URL
(`https://ehsankolivand.github.io/`); identity = "Ehsan Kolivand", Senior Android Engineer, Istanbul,
with every asserted skill/title/link grounded verbatim in the portfolio.

**Scale/Scope**: Personal site, 3 posts + 4 categories (2 empty) today; architecture scales unchanged.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.* (Constitution **v1.3.0**.)

| # | Principle | How this plan complies | Status |
|---|-----------|------------------------|--------|
| I | SEO-Correct Static Generation | Identity signals, heading anchors, and the lighter portfolio are all emitted/edited at build time into static HTML; nothing depends on client JS. Heading `id`s and `knowsAbout` are in the served markup; internal links stay real anchors. | ✅ PASS |
| II | GitHub Pages Only (static, CI, no backend) | No server/DB/paid service. The font subset is a one-off **offline** text edit (no font library in CI/runtime); `knowsAbout`/anchors are pure-Python build output. No new dependency. | ✅ PASS |
| III | Design Fidelity | No restyle. Heading anchors are an invisible `id` attribute (Clarification: no hover affordance). The font change is **non-visual** (only unused, never-rendered subsets removed; every rendered glyph keeps coverage — proven). No template visual change. | ✅ PASS |
| IV | Obsidian As Single Content Source | No new required frontmatter. `knowsAbout` is a grounded config constant mirrored from the portfolio; heading anchors derive from heading text; empty-category handling is data-driven from `categories.yml`. Generated output stays git-ignored, never hand-edited. | ✅ PASS |
| V | Per-Page SEO/GEO Completeness | Enriches per-page identity (grounded `knowsAbout` + `jobTitle` + unified `@id` + exact `sameAs`); hardens author/locale/article-tag completeness via the verifier. Every asserted signal is grounded (no fabricated capability — FR-005/FR-002). | ✅ PASS |
| VI | Accessibility & Core Web Vitals | **Improves** CWV: the highest-traffic page sheds ~323 KB of unused font bytes. One `<h1>` retained (anchors apply to body h2–h4 only); landmarks/contrast/reduced-motion untouched; no CLS introduced. Heading `id`s aid in-page navigation (a11y positive). | ✅ PASS |
| VII | Non-Destructive To Portfolio | Build still copies `index.html` verbatim. The **only** portfolio source edit is inside the new, constitution-sanctioned (v1.3.0, exception 2) `PORTFOLIO-FONTS` zone — non-visual, fidelity-proven (glyph coverage preserved + outside-zone byte-identical to a committed baseline), original recoverable. **Prove-or-defer**: not landed unless proven. Field-notes region behavior unchanged. | ✅ PASS |
| VIII | Machine-Readable Discovery & Single-Source Publishing | Strengthens the unified identity (`knowsAbout` + exact `sameAs` lock) so engines merge portfolio+blog into one richer entity; heading anchors deepen machine citability; one-commit publishing + determinism preserved; verifier still guards no-dangling-links and now identity/anchor/font invariants. | ✅ PASS |

**Initial gate: PASS** (no violations). **Post-design re-check (after Phase 1): PASS** — research,
data-model delta, contracts, and quickstart introduce no deviation. Complexity Tracking is empty.

### Font-fidelity reconciliation (Principle VI ⟷ Principle VII) and the prove-or-defer gate

This is the single highest-risk change: the only edit to committed portfolio source bytes outside the
managed Field-notes region. The constitution was amended to **v1.3.0** to sanction it explicitly as a
second bounded, marker-delimited, non-visual exception to Principle VII, justified by Principle VI.
The reconciliation is made safe by a deterministic, offline **fidelity proof** in the verifier, and a
**prove-or-defer** rule:

- **Sanctioned zone**: the inlined `@font-face` block in `index.html`, wrapped in
  `<!--PORTFOLIO-FONTS:START-->` / `<!--PORTFOLIO-FONTS:END-->` markers. Only bytes inside this zone
  may change, and only by deleting whole unused `@font-face` rules.
- **Recoverable original**: before subsetting, the full pre-change `index.html` (markers added, all 54
  faces intact) is committed as a baseline at `assets/portfolio-fonts/index.baseline.html` (a path the
  build never copies — not served). Deferral = leave `index.html` byte-equal to this baseline.
- **Proof obligation (a) — glyph coverage**: extract every codepoint the portfolio could render
  (whole file minus the base64 font payloads — a conservative superset of visible text). For each such
  codepoint that the **baseline** font set covered via some `@font-face` `unicode-range`, the
  **current** font set MUST still cover it. (Empirically pre-verified: every non-ASCII rendered
  codepoint — em-dash, middle-dot, é, °, …, ©, ↓ — is covered by the retained Latin subset or by no
  subset at all; none is covered only by a dropped non-Latin subset.)
- **Proof obligation (b) — outside-zone integrity**: split both `index.html` and the baseline at the
  `PORTFOLIO-FONTS` markers; the prefix+suffix (everything outside the zone) MUST be byte-identical;
  and every retained `@font-face` rule in the current zone MUST appear verbatim in the baseline zone
  (only whole-subset removals, never edits to a kept face).
- **Prove-or-defer**: if either obligation cannot be made to pass deterministically and offline, the
  font change is reverted to the baseline and recorded as deferred with the reason; **every other
  thread still ships** and the verifier stays green (the font proof only runs when the zone differs
  from the baseline; an untouched/zone-equal portfolio trivially passes).

This keeps Principle VII intact (nothing but sanctioned, proven-non-visual font bytes changes) while
honoring Principle VI (a materially lighter highest-traffic page), with no principle weakened.

### Grounding discipline (Principle V) — every identity signal traces to the portfolio

`AUTHOR_KNOWS_ABOUT` is the portfolio `Person.knowsAbout` list copied verbatim (Android development,
Kotlin, Jetpack Compose, MVI, MVVM, Clean Architecture, Multi-module architecture, Coroutines,
Dagger/Hilt, Server-Driven UI, Android TV, Spec-driven development, Agentic code generation).
`jobTitle` = the portfolio's "Senior Android Engineer". `sameAs` = the portfolio's three profiles
(GitHub, LinkedIn, Telegram). The verifier parses `index.html`'s JSON-LD and asserts the blog's values
**equal** the portfolio's — so nothing is fabricated and nothing can silently drift. No new skill,
title, profile, or post is invented.

## Project Structure

### Documentation (this feature)

```text
specs/003-positioning-geo-performance/
├── plan.md              # This file
├── spec.md              # Feature spec (with Clarifications)
├── research.md          # Phase 0 output (decisions + rationale + primary sources)
├── data-model.md        # Phase 1 output (identity/anchor/font-zone shapes)
├── quickstart.md        # Phase 1 output (run + validate + font-subset procedure)
├── contracts/           # Phase 1 output
│   ├── identity.md          # Grounded Person/knowsAbout/sameAs structured-data contract
│   ├── heading-anchors.md   # Deterministic heading-id contract
│   ├── font-optimization.md # Sanctioned font-zone + fidelity-proof contract
│   └── verifier.md          # New Definition-of-Done assertions
├── checklists/
│   ├── requirements.md      # Spec quality (from /speckit-specify)
│   └── positioning-geo-perf.md  # Positioning/GEO/perf/a11y checklist (/speckit-checklist)
└── tasks.md             # Phase 2 output (/speckit-tasks)
```

### Source Code (repository root) — files this feature touches

```text
content/blog/*.md                    # UNCHANGED authoring surface (no new fields, no new posts)
content/blog/categories.yml          # UNCHANGED (Compose/Architecture already declared + empty)

index.html                           # ONE sanctioned edit: add <!--PORTFOLIO-FONTS:*--> markers and
                                     #   delete the 32 unused non-Latin @font-face rules (prove-or-defer).
                                     #   Everything outside the zone byte-identical to the baseline.
assets/portfolio-fonts/
└── index.baseline.html              # NEW committed baseline (recoverable original; NOT served/copied)

templates/blog/partials/block-h2.html  # add id="{{ID}}" to the heading element (invisible; no style change)

scripts/blog/
├── config.py                        # add AUTHOR_KNOWS_ABOUT (verbatim from portfolio knowsAbout)
├── seo.py                           # emit knowsAbout on the full author node (post + index)
└── markdown_render.py               # deterministic, unique heading-id slugging; pass ID to block-h2

scripts/verify_build.py              # + assertions: grounded knowsAbout/jobTitle/@id present & equal to
                                     #   portfolio; sameAs exact-match vs portfolio; author/locale
                                     #   consistency; per-post tag→keyword + article:tag; heading anchors
                                     #   present/unique/deterministic; empty-category graceful; font
                                     #   fidelity proof (codepoint coverage + outside-zone byte-equality)

specs/001-obsidian-blog/spec.md      # Status: Draft -> Implemented (carried-over fix)
specs/002-seo-geo-publish/spec.md    # Status: Ready for Planning -> Implemented (carried-over fix)
.specify/memory/constitution.md      # v1.2.0 -> v1.3.0 (done in the constitution phase)
.github/workflows/deploy.yml         # UNCHANGED (already builds + verifies + deploys)
```

**Structure Decision**: Single-project static-site generator, unchanged boundaries (author surface
`content/blog/`, design `templates/blog/`, generator `scripts/`, portfolio `index.html`). The font
baseline gets its own non-served `assets/portfolio-fonts/` path so it is recoverable but never
deployed. No new generator module is needed (identity = a config constant + a few `seo.py` lines;
anchors = a slugging helper in the existing renderer). CI is unchanged — it already builds then
verifies.

## Complexity Tracking

> No Constitution Check violations — this section is intentionally empty.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none)    | —          | —                                   |
