# Feature Specification: Technical-Writing Canvas — Syntax Highlighting, Richer Code, Callouts/Footnotes & Renderer Tests

**Feature Branch**: `004-technical-writing-canvas`

**Created**: 2026-06-29

**Status**: Draft

**Input**: User description: "Make the in-house Markdown renderer a first-class technical-writing surface: deterministic, dependency-free syntax highlighting for the languages the blog uses; richer code blocks (optional filename label + line-emphasis); upgraded blockquotes and hardened GFM tables; two high-value constructs (admonition/callout + footnotes); and the security-sensitive renderer finally covered by isolated unit tests — with no new runtime/build/CI dependency, no client-side rendering, deterministic output, and the existing design language honored. Governed by Constitution v1.4.0."

## Overview

The blog generator already renders Obsidian Markdown into the locked dark design through an in-house, stdlib-only, closed-vocabulary renderer (`scripts/blog/markdown_render.py`) with full HTML escaping, a URL-scheme allow-list, single-pass `{{TOKEN}}` substitution, and (feature 003) deterministic heading anchors. Today it renders fenced code with a caption **but no syntax highlighting**, supports blockquotes and GFM tables, and has **no isolated unit tests** — the only automated gate is the post-build verifier (273 checks).

This feature turns the renderer into a surface that presents serious engineering writing well, **without adding a single runtime, build, or CI dependency** and without restyling the look. It (a) adds **deterministic, vendored, build-time syntax highlighting** that emits semantic CSS-classed spans for the languages the blog actually uses (Kotlin, Java, Python, bash/shell) plus the common web/data languages (JSON, YAML, XML/HTML, JavaScript, TypeScript, SQL), with a safe escape-only fallback for anything unrecognized; (b) makes code blocks **richer** with an optional filename/title label and optional line-emphasis driven purely from the fenced-code info string (no new frontmatter); (c) **upgrades** the existing blockquotes and **hardens** GFM tables against real-world edge cases; (d) adds two **high-value constructs** — a callout/admonition block and footnotes — as accessible static HTML with no client JS; and (e) finally gives the security-sensitive renderer an **isolated, deterministic unit-test suite** (stdlib `unittest`), wired into CI, while the post-build verifier remains the integration Definition-of-Done gate and grows to cover every new rendered surface.

It is governed by **Constitution v1.4.0**, whose Principle III now permits **sanctioned body-content semantic styling**: new CSS classes confined to `blog.css` under `#blog-root`, drawn only from the design's existing palette and already-loaded fonts, never altering page chrome/layout/portfolio.

## Clarifications

### Session 2026-06-29

All questions were resolved autonomously (unattended Spec Kit run) toward the option that best serves the objective and the Constitution; each carries a one-line rationale. These nine decisions shape the architecture, syntax, and test/verification strategy.

- Q: How is the fenced-code **info string** parsed (language vs. filename vs. line-emphasis vs. legacy caption)? → A: **A GFM superset.** The first whitespace-delimited bare token (`[A-Za-z0-9+#._-]+`, containing no `=`/`{`) is the **language**; `title="…"` (aliases `file=`/`filename=`) is the **filename label**; a brace group `{1,3-5,8}` is the 1-based **emphasized-line set**. If the info string does NOT begin with a bare-word language token (starts with `//`, has `=` first, or is free prose), the WHOLE info string is a **legacy caption** with no highlighting. *Rationale: keeps the one existing ```` ```bash ```` block working, needs no new frontmatter, and parses unambiguously + deterministically.*
- Q: What does the code-block **title bar** show? → A: **Precedence:** filename if given; else the legacy caption if given; else the language label (lowercased, e.g. `bash`); else empty (just the window dots). *Rationale: preserves today's behavior (the bash info string already showed there) while letting filenames take over — never a blank regression.*
- Q: How is **line-emphasis** rendered while keeping code copy-friendly? → A: **Two emit modes.** With no emphasis requested, token spans are emitted with **literal newlines** (today's `<pre>` flow → perfect copy fidelity). With emphasis requested, each source line is wrapped in a block-level `<span class="cl">` (emphasized lines add `cl--hl`), no literal newline between line spans; the block is tokenized whole first (multi-line tokens survive) then split at line boundaries. *Rationale: keeps the common case byte-for-byte copyable and minimal; only the emphasis case uses line boxes (the standard Shiki/Prism technique).*
- Q: Which **languages** get highlighting? → A: **Full tokenizers** for Kotlin, Java, Python, Bash; **lighter tokenizers** for JSON, YAML, XML/HTML, JavaScript, TypeScript, SQL; documented case-insensitive **aliases**; everything else → escape-only fallback. *Rationale: covers the stated Android+tooling stack plus the web/data formats the blog will use, without an unbounded grammar zoo.*
- Q: What **callout/admonition syntax**? → A: **Obsidian callout syntax** — a blockquote whose first line is `> [!kind]` or `> [!kind] Optional Title`, remaining `>` lines as body. Known kinds: note, tip, warning, important, caution (+ synonyms: info→note, success→tip, danger/error→caution, question/hint→note). Unknown kind → default **note** callout. *Rationale: identical authoring in the Obsidian vault and the build (Principle IV); extends the existing blockquote parser; degrades safely.*
- Q: What **footnote syntax** and placement? → A: **`[^id]` inline reference + `[^id]: definition` block** (PHP-Markdown-Extra / Obsidian-compatible). References render as superscript `<a>` links; definitions render in an end-of-body `<section class="footnotes">` ordered list, each with a back-reference (`↩`) link; ids are deterministic (`fn-…`/`fnref-…`) and collision-free via the post-scoped allocator. Undefined ref → plain text (no dangling link); unreferenced def → handled without crash. *Rationale: the universal, Obsidian-native footnote convention; accessible; deterministic; no client JS.*
- Q: How are the **new rendered surfaces verified** without authoring content? → A: **No new `content/blog/*.md` file.** The stdlib `unittest` suite is the primary coverage; `verify_build.py` additionally (i) asserts the REAL ```` ```bash ```` block on the built AnkiVoice page is highlighted, and (ii) renders a few **synthetic Markdown fixtures** through `markdown_render` and asserts highlighted code (per language), unknown-language fallback, filename label, line-emphasis, callouts, footnotes, and table edge cases. *Rationale: honors "no blog content authored" while giving the integration gate honest coverage; the verifier already imports the renderer.*
- Q: Where do **tests** live and how does **CI** run them? → A: A new repo-root **`tests/`** package run via **`python -m unittest`** locally and as a CI step added **before** build/verify in `.github/workflows/deploy.yml`; no dependency install added. *Rationale: stdlib-only, zero new dependency, standard discovery, fails the pipeline early on a renderer regression.*
- Q: Where does the **highlighter** live? → A: A new self-contained module **`scripts/blog/highlight.py`** (the shared deterministic scanner engine + per-language rule tables + alias map + token→class vocabulary); `markdown_render.py` calls it from the fenced-code path. *Rationale: isolates the separately-testable highlighter and keeps `markdown_render.py` focused.*

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Syntax-highlighted, dependency-free code blocks (Priority: P1)

A reader opens a post that contains a Kotlin, Java, Python, or shell snippet. The code renders with semantic color: keywords, strings, comments, numbers, types, and function names are visually distinct, in the post's static HTML, before any script runs. A snippet whose language tag is unknown (or omitted) still renders — safely escaped, exactly as today — and the build never fails because of a language tag.

**Why this priority**: This is the headline value — the blog is a technical-writing surface and unreadable monochrome code blocks are its biggest gap. It is independently shippable: with only this story, the blog already presents code far better. It also resolves the long-standing "no syntax highlighting" known issue.

**Independent Test**: Author fenced blocks tagged `kotlin`, `java`, `python`, `bash`, `json`, and `xyzlang`; build; confirm the first five contain classed token spans (`class="tok-…"`) for the expected token kinds in the served HTML, the unknown one is plain escaped code with no spans, and the build exits 0. Build twice and confirm byte-identical output.

**Acceptance Scenarios**:

1. **Given** a fenced block ```` ```kotlin ````, **When** the site builds, **Then** the served HTML contains semantic classed spans for Kotlin keywords/strings/comments and every source character appears HTML-escaped exactly once.
2. **Given** a fenced block tagged with an unsupported language, **When** the site builds, **Then** the code renders as safe escaped text with no token spans and the build exits 0 (no error).
3. **Given** code that contains `<`, `>`, `&`, `"`, a `{{TOKEN}}` sequence, and a `</span>` literal, **When** highlighted, **Then** all of it appears as inert escaped text and none of it breaks out of the code block or the token-substitution pass.
4. **Given** the same content, **When** the build runs twice, **Then** the two outputs are byte-identical.

---

### User Story 2 - Richer code blocks: filename label + line emphasis (Priority: P2)

An author wants a code block to show the file it came from (e.g. `build.gradle.kts`) in the block's title bar, and to draw the reader's eye to the two lines that matter. They express both from the fenced-code info string — no new frontmatter — and the rendered block shows the filename and visibly emphasizes the chosen lines, while still being fully copy-pasteable.

**Why this priority**: High-leverage polish that makes walkthroughs readable, building directly on US1's code path. Optional and backward-compatible, so it ships after the highlighting core.

**Independent Test**: Author ```` ```python title="app/main.py" {2,4-5} ````; build; confirm the title bar shows `app/main.py`, lines 2 and 4–5 carry an emphasis class/background, the other lines do not, and selecting + copying the block yields the original source with correct newlines and none of the chrome text.

**Acceptance Scenarios**:

1. **Given** an info string with a filename/title attribute, **When** rendered, **Then** the block's title bar shows that filename instead of the bare language label.
2. **Given** an info string with a line-emphasis range, **When** rendered, **Then** exactly those source lines carry the emphasis treatment and all others render normally.
3. **Given** a plain ```` ```bash ```` block with no extra metadata (the one existing in content today), **When** rendered, **Then** it renders highlighted bash with its label and no regression in meaning versus before.
4. **Given** any code block, **When** a reader copies it, **Then** the clipboard contains the exact source code (newlines preserved) and no title-bar/line-number chrome.

---

### User Story 3 - Callouts and footnotes for technical writing (Priority: P2)

An author writes a "note", a "warning", and a "tip" as visually distinct callout blocks, and adds footnotes for asides and citations. Both render as accessible static HTML — the callouts as labeled regions, the footnotes as superscript reference links to a definitions list with working back-links — with no client JavaScript.

**Why this priority**: These are the two constructs that most elevate long-form engineering writing beyond what the renderer supports today, and both are achievable within the single-pass renderer. They are independent of the code-block work.

**Independent Test**: Author a `> [!warning]` callout and a paragraph with a `[^1]` footnote plus its `[^1]:` definition; build; confirm the callout renders as a labeled, role-annotated region styled in the design palette, the footnote reference is a superscript anchor linking to a deterministic id in a footnotes section, the back-reference link returns to the citation, and no script is required for any of it.

**Acceptance Scenarios**:

1. **Given** a callout with a known kind (note/tip/warning/important/caution), **When** rendered, **Then** it produces a static, accessible labeled region using the design's existing palette and the kind's label.
2. **Given** a callout with an unknown kind, **When** rendered, **Then** it degrades gracefully to a default (note) callout or a plain blockquote and the build does not fail.
3. **Given** a paragraph with a footnote reference and a matching definition, **When** rendered, **Then** the reference is a superscript link to a uniquely-id'd definition in an end-of-body footnotes list, with a back-reference link, all in the static HTML.
4. **Given** an undefined footnote reference or an unreferenced definition, **When** rendered, **Then** the renderer degrades gracefully (no crash, no dangling 404-bound anchor).

---

### User Story 4 - Upgraded blockquotes and hardened tables (Priority: P3)

A reader encounters a pull-quote and a comparison table in a post. The blockquote has a refined, on-brand treatment, and the table renders correctly even when cells are empty, contain inline code/links/bold, are aligned per-column, or when a row has fewer or more cells than the header.

**Why this priority**: Quality and robustness work on already-supported features. It protects against malformed real-world Markdown and lifts visual quality, but the existing rendering already works, so it is the lowest-priority slice.

**Independent Test**: Render a table with left/center/right column alignment, an empty cell, a cell containing `` `code` `` and a `[link](…)` and `**bold**`, and one short row and one long row; confirm the HTML is well-formed, alignment matches the separator row, the inline markup renders inside the cells, missing cells render empty and extra cells are handled without breaking the table; render a multi-paragraph blockquote and confirm the refined styling with no regression.

**Acceptance Scenarios**:

1. **Given** a GFM table separator with `:---`, `:---:`, `---:`, **When** rendered, **Then** the columns are left/center/right aligned accordingly.
2. **Given** a table row with fewer cells than the header, **When** rendered, **Then** the missing cells render as empty `<td>` and the table stays well-formed; a row with more cells does not corrupt the structure.
3. **Given** table cells containing inline code, links, and emphasis, **When** rendered, **Then** that inline markup renders inside the cells (escaped and safe).
4. **Given** an existing blockquote, **When** rendered after this feature, **Then** it still renders its content correctly (no regression) with the refined treatment.

---

### User Story 5 - The renderer is finally test-covered (Priority: P1)

A maintainer changes the renderer and runs an isolated, fast, dependency-free unit-test suite that proves the security guarantees and rendering behaviors still hold — escaping, the URL-scheme allow-list, token-injection resistance, nested lists, table edge cases, code highlighting, callouts, footnotes, and heading-anchor determinism — before anything is built or deployed. CI runs the same suite.

**Why this priority**: The renderer is security-sensitive and was the one load-bearing module with no isolated tests (a standing known issue). Tests for its *existing* behavior are independently valuable and can be written immediately, and they are the safety net that makes the rest of this feature safe to land — hence P1 alongside the highlighting MVP.

**Independent Test**: Run `python -m unittest` (no third-party packages installed); confirm the suite executes, covers each guarantee with explicit assertions (including `javascript:`/`data:` neutralization and `{{TOKEN}}` injection inertness), and passes with 0 failures; confirm `requirements.txt` gained no test dependency and CI invokes the suite before build/verify.

**Acceptance Scenarios**:

1. **Given** a fresh checkout with only the pinned runtime dependency installed, **When** `python -m unittest` runs, **Then** the renderer suite runs and passes using only the standard library.
2. **Given** a malicious input (`javascript:` link, `data:` URL, control-char scheme bypass, `{{BODY}}` in author text, `</pre>` inside a code fence), **When** the corresponding test runs, **Then** it asserts the output is neutralized/escaped and the test passes.
3. **Given** the CI workflow, **When** it runs on push, **Then** it executes the renderer unit tests before the build and verify steps, with no new dependency install.

---

### Edge Cases

- **Empty / whitespace-only code block** → renders an empty `<pre>` (highlighted path produces no spurious spans); no crash.
- **Unclosed fence at end of body** → consumes to end of body (current behavior preserved); no crash.
- **Language tag with odd casing/alias** (`Kotlin`, `KTS`, `SH`, `JS`) → resolved case-insensitively via the alias map; unknown → escape-only fallback.
- **Info string that is a legacy caption** (free text, not `lang [meta]`) → preserved as a caption (backward compatibility) with no highlighting.
- **Multi-line tokens** (block comments, triple-quoted/multi-line strings) crossing line boundaries → highlighted correctly and still wrap into line-emphasis line boxes without losing characters.
- **Code containing `{{TOKEN}}`, `</span>`, `&`, `<`, `>`** → fully inert escaped text; no breakout, no double-escape.
- **Footnote referenced multiple times / out of order / undefined / defined-but-unreferenced** → deterministic ids, graceful handling, no dangling anchors.
- **Callout with no body, or nested markup in its body** → renders the labeled region with the inline markup; empty body does not crash.
- **Table with a single column, no body rows, escaped pipes (`\|`) in cells, or ragged rows** → well-formed output, no character loss, no structural corruption.
- **Reduced motion / no JavaScript** → all new constructs are fully present and legible without script; reveal animations remain progressive enhancement only.

## Requirements *(mandatory)*

### Functional Requirements

**Syntax highlighting (vendored, deterministic, build-time)**

- **FR-001**: The renderer MUST highlight fenced code blocks at build time by emitting semantic, CSS-classed `<span>` elements for recognized token kinds (at least: comment, keyword, string, number, function, type/class, builtin/constant, operator/punctuation, and markup tag/attribute), implemented in-house with NO third-party library and NO client-side highlighter.
- **FR-002**: Highlighting MUST cover at minimum Kotlin, Java, Python, and bash/shell, plus the common web/data languages the blog is likely to use (JSON, YAML, XML/HTML, JavaScript, TypeScript, SQL), with documented case-insensitive language aliases (e.g. `kt`/`kts`→kotlin, `py`→python, `sh`/`shell`/`zsh`/`console`→bash, `js`→javascript, `ts`→typescript, `yml`→yaml, `html`→xml/markup).
- **FR-003**: An unrecognized or absent language tag MUST fall back to safe, escape-only rendering (today's behavior) and MUST NEVER fail the build.
- **FR-004**: Highlighting MUST preserve the renderer's security-by-construction posture: every character of author code is HTML-escaped exactly once; all emitted CSS class names come from a fixed, closed vocabulary (never derived from author text); and the highlighted output cannot break out of the code block, inject markup, or survive into a later `{{TOKEN}}` substitution.
- **FR-005**: Highlighting MUST be deterministic — identical (code, language) in → byte-identical HTML out — using stable ordering and no `today()`/network/randomness.
- **FR-006**: Token styling MUST be delivered as new CSS classes in `templates/blog/assets/blog.css`, scoped to the blog body, drawn ONLY from the design's existing palette and the already-loaded mono font — no new web font, no new color system.

**Richer code blocks (info-string driven; no new frontmatter)**

- **FR-007**: The fenced-code info string MUST be parsed into an optional language (first token) plus optional metadata, introducing NO new required or optional frontmatter field.
- **FR-008**: An optional filename/title label supplied in the info string MUST render in the code block's existing title-bar chrome, taking the place of the bare language label when present.
- **FR-009**: An optional line-emphasis range supplied in the info string MUST visually emphasize exactly those source lines within the block, using a design-token background; when absent, no line is emphasized.
- **FR-010**: The existing caption behavior MUST keep working — a code block whose info string is not a recognized `language [metadata]` form MUST still show that info string as a caption — so existing content renders unchanged in meaning (backward compatibility).
- **FR-011**: Code blocks MUST remain copy-friendly: selecting and copying a block MUST yield the exact source text with newlines preserved and without any title-bar/line-emphasis chrome text; the block MUST NOT introduce cumulative layout shift, and the existing title-bar dots/chrome are preserved.

**Blockquotes & GFM tables (upgrade + harden, no rebuild)**

- **FR-012**: Blockquotes MUST keep rendering with no regression and receive a refined visual treatment within the existing design tokens; the `data-reveal` progressive-enhancement hook and reduced-motion behavior are preserved.
- **FR-013**: GFM tables MUST be hardened — without regression — so that per-column alignment (left/center/right from the separator row), empty cells, inline markup inside cells (code, links, bold/italic), escaped pipes, and rows with fewer or more cells than the header all produce correct, well-formed HTML with no character loss or structural corruption.

**Callouts & footnotes (new constructs; accessible static HTML)**

- **FR-014**: The renderer MUST support an admonition/callout block for at least note, tip, warning, important, and caution, with a syntax compatible with the single-pass renderer and Obsidian authoring; it MUST render to static, accessible HTML (a labeled region with an appropriate ARIA role/label) with NO client JS.
- **FR-015**: An unknown callout kind MUST degrade gracefully (render as the default kind or a plain blockquote) and MUST NOT fail the build.
- **FR-016**: The renderer MUST support footnotes: an in-text reference renders as a superscript link to a definition in an end-of-body footnotes section, each definition carries a back-reference link to its citation, and all of it is present in the static HTML with NO client JS.
- **FR-017**: Footnote anchor ids MUST be deterministic and collision-free within a post (consistent with the heading-anchor allocator); undefined references and unreferenced definitions MUST degrade gracefully with no crash and no dangling, 404-bound anchor.

**Isolated renderer tests + extended verifier**

- **FR-018**: The project MUST include an isolated, deterministic unit-test suite for `scripts/blog/markdown_render.py` using ONLY the Python standard library (`unittest`), adding NO third-party test dependency.
- **FR-019**: The suite MUST cover, with explicit assertions: HTML escaping; the URL-scheme allow-list (neutralizing `javascript:`, `data:`, and control-char/whitespace scheme bypasses); token-injection resistance (`{{…}}` in author text); inline emphasis/links/inline-images/inline-code; nested ordered/unordered lists; GFM table edge cases; fenced code with highlighting, filename label, line-emphasis, and unknown-language fallback; blockquotes; callouts (known + unknown kinds); footnotes (defined/undefined/duplicate); and heading-anchor determinism and uniqueness.
- **FR-020**: The suite MUST be runnable locally via `python -m unittest` (discovering a `tests/` suite) and MUST be invoked in the CI workflow before the build and verify steps, with no new dependency install.
- **FR-021**: The post-build `verify_build.py` MUST remain the integration Definition-of-Done gate and MUST be extended with assertions for every new rendered surface — highlighted classed code present and well-formed for known languages; safe escape-only fallback for unknown languages; filename label and line-emphasis present when requested and absent otherwise; existing captions still working; upgraded blockquote markup; hardened table output including the edge cases; callouts and footnotes as accessible static HTML; no raw author text escaping the highlighter; determinism preserved — and its total check count MUST grow beyond the post-003 baseline of 273.
- **FR-022**: The end-to-end build MUST remain deterministic (two builds byte-identical) and MUST add NO new runtime, build, or CI dependency (`requirements.txt` gains no package; CI gains only a standard-library test invocation).

**Accessibility & fidelity (cross-cutting)**

- **FR-023**: All new and refined rendered surfaces MUST preserve accessibility and design fidelity: exactly one `<h1>` per page is preserved; semantic structure and keyboard operability are maintained (footnote/back-reference links focusable; callouts labeled); decorative elements are `aria-hidden`; animations stay compositor-only and respect `prefers-reduced-motion`; and the portfolio `index.html` and all existing non-code design stay byte-faithful outside the two sanctioned portfolio zones.

### Key Entities *(derived; in-memory only — no new persisted data, no new frontmatter)*

- **Fenced code block**: parsed from the fence + info string into `(language?, filename?, emphasized_line_set, legacy_caption?)` plus the raw code; rendered to a highlighted, line-aware token stream inside the existing code-block chrome.
- **Language grammar**: a per-language, ordered set of tokenization rules (comments, strings, numbers, keyword/type/builtin sets, operators, markup) consumed by a single shared, deterministic scanner; plus an alias map and a closed token-kind → CSS-class vocabulary.
- **Callout block**: `(kind, optional title, body markdown)`; rendered to a labeled, role-annotated region styled per kind from the existing palette.
- **Footnote**: a `(reference id, definition body, back-reference)` set, resolved within a post to deterministic, collision-free anchor ids and an end-of-body definitions list.
- **Renderer test suite**: a stdlib `unittest` package of deterministic cases asserting the security guarantees and rendering behaviors of `markdown_render.py`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: **100%** of fenced code blocks tagged with a supported language render with semantic classed token spans in the served static HTML, with **0** reliance on client-side script to appear.
- **SC-002**: An unknown or absent language tag renders safely-escaped code with **0** build failures and **0** token spans, across the full test corpus.
- **SC-003**: Two consecutive builds of identical content produce **byte-identical** output (determinism), including all highlighted code, callouts, and footnotes.
- **SC-004**: The renderer unit-test suite runs with **0** failures using the **standard library only** — **0** third-party test packages added to `requirements.txt`.
- **SC-005**: The post-build verifier passes with **0** failures and **more checks than the post-003 baseline of 273**.
- **SC-006**: **0** new runtime, build, or CI dependencies are introduced (PyYAML remains the only third-party runtime dependency; CI adds only a standard-library test step).
- **SC-007**: The portfolio `index.html` stays **byte-identical outside its two sanctioned zones**, and **0** new `@font-face` rules or color systems are introduced (design fidelity preserved).
- **SC-008**: Copying any highlighted code block yields the **exact source text** (newlines preserved, no chrome text) — proven by an automated assertion.
- **SC-009**: Callouts and footnotes render as **accessible static HTML** (semantic role/label, keyboard-focusable footnote links) with **0** client-JS dependency.
- **SC-010**: The renderer's security guarantees are **test-proven**: `javascript:`/`data:`/control-char scheme bypasses neutralized, `{{TOKEN}}` author-text injection inert, and every code character HTML-escaped **exactly once** — **0** breakout paths.
- **SC-011**: **0** regressions in the meaning of existing rendered output: existing posts' blockquotes, tables, lists, inline markup, and code captions still render correctly.

## Assumptions

- The blog's real languages are the Android + tooling stack (Kotlin, Java, Python, bash/shell) plus the common web/data formats; only one fenced block (a `bash` install command) exists in committed content today, so the highlighter is forward-looking but grounded in the stated stack and must be backward-compatible with that existing block.
- The fenced-code info-string grammar is a **superset of GFM** (first whitespace-delimited token = language) chosen so the single existing ```` ```bash ```` block keeps working and so authors never need new frontmatter; the filename label uses `title="…"` and line-emphasis uses `{1,3-5}` brace ranges (see Clarifications).
- The callout and footnote syntaxes are **compatible with the single-pass renderer and Obsidian** (so the same note reads well in the vault): callouts use Obsidian's `> [!kind]` blockquote form and footnotes use `[^id]` / `[^id]:` (see Clarifications), with graceful degradation for unknown variants.
- **No new authoring frontmatter** and **no new persisted data** are introduced (Principle IV unchanged); everything is driven from the Markdown body and fenced info strings.
- New visual styling is permitted only under the **Constitution v1.4.0** "sanctioned body-content semantic styling" exception to Principle III (new `blog.css` classes, existing tokens only, body content only, no portfolio/chrome change).
- The renderer test suite uses the standard library's `unittest`; `python -m unittest` discovery from the repo root is the local + CI entry point.

### Out of Scope (recorded)

- **Authoring blog posts** — the owner writes content next; this cycle only upgrades the rendering engine. NO `content/blog/*.md` file is added: every new rendered surface is exercised by the stdlib unit-test suite and synthetic verifier fixtures (see Clarifications), leaving `content/blog/` untouched.
- **A full general-purpose Markdown/CommonMark implementation** — only the listed constructs are added; the renderer stays a deliberate closed vocabulary.
- **Any visible redesign** beyond styling the new or again-touched body-content elements within the existing design tokens (Principle III).
- **A backend, database, or any new runtime/build/CI dependency** (Principle II) — highlighting is vendored stdlib code, not a library or browser highlighter.
- **An RTL / Persian edition** of the blog — a separate epic.
