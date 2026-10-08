---
name: anti-ai-slop-writing
description: "Draft authentic prose and UI copywriting avoiding formulaic AI writing patterns, clichés, parataxis, and template headlines. Blended with github.com/miqdadbadjuber/anti-slop (antislop-copywriting)."
version: 3.0.0
---

# Anti-AI-Slop Writing & Copywriting Directive v3.0

Produces authentic prose, technical documentation, and UI copywriting that eliminates statistically detectable AI patterns. Integrates `anti-ai-slop-writing` with [`antislop-copywriting`](../antislop-copywriting/SKILL.md) and [`anti-ai-slop`](../anti-ai-slop/SKILL.md).

## 1. Before Writing Anything

Load the banned words and phrases list from [references/banned-words.md](references/banned-words.md) and [`../anti-ai-slop/references/phrases-en.md`](../anti-ai-slop/references/phrases-en.md). Never use any word or phrase on those lists:
- **Hard-Banned Buzzwords**: *seamless, unleash, empower, elevate, revolutionize, delve, tapestry, landscape, game-changer, cutting-edge, next-gen, robust, leverage, synergy, streamline, holistic, impactful, supercharge, unlock, future-proof, world-class*.
- **Indonesian Slop Openers (Banned)**: *"Perlu diketahui bahwa"*, *"Tidak dapat dipungkiri"*, *"Di era digital saat ini"*, *"Hadir sebagai solusi terpadu"*, *"Tentunya hal ini"*, *"Secara keseluruhan"*.

## 2. Structural & Rhythm Rules

- **No Rule of Three.** AI defaults to threes (three adjectives, three bullet points, three feature columns). Use one, two, four, or the exact domain count.
- **No uniform sentence length.** Never write three consecutive sentences of similar length. Mix 4-word blunt declarations with 25–35 word sentences connected by subordinate clauses.
- **No parataxis.** Do not chain short fragments ("Short sentence. Then another. Then another."). Use conjunctions, semicolons, or causal clauses ("because", "since", "although") to show how ideas actually relate.
- **No binary contrast formulas.** Ban *"Not X, but Y"*, *"It's not just X — it's Y"*, and *"Built for X, designed for Y"*. State what the system does directly.
- **No hedging seesaw.** Commit to the technical fact. State tradeoffs in one direct sentence.
- **No identical paragraph or section structure.** Vary openings and lengths. Let paragraphs end as soon as the last fact lands — never append a motivational pull-quote or summary sentence.
- **No passive construction.** Replace *"is being processed"* or *"was found to be"* with the concrete actor: *"SapB1Service posts the InventoryTransfer payload to `/api/StockTransfer`."*

## 3. UI Copywriting & Technical Documentation Rules (`antislop-copywriting`)

- **No Formulaic Headlines**: Ban *"The Future of [X]"*, *"Supercharge Your [X]"*, *"All-in-One Platform for [X]"*, *"Reimagining [X]"*. Name the actual module or capability (*"Requisition List"*, *"Purchase Quotation"*, *"Procurement Report"*).
- **No Eyebrow Duplication**: Do not place a small pill badge above a heading that repeats the heading text.
- **No Redundant Subtitle Echo**: If a page title already states the document or report name clearly (e.g., *Procurement Report*), do not add a filler subtitle explaining what a procurement report is unless it conveys operational constraints.
- **Specific CTAs Only**: Every button label must name the concrete action (*"Buat Transfer"*, *"Simpan Seri"*, *"Sync ke SAP"*), never *"Submit"*, *"Learn More"*, or *"Get Started"*.
- **Honest Numbers & Claims**: Never invent statistics, percentages, or customer quotes. Cite exact table counts, seeded record counts, or verifiable test results.

## 4. Punctuation & Formatting Hygiene

- **Em dashes (`—`)**: Maximum ONE per 500 words. Use commas, colons, semicolons, or parentheses instead.
- **Exclamation marks (`!`)**: Maximum one per 1,000 words in technical prose/UI.
- **Emoji**: Zero decorative emoji in UI headings, table cells, badges, or code comments.
- **Colons & Semicolons**: Use colons to introduce concrete specifications or code; use semicolons to join closely linked independent clauses.

## 5. Silent Pre-Output Gate

Before emitting any prose, documentation, or UI copy, verify silently:
1. Zero banned words or Indonesian filler openers?
2. Sentence lengths varied (no 3 consecutive equal-length sentences, no parataxis)?
3. Zero binary *"Not X, but Y"* or *"Built for X, designed for Y"* slogans?
4. Max 1 em dash per 500 words?
5. Active voice with exact model, table, route, or operator names?
6. Paragraphs and sections end on concrete facts without summary fluff?

Apply all rules silently without announcing them.
