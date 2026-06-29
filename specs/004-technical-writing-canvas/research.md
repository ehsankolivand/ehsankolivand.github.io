# Research: Technical-Writing Canvas

Phase 0 decisions, each with rationale and (where relevant) a primary source. Every decision serves the objective and the Constitution; all were resolved autonomously (unattended run) and align with the spec's Clarifications session (2026-06-29).

## R1 — Highlighter engine: a single deterministic ordered-alternation scanner

**Decision**: One shared `Scanner` in `scripts/blog/highlight.py`. Each language is an **ordered list of `(token-kind, regex)` rules** compiled into one master pattern of named alternatives (`(?P<kind>…)|…`). Scanning walks the source left→right: at each position try `master.match(code, pos)`; the **first** alternative that matches wins (ordered priority); emit `(kind, matched_text)` and advance; if nothing matches, emit one character as plain text (`kind=None`) and advance. Identifiers are matched by one rule then **post-classified** against per-language keyword / type / builtin frozensets.

**Rationale**: Python's `re` alternation is **ordered** (first-match-wins, PCRE-style, not POSIX-longest), and `Pattern.match(s, pos)` is deterministic — so rule order *is* priority and the output is a pure function of `(code, language)`. The "emit one char on no match" rule guarantees **total coverage**: the concatenation of all emitted token texts equals the input exactly, so nothing is dropped or duplicated. This is the classic mini-Pygments/Rouge scanner shape, reduced to the stdlib.

**Primary source**: Python `re` docs (alternation "scans … left-to-right, first matching"); Pygments `RegexLexer` design (ordered token rules).

**Alternatives rejected**: (a) a third-party highlighter (Pygments) — violates Principle II (new dependency); (b) a browser-side highlighter (Prism/Shiki/highlight.js) — violates Principle I (client-rendered content) and II; (c) a hand-rolled char-by-char state machine per language — far more code, harder to keep deterministic and safe than a rule table over one engine.

## R2 — Token vocabulary + design-grounded color mapping

**Decision**: A **closed** token-kind enum → fixed `tok-*` CSS class set (11): `tok-comment, tok-keyword, tok-string, tok-number, tok-function, tok-type, tok-builtin, tok-operator, tok-tag, tok-attr, tok-meta`. Plain text (kind `None`) inherits the existing `<pre>` color. Colors are mapped to hues **already present in the design bundle** (verified by a palette scan of `Ehsan Koolivand - Blog.html`):

| class | color | role |
|---|---|---|
| `tok-comment` | `#66756F` italic | comments |
| `tok-keyword` | `#34E6A0` | keywords / control flow |
| `tok-string` | `#E7D2A6` | strings / char literals |
| `tok-number` | `#b388ff` | numeric literals |
| `tok-function` | `#7DF0C2` | function / method names |
| `tok-type` | `#ffd166` | types / classes / annotations |
| `tok-builtin` | `#46a8e0` | builtins / constants (true/false/null/None) |
| `tok-operator` | `#9FB0AA` | operators / punctuation (subtle) |
| `tok-tag` | `#34E6A0` | markup element tags |
| `tok-attr` | `#ffd166` | markup attributes / data keys |
| `tok-meta` | `#9FB0AA` | decorators / preprocessor / shebang |

**Rationale**: A small closed vocabulary keeps the CSS, the tokenizers, and the test surface bounded, and (crucially) makes class names **un-author-derivable** (security). Reusing the bundle's own hues satisfies the Principle III bound "existing vocabulary only — no new color system". Plain text staying `#9FE9C8` means an **unhighlighted/fallback block is byte-visually identical to today**.

**Primary source**: palette frequency scan of the design bundle (mint family + sand + amber `#ffd166` / coral `#ff8a80` / blue `#46a8e0` / purple `#b388ff` already present).

**Alternatives rejected**: a full Pygments-scale token taxonomy (overkill, more CSS/tests); inventing a fresh accent palette (violates Principle III bound (a)).

## R3 — Language coverage, grammars, and aliases

**Decision**: Full tokenizers for **Kotlin, Java, Python, Bash**; lighter tokenizers for **JSON, YAML, XML/HTML (markup), JavaScript, TypeScript, SQL**. Case-insensitive alias map: `kt`/`kts`→kotlin, `py`/`python3`→python, `sh`/`shell`/`zsh`/`bash`/`console`/`shell-session`→bash, `js`/`jsx`→javascript, `ts`/`tsx`→typescript, `yml`→yaml, `html`/`xhtml`/`svg`/`xml`→markup, `kotlin-script`→kotlin, `gradle`→groovy-not-supported→fallback (documented). Keyword/type/builtin sets sourced from each language's official grammar/spec. Anything unmapped → `recognized=False` → escape-only.

**Rationale**: Covers the blog's stated Android + tooling stack (Kotlin/Java/Python/Bash) plus the web/data formats it will use, matching the languages "actually used … already appearing in posts" plus the obvious near-future set, without an unbounded grammar zoo. Aliases mean authors can tag naturally.

**Primary source**: Kotlin language spec keyword list; Java SE keywords (JLS §3.9); Python `keyword.kwlist` + builtins; Bash reserved words/builtins; ECMAScript reserved words; JSON (RFC 8259) / YAML 1.2 / SQL token shapes.

**Alternatives rejected**: only the four "required" languages (too thin for a tech blog that will show JSON/YAML/Gradle/HTML); a generic one-size tokenizer (produces wrong, misleading colors).

## R4 — Fenced-code info-string grammar (GFM superset)

**Decision**: Parse the info string as: optional **language** = first bare token matching `[A-Za-z0-9+#._-]+` (no `=`/`{`); then attributes anywhere — `title="…"` / `file="…"` / `filename="…"` → **filename label**; a brace group `{1,3-5,8}` → **emphasized 1-based line set**. If the first token is NOT a bare-word language (info string starts with `//`, has `=` before any bare word, or is otherwise free prose) → the **entire info string is a legacy caption**, no language, no highlighting.

**Rationale**: A superset of GFM (first token = language) that (i) keeps the single existing ```` ```bash ```` block working as highlighted bash, (ii) needs **no new frontmatter** (Principle IV), (iii) preserves the original "info string = caption" behavior for any legacy/prose usage, and (iv) is unambiguous and deterministic to parse with a couple of regexes.

**Primary source**: GFM spec §4.5 (info string; "first word is the info string"); common ` {1,3-5}`/`title=` conventions (Rouge, Docusaurus, MkDocs-Material).

**Alternatives rejected**: a bespoke non-GFM syntax (breaks Obsidian/GFM muscle memory); putting filename/lines in frontmatter (violates "no new frontmatter").

## R5 — Line-emphasis emission + copy-friendliness

**Decision**: Two emit modes from the same token list. **No emphasis** → join token spans with **literal `\n`** inside the existing `<pre>` (today's text flow). **Emphasis requested** → wrap each source line in a block-level `<span class="cl">` (emphasized lines add `cl--hl`), with **no literal newline between line spans** (block display provides the line break). The block is tokenized whole first (so a multi-line comment/string survives), then each token's text is split at `\n` to distribute across line spans.

**Rationale**: The no-emphasis path is **byte-for-byte copyable** (literal newlines copy perfectly) and minimal. The emphasis path uses the standard Shiki/Prism block-line technique; browsers insert newlines between block boxes on copy, so copy fidelity holds. Splitting tokens across lines after whole-block tokenization is what lets line-emphasis coexist with multi-line tokens without losing characters.

**Primary source**: Shiki / Prism line-highlight implementations (block-display line spans); CSS `white-space:pre` + block-element copy behavior.

**Alternatives rejected**: always wrapping every line (more markup + slightly riskier copy for the common case); CSS `:nth-line` (does not exist); JS line numbering (violates Principle I).

## R6 — Callout / admonition syntax (Obsidian)

**Decision**: Reuse the **Obsidian callout** form: a blockquote whose first de-quoted line is `[!kind]` or `[!kind] Optional Title`; the remaining quoted lines are the body. Detected inside the existing blockquote branch. Known kinds + synonyms map to five visual variants: **note** (info), **tip** (success/hint), **warning**, **important**, **caution** (danger/error/bug). Unknown kind → render as **note**. Rendered as `<aside class="callout callout--<kind>" role="note" aria-label="<Label>">` with a title row (`aria-hidden` glyph + label) and a body div; reduced-motion-safe `data-reveal` reused.

**Rationale**: Identical authoring in the Obsidian vault and the build (Principle IV) — the same note renders natively in Obsidian and on the site. It is a pure extension of the existing blockquote parser, and unknown kinds degrade to a normal note callout (or, if `[!` is absent, a plain blockquote) — never a build failure (FR-015). `role="note"` + visible label is the accessible pattern for an advisory aside.

**Primary source**: Obsidian Callouts documentation (`> [!note] Title` syntax); WAI-ARIA `note` role guidance.

**Alternatives rejected**: a custom `:::note` fence (not Obsidian-native; would read as literal text in the vault); admonition via a directive plugin (new dependency / not stdlib).

## R7 — Footnotes: syntax, placement, determinism, accessibility

**Decision**: Standard **`[^id]`** inline reference + **`[^id]: definition`** block definition (PHP-Markdown-Extra / Obsidian-compatible). A **pre-pass** over the body (fence-aware, so `[^x]` inside code is ignored) extracts definitions and removes their lines; their anchor ids (`fn-<slug(id)>` / `fnref-<slug(id)>`) are **reserved in the same `used_ids` set the heading-anchor allocator uses**, so headings and footnotes can never collide. During render, a `[^id]` whose def exists becomes a superscript `<sup class="fnref" id="fnref-…"><a href="#fn-…">n</a></sup>` (n = order of first reference); an `[^id]` with **no** def is left as literal escaped text (no dangling link). After the body, a `<section class="footnotes"><ol>` lists each referenced+defined footnote in reference order, each `<li id="fn-…">` ending with a back-reference `<a href="#fnref-…" class="fn-back" aria-label="Back to content">↩</a>`. Unreferenced defs are omitted. Repeated references get unique `fnref-…-k` ids; the back-ref points to the first.

**Rationale**: The universal footnote convention, native to Obsidian, fully static and accessible (superscript links + back-links, all keyboard-focusable), and **deterministic** (numbering by reference order; ids reserved up front decouples uniqueness from numbering and guarantees collision-freedom vs. headings — FR-017). Undefined-ref-as-literal and unreferenced-def-omitted satisfy "no dangling, 404-bound anchor" (Principle VIII).

**Primary source**: PHP Markdown Extra footnotes; Obsidian footnotes; the heading-anchor allocator already in `markdown_render.py` (003).

**Alternatives rejected**: inline footnotes `^[text]` only (less common, weaker separation); rendering footnotes via JS tooltips (violates Principle I/VI).

## R8 — GFM table hardening

**Decision**: Replace the monolithic separator regex with a **split-and-check predicate**: a line is a table separator iff splitting it on unescaped pipes yields ≥1 cells and **every** cell matches `^:?-+:?$`. This fixes single-column tables (previously unrecognized). Keep and verify the existing behaviors: per-column alignment from `:` markers, escaped pipes (`\|`) preserved, inline markup rendered per cell (`render_inline`), ragged rows tolerated (missing cells → empty `<td>`; extra cells beyond the header dropped per GFM). Add a `class` hook on the table for a subtle refinement (zebra/row-hover) in `blog.css`.

**Rationale**: The current `_TABLE_SEP` regex requires ≥2 columns and can mis-handle edge separators; a split-and-check is both more correct and easier to reason about/test. Everything else the renderer already does correctly (alignment, escaped pipes, inline cells) is preserved and pinned by tests so the hardening introduces **no regression** (FR-013).

**Primary source**: GitHub Flavored Markdown spec §4.10 (tables: delimiter row, alignment, cell counts — "remainder … ignored", "missing … empty").

**Alternatives rejected**: a full CommonMark/GFM table state machine (out of scope; the existing approach is adequate once the separator predicate is fixed).

## R9 — Blockquote refinement (no regression)

**Decision**: Keep `block-quote.html`'s existing inline styling intact; add a `class` layer (`pquote`) and a `blog.css` rule providing a subtle decorative open-quote mark (mint, low opacity) via `::before`. The callout detection happens **before** plain-blockquote rendering, so `> [!kind]` never falls through to the quote path.

**Rationale**: A light, on-token enhancement that lifts the pull-quote without touching its existing inline style (so existing quotes can't regress — FR-012). Layering a class over the inline style is the lowest-risk way to refine within the sanctioned styling allowance.

**Alternatives rejected**: rewriting the blockquote partial's inline styles (regression risk for no benefit).

## R10 — Test strategy + CI wiring

**Decision**: A new repo-root **`tests/`** package (`__init__.py`, `test_markdown_render.py`, `test_highlight.py`) using stdlib **`unittest`**, run via `python -m unittest` locally and as a **CI step added before** the build/verify steps in `.github/workflows/deploy.yml`. Tests are pure (no filesystem/network), asserting on `markdown_render`/`highlight` outputs directly. Coverage matrix lives in `contracts/renderer-tests.md`.

**Rationale**: stdlib-only (Principle II — no new dependency), deterministic, fast, and it fails the pipeline early on a renderer regression — closing the long-standing "no renderer tests" known issue. `unittest` discovery needs no config.

**Alternatives rejected**: pytest (new dependency); doctest only (weaker for security assertions); testing only through `verify_build.py` (slow, integration-level, can't isolate the security guarantees).

## R11 — Verifier extension strategy (synthetic fixtures, no authored content)

**Decision**: Extend `verify_build.py` to (i) assert the **real** built AnkiVoice page's ```` ```bash ```` block now contains highlighted classed spans, and (ii) render a small set of **synthetic Markdown fixtures** through `markdown_render.render` and assert each new surface: highlighting per language, unknown-language fallback (no spans), filename label, line-emphasis (`cl--hl`), callouts (role/label/variant), footnotes (refs + section + backrefs + no dangling), and the table edge cases. No `content/blog/*.md` file is added.

**Rationale**: Honors the out-of-scope "no blog content authored" while still giving the **integration** Definition-of-Done gate honest coverage of surfaces no committed post exercises (the verifier already imports `markdown_render` and re-derives heading slugs, so calling the renderer is established precedent). The check count grows well beyond 273 (FR-021, SC-005).

**Alternatives rejected**: adding a draft fixture post (still authoring a content file; and CI builds without `--drafts`, so the verifier wouldn't see it); relying only on unit tests (the role requires the verifier itself to assert the new surfaces).

## Out of scope (recorded)

- **Authoring blog posts / adding any `content/blog/*.md`** — owner writes content next; new surfaces are proven by unit tests + synthetic verifier fixtures.
- **A general-purpose Markdown/CommonMark engine** — only the listed constructs; the renderer stays a closed vocabulary.
- **Languages beyond the ten** — unmapped tags fall back safely; more can be added later as pure rule-table data.
- **A visible redesign** beyond the sanctioned body-content classes; **no new dependency / backend**; **no RTL/Persian edition**.
