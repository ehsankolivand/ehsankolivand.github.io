---
description: "Task list for feature 004 — Technical-Writing Canvas (highlighting, rich code, callouts/footnotes, renderer tests)"
---

# Tasks: Technical-Writing Canvas

**Input**: Design documents from `specs/004-technical-writing-canvas/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/{highlighter,code-block,callout-footnote,renderer-tests,verifier}.md, quickstart.md

**Tests**: REQUESTED — a stdlib `unittest` suite is a first-class deliverable (US5). Test tasks are included and, where they pin behavior, are written before/with the implementation they guard.

## Format: `[ID] [P?] [Story] Description`

- **[P]** = different file, no dependency on another in-flight task → parallelizable.
- **[Story]** = US1 (highlighting) | US2 (rich code) | US3 (callouts/footnotes) | US4 (quotes/tables) | US5 (tests/verifier).
- **Single-file rule**: all edits to one file are sequential among themselves and never `[P]` together — this applies to `scripts/blog/highlight.py`, `scripts/blog/markdown_render.py`, `templates/blog/assets/blog.css`, and `tests/test_markdown_render.py`.

## Phase 1: Setup

- [ ] T001 [P] Create the test package `tests/__init__.py` (empty) so `python -m unittest discover -s tests` resolves the package. (US5 scaffold)

## Phase 2: Foundational — the vendored highlighter engine (BLOCKS US1/US2)

**⚠️ The highlighter is the prerequisite for the code-block stories.**

- [ ] T002 Create `scripts/blog/highlight.py`: the closed `TOKEN_CLASSES` vocabulary, the ordered-alternation `Scanner` engine, `tokenize(code, lang) -> (tokens, recognized)`, `emit_html(tokens, emphasized_lines)` (inline + block-line modes), `resolve_lang`, the `ALIASES` map, and the `highlight_code` convenience — per `contracts/highlighter.md`. Pure, deterministic, stdlib `re`/`html` only.
- [ ] T003 In `scripts/blog/highlight.py`, add the FULL rule tables + keyword/type/builtin frozensets for **kotlin, java, python, bash** (comments, strings incl. multi-line, numbers, operators, identifiers→classify). (depends on T002)
- [ ] T004 In `scripts/blog/highlight.py`, add the lighter rule tables for **json, yaml, markup (xml/html), javascript, typescript, sql** and finalize the alias map. (depends on T002; same file as T003 → sequential)

**Checkpoint**: `python -c "from scripts.blog import highlight"` imports; engine + 10 languages available.

## Phase 3: User Story 1 — Syntax-highlighted code blocks (Priority: P1) 🎯 MVP

**Goal**: Fenced code is highlighted at build time for the 10 languages; unknown/absent language → safe escaped fallback; security preserved.

**Independent Test**: build with `kotlin`/`java`/`python`/`bash`/`json`/`xyzlang` fences → first five have `tok-*` spans, the unknown is plain escaped, build exits 0, two builds byte-identical.

- [ ] T005 [P] [US1] Write `tests/test_highlight.py`: total-coverage invariant (`"".join(text)==code`), per-language token spans, unknown-language fallback (no spans), escaping/`</span>`/`</pre>` breakout inert, `{{TOKEN}}` inert, determinism (tokenize twice). (V-HL1..V-HL7)
- [ ] T006 [US1] In `scripts/blog/markdown_render.py`, add `parse_info_string(info) -> (language, filename, emphasized_lines, caption)` per `contracts/code-block.md` (GFM superset + legacy-caption fallback). (depends on T002)
- [ ] T007 [US1] In `scripts/blog/markdown_render.py`, rewrite the fenced-code path (`_code_block`/`render`) to call `highlight_code` and fill `block-code.html` with highlighted `{{CONTENT}}` + the title-bar label (precedence filename→caption→language→""). (depends on T006, T003, T004; same file as T006 → sequential)
- [ ] T008 [P] [US1] In `templates/blog/assets/blog.css`, add `#blog-root .tok-*` token color classes (11, design palette) + `.cl` / `.cl--hl` line classes (full-bleed emphasis). (FR-006)
- [ ] T009 [P] [US1] Start `tests/test_markdown_render.py`: code-fence highlighting present for a known language, fallback for unknown, title-bar label, escaping + `{{TOKEN}}` injection inside a code block. (depends on T007 for assertions)

**Checkpoint**: `python scripts/build_blog.py` highlights the real AnkiVoice bash block; US1 testable.

## Phase 4: User Story 2 — Filename label + line-emphasis (Priority: P2)

**Goal**: `title="…"` filename label + `{1,3-5}` line-emphasis from the info string; copy-friendly; backward compatible.

**Independent Test**: ```` ```python title="app/main.py" {2,4-5} ```` → label `app/main.py`, `cl--hl` on lines 2/4/5 only, copy yields source.

- [ ] T010 [US2] In `scripts/blog/markdown_render.py`, wire the filename label into the title-bar slot and the `emphasized_lines` set into the emit (block-line mode when non-empty; inline otherwise). (depends on T007; same file → sequential)
- [ ] T011 [US2] Extend `tests/test_markdown_render.py`: `title=` label precedence, `{2,4-5}` → `cl--hl` on exactly those lines, no-metadata → inline mode (literal newlines), legacy caption preserved, copy-text == source. (depends on T009; same file → sequential)

**Checkpoint**: rich code blocks work; existing captions unaffected.

## Phase 5: User Story 3 — Callouts + footnotes (Priority: P2)

**Goal**: Obsidian `> [!kind]` callouts and `[^id]`/`[^id]:` footnotes render as accessible static HTML; graceful degradation; deterministic ids.

**Independent Test**: `> [!warning] Title` → `<aside class="callout callout--warning" role="note">`; `[^1]`+`[^1]:` → superscript ref + footnotes section + backref; undefined ref → literal.

- [ ] T012 [P] [US3] Create partial `templates/blog/partials/block-callout.html` per `contracts/callout-footnote.md` (aside/role/aria, head icon+label, body).
- [ ] T013 [P] [US3] Create partial `templates/blog/partials/block-footnotes.html` per `contracts/callout-footnote.md` (section/role=doc-endnotes, ol, items + backrefs).
- [ ] T014 [US3] In `scripts/blog/markdown_render.py`, detect the `> [!kind]` callout form inside the blockquote branch (synonym map, title, body, unknown→note) and fill `block-callout.html`. (depends on T012; same file → sequential)
- [ ] T015 [US3] In `scripts/blog/markdown_render.py`, implement footnotes: fence-aware definition pre-pass + id reservation in the shared `used_ids` set, `[^id]` ref handling in `render_inline` (threaded footnote registry), and the end-of-body footnotes section. (depends on T013; same file → sequential)
- [ ] T016 [US3] In `templates/blog/assets/blog.css`, add `.callout` + per-kind variants and `.footnotes`/`.fnref`/`.fn-back` classes (design palette, DPUB styling). (same file as T008 → sequential)
- [ ] T017 [US3] Extend `tests/test_markdown_render.py`: callouts (known kind, unknown→note, plain `>` quote unaffected), footnotes (defined/undefined/duplicate/unreferenced, deterministic ids, no dangling anchor). (same file → sequential)

**Checkpoint**: both new constructs render accessibly with no client JS.

## Phase 6: User Story 4 — Blockquote refinement + table hardening (Priority: P3)

**Goal**: refined blockquote treatment (no regression) + hardened GFM tables (alignment, empty/ragged cells, inline markup, escaped pipes, single column).

**Independent Test**: render aligned/empty/inline/escaped-pipe/ragged/single-column tables → well-formed; multi-paragraph blockquote → refined, no regression.

- [ ] T018 [US4] In `scripts/blog/markdown_render.py`, replace the `_TABLE_SEP` monolith with a split-and-check separator predicate (single-column + ragged safe); confirm alignment/escaped-pipe/inline-cell paths; add a `mdtable` class hook. (same file → sequential)
- [ ] T019 [P] [US4] Add class hooks to `templates/blog/partials/block-quote.html` (`pquote`) and `templates/blog/partials/block-table.html` (`mdtable`); add the `.pquote`/`.mdtable` refinements to `templates/blog/assets/blog.css` (decorative quote mark, table row-hover). (blog.css same file as T016 → sequential)
- [ ] T020 [US4] Extend `tests/test_markdown_render.py`: table alignment/empty/inline-markup/escaped-pipe/ragged/single-column + blockquote no-regression. (same file → sequential)

**Checkpoint**: existing quotes/tables improved with zero regression.

## Phase 7: User Story 5 — Isolated tests + extended verifier + CI (Priority: P1)

**Goal**: the security-sensitive renderer is fully test-covered; the verifier asserts every new surface; CI runs the suite; check count > 273.

**Independent Test**: `python -m unittest` passes stdlib-only; `verify_build.py` passes with > 273 checks; CI runs the suite before build/verify.

- [ ] T021 [US5] Complete `tests/test_markdown_render.py`: escaping, URL allow-list (`javascript:`/`data:`/control-char bypass), token-injection across paragraph/cell/callout, inline markup (bold/italic/code/links/images/autolinks), nested lists (BUG-034/008/009), heading-anchor determinism + uniqueness + `section-<n>` fallback. (same file → sequential; FR-019, V-TS1..4)
- [ ] T022 [US5] Extend `scripts/verify_build.py`: assert the built AnkiVoice bash block is highlighted; render synthetic Markdown fixtures through `markdown_render` and assert per-language highlight, unknown-language fallback, filename label, line-emphasis, callouts, footnotes (incl. no dangling anchor), table edge cases, and security; assert `blog.css` ships the new classes; ensure `checks` > 273. (depends on T007/T010/T014/T015/T018; per `contracts/verifier.md`)
- [ ] T023 [P] [US5] Extend `.github/workflows/deploy.yml`: add a `python -m unittest discover -s tests -v` step before the build and verify steps (no new `pip install`).

**Checkpoint**: unit suite + extended verifier both green; CI wired.

## Phase 8: Polish & cross-cutting

- [ ] T024 Run `python -m unittest`, then `python scripts/build_blog.py --out _site`, then `python scripts/verify_build.py --out _site`; iterate to green; confirm determinism (two builds byte-identical via `diff -r`). (depends on all prior)
- [ ] T025 [P] Update `PROJECT_CONTEXT.md`: new `highlight.py` module + language coverage + fallback, rich code-block/quote/table/callout/footnote capabilities, the `tests/` suite + how to run, the verifier's new count, Constitution v1.4.0, the 004 spec folder, and the now-closed "no renderer tests"/"no syntax highlighting" known issues.
- [ ] T026 [P] Update `CLAUDE.md` active-feature pointer to `004-technical-writing-canvas` (IMPLEMENTED) with the plan/constitution/verifier-count references.

---

## Dependencies & Execution Order

- **Setup (T001)** → no deps.
- **Foundational (T002 → T003 → T004)** — `highlight.py` engine then language tables; BLOCKS US1/US2.
- **US1 (T005–T009)** depends on Foundational. **MVP.** T006→T007 sequential (`markdown_render.py`); T008 (blog.css) and T005 (test_highlight.py) are `[P]`.
- **US2 (T010–T011)** depends on US1 (T007/T009); both sequential within their files.
- **US3 (T012–T017)** depends on Foundational; partials T012/T013 are `[P]`; T014/T015 sequential (`markdown_render.py`, after their partials); T016 sequential on blog.css; T017 sequential on the test file.
- **US4 (T018–T020)** depends on Foundational; T018 sequential (`markdown_render.py`), T019 `[P]` partials (blog.css part sequential), T020 sequential test file.
- **US5 (T021–T023)** — T021 completes the test file (sequential); T022 verifier depends on all render work; T023 CI is `[P]`.
- **Polish (T024–T026)** — T024 after everything; T025/T026 `[P]` docs.

| Story | Primary files |
|---|---|
| Foundational | `scripts/blog/highlight.py` |
| US1 | `scripts/blog/markdown_render.py`, `templates/blog/assets/blog.css`, `tests/test_highlight.py`, `tests/test_markdown_render.py`, `templates/blog/partials/block-code.html` |
| US2 | `scripts/blog/markdown_render.py`, `tests/test_markdown_render.py` |
| US3 | `scripts/blog/markdown_render.py`, `templates/blog/partials/block-callout.html`, `block-footnotes.html`, `blog.css`, `tests/test_markdown_render.py` |
| US4 | `scripts/blog/markdown_render.py`, `templates/blog/partials/block-quote.html`, `block-table.html`, `blog.css`, `tests/test_markdown_render.py` |
| US5 | `tests/test_markdown_render.py`, `scripts/verify_build.py`, `.github/workflows/deploy.yml` |

## Parallel Opportunities

- After Foundational: T005 (`test_highlight.py`) ∥ T008 (`blog.css` tokens) ∥ the T006→T007 `markdown_render.py` chain.
- US3 partials T012 ∥ T013 (different files) before their `markdown_render.py` wiring.
- Polish docs T025 ∥ T026 ∥ T023 (CI) are independent files.

## Implementation Strategy

- **MVP** = Phase 1 + 2 + US1: highlighting live with a safe fallback and security preserved.
- **Increment**: US5's test file grows alongside each story (write the pinning tests as each surface lands), so the suite is green continuously and the verifier extension (T022) closes the loop.
- **Single-file discipline**: the `markdown_render.py`, `highlight.py`, `blog.css`, and `tests/test_markdown_render.py` edits are sequential within each file to avoid conflicts — reflected in the task ordering above.
