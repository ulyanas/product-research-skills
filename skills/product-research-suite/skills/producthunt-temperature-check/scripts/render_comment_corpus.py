#!/usr/bin/env python3
import argparse
import json
import re


INTRO_PATTERNS = [
    r"^we built ",
    r"^hi all! i.?m ",
    r"^hi! i.?m ",
    r"^hello!\s*this is ",
    r"^hey all!",
    r"^constructo - dungeons builder",
    r"^say goodbye to the limitations of physical distance",
    r"^if you.?d like to try out our platform",
]

REPLY_PATTERNS = [
    r"^@",
    r"^still going strong",
    r"^amazing support so far",
]


def clean(text):
    text = re.sub(r"<[^>]+>", "", text)
    return text.replace("\r", "").strip()


def classify(text):
    body = clean(text)
    if re.search("|".join(INTRO_PATTERNS), body, re.I):
        return "creator_intro"
    if re.search("|".join(REPLY_PATTERNS), body, re.I):
        return "creator_reply_or_update"
    return "user_comment"


def parse_args():
    parser = argparse.ArgumentParser(description="Render Product Hunt thread JSON to markdown.")
    parser.add_argument("--input", required=True, help="Input JSON path")
    parser.add_argument("--output", required=True, help="Output markdown path")
    return parser.parse_args()


def main():
    args = parse_args()
    with open(args.input, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    total_comments = sum(len(item["comments"]) for item in data)
    lines = [
        "# Product Hunt Comment Corpus",
        "",
        f"Listings covered: {len(data)}",
        f"Comment records collected: {total_comments}",
        "",
        "Comments are split into `creator intros`, `creator replies or updates`, and `user comments` with heuristic classification.",
    ]

    for item in data:
        comments = [
            {
                "author": (c.get("user") or {}).get("name") or "Unknown",
                "date": c.get("createdAt") or "Unknown date",
                "body": clean(c["body"]),
                "classification": classify(c["body"]),
            }
            for c in item["comments"]
        ]
        lines.extend(
            [
                "",
                f"## {item['name']}",
                "",
                f"- Product Hunt: {item['product_hunt_url']}",
                f"- Tagline: {item['tagline']}",
                f"- Launch date: {item['launch_date']}",
                f"- Topics: {', '.join(item['topics'])}",
                f"- Product Hunt counts: {item['votes_count']} votes, {item['comments_count_reported']} comments, {item['reviews_count']} reviews",
                f"- Thread records collected: {item['thread_records_collected']}",
            ]
        )

        for section, heading in [
            ("creator_intro", "Creator Intros"),
            ("creator_reply_or_update", "Creator Replies or Updates"),
            ("user_comment", "User Comments"),
        ]:
            subset = [c for c in comments if c["classification"] == section]
            lines.extend(["", f"### {heading}", ""])
            if not subset:
                lines.append("_None detected in this listing._")
                continue
            for idx, comment in enumerate(subset, start=1):
                lines.extend(
                    [
                        f"#### {heading[:-1] if heading.endswith('s') else heading} {idx}",
                        f"- Author: {comment['author']}",
                        f"- Date: {comment['date']}",
                        "",
                    ]
                )
                lines.extend(comment["body"].splitlines() or [""])
                lines.append("")

    with open(args.output, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines).rstrip() + "\n")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
