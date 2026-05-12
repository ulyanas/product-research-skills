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
