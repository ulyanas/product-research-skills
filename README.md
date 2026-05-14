# Product Research Skills

A consumer-friendly skill bundle for product managers, founders, and researchers who want to turn public channels into structured product insight. These skills help collect evidence, extract customer language, map competitors, and build reusable research outputs you can review or feed into later analysis. The bundle is designed so you can install one entrypoint for broader workflows or install just the source-specific skill you need for a single task. Today the focus is YouTube and Product Hunt. Reddit research is planned next.

## Install

Install the full bundle with the `skills.sh` CLI:

```bash
npx skills add ulyanas/product-research-skills --skill product-research-suite -g -y
```

Install the bundle only for the current project:

```bash
npx skills add ulyanas/product-research-skills --skill product-research-suite -y
```

## Included Skills

### `product-research-suite`

`product-research-suite` is the bundle entrypoint for this repo. It is useful when you want one install that can route between multiple research channels without deciding up front which source-specific skill to use. The suite is designed for broader product discovery work, recurring research habits, and mixed workflows where one project may start with YouTube and later expand into Product Hunt or other public channels. It focuses on reusable outputs, structured synthesis, and keeping research workflows organized as the bundle grows. Use it when you want the most flexible install path and a single research-oriented skill name to remember.

Install:

```bash
npx skills add ulyanas/product-research-skills --skill product-research-suite -g -y
```

### `youtube-channel-parse`

`youtube-channel-parse` is the YouTube-focused research skill for collecting channel or single-video data, pulling transcripts, filtering videos by topic or date, and turning long-form content into usable product insight. It is a strong fit for founder interviews, conference talks, launch videos, customer education channels, and creator ecosystems where product language emerges through spoken content rather than short text posts. The skill is built to save the raw transcript outputs, support filtering, and produce summaries you can reuse later. Install this when your research question is primarily about YouTube content and you do not need the broader bundle.

Install:

```bash
npx skills add ulyanas/product-research-skills --skill youtube-channel-parse -g -y
```

### `producthunt-temperature-check`

`producthunt-temperature-check` is the Product Hunt research skill for analyzing how a product idea or existing company appears through Product Hunt listings, creator intros, user comments, feature framing, and adjacent launches. It is useful for competitor discovery, customer language capture, feature expectation mapping, and comment-driven category research. The skill separates creator framing from user feedback, preserves raw comment corpora, and generates a structured research report plus audit artifacts. Use it when Product Hunt is a meaningful public signal for your category and you want exact language from listings and discussion threads rather than a loose summary.

Install:

```bash
npx skills add ulyanas/product-research-skills --skill producthunt-temperature-check -g -y
```

List available skills before installing:

```bash
npx skills add ulyanas/product-research-skills --list
```

## Planned

- `reddit-research`
  A planned skill for collecting and analyzing public Reddit discussions, repeated pain points, language patterns, objections, and community sentiment for product and market research.
