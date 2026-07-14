# Tasks: SEO / GEO-AEO Optimization Refinement (Portfolio + Blog)

**Feature**: `006-seo-geo-optimization` (work stays on `main`)
**Input**: [spec.md](./spec.md), [plan.md](./plan.md), [research.md](./research.md),
[data-model.md](./data-model.md), [contracts/output-contracts.md](./contracts/output-contracts.md),
[quickstart.md](./quickstart.md)

**Tests**: Light TDD-adjacent coverage added for the two blog changes (spec §Edge Cases calls for
an added unit test on the first-script contract); the 594-check verifier remains the primary gate.

**Conventions**: Tasks run sequentially. `[P]` marks tasks that touch different files and could run
in parallel. `[US#]` maps to the spec's user stories. Every task lists an exact file path.

---

## Phase 1: Setup (baseline confirmation)

- [X] T001 Confirm the green baseline before changes: run `python -m unittest discover -s tests`, `python scripts/build_blog.py --out _site`, and `python scripts/verify_build.py --out _site` and record the check count/0-failures (baseline reference for regression) — commands only, no file change.
- [X] T002 Commit the Spec Kit artifacts (spec.md, plan.md, research.md, data-model.md, contracts/, quickstart.md, checklists/, and the CLAUDE.md marker update) under `specs/006-seo-geo-optimization/` and `CLAUDE.md` before implementation begins.

## Phase 2: Foundational (blocking prerequisites)

*No foundational blockers.* All five changes are independent edits to existing files; the canonical
identity constants in `scripts/blog/config.py` are already equal to the portfolio and are NOT changed
this cycle, so no shared groundwork is required before the user stories.

---

## Phase 3: User Story 1 — Self-contained post entity + real author link (Priority: P1) 🎯 MVP

**Goal**: Every blog post carries the unified single-entity graph and a crawlable byline link to the
author/entity page, so an AI engine citing a single post URL resolves the identity from that page
alone.

**Independent test**: Build; open any `_site/blog/<slug>/index.html`; confirm the byline "Ehsan
Kolivand" is an `<a href="/">` anchor and a `WebSite` JSON-LD node (`@id=#website`,
`publisher=#person`) is present while `BlogPosting` is still the first `ld+json` script; verifier 0
failures. (Contracts C1, C2.)

- [X] T003 [US1] Add a standalone `WebSite` JSON-LD node to each post's `<head>` in `scripts/blog/seo.py` (`head_for_post`): append it AFTER the existing `BlogPosting` (first) and `BreadcrumbList` (second) scripts, with `@id=config.WEBSITE_ID`, `name=config.SITE_NAME`, `url=home`, `publisher={"@id": config.PERSON_ID}` — reusing existing identity constants (no new identity).
- [X] T004 [US1] Make the visible post byline a crawlable anchor in `templates/blog/article.html`: wrap the name text "Ehsan Kolivand" in `<a href="/">` styled to inherit appearance (`color:inherit; text-decoration:none`), keeping the role line and layout unchanged.
- [X] T005 [P] [US1] Add a unit test in `tests/` asserting `seo.head_for_post(...)` output keeps `BlogPosting` as the FIRST `application/ld+json` script AND includes a `WebSite` node whose `@id`==`config.WEBSITE_ID` and `publisher.@id`==`config.PERSON_ID`.
- [X] T006 [US1] Rebuild (`python scripts/build_blog.py --out _site`) and verify (`python scripts/verify_build.py --out _site`); inspect one built post page to confirm C1 + C2 hold and the byline appears visually unchanged.

**Checkpoint**: US1 independently delivers the highest-value GEO + E-E-A-T improvement; verifier green.

---

## Phase 4: User Story 2 — Portfolio head completeness parity (Priority: P2)

**Goal**: The highest-traffic page (portfolio) exposes the same discovery + completeness signals as
blog pages: Atom autodiscovery, a large-image-preview robots directive, and ProfilePage freshness
dates — all additive, design-neutral, identity-preserving.

**Independent test**: Build; open `_site/index.html`; confirm the three additions are present, the
`#person`/`#website` `@id`s + both marker zones + single `<h1>` + robot hooks are intact, and the
portfolio is byte-identical to source outside these additions. (Contract C3, C6.)

- [X] T007 [US2] In portfolio `index.html <head>`, add `<link rel="alternate" type="application/atom+xml" title="Ehsan.kolivand — Field Notes" href="/blog/feed.xml">` (Atom feed autodiscovery), placed with the other head links, without altering any `@id` or marker zone.
- [X] T008 [US2] In portfolio `index.html <head>`, add `<meta name="robots" content="index, follow, max-image-preview:large">`.
- [X] T009 [US2] In the portfolio ProfilePage JSON-LD node in `index.html`, add `"dateCreated"` and `"dateModified"` set to the fixed date `2026-07-14` (deterministic constant; no `today()`), leaving Person/WebSite/ProfilePage `@id`s and all identity fields unchanged.
- [X] T010 [US2] Rebuild + verify; confirm C3 passes and the verifier's portfolio checks (marker zones ×1, single `<h1>`, `#person`/`#website`, robot hooks, byte-identity outside notes region) stay green.

**Checkpoint**: US2 brings the portfolio to per-page completeness parity; verifier green.

---

## Phase 5: User Story 3 — Fast, clean crawl + complete crawler set (Priority: P3)

**Goal**: Remove wasted/leaky connections from the portfolio and welcome the confirmed-live Applebot
crawler.

**Independent test**: Confirm `_site/index.html` has zero references to Google Fonts hosts; confirm
`_site/robots.txt` allows `Applebot`, still declares the sitemap, and retains all prior tokens; no
visual/functional regression. (Contracts C4, C5.)

- [X] T011 [P] [US3] Remove the two dead resource hints from portfolio `index.html <head>`: delete `<link rel="preconnect" href="https://fonts.googleapis.com">` and `<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="">` (nothing loads from these hosts; fonts are self-hosted/inlined).
- [X] T012 [P] [US3] Add an `Applebot` `Allow: /` stanza to `robots.txt`, keeping the `Sitemap:` line and every existing search/AI-citation token (Googlebot, OAI-SearchBot, ChatGPT-User, PerplexityBot, Perplexity-User, Claude-SearchBot, Claude-User, ClaudeBot, GPTBot, Google-Extended).
- [X] T013 [US3] Rebuild + verify; confirm C4 (no Google-Fonts refs in built portfolio) and C5 (Applebot + sitemap in built robots.txt) hold and the verifier stays green.

**Checkpoint**: US3 completes the crawl-hygiene + crawler-completeness improvements.

---

## Phase 6: Polish & Cross-Cutting Verification

- [X] T014 Run the full gate end-to-end: `python -m unittest discover -s tests` → `python scripts/build_blog.py --out _site` → `python scripts/verify_build.py --out _site`; require ≥ 594 checks and 0 failures (SC-001, Contract C7).
- [X] T015 [P] Determinism check: build twice into separate dirs and `diff -r` them; expect no diff (SC-006, Contract C6), then remove the temp dirs.
- [X] T016 [P] Gate-integrity check: `git diff --name-only -- scripts/verify_build.py .specify/memory/constitution.md` must be empty (no gate weakened, no principle amended — Contract C7).
- [X] T017 Delegate an independent JSON-LD/head-meta audit to a clean-context subagent over the built `_site/` (every page's canonical, meta, OG/Twitter, and JSON-LD vs. the briefs; report discrepancies by file); triage findings and fix any real issue in source, keeping final judgment with the implementer.
- [X] T018 Update the requirements/seo-geo checklists' status if any item changed, then commit the verified implementation to `main` with a descriptive message and push (only after tests + build + verifier are all green locally).

---

## Dependencies & Execution Order

- **Phase 1 (Setup)** → **Phase 2 (none)** → **Phase 3 (US1)** → **Phase 4 (US2)** → **Phase 5 (US3)** → **Phase 6 (Polish)**.
- User stories are mutually independent (different files: `seo.py`/`article.html` for US1;
  `index.html` head for US2; `index.html` head + `robots.txt` for US3). US2 and US3 both edit
  `index.html`, so their `index.html` edits are sequential, but each story is independently testable.
- Within US1, T005 (test, different file) is `[P]` with T003/T004.

## Parallel Opportunities

- T005 (unit test) alongside T003/T004.
- T011 (`index.html` hint removal) and T012 (`robots.txt`) touch different files → `[P]`.
- T015 and T016 (independent read-only checks) → `[P]`.

## Implementation Strategy

- **MVP = User Story 1** (self-contained post entity + author link): the highest-leverage GEO/E-E-A-T
  gain and independently shippable.
- Deliver US2 and US3 incrementally; each ends at a green verifier checkpoint.
- Never push a red build to `main`; the final push (T018) happens only after the full local gate is
  green.


---

## Convergence Note (post-implementation)

**Full gate: GREEN** — 111 unit tests (was 107; +4), `build` deterministic (double-build byte-identical),
`verify_build` 594 checks / 0 failures. `verify_build.py` and `constitution.md` unmodified (no gate
weakened, no principle amended).

**Independent audit (T017)** over the built `_site/` returned CLEAN except one LOW cross-page identity
divergence: the shared `#website` `@id` carried two `name` values ("Ehsan Kolivand" on the portfolio
vs. "Ehsan.kolivand — Field Notes" on blog pages). Because that conflicts with the cycle's core goal
(one cleanly-resolvable entity), it was fixed in `scripts/blog/seo.py`: the blog's WebSite-node name
now uses `AUTHOR_NAME`, unifying `#website.name` to "Ehsan Kolivand" across all 8 pages, while the
`Blog` node keeps its "Field Notes" brand. Re-audited by re-running the full gate: still green.

Audit observations left as-is (present + spec-passing, not defects): portfolio `og:type=profile`
(correct for a profile page); some posts reuse a generic `og:image:alt` (content-side, out of scope —
authoring pipeline not touched this cycle).
