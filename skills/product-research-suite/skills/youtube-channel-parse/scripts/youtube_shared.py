#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from collections.abc import Iterable
from pathlib import Path
from typing import Any

DEFAULT_STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "that",
    "this",
    "from",
    "into",
    "your",
    "their",
    "about",
    "have",
    "will",
    "they",
    "what",
    "when",
    "where",
    "which",
    "more",
    "than",
    "just",
    "over",
    "across",
    "like",
    "them",
    "then",
    "also",
    "being",
    "because",
    "much",
    "many",
    "video",
    "videos",
    "youtube",
    "channel",
}


def clean_text(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def split_sentences(text: str) -> list[str]:
    if not text:
        return []
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", text) if part.strip()]


def shorten(text: str, limit: int) -> str:
    text = clean_text(text)
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def summary_from_record(record: dict[str, Any], limit: int = 280) -> str:
    description = clean_text(str(record.get("description") or ""))
    transcript_text = clean_text(str(record.get("transcript_text") or ""))
    title = clean_text(str(record.get("title") or record.get("video_id") or "Video"))

    description_sentences = split_sentences(description)
    if description_sentences:
        return shorten(" ".join(description_sentences[:2]), limit)

    transcript_sentences = split_sentences(transcript_text)
    if transcript_sentences:
        return shorten(" ".join(transcript_sentences[:2]), limit)

    return title


def extract_top_phrases(record: dict[str, Any], limit: int = 5) -> list[str]:
    blobs = [
        str(record.get("title") or ""),
        str(record.get("description") or ""),
        str(record.get("transcript_text") or ""),
    ]
    corpus = clean_text(" ".join(blobs)).lower()
    words = re.findall(r"[a-z][a-z\-]{3,}", corpus)
    counts = Counter(word for word in words if word not in DEFAULT_STOPWORDS)
    return [word for word, _ in counts.most_common(limit)]


def parse_date_value(value: str | None) -> str | None:
    if not value:
        return None
    compact = value.strip().replace("-", "")
    if not re.fullmatch(r"\d{8}", compact):
        raise ValueError(f"Expected YYYY-MM-DD or YYYYMMDD, got: {value}")
    return compact


def parse_metadata_filters(values: list[str]) -> list[tuple[str, str]]:
    filters: list[tuple[str, str]] = []
    for item in values:
        if "=" not in item:
            raise ValueError(f"Metadata filter must use FIELD=VALUE: {item}")
        field, needle = item.split("=", 1)
        field = field.strip()
        needle = needle.strip()
        if not field or not needle:
            raise ValueError(f"Metadata filter must use FIELD=VALUE: {item}")
        filters.append((field, needle))
    return filters


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def inventory_dir(output_dir: Path) -> Path:
    return ensure_dir(output_dir / "inventory")


def filtered_dir(output_dir: Path) -> Path:
    return ensure_dir(output_dir / "filtered")


def transcripts_dir(output_dir: Path) -> Path:
    return ensure_dir(output_dir / "transcripts")


def reports_dir(output_dir: Path) -> Path:
    return ensure_dir(output_dir / "reports")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def extract_caption_urls(raw: dict[str, Any]) -> list[dict[str, str]]:
    automatic_captions = raw.get("automatic_captions") or {}
    subtitles = raw.get("subtitles") or {}
    tracks: list[dict[str, str]] = []

    def add_tracks(source: dict[str, Any], category: str) -> None:
        for language_key in ("en", "en-orig"):
            entries = source.get(language_key) or []
            if not isinstance(entries, Iterable):
                continue
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                url = str(entry.get("url") or "").strip()
                ext = str(entry.get("ext") or "").strip()
                if not url or not ext:
                    continue
                tracks.append(
                    {
                        "category": category,
                        "language": language_key,
                        "ext": ext,
                        "url": url,
                    }
                )

    add_tracks(subtitles, "subtitle")
    add_tracks(automatic_captions, "automatic")

    preferred_order = {
        ("subtitle", "en", "vtt"): 0,
        ("subtitle", "en-orig", "vtt"): 1,
        ("automatic", "en", "vtt"): 2,
        ("automatic", "en-orig", "vtt"): 3,
        ("subtitle", "en", "srv3"): 4,
        ("subtitle", "en-orig", "srv3"): 5,
        ("automatic", "en", "srv3"): 6,
        ("automatic", "en-orig", "srv3"): 7,
        ("subtitle", "en", "ttml"): 8,
        ("subtitle", "en-orig", "ttml"): 9,
        ("automatic", "en", "ttml"): 10,
        ("automatic", "en-orig", "ttml"): 11,
        ("subtitle", "en", "json3"): 12,
        ("subtitle", "en-orig", "json3"): 13,
        ("automatic", "en", "json3"): 14,
        ("automatic", "en-orig", "json3"): 15,
    }
    tracks.sort(
        key=lambda item: preferred_order.get(
            (item["category"], item["language"], item["ext"]),
            100,
        )
    )
    return tracks


def normalize_video_record(raw: dict[str, Any]) -> dict[str, Any]:
    video_id = str(raw.get("id") or raw.get("video_id") or "").strip()
    title = clean_text(str(raw.get("title") or ""))
    description = clean_text(str(raw.get("description") or ""))
    url = (
        raw.get("webpage_url")
        or raw.get("original_url")
        or raw.get("url")
        or (f"https://www.youtube.com/watch?v={video_id}" if video_id else "")
    )
    upload_date = str(raw.get("upload_date") or "").strip()
    duration_value = raw.get("duration") if raw.get("duration") is not None else raw.get("duration_seconds")
    duration_seconds = int(duration_value) if duration_value not in (None, "") else None
    view_value = raw.get("view_count")
    view_count = int(view_value) if view_value not in (None, "") else None
    return {
        "video_id": video_id,
        "title": title,
        "description": description,
        "url": url,
        "upload_date": upload_date,
        "duration_seconds": duration_seconds,
        "view_count": view_count,
        "channel_title": clean_text(str(raw.get("channel") or raw.get("channel_title") or raw.get("uploader") or "")),
        "transcript_text": clean_text(str(raw.get("transcript_text") or "")),
        "transcript_status": str(raw.get("transcript_status") or ""),
        "transcript_word_count": int(raw.get("transcript_word_count") or 0),
        "summary": clean_text(str(raw.get("summary") or "")),
        "top_phrases": list(raw.get("top_phrases") or []),
        "caption_urls": list(raw.get("caption_urls") or extract_caption_urls(raw)),
    }


def matches_filters(
    record: dict[str, Any],
    *,
    since_date: str | None = None,
    until_date: str | None = None,
    topic_filter: str | None = None,
    speaker_filter: str | None = None,
    metadata_filters: list[tuple[str, str]] | None = None,
    include_transcript: bool = False,
) -> bool:
    upload_date = str(record.get("upload_date") or "")
    if since_date and upload_date and upload_date < since_date:
        return False
    if until_date and upload_date and upload_date > until_date:
        return False

    for field, expected in metadata_filters or []:
        actual = str(record.get(field, "") or "").lower()
        if expected.lower() not in actual:
            return False

    searchable = " ".join(
        part
        for part in [
            str(record.get("title") or ""),
            str(record.get("description") or ""),
            str(record.get("channel_title") or ""),
            str(record.get("transcript_text") or "") if include_transcript else "",
        ]
        if part
    ).lower()

    if topic_filter and topic_filter.lower() not in searchable:
        return False
    if speaker_filter and speaker_filter.lower() not in searchable:
        return False
    return True


def apply_filters(
    records: list[dict[str, Any]],
    *,
    since_date: str | None = None,
    until_date: str | None = None,
    topic_filter: str | None = None,
    speaker_filter: str | None = None,
    metadata_filters: list[tuple[str, str]] | None = None,
    include_transcript: bool = False,
) -> list[dict[str, Any]]:
    return [
        record
        for record in records
        if matches_filters(
            record,
            since_date=since_date,
            until_date=until_date,
            topic_filter=topic_filter,
            speaker_filter=speaker_filter,
            metadata_filters=metadata_filters,
            include_transcript=include_transcript,
        )
    ]


def write_records_csv(records: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "upload_date",
        "video_id",
        "title",
        "url",
        "duration_seconds",
        "view_count",
        "channel_title",
        "transcript_status",
        "transcript_word_count",
        "top_phrases",
        "summary",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "upload_date": record.get("upload_date", ""),
                    "video_id": record.get("video_id", ""),
                    "title": record.get("title", ""),
                    "url": record.get("url", ""),
                    "duration_seconds": record.get("duration_seconds", ""),
                    "view_count": record.get("view_count", ""),
                    "channel_title": record.get("channel_title", ""),
                    "transcript_status": record.get("transcript_status", ""),
                    "transcript_word_count": record.get("transcript_word_count", 0),
                    "top_phrases": "; ".join(record.get("top_phrases", [])),
                    "summary": record.get("summary", ""),
                }
            )


def dataset_markdown(
    *,
    title: str,
    records: list[dict[str, Any]],
    criteria_lines: list[str] | None = None,
) -> str:
    lines = [f"# {title}", ""]
    if criteria_lines:
        lines.extend(criteria_lines)
        lines.append("")
    lines.append(f"Videos: {len(records)}")
    lines.append("")
    for record in records:
        phrases = ", ".join(record.get("top_phrases", [])[:4]) or "n/a"
        summary = record.get("summary") or summary_from_record(record)
        lines.append(
            f"- {record.get('upload_date', '')}: [{record.get('title', record.get('video_id', 'Video'))}]({record.get('url', '')})"
            f" | transcript: {record.get('transcript_status', '') or 'pending'}"
            f" | phrases: {phrases}"
        )
        lines.append(f"  Summary: {summary}")
    return "\n".join(lines).strip() + "\n"
