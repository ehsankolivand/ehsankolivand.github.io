# Requirements Quality Checklist: SEO + GEO + Accessibility + Performance + Publishing

**Purpose**: "Unit tests for the requirements" — validate that the spec's requirements for
best-in-class SEO/GEO, accessibility, Core Web Vitals, and one-commit publishing are complete,
clear, consistent, and measurable before implementation.
**Created**: 2026-06-29
**Feature**: [spec.md](../spec.md)

**Depth**: Standard · **Audience**: Reviewer (PR) · **Focus**: SEO/GEO/a11y/perf/publishing quality

## Requirement Completeness

- [x] CHK001 Are all required per-page metadata fields enumerated (title, description, canonical, OG incl. image dimensions + alt, Twitter incl. image alt, author, language, locale, keywords)? [Completeness, Spec §FR-011, §FR-012, §FR-013]
- [x] CHK002 Are the structured-data entities and their required fields enumerated for both page types (article + breadcrumb on posts; blog + website + breadcrumb on index)? [Completeness, Spec §FR-015, §FR-016]
- [x] CHK003 Is the social/structured-data image fallback specified for code-cover posts (default image + its dimensions + alt)? [Completeness, Spec §FR-012, Clarifications]
- [x] CHK004 Are the GEO machine-readable surfaces enumerated (Atom feed, llms.txt) with their required contents (per-post title, URL, dates, summary)? [Completeness, Spec §FR-019, §FR-021]
- [x] CHK005 Is feed autodiscovery specified, and the set of pages that must advertise the feed? [Completeness, Spec §FR-020]
- [x] CHK006 Are accessibility requirements specified (one h1, landmarks, alt text, decorative-hidden, keyboard, contrast, reduced-motion)? [Completeness, Spec §FR-022, §FR-024]
- [x] CHK007 Are the derived artifacts that must regenerate on publish exhaustively listed? [Completeness, Spec §FR-002]
- [x] CHK008 Is the verifier's expanded coverage scope stated (what new invariants it must assert)? [Completeness, Spec §FR-025]

## Requirement Clarity

- [x] CHK009 Is "machine-readable form" for on-page dates clarified to a concrete, unambiguous mechanism? [Clarity, Spec §FR-022, Clarifications — semantic time element]
- [x] CHK010 Is the unified-identity requirement unambiguous about how the blog references the portfolio identity (one stable identifier for Person and WebSite)? [Clarity, Spec §FR-017]
- [x] CHK011 Are sitemap `lastmod`, canonical, and the homepage-date floor rules stated unambiguously and deterministically? [Clarity, Spec §FR-007, §FR-008, §FR-005]
- [x] CHK012 Is the committed-homepage-region end state unambiguous (post-link-free fallback, build-regenerated for deploy)? [Clarity, Spec §FR-003, Clarifications]
- [x] CHK013 Is the feed-level "updated" value defined deterministically (derived from post dates, never current date)? [Clarity, Spec §FR-019, §FR-005]

## Requirement Consistency

- [x] CHK014 Do the "all content static pre-JS" requirement (§FR-006) and the existing progressive-enhancement JS coexist without conflict? [Consistency, Spec §FR-006]
- [x] CHK015 Is author/site identity consistent across metadata, structured data, feed, and llms.txt (one name, one URL, one identifier)? [Consistency, Spec §FR-014, §FR-017]
- [x] CHK016 Do the "single-commit publish" (§FR-001) and "non-destructive to portfolio" (§FR-004) requirements align given the homepage region is regenerated only in the build output? [Consistency, Spec §FR-001, §FR-004]
- [x] CHK017 Are the two scope exclusions (no SearchAction, no Twitter handle) stated consistently as requirements so they are not implemented by mistake? [Consistency, Spec §FR-018, Assumptions, Clarifications]

## Acceptance Criteria Quality (Measurability)

- [x] CHK018 Can "single-commit publish with all derived surfaces updated" be objectively measured? [Measurability, Spec §SC-001]
- [x] CHK019 Can "zero dangling internal links in committed source and built pages" be objectively verified? [Measurability, Spec §SC-002]
- [x] CHK020 Can structured-data validity and metadata uniqueness be objectively measured (zero errors / 100% unique)? [Measurability, Spec §SC-003]
- [x] CHK021 Can feed/llms.txt completeness (100% of posts, accurate dates) be objectively verified? [Measurability, Spec §SC-004]
- [x] CHK022 Can "content present before scripts run", "one h1 + no CLS", and "byte-identical portfolio outside region" each be objectively verified? [Measurability, Spec §SC-005, §SC-006, §SC-007]
- [x] CHK023 Is determinism given a verifiable acceptance check (byte-identical repeat builds)? [Measurability, Spec §SC-008]

## Scenario & Edge-Case Coverage

- [x] CHK024 Are requirements defined for the empty-blog state across feed, llms.txt, sitemap, and homepage region? [Coverage, Spec §Edge Cases]
- [x] CHK025 Is draft exclusion from every derived surface (incl. feed + llms.txt) specified? [Coverage, Spec §Edge Cases — added this pass]
- [x] CHK026 Is the image-cover vs code-cover branch covered for social/structured-data image metadata? [Coverage, Spec §Edge Cases, §FR-012]
- [x] CHK027 Is behavior specified when the homepage lacks the managed markers or is absent (build + verifier tolerance)? [Coverage, Spec §Edge Cases]
- [x] CHK028 Is unresolved/related-link and date-consistency (updated ≥ published) behavior covered? [Coverage, Spec §Edge Cases]

## Non-Functional Requirements

- [x] CHK029 Are Core Web Vitals requirements specified (intrinsic image dimensions / no CLS, font preloads)? [Non-Functional, Spec §FR-023]
- [x] CHK030 Is "no accessibility or CWV regression against the current build" stated as a measurable constraint? [Non-Functional, Spec §FR-024, §SC-006]

## Dependencies & Assumptions

- [x] CHK031 Are platform constraints (GitHub Pages only, no backend, no new runtime dependency) documented and used to justify the scope exclusions? [Assumption/Dependency, Spec §Assumptions, §FR-018]
- [x] CHK032 Is the reuse of the portfolio's existing identity graph (Person/WebSite) documented as the source of the unified identity? [Dependency, Spec §FR-017, Assumptions]

## Notes

- Result: **32/32 items passing** after a one-pass remediation.
- One genuine requirement-quality gap was surfaced and fixed in `spec.md` during this pass:
  - **CHK025** — draft exclusion from the *new* surfaces (feed, llms.txt) was implied by "every
    published post" but not stated; added explicitly to **Edge Cases** so no unpublished content
    can leak into a machine-readable surface.
- CHK009 (machine-readable dates) and CHK017 (scope exclusions) were confirmed clear by the
  Clarifications section; they stay at what/why altitude in the spec with the concrete mechanism in
  `plan.md`/`contracts/`, which is correct separation.
- No CRITICAL or HIGH gaps. The spec is ready for `/speckit-tasks` and implementation.
