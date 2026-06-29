# Quickstart: Technical-Writing Canvas (feature 004)

## Run the renderer tests (NEW)

```bash
python -m unittest discover -s tests -v      # stdlib only; no pip install needed
# expect: OK (N tests) — every renderer + highlighter guarantee green
```

## Build + verify (unchanged commands)

```bash
pip install -r requirements.txt              # still just PyYAML==6.0.1
python scripts/build_blog.py --out _site      # add --drafts for local-only drafts
python scripts/verify_build.py --out _site     # Definition-of-Done gate; expect "checks > 273, 0 failure(s)"
python -m http.server -d _site 8080            # preview http://localhost:8080/blog/
```

Determinism check (two builds byte-identical):

```bash
python scripts/build_blog.py --out _site && cp -r _site _site_a
python scripts/build_blog.py --out _site && diff -r _site _site_a && echo "DETERMINISTIC"
```

## What changed (feature 004)

- **Syntax highlighting**: fenced code is now highlighted at build time (Kotlin, Java, Python, Bash, JSON, YAML, XML/HTML, JavaScript, TypeScript, SQL). Unknown languages render safely escaped (no error). New module `scripts/blog/highlight.py`.
- **Richer code blocks**: optional filename label + line-emphasis from the info string (no new frontmatter).
- **Callouts + footnotes**: Obsidian `> [!kind]` callouts and `[^id]` footnotes render as accessible static HTML.
- **Quotes + tables**: refined blockquote treatment; hardened GFM tables (alignment, empty/ragged cells, inline markup, escaped pipes, single column).
- **Tests**: a stdlib `unittest` suite (`tests/`) covers the renderer's security guarantees + behaviors; CI runs it before build/verify; `verify_build.py` extended.

## Authoring syntax (for the owner's next content cycle)

Code with a filename + emphasized lines:

````markdown
```kotlin title="MainActivity.kt" {3,5-6}
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { App() }
    }
}
```
````

Callout:

```markdown
> [!warning] Don't ship this
> The token is logged in plaintext here.
```

Footnote:

```markdown
This runs fully offline.[^1]

[^1]: No network calls after the one-time model download.
```

## Validate by hand

```bash
# highlighting present on the real bash block:
grep -o 'class="tok-[a-z]*"' _site/blog/ankivoice-offline-audio-anki-decks/index.html | sort -u | head
# new CSS classes shipped:
grep -oE '#blog-root \.(tok-[a-z]+|cl|callout|footnotes)' _site/blog/assets/blog.css | sort -u | head
# fallback never errors (unknown language builds clean): exercised by tests + verifier synthetic fixtures
# no new dependency:
cat requirements.txt        # PyYAML==6.0.1 only
```

## Procedure notes

- The highlighter is pure data + one scanner: adding a language later = adding a rule table + alias entries in `highlight.py` (no engine change).
- The verifier proves the new surfaces with synthetic fixtures (rendered in-process) plus the one real built bash block — **no** `content/blog/*.md` is added (content authoring is the owner's next, separate cycle).
