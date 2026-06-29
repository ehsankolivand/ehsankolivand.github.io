# Contract: Isolated Renderer Unit-Test Suite (`tests/`)

Governs the stdlib `unittest` suite for the security-sensitive renderer + highlighter. No third-party dependency. (FR-018..FR-020; Principle II.)

## Layout & run

```text
tests/
├── __init__.py
├── test_markdown_render.py   # renderer behaviors + security guarantees
└── test_highlight.py         # highlighter tokenization, escaping, determinism
```

- **Local**: `python -m unittest` (discovery from repo root) — runs with only PyYAML installed (the suite imports neither PyYAML nor any third-party package).
- **CI**: a step `python -m unittest discover -s tests -v` added to `.github/workflows/deploy.yml` **before** the build and verify steps; no extra `pip install`.
- Tests are **pure**: they import `scripts/blog/markdown_render` + `highlight` and assert on returned strings; no filesystem writes, no network, no randomness. An `image_resolver` stub is passed where `render()` needs one.

## Coverage matrix (FR → assertions)

| Area | FR | Representative assertions |
|---|---|---|
| HTML escaping | FR-004/019 | `<`,`>`,`&` in text/code/cells → `&lt;&gt;&amp;`; escaped exactly once (no `&amp;lt;`) |
| URL allow-list | FR-004/019 | `javascript:`, `data:`, `vbscript:`, `\x01javascript:` links → neutralized (label kept, no `href`); `http/https/mailto`/relative kept |
| Token-injection | FR-004/019 | `{{BODY}}`/`{{CAPTION}}` in paragraph, code, cell, callout → literal `{{BODY}}` (single-pass, never substituted) |
| Inline | FR-019 | bold/italic/bolditalic, inline code (verbatim+escaped), links (emphasis in label), inline images, autolinks |
| Lists | FR-019 | nested ol/ul, marker-type switch (BUG-034), indentation nesting (BUG-008/009) |
| Tables | FR-013/019 | alignment `:--`/`:-:`/`--:`; empty cell; inline markup in cell; escaped pipe `\|`; ragged rows (short→empty `<td>`, long→no corruption); single-column |
| Code + highlight | FR-001..011/019 | per-language `tok-*` spans present; unknown lang → no spans, escaped code; `</span>`/`</pre>` in code inert; multi-line string/comment highlighted; coverage (`"".join`==source) |
| Filename + line-emphasis | FR-008/009/019 | `title="x"` → label `x`; `{2,4-5}` → `cl--hl` on lines 2,4,5 only; legacy caption preserved; copy text == source |
| Callouts | FR-014/015/019 | known kind → `callout--<kind>` + `role="note"`; unknown → note; `> quote` (no `[!]`) → blockquote |
| Footnotes | FR-016/017/019 | ref → `<sup class="fnref">`+link; section `<li id="fn-…">`+backlink; undefined ref → literal; unreferenced def → omitted; deterministic ids |
| Heading anchors | FR-019 | slug determinism, uniqueness/`-1`/`-2`, `section-<n>` fallback, no body `<h1>` |
| Determinism | FR-005/022 | render the same fixture twice → identical strings |

## Invariants

1. **V-TS1**: the suite runs and passes via `python -m unittest` using ONLY the standard library (no package added to `requirements.txt`).
2. **V-TS2**: every security guarantee (escaping, URL allow-list, token-injection, highlighter breakout) has at least one explicit asserting test.
3. **V-TS3**: tests are deterministic and order-independent (no shared mutable state, no `today()`/network).
4. **V-TS4**: CI invokes the suite before build/verify; a renderer regression fails the pipeline early.
