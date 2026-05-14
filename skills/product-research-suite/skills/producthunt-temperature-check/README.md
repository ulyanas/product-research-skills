# Product Hunt Temperature Check

Product Hunt competitor and category research for product managers.

This skill helps you:

- find adjacent Product Hunt listings for a product idea
- collect creator intros, creator replies, and user comments
- extract positioning language, feature patterns, and customer language
- save a raw audit trail in markdown and JSON

## What You Need

- a Product Hunt account
- a Product Hunt API token
- Python 3

## How To Get a Product Hunt Token

Product Hunt’s official docs say you can use a `developer_token` from the API dashboard for simple scripts.

Official sources:

- [Product Hunt API docs](https://www.producthunt.com/v2/docs)
- [Product Hunt Help Center: Does Product Hunt have an API?](https://help.producthunt.com/en/articles/484971-does-producthunt-have-an-api)

### Steps

1. Log in to Product Hunt.
2. Open [My Apps](https://www.producthunt.com/v2/docs) and click `API dashboard`.
3. Create or open an app in the dashboard.
4. Copy the `developer_token` shown in the dashboard.

The docs describe this token as a non-expiring token linked to your account for script use.

## What To Put In Redirect URI

If the Product Hunt app form requires a Redirect URI, use:

```text
http://localhost:3000/callback
```

That is a safe local default Redirect URI for this skill.

Keep the exact same Redirect URI value if you later run a real OAuth flow with the app.

## Add the Token to Your Environment

### For the current terminal session

```bash
export PH_TOKEN='your_product_hunt_token_here'
```

### Persist it in `zsh`

Add this line to `~/.zshrc`:

```bash
export PH_TOKEN='your_product_hunt_token_here'
```

Then reload your shell:

```bash
source ~/.zshrc
```

### Verify it is available

```bash
echo "$PH_TOKEN"
```

Do not commit tokens to git. Keep them in your shell environment or a local secrets file that stays untracked.

## Deterministic Collection

This skill uses one exact API endpoint:

- `POST https://api.producthunt.com/v2/api/graphql`

It uses these local scripts:

- `scripts/collect_listing_threads.py`
- `scripts/render_comment_corpus.py`

### 1. Collect listing threads

```bash
python3 scripts/collect_listing_threads.py \
  --slug rpgmeet \
  --slug spawn-2 \
  --slug ai-game-master-dungeon-rpg \
  --out /tmp/producthunt_threads.json
```

### 2. Render a markdown corpus

```bash
python3 scripts/render_comment_corpus.py \
  --input /tmp/producthunt_threads.json \
  --output /tmp/producthunt_threads.md
```

## What the scripts do

`collect_listing_threads.py`:

- reads `PH_TOKEN` or `PRODUCT_HUNT_TOKEN`
- fetches listing metadata by slug
- paginates top-level comments
- fetches reply threads returned by the listing query
- writes a normalized JSON file

`render_comment_corpus.py`:

- reads the normalized JSON
- classifies comments into:
  - creator intros
  - creator replies or updates
  - user comments
- writes a readable markdown corpus

## Expected Outputs

- main research report in markdown
- full comment corpus in markdown
- structured thread corpus in JSON

## Notes

- Product Hunt `commentsCount` and returned thread records may differ slightly.
- Product Hunt is one research channel. Use it for language, framing, adjacency, and user expectations.
