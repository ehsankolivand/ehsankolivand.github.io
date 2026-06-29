# Cross-Artifact Analysis (read-only gate) — feature 004

Date: 2026-06-29 · Inputs: spec.md, plan.md, research.md, data-model.md, contracts/{highlighter,code-block,callout-footnote,renderer-tests,verifier}.md, tasks.md, constitution.md (v1.4.0). Autonomous run — Critical/High findings resolved before implementation. No artifact was modified to produce this report (the report file itself is the deliverable).

## A. Requirement → task coverage

| FR | Requirement (short) | Covered by | Status |
|---|---|---|---|
| FR-001 | highlight fenced code → classed spans | T002, T003, T004, T007 | ✅ |
| FR-002 | cover 10 languages + aliases | T003, T004 | ✅ |
| FR-003 | unknown lang → escape-only, never fail | T002, T009 | ✅ |
| FR-004 | preserve security guarantees | T002 (emit), T005, T021 | ✅ |
| FR-005 | deterministic highlighting | T002, T005 | ✅ |
| FR-006 | token CSS in blog.css, existing palette | T008 | ✅ |
| FR-007 | parse info string, no new frontmatter | T006 | ✅ |
| FR-008 | optional filename label | T007, T010 | ✅ |
| FR-009 | optional line-emphasis | T010 | ✅ |
| FR-010 | keep caption behavior (backward compat) | T006, T007, T011 | ✅ |
| FR-011 | copy-friendly, no CLS | T010, T011 | ✅ |
| FR-012 | blockquote refine, no regression | T019, T020 | ✅ |
| FR-013 | harden GFM tables | T018, T020 | ✅ |
| FR-014 | callout block, accessible static | T012, T014 | ✅ |
| FR-015 | unknown callout → graceful | T014, T017 | ✅ |
| FR-016 | footnotes, accessible static | T013, T015 | ✅ |
| FR-017 | footnote determinism + degradation | T015, T017 | ✅ |
| FR-018 | stdlib unittest suite | T001, T005, T009 | ✅ |
| FR-019 | suite coverage matrix | T005, T009, T011, T017, T020, T021 | ✅ |
| FR-020 | run locally + CI before build/verify | T001, T023 | ✅ |
| FR-021 | extend verifier, > 273 checks | T022 | ✅ |
| FR-022 | deterministic, no new dependency | T024 + global constraint | ✅ |
| FR-023 | a11y + design fidelity | T012, T013, T016, T022 | ✅ |

**Coverage: 23/23 FRs (100%) have ≥1 task.** Success Criteria SC-001..011 map to the same tasks plus the verifier (T022) and the determinism check (T024). No task is unmapped to a requirement.

## B. Consistency checks

- ✅ Info-string grammar identical across spec Clarifications Q1, `contracts/code-block.md`, and `data-model.md` §1.
- ✅ Callout (`> [!kind]`) + footnote (`[^id]`/`[^id]:`) syntaxes identical across spec Clarifications Q5/Q6, `contracts/callout-footnote.md`, and `research.md` R6/R7.
- ✅ Language set identical: spec FR-002 (Kotlin/Java/Python/Bash + JSON/YAML/XML-HTML/JS/TS/SQL) ↔ `contracts/highlighter.md` (where "markup" is the canonical name for the XML/HTML tokenizer — see Low-2).
- ✅ Token vocabulary (11 `tok-*`) consistent between `contracts/highlighter.md` and `data-model.md` §2; colors all sourced from the design bundle (plan Principle III reconciliation).
- ✅ Verifier growth target ("> 273") consistent across spec FR-021/SC-005, `contracts/verifier.md`, and tasks T022.
- ✅ "No new dependency / deterministic" consistent across spec FR-022/SC-006, plan Constitution Check II, and `contracts/renderer-tests.md`.
- ✅ Constitution v1.4.0 referenced consistently (spec Overview, plan Constitution Check, research). The plan's Principle III reconciliation matches the v1.4.0 bounded exception wording.
- ✅ Task ordering respects dependencies (Foundational T002–T004 before US1/US2; partials before their wiring; single-file edits sequential).

## C. Code-fact validation (against the current renderer)

Each plan/contract claim was checked against the live `scripts/blog/markdown_render.py` / `verify_build.py` / partials / `seo.py`:

1. ✅ Fenced-code path today sets `caption = info_string` (whole string) — `parse_info_string` (T006) cleanly supersedes it; backward compat for the lone ```` ```bash ```` block holds (becomes highlighted bash, label "bash").
2. ✅ `block-code.html` already exposes `{{CAPTION}}` + `{{CONTENT}}` slots → highlighting needs **no structural partial edit** (CONTENT receives highlighted HTML; CAPTION receives the title-bar label). See Low-1.
3. ✅ Blockquote branch (`if s.startswith(">")`) is the correct insertion point for `> [!kind]` callout detection (before plain-quote rendering).
4. ✅ Heading-anchor allocator uses a post-scoped `used_ids` set + `_alloc_heading_id` → footnote ids can be reserved in the SAME set (contract V-FN2) to guarantee collision-freedom (Low-3).
5. ✅ `render_inline` is a free function → footnote-ref handling requires threading a footnote registry param (data-model §4); confirmed feasible without breaking existing callers (default `None`).
6. ✅ `_TABLE_SEP` regex requires ≥2 columns → single-column tables are currently unrecognized; the split-and-check predicate (T018) fixes this (validates the FR-013 edge case).
7. ✅ `sub_tokens` is single-pass → `{{TOKEN}}` in highlighted code is inert; `esc()` does not touch `{`/`}` so `{{BODY}}` survives as literal text (security preserved by construction).
8. ✅ `seo.py:_common()` links `/blog/assets/blog.css` on every page → new `#blog-root` classes apply with no template change.
9. ✅ `verify_build.py` already imports `markdown_render` and re-derives heading slugs → rendering synthetic fixtures in the verifier (T022) is established precedent (stdlib-only).

## D. Findings

- **Critical**: none.
- **High**: none.
- **Medium**: none.
- **Low-1 (C.2)**: plan §"Project Structure" lists `block-code.html` as EXTENDED, but its existing `{{CAPTION}}`/`{{CONTENT}}` slots suffice. *Resolution*: treat the partial as **unchanged** during implementation unless a language badge is genuinely wanted — fewer edits, stronger fidelity. (No spec/plan edit needed; documented here.)
- **Low-2 (B/A)**: terminology "XML/HTML" (spec) vs "markup" (contracts/highlighter). *Resolution*: `markup` is the canonical tokenizer name covering xml/html/svg/xhtml via the alias map; not a conflict — recorded so the implementer maps `html`→`markup`.
- **Low-3 (C.4)**: theoretical footnote-id vs heading-id collision. *Resolution*: already mandated — reserve `fn-…`/`fnref-…` in the shared `used_ids` set during the footnote pre-pass, before heading allocation (contract V-FN2). Implementer must honor the ordering.
- **Low-4 (research R3)**: `gradle` appears as an alias candidate but maps to an unsupported Groovy grammar. *Resolution*: documented as **fallback** (escape-only), not a false "supported" claim; no over-promise.

## E. Gate result

**PASS.** 100% FR→task coverage; full cross-artifact consistency; every plan/contract claim validated against the live renderer; **zero Critical/High/Medium** findings; four Low findings, all resolved here (no artifact change required). Cleared to commit the pre-implement checkpoint and run `/speckit-implement`.

## Metrics

- Total functional requirements: **23** · Success criteria: **11**
- Total tasks: **26** · Coverage: **100%** (23/23 FRs ≥1 task) · Unmapped tasks: **0**
- Ambiguities: **0** (9 resolved in Clarifications) · Duplications: **0** · Constitution conflicts: **0**
- Critical: **0** · High: **0** · Medium: **0** · Low: **4 (resolved)**
