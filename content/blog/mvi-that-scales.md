---
title: "MVI that scales: one state, one source of truth"
date: 2026-05-21
category: Architecture
tags: [mvi, architecture, state, crypto]
excerpt: "Intents in, state out, side-effects on the side. Why a single immutable state object made our crypto app genuinely debuggable."
slug: mvi-that-scales
readTime: "7 min"
cover:
  type: code
  glyph: "↺"
  caption: "// cover: intent → reducer → state"
---

On a crypto app, the worst bugs aren't crashes — they're states that shouldn't exist. A screen that's loading and showing an error at once. A confirm button that's tappable while a request is already in flight. MVI exists to make those states unrepresentable.

## One state object

The whole screen is described by a single immutable State. The UI is a pure function of it. Intents flow in, a reducer produces the next State, side-effects are handled separately and never mutate the UI directly. When something looks wrong on screen, there is exactly one object to inspect.

```// TopUpContract.kt
sealed interface Intent {
  data class EnterAmount(val raw: String) : Intent
  data object Submit : Intent
}

data class State(
  val amount: Long = 0,
  val loading: Boolean = false,
  val error: String? = null,
)
```

> If a screen can't be drawn from a single data class, the bug is in your model — not your view.

- Reproduce any screen by constructing its State in a test.
- Time-travel: log every State and replay the exact path into a bug.
- No more 'which of six booleans is the real source of truth' meetings.

It's more ceremony up front than wiring a few LiveDatas together. It pays that back the first time QA hands you a State dump and you fix the issue without ever reaching for the debugger.

---
## More notes
- [[server-driven-ui]]
- [[sole-owner-defi]]
- [[spec-driven-android]]
