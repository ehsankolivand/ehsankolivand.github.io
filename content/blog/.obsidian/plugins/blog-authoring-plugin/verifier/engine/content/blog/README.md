# Writing blog posts (Obsidian → static site)

This folder is the **only** place you edit to publish. One post = one markdown note here.
You never touch generated HTML.

## Publish a post in 3 steps

1. **Create a note** in this folder, e.g. `my-post.md`, starting with YAML frontmatter:

   ```yaml
   ---
   title: "Custom layouts in Jetpack Compose"
   date: 2026-07-01            # publication date (YYYY-MM-DD)
   category: Compose          # must match a name in categories.yml
   tags: [compose, ui]
   excerpt: "A practical mental model for writing your own Layout."
   slug: custom-layouts        # optional; defaults to a slug of the title
   cover:                      # optional; a code-style cover is the default
     type: code
     glyph: "◳"
     caption: "// cover: measure → place"
   # image cover instead:
   #   type: image
   #   src: assets/cover.png   # put images in content/blog/assets/
   #   alt: "Diagram of measure → place"
   #   width: 1200
   #   height: 630
   # draft: true              # set while writing; excludes from the build
   ---
   ```

   Then write the body in normal Markdown: `## headings`, paragraphs, **bold**, *italic*,
   `inline code`, [links](https://example.com), lists, tables, > blockquotes, images
   `![alt](assets/pic.png)`, Obsidian callouts (`> [!note]`, `> [!tip]`, `> [!warning]`, …),
   and footnotes (`a claim[^1]` plus a matching `[^1]: the note` line).

   Fenced code blocks read an **info string** after the opening backticks:

   ````
   ```kotlin title="StaggeredColumn.kt" {2,5-7}
   @Composable fun StaggeredColumn(...) { ... }
   ```
   ````

   - the first bare word is the **language** for syntax highlighting — `kotlin`, `java`,
     `python`, `bash`, `json`, `yaml`, `html`/`xml`, `js`, `ts`, `sql` (and aliases like
     `kt`, `py`, `sh`); an unknown language just renders as escaped, unhighlighted code;
   - `title="…"` (or `file=`/`filename=`) adds a **filename label** on the code card;
   - `{2,5-7}` **emphasizes** those 1-based lines;
   - if the first token is *not* a bare language word (e.g. it starts with `//` or contains a
     space), the whole info string is treated as the **caption** — so the old
     ` ```// StaggeredColumn.kt ` caption style still works unchanged.

2. **Link a few related posts at the very end** (these become the "More notes" cards):

   ```
   ---
   ## More notes
   - [[speakloop-offline-interview-practice]]
   - [[telegram-topic-export-markdown-jsonl]]
   ```

   Use Obsidian wikilinks `[[slug]]` (or `[[slug|Label]]`), or markdown links to
   `/blog/<slug>/`. Unresolved links are reported as a build warning, not a broken card.

3. **Commit & push to `main`.** GitHub Actions rebuilds and deploys. Your post appears on
   the blog index, gets its own static, SEO-complete page in the existing design, lands in
   `sitemap.xml`, and shows its "More notes".

## Categories

Edit `categories.yml` to add, reorder, or relabel categories. Order there = order in the
top navigation (after "All"). A post's `category` must be one of those names.

## Preview locally (optional)

```bash
pip install -r requirements.txt
python scripts/build_blog.py --out _site        # add --drafts to include drafts
python scripts/verify_build.py --out _site
python -m http.server -d _site 8080             # open http://localhost:8080/blog/
```

## Rules of thumb

- Required frontmatter: `title`, `date`, `category`, `excerpt`. Missing fields fail the build
  with a clear message (so broken pages never deploy).
- `slug` is your permalink (`/blog/<slug>/`). Keep it stable; renaming the title won't break
  the URL if `slug` is set. Duplicate slugs fail the build.
- Read time is computed automatically; override with `readTime: "7 min"` if you like.
- Images go in `content/blog/assets/`; reference them as `assets/<file>`.
