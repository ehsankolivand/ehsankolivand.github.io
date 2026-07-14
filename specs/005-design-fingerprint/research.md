# Phase 0 Research — Design-Fingerprint Differentiation

Consolidated evidence behind the locked "Field Almanac" fingerprint. All NEEDS CLARIFICATION resolved (there were none blocking; the spec's Clarifications session captured the five design ambiguities).

## Method
1. **Audit (evidence, not opinion).** Ran `hallmark audit` on each surface (its ~65-gate slop test + structural-sameness read) and cross-checked with `ui-ux-pro-max` (`search.py --design-system`, `--domain typography|style`). Two ranked punch lists produced.
2. **Explore (competing directions).** Three parallel design directions (editorial / engineered-spec-sheet / warm-tactile), each grounded in a real ui-ux search + hallmark reference files, each designing AROUND the fixed robots and fixed palette/fonts.
3. **Confirm (hallmark's own fingerprint).** Ran `hallmark redesign templates/blog`, stopping at its emitted fingerprint. It independently converged on the same spine (Long Document 02 + HP1 vertical-rail; slop-test 58/58; pre-emit P5 H5 E4 S5 R5 V4).

## Decision: adopt "Field Almanac" — a warm, pressed-ink technical field-journal on dark stock
- **Rationale**: it is the synthesis all three directions + hallmark converged on; it sheds every audited slop tell with a concrete replacement; it keeps the palette, the three fonts, and (crucially) makes the robots *more* at home via the tin-toy reskin; and it maps cleanly onto the blog's existing "Field Notes" identity, so it reads as the same site, better set — not a rebrand.
- **Alternatives considered**: (a) a pure catalog theme swap — rejected: palette + fonts are constitutionally fixed, so a catalog theme can't apply; (b) keeping the terminal-cosplay aesthetic and only fixing contrast — rejected: leaves the strongest tells (gradient text, fake window chrome, glow, eyebrow-everywhere) intact, failing SC-001; (c) a bolder structural rebuild that reorders/removes sections — rejected: violates FR-007 (IA preserved) and the "recognizable character" constraint.

## Audit punch list (confirmed, condensed)

### Blog (pre-emit P4 H4 E3 S5 R3 V3; structural: escapes hero→3-feat→CTA but equal-whitespace stacked columns + uniform card grid)
Gradient-clip headline (index.html:12) · fake macOS window on code blocks (block-code.html, off-palette traffic dots) · no token layer / inline hex everywhere · shadow-glow on static dots/pills · compound 6-property card hover (blog.js) · equal-whitespace sections + uniform auto-fill grid · comment-token contrast fail (#66756F ≈3.9:1) · table missing tabular-nums · overflow-x:hidden vs clip · stacked hero eyebrows ("New ·" pill) · same-hue green→green button gradients. KEEP (correct): aria-hidden Unicode callout dingbats + text label, prefers-reduced-motion, focus ring, SVG nav icon.

### Portfolio (pre-emit P4 H4 E4 S3 R2 V3; macro identity distinctive; sameness at section-HEAD level)
Fake terminal window on git-log card (dots + `ehsan@portfolio:~/career $ git log`) · numbered eyebrow on EVERY section (01–05) · gradient-clip headline ("Kolivand") · emoji-as-icons + mismatched sets (✉ ⌥ ✈ 🇹🇷; ◳ ⧉ ⟳) · invented skill-% bars (Kotlin 95% …) · universal scroll fade-up · icon-tile feature quad · shadow-glow everywhere · card-in-card 3-deep · straight quotes · 100vh hero · overflow-x:hidden. A11y bugs to fix (improve, not regress): two `<nav>` lack `aria-label`; `<footer>` nested inside `#sec-contact` (no `contentinfo` landmark). Single h1 OK; zero `<img>` (all art aria-hidden).

### ui-ux-pro-max authoritative second opinion
Style **Dark Mode (OLED)** — deep-black (already #07090A, not pure #000 ✓), high-contrast, WCAG-AAA target, **minimal glow**. Typography: DB default is Inter, but its "Developer Mono" validates JetBrains-Mono-for-code; **the existing Space Grotesk + Manrope + JetBrains Mono trio is stronger than the Inter default → keep it.** Pre-delivery checks that become success criteria: contrast ≥4.5:1 (7:1 AAA), **no emoji as icons → SVG**, minimal glow, no pure #000, prefers-reduced-motion.

## The three explored directions (self-scored /25)
- **A — Editorial technical journal** (23): typographic authority, margin/gutter rail with folios, green-as-ink, sand second accent, masthead nav, colophon footer. Strongest anti-templated *structure*.
- **B — Engineered spec-sheet** (23): visible 12-col grid, key/value fields, **green = live/interaction STATE**, mono as wayfinding, dot-leader skill tiers, tabular data, debug-overlay easter egg. Strongest *token discipline* and best fit for the technical-writing blog (code/tables/callouts).
- **C — Warm-tactile craft** (24): sand co-lead warm tint, letterpress insets, **tin-toy robot reskin (sand shell + green LED eye)**, warmest + highest robot-fit. The freshest, most identity-strengthening differentiator.

## Synthesis (what was taken from each)
- From **A**: editorial rhythm + gutter rail + hairline divider language + colophon nav/footer.
- From **B**: the token discipline — green = live-state, sand = metadata, semantic = syntax/callouts only; editorial-index/field composition; tabular-nums; dot-leader skill tiers; typographic git-log.
- From **C**: warm sand co-lead + pressed-ink tactile surfaces + the tin-toy robot reskin (the standout differentiator that makes the mascots native to the new surface).

## hallmark redesign convergence + 3 adopted refinements
Hallmark's emitted fingerprint matched the synthesis spine exactly (editorial Long Document + vertical rail, editorial index over cards, solid-ink roman Space Grotesk, mono functional-only, typographic code/git frames with no window chrome, green=live-state ≤3%, sand=metadata, section-level reveal, tin-toy robots). Three refinements adopted:
1. **Green ≤3% budget = exactly the live-state set** (links-on-hover, focus ring, active nav underline, HEAD/live marker, robot LED eyes). No decorative green anywhere; those protected live-state uses ARE the budget, kept disciplined.
2. **"Letterpress" → "pressed-ink on dark stock."** On #07090A there is no light paper to deboss; express tactility as inset/recessed panel shadow on `--paper-2` + hairline debossed rules. Same tactile goal, correct physical model for a dark surface.
3. **Tin-toy shell uses DESATURATED sand/panel** (not saturated `#E7D2A6`), reserving saturated sand for text metadata — so the reader keeps reading sand as "warm data," not "robot paint." Avoids role-contention between the robots and the metadata layer.

## Known tension (documented, not a blocker)
Fixed near-black paper `#07090A` brushes hallmark's pure-black-paper gate but **passes on tint** (it carries a cool-green cast, not `#000`). It is constitutionally fixed and already the site's stock; no action.
