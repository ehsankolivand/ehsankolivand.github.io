# Contract: categories.yml

The single, author-owned declaration of the canonical category set. Path:
`content/blog/categories.yml`.

## Schema

```yaml
# Ordered list. Order here = order in the index nav (after the always-present "All").
# `name` is the stable key posts reference in their `category:` field.
# `label` is the display text (defaults to name if omitted).
# `palette` (optional): 'mint' | 'sand' — overrides the automatic chip color.
- { name: Compose,      label: Compose }
- { name: Architecture, label: Architecture }
- { name: Tooling,      label: Tooling }
- { name: Crypto,       label: Crypto, palette: sand }   # optional explicit palette
```

## Rules

- The file MUST be a YAML list of mappings, each with at least `name`.
- `name` values MUST be unique.
- The "All" view is implicit and always rendered first; it is NOT listed here.
- A post whose `category` is not a `name` in this file is a build error (FR-006).
- Adding / reordering / relabeling entries here changes the index nav, post chips, and
  `articleSection` metadata on the next build with no code change (FR-005, SC-007).
- The category chip color follows the design palette automatically (mint for Tooling/Compose,
  sand otherwise), matching the existing design's `_tagStyle`.
- An optional per-entry `palette: mint | sand` overrides that automatic color. Omit it to use
  the default; any value other than `mint`/`sand` is a build error.
