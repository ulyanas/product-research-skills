# Product Research Skills

A work-in-progress skill set for product managers running research and discovery workflows with agents.

## Current Focus

- extracting insights from YouTube channels
- collecting transcripts from videos
- filtering videos by criteria such as topic or date
- organizing findings into summaries, notes, and structured datasets
- mapping Product Hunt competitors and adjacent products
- collecting Product Hunt creator intros and user comments
- extracting customer language, feature expectations, and public feedback patterns

## Included Skills

This repo now supports:

- a bundle skill
- individual installable skills

- `youtube-channel-parse`
  Analyze a YouTube channel or a single video, collect transcripts, extract insights, filter videos by criteria such as topic or date, and produce structured outputs.
- `producthunt-temperature-check`
  Analyze a product idea or existing product through Product Hunt listings, creator intros, user comments, positioning, feature patterns, and full comment corpus collection.
- `product-research-suite`
  Use one entrypoint that can route to YouTube research or Product Hunt research depending on the task.

## Example Use Cases

- Parse all videos from a particular conference or other event and provide summaries and insights.
- Review Product Hunt for insights on the topic and collect exact creator and user language.
- Compare YouTube language with Product Hunt public feedback for the same category.

## Install

Install with the `skills.sh` CLI:

```bash
npx skills add ulyanas/product-research-skills --skill product-research-suite -g -y
```

This installs the skill globally for your current agent.

Install it only for the current project:

```bash
npx skills add ulyanas/product-research-skills --skill product-research-suite -y
```

Install only the YouTube skill:

```bash
npx skills add ulyanas/product-research-skills --skill youtube-channel-parse -g -y
```

Install only the Product Hunt skill:

```bash
npx skills add ulyanas/product-research-skills --skill producthunt-temperature-check -g -y
```

List available skills before installing:

```bash
npx skills add ulyanas/product-research-skills --list
```

Set the target agent explicitly when you want a fixed destination. Most users do not need this because the CLI detects the current agent automatically.

## Source Repo Paths

Top-level skill paths in this repo:

- `skills/product-research-suite`
- `skills/youtube-channel-parse`
- `skills/producthunt-temperature-check`

### Agent Examples

Codex:

```bash
npx skills add ulyanas/product-research-skills --skill product-research-suite -a codex -g -y
```

Claude Code:

```bash
npx skills add ulyanas/product-research-skills --skill product-research-suite -a claude-code -g -y
```

Cursor:

```bash
npx skills add ulyanas/product-research-skills --skill product-research-suite -a cursor -g -y
```
