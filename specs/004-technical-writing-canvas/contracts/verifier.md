# Contract: Extended Definition-of-Done Verifier (`scripts/verify_build.py`)

The post-build verifier stays the integration gate and grows to assert every new rendered surface, on the real built site plus synthetic fixtures. Its check count grows beyond the post-003 baseline of **273**. (FR-021; SC-005.)

## New assertions

**On the real built site:**
1. **V-VB1**: the built AnkiVoice post page (its ```` ```bash ```` block) contains highlighted classed spans (`class="tok-` present in the code panel) — proves the highlighter runs on real content (V-CB6).
2. **V-VB2**: every built page's code panels are well-formed — no unresolved `{{…}}` token leaks (existing token check still passes over the new markup); `blog.css` is present and contains the new `tok-*`, `cl`, `callout`, and `footnotes` class definitions.
3. **V-VB3**: determinism — the existing double-build byte-identical guarantee holds with highlighting/callouts/footnotes present (asserted in the build/verify run, see quickstart).

**On synthetic fixtures** (a constant Markdown string rendered through `markdown_render.render` inside the verifier — no `content/blog/*.md` added):
4. **V-VB4**: each supported language fixture → `tok-*` spans for that language; an `xyzlang` fixture → no `tok-` spans, code present + escaped, no error.
5. **V-VB5**: a `title="…" {2,4-5}` fixture → the filename in the label slot + `cl--hl` on exactly lines 2,4,5; a no-metadata fixture → no `cl` wrapper.
6. **V-VB6**: a `> [!warning] Title` fixture → `<aside class="callout callout--warning" role="note"`; an unknown-kind fixture → `callout--note`.
7. **V-VB7**: a footnote fixture → a `fnref` superscript link + a `footnotes` section `<li id="fn-…">` with a `fn-back` backlink; an undefined-ref fixture → literal text, **no** `href="#fn-` dangling anchor.
8. **V-VB8**: table edge-case fixtures → correct alignment (`text-align:center/right`), empty `<td>`, inline markup inside `<td>`, ragged rows well-formed, single-column table recognized.
9. **V-VB9**: security fixtures → `javascript:`/`data:` links neutralized, `{{BODY}}` literal, `</span>`/`</pre>` in code escaped — re-proving the guarantees at the integration layer.
10. **V-VB10**: the highlighter coverage invariant — for each fixture language, the visible text recovered from the rendered code panel (tags stripped, entities unescaped) equals the source code (no character lost or duplicated).

## Synthetic-fixture discipline

- Fixtures are module-level constants in `verify_build.py`; rendering uses a trivial `image_resolver` stub. They are **not** written to `_site` and add **no** content file (honors out-of-scope).
- Each fixture assertion increments the check counter; the final `checks` total MUST exceed 273 and print `verify_build: <N> checks, 0 failure(s)`.

## Unchanged guarantees (regression guard)

All pre-004 assertions remain: per-post content + SEO + JSON-LD + single `<h1>`; index links + graph identity; sitemap; feed; `llms.txt`; portfolio byte-identical outside its two sanctioned zones; required companions; no dangling internal links; unique titles; grounded identity vs. portfolio; font-fidelity proof; heading anchors. The new code must not regress any of these (SC-011).

## Invariants

1. **V-VB-A**: `verify_build.py` exits 0 with `checks > 273` on the current corpus.
2. **V-VB-B**: every new rendered surface (highlight, fallback, filename, line-emphasis, callout, footnote, table edge cases, security) has ≥1 verifier assertion (real or synthetic).
3. **V-VB-C**: the verifier adds no third-party import (stdlib + `blog.*` only).
