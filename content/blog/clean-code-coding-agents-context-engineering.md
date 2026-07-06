---
title: "Clean Code Didn't Make My Coding Agent Smarter. It Made It Cheaper."
description: "A controlled 2026 SonarSource study found clean code doesn't raise a coding agent's success rate, but it cuts token cost and file re-reads. Here's the mechanism, and how I scoped context with per-module CLAUDE.md files in an Android project."
date: 2026-07-06
category: Architecture
tags:
  - coding agents
  - clean code
  - context engineering
  - CLAUDE.md
  - Claude Code
  - Android
  - Kotlin
  - software architecture
  - token cost
slug: clean-code-coding-agents-context-engineering
cover:
  type: image
  src: assets/clean-code-agents-module-map.png
  alt: "Module map of a Kotlin Multiplatform app: androidApp, iosApp, and desktopApp shells over a shared composition root, a set of core modules, and per-feature module triplets each with its own CLAUDE.md context file"
---

I used to think messy code slowed a coding agent down the way it slows a person down: more confusion, more mistakes, more wrong turns. Half of that is right. The other half surprised me. In May 2026, two engineers at SonarSource ran a controlled study on exactly this question, and the result flips the usual assumption. On cleaner code, the agent didn't pass more tests. It just spent less to get to the same place.

I'd been circling the same idea from a different direction, rebuilding an Android app around hard module boundaries so an agent would have to read less of it. Here is what both the study and my own refactor taught me: with an agent, clean structure doesn't buy you correctness. It buys you cost and focus.

## What the study actually measured

The paper is [*Does Code Cleanliness Affect Coding Agents?*](https://arxiv.org/abs/2605.20049) by Priyansh Trivedi and Olivier Schmitt at SonarSource. They ran 660 trials with Claude Code on Sonnet 4.6, handing the agent 33 tasks across six repositories, each task checked by hidden tests at the app's public surface.

The headline is one sentence: cleanliness didn't move the pass rate. The clean and messy versions of each repo succeeded at the same rate. What moved was the footprint. On the cleaner code, the agent used 7 to 8 percent fewer tokens and went back to re-read files about 34 percent less often. Correctness stayed flat. Cost dropped.

That inversion is the whole point, and it's worth sitting with, because it isn't what most of us would have guessed. We assume clean code makes the machine *succeed* more. On this evidence, it makes the machine *spend* less to succeed exactly as often.

## Why the numbers are believable: minimal pairs

The design is the part I trust. Instead of timing an agent on whatever code it happened to be handed, the authors built matched pairs of repositories that behave identically. Same architecture, same dependencies, same tests, same external output. The only thing that differs inside a pair is code quality, measured as static-analysis rule violations and cognitive complexity.

They built the pairs in both directions: cleaning up a messy repo, and degrading a clean one through a pipeline they call Slopify. Because everything except cleanliness is held constant, the cost gap has one plausible cause. You can't explain it away with a different framework, a heavier dependency, or an easier task. That is a much stronger claim than a normal benchmark can make.

## The agent isn't confused. It's reading too much.

Here is the mechanism, and it has nothing to do with intelligence. A language model works inside a finite attention budget. Anthropic's own write-up on [context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) states the goal directly: find the "smallest possible set of high-signal tokens" that get the job done. As the window fills, the model's precision for finding the right detail drops. Anthropic calls the effect context rot, and notes it's a gradient, not a sudden cliff.

Messy code makes the agent read more to understand less. It chases a tangled call graph. It opens a file, loses the thread, and opens it again. It holds more state in its head just to keep track of what's going on. Every token it burns untangling structure is a token it doesn't spend on your actual change. The SonarSource numbers are what that looks like on an invoice: more tokens in, more file revisitations, same result out, higher bill.

## My version of the same fight: architecture

The study cleaned the code and left the architecture alone. I did close to the reverse. I split my Android app into modules with hard boundaries, and I gave each module its own `CLAUDE.md`, plus one `CLAUDE.md` at the project root.

![Module map of the app: thin androidApp, iosApp, and desktopApp shells consume a shared composition root; core modules (domain, platform, network, database, data, designsystem, testing) sit beside per-feature domain/data/ui triplets, and every feature carries its own CLAUDE.md context unit](assets/clean-code-agents-module-map.png)

Before, the agent carried the whole project's context to make a change in one corner of it. It loaded a large, shared context file that described everything, most of which had nothing to do with the task in front of it. After, the path is narrow. The agent reads my prompt, works out from the root file which module owns the thing I'm asking about, and pulls in only that module's context.

My dev loop got faster and cheaper for the same reason the study found: the model reads less. The drop in cost and iteration time was obvious in daily use. Its attention lands on the code that has to change, not on files it was never going to touch.

## How the scoping actually works in Claude Code

This part matters, because it's why scoped context stays lean without any effort from me. Per Claude Code's [memory documentation](https://code.claude.com/docs/en/memory), the root `CLAUDE.md` loads at the start of every session. A `CLAUDE.md` that sits inside a module does *not* load at launch. It loads on demand, the moment the agent reads a file in that module's directory.

So a project with per-module files keeps the agent's active context small by default, and expands it only into the corner it's currently working in. The setup is boring, which is the point:

1. **One `CLAUDE.md` at the repo root — the map.** Module layout, the dependency rule between layers, and a short note on which module owns what.
2. **One `CLAUDE.md` per feature and core module — the local rules.** That module's conventions, its known traps, and its short "never do" list.
3. **Keep each one short.** The docs target under 200 lines per file, because longer files cost more context and, in Anthropic's own words, reduce how reliably the agent follows them.

The root file is the routing layer. The module files are the detail. The agent walks from one to the other on its own, only when it needs to.

## The maintenance win nobody mentions

The reach of this goes past any single session. When a convention changes, I edit one module's file. Not one 800-line document that I've quietly stopped trusting because it's too long to keep true.

Scoped context is easier to keep accurate, and accuracy is the entire value of these files. A stale, sprawling context file is worse than none at all, because the agent treats it as ground truth and confidently follows the parts that are now wrong. Small files stay honest, because keeping them honest is cheap. That's the unglamorous reason this holds up over months instead of decaying into another out-of-date doc.

## What I won't claim

I want to be careful about what the evidence supports. The study measured cost and navigation, and it found success unchanged. So I'm not going to tell you clean modules make your agent fail less often. That isn't what the data shows, and I haven't measured it myself either.

What clean boundaries do, on the evidence and in my own use, is shrink how much the agent has to read. That lowers cost, and it keeps the model's attention on the part of the codebase that's actually in play. When it does get something wrong, it's wrong inside a smaller blast radius, because it loaded less of the system to begin with. That last point is my reasoning from how these models handle context, not a measured result. Treat it as a hypothesis you can test on your own repo.

And keep the scope honest on both sides. The paper is one study: six repo pairs, one agent, one model. My architecture experience is one engineer's, without a hard number attached. Neither is the last word. Both point the same way.

## The part that actually changed my mind

Maintainability used to be an argument you had with the next person who'd open your code. It still is. But now there's a second reader who opens it every day, never gets tired, and never learns your codebase well enough to stop re-reading it. That reader's confusion doesn't show up in a code review. It shows up as a line item you can measure.

The interesting thing about the SonarSource result isn't that clean code helps the agent. It's that the agent finally puts a price on the mess. For years, "this is hard to work in" was a feeling you had to talk your team into taking seriously. Now it has a number, and the number is on your bill every month.

---

## More notes

- [[compose-multiplatform-1-12-ios-fixes]]
- [[ankivoice-offline-audio-anki-decks]]
