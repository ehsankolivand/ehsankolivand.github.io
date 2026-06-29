# Data Model: Android-Engineer Positioning, Deep-Citability & Portfolio Performance

This feature adds **no** new authoring field and **no** persisted data. It changes three derived
shapes and adds one non-served reference file. (Principle IV — single content source unchanged.)

## 1. Author identity node (derived; `scripts/blog/seo.py`)

The canonical author `Person`, emitted on each post (`BlogPosting.author`) and the index
(`Blog.author`). **Delta**: add `knowsAbout`.

| Field | Source | Notes |
|---|---|---|
| `@type` | constant `"Person"` | unchanged |
| `@id` | `config.PERSON_ID` | == portfolio `#person` (merge anchor) |
| `name` | `config.AUTHOR_NAME` | unchanged |
| `url` | site root | unchanged (full node only) |
| `jobTitle` | `config.AUTHOR_ROLE` | "Senior Android Engineer" — grounded |
| `knowsAbout` | **`config.AUTHOR_KNOWS_ABOUT`** (NEW) | verbatim from portfolio `knowsAbout` |
| `sameAs` | `config.AUTHOR_SAMEAS` | == portfolio `sameAs` (locked by verifier) |

Lean reference node (`publisher`, index `blogPost[].author`) stays `@id`+minimal — no `knowsAbout`.
No second `Person` entity anywhere. `AUTHOR_KNOWS_ABOUT` is the only new constant.

```
config.AUTHOR_KNOWS_ABOUT = [
  "Android development", "Kotlin", "Jetpack Compose", "MVI", "MVVM", "Clean Architecture",
  "Multi-module architecture", "Coroutines", "Dagger/Hilt", "Server-Driven UI", "Android TV",
  "Spec-driven development", "Agentic code generation",
]  # === portfolio index.html Person.knowsAbout, verbatim + same order
```

## 2. Heading anchor (derived; `scripts/blog/markdown_render.py`)

A per-post, document-ordered id attached to each rendered body heading. Not stored, not authored —
computed at render time and emitted into static HTML.

| Property | Rule |
|---|---|
| `id` | GitHub-style slug of heading visible text (NFKD→ASCII, lowercase, non-alnum→`-`, trim) |
| collision | deterministic numeric suffix `-1`, `-2`, … within the page (document order) |
| empty-slug fallback | `section-<n>` (n = 1-based heading index) |
| scope | body h2–h4 only; never the post `<h1>` |
| stability | function of (heading text, order) only → byte-identical across rebuilds |

State: a per-render allocator (`seen: dict[str,int]`) — post-scoped, so no cross-post collision and
fully reproducible. No global/build-wide state, no `today()`, no randomness.

## 3. Sanctioned font-data zone (portfolio `index.html`)

| Element | Value |
|---|---|
| markers | `<!--PORTFOLIO-FONTS:START-->` … `<!--PORTFOLIO-FONTS:END-->` around the `@font-face` `<style>` |
| original faces | 54 (`JetBrains Mono` 12, `Manrope` 30, `Space Grotesk` 12) across 6 subsets |
| retained | Latin + Latin-ext = 22 faces |
| removed (when landed) | Cyrillic, Cyrillic-ext, Greek, Vietnamese = 32 faces (~242 KB decoded / ~323 KB base64 source) |
| baseline | `assets/portfolio-fonts/index.baseline.html` (full original, not served) |
| mutation rule | delete whole `@font-face` blocks only; never edit a retained face |

## 4. Category (taxonomy) — unchanged shape, asserted behavior

No model change. Existing `Category{name,label,palette}` from `categories.yml`. The feature only adds
verifier assertions that declared empty categories (Compose, Architecture) render gracefully and that a
future post in any category flows through unchanged. Current set: Compose (empty), Architecture
(empty), Tooling (3 posts), Crypto (empty).

## Determinism summary

Every derived shape is a pure function of committed inputs (post text, `config` constants, portfolio
`index.html`). No `today()`, no network, no randomness → same content in, byte-identical output. The
verifier re-derives heading ids and re-parses portfolio identity to prove this at build time.
