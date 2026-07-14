<!--
SYNC IMPACT REPORT
==================
Version change: 1.4.0 → 1.5.0
Bump rationale: Broadens Principle III (Design Fidelity) and Principle VII (Non-Destructive To
  The Existing Portfolio) to sanction a bounded "design-fingerprint differentiation" scope on
  BOTH surfaces, so the site can shed an AI-generated/templated feel while keeping its
  recognizable brand and every functional guarantee. Feature 005 refreshes the design
  fingerprint — (1) type-pairing & type treatment/scale within the three already-loaded
  self-hosted fonts (Space Grotesk, Manrope, JetBrains Mono; NO new web font, NO new
  @font-face), (2) spacing & vertical rhythm, (3) color-accent usage & discipline via a CSS
  custom-property token layer that NAMES existing palette colors (NO new color system, NO new
  hues), (4) component structure & composition (section rhythm, dividers, grid spans, card /
  quote / code-block / callout composition, heading placement), and (5) motion &
  microinteraction detailing — on the blog (through the generator ONLY: templates/blog/**,
  templates/blog/assets/blog.css scoped under #blog-root, scripts/blog/**; never hand-editing
  generated HTML) and, for the first time in committed source, on the hand-authored portfolio
  index.html and its own inline styles/assets. Both exceptions are hard-bounded: the robot
  characters and their reactive animations are PROTECTED identity (reskin-only — never removed,
  disabled, or flattened); content & information architecture are preserved; the recognizable
  brand character (dark green/teal palette family, the three fonts, ambient living background,
  robot mascots, dark-tech-with-warmth mood) stays; the portfolio's two machine-readable marker
  zones (LATEST-NOTES, PORTFOLIO-FONTS) remain present, correctly paired, and writable by the
  build; the canonical per-page SEO/GEO metadata and JSON-LD Person/WebSite @id identity stay
  intact and consistent; and accessibility & Core Web Vitals are preserved or improved (the
  portfolio restyle MAY fix pre-existing a11y gaps but MUST NOT regress). MINOR: broadens two
  NON-NEGOTIABLE principles by adding one bounded exception to each (no principle removed or
  weakened) — exactly parallel to the 1.2.0→1.3.0 and 1.3.0→1.4.0 amendments. Every
  out-of-scope principle is untouched and remains fully in force: I (SEO-correct static
  generation), II (GitHub Pages only), IV (Obsidian single source), V (per-page SEO/GEO
  completeness), VI (accessibility & Core Web Vitals), VIII (machine-readable discovery &
  single-source publishing). Also extends the Development Workflow Verification gate with the
  fingerprint-differentiation Definition-of-Done checks (no new @font-face and no new color
  system on either surface; blog styling confined to the generator + #blog-root with no
  hand-edited generated HTML; portfolio marker zones + canonical SEO/JSON-LD identity + single
  h1 intact; robots + reactive animations still present on both surfaces). Templates reviewed
  and remain compatible (generic Constitution Check references this file; verified directly
  against plan-template.md L39/L43 "[Gates determined based on constitution file]" +
  spec-template.md + tasks-template.md, neither of which hardcodes a principle list):
  ✅ plan-template.md, ✅ spec-template.md, ✅ tasks-template.md,
  ✅ .claude/skills/speckit-*/SKILL.md.

----- Prior entry -----
Version change: 1.3.0 → 1.4.0
Bump rationale: Amends Principle III (Design Fidelity) to add a SECOND bounded exception —
  "Sanctioned body-content semantic styling" — so the blog can render serious technical
  writing well without restyling the look. Feature 004 turns the in-house Markdown renderer
  into a first-class technical-writing surface: build-time, dependency-free syntax-
  highlighting token classes for fenced code, an optional code-block filename/title label +
  line-emphasis, callout/admonition blocks (note/tip/warning/...), footnotes, and refinements
  to the already-supported blockquotes and GFM tables. All of this is NEW visual styling on
  BODY CONTENT, which a strict reading of Principle III ("new visual styling MUST NOT be
  invented") would forbid. The amendment permits it under tight bounds: new CSS classes live
  ONLY in templates/blog/assets/blog.css, scoped to the blog body (#blog-root); they draw
  EXCLUSIVELY on the design's existing visual vocabulary — the bundle's palette colors, the
  already-loaded fonts (JetBrains Mono / Manrope / Space Grotesk), and the existing spacing/
  radius/border idioms — adding NO new web font and NO new color system; they style only
  author-content constructs and MUST NOT alter page chrome, layout, covers, cards, nav, or any
  existing non-code design (all byte-faithful to the bundle); they are produced
  deterministically at build time with no new runtime/build/CI dependency, no client-side
  rendering, and without weakening the renderer's security posture; and they never touch the
  portfolio index.html (Principle VII still governs it, unchanged). Gated by the Definition-of-
  Done verifier: the design stays faithful (portfolio byte-identical outside its two sanctioned
  zones, no new @font-face, no new color system), highlighted code is well-formed escaped
  classed markup with a safe escape-only fallback for unknown languages, and the new constructs
  render as accessible static HTML. MINOR: narrows a NON-NEGOTIABLE principle by adding a
  bounded exception consistent with the design's own tokens (no principle removed or weakened)
  — exactly parallel to the 1.2.0→1.3.0 Principle VII font-zone amendment. Also extends the
  Development Workflow Verification gate with the body-content-styling fidelity Definition-of-
  Done check. Templates reviewed and remain compatible (generic Constitution Check references
  this file; verified directly against plan-template.md + tasks-template.md + spec-template.md):
  ✅ plan-template.md, ✅ spec-template.md, ✅ tasks-template.md,
  ✅ .claude/skills/speckit-*/SKILL.md.

----- Prior entry -----
Version change: 1.2.0 → 1.3.0
Bump rationale: Amends Principle VII (Non-Destructive To The Existing Portfolio) to add a
  SECOND bounded exception — a one-time, performance-only, NON-VISUAL font-data
  optimization zone in the portfolio index.html — reconciling Principle VI (Core Web
  Vitals) with Principle VII. The portfolio <head> inlines ~682 KB of base64 woff2 font
  data across 54 @font-face rules covering Latin, Latin-ext, Cyrillic, Cyrillic-ext,
  Greek, and Vietnamese subsets; the page renders only Latin-script text, so the non-Latin
  subsets are dead weight on the highest-traffic page. The amendment permits removing
  demonstrably-unused @font-face subsets from a marker-delimited font zone, one time,
  committed to source (the build still copies index.html verbatim and never regenerates
  fonts), gated by a verifier fidelity proof: (a) every Unicode codepoint the page renders
  keeps the webfont glyph coverage it had (no visible glyph regresses), (b) nothing outside
  the sanctioned font-data bytes changes, and (c) the original font data stays recoverable
  from a committed baseline. If fidelity cannot be proven deterministically and offline, NO
  change is made (prove-or-defer). MINOR: narrows a NON-NEGOTIABLE principle by adding a
  bounded, fidelity-proven exception (no principle removed or weakened). Also CORRECTS a
  stale "Principles I–VII" reference in the Development Workflow Constitution-Check gate to
  "Principles I–VIII" (an incomplete propagation left by the 1.2.0 amendment that added
  Principle VIII) and extends the Verification gate with the font-fidelity Definition-of-
  Done check. Templates reviewed and remain compatible (generic Constitution Check
  references this file; verified directly against plan-template.md + tasks-template.md +
  spec-template.md): ✅ plan-template.md, ✅ spec-template.md, ✅ tasks-template.md,
  ✅ .claude/skills/speckit-*/SKILL.md.

----- Prior entry -----
Version change: 1.1.0 → 1.2.0
Bump rationale: Adds Principle VIII (Machine-Readable Discovery & Single-Source
  Publishing) — a NON-NEGOTIABLE rule codifying the always-apply invariants this
  GEO/publishing feature introduces: build-generated machine surfaces (an Atom feed and
  an llms.txt that list every published post), a single unified structured-data identity
  shared by the portfolio and the blog (one canonical Person, referenced by stable @id),
  one-note single-commit publishing where every derived artifact regenerates
  deterministically at build time, and the invariant that no committed source file may
  carry internal links to content that does not exist (verifier-enforced). MINOR: a new
  principle is ADDED; no existing principle is removed or weakened. Also extends the
  Additional Constraints (machine-readable surfaces, derived-artifact determinism) and
  the Development Workflow Verification gate (new Definition-of-Done checks).
  Templates reviewed and remain compatible (generic Constitution Check references this
  file): ✅ plan-template.md, ✅ spec-template.md, ✅ tasks-template.md,
  ✅ .claude/skills/speckit-*/SKILL.md.

----- Prior entry -----
Version change: 1.0.0 → 1.1.0
Bump rationale: Principle VII reworded to document the one bounded exception the build
  has always implemented — the managed "Field notes" region in the deployed homepage
  (delimited by LATEST-NOTES markers) is deterministically regenerated, while the repo
  source index.html is never modified and everything outside the markers stays
  byte-for-byte identical. MINOR: narrows a NON-NEGOTIABLE principle by adding a bounded,
  deterministic exception (no principle removed). Reconciles spec FR-025/SC-005,
  plan.md, contracts/build-cli.md, quickstart.md, and research.md with the actual build.
  (See bugfixtodolist.md BUG-001 / BUG-005.)

----- Prior entry -----
Version change: (template / unversioned) → 1.0.0
Bump rationale: Initial ratification of the project constitution (first concrete
  set of principles replacing the unfilled template).

Principles defined (7):
  I.   SEO-Correct Static Generation
  II.  GitHub Pages Only (Static, CI-Built, No Backend)
  III. Design Fidelity
  IV.  Obsidian As The Single Content Source
  V.   Per-Page SEO/GEO Completeness
  VI.  Accessibility & Core Web Vitals
  VII. Non-Destructive To The Existing Portfolio

Added sections:
  - Core Principles (I–VII)
  - Additional Constraints & Technology Guardrails
  - Development Workflow & Quality Gates
  - Governance

Removed sections: none (template placeholders replaced)

Templates requiring updates:
  ✅ .specify/templates/plan-template.md  — Constitution Check gate aligns (generic gate references this file; no edit required)
  ✅ .specify/templates/spec-template.md  — scope/requirements structure compatible (no mandatory-section conflict)
  ✅ .specify/templates/tasks-template.md — task categories compatible; SEO/a11y/design-fidelity verification tasks fit existing phases
  ✅ .claude/skills/speckit-*/SKILL.md    — reviewed; no agent-specific reference requires edits for these principles

Follow-up TODOs: none. RATIFICATION_DATE set to first adoption date (2026-06-27).
-->

# Obsidian-Driven Blog Constitution

This constitution governs the Obsidian-vault-driven blog that is generated into the
existing personal site hosted on GitHub Pages (`https://ehsankolivand.github.io/`).
The site already ships a portfolio `index.html` and SEO companion files; this blog
system is additive. Every specification, plan, and task in this project MUST comply
with the principles below. Where any later artifact conflicts with a principle, the
artifact MUST be changed — the principle MUST NOT be diluted.

## Core Principles

### I. SEO-Correct Static Generation (NON-NEGOTIABLE)

Every blog page MUST be rendered to static HTML at build time, with its real content
present in the initial markup that a non-JavaScript crawler receives.

- The blog index and every post page MUST contain their full human-readable content
  (post body text, headings, titles, excerpts, links) in the served HTML before any
  script runs.
- Post bodies MUST NOT be rendered client-side only. JavaScript on these pages is
  limited to progressive enhancement (animation, filtering, reading progress) and MUST
  NOT be the sole source of any content, link, or metadata a crawler needs.
- All internal post links and the category navigation MUST appear as real anchors in
  the static HTML so they are crawlable without script execution.

Rationale: The site has no backend and must rank in search engines and be readable by
AI assistants. A page on this same site previously failed because it was client-rendered;
that failure mode is forbidden here by construction.

### II. GitHub Pages Only — Static, CI-Built, No Backend (NON-NEGOTIABLE)

The blog MUST remain deployable as static files on GitHub Pages with no server runtime.

- No backend, database, server-side runtime, authentication system, comment system, or
  paid service may be introduced.
- The build MUST run in CI (GitHub Actions) on push to the main branch and deploy static
  output to GitHub Pages.
- A `.nojekyll` file MUST be present so files are served verbatim.
- Build tooling MUST be free and runnable in CI; it MUST NOT require paid services or
  manual local-only steps to produce the deployable site.

Rationale: The hosting model is fixed (GitHub Pages). Any dependency on a server breaks
deployment and the project's zero-cost constraint.

### III. Design Fidelity (NON-NEGOTIABLE)

The existing blog and post-page visual design MUST be preserved — its recognizable brand
character kept intact — and MAY change only where a bounded exception below expressly permits
it. The system extracts that design into templates and renders content into it; outside the
sanctioned exceptions it MUST NOT restyle or regenerate the look.

- The canonical design source is the existing bundled design (`Ehsan Koolivand - Blog.html`).
  Its markup, inline styles, CSS, keyframes, fonts, mascots, and interaction behaviors are
  the source of truth and MUST be reproduced faithfully.
- Templates MUST be derived from that design; new visual styling MUST NOT be invented.
- Self-hosted fonts and design assets from the bundle MUST be preserved; the look MUST be
  byte-faithful within the limits of converting a client-rendered bundle to static HTML.
- **Bounded exception — Sanctioned body-content semantic styling.** To render author
  content the in-house renderer newly supports, NEW CSS classes MAY be added — in
  `templates/blog/assets/blog.css` ONLY, scoped to the blog body (`#blog-root`) — giving that
  content semantic visual treatment: build-time syntax-highlighting token classes for fenced
  code, an optional code-block filename/title label and line-emphasis, callout/admonition
  blocks (e.g. note/tip/warning), footnote markers and back-references, and refinements to the
  already-supported blockquote and GFM-table elements. This is the ONLY sanctioned addition of
  new visual styling, and it is permitted ONLY when ALL of the following hold:
  - **(a) Existing vocabulary only.** It draws EXCLUSIVELY on the design's existing visual
    language — the bundle's palette colors, the already-loaded fonts (JetBrains Mono, Manrope,
    Space Grotesk), and the existing spacing/radius/border idioms. It introduces NO new web
    font and NO new color system.
  - **(b) Body content only, via blog.css.** It is confined to author-content constructs in the
    blog body and delivered as classes in `blog.css`. It MUST NOT restyle or alter the page
    chrome, layout, header/nav, covers, cards, or any existing non-code design — all of which
    stay byte-faithful to the bundle.
  - **(c) Deterministic & safe.** It is produced deterministically at build time with no new
    runtime/build/CI dependency and no client-side rendering, and it MUST NOT weaken the
    renderer's security posture (full HTML escaping, the URL-scheme allow-list, single-pass
    token substitution). Unknown or unsupported variants degrade gracefully (e.g. an unknown
    code-fence language falls back to safe escaped text — never a build failure).
  - **(d) Portfolio untouched.** It never modifies the portfolio `index.html`; Principle VII
    continues to govern that file unchanged.
  The Definition-of-Done verifier MUST assert this fidelity: the portfolio stays byte-identical
  outside its two sanctioned zones, no new `@font-face` rule or color system is introduced, and
  the new styling appears only on body-content elements. If any of these bounds cannot be met,
  the styling MUST be reduced until they are; a principle is never weakened to ship it.
- **Bounded exception — Sanctioned design-fingerprint differentiation (blog).** The blog's
  visual *fingerprint* MAY be deliberately refreshed to shed templated / AI-generated "slop"
  tells (e.g. gradient-clipped headline text, fake-terminal/OS window chrome on code blocks,
  decorative status pills, coloured glow-on-dark, mono-cap eyebrows on every section, uniform
  card grids, "the page never settles" reveal-on-everything). ONLY these five fingerprint
  elements MAY change: **(1) type-pairing & type treatment/scale** — restricted to the three
  already-loaded self-hosted fonts (Space Grotesk, Manrope, JetBrains Mono); NO new web font
  and NO new `@font-face` rule; **(2) spacing & vertical rhythm**; **(3) colour-accent usage &
  discipline** — a CSS custom-property token layer MAY be introduced that NAMES the design
  bundle's EXISTING palette colours, but it MUST NOT introduce a new colour system or new hues;
  **(4) component structure & composition** — section rhythm, dividers, grid spans, and the
  composition of cards, blockquotes, code blocks, callouts, and heading placement; and **(5)
  motion & microinteraction detailing**. It is permitted ONLY when ALL of the following hold:
  - **(a) Generator-only, #blog-root-scoped, never hand-edited output.** The change flows ONLY
    through the generator — `templates/blog/**`, `templates/blog/assets/blog.css` (scoped to
    `#blog-root`), and `scripts/blog/**` — so the build reproduces it. No generated HTML is
    ever hand-edited (Principle IV).
  - **(b) Deterministic & dependency-free.** It is produced deterministically at build time
    with no new runtime/build/CI dependency, no client-only content, and no weakening of the
    renderer's security posture (Principles I & II).
  - **(c) Robots preserved.** It MUST NOT remove, disable, or flatten the robot characters and
    their reactive animations (the scroll-reactor + graduation-cap rider, the hero companion,
    the robot author-avatar, the magnetic cursor, `[data-ripple]`/`[data-magnetic]`, and
    reveal-on-scroll). These are protected identity; they MAY be reskinned to sit inside the
    new fingerprint but MUST stay present and reactive.
  - **(d) Brand, content & IA preserved.** It keeps the recognizable brand character (the dark
    green/teal palette family, the three fonts, the ambient living background, the robot
    mascots, the dark-tech-with-warmth mood) and preserves the content and information
    architecture. Accessibility & Core Web Vitals (Principle VI) and per-page SEO/GEO
    (Principle V) remain fully in force.
  The Definition-of-Done verifier MUST assert this stayed in bounds: no new `@font-face` rule
  and no new colour system is introduced, the blog fingerprint change is confined to the
  generator + `#blog-root` with no hand-edited generated HTML, and the robots and their
  reactive animations are still present. If any bound cannot be met, the change MUST be reduced
  until it can; a principle is never weakened to ship it. (The prior two exceptions above —
  body-content semantic styling, and the portfolio being untouched by the blog system — remain
  unchanged; the portfolio's own fingerprint is governed by Principle VII, not this one.)

Rationale: The design was produced deliberately; the engineering task is content
generation into a fixed design, not redesign. Extending the design's own tokens to present
newly-supported content (highlighted code, callouts, footnotes, refined quotes/tables) is not a
redesign — it renders serious technical writing within the established look rather than inventing
a new one, and the bounds above keep every pixel outside that body content faithful to the bundle.
The later fingerprint-differentiation exception is a distinct, deliberate act: the design had
drifted into a common, templated "AI-generated" look, and shedding those specific tells — within
the existing fonts and palette, through the generator, with the robots and brand kept — makes the
site distinctive again without becoming a different site. It is a bounded refresh of the same
identity, not a rebrand.

### IV. Obsidian As The Single Content Source (NON-NEGOTIABLE)

Posts MUST be authored as Obsidian markdown notes with YAML frontmatter and committed to
the repository's content directory; the site is generated from them.

- No one hand-edits generated HTML. Generated output is a build artifact, never a source.
- All post metadata (title, date, category, tags, excerpt, cover, slug, SEO fields, draft
  flag) MUST come from frontmatter; the post body MUST be normal markdown.
- The category list (canonical set, ordering, labels) MUST be author-declarable from the
  vault — it MUST NOT be hardcoded somewhere the author cannot change.
- Related "More notes" MUST be resolved at build time from author-placed links
  (Obsidian wikilinks or markdown links) at the end of a post.

Rationale: A single, simple authoring flow (write one note, commit, push) is the product.
Generated HTML as a source of truth would break that flow and invite drift.

### V. Per-Page SEO/GEO Completeness (NON-NEGOTIABLE)

Every generated page MUST be SEO- and GEO-complete and identity-consistent.

- Each post page MUST carry a correct `<title>`, meta description, canonical URL, Open
  Graph tags, Twitter card tags, and Article/BlogPosting JSON-LD (headline, author,
  datePublished, dateModified, image, description, articleSection from category, keywords
  from tags), all fed from frontmatter.
- Every published post MUST be listed in `sitemap.xml` with an appropriate `lastmod`.
- The blog MUST reuse the existing `robots.txt`, `site.webmanifest`, and favicon set.
- One consistent absolute site URL (`https://ehsankolivand.github.io/`) MUST be used
  everywhere; the author identity MUST be consistent with the rest of the site
  ("Ehsan Kolivand", Senior Android Engineer, Istanbul).

Rationale: Discoverability by search engines and AI assistants is the reason the system
must be static; incomplete or inconsistent metadata silently defeats that goal.

### VI. Accessibility & Core Web Vitals (NON-NEGOTIABLE)

Generated pages MUST preserve semantic structure and good runtime performance.

- Each page MUST have exactly one `<h1>`, semantic landmarks (`header`, `nav`, `main`),
  and meaningful `alt` text (decorative mascots marked `aria-hidden`).
- All links and interactive controls MUST be keyboard-focusable and operable.
- Animations MUST be compositor-only (transform/opacity) and MUST respect
  `prefers-reduced-motion`; pages MUST avoid cumulative layout shift.

Rationale: Accessibility and Core Web Vitals are both user-facing quality and ranking
signals; they are cheap to keep and expensive to retrofit.

### VII. Non-Destructive To The Existing Portfolio (NON-NEGOTIABLE)

The existing portfolio and its prior SEO work MUST stay intact.

- `index.html` (the portfolio bundle) and its prior SEO pass MUST NOT be modified or
  regenerated by this system, with **three bounded exceptions** and no others — the first two
  marker-delimited and build-managed, the third a one-time design-fingerprint restyle committed
  to source:
  - **(1) Managed "Field notes" region** — a single region in the deployed copy,
    delimited by `<!--LATEST-NOTES:START-->` / `<!--LATEST-NOTES:END-->` markers, is
    deterministically regenerated by the build from the latest posts so the homepage links
    to current notes. The repo source `index.html` is never written to by the build; only
    the assembled `_site/index.html` carries the refreshed region, the region is always
    fully regenerated (no hand-editing, no stale content), and everything outside the
    markers stays byte-for-byte identical to source.
  - **(2) Performance-only, non-visual font-data optimization** — the portfolio's inlined
    `@font-face` font data MAY be optimized ONE time, in place, within a single zone
    delimited by `<!--PORTFOLIO-FONTS:START-->` / `<!--PORTFOLIO-FONTS:END-->` markers, by
    removing demonstrably-unused font subsets to cut page weight (Principle VI). This is the
    ONLY sanctioned edit to the committed portfolio source bytes, and it is strictly
    NON-VISUAL: it MUST NOT change layout, styling, or any rendered glyph. It is performed
    offline (no new CI/runtime dependency), the build still copies `index.html` verbatim
    (it never regenerates the fonts), and it is gated by a Definition-of-Done fidelity proof
    in the verifier: (a) every Unicode codepoint the portfolio renders that had webfont
    coverage in the original still has it (no visible glyph regresses to a fallback it did
    not already use), (b) nothing outside the sanctioned font-data bytes — everything
    outside the `PORTFOLIO-FONTS` markers — changes, byte-for-byte, against a committed
    baseline, and every retained `@font-face` rule appears verbatim in that baseline (only
    whole-subset removals, never edits to kept faces), and (c) the original font data
    remains recoverable from the committed baseline. If any part of this proof cannot be
    made to pass deterministically and offline, the optimization MUST be deferred and the
    fonts left untouched (prove-or-defer); a principle is never weakened to ship it.
  - **(3) Sanctioned portfolio design-fingerprint differentiation** — a ONE-TIME, deliberate
    restyle of the hand-authored `index.html` and its own inline stylesheet/assets MAY be
    committed to source to shed the same templated / AI-generated "slop" tells the blog sheds
    (gradient-clipped headline text, fake terminal/OS window chrome, decorative status pills,
    emoji-as-icons, invented skill-percentage bars, coloured glow-on-dark, numbered eyebrows on
    every section, reveal-on-everything). Unlike exceptions (1) and (2), this edits the
    committed portfolio bytes broadly (not a marker zone) — but ONLY the same five fingerprint
    elements as Principle III's blog exception: **(i) type-pairing & treatment** within the
    existing three fonts (NO new web font, NO new `@font-face`); **(ii) spacing & vertical
    rhythm**; **(iii) colour-accent discipline** within the EXISTING palette (NO new colour
    system or hues); **(iv) component structure & composition**; and **(v) motion &
    microinteraction detailing**. It is permitted ONLY when ALL of the following hold:
    - **(a) Marker zones intact.** Both machine-readable zones —
      `<!--LATEST-NOTES:START-->`/`<!--LATEST-NOTES:END-->` and
      `<!--PORTFOLIO-FONTS:START-->`/`<!--PORTFOLIO-FONTS:END-->` — MUST remain present,
      correctly paired, and functional, so the build can still regenerate the "Field notes"
      region and the font-data zone stays usable. The build still copies `index.html` verbatim
      (it does not regenerate the page).
    - **(b) Content & IA preserved.** The page's content and information architecture — its
      sections and their arc (hero → about → skills → experience → writing → contact), copy
      meaning, headings, and links — are preserved. Copy may be re-typeset and punctuation
      refined, but its meaning is not rewritten.
    - **(c) SEO/GEO identity intact.** All per-page SEO metadata and structured data in
      `<head>` (title, meta description, canonical URL, Open Graph, Twitter card, and the
      JSON-LD Person / WebSite graph keyed by the canonical `…/#person` and `…/#website`
      `@id`s) stay intact and identity-consistent (Principles V & VIII).
    - **(d) Robots preserved.** The robot characters and their reactive animations (the
      scroll-reactor with its shouts, the android mascot, the chase gag, the logo-tap easter
      egg, the walk/stride bots, and the blink/hover/cursor/parallax behaviours) MUST NOT be
      removed, disabled, or flattened. They are protected identity; they MAY be reskinned to
      sit inside the new fingerprint but MUST stay present and reactive.
    - **(e) Brand preserved; a11y & CWV preserved or improved.** The recognizable brand
      character is kept, and accessibility & Core Web Vitals (Principle VI) are preserved or
      improved — this restyle MAY fix pre-existing a11y gaps (e.g. an unlabelled landmark, a
      footer nested out of `contentinfo`) but MUST NOT regress: compositor-only
      transform/opacity motion, `prefers-reduced-motion` honoured, exactly one `<h1>`, semantic
      landmarks, and decorative art kept `aria-hidden`.
    This exception does NOT authorize changing the hosting model, the content pipeline, or any
    out-of-scope principle. The Definition-of-Done verifier MUST assert: both marker zones still
    present and correctly paired, the canonical SEO/JSON-LD identity intact, exactly one `<h1>`
    preserved, and the robots and their reactive animations still present. If any bound cannot
    be met, the restyle MUST be reduced until it can; a principle is never weakened to ship it.
- The blog MUST live in its own path (`/blog/`) and write only blog files plus the shared
  `sitemap.xml` entry; it MUST NOT overwrite unrelated files.
- Shared root companion files (`robots.txt`, `site.webmanifest`, favicons, `.nojekyll`)
  are reused, not duplicated or forked.

Rationale: The portfolio is live and already optimized; the blog is additive and must not
regress it.

### VIII. Machine-Readable Discovery & Single-Source Publishing (NON-NEGOTIABLE)

The site MUST be maximally discoverable and citable by search engines and AI/generative
engines, and publishing MUST stay a single-commit action whose every derived artifact is
build-generated and self-consistent.

- **Machine-readable surfaces**: The build MUST generate, as static files, a standards-
  compliant syndication feed (Atom) that lists every published post and an `llms.txt`
  that enumerates the published posts with titles, absolute URLs, and one-line summaries.
  These are generated from the same Obsidian content as the pages — never hand-maintained.
- **Unified structured identity**: Author and site identity MUST be expressed as one
  canonical entity shared by the portfolio and the blog. Blog structured data MUST
  reference the portfolio's canonical Person and WebSite by stable `@id`
  (`…/#person`, `…/#website`) so engines resolve the portfolio and blog as a single
  entity rather than duplicates.
- **Single-source, single-commit publishing**: Publishing or updating a post MUST require
  editing/committing exactly one Markdown note. Every derived artifact — post pages, the
  blog index, `sitemap.xml`, the Atom feed, `llms.txt`, and the homepage "Field notes"
  region — MUST regenerate deterministically at build time from that content, with no
  second manual edit and no `today()`-style nondeterminism.
- **No dangling committed links**: No committed source file (including the portfolio
  `index.html`) may contain an internal link to a blog post or page that does not exist.
  Committed source MUST NOT carry stale/404-bound internal links between builds; the
  Definition-of-Done verifier MUST assert this.

Rationale: Discoverability for AI assistants and search engines is the entire reason this
site is static; feeds and an accurate `llms.txt` are the cheapest durable citation
surfaces, a unified identity prevents the knowledge graph from splitting the same person
into two, and a one-commit flow with no dangling links is what keeps publishing safe and
the served site always correct.

## Additional Constraints & Technology Guardrails

- **Hosting**: GitHub Pages (user/org site served at root). Canonical base URL:
  `https://ehsankolivand.github.io/`.
- **URL layout**: Blog index at `/blog/`; each post at `/blog/<slug>/` (clean URLs).
  Shared assets under `/blog/assets/`. Root-absolute paths are used so links and assets
  resolve at any page depth.
- **Machine-readable surfaces**: Beyond the HTML pages, the deployable site MUST ship
  `sitemap.xml`, an Atom feed (`/blog/feed.xml`), and `llms.txt`, all build-generated from
  the Obsidian content. Pages MUST link the feed via `<link rel="alternate">` autodiscovery.
- **Build tooling**: A single static generator that runs with tooling available for free
  in GitHub Actions (no paid services, no server). Dependencies MUST be minimal and
  pinned; the build MUST be reproducible in CI.
- **Determinism**: Same content in → same HTML out. The generator MUST be deterministic so
  diffs are reviewable and the build is idempotent. This applies to every derived artifact
  (pages, `sitemap.xml`, Atom feed, `llms.txt`, homepage "Field notes" region): all dates
  come from frontmatter or configured constants, never from `today()`.
- **No client-only content**: see Principle I. The progressive-enhancement script is the
  only client JS and is optional to the page's meaning.
- **Out of scope**: backend, database, server-side runtime, paid service, comment system,
  authentication, redesigning the existing look, and changing the existing portfolio
  page's content.

## Development Workflow & Quality Gates

- **Spec-driven**: Work flows through the Spec Kit cycle (constitution → specify → clarify
  → plan → tasks → analyze → checklist → implement). Each phase's artifacts MUST agree
  with this constitution and with each other.
- **Constitution Check**: `plan.md` MUST include a Constitution Check that explicitly
  confirms compliance with Principles I–VIII before and after design. Any violation MUST be
  resolved by changing the spec/plan/tasks, not by weakening a principle.
- **Verification before done**: The implementation is "done" only when the build runs
  successfully and the generated index and an example post are verified to contain their
  content and SEO tags in the static HTML (Principle I & V), the existing portfolio is
  byte-unchanged outside its two sanctioned regions — the managed "Field notes" region
  and, where applied, the `PORTFOLIO-FONTS` font-data zone (the latter proven NON-VISUAL:
  every rendered codepoint keeps its webfont glyph coverage and only whole unused font
  subsets were removed) (Principles VII & VI), the design matches the source (Principle
  III) — and where body-content semantic styling is applied (syntax-highlighting tokens,
  callouts, footnotes, code filename/line-emphasis, blockquote/table refinements), the verifier
  proves it stays within the sanctioned bounds (well-formed escaped classed code with a safe
  escape-only fallback for unknown languages, the new constructs rendered as accessible static
  HTML, no new web font or color system introduced, and everything outside the blog body content
  byte-faithful) — the Atom feed and `llms.txt` are present and list every published post, structured
  data references the canonical Person/WebSite `@id`, and no committed source file carries
  an internal link to a nonexistent page (Principle VIII). Where the sanctioned design-
  fingerprint differentiation is applied (Principles III & VII), the verifier ALSO proves it
  stayed in bounds: no new `@font-face` rule and no new colour system is introduced on either
  surface; the blog fingerprint change lives only in the generator + `#blog-root` with no
  hand-edited generated HTML; the portfolio's two marker zones remain present and correctly
  paired, its canonical SEO/JSON-LD Person/WebSite `@id` identity is intact, and it keeps
  exactly one `<h1>`; and the robot characters and their reactive animations are still present
  on both surfaces. These checks are encoded in the post-build verifier.
- **No silent degradation**: A build error MUST be fixed at the root cause or reported
  honestly; a feature MUST NOT be disabled or a principle weakened to silence an error.
- **Example content**: At least one real example post authored as an Obsidian note MUST
  exist to prove the end-to-end flow.

## Governance

This constitution supersedes other practices for this project. It is the source of truth
for what the blog system MUST and MUST NOT do.

- **Amendments**: Changes to principles require updating this file, bumping the version per
  the policy below, recording the change in the Sync Impact Report at the top of this file,
  and propagating the change to dependent Spec Kit templates and artifacts.
- **Versioning policy** (semantic):
  - MAJOR: backward-incompatible governance/principle removal or redefinition.
  - MINOR: a new principle/section is added or guidance is materially expanded.
  - PATCH: clarifications, wording, or non-semantic refinements.
- **Compliance review**: Every spec, plan, and task set MUST be checked against these
  principles (the `/speckit-analyze` and Constitution Check gates enforce this). Violations
  block progress until resolved.
- **Runtime guidance**: Implementation-level guidance lives in the feature's `plan.md`,
  `research.md`, and `quickstart.md`; those documents MUST defer to this constitution on
  any conflict.

**Version**: 1.5.0 | **Ratified**: 2026-06-27 | **Last Amended**: 2026-07-14
