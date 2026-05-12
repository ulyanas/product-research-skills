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
    "a",
    "an",
    "are",
    "as",
    "at",
    "be",
    "been",
    "but",
    "by",
    "can",
    "could",
    "did",
    "do",
    "does",
    "doing",
    "done",
    "get",
    "gets",
    "got",
    "had",
    "has",
    "the",
    "and",
    "for",
    "you",
    "our",
    "ours",
    "we",
    "us",
    "with",
    "that",
    "this",
    "from",
    "were",
    "was",
    "it's",
    "its",
    "i'm",
    "i've",
    "we're",
    "we've",
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
    "there",
    "here",
    "how",
    "not",
    "next",
    "every",
    "single",
    "one",
    "two",
    "three",
    "very",
    "really",
    "quite",
    "yeah",
    "okay",
    "ok",
    "right",
    "well",
    "want",
    "wants",
    "wanted",
    "need",
    "needs",
    "going",
    "gone",
    "come",
    "comes",
    "coming",
    "look",
    "looks",
    "looking",
    "make",
    "makes",
    "made",
    "thing",
    "things",
    "stuff",
    "people",
    "person",
    "actually",
    "basically",
    "literally",
    "maybe",
    "perhaps",
    "still",
    "even",
    "back",
    "again",
    "already",
    "able",
    "let",
    "lets",
    "lot",
    "lots",
    "kind",
    "sort",
    "mean",
    "means",
    "said",
    "say",
    "says",
    "talk",
    "talks",
    "agent",
    "clicker",
    "little",
    "bit",
    "thank",
    "thanks",
}

FACT_HINTS = ("%", "percent", "million", "billion", "year", "years", "today", "now", "currently", "data", "result", "results")
INSIGHT_HINTS = ("because", "therefore", "however", "problem", "challenge", "opportunity", "risk", "benefit", "future", "scale", "why", "thesis", "insight", "lesson", "tradeoff", "better", "worse", "important")
OPINION_HINTS = ("think", "believe", "argue", "should", "must", "recommend", "prefer", "opinion", "view")
OUTCOME_HINTS = ("outcome", "result", "conclusion", "takeaway", "next", "future", "goal", "plan", "closing", "summary", "ultimately")
DISFLUENCY_TOKENS = {"um", "uh", "yeah", "oh", "okay", "ok", "hmm", "ah"}


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


def _unique_sentences(sentences: list[str]) -> list[str]:
    unique: list[str] = []
    seen: set[str] = set()
    for sentence in sentences:
        key = sentence.lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(sentence)
    return unique


def _pick_sentences(
    sentences: list[str],
    predicate,
    *,
    limit: int = 2,
    used: set[str] | None = None,
) -> list[str]:
    picked: list[str] = []
    used = used if used is not None else set()
    for sentence in sentences:
        key = sentence.lower()
        if key in used:
            continue
        if predicate(sentence):
            picked.append(sentence)
            used.add(key)
            if len(picked) >= limit:
                break
    return picked


def _sentence_has_signal(sentence: str) -> bool:
    lowered = sentence.lower()
    if "[applause]" in lowered:
        return False
    raw_tokens = re.findall(r"[a-z][a-z0-9\-]{1,}", lowered)
    if len(raw_tokens) < 6:
        return False
    meaningful_tokens = [token for token in raw_tokens if token not in DEFAULT_STOPWORDS]
    if len(meaningful_tokens) < 4:
        return False
    disfluencies = sum(token in DISFLUENCY_TOKENS for token in raw_tokens)
    return disfluencies <= max(1, len(raw_tokens) // 6)


def detailed_summary_from_record(record: dict[str, Any], limit: int = 900) -> str:
    description = clean_text(str(record.get("description") or ""))
    transcript_text = clean_text(str(record.get("transcript_text") or ""))
    title = clean_text(str(record.get("title") or record.get("video_id") or "Video"))

    description_sentences = _unique_sentences(split_sentences(description))
    transcript_sentences = _unique_sentences(split_sentences(transcript_text))
    source_sentences = transcript_sentences or description_sentences
    used: set[str] = set()

    main_plot = description_sentences[:2] or source_sentences[:2]
    for sentence in main_plot:
        used.add(sentence.lower())

    facts = _pick_sentences(
        source_sentences,
        lambda sentence: _sentence_has_signal(sentence)
        and (any(hint in sentence.lower() for hint in FACT_HINTS) or bool(re.search(r"\d", sentence))),
        used=used,
    )
    insights = _pick_sentences(
        source_sentences,
        lambda sentence: _sentence_has_signal(sentence)
        and any(hint in sentence.lower() for hint in INSIGHT_HINTS + OPINION_HINTS),
        used=used,
    )
    outcome = _pick_sentences(
        list(reversed(source_sentences)),
        lambda sentence: _sentence_has_signal(sentence)
        and (any(hint in sentence.lower() for hint in OUTCOME_HINTS) or len(sentence.split()) > 8),
        limit=1,
        used=used,
    )

    sections: list[str] = []
    if main_plot:
        sections.append(f"Main plot: {' '.join(main_plot)}")
    if facts:
        sections.append(f"Facts: {' '.join(facts)}")
    if insights:
        sections.append(f"Insights and opinions: {' '.join(insights)}")
    if outcome:
        sections.append(f"Outcome: {' '.join(outcome)}")

    if sections:
        return shorten(" ".join(sections), limit)
    return title


def _keyword_tokens(text: str) -> list[str]:
    tokens = re.findall(r"[a-z][a-z0-9\-]{2,}", clean_text(text).lower())
    return [token for token in tokens if token not in DEFAULT_STOPWORDS]


def _raw_keyword_tokens(text: str) -> list[str]:
    return re.findall(r"[a-z][a-z0-9\-]{2,}", clean_text(text).lower())


def extract_top_phrases(record: dict[str, Any], limit: int = 5) -> list[str]:
    weighted_sections = [
        (str(record.get("title") or ""), 5),
        (str(record.get("description") or ""), 3),
        (str(record.get("transcript_text") or ""), 1),
    ]
    phrase_counts: Counter[str] = Counter()
    word_counts: Counter[str] = Counter()

    for text, weight in weighted_sections:
        raw_tokens = _raw_keyword_tokens(text)
        tokens = [token for token in raw_tokens if token not in DEFAULT_STOPWORDS]
        for token in tokens:
            word_counts[token] += weight
        for size in (3, 2):
            for index in range(len(raw_tokens) - size + 1):
                phrase_tokens = raw_tokens[index : index + size]
                if any(token in DEFAULT_STOPWORDS for token in phrase_tokens):
                    continue
                if len(set(phrase_tokens)) < size:
                    continue
                phrase = " ".join(phrase_tokens)
                phrase_counts[phrase] += weight + size

    ranked_phrases = sorted(phrase_counts.items(), key=lambda item: (-item[1], -len(item[0].split()), item[0]))
    ranked_words = sorted(word_counts.items(), key=lambda item: (-item[1], item[0]))
    selected: list[str] = []
    for phrase, _ in ranked_phrases:
        phrase_tokens = set(phrase.split())
        if any(
            phrase_tokens <= set(existing.split()) or set(existing.split()) <= phrase_tokens
            for existing in selected
        ):
            continue
        selected.append(phrase)
        if len(selected) >= limit:
            break
    if len(selected) < limit:
        for word, _ in ranked_words:
            if any(word in existing.split() for existing in selected):
                continue
            selected.append(word)
            if len(selected) >= limit:
                break
    return selected


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
        "detailed_summary": clean_text(str(raw.get("detailed_summary") or "")),
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
        "detailed_summary",
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
                    "detailed_summary": record.get("detailed_summary", ""),
                }
            )


def transcript_source_label(status: str | None) -> str:
    value = (status or "").strip()
    if not value:
        return "transcript pending"
    if value == "cached":
        return "saved transcript"
    if value == "direct":
        return "captions available on YouTube"
    if value == "caption-url":
        return "captions retrieved from YouTube"
    if value == "subtitle":
        return "subtitle file downloaded from YouTube"
    if value == "local":
        return "transcribed from audio"
    if "audio-unavailable" in value:
        return "transcript unavailable"
    if value.startswith("direct-unavailable") or value.startswith("caption-unavailable") or value.startswith("subtitle-unavailable"):
        return "captions unavailable"
    return "transcript available"


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
        summary = record.get("detailed_summary") or record.get("summary") or summary_from_record(record)
        lines.append(
            f"- {record.get('upload_date', '')}: [{record.get('title', record.get('video_id', 'Video'))}]({record.get('url', '')})"
            f" | transcript source: {transcript_source_label(record.get('transcript_status'))}"
            f" | phrases: {phrases}"
        )
        lines.append(f"  Summary: {summary}")
    return "\n".join(lines).strip() + "\n"
