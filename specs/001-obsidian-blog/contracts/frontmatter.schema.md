# Contract: Post Frontmatter

The authoring contract. Each post is `content/blog/<name>.md` beginning with a YAML frontmatter
block delimited by `---`, followed by a Markdown body.

## Schema

```yaml
---
title: "Spec-driven Android: generating modules an AI can't get wrong"   # REQUIRED string
date: 2026-06-18              # REQUIRED  YYYY-MM-DD  (datePublished)
updated: 2026-06-20          # optional  YYYY-MM-DD  (dateModified; default = date)
category: Tooling            # REQUIRED  must equal a name in categories.yml
tags: [android, codegen, ai] # optional  string list -> JSON-LD keywords
excerpt: "Replacing ask-and-hope with deterministic generators..."  # REQUIRED (a.k.a. description)
slug: spec-driven-android    # optional  default = kebab-case(title); stable permalink; unique
readTime: "9 min"            # optional  default = computed from body
draft: false                 # optional  default false; true = excluded from build

# Cover — choose ONE style:
# (a) code-style cover (design default):
cover:
  type: code
  glyph: "{ }"
  caption: "// cover: spec -> generators -> feature module"
# (b) image cover:
# cover:
#   type: image
#   src: assets/spec-cover.png   # relative to content/blog/
#   alt: "Spec to generators to module diagram"   # REQUIRED for image
#   width: 1200
#   height: 630
# Shorthand also accepted:  cover: "{ }"  (code glyph)  |  cover: assets/x.png  (image)

# Optional SEO overrides:
canonical: https://ehsankolivand.github.io/blog/spec-driven-android/   # default derived
ogDescription: "Custom social blurb"   # default = excerpt
image: assets/spec-cover.png           # social/JSON-LD image; default = cover image or site og-image
---

Normal **markdown** body here...

## A section heading

Paragraphs, `inline code`, [links](https://example.com), lists, blockquotes, and fenced
code blocks with the caption in the info string:

```// wallet-topup.feature.yaml
feature: wallet-topup
module:  feature_wallet
```

Images become figure blocks: ![Module graph](assets/module-graph.png)

---

<!-- Related "More notes": link a few posts at the very end -->
- [[mvi-that-scales]]
- [[custom-layouts-in-compose|Custom layouts in Compose]]
```

## Rules

- Frontmatter MUST be valid YAML between the first two `---` lines.
- REQUIRED: `title`, `date`, `category`, `excerpt` (or `description`), and a non-empty body.
- `category` MUST be one of the `name`s declared in `categories.yml` (else build error).
- `slug` MUST be unique across posts (else build error).
- For an image cover, `alt` is REQUIRED and `width`/`height` SHOULD be provided (no-CLS).
- Related links go at the **end** of the body as wikilinks `[[slug]]` / `[[slug|label]]` or
  markdown links to `/blog/<slug>/` or `<slug>.md`. Unresolved links → warning, not error.
- The author NEVER edits generated HTML.
