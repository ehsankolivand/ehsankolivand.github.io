---
title: "Server-driven UI: shipping screens without shipping the app"
date: 2026-05-06
category: Architecture
tags: [sdui, architecture, backend]
excerpt: "We moved promo surfaces, onboarding and feature flags to the backend. Here's the contract that kept it sane."
slug: server-driven-ui
readTime: "6 min"
cover:
  type: code
  glyph: "☰"
  caption: "// cover: server → schema → native render"
---

Some screens change faster than your release cycle. Promo banners, onboarding order, which feature is live in which country. Server-driven UI moves those decisions to the backend so a screen can change without a single line shipping to the store.

## A contract, not a free-for-all

The trap is letting the server send arbitrary UI — that just moves your spaghetti across the network. The discipline is a closed schema: a fixed catalogue of block types the client knows how to render, composed in any order the server likes.

```// home.screen.json
{
  "screen": "home",
  "blocks": [
    { "type": "hero",  "title": "Welcome back" },
    { "type": "promo", "ref": "summer_yield" },
    { "type": "list",  "source": "/v2/feed" }
  ]
}
```

- Client owns the components; server owns the composition.
- Unknown block type? Render nothing and log it — never crash.
- Version the schema so older apps degrade gracefully.

Done with restraint, you get the flexibility of a web page with the polish of native — and your growth team stops filing tickets that begin with 'can we just move the banner...'.

---
## More notes
- [[mvi-that-scales]]
- [[spec-driven-android]]
