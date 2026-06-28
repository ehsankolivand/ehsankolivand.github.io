---
title: "I got added to a 10,000-message Telegram group. I read none of it."
date: 2026-06-28
category: Tooling
description: "A small Python script that exports any Telegram group or topic to an LLM-friendly Markdown file — so you can drop it into NotebookLM and get a summary, a timeline, and the key points in minutes instead of days."
slug: telegram-topic-export-markdown-jsonl
tags:
  - telegram
  - python
  - notebooklm
  - llm-tooling
  - developer-tools
cover:
  type: code
  glyph: "≡"
  caption: "// tooling · telegram → markdown → notebooklm"
---

A few months ago someone added me to a Telegram group. Thousands of messages, dozens of topics, months of history I'd missed. The useful stuff was all in there somewhere: decisions, links, the one person who actually knew the answer. But it was buried under thousands of "thanks 🙏" and forwarded memes, and I was never, realistically, going to scroll back and read all of it.

Then it clicked. I didn't need to read the group. I needed a summary of it. And we now have tools that are very good at summarizing a pile of text — they just need the text.

The problem is that Telegram doesn't hand you the text. You can scroll, and that's about it. There's no "export this topic as something an AI can read" button. So I wrote one.

## What it does

It's a small Python script. You give it a link to a group or topic, you log in once in your terminal, and it pulls the messages down and writes them out as a clean, LLM-friendly Markdown file. That's the whole loop.

The point isn't the file. The point is what you do with the file next. I drop the Markdown into [NotebookLM](https://notebooklm.google.com) — it takes Markdown directly — and then I ask the questions I actually had: summarize the last three months, build me a timeline of what was decided, list the resources people shared, tell me who keeps answering the hard questions. NotebookLM will generate a literal Timeline view and a briefing doc from a source like this, and because it only answers from what you uploaded, it isn't making things up about a group it's never seen.

In about ten minutes I went from "I have no idea what happened in here" to caught up. That's the entire reason this exists.

## A couple of details I care about

Under the hood it runs on Telethon, with your own API credentials from my.telegram.org, so you're reading through your own account rather than scraping anything.

Two choices matter more than the export itself.

It indexes reply previews in a small SQLite database, so the flattened export doesn't turn into nonsense. When a message is a reply, you can still see what it was replying to. A conversation stripped of its reply structure reads like half of a phone call. This keeps the thread intact, which also makes the AI summary far more accurate.

And media is opt-in. Leave it off and you get just the text and metadata. Turn it on and it downloads the files. On a big group that's the difference between a tidy Markdown file and a four-gigabyte folder of stickers you'll never look at.

There's also a second script that splits a huge export into smaller parts on message boundaries, never mid-message. I didn't understand why I needed it until a really active group produced a file big enough to bump against NotebookLM's per-source ceiling (around 500,000 words). Split it into parts, upload the parts, done.

## Honest about what this is

This isn't a polished product. It's a couple of scripts with constants you edit at the top of the file, no installer, no UI. It's older than most of what I publish now and it predates the spec-first workflow I use today.

But it solved a real, specific annoyance of mine, I posted it, and far more people than I expected said it solved theirs too. For something this small, that's the right amount of tool. Anything fancier would just be in the way.

## Try it

If you're sitting on a busy group or topic you don't have the hours to read, point this at it, export it, and let an AI do the catching up for you.

👉 **[github.com/ehsankolivand/telegramExtractor](https://github.com/ehsankolivand/telegramExtractor)**

You'll need Python 3.9 or newer, `pip install telethon`, and a Telegram API app from my.telegram.org. Edit the constants at the top, run it, and you'll have your group as a Markdown file that's ready to upload and ask questions of.

If you end up using it, tell me what you asked your group once it was finally readable. That part's been the most fun.
