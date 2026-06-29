# Contract: Grounded Author Identity (structured data)

Governs the blog's author structured data so engines resolve one canonical Senior Android Engineer
whose expertise includes the developer-tooling/code-generation topics. Every value is grounded
verbatim in the portfolio `index.html` JSON-LD. (FR-001..FR-005, FR-017; Principle V, VIII.)

## Source of truth (portfolio `index.html` `Person`)

```
@id        : https://ehsankolivand.github.io/#person
name       : Ehsan Kolivand
jobTitle   : Senior Android Engineer
knowsAbout : [Android development, Kotlin, Jetpack Compose, MVI, MVVM, Clean Architecture,
              Multi-module architecture, Coroutines, Dagger/Hilt, Server-Driven UI, Android TV,
              Spec-driven development, Agentic code generation]
sameAs     : [https://github.com/ehsankolivand,
              https://www.linkedin.com/in/ehsan-koolivand,
              https://t.me/eksapps]
```

## Config additions (`scripts/blog/config.py`)

- `AUTHOR_KNOWS_ABOUT: list[str]` — the portfolio `knowsAbout` list, **verbatim and in the same
  order**. This is the single grounded source the blog emits.
- (`AUTHOR_ROLE` = "Senior Android Engineer" and `AUTHOR_SAMEAS` already exist and already match the
  portfolio; this feature locks them with verifier assertions.)

## Emission (`scripts/blog/seo.py` — `_author_node(base_url, full=True)`)

The **full** author node (used by `BlogPosting.author` on posts and `Blog.author` on the index) MUST
emit, in addition to the existing `@type`/`@id`/`name`/`url`/`jobTitle`/`sameAs`:

```json
"knowsAbout": ["Android development", "Kotlin", "Jetpack Compose", "MVI", "MVVM",
  "Clean Architecture", "Multi-module architecture", "Coroutines", "Dagger/Hilt",
  "Server-Driven UI", "Android TV", "Spec-driven development", "Agentic code generation"]
```

Rules:
- The **lean** reference node (`full=False`, used by `publisher` and the index `blogPost[].author`)
  stays `@id`-only / minimal — no duplication of skills there (avoids bloat; the `@id` merges).
- No second `Person` entity is created anywhere. The portfolio remains the canonical definition
  (description/address/seeks live there only); the blog reinforces via `@id` + grounded `jobTitle` +
  `knowsAbout` + `sameAs`.
- No fabricated value: the emitted `knowsAbout`, `jobTitle`, and `sameAs` MUST be exactly the
  portfolio's. Nothing tooling-specific (e.g. "Python") is added unless the portfolio asserts it.

## Invariants (verifier-enforced)

1. Every post page and the index carry a `knowsAbout` array on the canonical author node, equal to
   `config.AUTHOR_KNOWS_ABOUT`.
2. `config.AUTHOR_KNOWS_ABOUT` == the portfolio `Person.knowsAbout` (parsed from `index.html`), exact
   list + order.
3. `config.AUTHOR_SAMEAS` == the portfolio `Person.sameAs`, exact list + order.
4. `config.AUTHOR_ROLE` == the portfolio `Person.jobTitle`.
5. The blog author `@id` == `config.PERSON_ID` == the portfolio `Person.@id`.
6. The grounded list contains the bridge topics "Spec-driven development" and "Agentic code
   generation" (positioning anchor present).
