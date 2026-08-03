---
title: "I Spent Twelve Days Trying to Cut My Coding Agent's Token Use by 30%. The Answer Was Arithmetic, Not Code."
description: "A semantic index plus a compiler-grade call graph did not cut my coding agent's token bill. It came out 4.4% more expensive. Here is the arithmetic that made the 30% target impossible, and the one job the tool is genuinely good at."
date: 2026-08-03
category: Tooling
tags:
  - coding agents
  - MCP
  - token cost
  - context engineering
  - Kotlin Multiplatform
  - Android
  - semantic search
  - code retrieval
  - negative result
  - benchmarking
slug: semantic-index-coding-agent-token-cost
cover:
  type: code
  glyph: "%"
  caption: "// tooling - repo-intel - reductionTokens = -0.0439 vs a 0.30 floor"
---

**Short answer: no, a semantic index of your codebase will not cut your coding agent's token use.** My last committed measurement reads `reductionTokens = -0.0439` against a `0.30` floor — the tool came out 4.4% *more* expensive than working without it. And that is not an implementation failure. To reach 30%, the tool arm had to shed 51,870 tokens per session, while everything it produced — every response, every file read, every grep — came to 38,665 tokens. Even with the tools silent and the agent reading nothing, the target sits out of reach.

The same tool earned its place at a different job: structural questions on a large codebase. `impact_of` — what breaks if I change this — measured 17.6% cheaper than working the same question out by hand, worth 51,340 tokens per query.

This is the whole route, from the observation that started it to the arithmetic that ended it. Every number comes from my own project artifacts, and [the repo is public](https://github.com/ehsankolivand/CodeBaseBrain).

## Why do coding agents work worse on Android projects?

**Because an Android codebase fills the context window sooner, and output quality falls as that window fills — well before it is actually full.**

I noticed this as a feeling first. The same model that answered cleanly in my Python and backend projects answered carelessly in my Android one. The model had not changed. The codebase had.

The cause is structural. An Android or KMP project carries several modules, each with several source sets, and generated layers sit on top of all of it — Compose resources, BuildKonfig, Apollo or Wire output. To answer one ordinary question, the agent has to walk several modules and open several files. The model has not reached the problem yet and the window is already full.

That feeling has been measured. [Chroma's Context Rot research](https://www.trychroma.com/research/context-rot) tested 18 frontier models — GPT-4.1, the Claude 4 family, Gemini 2.5, Qwen3 — and found: "performance degrades consistently with increasing input length" across every experiment. Not some models. All of them. And the decline starts long before the window fills.

Stanford's complementary result puts a shape on it: accuracy follows a U-curve, and information sitting in the middle of the context takes the worst of it. Birgitta Böckeler, writing on martinfowler.com in February 2026, drew the same conclusion from practice: "an agent's effectiveness goes down when it gets too much context."

So the problem is not a weak model. The problem is that Android codebases naturally produce longer inputs, and input length carries an accuracy cost of its own.

## Does clean architecture solve it?

**No, though it helps.** This is the first thing anyone says, and it is a correct answer that does not fix the problem.

The project I work on has 9 modules, clear boundaries, and a module layout I designed myself. The window still fills sooner than in my web project. Clean modularisation does not reduce the *number* of files the agent has to see; it only tidies them. To answer "what calls this," the agent has to search — and searching means reading.

Cognition measured this in coding agents specifically: agents spend more than 60% of their first turn just searching.

That number is what gave me the idea.

## What if the agent did not have to search?

**Build the map of the codebase once, hand it to the agent, and it never has to rediscover the structure.** That was the hypothesis I built.

The tool is called `repo-intel`. It builds a semantic index plus a compiler-grade declaration graph of a Kotlin, Android or KMP project, and serves both to two places: to Claude Code over MCP as five tools, and to me through an Android Studio tool window.

Four retrieval lanes sit behind it. A BM25 lexical lane on Apache Lucene with a code-aware analyzer. A dense lane on the same Lucene index, with `qwen/qwen3-embedding-8b` embeddings truncated to 2048 dimensions via Matryoshka. A rerank lane running `Qwen3-Reranker-0.6B` locally on `llama-server`. And the graph, built with the standalone Kotlin Analysis API out of process, persisted to SQLite.

I wrote the hypothesis as a measurable claim from the start: **an agent with a map should finish the same task on 30% fewer tokens.** The baseline was an agent with grep, burning 88,948 tokens per question.

Miss that target and the project had not earned its complexity.

## How many tokens did it save?

**None. It spent more.**

The measurements ran like this:

| Measurement | Result |
|---|---|
| First | 11.8% more expensive than grep |
| Second | 29.7% more expensive — which later turned out to have measured nothing |
| Third (published) | 10.8% more expensive |
| Last (committed) | **4.4% more expensive** |

At first I assumed I had a bug. I didn't.

The second number has a story of its own worth telling. Forensics on the raw transcripts showed the graph had answered **zero of forty-four** calls. Twenty-one were permission denials, twenty-one were rejections, two were crashes. I had published a number that measured nothing.

Accuracy went up, though, and stayed there. On the twenty-question benchmark set, the tool answered 20 of 20 correctly against grep's 18 of 20.

## Why was the 30% target impossible from the start?

**Because most of the tokens in a session are not mine.**

A dedicated investigation asked one question: where do the extra tokens actually go? The answer was arithmetic, not engineering.

**69% of every session is untouchable** — roughly 21,217 tokens belonging to Claude Code itself: its own system prompt, its twenty-two built-in tools, and its memory, re-read on every single call.

To clear the 0.30 floor, the tool arm had to shed 51,870 tokens. **Its entire payload is 38,665 tokens.** The target was dead before I wrote a line of it.

Worse: **the metric is essentially a call-count ratio.** The billed-call ratio computes to `+0.0192` against a measured `reductionTokens` of `+0.0224` — a gap of three thousandths. Everything the investigation priced — an 8,292-token prefix, 12,604 tokens of responses, 16,623 tokens of file reads, 7,266 tokens of greps — moves the published number by three thousandths. Only round trips count, and nothing the project ships can force the agent to batch them.

The last nail: **the measurement apparatus cannot see the effect I was chasing.** The 95% confidence interval on the paired metric is `[−0.144, +0.143]` — twenty-eight points wide. The probability of demonstrating a 30% reduction is zero. The control arm itself moved 1.1% between two runs on identical questions. Resolving a 4.5% effect from zero would take roughly 200 queries, not 20.

## Why don't other tools' 90% numbers match mine?

**Because the baseline differs, not the tool quality.**

This needs saying plainly, because big numbers are common in the MCP space. `codebase-memory-mcp` claims a 99.2% reduction on its own README: about 3,400 tokens against about 412,000 for five structural queries.

An [independent reproduction](https://pantheon-org.github.io/agentic-context/benchmarks/deusdata-codebase-memory-mcp/) confirmed the compact output but recorded three conditions: the baseline was file-by-file grep rather than focused reads or optimised RAG; the run covered a single undisclosed repository; and "tokens" counted the entire answering session, including the model's own reasoning.

A separate [independent analysis](https://particula.tech/blog/semantic-code-search-vs-grep-coding-agents) reaches the same conclusion: the gap between a 40% claim and a 98% claim is not one tool being wildly better than another, it is what each was compared against.

And another builder published [a 60-task hand-verified evaluation](https://sverklo.com/blog/i-benchmarked-code-retrieval-for-ai-agents/) in which tuned grep beats his own MCP server on F1.

I measured whole sessions against a baseline I would defend in a review. Different question, different answer.

## What happened when I applied the obvious fix?

**Half the predicted saving arrived, and the agent spent the other half.** This is the most interesting thing I learned in the whole project.

Forensics showed the tool arm makes **0.65 more billed calls** per session, and that one difference accounts for **95.7% of the entire deficit**. The cause: Claude Code defers MCP tool schemas by default, so each session spent one `ToolSearch` call discovering them. This overhead is a known phenomenon — [issue 2808 in the MCP repository](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/2808) records it at roughly 1,000 tokens per tool.

The fix was three files: `alwaysLoad: true` on the MCP server, so the schemas load up front.

| Metric | Before | After |
|---|---|---|
| `ToolSearch` calls | 20 across 20 sessions | **0** |
| Billed calls | 5.85 | **5.10** |
| Tool arm tokens | 167,646 | **157,457** |
| `reductionTokens` | −0.1083 | **−0.0439** |

The mechanism worked perfectly. **Only 51% of the predicted saving materialised.**

**60.6% of the shortfall was a change in the agent's own behaviour.** Given the tools earlier in the session, it read *more* files, not fewer: reads after a tool answer went from 58 to 66, and mean files opened from 2.8 to 3.3. I handed it a shortcut and it spent the freed budget double-checking me.

The lesson I wrote down: **a simulation that assumes fixed agent behaviour will overpromise.**

A related problem I still have not solved: **in 52 of 58 cases, the agent's read after a tool answer opened the exact file the tool had just named.** The tool hands back a correct answer with the file name attached, and the agent goes and looks anyway.

And the fix my own two prior reports had ranked #1 — attaching evidence provenance so the agent would stop reopening files it already had answers for, costed at 31,717 tokens — measured out at **1,735 tokens** of real value. About one twentieth of what it was sold at.

## So what is the tool actually good for?

**Structural questions a text search cannot express.** I found this by reading the results per question class instead of by average.

| Question class | Token change |
|---|---|
| `impact_of` | **17.6% cheaper** (51,340 tokens per query) |
| Graph class (`who_calls` + `impact_of`) | 9.9% cheaper |
| `exact_regex` | 22.6% more expensive |

My evaluation set held 12 retrieval questions and 8 graph questions — weighted toward the class where the tool loses to grep by design. Twelve days grading a hammer on how quietly it turns screws.

Then I ran it against fourteen real questions from my own production KMP app, not a benchmark fixture. **All fourteen answers were correct**, each verified against an *independent* observation — a grep over the working tree, or reading the named file — never the tool agreeing with itself.

Three results are worth naming.

`impact_of` on `PlatformContext` returned `coverage.complete = false` with two non-indexed actuals. On real iOS and JVM code, it declared its own incompleteness rather than quietly under-reporting the blast radius.

`impact_of` on `collectAsStateMultiplatform` returned **zero**, and a grep confirmed the extension genuinely has no call sites. A trustworthy zero beats a list — confirming "nothing uses this" with grep means convincing yourself the grep was exhaustive.

`who_calls` on `HttpClientFactory` exposed a real gap in the payload: two reference *sites* inside one *caller*. A surface labelling the total as "callers" would report 2 where the truth is 1. Both numbers now travel with the answer.

Of those fourteen, **I would have reached for it again in 9**. That is an operator judgment, not an observation of behaviour — nobody watched me work, and every project record carries the same label.

**The split is itself the finding.** The five cases grep or Go-To-Declaration would have answered faster were all one shape: *where is X defined*. The nine worth reaching for were blast radius across source sets, cross-module dependents including test doubles, and behavioural questions whose vocabulary you cannot guess in advance.

And for direct human use from the command line or the IDE, **the model-token cost is zero** — it is a local index query.

## What was I measuring wrong?

**Two things had never been measured at all, and both sat under my nose for months.**

First: **the dense retrieval lane was switched off in 100% of every session ever run.** The measurement harness scrubbed the API credential from the child process. The system reported `lanes_available` honestly on *every response*. Four cycles of measurement passed through it and nobody read it, including me.

Second, and worse: **the shipped plugin did not load.** After running the installer in a clean project on Claude Code 2.1.220, `mcp_servers` was empty, zero tools were advertised, the session hook never fired, and the skill never appeared. Meanwhile **`claude plugin validate` passed.**

Which means every measurement I had ever taken of the tool arm reflected a wiring the harness constructed by hand — a configuration no user of the installer ever received. The product had never been installed by anyone, including its author.

The root cause was established empirically: Claude Code 2.1.220 does not read `<project>/.claude/plugins/`. The discovery root is `~/.claude/skills/<name>/`. A bundle in the wrong location passes validation and is never loaded, because validation checks that the manifest is well-formed, not that the location is read.

**Two lessons came out of this. A validator's PASS is not a load. And the measurement environment can differ from the human's environment even when both are called "the product path."**

On 3 August I installed it myself for the first time. Three defects surfaced within minutes that 1,118 tests and 92 review findings had not: the CLI crashed in an interactive terminal (the terminal library fails on macOS ARM reading the window size, but only when stdout is a TTY — piped, it works perfectly), the rerank lane was missing in live use, and the keyboard shortcut collided with an existing Android Studio binding.

**Every product-path verification in the previous cycle had run under a pipe**, because the harness reads the output.

## What would I do differently from day one?

**Three things, all before writing a line of code.**

**Build the evaluation set balanced by question class, not by what is easy.** Twelve retrieval questions against eight graph questions meant the headline result was decided in advance. Had I drawn the distribution from my actual work, I would have known in week one what the tool was good at.

**Compute the statistical power before choosing the metric.** At 20 queries the confidence interval is twenty-eight points wide, so any number landing inside it is indistinguishable from noise. That calculation takes five minutes and would have saved four cycles.

**Verify the product through the real user path from day one, not through the harness.** Run the installer, open a real session, and read what the *running surface* reports — not whether the files were written.

And one thing I got *right* and will keep: **I wrote the stop condition into the spec in advance.** If both readings came out negative and the token reading was ≤ −0.20, the project would close with a published negative result. That condition was written before the numbers were known, which is the only time such a condition means anything.

## What was proven, and what wasn't

**On the original goal — token savings — the answer is no, and it is arithmetic rather than opinion.** The realistic ceiling after fixing every remaining defect is roughly parity: somewhere between 1% worse and 4.5% better, inside a noise band of ±14%. Even a real improvement that size could not be demonstrated with the current twenty-query apparatus.

**On accuracy the answer is yes, and it is measured.** 14 of 14 correct on real production questions, each independently verified. 20 of 20 against grep's 18 of 20 on the benchmark set. These are two different measurements and they are not interchangeable.

**On the one capability the tool was built for, it wins on both counts at once:** `impact_of` is 17.6% cheaper in tokens *and* answers a question a text search cannot express at all. "What breaks if I change this" has no grep equivalent.

And **one question remains unmeasured**: whether I reach for it during real work over a period of weeks. Everything above is either a benchmark or a scripted session. That measurement starts now, and honestly recording *not* reaching for it counts as data of equal value.

After all of it, I still think there is a way to get better output from agents on Android codebases. I just no longer think that way runs through cutting tokens.

## Want to try it?

The repo is here: **[github.com/ehsankolivand/CodeBaseBrain](https://github.com/ehsankolivand/CodeBaseBrain)**

Every cycle report, the token deep dive, and the review logs are all committed — including the numbers that were retracted, and why.

Two things to know before you clone it. macOS and JDK 21 only. And the README's Known Issues section is honest about what is still rough.

If you have found a way to make agents work as well on an Android codebase as they do on your frontend and backend, write to me: `ehsankolivandeh@gmail.com`

*Every number in this article comes from the artifacts of the [CodeBaseBrain](https://github.com/ehsankolivand/CodeBaseBrain) project — cycle reports, evaluation transcripts, and test results read from XML files. The entire history spans twelve days, from 22 July to 3 August 2026.*

---
## More notes
- [[clean-code-coding-agents-context-engineering]]
- [[codex-plugin-claude-code-cross-model-review]]
