# Contract: Generated `llms.txt`

Built by `scripts/blog/llms.py::build_llms(base_text, posts, base_url) -> str`. Written to
`_site/llms.txt` by `build_blog.py`. `llms.txt` is removed from the verbatim root-copy step (it is
now a derived artifact). Deterministic; stdlib-only.

## Inputs

- `base_text`: the committed repo-root `llms.txt` (human-authored identity/profile). It MUST NOT be
  modified on disk; it is the source the build reads.
- `posts`: published posts, newest-first.

## Output structure (conformant with llmstxt.org)

```text
<base_text, with any prior build-managed "## Writing" block stripped>

## Writing

Latest field notes (full archive at https://ehsankolivand.github.io/blog/):

- [<post.title>](https://ehsankolivand.github.io/blog/<slug>/): <post.excerpt>
- …one line per published post, newest-first…
```

## Rules

- **Idempotent**: before appending, strip any existing `## Writing` section from `base_text` (match
  from a line equal to `## Writing` to the next `## ` heading or EOF) so re-running never stacks
  duplicates and a committed-by-mistake block is normalized.
- **Absolute URLs** for every post link (`config.abs_url(base_url, post.url)`).
- **One line per post**, format `- [Title](url): excerpt`. Title and excerpt are used verbatim
  (already plain text); collapse internal newlines to spaces.
- **Empty blog**: omit the `## Writing` section entirely; output = `base_text` (normalized).
- **Determinism**: order = input order (newest-first); no dates from `today()`.
- The committed root `llms.txt` SHOULD NOT contain a `## Writing` block (kept clean); the builder
  tolerates one if present (strips it).

## Verifier hooks (see verifier.md)

`_site/llms.txt` exists; contains the H1 site/author name from the base; contains a `## Writing`
heading when posts exist; and contains every published post's absolute URL.
