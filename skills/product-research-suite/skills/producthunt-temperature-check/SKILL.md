---
name: producthunt-temperature-check
description: Product Hunt-based competitor and category research for product managers. Use when you want to analyze a product idea or existing product through Product Hunt listings, creator intros, user comments, positioning, feature patterns, customer language, adjacent products, and early channel signals. Requires a Product Hunt API token.
---

# Product Hunt Temperature Check

Use this skill when the user wants Product Hunt to serve as a research channel for:

- competitor discovery
- category mapping
- positioning analysis
- customer language extraction
- feature discovery
- creator intro analysis
- full comment corpus collection
- Product Hunt-specific research reports

This skill treats Product Hunt as a research dataset, not as a launch forecast.

Deterministic collection matters for this skill. Use the exact endpoint, script entrypoints, and output artifacts documented in:

- `./README.md`
- `./references/implementation.md`
- `./references/field-notes.md`
- `./scripts/collect_listing_threads.py`
- `./scripts/render_comment_corpus.py`

## Field Notes

The live test runs produced a few stable lessons that should guide future work:

- API-first collection is more reliable than page scraping.
- Topic-based discovery is stronger than naive URL matching.
- `posts(url: ...)` can miss relevant listings.
- Creator intros are often the densest source of positioning language.
- Reply threads often contain feature, pricing, or platform clarifications.
- AI-heavy listings can contain more noisy comments and self-promo.
- Marketplace and workflow listings often produce the strongest user language.

Read `./references/field-notes.md` when:

- the category is niche
- comment quality matters
- the first-pass discovery set looks sparse
- you need stronger heuristics for grouping direct competitors, substitutes, and low-signal comments

## Preflight

Before doing any Product Hunt API work, check whether a token is already available in the environment.

Accepted environment variable names:

- `PH_TOKEN`
- `PRODUCT_HUNT_TOKEN`

If neither variable is set, ask the user for a token before running the workflow.

Use a short direct prompt:

`To run the Product Hunt research workflow, share a Product Hunt API token or set PH_TOKEN in the environment.`

If the user already pasted a token in the conversation, use it for the current task and avoid asking again.

For concrete token-setup steps, see `./README.md`.

If the user needs to create a Product Hunt app and the form requires a Redirect URI, use:

- `http://localhost:3000/callback`

Keep the same exact Redirect URI if the app later uses the OAuth authorize and token flow.

## When To Use This Skill

Use this skill for requests like:

- "Research this product on Product Hunt"
- "Find Product Hunt competitors for this idea"
- "Pull creator language and user feedback from Product Hunt"
- "Collect all Product Hunt comments for adjacent products"
- "Turn Product Hunt listings into a PM research report"
- "Extract feature patterns and customer language from Product Hunt"

## Inputs

Expected user input:

- product idea, product URL, or short product description

Optional inputs:

- niche
- target audience
- key workflow
- competitor seeds
- date range
- output path

## Workflow

### 1. Clarify the research target

Parse the request into:

- product or idea name
- niche
- target audience
- key workflow
- likely category terms
- adjacent workflow terms

Ask follow-up questions only when the core workflow or audience is still too ambiguous to search well.

### 2. Build the candidate set

Use Product Hunt as a discovery surface to find:

- direct competitors
- indirect competitors
- substitutes
- adjacent tools

Use:

- Product Hunt GraphQL API for structured listing retrieval
- topic-based discovery
- slug-based and known-product enrichment
- external search only when Product Hunt-native discovery leaves obvious gaps

Exact endpoint:

- `POST https://api.producthunt.com/v2/api/graphql`

Prefer topic-first discovery when the product lives in a niche category. For tabletop and TTRPG-style products, start with the guidance in `./references/field-notes.md`.

### 3. Collect listing metadata

For each relevant Product Hunt listing, collect:

- product name
- Product Hunt URL
- tagline
- launch date
- topics
- vote count
- comments count
- review count and rating when available

### 4. Collect and split comments

For each relevant listing, collect the fullest comment set available through the API, including reply threads when returned.

Split comments into:

- creator intros
- creator replies or updates
- user comments

Keep the full raw corpus.

### 5. Analyze creator intros

Extract:

- exact framing language
- problem statement language
- promise language
- workflow language
- differentiation claims
- feature emphasis

Summarize recurring creator-side ideas across listings.

### 6. Analyze user comments

Extract exact user language for:

- pros
- cons
- friction points
- expectations
- requests
- confusion
- use cases

Prefer direct short quotes over paraphrase when the wording is especially strong.

Downweight:

- generic praise with no concrete detail
- obvious self-promo
- comments that only restate the maker copy

### 7. Build the research report

The main report should include:

- scope
- method
- competitor intelligence
- benchmarking snapshot
- positioning research
- customer language
- feature discovery
- validation of demand as a directional channel signal
- audience and segment research
- pricing and packaging
- go-to-market research
- trend tracking
- comments analysis
- synthesis for the target product

### 8. Save the artifacts

Prefer three outputs when writing files locally:

- main report in markdown
- full comment corpus in markdown
- structured comment corpus in JSON

Prefer the local scripts for the collection layer so the raw results stay reproducible:

- `./scripts/collect_listing_threads.py`
- `./scripts/render_comment_corpus.py`

## Output Standards

The report should:

- separate evidence from interpretation
- keep Product Hunt links for every referenced listing
- separate creator intros from user comments
- preserve exact user language for pros and cons
- include the full listing-level comment corpus in a separate file
- state when Product Hunt counts differ from returned thread records

## Practical Rules

- Treat Product Hunt as one research channel among others.
- Use Product Hunt evidence for language, framing, category adjacency, and user expectations.
- Do not claim Product Hunt alone proves total market demand.
- Prefer concise synthesis backed by exact quotes.
- Preserve a raw audit trail whenever comments are collected at scale.
