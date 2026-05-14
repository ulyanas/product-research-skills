#!/usr/bin/env python3
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request


ENDPOINT = "https://api.producthunt.com/v2/api/graphql"

POST_QUERY = """
query($slug:String!,$after:String){
  post(slug:$slug){
    name
    tagline
    url
    createdAt
    votesCount
    commentsCount
    reviewsCount
    reviewsRating
    topics(first:10){nodes{name slug}}
    comments(first:50, after:$after){
      pageInfo{hasNextPage endCursor}
      nodes{
        id
        body
        createdAt
        user{name username}
        replies(first:50){
          pageInfo{hasNextPage endCursor}
          nodes{
            id
            body
            createdAt
            user{name username}
          }
        }
      }
    }
  }
}
""".strip()


def get_token(explicit_token=None):
    token = explicit_token or os.environ.get("PH_TOKEN") or os.environ.get("PRODUCT_HUNT_TOKEN")
    if not token:
        raise SystemExit(
            "Missing Product Hunt token. Set PH_TOKEN or PRODUCT_HUNT_TOKEN, or pass --token."
        )
    return token


def gql_request(token, query, variables, retries=5):
    payload = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    delay = 2
    for attempt in range(retries):
        req = urllib.request.Request(ENDPOINT, data=payload, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read().decode("utf-8")
            data = json.loads(body)
            if data.get("errors"):
                raise RuntimeError(data["errors"])
            return data["data"]
        except urllib.error.HTTPError as exc:
            if exc.code == 429 and attempt < retries - 1:
                time.sleep(delay)
                delay *= 2
                continue
            raise


def collect_slug(token, slug):
    after = None
    post_record = None
    top_comments = []
    while True:
        data = gql_request(token, POST_QUERY, {"slug": slug, "after": after})
        post = data.get("post")
        if not post:
            raise RuntimeError(f"Listing not found for slug: {slug}")
        if post_record is None:
            post_record = {
                "slug": slug,
                "name": post["name"],
                "tagline": post["tagline"],
                "product_hunt_url": post["url"],
                "launch_date": post["createdAt"],
                "votes_count": post["votesCount"],
                "comments_count_reported": post["commentsCount"],
                "reviews_count": post["reviewsCount"],
                "reviews_rating": post["reviewsRating"],
                "topics": [t["slug"] for t in post["topics"]["nodes"]],
            }
        conn = post["comments"]
        top_comments.extend(conn["nodes"])
        if not conn["pageInfo"]["hasNextPage"]:
            break
        after = conn["pageInfo"]["endCursor"]
        time.sleep(1)

    flat_comments = []
    for comment in top_comments:
        flat_comments.append(
            {
                "id": comment["id"],
                "body": comment["body"],
                "createdAt": comment["createdAt"],
                "user": comment["user"],
            }
        )
        for reply in comment["replies"]["nodes"]:
            flat_comments.append(
                {
                    "id": reply["id"],
                    "body": reply["body"],
                    "createdAt": reply["createdAt"],
                    "user": reply["user"],
                }
            )

    post_record["thread_records_collected"] = len(flat_comments)
    post_record["comments"] = flat_comments
    return post_record


def parse_args():
    parser = argparse.ArgumentParser(description="Collect Product Hunt listing threads by slug.")
    parser.add_argument("--slug", action="append", required=True, help="Product Hunt listing slug")
    parser.add_argument("--out", required=True, help="Output JSON path")
    parser.add_argument("--token", help="Product Hunt token. Falls back to PH_TOKEN.")
    return parser.parse_args()


def main():
    args = parse_args()
    token = get_token(args.token)
    results = [collect_slug(token, slug) for slug in args.slug]
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(results, fh, ensure_ascii=False, indent=2)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
