---
title: "A Figma plugin that writes correct Compose"
date: 2026-04-19
category: Tooling
tags: [figma, compose, design-systems, codegen]
excerpt: "Reading the design tree, mapping tokens, and emitting code the compiler — not a reviewer — validates."
slug: figma-plugin-compose
readTime: "5 min"
cover:
  type: code
  glyph: "▤"
  caption: "// cover: figma → token map → Composable"
---

A design system is only as good as the gap between Figma and the code that ships. We closed most of that gap with a plugin that reads the design tree and emits Compose the compiler will accept.

## Tokens, not screenshots

The plugin doesn't try to recreate the pixels. It walks the node tree, maps each style to a design-system token — color, type, spacing, radius — and refuses to emit anything that isn't a known token. If a designer used a one-off hex, it flags that instead of hard-coding it.

- Walk the Figma node tree and resolve component variants.
- Map every value to a typed token, or fail loudly.
- Emit Composable functions — not XML, not screenshots.
- Round-trip: the output compiles in CI, not just in a demo.

![// figma node tree → token resolver → Composable]()

The point was never to remove engineers from the loop. It was to delete the boring, error-prone transcription — so we could spend the meeting arguing about the things worth arguing about.

---
## More notes
- [[spec-driven-android]]
- [[custom-layouts-compose]]
