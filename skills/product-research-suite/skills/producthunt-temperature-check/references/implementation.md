# Implementation Notes

This skill becomes more deterministic when the collection layer is explicit.

## Exact API endpoint

- `POST https://api.producthunt.com/v2/api/graphql`

Authorization header:

- `Authorization: Bearer $PH_TOKEN`

Content type:

- `Content-Type: application/json`

## Exact collection stages

### 1. Listing enrichment by slug

Use the `post(slug: ...)` GraphQL query to collect:

- `name`
- `tagline`
- `url`
- `createdAt`
- `votesCount`
- `commentsCount`
- `reviewsCount`
- `reviewsRating`
- `topics`

### 2. Comment collection

Use paginated `comments(first: 50, after: ...)` on the listing query.

For each returned comment node, collect:

- `id`
- `body`
- `createdAt`
- `user`
- `replies(first: 50)`

This gives a deterministic raw corpus for a known set of listing slugs.

### 3. Corpus rendering

Normalize comments into:

- creator intros
- creator replies or updates
- user comments

Heuristic classification is acceptable at the rendering layer as long as:

- the raw text is preserved
- the classification is transparent
- the final report links back to the raw corpus

## Local scripts

- `../scripts/collect_listing_threads.py`
- `../scripts/render_comment_corpus.py`

## Why this matters

The interpretation layer can stay flexible, while the collection layer stays reproducible:

- exact endpoint
- exact query fields
- exact output files
- exact script entrypoints
