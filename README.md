# Product Research Skills

Source repo for a self-contained product research skill bundle built for agent workflows.

## Contents

- `skills/product-research-suite/`
  A distributable bundle entrypoint for YouTube-first product research workflows.

## Bundle Contents

The bundle currently includes:

- `youtube-channel-parse`
  Fetch, transcribe, summarize, and filter YouTube channels or individual videos.

## Packaging

Package the bundle with:

```bash
python <path-to-skill-creator>/package_skill.py skills/product-research-suite dist
```

The generated artifact will be written to `dist/product-research-suite.skill`.

## Repo Conventions

- Keep runtime instructions inside the skill files.
- Keep generated artifacts out of source control.
- Keep bundled scripts self-contained and portable.
- Add new research skills under `skills/product-research-suite/skills/` so the suite stays self-contained when packaged.
