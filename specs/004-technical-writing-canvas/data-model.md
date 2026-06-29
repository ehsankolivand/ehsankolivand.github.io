# Data Model: Technical-Writing Canvas

This feature adds **no** new authoring field, **no** new frontmatter, and **no** persisted data. It introduces a handful of **derived, in-memory shapes** consumed during a single `render()` call and a new self-contained highlighter module. (Principle IV — single content source unchanged; Principle II — no storage.)

## 1. Parsed fenced code block (derived; `scripts/blog/markdown_render.py`)

Produced by parsing the fence line's info string. **Delta**: today the whole info string is a single `caption`; now it is parsed into structured fields (backward-compatible — see `contracts/code-block.md`).

| Field | Source | Notes |
|---|---|---|
| `language` | first bare token of the info string | `None` if absent or if the info string is a legacy caption; resolved through the alias map |
| `filename` | `title=`/`file=`/`filename="…"` attribute | `None` if absent; takes the title-bar slot when present |
| `emphasized_lines` | `{1,3-5,8}` brace group | a `frozenset[int]` of 1-based line numbers; empty when absent |
| `legacy_caption` | whole info string when it is not `lang [attrs]` | `None` otherwise; preserves the pre-004 caption behavior |
| `code` | raw lines between the fences | escaped + highlighted at emit time; never executed |

Derived **title-bar label** = `filename or legacy_caption or language or ""` (precedence).

## 2. Language grammar + token vocabulary (derived; `scripts/blog/highlight.py`)

Static data tables, not runtime state.

| Element | Shape | Notes |
|---|---|---|
| `TOKEN_CLASSES` | closed set of 11 `tok-*` kind→class names | fixed vocabulary; never author-derived (security) |
| per-language `RULES` | ordered `list[(kind, compiled_regex)]` | compiled once at import; ordered = priority |
| per-language `KEYWORDS`/`TYPES`/`BUILTINS` | `frozenset[str]` | identifier post-classification |
| `ALIASES` | `dict[str, str]` | case-insensitive tag → canonical language |
| token | `tuple[str | None, str]` | `(kind-class or None, exact source text)`; concatenated texts == input |

Functions: `resolve_lang(tag) -> str | None`; `tokenize(code, lang) -> tuple[list[token], bool]`; `emit_html(tokens, emphasized_lines) -> str`. All pure and deterministic.

## 3. Callout block (derived; `markdown_render.py` + `block-callout.html`)

Parsed from an Obsidian callout blockquote.

| Field | Source | Notes |
|---|---|---|
| `kind` | `[!kind]` on the first quoted line | normalized + synonym-mapped to one of {note, tip, warning, important, caution}; unknown → note |
| `title` | text after `[!kind]` on that line | defaults to the kind's capitalized label when empty |
| `body` | remaining de-quoted lines | rendered as inline markdown (escaped, safe) |

Rendered as a labeled `role="note"` region styled `callout--<kind>` from the existing palette.

## 4. Footnote registry (derived, post-scoped; `markdown_render.py` + `block-footnotes.html`)

One registry per `render()` call (one post), mirroring the heading-anchor allocator's post-scoping.

| Field | Shape | Notes |
|---|---|---|
| `definitions` | `dict[str, str]` (author id → markdown) | extracted in a fence-aware pre-pass; def lines removed from the body |
| `order` | `list[str]` | author ids in order of first **reference** (only defined ones) |
| `ref_count` | `dict[str, int]` | for unique repeat-reference ids (`fnref-<slug>-k`) |
| anchor ids | `fn-<slug(id)>` / `fnref-<slug(id)>` | reserved in the shared `used_ids` set → collision-free vs. headings |

Visible number = `order.index(id) + 1`. Undefined references render as literal text; unreferenced definitions are omitted. Output appended as one `<section class="footnotes">` after the body blocks.

## 5. Renderer test suite (new; `tests/`)

A stdlib `unittest` package; not site data. Cases assert the pure outputs of `markdown_render`/`highlight` (escaping, allow-list, token-injection, lists, tables, code/highlight/filename/line-emphasis/fallback, callouts, footnotes, heading anchors). See `contracts/renderer-tests.md`.

## Determinism summary

Every derived shape is a pure function of committed inputs (the Markdown body + the fenced info string + the static language tables). No `today()`, no network, no randomness; dict/`frozenset` membership and ordered-alternation regex are deterministic; footnote numbering is by reference order; anchor ids are reserved deterministically. → **same content in, byte-identical output.** The verifier re-renders synthetic fixtures and the build twice to prove this.
