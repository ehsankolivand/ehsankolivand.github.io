# Cross-Artifact Analysis (read-only gate) — feature 003

Date: 2026-06-29 · Inputs: spec.md, plan.md, research.md, data-model.md, contracts/*, tasks.md,
constitution.md (v1.3.0). Autonomous run — Critical/High findings resolved before implementation.

## A. Requirement → task coverage (every FR has ≥1 task; every task traces to an FR)

| FR | Covered by | Status |
|---|---|---|
| FR-001 one canonical `@id` | T005 emit, T006/T007 verify | ✅ |
| FR-002 grounded jobTitle+skills | T004, T005, T006, T007 | ✅ |
| FR-003 tooling framed as Android skill | T004 (bridge topics), T006 (V-ID5) | ✅ |
| FR-004 `sameAs` exact | T006 (V-ID1) | ✅ |
| FR-005 no fabricated content | grounding (T004 verbatim + T006 asserts); no post-adding task exists | ✅ |
| FR-006 empty categories graceful | T008 | ✅ |
| FR-007 future post flows in | existing data-driven pipeline (proven by 001/002) + T008 nav assertion | ✅ (architectural) |
| FR-008 valid while empty | T008 | ✅ |
| FR-009 unique heading ids | T009, T011 | ✅ |
| FR-010 byte-stable ids | T009 (deterministic), T011 (V-HA3), T021 (double-build diff) | ✅ |
| FR-011 static/invisible/one-h1 | T009, T010, T011 (V-HA4) | ✅ |
| FR-012 lighter page, no dep, no visual | T012–T015 | ✅ |
| FR-013 zone + baseline + outside byte-identical | T012, T013, T014 (V-FZ2) | ✅ |
| FR-014 fidelity proof + prove-or-defer | T014, T015 | ✅ |
| FR-015 constitution finalized + amendment | T002 (done in constitution phase) | ✅ |
| FR-016 status hygiene | T018, T019 | ✅ |
| FR-017 verifier grows + all invariants | T006–T008, T011, T014, T016, T017, T020 | ✅ |
| FR-018 deterministic/static/no dep/no client | inherent + T021 | ✅ |

All 10 Success Criteria map to the above (SC-010 verified by T020: checks > 163).

## B. Consistency checks

- **Terminology**: `knowsAbout`, `AUTHOR_KNOWS_ABOUT`, `#person`/`PERSON_ID`, `PORTFOLIO-FONTS`,
  `prove-or-defer`, "Senior Android Engineer" used identically across spec/plan/contracts/tasks. ✅
- **Constitution alignment**: plan Constitution Check covers all **8** principles (PASS); the font
  change is sanctioned by the v1.3.0 Principle VII exception 2 and justified by VI; no principle
  weakened. The Governance gate now reads "Principles I–VIII" (corrected). ✅
- **Grounding**: every asserted identity value (jobTitle, knowsAbout list, sameAs) is required to equal
  the portfolio `index.html` values; verifier V-ID1–4 lock equality. No fabricated capability. ✅
- **No contradictions**: spec (what/why) ↔ plan/contracts (how) consistent; no duplicate/conflicting
  requirements; out-of-scope items (no posts, no backend, no RTL, no redesign) consistent everywhere. ✅

## C. Code-fact validation (confirmed against the current repo)

1. `seo.py` emits `Blog.author` with `full=True` (line 208) and post `BlogPosting.author` with
   `full=True` (line 141) → adding `knowsAbout` to the full node covers **both** post and index. ✅
2. `templates/blog/partials/block-h2.html` is referenced **only** by `markdown_render.py:289` → adding
   `id="{{ID}}"` is isolated; no other surface affected. The renderer must pass `ID` whenever the
   template carries `{{ID}}` (else the token-leak check fails) → T009+T010 land together. ✅
3. The heading-id allocator can be **local to `render()`** (one call = one post body) → per-post
   uniqueness/determinism with **no signature change** and `render.py` untouched (matches plan's
   files-touched list, which omits render.py for US3). ✅
4. `.gitignore` ignores `research/`,`readme.html`,`_site/`,`__pycache__` — **not** a top-level
   `assets/` → the font baseline `assets/portfolio-fonts/index.baseline.html` **will be committed**. ✅
5. `build_blog.py` copies only `templates/blog/assets` + `content/blog/assets` + `ROOT_COPY_ALLOWLIST`
   → a top-level `assets/` is **not** deployed → the baseline never ships to `_site`. ✅

## D. Findings

- **Critical**: none.
- **High**: none.
- **Medium**: none.
- **Low-1 (FR-007 coverage)**: No build-time task adds a throwaway post to positively prove "a future
  post flows into every surface." *Resolution*: this is an Independent Test (US2), satisfied by the
  existing data-driven pipeline already proven by features 001/002 (adding a note regenerates all
  surfaces); T008 locks the empty-category nav path. No new task needed; documented.
- **Low-2 (baseline repo size)**: committing the full `index.baseline.html` (~1.08 MB) grows the repo
  by ~0.76 MB net (index.html itself shrinks ~0.32 MB). *Resolution*: accepted — it is the rigorous,
  self-contained way to satisfy both "original recoverable" and "outside-zone byte-equality proof"
  offline; a zone-only baseline could not prove outside-zone integrity. Documented in research R4.
- **Low-3 (V-HA3 determinism assertion)**: full allocator replay in the verifier is heavy.
  *Resolution*: V-HA3 re-derives each heading's base slug from its own visible text and asserts the id
  is `base` or `base-<n>` or `section-<n>`, plus global uniqueness; byte-stability is additionally
  proven by the T021 double-build diff. Sufficient and lightweight; documented in contracts/verifier.

## E. Gate result

**PASS.** Coverage complete, no contradictions, constitution-aligned, code facts verified. No Critical
or High items to resolve. Cleared to commit the pre-implement checkpoint and run `/speckit-implement`.
