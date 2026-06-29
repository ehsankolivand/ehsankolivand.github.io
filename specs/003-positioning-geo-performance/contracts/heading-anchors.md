# Contract: Deterministic Heading Anchors

Every rendered body heading on a post page carries a stable, unique, invisible `id` for section-level
deep-linking. (FR-009..FR-011; Principle I, III, VI, VIII.)

## Slug algorithm (`scripts/blog/markdown_render.py`)

`heading_slug(text) -> str`:
1. Take the heading's **visible text** (inline Markdown already rendered, then tags/entities reduced
   to their text — i.e. slug the human-readable words, not the HTML).
2. Unicode NFKD normalize → encode ASCII "ignore" (transliterate accents; drop non-Latin), lowercase.
   *(Same fold as `content.slugify`.)*
3. Replace every run of non-`[a-z0-9]` with a single `-`; strip leading/trailing `-`.
4. If the result is empty (symbol/emoji-only heading), use `""` and let the caller assign the
   `section-<n>` fallback.

## Uniqueness + determinism (within one post, document order)

A per-page allocator assigns final ids deterministically:
- Maintain a `seen: dict[str,int]`. For each heading in order:
  - `base = heading_slug(text)` or `section-<n>` (n = 1-based index of this heading) if empty.
  - If `base` unused → id = `base`. Else → id = `f"{base}-{seen[base]}"` (suffix `-1`, `-2`, … in
    order of recurrence). Record/increment `seen[base]`.
- Depends only on heading text + order → **byte-identical across rebuilds** of identical content.
- The allocator is created per article render (post-scoped) so ids never collide across posts and are
  reproducible.

## Template (`templates/blog/partials/block-h2.html`)

Add `id="{{ID}}"` to the heading element. No other attribute or style changes. Example:

```html
<{{TAG}} id="{{ID}}" data-reveal="" style="…unchanged…">{{CONTENT}}</{{TAG}}>
```

- `ID` is `esc_attr`-escaped (it is already slug-safe ASCII, but escape defensively).
- The `id` is **invisible**: no `:target` styling, no hover "#" affordance (Clarification — design
  fidelity). The only behavior is native fragment navigation.

## Scope

- Applies to body headings only (h2–h4 produced by the renderer). The post `<h1>` (title, in
  `article.html`) is untouched — exactly one `<h1>` per page is preserved (Principle VI).
- Headings inside the markdown body are the only place `block-h2.html` is used, so no other surface is
  affected.

## Invariants (verifier-enforced)

1. Every body heading (`<h2 id>`/`<h3 id>`/`<h4 id>`) on a post page has a non-empty `id`.
2. All heading ids on a page are unique.
3. Ids are deterministic: a second build of identical content yields byte-identical ids (checked by
   re-running the slug allocator over the post bodies and matching the built HTML).
4. The page still has exactly one `<h1>` and no `id` is attached to it.
5. No visual affordance is introduced (no new style/markup beyond the `id` attribute).
