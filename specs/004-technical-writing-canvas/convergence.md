# Convergence Assessment — feature 004

This project has no installed `/speckit-converge` skill, so convergence is assessed **manually** (as feature 003 was): the implemented codebase is checked thread-by-thread against the spec/plan/contracts, each claim is verified non-vacuously (the assertion would actually fail if the behavior were wrong), and convergence is declared only when every thread has landed and the gates are green.

## Pass 1 — codebase vs. artifacts

| Thread / FR | Artifact intent | In codebase | Converged |
|---|---|---|---|
| Highlighting (FR-001..006) | vendored stdlib scanner, 10 languages, fallback, classed spans, design palette | `scripts/blog/highlight.py` (engine + 10 rule tables + aliases); `blog.css` `tok-*`; real bash block highlighted | ✅ LANDED |
| Rich code (FR-007..011) | info-string grammar, filename label, line-emphasis, legacy caption, copy-friendly | `parse_info_string` + `_code_block` in `markdown_render.py`; `cl`/`cl--hl` in `blog.css` | ✅ LANDED |
| Quotes/tables (FR-012..013) | refined blockquote (no regression), hardened GFM tables | `pquote`/`mdtable` classes; `_is_table_sep` split-and-check predicate | ✅ LANDED |
| Callouts (FR-014..015) | Obsidian `> [!kind]`, accessible, graceful degradation | `_callout` + synonym/meta maps; `block-callout.html`; `callout--*` CSS | ✅ LANDED |
| Footnotes (FR-016..017) | `[^id]`/`[^id]:`, deterministic collision-free ids, no dangling anchor | footnote pre-pass + `_FnCtx` + `_footnote_ref`; `block-footnotes.html`; `footnotes`/`fnref`/`fn-back` CSS | ✅ LANDED |
| Tests (FR-018..020) | stdlib `unittest`, coverage matrix, CI before build | `tests/test_highlight.py` + `tests/test_markdown_render.py` (71 tests); CI step added | ✅ LANDED |
| Verifier (FR-021) | extend with new-surface assertions, > 273 checks | `verify_build.py` +45 checks → **318**, 0 failures | ✅ LANDED |
| No-dep / determinism (FR-022) | no new runtime/build/CI dep; two builds byte-identical | `requirements.txt` unchanged (PyYAML only); double-build diff clean | ✅ LANDED |
| A11y / fidelity (FR-023) | one h1, roles/aria, focusable links, portfolio byte-faithful | DPUB roles on footnotes; `role=note`+label on callouts; verifier portfolio-byte-equality passes | ✅ LANDED |

## Adversarial verification (non-vacuous proof)

Each guarantee was attacked, not just asserted:

- **Escaping / breakout** — a kitchen-sink render with `<out>`, `</span>`, `<b>`, `&` inside code, callouts, and footnote definitions produces only escaped text (`&lt;out&gt;`, `&lt;b&gt;`); `0` raw author tags survive. The real built bash block escapes `<BOT_TOKEN>` → `&lt;BOT_TOKEN&gt;` with `0` raw `<BOT_TOKEN>` in the page.
- **Token-injection** — `{{BODY}}`/`{{CAPTION}}` in paragraphs, code, callouts, and table cells render literally; `0` intact `{{TOKEN}}` pairs reach the substitution pass (the highlighter even splits braces into separate operator spans). Single-pass `sub_tokens` is preserved.
- **URL allow-list** — `javascript:`, `data:`, `vbscript:`, and `\x01javascript:` links are neutralized (link dropped, label kept); `http/https/mailto`/relative kept. Proven by unit tests.
- **Unknown-language fallback** — `xyzlang` → `recognized=False`, `0` `tok-` spans, code escaped, build exits `0` (never fails).
- **Id collision** — a heading "Fn 1" and a footnote `[^1]` both want `fn-1`; the footnote reserves it first (pre-pass), the heading is bumped to `fn-1-1`; the kitchen-sink doc has `0` duplicate ids across all headings + footnotes.
- **Coverage** — for every language, the visible text recovered from the rendered code panel equals the source byte-for-byte (no char lost/duplicated) — asserted both in unit tests and in the verifier.
- **Determinism** — two full builds are byte-identical; the kitchen-sink render is equal across two calls.
- **No regression** — all 273 pre-004 verifier checks still pass (318 total, 0 failures); the portfolio stays byte-identical outside its two sanctioned zones (font-fidelity proof still green).

These are non-vacuous: each test fails if the property is violated (verified during development — e.g. an over-strict early test regex correctly failed on the `cl cl--hl` class form until fixed).

## Remaining work appended

None. Every `<scope>` thread is addressed; every FR has landed and is gate-verified. The feature has **converged** in a single implement pass (no implement→converge loop iteration required).

## Notes for the maintainer

- **Adding a language** later = add a rule table + alias entries in `scripts/blog/highlight.py` (data only; the engine is unchanged) + (optionally) a fixture line in `verify_build.py`/tests. Unknown tags already fall back safely, so this never blocks a build.
- **The new constructs are not yet exercised by committed content** (the 3 posts only contain the one bash block) — they are proven by the unit suite + the verifier's in-process synthetic fixtures. When the owner authors content using callouts/footnotes/tables, they render with no further code change (authoring syntax is in `quickstart.md`).
- **Run order**: `python -m unittest discover -s tests` → `python scripts/build_blog.py --out _site` → `python scripts/verify_build.py --out _site`. CI runs the same, tests first.
