# Feature Specification: Design-Fingerprint Differentiation (Blog + Portfolio)

**Feature Branch**: `005-design-fingerprint`

**Created**: 2026-07-14

**Status**: Draft

**Input**: User description: "Make the site distinctive and non-templated on both surfaces (blog + portfolio) while keeping its recognizable character and every functional guarantee — shed the AI-generated/templated look, keep the brand and the robots."

## Clarifications

### Session 2026-07-14

Autonomous run — the five highest-impact ambiguities were resolved by the executor (grounded in the spec, the audit notes, and constitution v1.5.0) and folded into the requirements below.

- Q: How far does the structural/component change go — reorder or replace the macrostructure (sections), or keep the section arc and change only composition? → A: Keep the information architecture and section arc intact (no section added, removed, or reordered on either surface); change only intra- and inter-section composition — vertical rhythm, dividers, grid spans, heading placement, and the composition of cards/quotes/code/callouts, plus deliberate variety between section transitions. (Folded into FR-002, FR-007.)
- Q: The invented skill-percentage bars (gate 46) are removed — replaced with what, under the "no fabricated content" rule? → A: Replace the numeric meters/bars with qualitative, non-fabricated proof — the same real skills grouped as labelled tiers/chips (e.g. "primary", "daily driver", "shipped with"), with NO invented percentages and NO new numbers. (Folded into FR-001, FR-007.)
- Q: Does the portfolio also adopt a named-colour token layer, and how is "one shared fingerprint" made concrete and verifiable? → A: Yes — both surfaces adopt a CSS custom-property token layer that names the SAME existing palette colours and applies the SAME type-scale and spacing-rhythm rules, so the shared fingerprint is a concrete, checkable artifact (same token names/values and rhythm ladder across surfaces). (Folded into FR-003, FR-004, SC-003.)
- Q: The fake terminal/OS window chrome is flagged (code blocks on the blog; the career "git log" card on the portfolio) — is the terminal/CLI motif removed entirely or kept where motivated? → A: Remove the fake window *chrome* (traffic-light dots + mock OS/shell title bars — the off-palette tell), but KEEP the genuine terminal/CLI *motif* where it is motivated and on-brand (a real shell-prompt eyebrow, a typographic code caption/filename bar, the git-log concept), reframed typographically within the palette. The tell is the faked window, not the CLI voice. (Folded into FR-001.)
- Q: Reveal-on-scroll is both a PROTECTED element and a flagged "page never settles" tell — how is that reconciled? → A: It stays (protected) but is re-orchestrated rather than removed: the indiscriminate per-element stagger is reduced to a restrained, section-level entrance (reveal section heads / grouped blocks once, not every paragraph and chip). The mechanism and its identity remain; the "never settles" tell is gone. This is a sanctioned reskin/tuning of a protected behaviour. (Folded into FR-006.)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The site stops looking machine-made (Priority: P1)

A recruiter or fellow engineer lands on the portfolio, then follows a link into the blog. Today the design reads as a familiar, template-derived "dark-tech-portfolio-with-neon-accents" — the kind of look now common enough to feel auto-generated. After this feature, the same visitor perceives a deliberately, distinctively designed site: the specific tells that make it look machine-made are gone, and the two surfaces feel like one hand-made system rather than two colour-swaps of a common template.

**Why this priority**: This is the entire reason for the work. If the site still reads as templated, nothing else matters. It is the one outcome that must ship for the feature to have value.

**Independent Test**: Re-run the same anti-AI-slop audit (hallmark) and design-database anti-pattern check (ui-ux-pro-max) that produced the original punch list, on both surfaces, and confirm the enumerated slop tells no longer appear and no slop-gate fails. Independently, a person who has not seen the notes can be shown before/after and asked "which looks more template-generated?" — the after must not be chosen.

**Acceptance Scenarios**:

1. **Given** the current blog and portfolio, **When** the enumerated slop tells are inspected (gradient-clipped headline text; fake terminal/OS window chrome on code blocks and the career "git log" card; decorative status pills; colour glow on static elements against the dark surface; mono-cap "eyebrow" labels repeated on every section; invented skill-percentage bars; emoji used as icons; a uniform equal-weight card grid; reveal-on-scroll applied to every element), **Then** after the feature none of these tells is present as originally described.
2. **Given** the redesigned surfaces, **When** the hallmark audit is re-run on each, **Then** it reports no slop-gate failures, and the ui-ux-pro-max pre-delivery checks pass.
3. **Given** the blog and the portfolio side by side, **When** their fingerprints are compared (type treatment, spacing rhythm, accent discipline, component composition, motion), **Then** they read as one coherent, differentiated system, and each differs meaningfully from the common template it previously resembled.

---

### User Story 2 - It is still unmistakably the same site (Priority: P1)

A returning visitor who knows the site recognizes it immediately — the dark green/teal world, the voice, and above all the robot mascots are still there and still behave the way they love. The refresh feels like the same identity, better executed — not a rebrand and not a different site.

**Why this priority**: A "distinctive" redesign that discards the brand or the loved robots would fail the brief as badly as one that stays templated. Character preservation is co-equal with User Story 1; both are P1 and both gate the release.

**Independent Test**: Enumerate the brand-identity elements and the robot characters with their reactive animations (from the protected-elements inventory), then verify each is still present and still reacts after the redesign — by loading each surface and exercising scroll, hover, cursor movement, and the logo-tap easter egg, and by confirming the palette family and the three fonts are unchanged.

**Acceptance Scenarios**:

1. **Given** the redesigned portfolio, **When** the visitor scrolls quickly, hovers, moves the cursor, and taps the logo repeatedly, **Then** the scroll-speed "reactor" companion (with its shout speech-bubbles), the android mascot, the chase gag, the walk/stride bots, the cursor/parallax reactions, and the logo-tap easter egg all still play.
2. **Given** the redesigned blog, **When** the visitor scrolls and reads a post, **Then** the scroll-reactor + graduation-cap rider, the hero companion, the robot author-avatar, the magnetic cursor, ripple/magnetic feedback, and reveal-on-scroll are all still present and reactive.
3. **Given** the redesigned surfaces, **When** the brand core is inspected, **Then** the dark green/teal palette family, the three existing fonts, the ambient living background, and the dark-tech-with-warmth mood are all retained (no new web font and no new colour system introduced).
4. **Given** an audit flags a robot or the custom cursor as "decorative without purpose" or a "microinteraction anti-pattern", **Then** that finding is recorded as an intentional, sanctioned exception (a false positive for this project) and the element is kept, not removed.

---

### User Story 3 - Nothing functional regresses (Priority: P1)

The maintainer publishes as before — edit one Obsidian note, commit, push — and the site still builds statically, deploys to GitHub Pages, ranks and is machine-readable, and passes its accessibility and performance bar. The visual refresh changes how the site looks, not how it works.

**Why this priority**: The redesign is explicitly bounded by the project's non-negotiable principles. A fingerprint change that broke SEO, the content pipeline, the marker zones, or accessibility would violate the constitution and is not shippable.

**Independent Test**: Run the existing build, the renderer unit tests, and the definition-of-done verifier; confirm all pass. Confirm the portfolio's two machine-readable marker zones remain present and writable, the per-page SEO/GEO metadata and canonical identity are unchanged, and the accessibility invariants hold.

**Acceptance Scenarios**:

1. **Given** the redesigned generator, **When** the site is built, **Then** the renderer unit test suite and the post-build verifier both pass with no new failures.
2. **Given** the redesigned portfolio, **When** the build assembles the deployed homepage, **Then** the `LATEST-NOTES` region is still regenerated into it and the `PORTFOLIO-FONTS` zone is intact — both marker pairs present and correctly matched.
3. **Given** the redesigned pages, **When** their served HTML is inspected, **Then** each page keeps its full crawlable content, per-page SEO tags, the canonical Person/WebSite JSON-LD identity, exactly one `<h1>`, semantic landmarks, and meaningful/`aria-hidden` treatment; the Atom feed, `llms.txt`, and `sitemap.xml` still enumerate every published post.
4. **Given** blog styling changes, **When** the source of those changes is inspected, **Then** they live only in the generator (templates + `#blog-root`-scoped stylesheet + generator scripts) with no hand-edited generated HTML.

---

### Edge Cases

- **A protected robot is flagged by a design tool.** The audit will call the custom cursor, the reactive robots, the ambient blobs, or the reveal-on-scroll a "tell." Resolution: these are named brand DNA; the finding is a sanctioned false positive and the element stays (reskin-only). The redesign must not "fix" them by removal.
- **A slop-fix would collide with a functional guarantee.** E.g., removing the fake-terminal chrome on code blocks must not change how code content is escaped/rendered; reworking the skill section must not invent or remove real content. Resolution: keep the functional behaviour; change only the fingerprint. If a fix cannot be made without regressing a guarantee, it is reduced or deferred (prove-or-defer), never shipped by weakening a principle.
- **`prefers-reduced-motion` users.** New motion detailing must collapse gracefully; robots and reveals are already hidden/neutralised under reduced motion and must stay that way. No new animation may run for reduced-motion users.
- **Mobile / small screens.** The new component composition must not introduce horizontal scroll or clip the robots' reserved space; existing mobile behaviour (companion hidden, comfortable tap targets) is preserved or improved.
- **The blog writes into the portfolio's `LATEST-NOTES` region after the restyle.** The next build must still find the markers and inject current notes without disturbing the new styling around them.
- **A code-fence language is unknown, a callout kind is unrecognised, or a table is malformed.** The refreshed body-content styling must still degrade to safe, readable output (no build failure), exactly as before.

## Requirements *(mandatory)*

### Functional Requirements

**Differentiation (what must change):**

- **FR-001**: The blog and portfolio MUST shed each enumerated slop tell identified in the audit: gradient-clipped headline text; fake terminal/OS window chrome on code blocks and the career "git log" card; decorative status pills; colour glow applied to static (non-functional) elements on the dark surface; mono-cap "eyebrow" labels repeated on every section; invented skill-percentage bars; emoji used as icons; a uniform equal-weight card grid with no rhythm break; and reveal-on-scroll applied indiscriminately to every element. Two clarified boundaries (Session 2026-07-14): (a) the tell to remove is the faked *window chrome* — traffic-light dots and mock OS/shell title bars — NOT the terminal/CLI voice; a genuine, motivated CLI motif (a real shell-prompt eyebrow, a typographic code caption/filename bar, the git-log concept) is kept and reframed typographically within the palette; (b) the removed skill-percentage bars are replaced with qualitative, non-fabricated proof — the same real skills grouped as labelled tiers/chips ("primary", "daily driver", "shipped with") with NO invented percentages and NO new numbers.
- **FR-002**: The refresh MUST change the design fingerprint across five dimensions — type-pairing & treatment/scale, spacing & vertical rhythm, colour-accent usage & discipline, component structure & composition, and motion & microinteraction detailing — such that each surface is meaningfully distinct from the common template it currently resembles. The component/structure change is bounded to composition: no section is added, removed, or reordered on either surface (the information architecture and section arc are preserved per FR-007); what changes is intra- and inter-section composition — rhythm, dividers, grid spans, heading placement, card/quote/code/callout composition, and deliberate variety between section transitions.
- **FR-003**: The blog and the portfolio MUST end up sharing one coherent, differentiated fingerprint so the two surfaces read as a single hand-made system — made concrete by a shared token layer: the SAME named palette-colour tokens and the SAME type-scale and spacing-rhythm rules applied on both surfaces (same token names/values and rhythm ladder), so the shared fingerprint is a checkable artifact, not a subjective impression.
- **FR-004**: Type changes MUST stay within the three fonts already loaded by the design (no new web font, no new `@font-face`); accent changes MUST stay within the existing palette. A CSS custom-property token layer that NAMES the existing palette colours (and encodes the type-scale/spacing rhythm) is introduced on both surfaces, but it MUST NOT introduce a new colour system or new hues.

**Preservation (what must not change):**

- **FR-005**: The recognizable brand character MUST be preserved: the dark green/teal palette family, the three existing fonts, the ambient living background, the robot mascots, and the dark-tech-with-warmth mood.
- **FR-006**: Every robot character and its reactive animations MUST remain present and reactive on both surfaces (portfolio: scroll-speed reactor with shouts, android mascot, chase gag, logo-tap easter egg, walk/stride bots, blink/hover/cursor/parallax; blog: scroll-reactor + grad-cap rider, hero companion, robot author-avatar, magnetic cursor, ripple/magnetic, reveal-on-scroll). They MAY be reskinned to fit the new fingerprint but MUST NOT be removed, disabled, or flattened. Reveal-on-scroll is a special case (it is both protected AND a flagged "page never settles" tell): it MUST be re-orchestrated, not removed — the indiscriminate per-element stagger is reduced to a restrained, section-level entrance (section heads / grouped blocks reveal once, not every paragraph and chip), keeping the mechanism and its identity while eliminating the tell.
- **FR-007**: The content and information architecture of both surfaces MUST be preserved — sections and their arc, copy meaning, headings, and links. Copy may be re-typeset and its punctuation refined; its meaning MUST NOT be rewritten, and no real content may be invented or deleted (fabricated metrics are removed, not replaced with new fabrications).
- **FR-008**: Design audit findings against protected elements (robots, custom cursor, ambient background, reveal-on-scroll) MUST be recorded as sanctioned false positives rather than acted upon.

**Bounds (how the change is delivered):**

- **FR-009**: All blog styling changes MUST flow only through the generator — the blog templates, the `#blog-root`-scoped blog stylesheet, and the generator scripts — so the build reproduces them; no generated HTML may be hand-edited.
- **FR-010**: The portfolio restyle MUST keep both machine-readable marker zones (`LATEST-NOTES`, `PORTFOLIO-FONTS`) present, correctly paired, and writable by the build; the build still copies the portfolio verbatim.
- **FR-011**: Per-page SEO/GEO metadata and the canonical Person/WebSite JSON-LD identity MUST remain intact and consistent on every page.
- **FR-012**: Accessibility and Core Web Vitals MUST be preserved or improved: exactly one `<h1>` per page, semantic landmarks, meaningful/`aria-hidden` treatment, keyboard operability, compositor-only (transform/opacity) motion that respects `prefers-reduced-motion`, and no cumulative layout shift. The portfolio restyle MAY fix pre-existing accessibility gaps (e.g. an unlabelled landmark, a footer outside `contentinfo`) provided nothing regresses.
- **FR-013**: The change MUST remain deterministic at build time with no new runtime/build/CI dependency and no client-only content, and MUST NOT weaken the renderer's security posture.
- **FR-014**: The post-build verifier and the renderer unit tests MUST pass, and MUST additionally assert the differentiation stayed in-bounds (no new font/colour system; blog changes generator-only + `#blog-root`; portfolio marker zones + canonical identity + single `<h1>` intact; robots present on both surfaces).

### Key Entities

- **Design fingerprint**: The set of five differentiable qualities of a surface — type treatment, spacing rhythm, accent discipline, component composition, and motion. This is what the feature changes.
- **Brand core**: The invariant identity — dark green/teal palette family, the three fonts, ambient living background, robot mascots, dark-tech-with-warmth mood. This is what the feature preserves.
- **Protected robots**: The named robot characters and their reactive animations on each surface (see protected-elements inventory). Reskin-allowed, remove-forbidden.
- **Marker zones**: The portfolio's two machine-readable regions (`LATEST-NOTES`, `PORTFOLIO-FONTS`) the build depends on. Must stay present, paired, and writable.
- **Slop tell**: A concrete, named pattern that makes the design read as AI-generated/templated (the audit punch list). Each is a removal target.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (distinctive & non-templated): Re-running the hallmark audit on both surfaces reports zero slop-gate failures, and every slop tell enumerated in FR-001 is verifiably absent from the redesigned surfaces.
- **SC-002** (distinctive & non-templated): The ui-ux-pro-max pre-delivery / anti-pattern checks pass for both surfaces (including "no emoji as icons", contrast ≥ 4.5:1, and restrained glow).
- **SC-003** (distinctive & non-templated): Both surfaces change on all five fingerprint dimensions (FR-002), evidenced by a per-surface, per-dimension before→after design-decision record; the blog and portfolio share one fingerprint (FR-003), demonstrated by a shared token layer using the same named palette-colour tokens and the same type-scale/spacing-rhythm rules on both surfaces.
- **SC-004** (character preserved): The brand core is 100% retained — palette family and the three fonts unchanged, ambient background and mood retained — with no new web font and no new colour system introduced.
- **SC-005** (robots preserved): 100% of the protected robots and their reactive animations are present and demonstrably still reactive after the redesign, on both surfaces, verified by exercising scroll/hover/cursor/tap; none is removed, disabled, or flattened.
- **SC-006** (guarantees intact): The renderer unit test suite passes (all tests green) and the definition-of-done verifier passes (all checks green), including the new in-bounds assertions.
- **SC-007** (guarantees intact): Both portfolio marker zones remain present and correctly paired; the build still regenerates the `LATEST-NOTES` region into the deployed homepage; every page keeps its full crawlable content, per-page SEO tags, and the canonical Person/WebSite identity; the Atom feed, `llms.txt`, and `sitemap.xml` still list every published post.
- **SC-008** (guarantees intact): Every page has exactly one `<h1>`, semantic landmarks, and correct decorative-vs-meaningful treatment; all motion is compositor-only and honours `prefers-reduced-motion`; no accessibility check regresses versus the current site, and at least the pre-existing portfolio a11y gaps found in the audit are fixed.
- **SC-009** (bounds respected): No blog styling change exists outside the generator + `#blog-root`; no generated HTML is hand-edited; the change adds no new runtime/build/CI dependency.

## Assumptions

- The design authority for "does this still look templated / does the brand survive" is the hallmark audit + ui-ux-pro-max checks plus the maintainer's own eye; because this run is autonomous, ambiguity is resolved with a documented assumption rather than a pause.
- "The three existing fonts" are the self-hosted faces already loaded by the design (a display face, a body face, and a monospace face); the feature treats the specific families as fixed and does not name or add new ones.
- The portfolio is edited in committed source for the first time (sanctioned by constitution v1.5.0 Principle VII exception 3); the build continues to copy it verbatim.
- The blog's design lives largely in template-level inline styles and the generator's scripts today; "through the generator" therefore includes editing those templates and scripts, not only the stylesheet — provided no generated output is hand-edited.
- The existing protected-elements inventory and audit punch list (captured during diagnosis) are the authoritative lists of what to preserve and what to shed; this spec references them rather than re-deriving them.
- Governance: this feature is bounded by constitution v1.5.0; its plan MUST pass the Constitution Check against Principles I–VIII, treating a clean check as a required gate, not a formality.
