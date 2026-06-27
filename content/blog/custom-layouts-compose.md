---
title: "Custom layouts in Jetpack Compose without losing your mind"
date: 2026-06-02
category: Compose
tags: [compose, layout, ui]
excerpt: "Measure, place, repeat. A practical mental model for writing your own Layout — and knowing when to actually reach for one."
slug: custom-layouts-compose
readTime: "6 min"
cover:
  type: code
  glyph: "◳"
  caption: "// cover: measure → place"
---

Compose ships with Row, Column and Box, and ninety percent of the time that's all you need. The other ten percent is where Layout earns its keep — and writing your own is far less scary than that first @Composable fun Layout signature suggests.

## Measure, then place

Every custom layout is the same two-step dance. You measure your children inside the constraints you're given, decide how big you want to be, then place each child at an offset. That's the whole job. The mental model never gets more complicated than that.

```// StaggeredColumn.kt
@Composable
fun StaggeredColumn(
  modifier: Modifier = Modifier,
  gap: Dp = 8.dp,
  content: @Composable () -> Unit,
) = Layout(content, modifier) { measurables, constraints ->
  val placeables = measurables.map { it.measure(constraints) }
  val height = placeables.sumOf { it.height } +
               gap.roundToPx() * (placeables.size - 1)
  layout(constraints.maxWidth, height) {
    var y = 0
    placeables.forEach { p ->
      p.placeRelative(0, y); y += p.height + gap.roundToPx()
    }
  }
}
```

## When to reach for it

- Your rule can't be expressed with weights, arrangements or alignment.
- You're fighting Modifier chains to fake something a Layout would say directly.
- You need to measure children against each other — a bubble capped at 75% of the row.

If you find yourself nesting four Boxes to coax one behaviour out of the framework, that's the signal. Drop down to Layout, write the measure-and-place by hand, and the code usually gets shorter — not longer.

---
## More notes
- [[mvi-that-scales]]
- [[figma-plugin-compose]]
