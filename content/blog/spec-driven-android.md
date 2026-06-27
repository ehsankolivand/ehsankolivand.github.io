---
title: "Spec-driven Android: generating modules an AI can't get wrong"
date: 2026-06-18
category: Tooling
tags: [android, codegen, ai, architecture]
excerpt: "Replacing \"ask the model and hope\" with deterministic generators that turn a design-system spec into modules, screens, ViewModels and APIs — correct by construction, not guessed."
slug: spec-driven-android
readTime: "9 min"
cover:
  type: code
  glyph: "{ }"
  caption: "// cover: spec → generators → feature module"
---

For two years I shipped a DeFi suite where a single wrong field in a transfer screen could cost someone real money. So when people started 'vibe-coding' whole features by asking a model and pasting the result, I felt what every banking engineer feels: that's not a workflow, it's a liability.

## The problem with guessing

A language model is a probabilistic engine. It's wonderful at the fuzzy middle of a task and unreliable at the edges — and in a multi-module banking app, the edges are the whole game: the exact API contract, the navigation route, the DI graph, the state class the rest of the screen depends on. Let it guess those and you spend your whole review budget hunting for the one field it quietly renamed.

> The model should write the parts that are genuinely creative. Everything that is merely correct should be generated, not guessed.

## Specs first, code second

The fix was to stop treating generation as ask-and-hope and start treating it as a compiler with a human front-end. Every feature begins as a small, declarative spec — the module name, the screens, the state object, the intents, the API. That spec is the single source of truth.

```// wallet-topup.feature.yaml
feature: wallet-topup
module:  feature_wallet
screens:
  - TopUpAmount
  - TopUpConfirm
state:   TopUpState
intents: [EnterAmount, Submit, Retry]
api:     POST /v2/wallet/topup
```

From that file, deterministic generators emit the module, the ViewModels, the repository, the API interface and the navigation wiring. No model is asked what a TopUpState should contain — the spec already said. The model is only invited in for the parts that actually need judgement: the body of a non-trivial use case, an animation, a gnarly validation rule.

## Determinism beats cleverness

- Same spec in, byte-identical code out — every diff is reviewable.
- The compiler validates the result, not a tired reviewer at 6pm.
- New engineers read the spec, not four thousand lines of boilerplate.
- The AI's surface area shrinks to exactly where it's actually good.

![// module graph: spec → generators → feature module]()

## What it changed for the team

Scaffolding a new feature went from an afternoon of careful copy-paste to a thirty-second command. More importantly, the generated layer stopped showing up in code review at all — there was nothing to argue about, because nothing was guessed. We got to spend our attention on the things that were actually hard. That, to me, is what 'agentic' should mean.

---
## More notes
- [[figma-plugin-compose]]
- [[mvi-that-scales]]
- [[sole-owner-defi]]
