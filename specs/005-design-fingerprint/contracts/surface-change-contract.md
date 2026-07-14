# Contract — Per-Surface Change List & In-Bounds Guarantees

What each file may change, and the hard guarantees the verifier checks. "Reskin-only" = markup structure/behaviour preserved, styling changed.

## Blog surface (through the generator ONLY; no hand-edited generated HTML)

| File | Changes | Must NOT change |
|---|---|---|
| `templates/blog/assets/blog.css` | Add the token layer (`:root`/`#blog-root`); add fingerprint classes (editorial-index rows, code frame, callout field, quote, table, dividers, gutter rail, pressed-ink surfaces); fix comment-token + caption contrast; `overflow-x: clip`; tabular-nums on tables. All under `#blog-root`. | The `@font-face` block (3 families) — byte-preserved. No new `@font-face`, no new hue. |
| `templates/blog/base.html` | Recompose header/nav (masthead + hairline, functional mono, green active), tokens; tin-toy reskin of scroll-reactor + grad-cap; ambient mesh opacity down; gutter rail scaffold. | Robot DOM/behaviour hooks (`data-reactor*`, `data-cursor*`, `data-ambient`) present; `{{HEAD}}/{{MAIN}}/{{NAV_ITEMS}}` slots intact; `aria-hidden` on decorative art. |
| `templates/blog/index.html` | Hero solid-ink + one mono shell-prompt eyebrow; **card grid → editorial index**; footer → colophon; hero companion reskin. | Section set + order; `{{FEATURED}}/{{GRID}}` slots; hero companion behaviour. |
| `templates/blog/article.html` | Gutter rail for meta/footnote ticks; robot author-avatar tin-toy reskin; signature → colophon; type rhythm. | `{{COVER}}/{{BODY}}/{{MORE_NOTES_SECTION}}` slots; single `<h1>`; author-avatar presence. |
| `templates/blog/partials/block-code.html` | Typographic frame (top hairline + mono filename left + language right + bottom hairline); drop traffic-light dots + title bar. | The `{{CODE}}` / filename / language / line-emphasis data contract from feature 004; HTML escaping. |
| `templates/blog/partials/block-callout.html` | Warm field + kind-keyed 1–2px left rule + single-stroke **SVG** kind-mark (`aria-hidden`) + text label; drop pill/emoji/glow. | The kind → colour mapping semantics; the accessible text label; safe fallback for unknown kind. |
| `templates/blog/partials/block-table.html`, `block-quote.html` | tabular-nums + hairline rules + warm zebra (table); hanging sand quote-mark (quote). | GFM table semantics; blockquote content. |
| `templates/blog/partials/grid-card.html`, `featured-card.html`, `home-notes-section.html`, `more-note*.html` | Editorial-index row composition; drop glow dots/pills. | The post data fields + links (crawlable anchors). |
| other `block-*` partials | Typography/rhythm/token application only. | Block semantics + escaping. |
| `templates/blog/assets/blog.js` | Reveal re-orchestration (load stagger + section-level draw, not per-element); hover discipline (drop compound 6-property hover); tin-toy robot params. | Every robot/cursor/ripple/magnetic/reveal BEHAVIOUR stays present and reactive; reduced-motion guards. |
| `scripts/blog/markdown_render.py` | Emit the new callout SVG kind-marks, code-frame markup, table/quote classes; enforce mono-eyebrow discipline. Deterministic. | Escaping, URL-scheme allow-list, single-pass substitution; unknown language/kind → safe fallback; no new dependency. |
| `scripts/blog/highlight.py` | Token *class* set unchanged; colours come from tokens (CSS). | Escape-only fallback for unknown languages. |

## Portfolio surface (committed `index.html` source — Principle VII exception 3)

| Region | Changes | Must NOT change |
|---|---|---|
| `<head>` (1–106) | none (may only ensure token `<style>` is added below it) | ALL SEO/meta/canonical/OG/Twitter + JSON-LD Person/WebSite/@id — byte-intent preserved. |
| `PORTFOLIO-FONTS` zone (107–307) | **none** | The `<!--PORTFOLIO-FONTS:START/END-->` markers + the 3-family `@font-face` data — untouched. |
| `<style>` (308–375) | Add token layer (`#ek-root`); fingerprint restyle (kill gradient headline, glow, eyebrow-everywhere, card-in-card; pressed-ink surfaces; `overflow-x: clip`). | No new `@font-face`, no new hue. |
| Header/nav (425–437) | Masthead + hairline, real destinations, green active underline, drop glassy pill; **add distinct `aria-label`** to top + bottom nav. | Wordmark + logo easter-egg hook (`data-logo`). |
| Hero (442–489) | Solid-ink headline (kill gradient "Kolivand"); content-height (~88vh); curly quotes. | Single `<h1>` (450); hero content/links. |
| Skills (559–698) | **Kill invented %-bars** → qualitative tiers (Core/Fluent/Familiar), dot-leader/chips, sand labels, green ring on primary; **SVG icons** not emoji. Android mascot tin-toy reskin. | The real skill list (no fabricated numbers, none added); android mascot presence + behaviour. |
| Work / git-log card (698–912) | Keep git-log concept; **drop fake terminal window** → typeset changelog. Reveal re-orchestration. | Content/timeline; `LATEST-NOTES` markers (913–941) — present + paired, region still build-writable. |
| `LATEST-NOTES` zone (913–941) | none (styling around it only, outside the markers) | The `<!--LATEST-NOTES:START/END-->` markers + build-managed region structure. |
| Contact/footer (943–982) | Colophon/letter-close; **move `<footer>` out of `#sec-contact` to a `contentinfo` landmark**; curly quotes; SVG contact icons. | Contact links; companion robot. |
| Inline JS (1000–1494) | Reveal re-orchestration; hover discipline; tin-toy robot params. | Every robot/reactor/chase/easter-egg/cursor/parallax BEHAVIOUR present + reactive; reduced-motion guards. |

## In-bounds guarantees (verifier asserts these — Definition of Done)
1. No new `@font-face` rule on either surface (grep the 3 family names only).
2. No new colour system — only the named token hexes appear as the palette.
3. Blog fingerprint CSS lives only under `#blog-root`; no generated HTML in `_site/**` is hand-edited (build reproduces it).
4. Both portfolio marker zones present + correctly paired; `LATEST-NOTES` still regenerated by the build.
5. Canonical Person/WebSite `@id` JSON-LD + per-page SEO tags intact; exactly one `<h1>` per page.
6. Every protected robot + reactive behaviour present on both surfaces (grep the behaviour hooks; render + exercise).
7. Renderer unit tests green; `verify_build.py` green including the new assertions.
