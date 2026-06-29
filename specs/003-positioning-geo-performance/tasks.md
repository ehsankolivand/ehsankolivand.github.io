---
description: "Task list for feature 003 — Android-engineer positioning, deep-citability, performance"
---

# Tasks: Android-Engineer Positioning, Deep-Citability & Portfolio Performance

**Input**: Design documents from `specs/003-positioning-geo-performance/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/*

**Tests**: No unit-test framework is introduced (consistent with the project). The single automated
gate is `scripts/verify_build.py`; new assertions are tasks below, not separate test files.

## Format: `[ID] [P?] [Story] Description`

- **[P]** = different file, no dependency on another in-flight task → parallelizable.
- **[Story]** = US1 positioning · US2 taxonomy · US3 anchors · US4 fonts · US5 inherited fixes.
- All `scripts/verify_build.py` edits share one file → sequential among themselves (never [P] together).

---

## Phase 1: Setup

- [ ] T001 Confirm the post-002 baseline: `python scripts/build_blog.py --out _site && python
  scripts/verify_build.py --out _site` → **163 checks, 0 failures** (the bar to grow).

## Phase 2: Foundational (blocking prerequisites)

- [ ] T002 Constitution finalized at **v1.3.0** in `.specify/memory/constitution.md` (Principle VIII
  ratified + stale "I–VII"→"I–VIII" gate fix + Principle VII font exception + fresh Sync Impact
  Report). *(Done in the constitution phase; this records the dependency — the font tasks rely on it.)*
- [ ] T003 [P] Read & confirm the portfolio identity source of truth: `index.html` `Person` JSON-LD
  (`@id`, `jobTitle`, `knowsAbout`, `sameAs`) — the grounded values every emission/assertion mirrors.

**Checkpoint**: governance + grounding source confirmed → story work can begin.

---

## Phase 3: User Story 1 — Positioning as a Senior Android Engineer (P1) 🎯 MVP

**Goal**: every post + the index resolve one canonical Android-engineer identity carrying grounded
skills, so the tooling posts read as an Android engineer's work.

**Independent Test**: build; confirm each post/index author node has `@id == #person`, `jobTitle ==
"Senior Android Engineer"`, and `knowsAbout ==` the portfolio list; confirm no fabricated value.

- [ ] T004 [US1] Add `AUTHOR_KNOWS_ABOUT` to `scripts/blog/config.py` — the portfolio
  `Person.knowsAbout` list **verbatim, same order** (contracts/identity.md). Document it as grounded
  (comment: "=== index.html Person.knowsAbout").
- [ ] T005 [US1] Emit `knowsAbout` in `scripts/blog/seo.py` `_author_node(..., full=True)` (so it lands
  on `BlogPosting.author` for posts and `Blog.author` on the index); leave the lean `full=False` node
  unchanged. (depends on T004)
- [ ] T006 [US1] `scripts/verify_build.py`: parse the portfolio `Person` from `index.html` once
  (tolerant if absent). Assert V-ID1 `AUTHOR_SAMEAS == Person.sameAs`, V-ID2 `AUTHOR_KNOWS_ABOUT ==
  Person.knowsAbout`, V-ID3 `AUTHOR_ROLE == Person.jobTitle`, V-ID4 `PERSON_ID/WEBSITE_ID == Person/
  WebSite @id`, V-ID5 bridge topics present. (depends on T004)
- [ ] T007 [US1] `scripts/verify_build.py`: per post + index, assert V-ID6 `jobTitle`, V-ID7
  `knowsAbout == AUTHOR_KNOWS_ABOUT`, V-ID8 author `@id == PERSON_ID` co-present on the full node.
  (depends on T005, after T006 in the same file)

**Checkpoint**: positioning MVP — identity grounded, unified, verifier-locked.

---

## Phase 4: User Story 2 — Taxonomy readiness & graceful empty categories (P2)

**Goal**: declared empty categories render gracefully and are ready for future Android/architecture
posts.

**Independent Test**: with current content, confirm Compose/Architecture render as valid nav entries +
graceful empty state, no broken markup.

- [ ] T008 [US2] `scripts/verify_build.py`: assert V-CAT1 every declared category (incl. empty Compose/
  Architecture) appears as a `data-cat` nav entry; V-CAT2 empty grid shows the empty-state marker and
  no token leak. (sequential in verify_build.py, after T007)

**Checkpoint**: positioning scaffold is structurally credible and locked.

---

## Phase 5: User Story 3 — Deterministic heading anchors (P3)

**Goal**: every body heading is precisely deep-linkable; invisible; deterministic; unique.

**Independent Test**: build; every `<h2|h3|h4>` has a unique slug `id`; rebuild → byte-identical ids;
the `<h1>` has none.

- [ ] T009 [P] [US3] Add a deterministic heading-slug + per-post uniqueness allocator to
  `scripts/blog/markdown_render.py` (contracts/heading-anchors.md): `heading_slug(text)` (NFKD→ASCII,
  lowercase, non-alnum→`-`, trim) + a post-scoped `seen` allocator with `-1/-2…` suffixes and
  `section-<n>` empty fallback; thread an allocator through `render(...)` so each heading partial gets
  its `ID`. Preserve single-pass token substitution.
- [ ] T010 [P] [US3] Add `id="{{ID}}"` to the heading element in
  `templates/blog/partials/block-h2.html` — no other markup/style change (invisible). (pairs with T009)
- [ ] T011 [US3] `scripts/verify_build.py`: assert V-HA1 every body heading has a non-empty `id`,
  V-HA2 ids unique per page, V-HA3 ids deterministic (re-derive from the post body headings and match),
  V-HA4 exactly one `<h1>` with no anchor id. (depends on T009/T010; sequential in verify_build.py)

**Checkpoint**: posts are section-citable with zero visual change.

---

## Phase 6: User Story 4 — Portfolio font optimization (P3, prove-or-defer)

**Goal**: the highest-traffic page sheds unused font subsets, proven non-visual — or is deferred.

**Independent Test**: page meaningfully smaller; fidelity proof green; byte-identical outside the zone.

- [ ] T012 [US4] In `index.html`, wrap the `@font-face` `<style>` block in
  `<!--PORTFOLIO-FONTS:START-->` / `<!--PORTFOLIO-FONTS:END-->` markers (no byte change to the faces
  yet). (depends on T002)
- [ ] T013 [US4] Snapshot `index.html` → `assets/portfolio-fonts/index.baseline.html` (recoverable
  original; ensure the path is NOT served — not in `ROOT_COPY_ALLOWLIST`, not a copied asset tree).
  (depends on T012)
- [ ] T014 [US4] `scripts/verify_build.py`: implement the font-fidelity proof (V-FZ1–6) against the
  baseline — markers, outside-zone byte-equality, retained-faces-verbatim, `cover_cur ⊆ cover_base`,
  glyph-coverage over codepoints(index.html minus base64), byte-savings report. Make it skip-with-NOTE
  when the zone equals the baseline (deferral path stays green). (depends on T013; sequential in
  verify_build.py)
- [ ] T015 [US4] Subset: delete the 32 non-Latin `@font-face` rules (Cyrillic, Cyrillic-ext, Greek,
  Vietnamese) + their `/* label */` comments inside the zone in `index.html`. Then build + verify; if
  V-FZ* fails, **defer** (restore `index.html` from the baseline) and record the reason. (depends on
  T014 — the proof must exist before the cut so it gates the cut)

**Checkpoint**: portfolio lighter and proven, or cleanly deferred.

---

## Phase 7: User Story 5 — Inherited 002 gaps & quality-gate hardening (P4)

**Goal**: identity exactness, author/locale + article-tag coverage, and status hygiene — all locked.

**Independent Test**: verifier fails on sameAs/locale/tag divergence; no implemented spec labeled
pre-implementation.

- [ ] T016 [US5] `scripts/verify_build.py`: assert V-LC1 `<meta name="author">==AUTHOR_NAME`, V-LC2
  `inLanguage==LOCALE` (posts + index `Blog`), V-LC3 `og:locale==OG_LOCALE` on every page. (sequential
  in verify_build.py)
- [ ] T017 [US5] `scripts/verify_build.py`: assert V-TAG1 keywords-contains-every-tag, V-TAG2 one
  `article:tag` per tag, V-TAG3 `BlogPosting.keywords` contains every tag — for each tagged post.
  (sequential in verify_build.py)
- [ ] T018 [P] [US5] Set `specs/001-obsidian-blog/spec.md` Status `Draft → Implemented` and
  `specs/002-seo-geo-publish/spec.md` Status `Ready for Planning → Implemented` (add a one-line shipped
  note). (independent file)
- [ ] T019 [P] [US5] Set this spec's Status to reflect progress (`Draft → Implemented` at the end).
  (independent file)

**Checkpoint**: inherited gaps closed; identity durable.

---

## Phase 8: Polish & validation

- [ ] T020 Full build + verify: `python scripts/build_blog.py --out _site && python
  scripts/verify_build.py --out _site` → **0 failures, checks > 163**. Iterate to green.
- [ ] T021 Determinism check: build twice to two dirs and diff (`_site` vs `_site2`) → byte-identical
  (heading ids stable, no `today()`).
- [ ] T022 Portfolio integrity: confirm `_site/index.html` byte-identical to repo `index.html` outside
  the Field-notes region (existing check) AND repo `index.html` byte-identical to the baseline outside
  the `PORTFOLIO-FONTS` zone (new check). Confirm `assets/portfolio-fonts/` is not in `_site`.
- [ ] T023 Update `PROJECT_CONTEXT.md` (positioning/identity, anchors, font outcome landed/deferred,
  expanded verifier + new count, constitution v1.3.0, 003 folder, resolved inherited gaps).
- [ ] T024 Update `CLAUDE.md` active-feature pointer to 003 (managed agent-context).

---

## Dependencies & order

- **Setup (T001)** → **Foundational (T002–T003)** → stories.
- **US1 (T004–T007)**: T004→T005, T004→T006, T005/T006→T007. MVP; do first.
- **US2 (T008)**: after US1 verifier block (same file).
- **US3 (T009–T011)**: T009+T010 parallel (different files), then T011.
- **US4 (T012–T015)**: T012→T013→T014→T015, strictly ordered (proof before cut; prove-or-defer).
- **US5 (T016–T019)**: T016/T017 sequential in verify_build.py; T018/T019 parallel (separate files).
- **Polish (T020–T024)**: after all stories.

## Parallel opportunities

- T009 (`markdown_render.py`) ∥ T010 (`block-h2.html`) — different files.
- T018 (`specs/001`,`specs/002`) ∥ T019 (`specs/003`) ∥ T009/T010 — all different files.
- All `verify_build.py` tasks (T006, T007, T008, T011, T014, T016, T017) are the **same file** →
  sequential; batch them into one coherent editing pass for efficiency.

## Story → primary files

| Story | Files |
|---|---|
| US1 | `scripts/blog/config.py`, `scripts/blog/seo.py`, `scripts/verify_build.py` |
| US2 | `scripts/verify_build.py` |
| US3 | `scripts/blog/markdown_render.py`, `templates/blog/partials/block-h2.html`, `scripts/verify_build.py` |
| US4 | `index.html`, `assets/portfolio-fonts/index.baseline.html`, `scripts/verify_build.py` |
| US5 | `scripts/verify_build.py`, `specs/001…/spec.md`, `specs/002…/spec.md`, `specs/003…/spec.md` |
| Polish | `PROJECT_CONTEXT.md`, `CLAUDE.md`, build/verify |
