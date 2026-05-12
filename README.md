# Product Research Skills

Skill set for product managers running research and discovery workflows with agents.

## Contents

- `skills/product-research-suite/`
  A distributable bundle entrypoint for product research, discovery, and synthesis workflows.

## Bundle Contents

The bundle currently includes:

- `youtube-channel-parse`
  Fetch, transcribe, summarize, and filter YouTube channels or individual videos.

## Install

Install the suite locally with the `skills.sh` CLI:

```bash
npx skills add ulyanas/product-research-skills --skill product-research-suite -g -y
```

The CLI detects the current agent and installs the bundle into that agent's skills directory.

For Codex, this installs into `~/.agents/skills/`.

Install it for one project instead of your user profile:

```bash
npx skills add ulyanas/product-research-skills --skill product-research-suite -y
```

Set the agent explicitly when you want a fixed target:

```bash
npx skills add ulyanas/product-research-skills --skill product-research-suite -a codex -g -y
```

## Packaging

Package the bundle with:

```bash
python <path-to-skill-creator>/package_skill.py skills/product-research-suite dist
```

The generated artifact will be written to `dist/product-research-suite.skill`.

## Repo Conventions

- Keep runtime instructions inside the skill files.
- Keep generated artifacts out of source control.
- Keep local install artifacts out of source control.
- Keep bundled scripts self-contained and portable.
- Add new research skills under `skills/product-research-suite/skills/` so the suite stays self-contained when packaged.
