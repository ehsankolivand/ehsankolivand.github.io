# Contract: Fenced Code Block (info string, title bar, line-emphasis, backward compat)

Governs how `markdown_render` parses the fenced info string and renders the code panel. No new frontmatter. (FR-007..FR-011; Principle IV.)

## Info-string grammar (GFM superset)

```text
info        := language? attr*                |  legacy-caption
language    := token matching ^[A-Za-z0-9+#._-]+$  (no '=' or '{'); FIRST whitespace-delimited token only
attr        := title-attr | brace-lines
title-attr  := ('title'|'file'|'filename') '=' '"' value '"'
brace-lines := '{' rangespec '}'        rangespec := N | N-M , comma-separated (1-based)
legacy-caption := the ENTIRE info string, used verbatim, when it does NOT start with a bare-word
                  language token (i.e. starts with '//', has '=' before any bare word, or is free prose)
```

`parse_info_string(info: str) -> (language|None, filename|None, emphasized_lines: frozenset[int], caption|None)`

## Examples

| info string | language | filename | emphasized | caption |
|---|---|---|---|---|
| `kotlin` | kotlin | — | ∅ | — |
| `bash` (the one existing block) | bash | — | ∅ | — |
| `python title="app/main.py" {2,4-5}` | python | `app/main.py` | {2,4,5} | — |
| `js {1}` | javascript | — | {1} | — |
| `// build.gradle.kts` | — | — | ∅ | `// build.gradle.kts` |
| `Some prose caption` | — | — | ∅ | `Some prose caption` |
| (empty) | — | — | ∅ | — |

## Title-bar label

`label = filename or caption or language or ""` → fills `{{CAPTION}}` in `block-code.html` (HTML-escaped). Precedence guarantees the existing `bash` block still shows a label (`bash`), filenames take over when present, and legacy prose captions are preserved.

## `block-code.html` (extended, structure preserved)

The mac-window chrome (three dots + a label span) and the `<pre>` are unchanged in structure; `{{CAPTION}}` = the title-bar label, `{{CONTENT}}` = the highlighter's `emit_html` output (or escape-only fallback). The `<pre>` keeps its inline `color:#9FE9C8`/`white-space:pre`/`overflow-x:auto` so fallback blocks are byte-visually identical to today and code stays copy-friendly. Token + line classes are styled in `blog.css` under `#blog-root`.

## Backward compatibility (no regression)

- ```` ```bash ```` → highlighted bash, label `bash` (was: caption `bash`; meaning preserved, now colored).
- ```` ```// note ```` or any non-language info string → legacy caption, **no** highlighting (today's behavior).
- Plain ```` ``` ```` (no info) → no language, empty label, escape-only `<pre>` (identical to today).
- Unclosed fence at EOF → consumes to end of body (today's behavior).

## Invariants (test- + verifier-enforced)

1. **V-CB1**: `parse_info_string` returns a language only for a leading bare-word token; otherwise the whole string is a `caption` (legacy mode).
2. **V-CB2**: `emphasized_lines` is a `frozenset[int]` of 1-based line numbers from `{…}`; empty when absent; out-of-range numbers are harmless (ignored at emit).
3. **V-CB3**: the title-bar label follows the precedence `filename → caption → language → ""` and is HTML-escaped.
4. **V-CB4**: a supported language yields `tok-*` spans in `{{CONTENT}}`; an unsupported/absent language yields escape-only `{{CONTENT}}` with no `tok-` spans; neither ever fails the build.
5. **V-CB5**: with line-emphasis, the rendered `<pre>` contains `cl--hl` on exactly the requested lines; without it, no `cl` wrapper is emitted (inline mode) and newlines are literal.
6. **V-CB6**: the existing AnkiVoice ```` ```bash ```` block renders highlighted on its built page with no other content change.
