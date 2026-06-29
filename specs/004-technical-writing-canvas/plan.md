# Implementation Plan: Technical-Writing Canvas — Syntax Highlighting, Richer Code, Callouts/Footnotes & Renderer Tests

**Branch**: `004-technical-writing-canvas` | **Date**: 2026-06-29 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/004-technical-writing-canvas/spec.md`

## Summary

Turn the in-house, stdlib-only Markdown renderer into a first-class technical-writing surface — without adding a single runtime/build/CI dependency, without client-side rendering, and without restyling the locked design beyond the **Constitution v1.4.0** "sanctioned body-content semantic styling" allowance. The renderer keeps its security-by-construction posture (full HTML escaping, URL-scheme allow-list, single-pass `{{TOKEN}}` substitution, deterministic heading anchors) and gains, for the first time, an isolated unit-test suite.

Technical approach (all build-time / offline, deterministic, stdlib-only):

1. **Vendored syntax highlighter** (`scripts/blog/highlight.py`, NEW): one shared, deterministic regex-scanner engine + per-language ordered rule tables for Kotlin, Java, Python, Bash, JSON, YAML, XML/HTML, JavaScript, TypeScript, SQL, plus a case-insensitive alias map and a closed token-kind → CSS-class vocabulary. `tokenize(code, lang) → (tokens, recognized)`; `emit_html(tokens, emphasized_lines) → str` (inline mode with literal newlines, or block-line mode for emphasis). Unknown language → `recognized=False`, a single plain token → escape-only fallback (never a build failure). Every emitted character is HTML-escaped exactly once; every class name is from the fixed vocabulary.
2. **Richer code blocks** (`scripts/blog/markdown_render.py`): parse the fenced info string into `(language?, filename?, emphasized_lines, legacy_caption?)` (GFM superset; no new frontmatter), call the highlighter, and fill the existing `block-code.html` chrome — title-bar precedence filename → caption → language label → empty; line-emphasis via block-line `cl`/`cl--hl` spans; copy-friendliness preserved (literal newlines when no emphasis).
3. **Quote + table upgrade/harden** (`markdown_render.py` + partials + `blog.css`): detect the `> [!kind]` callout form inside the existing blockquote branch; refine the blockquote treatment with a class layer (no inline-style regression); harden GFM tables (single-column separators, ragged rows, escaped pipes, per-column alignment, inline markup in cells) by replacing the monolithic separator regex with a split-and-check predicate.
4. **Callouts + footnotes** (`markdown_render.py` + `block-callout.html`/`block-footnotes.html` partials + `blog.css`): Obsidian `> [!kind] Title` callouts → labeled, role-annotated static regions; `[^id]` / `[^id]:` footnotes → superscript reference links + an end-of-body `<section class="footnotes">` with back-references, deterministic ids reserved in the shared heading-anchor `used_ids` set, undefined refs left as literal text, unreferenced defs omitted.
5. **Isolated renderer tests + extended verifier** (`tests/`, NEW; `scripts/verify_build.py`; `.github/workflows/deploy.yml`): a stdlib `unittest` suite covering escaping, the URL-scheme allow-list, token-injection, inline markup, nested lists, table edge cases, code highlighting + filename + line-emphasis + fallback, callouts, footnotes, and heading-anchor determinism; CI runs `python -m unittest` before build/verify; `verify_build.py` is extended to assert every new rendered surface (the real built bash block + synthetic fixtures) and its check count grows beyond the post-003 baseline of 273.

## Technical Context

**Language/Version**: Python 3.11+ (CI pins 3.12.7; local 3.12.7). No language change.

**Primary Dependencies**: **None added.** PyYAML==6.0.1 remains the only third-party runtime dependency. Highlighting, parsing, and tests are stdlib-only (`re`, `html`, `unicodedata`, `unittest`, `pathlib`, `functools`).

**Storage**: N/A (static site; no persistence; no new frontmatter or persisted data — Principle IV unchanged).

**Testing**: stdlib `unittest` suite under `tests/` (`python -m unittest`), NEW; the post-build `scripts/verify_build.py` remains the integration Definition-of-Done gate and is extended.

**Target Platform**: Static HTML on GitHub Pages; built in GitHub Actions (Ubuntu, Python 3.12.7); rendered in modern browsers; must be fully legible with no JS and with `prefers-reduced-motion`.

**Project Type**: Single-project static-site generator (author surface `content/blog/`, design `templates/blog/`, generator `scripts/`).

**Performance Goals**: Deterministic O(n) build; highlighting is a single linear scan per code block; no measurable build-time regression on the current 3-post corpus; pages keep their Core Web Vitals posture (no CLS from code blocks, no new web font, compositor-only animations).

**Constraints**: No backend, no new dependency, no client-side rendering, deterministic output (no `today()`/network/randomness), security-by-construction preserved, design byte-faithful outside the sanctioned body-content styling, portfolio `index.html` untouched.

**Scale/Scope**: ~3 posts today (1 fenced block); 10 highlighted languages; 2 new constructs (callouts, footnotes); ~5 touched/new generator files + 2-3 new partials + `blog.css` additions + a new `tests/` package + a CI step + an extended verifier.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.* (Constitution **v1.4.0**.)

| # | Principle | How this plan complies | Status |
|---|-----------|------------------------|--------|
| I | SEO-Correct Static Generation | All highlighting, callouts, footnotes, and refined quotes/tables are rendered to **static HTML at build time**; nothing renders client-side. Code content, callout text, footnote text + links, and table content are present in the served markup before any script runs. | ✅ PASS |
| II | GitHub Pages Only — Static, CI-Built, No Backend | **Zero** new runtime/build/CI dependency: the highlighter is vendored stdlib Python; tests use stdlib `unittest`. No server, no paid service, no browser highlighter. `.nojekyll` and the Actions build/deploy flow are unchanged except a stdlib test step. | ✅ PASS |
| III | Design Fidelity | New visual styling is confined to the **sanctioned body-content styling** exception (v1.4.0): new classes in `blog.css` under `#blog-root` for code tokens, line-emphasis, the filename label, callouts, footnotes, and quote/table refinements — drawn ONLY from the design's existing palette (mint/sand + the bundle's amber/coral/blue/purple accents) and the already-loaded JetBrains Mono; **no new web font, no new color system**; page chrome/layout/covers/cards/nav stay byte-faithful. See the Principle III reconciliation below. | ✅ PASS |
| IV | Obsidian As The Single Content Source | **No new frontmatter** and **no new persisted data**. Everything is driven from the Markdown body and the fenced info string; callout (`> [!kind]`) and footnote (`[^id]`) syntaxes are Obsidian-native, so the same note reads identically in the vault. Generated HTML stays a build artifact. | ✅ PASS |
| V | Per-Page SEO/GEO Completeness | No change to the per-page SEO/GEO contract; footnote/callout content is additional citable static text. Deterministic heading anchors (003) preserved; footnote anchors are deterministic and collision-free. | ✅ PASS |
| VI | Accessibility & Core Web Vitals | Callouts are labeled regions (`role`/`aria-label`); footnote refs/back-refs are keyboard-focusable anchors; decorative glyphs are `aria-hidden`. Exactly one `<h1>` per page preserved. No CLS from code blocks; no new web font; animations stay compositor-only and respect `prefers-reduced-motion` (the existing `data-reveal` idiom is reused). | ✅ PASS |
| VII | Non-Destructive To The Existing Portfolio | The portfolio `index.html` is **not touched** by this feature; both sanctioned portfolio zones (`LATEST-NOTES`, `PORTFOLIO-FONTS`) are unchanged. New CSS lives only in the blog's `blog.css`, which the portfolio does not load. The verifier still asserts byte-equality outside the portfolio's sanctioned zones. | ✅ PASS |
| VIII | Machine-Readable Discovery & Single-Source Publishing | Feed, `llms.txt`, sitemap, and one-commit publishing are unchanged and stay deterministic. New rendered surfaces add no `today()`/network nondeterminism; two builds remain byte-identical. No dangling links: undefined footnote refs render as plain text (never a 404-bound anchor). | ✅ PASS |

**Initial Constitution Check: PASS** (no violations; no Complexity Tracking entries required). Re-evaluated after Phase 1 design below.

### Principle III reconciliation (sanctioned body-content semantic styling)

Syntax highlighting, callouts, footnotes, the filename label, line-emphasis, and the quote/table refinements add **new visual styling to body content** — which a strict reading of Principle III ("new visual styling MUST NOT be invented") forbids. This was reconciled exactly the way feature 003 reconciled its font change: through a constitution amendment (**v1.3.0 → v1.4.0**) that adds a *bounded* exception to Principle III, narrowing it without weakening it. This plan stays inside those bounds by construction:

- **(a) Existing vocabulary only.** Token/callout colors are chosen from hues the design bundle **already uses** — verified by a palette scan of `Ehsan Koolivand - Blog.html`: mint family `#34E6A0`/`#7DF0C2`/`#18A06A`/`#9FE9C8`, sand `#E7D2A6`/`#CBB07A`, and the bundle's existing accents amber `#ffd166`, coral `#ff8a80`, blue `#46a8e0`, purple `#b388ff`. The mono font is the already-loaded JetBrains Mono. **No new `@font-face`, no new color system.**
- **(b) Body content only, via `blog.css`.** All new classes (`tok-*`, `cl`/`cl--hl`, `callout*`, `footnotes`/`fnref`/`fn-back`, quote/table refinements) live in `templates/blog/assets/blog.css` scoped to `#blog-root`. Page chrome, layout, header/nav, covers, and cards are untouched and stay byte-faithful to the bundle.
- **(c) Deterministic & safe.** Highlighting is a deterministic linear scan; unknown languages fall back to safe escaped text (never a build failure); the renderer's escaping / URL-scheme allow-list / single-pass-substitution guarantees are preserved and newly test-proven.
- **(d) Portfolio untouched.** `index.html` is not modified; Principle VII still governs it unchanged.

The verifier enforces the bounds: portfolio byte-identical outside its two zones, no new `@font-face`, highlighted code is well-formed escaped classed markup with a safe fallback, callouts/footnotes are accessible static HTML.

### Security reconciliation (renderer security-by-construction preserved)

The highlighter is a pure function from `(code, language)` to a list of `(token-class | None, text)` pairs whose concatenated `text` equals the input exactly. Emission wraps each token as `<span class="FIXED">esc(text)</span>` or bare `esc(text)`; class names are a closed enum, never author-derived. The highlighted HTML becomes the value of `{{CONTENT}}` in `block-code.html` under the existing **single-pass** `sub_tokens`, so any `{{TOKEN}}` in author code is inert and any `<`/`>`/`&` is already escaped — no breakout, no double-escape, no injection. This is asserted by the new unit suite (FR-004, FR-019).

## Project Structure

### Documentation (this feature)

```text
specs/004-technical-writing-canvas/
├── plan.md              # This file
├── spec.md              # Feature spec (+ Clarifications session)
├── research.md          # Phase 0 — decisions R1..Rn
├── data-model.md        # Phase 1 — derived shapes (no new persisted data)
├── quickstart.md        # Phase 1 — build/verify/test how-to + authoring syntax
├── contracts/           # Phase 1 — highlighter, code-block, callout, footnote, renderer-tests, verifier
│   ├── highlighter.md
│   ├── code-block.md
│   ├── callout-footnote.md
│   ├── renderer-tests.md
│   └── verifier.md
├── checklists/
│   ├── requirements.md          # spec-quality (from /speckit-specify)
│   └── rendering-quality.md     # "unit tests for English" (from /speckit-checklist)
├── analysis.md          # /speckit-analyze cross-artifact gate
├── tasks.md             # /speckit-tasks output
└── convergence.md       # /speckit-converge assessment
```

### Source Code (repository root)

```text
scripts/
├── build_blog.py                 # entry point — UNCHANGED (renderer is internal)
├── verify_build.py               # EXTENDED — assertions for every new rendered surface (+synthetic fixtures)
└── blog/
    ├── highlight.py              # NEW — vendored scanner engine + 10 language rule tables + aliases + token vocab
    ├── markdown_render.py        # EXTENDED — info-string parse, highlight call, callouts, footnotes, table hardening
    ├── config.py                 # (unchanged unless a small constant is cleaner there)
    ├── content.py render.py seo.py sitemap.py feed.py llms.py   # UNCHANGED
templates/blog/
├── assets/blog.css               # EXTENDED — new #blog-root classes (tok-*, cl/cl--hl, callout*, footnotes, quote/table refinements)
└── partials/
    ├── block-code.html           # EXTENDED — title-bar label slot reused; highlighted CONTENT
    ├── block-quote.html          # EXTENDED — class layer for refined treatment (no inline-style regression)
    ├── block-table.html          # EXTENDED — class hook for refined treatment
    ├── block-callout.html        # NEW — labeled, role-annotated callout region
    └── block-footnotes.html      # NEW — end-of-body footnotes section
tests/                            # NEW — stdlib unittest package
├── __init__.py
├── test_markdown_render.py       # renderer behaviors + security guarantees
└── test_highlight.py             # highlighter tokenization + escaping + determinism
.github/workflows/deploy.yml      # EXTENDED — `python -m unittest` step before build/verify
```

**Structure Decision**: Single-project layout preserved. The highlighter is isolated in its own `scripts/blog/highlight.py` (self-contained, separately testable) and called from the renderer's fenced-code path; tests live in a new top-level `tests/` package discoverable by `python -m unittest`. No author-surface or design-system reorganization; the design change is additive CSS classes + two new partials only.

## Phase 0 — Research (`research.md`)

Decisions resolved from the spec's Clarifications, the constitution, the existing code, and primary references (language keyword lists, the GFM tables spec, the PHP-Markdown-Extra footnote convention, the Obsidian callout convention, WAI-ARIA notes). Topics: the scanner-engine design and why ordered-alternation regex is deterministic and safe; the per-language token vocabulary; the info-string grammar; the line-emphasis emission technique and copy-friendliness; the callout + footnote syntaxes and accessibility; the design-grounded color mapping; and the test/verifier strategy. See `research.md`.

## Phase 1 — Design & Contracts

- **`data-model.md`** — the derived shapes: parsed code block, language grammar/token vocabulary, callout, footnote registry, and the test-suite shape. No new authoring field, no persisted data; a determinism summary.
- **`contracts/`** — five contracts: `highlighter.md` (API, token vocabulary, per-language coverage, safety invariants), `code-block.md` (info-string grammar, title-bar precedence, line-emphasis emission, backward compatibility), `callout-footnote.md` (syntaxes, HTML shapes, accessibility, graceful degradation, determinism), `renderer-tests.md` (suite layout, coverage matrix, CI wiring), and `verifier.md` (new assertions + synthetic-fixture strategy + check-count growth). Each lists verifier-/test-enforced invariants (V-prefix ids).
- **`quickstart.md`** — build + verify + test commands, the authoring syntax for the new constructs, and by-hand validation greps.
- **Agent context**: the repo's `CLAUDE.md` is hand-maintained without `<!-- SPECKIT START/END -->` managed markers, so the managed-marker update is N/A; the active-feature pointer is updated manually as the final step of the cycle (per the run's reporting requirements).

**Post-Design Constitution Check: PASS** — the Phase 1 contracts keep every guarantee above: stdlib-only, deterministic, security-preserving, design-bounded, portfolio-untouched, no new dependency. No new violations; Complexity Tracking remains empty.

## Complexity Tracking

> No Constitution Check violations — no entries required.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none) | — | — |
