# Checklist: Design-Fidelity (requirements quality)

**Purpose**: Unit-tests-for-English — validate that the spec + plan are complete, clear, consistent, and measurable for the four ways this feature can go wrong. Not implementation tests.
**Created**: 2026-07-14
**Feature**: [spec.md](../spec.md) · [plan.md](../plan.md)

## Distinctive & Non-Templated (the point of the feature)

- [ ] CHK001 - Is every audited slop tell enumerated with a specific removal AND a concrete replacement (not just "remove it")? [Completeness, plan §D4 / data-model Slop-Tell Ledger]
- [ ] CHK002 - Is a re-audit acceptance oracle defined (which tools, which pass/fail condition) so "non-templated" is measurable, not subjective? [Measurability, Spec §SC-001/SC-002]
- [ ] CHK003 - Are all five fingerprint dimensions (type, spacing/rhythm, colour-accent, component composition, motion) required to actually change, with a per-dimension before→after record? [Completeness, Spec §FR-002/SC-003]
- [ ] CHK004 - Is "one shared fingerprint" defined as a concrete, checkable artifact (the shared token layer) rather than an impression? [Clarity, Spec §FR-003 / contracts/fingerprint-token-layer]
- [ ] CHK005 - Is the boundary between "kill the fake window chrome" and "keep the genuine CLI voice" explicitly drawn so the fix can't over-correct? [Ambiguity, Spec §Clarifications Q4/FR-001]
- [ ] CHK006 - Is the skill-% replacement specified as qualitative tiers with NO new fabricated numbers? [Clarity, Spec §Clarifications Q2/FR-001/FR-007]

## Character Preserved (still the same site)

- [ ] CHK007 - Is "recognizable brand character" enumerated concretely (palette family, 3 fonts, ambient background, mascots, mood) rather than left vague? [Clarity, Spec §FR-005]
- [ ] CHK008 - Is "no new colour system / no new hue" stated as an enforceable invariant (token layer names existing hexes only)? [Measurability, Spec §FR-004 / contracts]
- [ ] CHK009 - Is "no new web font / no new @font-face" stated as an enforceable invariant on BOTH surfaces? [Consistency, Spec §FR-004 / plan Constitution Check]
- [ ] CHK010 - Does the spec bound structural change so the information architecture (section set + order) cannot be altered? [Coverage, Spec §Clarifications Q1/FR-002/FR-007]

## Robots Preserved (the loved part)

- [ ] CHK011 - Is every protected robot + reactive animation on BOTH surfaces inventoried by name/hook so none can be silently dropped? [Completeness, data-model Protected-Robot inventory / Spec §FR-006]
- [ ] CHK012 - Is "reskin-only" defined precisely (present + reactive; may restyle; MUST NOT remove/disable/flatten)? [Clarity, Spec §FR-006]
- [ ] CHK013 - Is the handling of audit findings AGAINST protected elements specified (recorded as sanctioned false positives, not acted on)? [Consistency, Spec §FR-008]
- [ ] CHK014 - Is reveal-on-scroll's dual status (protected AND a flagged tell) resolved unambiguously (re-orchestrate, not remove)? [Conflict, Spec §Clarifications Q5/FR-006]
- [ ] CHK015 - Are reduced-motion and mobile behaviours for the robots required to be preserved (still hidden/neutralised as today)? [Coverage/Edge Case, Spec §Edge Cases/FR-012]

## Guarantees Intact (nothing regresses)

- [ ] CHK016 - Is "blog styling flows only through the generator, no hand-edited generated HTML" stated as a hard, checkable bound? [Clarity, Spec §FR-009 / plan Structure]
- [ ] CHK017 - Are the portfolio's two marker zones required to stay present, correctly paired, AND writable by the build? [Completeness, Spec §FR-010 / contracts surface-change]
- [ ] CHK018 - Is preservation of per-page SEO/GEO + the canonical Person/WebSite @id JSON-LD identity stated, and single `<h1>` per page? [Coverage, Spec §FR-011/SC-007/SC-008]
- [ ] CHK019 - Are the accessibility/CWV requirements measurable (compositor-only motion, prefers-reduced-motion, no CLS) and is "preserved-or-improved" defined (incl. the two named portfolio a11y fixes)? [Measurability, Spec §FR-012/SC-008]
- [ ] CHK020 - Is the definition of done tied to concrete gates (renderer unit tests green + verify_build.py green + NEW in-bounds assertions) rather than a subjective sign-off? [Acceptance Criteria, Spec §FR-014/SC-006]
- [ ] CHK021 - Are the NEW verifier in-bounds assertions enumerated (no new font/colour system; #blog-root scope; marker zones; identity; single h1; robots present) so they are implementable? [Completeness, contracts surface-change §In-bounds guarantees]
- [ ] CHK022 - Is "deterministic + no new runtime/build/CI dependency" stated as a constraint? [Clarity, Spec §FR-013 / plan Technical Context]

## Cross-Artifact Consistency & Assumptions

- [ ] CHK023 - Do the spec FRs, the plan Design Decisions (D1–D6), and the two contracts agree with each other (no decision in one that contradicts another)? [Consistency]
- [ ] CHK024 - Does every plan Design Decision trace to either a shed slop tell or a preserved brand element (rationale present, not decoration)? [Traceability, plan §Design Decisions]
- [ ] CHK025 - Are the documented assumptions (fonts fixed; portfolio edited in source; "through the generator" includes templates+scripts; audit/inventory are authoritative) still valid and non-conflicting with the constitution v1.5.0? [Assumption, Spec §Assumptions]
- [ ] CHK026 - Is the Constitution Check in the plan complete for all of Principles I–VIII (not just the amended III & VII) with a per-principle verdict? [Coverage, plan §Constitution Check]

## Notes
- These validate the WRITING. The runtime oracles (build, tests, verifier, re-audit, robot exercise) live in quickstart.md and are executed during implement/verify, not here.
