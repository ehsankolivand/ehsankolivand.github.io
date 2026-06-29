# Contract: Callouts + Footnotes (accessible static HTML, no client JS)

Governs the two new constructs. Both render fully static and accessible, degrade gracefully, and are deterministic. (FR-014..FR-017; Principles I/IV/VI/VIII.)

## Callout / admonition

**Syntax** (Obsidian-native): a blockquote whose first de-quoted line is `[!kind]` or `[!kind] Optional Title`; remaining quoted lines are the body.

```markdown
> [!warning] Heads up
> Body line one.
> Body line two.
```

**Kind normalization** (lower-cased; synonyms → canonical of {note, tip, warning, important, caution}): `info`→note · `success`/`hint`/`check`→tip · `warn`/`attention`→warning · `important`→important · `danger`/`error`/`bug`/`failure`→caution. Unknown kind → **note**. A blockquote with no `[!…]` first line → a plain (refined) blockquote, unchanged.

**HTML shape** (`block-callout.html`):

```html
<aside class="callout callout--{{KIND}}" role="note" aria-label="{{ARIA}}" data-reveal="" style="…reveal…">
  <div class="callout__head"><span class="callout__icon" aria-hidden="true">{{ICON}}</span><span class="callout__label">{{TITLE}}</span></div>
  <div class="callout__body">{{BODY}}</div>
</aside>
```

- `{{KIND}}` ∈ {note,tip,warning,important,caution}; `{{ARIA}}` = `"{Label} callout"`; `{{TITLE}}` = custom title or the kind's label; `{{ICON}}` = an `aria-hidden` glyph per kind (note `ℹ`, tip `✓`, warning `⚠`, important `★`, caution `‼`); `{{BODY}}` = inline-rendered body (escaped, safe).
- Styling in `blog.css` under `#blog-root`: `.callout` (radius/border/tinted bg/left accent), per-kind left-border + head color from the existing palette — note `#46a8e0`, tip `#34E6A0`, warning `#ffd166`, important `#b388ff`, caution `#ff8a80`. Reduced-motion-safe `data-reveal` reused.

## Footnotes

**Syntax** (PHP-Markdown-Extra / Obsidian): inline reference `[^id]`; block definition `[^id]: definition text` (continuation lines indented).

**Algorithm** (`scripts/blog/markdown_render.py`, post-scoped per `render()`):
1. **Pre-pass** (fence-aware): scan body lines, collect `definitions: dict[id→markdown]`, remove def lines (+ indented continuations). `[^x]` inside a fenced code block is ignored.
2. **Reserve ids**: for each defined id, reserve `fn-<slug(id)>` and `fnref-<slug(id)>` in the **same `used_ids` set** the heading-anchor allocator uses → collision-free vs. headings.
3. **Render**: in `render_inline`, a `[^id]` whose def exists → `<sup class="fnref" id="fnref-<slug>"><a href="#fn-<slug>" role="doc-noteref" aria-label="Footnote {{N}}">{{N}}</a></sup>` (N = order of first reference, 1-based; repeat refs get `fnref-<slug>-k` ids). A `[^id]` with **no** def → literal escaped text (no link).
4. **Section** (`block-footnotes.html`), appended after the body when ≥1 referenced+defined footnote exists:

```html
<section class="footnotes" role="doc-endnotes" aria-label="Footnotes">
  <hr class="footnotes__rule">
  <ol class="footnotes__list">
    <li id="fn-{{SLUG}}" class="footnotes__item">{{DEF_HTML}} <a href="#fnref-{{SLUG}}" class="fn-back" role="doc-backlink" aria-label="Back to content">↩</a></li>
    …
  </ol>
</section>
```

Items in **reference order**. Unreferenced definitions are omitted.

## Invariants (test- + verifier-enforced)

1. **V-CO1**: a known callout kind → `<aside class="callout callout--<kind>" role="note" …>` with the kind's label/icon; the body's inline markup renders.
2. **V-CO2**: an unknown kind → a `note` callout (or a plain blockquote if `[!` absent); **never** a build failure.
3. **V-CO3**: a callout is static — no script needed to display it; decorative icon is `aria-hidden`.
4. **V-FN1**: a defined reference → a `<sup class="fnref">` superscript link to `#fn-<slug>`; the section `<li id="fn-<slug>">` carries a `fn-back` backlink to `#fnref-<slug>`.
5. **V-FN2**: footnote numbering is by reference order; ids are deterministic and **collision-free** (vs. headings and among footnotes) — proven by re-render.
6. **V-FN3**: an **undefined** reference renders as literal text (no anchor); an **unreferenced** definition is omitted — **no dangling, 404-bound anchor** (Principle VIII).
7. **V-FN4**: footnote refs/back-refs are real, keyboard-focusable `<a>` anchors with DPUB-ARIA roles; the section is `role="doc-endnotes"`.
