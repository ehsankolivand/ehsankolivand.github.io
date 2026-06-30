---
title: "AnkiVoice: turn text Anki decks into native-audio decks, fully offline"
date: 2026-06-28
category: Tooling
description: "A Telegram bot that adds clear, native-accent English audio to your Anki cards — generated locally with Kokoro-82M on a 4 GB VPS, no cloud TTS, your text untouched."
slug: ankivoice-offline-audio-anki-decks
tags:
  - anki
  - offline-ai
  - text-to-speech
  - telegram-bot
  - spec-driven-development
cover:
  type: code
  glyph: "♪"
  caption: "// tooling · ankivoice · local TTS on a 4 GB box"
---

I read English fine. I write it fine. But I learned half my vocabulary from text, which means for years I was confidently mispronouncing words I'd never actually heard out loud. "Determine." "Architecture." "Niche." Reading a flashcard teaches you the spelling and the meaning. It teaches you nothing about how the word sounds.

Anki is the obvious fix, except most decks are text on both sides. You flip the card, you read the answer in your own head with your own accent, and you reinforce the wrong pronunciation one more time.

So I built a thing that fixes that, and never sends my cards to anyone.

It's called [AnkiVoice](https://github.com/ehsankolivand/AnkiVoice).

## What it does

AnkiVoice is a Telegram bot. You send it a plain text Anki export — tab-separated, Front then Back — and it sends back an `.apkg` where revealing a card's answer auto-plays clear, native-accent English audio, with a replay button if you want to hear it again.

Your original card text is preserved exactly. Audio is added, nothing is rewritten. That mattered to me: I didn't want a tool that "improves" my decks behind my back. I wanted one that does one job and leaves everything else alone.

The speech comes from Kokoro-82M, an open text-to-speech model that runs locally on CPU. American voice by default, British if you flag it. You can have it voice just the answer side, or both the question and the answer.

## The constraint that shaped everything: a 4 GB VPS

Here's the design decision the whole project hangs on. AnkiVoice is built to run on a single CPU core with about 4 GB of RAM.

That's a deliberately cheap, deliberately small box. No GPU. No cloud TTS API billing you per character. No sending your study material to a third party so they can "generate" the audio. The model lives on your server, the synthesis happens on your server, and after the one-time warm-up download the running bot needs no inbound port, no TLS, and no reverse proxy. It just outbound-polls Telegram.

Cheap and offline aren't compromises here. They're the point. A study tool you fully own is worth more than a slicker one that rents you access to your own flashcards.

## How a card actually becomes audio

The pipeline is boring on purpose, which is the best compliment I can pay a piece of infrastructure: ingest → synthesize → package → deliver.

A deck comes in. It gets parsed and cleaned for speech. Kokoro synthesizes each line, ffmpeg encodes it to MP3, and genanki packages it into an `.apkg` with the `[sound:]` auto-play wired onto the answer side. Then it's delivered, a backup copy goes to an archive channel, and every working file for that job is deleted.

The part I'm quietly proud of is the queue. Jobs run through a durable SQLite store, strictly first-come-first-served, exactly one synthesis at a time, one active job per user. If the bot restarts mid-deck, the job resumes instead of vanishing. On a 4 GB box you cannot afford two syntheses fighting over memory, so the system simply never lets that happen. Delivery of one deck overlaps synthesis of the next, so serial doesn't mean slow.

There's also a fail-fast guard at startup. If ffmpeg is missing, or the voice and model can't synthesize offline, the bot refuses to start and tells you exactly why — rather than booting up and producing silently-wrong audio on your first real deck. It proves it can speak before it claims it's ready, using a one-word out-of-dictionary probe that doubles as a model warm-up.

## One command to deploy

I didn't want a README with twelve setup steps that rot the moment a dependency moves. On a clean Debian 12 or Ubuntu LTS box, deployment is one command:

```bash
sudo ./install.sh --token <BOT_TOKEN> --archive-id <ARCHIVE_CHAT_ID>
```

That installs ffmpeg and uv, creates a dedicated service user, provisions the app, does the one-time model warm-up so the bot then runs fully offline, writes a locked-down `.env` it will never overwrite, and installs a systemd service that auto-restarts and survives reboots. Re-running the same command is how you update — it refreshes the code and dependencies and never touches your secrets. The full spec lives under `specs/003-one-command-deploy/`.

You need exactly two things to start: a bot token from @BotFather, and an archive chat id where the bot drops a backup of every deck it delivers.

## Built spec-first

Like everything I ship now, AnkiVoice was built spec-first with GitHub Spec Kit. The constitution, spec, plan, research, and task breakdown all live in the repo under `specs/001-ankivoice-audio-decks/`, and the code is deliberately split into small, single-responsibility modules — parsing, speech, encoding, packaging, the queue, cleanup, delivery — each one easy to read and easy to reason about.

That's not ceremony for its own sake. When the rules ("offline-only," "never mutate the user's text," "one synthesis at a time") are written down before the code exists, the code has something to be checked against. The constraints stop being vibes and start being tests.

## Try it

AnkiVoice is open source. If you study a language through Anki and you're tired of guessing how words sound, send a deck through it and hear the difference. If you run a small VPS, the one-command installer will have a bot live in a few minutes.

👉 **[github.com/ehsankolivand/AnkiVoice](https://github.com/ehsankolivand/AnkiVoice)**

It pairs naturally with my other offline tool, [speakloop](https://github.com/ehsankolivand/speakloop), which is the speaking half of the same idea: AnkiVoice teaches your ear what a word should sound like, speakloop puts you on the clock to say it back. Both built on the same stubborn principle — your voice and your study material stay on your own machine.
