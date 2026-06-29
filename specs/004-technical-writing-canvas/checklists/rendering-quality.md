# Rendering-Quality Checklist: Technical-Writing Canvas — "Unit Tests for English"

**Purpose**: Validate that the spec + plan + contracts unambiguously, completely, and testably cover the five threads (syntax highlighting + safety, richer code blocks, callouts + footnotes, quote/table upgrade + hardening, renderer tests + verifier). Each item is a quality gate on the *requirements*, not the implementation. Checked items passed review; each cites where it is satisfied.
**Created**: 2026-06-29
**Feature**: [spec.md](../spec.md)

## Thread 1 — Syntax highlighting + safety

- [x] CHK001 — Are the highlighted token KINDS explicitly enumerated as a closed vocabulary? [Completeness] (contracts/highlighter.md "Token vocabulary", FR-001) ✔
- [x] CHK002 — Is "deterministic" defined operationally (ordered-alternation, no `today()`/network/randomness, byte-identical output)? [Clarity] (research R1, FR-005, contracts/highlighter.md V-HL6) ✔
- [x] CHK003 — Is the unknown-language behavior specified as escape-only AND "never fails the build"? [Edge Case] (FR-003, contracts/highlighter.md V-HL5) ✔
- [x] CHK004 — Are the security guarantees stated as testable invariants (escape-exactly-once, closed class set, no breakout, no token-injection)? [Measurability] (FR-004, contracts/highlighter.md V-HL1..V-HL4) ✔
- [x] CHK005 — Is "covered languages" quantified (the explicit 10 + alias map), rather than left as "the languages used"? [Clarity] (FR-002, research R3, contracts/highlighter.md) ✔
- [x] CHK006 — Is the no-new-dependency constraint stated for the highlighter (vendored stdlib, not a library/browser highlighter)? [Consistency] (FR-001/022, plan Constitution Check II) ✔
- [x] CHK007 — Is the design-fidelity bound on token colors specified (existing palette only, no new font/color system)? [Consistency] (FR-006, plan Principle III reconciliation, Constitution v1.4.0) ✔

## Thread 2 — Richer code blocks (filename / line-emphasis / backward-compat)

- [x] CHK008 — Is the info-string grammar specified unambiguously (language vs. attrs vs. legacy caption, with a decision rule)? [Clarity] (contracts/code-block.md grammar + examples, Clarifications Q1) ✔
- [x] CHK009 — Is the title-bar label precedence explicitly ordered (filename → caption → language → empty)? [Completeness] (contracts/code-block.md, Clarifications Q2, FR-008) ✔
- [x] CHK010 — Is line-emphasis input format defined (`{1,3-5}`, 1-based) and out-of-range handling stated? [Edge Case] (FR-009, contracts/code-block.md V-CB2) ✔
- [x] CHK011 — Is backward compatibility for the existing ```` ```bash ```` block an explicit, testable requirement? [Coverage] (FR-010, US2 scenario 3, contracts/code-block.md V-CB6) ✔
- [x] CHK012 — Is copy-friendliness specified measurably (clipboard == source, newlines preserved, no chrome text) including the line-emphasis case? [Measurability] (FR-011, SC-008, research R5) ✔
- [x] CHK013 — Is the "no new frontmatter" constraint explicit so richness can't leak into authoring metadata? [Consistency] (FR-007, plan Constitution Check IV) ✔

## Thread 3 — Callouts + footnotes (accessibility / degradation / determinism)

- [x] CHK014 — Is the callout syntax specified as Obsidian-native and the kind set + synonym mapping enumerated? [Completeness] (contracts/callout-footnote.md, Clarifications Q5, FR-014) ✔
- [x] CHK015 — Is graceful degradation for an unknown callout kind specified (→ note / plain blockquote, no build failure)? [Edge Case] (FR-015, contracts/callout-footnote.md V-CO2) ✔
- [x] CHK016 — Are callout accessibility requirements concrete (role, aria-label, aria-hidden icon, no client JS)? [Non-Functional] (FR-014/023, contracts/callout-footnote.md V-CO1/V-CO3) ✔
- [x] CHK017 — Is the footnote syntax + placement + back-reference behavior fully specified? [Completeness] (contracts/callout-footnote.md, Clarifications Q6, FR-016) ✔
- [x] CHK018 — Is footnote id determinism + collision-freedom (shared `used_ids` with headings) stated as a testable invariant? [Measurability] (FR-017, contracts/callout-footnote.md V-FN2) ✔
- [x] CHK019 — Are the degenerate footnote cases (undefined ref → literal; unreferenced def → omitted; no dangling 404 anchor) specified? [Edge Case] (FR-017, contracts/callout-footnote.md V-FN3, Principle VIII) ✔
- [x] CHK020 — Are footnote refs/back-refs required to be real, keyboard-focusable anchors with DPUB-ARIA roles? [Non-Functional] (FR-016/023, contracts/callout-footnote.md V-FN4) ✔

## Thread 4 — Blockquote + table upgrade/harden (no regression)

- [x] CHK021 — Are the table edge cases enumerated (alignment, empty cells, inline markup, escaped pipes, ragged rows, single column)? [Coverage] (FR-013, US4, research R8, contracts/verifier.md V-VB8) ✔
- [x] CHK022 — Is "no regression" stated as an explicit, testable requirement for existing blockquotes/tables/lists/captions? [Consistency] (FR-012/013, SC-011, contracts/renderer-tests.md) ✔
- [x] CHK023 — Is the blockquote refinement scoped so it cannot restyle chrome or regress inline styles (class layer only)? [Clarity] (FR-012, research R9, plan Principle III reconciliation) ✔
- [x] CHK024 — Is the callout-vs-blockquote disambiguation order specified (callout detected before plain blockquote)? [Consistency] (research R6/R9, contracts/callout-footnote.md) ✔

## Thread 5 — Renderer tests + verifier + dependency/determinism/fidelity

- [x] CHK025 — Is the test framework + run command + CI placement specified (stdlib `unittest`, `python -m unittest`, before build/verify)? [Completeness] (FR-018/020, contracts/renderer-tests.md, Clarifications Q8) ✔
- [x] CHK026 — Is the test coverage enumerated against each security guarantee and rendered surface (a matrix), not left vague? [Coverage] (FR-019, contracts/renderer-tests.md coverage matrix) ✔
- [x] CHK027 — Is the verifier-growth requirement quantified ("> 273 checks")? [Measurability] (FR-021, SC-005, contracts/verifier.md V-VB-A) ✔
- [x] CHK028 — Is the new-surface verification strategy specified without authoring content (real bash block + synthetic fixtures)? [Clarity] (Clarifications Q7, research R11, contracts/verifier.md) ✔
- [x] CHK029 — Is "no new runtime/build/CI dependency" stated as a hard, checkable constraint? [Non-Functional] (FR-022, SC-006, plan Constitution Check II) ✔
- [x] CHK030 — Is end-to-end determinism (two builds byte-identical) an explicit success criterion covering the new surfaces? [Measurability] (FR-022, SC-003, quickstart determinism check) ✔
- [x] CHK031 — Is the design-fidelity boundary (portfolio byte-identical outside its zones, no new @font-face/color system, body-content-only) stated and verifier-enforced? [Consistency] (FR-023, SC-007, plan Principle III reconciliation, constitution v1.4.0 Verification gate) ✔

## Cross-cutting — clarity, dependencies, assumptions

- [x] CHK032 — Are all open design choices from specify time resolved (no `[NEEDS CLARIFICATION]` remaining)? [Completeness] (spec Clarifications session 2026-06-29; checklists/requirements.md) ✔
- [x] CHK033 — Is each FR traceable to a user story / acceptance scenario and to a contract invariant? [Traceability] (spec FR-001..023 ↔ US1..US5 ↔ contracts V-* ids) ✔
- [x] CHK034 — Are assumptions (real languages, info-string superset, Obsidian syntaxes, stdlib tests) documented and validated against the codebase? [Assumption] (spec Assumptions; research R3/R4/R6/R7/R10) ✔
- [x] CHK035 — Is the security posture stated consistently across spec, plan, and the highlighter/renderer contracts (single-pass substitution, escaping, URL allow-list)? [Consistency] (FR-004, plan Security reconciliation, contracts/highlighter.md + renderer-tests.md) ✔

## Result

**35/35 reviewed and satisfied.** Every thread has enumerated, measurable, traceable requirements with explicit edge-case and graceful-degradation coverage; no `[Gap]`, `[Ambiguity]`, or `[Conflict]` remains open. Ready for `/speckit-tasks` and `/speckit-analyze`.
