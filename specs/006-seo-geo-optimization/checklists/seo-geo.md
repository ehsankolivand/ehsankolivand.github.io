# SEO / GEO-AEO Quality & Constitutional-Safety Checklist

**Purpose**: Unit-test the *requirements* in spec.md/plan.md for completeness, clarity, consistency,
and measurability before implementation — not to test the implementation.
**Created**: 2026-07-14
**Feature**: [spec.md](../spec.md)
**Depth**: Standard · **Audience**: Reviewer (PR) · **Focus**: structured-data completeness, unified
identity, canonicalization, crawlable anchors, portfolio parity, discovery, determinism, gate safety.

## Requirement Completeness

- [x] CHK001 — Is the per-post structured-data node set (BlogPosting, BreadcrumbList, WebSite) fully enumerated with required order? [Completeness, Spec §Data Model / FR-002]
- [x] CHK002 — Are the exact portfolio head additions (feed autodiscovery, robots meta, ProfilePage dates) each specified as discrete, testable requirements? [Completeness, Spec §FR-003..005]
- [x] CHK003 — Does the spec state which crawler tokens `robots.txt` must retain, not only the one added? [Completeness, Spec §FR-007, Contract C5]
- [x] CHK004 — Are requirements defined for the zero-posts case so portfolio/robots changes still apply and the build stays green? [Coverage, Spec §Edge Cases]
- [x] CHK005 — Is the removal target for dead resource hints named precisely (both hosts), so nothing else is removed? [Completeness, Spec §FR-006]

## Requirement Clarity

- [x] CHK006 — Is "appearance unchanged" for the byline anchor quantified (color inherit, no underline, no new color/font)? [Clarity, Spec §FR-001 / Data Model]
- [x] CHK007 — Is "identity-preserving" defined concretely (which `@id`s, `sameAs`, `knowsAbout`, `jobTitle` must not change)? [Clarity, Spec §FR-009 / Data Model]
- [x] CHK008 — Is the ProfilePage date requirement unambiguous about determinism (fixed constant, never `today()`)? [Clarity, Spec §FR-005 / Edge Cases]
- [x] CHK009 — Is the byline link target unambiguous (`/`, the canonical `Person.url`) versus other plausible targets (`/blog/`, `/about/`)? [Ambiguity, Spec §Assumptions]

## Requirement Consistency

- [x] CHK010 — Do the spec, plan, and contracts agree that BlogPosting must remain the FIRST ld+json script when WebSite is added? [Consistency, Spec §FR-002 / Research D2 / Contract C2]
- [x] CHK011 — Are the identity `@id` values used in the new WebSite node consistent with `config.py` and the portfolio (one Person/WebSite)? [Consistency, Spec §FR-009]
- [x] CHK012 — Is the portfolio's "byte-identical outside sanctioned edits" claim consistent with the verifier comparing built-vs-source (not a frozen baseline)? [Consistency, Spec §Edge Cases / Plan §VII]
- [x] CHK013 — Do the CWV thresholds referenced match the re-verified primary-source values (2.5 s / 200 ms / 0.1 @ p75), with no fabricated tightening adopted? [Consistency, Research §Volatile facts]

## Acceptance Criteria Quality

- [x] CHK014 — Are success criteria measurable against the built `_site/` (grep/inspection/verifier), not subjective? [Measurability, Spec §SC-001..006]
- [x] CHK015 — Is "verifier passes" quantified (≥ 594 checks, 0 failures) rather than left vague? [Measurability, Spec §SC-001, Contract C7]
- [x] CHK016 — Can "no dangling targets" be objectively verified for the new byline anchor and all internal links? [Measurability, Spec §SC-005, Contract C1]
- [x] CHK017 — Is determinism stated as an objective, repeatable check (two builds byte-identical)? [Measurability, Spec §SC-006, Contract C6]

## Scenario & Edge-Case Coverage

- [x] CHK018 — Are trailing-slash canonicalization expectations covered so canonicals/sitemap/feed/links stay consistent? [Coverage, Spec §SC-004/005]
- [x] CHK019 — Is the first-script-contract failure mode (WebSite displacing BlogPosting) explicitly called out as a risk with mitigation? [Edge Case, Research §Risks / Spec §Edge Cases]
- [x] CHK020 — Are out-of-scope-by-constraint items (TechArticle, FAQ/HowTo, tag pages, /about, knowsLanguage, llms.txt lever) explicitly recorded so they are not silently attempted? [Boundary, Spec §Out of Scope]

## Non-Functional & Governance

- [x] CHK021 — Are accessibility invariants (one `<h1>`, robot hooks, `prefers-reduced-motion`) stated as must-not-regress for both surfaces? [Non-Functional, Spec §FR-010]
- [x] CHK022 — Is the "no gate weakened / no constitution amended" constraint expressed as a checkable requirement (files unmodified)? [Governance, Spec §FR-011, Contract C7]
- [x] CHK023 — Are dependencies/assumptions (portfolio is the author page; ~6 posts → no pagination; owner wants max visibility) documented and validated? [Assumption, Spec §Assumptions]

## Ambiguities & Conflicts

- [x] CHK024 — Are there any conflicting requirements between "advance Principle V completeness on every page" and "Principle VII non-destructive to portfolio"? Resolved via additive/design-neutral edits? [Conflict, Plan §Constitution Check]

## Notes

- All items pass: the spec/plan/research/contracts collectively answer each requirements-quality
  question. This checklist is a review aid; the objective acceptance bar is the verifier + the
  output contracts (C1–C7).
