---
name: product-research-suite
description: YouTube-first product research skill bundle for transcript, filtering, summary, and structured research workflows. Use when you want one entrypoint for product research from YouTube channels or videos, reusable research outputs, or a bundle that can expand with additional product research skills over time.
---

# Product Research Suite

Use this as the bundle entrypoint when you want one skill that covers YouTube-based product research strategy plus execution.

This bundle currently includes:

- `youtube-channel-parse` for YouTube channel and single-video transcript, filtering, and summary workflows

## When To Use This Skill

Use this skill for requests like:

- "Research this market from YouTube and summarize the main themes"
- "Analyze a creator channel to understand product positioning"
- "Pull customer language from videos and organize the findings"
- "Build reusable research outputs from a filtered set of videos"
- "Build a product research workflow that starts with YouTube and keeps the outputs structured"

## Workflow Selector

Start by identifying the primary research source, then load only the relevant bundled skill.

### 1. YouTube Research

Use when the task involves:

- a YouTube channel
- a single YouTube video
- transcript collection
- filtering videos by topic, date, speakers, or metadata
- summary and notes generation from YouTube content

Primary source:

- `skills/youtube-channel-parse/SKILL.md`

Primary references:

- `skills/youtube-channel-parse/references/dependencies.md`
- `skills/youtube-channel-parse/references/filtering.md`
- `skills/youtube-channel-parse/references/outputs.md`

Scripts:

- `skills/youtube-channel-parse/scripts/fetch_channel.py`
- `skills/youtube-channel-parse/scripts/transcribe_with_fallback.py`
- `skills/youtube-channel-parse/scripts/build_report.py`

## Output Standards

When using this bundle, prefer structured outputs that include:

- research goal and scope
- source selection criteria
- filtered source set when applicable
- reusable transcripts, notes, and summaries
- machine-readable JSON or CSV when follow-up analysis is likely
- markdown reports for human review

## Practical Rule

If the request spans bundle-level research planning plus YouTube execution, stay in `product-research-suite` and pull in the bundled files above as needed.
