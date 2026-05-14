# Field Notes From Live Test Runs

This file captures practical knowledge gathered while running Product Hunt research on a real target product.

Use these notes to make future runs faster, cleaner, and more repeatable.

## Channel framing

- Treat Product Hunt as a research channel, not as a full market proxy.
- Use it for language, framing, category adjacency, feature expectations, and public feedback patterns.
- Do not claim that Product Hunt alone predicts total demand, launch outcome, or market size.

## Discovery lessons

### API-first works best for collection

- Use the official GraphQL endpoint as the primary source:
  - `POST https://api.producthunt.com/v2/api/graphql`
- Use public-page scraping only as fallback.
- Product Hunt public pages may be protected by Cloudflare, which makes scripted scraping brittle.

### URL matching is weak

- `posts(url: ...)` can return zero results even when a related product exists.
- Do not rely on domain lookup as the only way to find a listing.
- Prefer topic discovery, known competitor seeds, and slug-based enrichment.

### Topic-based discovery is stronger than naive keyword search

- Start with Product Hunt topics that fit the product’s workflow, audience, and surface area.
- Use client-side keyword filtering after topic pulls instead of relying on a single Product Hunt search path.
- Favor category terms, workflow terms, and substitute-language terms over brand-only searches.

### Known-seed expansion is often necessary

For niche spaces, the cleanest flow is:

1. define the product workflow
2. name obvious external competitors
3. validate whether they have Product Hunt listings
4. expand from those listings into topics, adjacent launches, and substitutes

## Comment collection lessons

### Count mismatches happen

- Product Hunt `commentsCount` can differ slightly from the thread records returned by the API.
- Preserve the fullest thread data returned by the API.
- State the mismatch explicitly in the report when it appears.

### Replies matter

- Pull reply threads, not just top-level comments.
- Replies often contain:
  - creator clarifications
  - feature answers
  - platform or pricing details
  - stronger evidence of user intent

### Split creator intros from user comments

This improves analysis quality immediately.

Creator intros usually contain:

- problem framing
- intended workflow
- differentiation claims
- feature emphasis

User comments usually contain:

- praise language
- friction language
- direct questions
- device or platform requests
- pricing objections
- use case evidence

### Comment quality varies sharply by listing type

- AI-heavy listings can attract more low-signal comments, generic praise, and self-promo.
- Mature utility listings often produce denser, more concrete user feedback.
- Marketplace and workflow tools tend to produce the strongest use-case language.

## High-signal comment buckets

During the live run, the most useful user-comment buckets were:

- setup speed
- remote togetherness
- immersion and atmosphere
- feature expectations
- beginner access
- pricing and platform constraints

These buckets are broadly reusable for future Product Hunt temperature checks.

## Language patterns worth preserving

High-value creator-side language:

- `simple and warm feeling of a live, in-person game`
- `within 2 clicks the adventure starts`
- `create characters in 2 minutes or less`
- `a faster way to cast spells during combat`

These examples are useful because they show the types of phrases to preserve from creator intros:

- workflow compression
- contrast with heavier alternatives
- immediacy of use
- clarity of the main promise

High-value user-side language often includes:

- exact praise for speed, simplicity, and ease
- exact friction language about price, availability, or polish
- direct feature requests
- concrete use-case descriptions

## What this means for future runs

- start from workflow, not from raw search
- use topic pulls plus known seeds
- keep API as the source of truth for collection
- collect replies and preserve the raw corpus
- separate creator intros from user comments
- downweight generic praise and obvious self-promo
- surface exact language for pros and cons whenever possible
