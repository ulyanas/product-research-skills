# Product Research Skills

A work-in-progress skill set for product managers running research and discovery workflows with agents.

The first shipped skill focuses on extracting insights from YouTube channels and videos.

## Current Focus

- extracting insights from YouTube channels
- collecting transcripts from videos
- filtering videos by criteria such as topic or date
- organizing findings into summaries, notes, and structured datasets

## Included Skill

The bundle currently includes one packaged workflow:

- `youtube-channel-parse`
  Analyze a YouTube channel or a single video, collect transcripts, extract insights, filter videos by criteria such as topic or date, and produce structured outputs.

## Example Use Cases

- Parse all videos from a particular conference or other event and provide summaries and insights.
- Review Reddit for insights on the topic. Coming soon.
- Review Product Hunt for insights on the topic. Coming soon.

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

List available skills before installing:

```bash
npx skills add ulyanas/product-research-skills --list
```

Set the target agent explicitly when you want a fixed destination. Most users do not need this because the CLI detects the current agent automatically.

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
