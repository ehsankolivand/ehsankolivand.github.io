# Tasks: Design-Fingerprint Differentiation (Blog + Portfolio)

**Feature**: `005-design-fingerprint` | **Plan**: [plan.md](./plan.md) | **Contracts**: [token-layer](./contracts/fingerprint-token-layer.md) · [surface-change](./contracts/surface-change-contract.md)

**Story map** (all P1, delivered together but tagged by what each task serves): **[US1]** distinctive & non-templated · **[US2]** character + robots preserved · **[US3]** functional guarantees intact.

`[P]` = parallelizable (different files, no incomplete dependency). Paths are repo-relative.

---

## Phase 1 — Foundation: shared token layer (BLOCKS all of Phase 2 & 3)

- [ ] T001 [US1] Add the shared token layer (colour/type/space/motion tokens from [contracts/fingerprint-token-layer.md](./contracts/fingerprint-token-layer.md)) to `templates/blog/assets/blog.css`, declared under `#blog-root` (colours name existing hexes only — no new hue/@font-face). Acceptance: `--paper/--ink/--signal/--sand/--sem-*/--space-*/--text-*/--ease-*/--dur-*` all defined; existing `@font-face` block byte-unchanged.
- [ ] T002 [US1] Add the IDENTICAL token layer to the portfolio `index.html` `<style>` block under `#ek-root` (same names/values as T001). Acceptance: token names+values match T001 exactly (the one-shared-fingerprint proof, FR-003); no marker-zone block touched.

## Phase 2 — Blog surface (through the generator ONLY; no hand-edited generated HTML)

### 2a. Stylesheet (depends on T001)
- [ ] T003 [US1] In `templates/blog/assets/blog.css` add fingerprint classes referencing tokens: editorial-index rows, typographic code frame + line-emphasis, callout field, hanging quote, table (tabular-nums + warm zebra, no vertical borders), hairline dividers + green square anchor, gutter-rail, pressed-ink inset surfaces. Acceptance: classes exist, all colours via `var(--…)`, scoped `#blog-root`.
- [ ] T004 [US3] In `blog.css` fix the audited a11y/CWV items: lift `.tok-comment` + caption tokens to ≥4.5:1; `overflow-x: clip` on `#blog-root`; keep `prefers-reduced-motion` + focus-ring rules. Acceptance: no text token under 4.5:1; `clip` not `hidden`.

### 2b. Templates (depend on T001/T003; different files → [P])
- [ ] T005 [P] [US1] `templates/blog/index.html`: hero solid-ink Space Grotesk (kill gradient "Notes"), one motivated mono shell-prompt eyebrow (drop "New ·" pill); card grid → editorial-index rows; footer → colophon. Acceptance: no `background-clip:text`; `{{FEATURED}}/{{GRID}}` slots intact; section set/order unchanged.
- [ ] T006 [P] [US2] `templates/blog/base.html`: masthead nav (hairline, functional mono, green active), gutter-rail scaffold, ambient-mesh opacity reduced; **tin-toy reskin** of scroll-reactor + grad-cap (desaturated sand shell + green LED eye, hairline speech tag). Acceptance: `data-reactor*`/`data-cursor*`/`data-ambient` hooks + `{{HEAD}}/{{MAIN}}/{{NAV_ITEMS}}` intact.
- [ ] T007 [P] [US2] `templates/blog/article.html`: gutter rail for date/footnote ticks; robot author-avatar tin-toy reskin; signature → colophon; type rhythm. Acceptance: single `<h1>`; `{{COVER}}/{{BODY}}/{{MORE_NOTES_SECTION}}` slots + avatar intact.

### 2c. Partials (depend on T003; different files → [P])
- [ ] T008 [P] [US1] `templates/blog/partials/block-code.html`: typographic frame (top hairline + mono filename left + language right + bottom hairline); **remove traffic-light dots + title bar**. Acceptance: no dot markup; feature-004 filename/lang/line-emphasis data contract preserved.
- [ ] T009 [P] [US1] `templates/blog/partials/block-callout.html`: warm field + kind-keyed 1–2px left rule + single-stroke inline **SVG** kind-mark (`aria-hidden`) + text label; drop pill/emoji/glow. Acceptance: kind→colour mapping + accessible label preserved; unknown kind safe-falls-back.
- [ ] T010 [P] [US1] `templates/blog/partials/block-table.html` + `block-quote.html`: tabular-nums + hairline rules (table); hanging sand quote-mark (quote). Acceptance: GFM/blockquote semantics unchanged.
- [ ] T011 [P] [US1] `templates/blog/partials/{grid-card,featured-card,home-notes-section,more-note,more-notes-section}.html`: editorial-index row composition; drop glow dots/pills. Acceptance: post fields + crawlable anchors preserved.
- [ ] T012 [P] [US1] Remaining `templates/blog/partials/block-*.html` (p, list, olist, h2, img*, footnotes): apply typography/rhythm/tokens only. Acceptance: block semantics + escaping unchanged.

### 2d. Generator scripts (depend on partial shapes T008–T012)
- [ ] T013 [US1] `scripts/blog/markdown_render.py`: emit the new callout SVG kind-marks, code-frame markup, table/quote classes; enforce mono-eyebrow discipline. Deterministic; keep escaping + URL allow-list + single-pass substitution; unknown language/kind → safe fallback. Acceptance: renders new markup; no new dependency.
- [ ] T014 [P] [US1] `scripts/blog/highlight.py`: confirm token classes unchanged (colours now via CSS tokens), escape-only fallback intact. Acceptance: no colour literals introduced; class set matches CSS token classes.

### 2e. Blog JS (depends on T003 classes/tokens)
- [ ] T015 [US2] `templates/blog/assets/blog.js`: reveal re-orchestration (one load stagger + section-level draw, not per-element); hover discipline (drop compound 6-property hover → one signal); tin-toy robot params. Acceptance: every robot/cursor/ripple/magnetic/reveal BEHAVIOUR still present + reactive; reduced-motion guards intact; transform/opacity only.

## Phase 3 — Portfolio surface (committed `index.html` source; Principle VII exception 3)

*Depends on T002. Single large file → mostly sequential; grouped by region.*

- [ ] T016 [US1] `index.html` `<style>` (308–375): fingerprint restyle — kill gradient headline styling + glow-on-static + card-in-card; pressed-ink surfaces; `overflow-x: clip`; **lift portfolio caption/muted text contrast to ≥4.5:1** (audit-found low-contrast greys), matching T004 on the blog. Acceptance: no new hue/@font-face; token-driven; no text token under 4.5:1.
- [ ] T017 [US2] `index.html` header/nav (425–437): masthead + hairline, real destinations, green active underline, drop glassy pill; **add distinct `aria-label`** to top + bottom nav (a11y fix). Acceptance: `data-logo` easter-egg hook intact; two navs have unique labels.
- [ ] T018 [US1] `index.html` hero (442–489): solid-ink headline (kill gradient "Kolivand"), content-height (~88vh), curly quotes. Acceptance: single `<h1>` at 450 preserved; no `background-clip:text`.
- [ ] T019 [US1] `index.html` skills (559–698): **kill invented %-bars** → qualitative tiers (Core/Fluent/Familiar) as dot-leader rows/chips, sand labels, green ring on primary; **SVG icons** replace emoji; android mascot tin-toy reskin. Acceptance: no numeric %; real skills unchanged; mascot behaviour intact.
- [ ] T020 [US1] `index.html` work/git-log card (698–912): keep git-log concept, **drop fake terminal window** → typeset changelog (mono hash + tabular date gutter, hairline rows, green `HEAD →`). Acceptance: no traffic-dot/titlebar markup; `LATEST-NOTES` markers (913–941) untouched.
- [ ] T021 [US3] `index.html` contact/footer (943–982): colophon/letter-close + SVG contact icons + curly quotes; **move `<footer>` out of `#sec-contact` into a `contentinfo` landmark** (a11y fix). Acceptance: footer is a landmark; contact links + companion robot preserved.
- [ ] T022 [US2] `index.html` inline JS (1000–1494): reveal re-orchestration + hover discipline + tin-toy robot params. Acceptance: scroll-reactor/chase/logo-easter-egg/walk-stride/cursor/parallax all present + reactive; reduced-motion guards intact.

## Phase 4 — Verifier + tests (after both surfaces exist)

- [ ] T023 [US3] `scripts/verify_build.py`: add in-bounds assertions — (a) no new `@font-face` / no new colour system on either surface; (b) blog fingerprint CSS only under `#blog-root`; (c) both portfolio marker zones present + correctly paired; (d) canonical Person/WebSite `@id` + per-page SEO tags intact; (e) exactly one `<h1>` per page; (f) every protected robot behaviour hook present on both surfaces. Acceptance: verifier passes; new checks fail loudly if a bound breaks.
- [ ] T024 [P] [US3] `tests/`: add/adjust unit tests for changed markup shape (typographic code frame; callout SVG kind-mark; table tabular-nums) while keeping all existing tests green. Acceptance: `python -m unittest discover -s tests` passes.

## Phase 5 — Validation (maps to quickstart + Success Criteria)

- [ ] T025 [US3] Run `python -m unittest discover -s tests` → `python scripts/build_blog.py` → `python scripts/verify_build.py`. Acceptance: all three green (SC-006); `LATEST-NOTES` regenerated (SC-007).
- [ ] T026 [US1] Re-run `hallmark audit templates/blog` + `hallmark audit index.html` and the ui-ux-pro-max checks. Acceptance: no slop-gate failures; every Slop-Tell Ledger item absent; no-emoji/contrast/minimal-glow pass (SC-001/SC-002).
- [ ] T027 [US2] Exercise every robot on both surfaces (scroll speed, hover, cursor, logo-tap) incl. `prefers-reduced-motion` collapse and 320/375/414/768px no-horizontal-scroll. Any design-tool flag against a robot/cursor/mesh/reveal is **recorded as a sanctioned false positive, not acted on** (FR-008). Acceptance: 100% robots present + reactive; reduced-motion settles (SC-005).
- [ ] T028 [US1] Confirm the 5-dimension before→after record (plan §D1–D6) and the shared token layer (T001≡T002). Acceptance: all five dimensions changed on both surfaces; token layers identical (SC-003).

---

## Dependencies
- **T001, T002** (tokens) block everything in their surface.
- Blog: T001→T003/T004→(T005,T006,T007 templates)‖(T008–T012 partials)→T013/T014 scripts; T003→T015 JS.
- Portfolio: T002→T016→(T017–T022).
- **T023/T024** (verifier+tests) require both surfaces done (Phase 2 + 3).
- **T025–T028** (validation) require T023/T024.

## Parallel opportunities
- T005 ‖ T006 ‖ T007 (distinct template files).
- T008 ‖ T009 ‖ T010 ‖ T011 ‖ T012 (distinct partial files).
- T014 ‖ T013 region-wise; T024 ‖ later portfolio polish.
- Phase 2 (blog) and Phase 3 (portfolio) touch disjoint files and can proceed in parallel once T001+T002 land — except both must be done before Phase 4.

## MVP / increment
- **Slice 1 (US1 core):** T001–T003, T005, T008, T009, T013, T016, T018, T019, T020 — sheds the loudest tells (gradient text, fake windows, skill-%). Independently demonstrable.
- **Slice 2 (US2):** T006, T007, T011, T015, T017, T022 — tin-toy reskin + reveal re-orchestration with all robots intact.
- **Slice 3 (US3):** T004, T010, T012, T014, T021, T023, T024 then T025–T028 — guarantees + a11y fixes + verification.
