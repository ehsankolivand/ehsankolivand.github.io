<!--
SYNC IMPACT REPORT
==================
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

The existing blog and post-page visual design MUST be preserved exactly. The system
extracts that design into templates and renders content into it; it MUST NOT restyle or
regenerate the look.

- The canonical design source is the existing bundled design (`Ehsan Koolivand - Blog.html`).
  Its markup, inline styles, CSS, keyframes, fonts, mascots, and interaction behaviors are
  the source of truth and MUST be reproduced faithfully.
- Templates MUST be derived from that design; new visual styling MUST NOT be invented.
- Self-hosted fonts and design assets from the bundle MUST be preserved; the look MUST be
  byte-faithful within the limits of converting a client-rendered bundle to static HTML.

Rationale: The design was produced deliberately; the engineering task is content
generation into a fixed design, not redesign.

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
  regenerated by this system, with one bounded exception: a single managed "Field notes"
  region in the deployed copy, delimited by `<!--LATEST-NOTES:START-->` /
  `<!--LATEST-NOTES:END-->` markers, is deterministically regenerated from the latest
  posts so the homepage links to current notes. The repo source `index.html` is never
  written to; only the assembled `_site/index.html` carries the refreshed region, the
  region is always fully regenerated (no hand-editing, no stale content), and everything
  outside the markers stays byte-for-byte identical to source.
- The blog MUST live in its own path (`/blog/`) and write only blog files plus the shared
  `sitemap.xml` entry; it MUST NOT overwrite unrelated files.
- Shared root companion files (`robots.txt`, `site.webmanifest`, favicons, `.nojekyll`)
  are reused, not duplicated or forked.

Rationale: The portfolio is live and already optimized; the blog is additive and must not
regress it.

## Additional Constraints & Technology Guardrails

- **Hosting**: GitHub Pages (user/org site served at root). Canonical base URL:
  `https://ehsankolivand.github.io/`.
- **URL layout**: Blog index at `/blog/`; each post at `/blog/<slug>/` (clean URLs).
  Shared assets under `/blog/assets/`. Root-absolute paths are used so links and assets
  resolve at any page depth.
- **Build tooling**: A single static generator that runs with tooling available for free
  in GitHub Actions (no paid services, no server). Dependencies MUST be minimal and
  pinned; the build MUST be reproducible in CI.
- **Determinism**: Same content in → same HTML out. The generator MUST be deterministic so
  diffs are reviewable and the build is idempotent.
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
  confirms compliance with Principles I–VII before and after design. Any violation MUST be
  resolved by changing the spec/plan/tasks, not by weakening a principle.
- **Verification before done**: The implementation is "done" only when the build runs
  successfully and the generated index and an example post are verified to contain their
  content and SEO tags in the static HTML (Principle I & V), the existing portfolio is
  byte-unchanged outside the managed "Field notes" region (Principle VII), and the design
  matches the source (Principle III).
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

**Version**: 1.1.0 | **Ratified**: 2026-06-27 | **Last Amended**: 2026-06-28
