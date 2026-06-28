---
title: "speakloop: offline interview practice for engineers who think in another language"
date: 2026-06-28
category: Tooling
description: "Why I built a fully offline CLI to practice technical interviews out loud — the 4/3/2 loop, local-only AI on Apple Silicon, and a Markdown report that names the one thing to fix next."
slug: speakloop-offline-interview-practice
tags:
  - interview-prep
  - offline-ai
  - apple-silicon
  - developer-tools
  - spec-driven-development
cover:
  type: code
  glyph: "</>"
  caption: "// tooling · speakloop · offline by construction"
---

I know the Activity lifecycle. I've chased config-change crashes through a real production app. Then an interviewer says "walk me through it," a timer starts, and my answer comes out as "the system creates new Activity instance" instead of "a new Activity instance." Persian has no indefinite article, so my brain quietly drops every "a" and "an" under pressure.

That gap is the whole problem. Not the knowledge. The speaking.

Most interview-prep tools assume the opposite. They drill algorithms, or they put a camera on your face, or they ship your voice off to someone's server for "AI feedback." None of that helped me, because the part I needed to practice was the most private part: fumbling the same sentence five times until the words land. So I built a tool that does exactly that, and never leaves my laptop.

It's called [speakloop](https://github.com/ehsankolivand/speakloop).

## The core idea: say it three times, faster each round

speakloop is a command-line tool. You hear a technical interview question spoken aloud, you hear an ideal answer, and then you answer it yourself under time pressure using the 4/3/2 method: the same answer in 4 minutes, then 3, then 2.

The compression is the point. The first round, you ramble. By the third, you've cut the filler and found the spine of the answer. It's an old impromptu-speaking technique, and it works for the same reason rewriting works — you keep what matters and drop what doesn't, except you're doing it out loud, against a clock, the way a real interview feels.

After each session, speakloop writes a Markdown report. Not a score out of ten. A short, honest debrief.

## Everything runs on your machine

Three AI models live locally: one for text-to-speech, one for speech recognition, and one language model for the grammar feedback. After a one-time download, speakloop makes zero network calls. No telemetry. No uploads. Your voice never leaves the device.

This wasn't a feature I added. It's a constraint I started with, written into the project's constitution as a non-negotiable. When the thing you're practicing is your own clumsy, accented, half-formed English, "we promise we won't misuse your recordings" is not good enough. The honest version is: the recordings physically cannot go anywhere.

It runs on macOS with Apple Silicon, on Python 3.12, through [uv](https://github.com/astral-sh/uv). The default feedback model is a local Qwen that wants about 8 GB of free memory. If your Mac can't spare that, you can route just the grammar step to a cloud model — speech and transcription still stay local, and the tool tells you exactly which bytes would leave before any of them do.

## The report tells you one thing to fix

Here's where most "AI feedback" falls apart. It gives you twelve suggestions, and you fix none of them.

speakloop separates two things that usually get tangled together. It tracks **content coverage** — did you actually hit the key points the ideal answer makes, round over round — apart from **grammar and fluency**, so a wrong fact never hides behind a missing article, and vice versa. Then it picks a single `top_priority`: the one pattern that, fixed, would most improve your next answer.

For me, that's almost always articles. The report quotes me back: "the system creates new Activity instance," corrected to "a new Activity instance," with a one-line explanation of why a Persian speaker drops it and a rule to catch it next time. Three occurrences in one session, ranked first by impact. That's a thing I can actually work on tomorrow.

The reports are plain Markdown with YAML frontmatter, saved in a folder you can open as an Obsidian vault. So your interview prep becomes a searchable, linkable record of every error you've made and beaten — which is, conveniently, exactly how I already write everything else.

## It's a loop, not a drill

A session isn't one question and done. It opens with a 30-to-60-second warm-up on your top recurring error, runs the 4/3/2 attempts, then asks one or two unscripted spoken follow-up questions built from what you actually just said — the way a real interviewer probes. Each question is scheduled for spaced repetition, so the answers you fumbled come back sooner than the ones you nailed.

There's also an optional pronunciation trainer with a tight hear → say → see → retry rhythm: it plays the sound, you say it, it flags what was off, and it hands you an immediate retry while the correction is still fresh.

## The honest edges

I'd rather you trust the tool than oversell it, so the README has a "Known limitations" section and so does this post.

A strong accent on dense technical vocabulary can still produce a wrong transcript, even though speakloop biases recognition toward each question's domain terms. If the language model isn't installed, the session degrades to fluency-only metrics instead of failing. And it doesn't yet score pronunciation at the phoneme level — it detects that a sound was off and suggests what it heard, but it won't pretend that suggestion is a verdict.

That last distinction matters to me. A tool that grades your accent with false confidence is worse than one that admits what it can't measure.

## Why I'm sharing it

speakloop is v1, MIT-licensed, and built the same way I build everything now: constitution first, then spec, then plan, then implementation, with the whole thing documented under `specs/`. It's small (8 stars and counting) and deliberately not a polished consumer app. If you want a GUI and a cloud account, this isn't that, on purpose.

But if you're an engineer who interviews in a language you didn't grow up in, and you've felt that specific frustration of knowing the answer and watching it come out wrong, this was built for you. By someone with the same problem.

Clone it, try a listen-only session first, and tell me what breaks:

👉 **[github.com/ehsankolivand/speakloop](https://github.com/ehsankolivand/speakloop)**

If it helps your prep, a star is appreciated. If you have a better prompt for the grammar feedback, open an issue — that's the part I'm still tuning.
