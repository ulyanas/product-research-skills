# Product Research Skills

Skill set for product managers running research and discovery workflows with agents.

Use this bundle when you want structured help with market research, customer language capture, content analysis, and reusable discovery outputs.

## What It Helps With

- turning research questions into repeatable workflows
- pulling useful signals from long-form content
- organizing findings into summaries, notes, and structured datasets
- building reusable discovery assets for product strategy, positioning, and planning

## Included Skill

The bundle currently includes one packaged workflow:

- `youtube-channel-parse`
  Analyze a YouTube channel or a single video, collect transcripts, filter videos by criteria such as topic or date, and produce summaries and structured outputs.

## Example Use Cases

- Research a market category by reviewing how founders, operators, or creators talk about the problem.
- Pull customer language from conference talks, interviews, and product videos.
- Analyze a creator or company channel to understand positioning, themes, and recurring narratives.
- Build a reusable discovery dataset from a filtered set of videos.

## Install

Install the bundle with the `skills.sh` CLI:

```bash
npx skills add ulyanas/product-research-skills --skill product-research-suite -g -y
```

The CLI detects the current agent automatically and installs the bundle into that agent's skills directory.

For Codex, this installs into `~/.agents/skills/`.

Install it for one project instead of your user profile:

```bash
npx skills add ulyanas/product-research-skills --skill product-research-suite -y
```

Set the agent explicitly when you want a fixed target:

```bash
npx skills add ulyanas/product-research-skills --skill product-research-suite -a codex -g -y
```
