# Implementation Plan: Design-Fingerprint Differentiation (Blog + Portfolio)

**Branch**: `005-design-fingerprint` | **Date**: 2026-07-14 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/005-design-fingerprint/spec.md`

## Summary

Refresh the site's *design fingerprint* on both surfaces (the generated blog and the hand-authored portfolio) to shed a common, templated "AI-generated" look, while keeping the recognizable brand, the loved robot mascots, and every functional guarantee. The concrete design is a single locked fingerprint — **"Field Almanac": a warm, pressed-ink technical field-journal on dark stock** — arrived at from an evidence-based audit (hallmark + ui-ux-pro-max), three parallel design directions (editorial / engineered-spec-sheet / warm-tactile), and hallmark's own emitted `redesign` fingerprint (Long Document + vertical gutter-rail, slop-test 58/58, pre-emit P5 H5 E4 S5 R5 V4), which converged on the same spine. It changes only the five sanctioned fingerprint dimensions (type treatment, spacing/rhythm, colour-accent discipline, component composition, motion) inside the FIXED palette and FIXED three fonts. Blog changes flow only through the generator (`templates/blog/**`, `blog.css` under `#blog-root`, `scripts/blog/**`); the portfolio is restyled in committed `index.html` source (sanctioned by constitution v1.5.0 Principle VII exception 3) with both marker zones and the canonical SEO identity intact. Verified by the renderer unit tests and `verify_build.py`, extended with new in-bounds assertions.

## Technical Context

**Language/Version**: Python 3.11+ static generator (stdlib-only: PyYAML + an in-house Markdown/highlighter renderer). Front-end is hand-written HTML/CSS/vanilla JS — no framework, no build step for CSS/JS.

**Primary Dependencies**: None added. Existing: PyYAML (pinned), stdlib. NO new runtime/build/CI dependency, NO new web font, NO CSS/JS library, NO new colour system. (Constitution II & III/VII bound this.)

**Storage**: N/A (static files; Obsidian markdown is the single content source).

**Testing**: `python -m unittest discover -s tests` (renderer unit suite, currently 71 tests) + `python scripts/verify_build.py` (definition-of-done verifier, currently 318 checks). Both must stay green; the verifier gains new fingerprint in-bounds checks.

**Target Platform**: Static site on GitHub Pages, served verbatim (`.nojekyll`); modern evergreen browsers; must remain crawlable without JS.

**Project Type**: Static-site generator + a hand-authored companion page. Two design surfaces, one shared fingerprint.

**Performance Goals**: Core Web Vitals preserved or improved — compositor-only (transform/opacity) motion, `prefers-reduced-motion` honoured, zero cumulative layout shift, no added network weight (no new font/asset; ambient mesh opacity reduced ⇒ same or fewer paint costs).

**Constraints**: No hand-edited generated HTML (blog). Portfolio marker zones (`LATEST-NOTES`, `PORTFOLIO-FONTS`) must stay present, paired, and writable. Per-page SEO/GEO + canonical Person/WebSite JSON-LD identity intact. Exactly one `<h1>` per page. Deterministic build (same content in → same HTML out).

**Scale/Scope**: 2 surfaces; ~3 blog templates + ~20 partials + `blog.css` + `blog.js` + `markdown_render.py`/`highlight.py`; 1 portfolio `index.html` (its `<style>` block + section markup + inline JS). Content volume small (5 posts). The change is stylistic breadth, not new subsystems.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design (below).*

**Governing version: v1.5.0** (Principles III & VII amended this cycle to sanction bounded design-fingerprint differentiation).

### Initial gate (pre-design)

| Principle | Verdict | Note |
|---|---|---|
| I. SEO-correct static generation | ✅ PASS | Pure styling change; all content stays server-rendered in static HTML. No content moves to client JS. |
| II. GitHub Pages only, no backend | ✅ PASS | No new dependency, no server, no build service. Vanilla CSS/JS only. |
| III. Design fidelity | ✅ PASS (under the new bounded exception) | The blog fingerprint change is exactly the sanctioned scope: five fingerprint dimensions only, within the 3 fonts + existing palette, generator-only + `#blog-root`, robots preserved, no new `@font-face`/colour system. |
| IV. Obsidian single source | ✅ PASS | No generated HTML hand-edited; posts unchanged; the generator still renders from `content/blog/**`. |
| V. Per-page SEO/GEO completeness | ✅ PASS | `<head>` SEO/JSON-LD untouched in intent; the restyle does not alter meta/canonical/OG/Twitter/Article JSON-LD or the canonical identity. |
| VI. Accessibility & CWV | ✅ PASS (improves) | Motion stays compositor-only + reduced-motion; one `<h1>`; landmarks; contrast fixes (comment-token, captions) and portfolio a11y-gap fixes (nav labels, footer landmark) improve it. |
| VII. Non-destructive to portfolio | ✅ PASS (under the new bounded exception 3) | Portfolio restyle is the sanctioned committed-source fingerprint change; both marker zones kept present/paired/writable; SEO/JSON-LD + single `<h1>` preserved; robots preserved. |
| VIII. Machine-readable discovery & single-source publishing | ✅ PASS | Atom feed, `llms.txt`, `sitemap.xml`, and `LATEST-NOTES` regeneration all unaffected; no dangling links introduced. |

**Initial gate result: PASS.** No violations → Complexity Tracking is empty (below).

## Design Decisions (the locked "Field Almanac" fingerprint, with rationale)

Every decision ties to either a **[shed]** slop tell or a **[keep]** brand element. Full derivation in [research.md](./research.md); token/interface contract in [contracts/fingerprint-token-layer.md](./contracts/fingerprint-token-layer.md); per-surface change list in [contracts/surface-change-contract.md](./contracts/surface-change-contract.md).

### D1 — Type treatment (within Space Grotesk / Manrope / JetBrains Mono)
- **Decision**: Solid-ink **roman** Space Grotesk headlines (H1 `clamp(2.75rem,4vw+1rem,4.25rem)` wt500; H2 2rem/600; H3 1.375rem/600; tracking −0.02em). Manrope body 17–18px, ~66ch measure, lh 1.6, wt400 (~360 optical on dark). **JetBrains Mono functional-only** — code, inline code, filename/caption bars, date·read-time·tags folios, git hashes, footnote back-refs, field labels, and ONE motivated shell-prompt eyebrow per page; banned as decorative eyebrows/pills/nav labels. Tabular-nums on numeric columns; curly quotes/em-dashes.
- **Rationale**: **[shed]** gradient-clipped headline text (solid ink, authority from weight/scale); **[shed]** mono-cap eyebrow-on-every-section and mono decoration (mono demoted to metadata). **[keep]** the three fonts and the technical/CLI voice where motivated. Backed by hallmark `typography.md` (ratio scale, mono = outlier/code role, no gradient/italic headers) and the ui-ux "JetBrains Mono = technical/data mono" result.

### D2 — Spacing & vertical rhythm
- **Decision**: 4px base, 8-step scale (`--space-3xs…4xl`), ~1.25 modular type ratio, 8px baseline; asymmetric section padding (generous top / tighter bottom), majors at `--space-3xl`; left-biased content column with a narrow **gutter rail** carrying body-level micro-meta (dates, footnote/heading-anchor ticks), not section eyebrows; sections deliberately differ in rhythm.
- **Rationale**: **[shed]** "sections separated by equal whitespace, no divider" (varied rhythm + rail create structure); **[shed]** hanging-header/eyebrow tell (rail holds meta, not tag-left/heading-right). Backed by hallmark `layout-and-space.md` (primary axis, intentional asymmetry, hairline as shadow alternative).

### D3 — Colour-accent discipline (shared token layer over the fixed palette)
- **Decision**: A CSS custom-property token layer that **names the existing hexes** (identical names/values on both surfaces): `--paper #07090A` / `--paper-2 #0C1512` (elevation via lightness + **pressed-ink inset shadow**, not glow) / `--ink #EDF2EF` / `--muted #9FB0AA` / `--muted-2 #828D86`. **Green = live/interaction state only**, budget ≤~3% of viewport = exactly the live-state set (links-on-hover, focus ring, active nav underline, HEAD/live marker, robot LED eyes): `--signal #34E6A0`, `--green-deep #18A06A/#1AA56E`, `--mint #7DF0C2`. **Sand = warm metadata/tint layer** (mono labels, folios, drop-cap, quote/footnote marks, hairline-rule warm tint 6–10% α): `--sand #E7D2A6` / `--sand-deep #CBB07A`. **Semantic = syntax tokens + the 5 callout kinds only, never chrome**: `--sem-blue #46a8e0` / `--sem-yellow #ffd166` / `--sem-purple #b388ff` / `--sem-coral #ff8a80`. **Glow reserved for live robot motion only.**
- **Rationale**: **[shed]** inline-hex/no-token-layer (gate 48), colour-glow-on-static (gate: shadow-glow-on-dark), decorative-green. **[keep]** the exact palette (no new hue/system) and green as the signature — now disciplined as state. This token layer is also the concrete artifact proving **[FR-003]** one shared fingerprint. Backed by hallmark `color.md` (one accent ≤3% viewport, elevation via lightness, tint the neutrals) and ui-ux "Dark OLED: minimal glow / no pure #000".

### D4 — Component recomposition (same IA — no section added/removed/reordered)
- **Hero**: solid-ink, left-biased, content-height (not 100vh) + one motivated mono shell-prompt eyebrow. **[shed]** gradient headline, 100vh-centred default.
- **Code block**: typographic frame — top hairline + mono filename (left) + language (right) + bottom hairline; line-emphasis = 2px gutter tick + faint `--paper-2` row tint. **No traffic-light dots / no mock title bar.** Reworks feature-004 `block-code.html` + `highlight.py` token classes. **[shed]** fake window chrome (gate 47); **[keep]** the git-log/CLI concept + 004 syntax highlighting.
- **Card grid → editorial index**: hairline-ruled rows (title + sand meta + tabular date folio; lead item larger). **[shed]** uniform equal-weight grid.
- **Callouts**: warm `--paper-2` field + 1–2px kind-keyed left rule + single-stroke **SVG** kind-mark (semantic colour); no pill/stripe/glow. Reworks 004 callout classes; swaps the `aria-hidden` dingbats for `aria-hidden` inline SVG. **[shed]** emoji-as-icon/pill/glow while keeping the accessible-label pattern.
- **Quotes**: oversized sand quotation mark hanging into the gutter. **Tables**: hairline row rules + tabular-nums + warm 3%-lightness zebra, no vertical borders. **[shed]** missing tabular-nums; **[keep]** GFM behaviour.
- **Dividers/eyebrows**: hairline + one green square anchor, not a mono-cap eyebrow. Ordinal eyebrows only where genuinely sequential, ≤2/page, stacked same column. **[shed]** eyebrow-everywhere (gate 54).
- **Portfolio skill section**: kill invented %-bars → qualitative tiers (Core/Fluent/Familiar) as dot-leader field rows / grouped tier chips, sand labels, green ring on the primary, **no numbers**. **[shed]** fabricated metrics (gate 46).
- **Portfolio git-log card**: keep the concept, drop the window chrome → typeset changelog (mono hash + tabular date in gutter, descriptions, hairline rows, green `HEAD →` marker). **[shed]** fake terminal window (gate 47).
- **Nav**: wordmark + hairline masthead, real destinations, active underlined green, drop the glassy pill; **add distinct `aria-label`s** to the two portfolio navs. **Footer**: colophon/letter-close (top hairline + typeset sign-off + real links + companion robot); **move the portfolio footer out of `#sec-contact` into a real `contentinfo` landmark**. **[shed]** SaaS pill-nav + 4-col footer; **[improve a11y]** the two audit-found gaps.

### D5 — Motion & microinteraction detailing (compositor-only)
- **Decision**: 3 eases (`--ease-out/-in/-in-out`), durations 120/220/420, exits ×0.75, no bounce on UI state. **Reveal re-orchestrated**: ONE staggered load entrance (`--i*60ms`, cap ~500ms) on hero + first section; scroll reveal reduced to **section-level** (a section's hairline rule draws `scaleX` + content opacity, once) — not per-element. Hover = one signal (hairline brighten OR text lift to mint), ≤1px translate, no box-shadow glow on dark. Focus ring instant, ≥3:1. Pressed-ink press = static inset hairline at rest + `translateY(1px)` on `:active`. `prefers-reduced-motion` collapses spatial motion to opacity crossfade.
- **Rationale**: **[shed]** reveal-on-everything ("page never settles") and compound 6-property hover; **[keep]** the ambient/cursor/robot motion (compositor-only). Backed by hallmark `motion.md` (three easings, stagger-by-`--i`, reveal-once, no hover glow on dark).

### D6 — Robots (reskin-only; ALL behaviours preserved on BOTH surfaces) — PROTECTED
- **Decision**: "Tin-toy" reskin — **desaturated** sand/panel shell + hairline outline (not a neon-glow body), with **green kept only as the LED eye/signal** so they still read as the brand's green robots; shout bubbles → hairline-ruled speech tags, not glossy pills; ambient drifting-mesh kept but at lower opacity (reads as dark-stock tooth, not aurora). Glow isolated to live robot motion (the sanctioned exception). **Nothing is removed, disabled, or flattened.** Portfolio: scroll-reactor + shouts, android mascot, chase gag, logo-tap easter egg, walk/stride bots, cursor/parallax. Blog: scroll-reactor + grad-cap rider, hero companion, robot author-avatar, magnetic cursor, ripple/magnetic, reveal-on-scroll.
- **Rationale**: **[keep]** the loved robots and every reactive animation (FR-006), integrated into — not fighting — the new fingerprint. hallmark's refinement adopted: shell uses *desaturated* sand so saturated sand stays "warm data," not "robot paint." Any audit finding against a robot/cursor/mesh/reveal is a **sanctioned false positive** (FR-008), recorded not acted on.

## Project Structure

### Documentation (this feature)

```text
specs/005-design-fingerprint/
├── plan.md                  # This file
├── spec.md                  # Feature spec (with Clarifications)
├── research.md              # Audit punch list, 3 directions, hallmark convergence, adopted refinements
├── data-model.md            # Design "entities": token layer, protected-robot inventory, marker zones, slop-tell ledger
├── quickstart.md            # How to build + verify + re-audit + exercise robots
├── contracts/
│   ├── fingerprint-token-layer.md   # The shared token contract (names → fixed hexes, type/space scale)
│   └── surface-change-contract.md   # Per-file change list + per-surface in-bounds guarantees
└── checklists/
    ├── requirements.md      # Spec quality checklist (from /speckit-specify)
    └── (design checklists added by /speckit-checklist)
```

### Source Code (repository root — real paths touched)

```text
templates/blog/
├── base.html                # shell: ambient bg, cursor, scroll-reactor+grad-cap, header/nav → recompose + tin-toy reskin, tokens
├── index.html               # blog index: hero, featured, editorial-index (was card grid), footer/colophon
├── article.html             # post page: header, robot author-avatar, gutter rail, signature/colophon
├── partials/
│   ├── block-code.html       # typographic code frame (drop traffic-light window chrome)
│   ├── block-callout.html     # warm field + SVG kind-mark (drop pill/emoji)
│   ├── block-table.html       # tabular-nums + hairline rules
│   ├── block-quote.html       # hanging sand quote-mark
│   ├── grid-card.html / featured-card.html / home-notes-section.html / more-note*.html  # editorial-index rows
│   └── (other block-* partials: rhythm/typography only)
└── assets/
    ├── blog.css              # @font-face (unchanged) + NEW token layer + fingerprint classes (all under #blog-root)
    └── blog.js               # reveal re-orchestration, hover discipline, tin-toy robot params (behaviour preserved)

scripts/blog/
├── markdown_render.py        # callout SVG kind-marks, code-frame markup, table/quote classes, mono-eyebrow discipline
└── highlight.py              # token classes unchanged in contract; colour via tokens

scripts/verify_build.py       # + new in-bounds assertions (no new @font-face/colour system; marker zones; single h1; robots present)
tests/                        # renderer unit tests kept green; add tests for new markup shape where behaviour changes

index.html (portfolio)        # <style> token layer + fingerprint restyle; section recomposition; a11y fixes; robots reskinned; MARKER ZONES UNTOUCHED IN STRUCTURE
```

**Structure Decision**: Two surfaces, one shared token layer. The blog is changed exclusively through the generator (templates + `#blog-root` CSS + generator scripts); generated `_site/**` is never hand-edited. The portfolio is changed in its committed source `index.html` (Principle VII exception 3), touching only its `<style>` block, section markup, and inline JS — never the two marker-zone blocks' machine-readable structure.

## Constitution Check — Post-Design Re-Evaluation

*Re-checked after the Design Decisions above are fully specified.*

- **III (amended)** — The blog decisions D1–D6 stay inside the exception: five fingerprint dimensions only; no new `@font-face` (D1 reuses the three faces); no new colour system (D3 names existing hexes); generator-only + `#blog-root`; robots preserved (D6). ✅
- **VII (amended)** — Portfolio decisions restyle committed source within the same five dimensions; marker zones kept present/paired/writable (surface-change contract lists them as untouched-structure); canonical SEO/JSON-LD + single `<h1>` preserved; robots preserved; a11y improved. ✅
- **V** — No change to any `<head>` SEO tag, canonical URL, OG/Twitter, or Article/Person/WebSite JSON-LD; the `@id` identity graph is untouched. ✅
- **VI** — Motion compositor-only + reduced-motion (D5); contrast fixes raise the comment-token/caption legibility; two portfolio a11y gaps fixed; one `<h1>` per page. ✅
- **VIII** — Feed/`llms.txt`/sitemap/`LATEST-NOTES` regeneration paths unchanged; no dangling links; determinism preserved. ✅
- **I, II, IV** — Static, dependency-free, Obsidian-sourced, no hand-edited generated HTML. ✅

**Post-design gate result: PASS.** The verifier will encode these as executable checks (D-of-D), so the gate is enforced, not asserted.

## Complexity Tracking

*No Constitution Check violations — this table is intentionally empty.*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|--------------------------------------|
| — | — | — |
