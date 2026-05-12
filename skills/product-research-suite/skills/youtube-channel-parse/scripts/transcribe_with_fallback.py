#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import urllib.request
from html import unescape
from pathlib import Path

from youtube_shared import (
    normalize_video_record,
    read_json,
    summary_from_record,
    transcripts_dir,
    write_json,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Retrieve YouTube transcripts and fall back to local audio transcription when needed."
    )
    parser.add_argument("--input-json", required=True, help="Path to a dataset JSON file from fetch_channel.py")
    parser.add_argument("--output-root", default="output")
    parser.add_argument("--output-prefix", required=True)
    parser.add_argument("--whisper-model", default="tiny.en")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--cookies", help="Optional path to a yt-dlp cookies.txt file")
    parser.add_argument("--cookies-from-browser", help="Optional browser name for yt-dlp --cookies-from-browser")
    return parser.parse_args()


def fetch_direct_transcript(video_id: str) -> tuple[str, str]:
    from youtube_transcript_api import YouTubeTranscriptApi

    api = YouTubeTranscriptApi()
    try:
        transcript = api.fetch(video_id, languages=["en"])
    except Exception as exc:  # noqa: BLE001
        return "", f"direct-unavailable:{type(exc).__name__}"
    text = " ".join(snippet.text.strip() for snippet in transcript if snippet.text.strip()).strip()
    return text, "direct"


def audio_path_for(audio_dir: Path, video_id: str) -> Path | None:
    matches = list(audio_dir.glob(f"{video_id}.*"))
    return matches[0] if matches else None


def subtitle_path_for(transcript_dir: Path, video_id: str) -> Path | None:
    patterns = [
        f"{video_id}*.vtt",
        f"{video_id}*.srv3",
        f"{video_id}*.ttml",
    ]
    for pattern in patterns:
        matches = list(transcript_dir.glob(pattern))
        if matches:
            return matches[0]
    return None


def caption_payload_to_text(ext: str, payload: str) -> str:
    ext = ext.lower()
    if ext == "json3":
        lines: list[str] = []
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            return ""
        for event in data.get("events", []):
            segments = event.get("segs") or []
            for segment in segments:
                text = str(segment.get("utf8") or "").strip()
                if text:
                    lines.append(text)
        return normalize_spaces(" ".join(lines))

    if ext in {"vtt", "srt"}:
        return subtitle_text_to_plain(payload)

    if ext in {"srv1", "srv2", "srv3", "ttml", "xml"}:
        text = re.sub(r"<[^>]+>", " ", payload)
        return normalize_spaces(unescape(text))

    return normalize_spaces(payload)


def normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def subtitle_text_to_plain(payload: str) -> str:
    lines: list[str] = []
    for raw_line in payload.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line == "WEBVTT":
            continue
        if "-->" in line:
            continue
        if re.fullmatch(r"\d+", line):
            continue
        if re.fullmatch(r"[0-9:.,\- >]+", line):
            continue
        line = re.sub(r"<[^>]+>", "", line)
        line = unescape(line)
        if line:
            lines.append(line)
    return normalize_spaces(" ".join(lines))


def yt_dlp_auth_args(args: argparse.Namespace) -> list[str]:
    auth_args: list[str] = []
    if args.cookies:
        auth_args.extend(["--cookies", args.cookies])
    if args.cookies_from_browser:
        auth_args.extend(["--cookies-from-browser", args.cookies_from_browser])
    return auth_args


def explain_yt_dlp_error(exc: subprocess.CalledProcessError) -> str:
    text = "\n".join(part for part in [exc.stdout, exc.stderr] if part).strip()
    if not text:
        return "yt-dlp failed without stderr output"
    lowered = text.lower()
    if "sign in to confirm you’re not a bot" in lowered or "sign in to confirm you're not a bot" in lowered:
        return "YouTube requested bot-verification. Retry with cookies or a less restricted environment."
    if "403 forbidden" in lowered:
        return "YouTube rejected the content request with 403 Forbidden."
    if "timed out" in lowered:
        return "The YouTube content request timed out."
    return shorten_error(text)


def shorten_error(text: str, limit: int = 500) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    if len(compact) <= limit:
        return compact
    return compact[: limit - 1].rstrip() + "…"


def vtt_to_text(path: Path) -> str:
    return subtitle_text_to_plain(path.read_text(encoding="utf-8", errors="ignore"))


def fetch_caption_urls(record: dict, timeout_seconds: int = 30) -> tuple[str, str]:
    for track in record.get("caption_urls", []):
        if not isinstance(track, dict):
            continue
        url = str(track.get("url") or "").strip()
        ext = str(track.get("ext") or "").strip()
        if not url or not ext:
            continue
        try:
            with urllib.request.urlopen(url, timeout=timeout_seconds) as response:
                payload = response.read().decode("utf-8", errors="ignore")
        except Exception as exc:  # noqa: BLE001
            continue
        text = caption_payload_to_text(ext, payload)
        if text:
            label = track.get("category") or "caption"
            return text, f"{label}-url:{ext}"
    return "", "caption-url-unavailable"


def download_subtitles(transcript_dir: Path, video_id: str, url: str, args: argparse.Namespace) -> tuple[str, str]:
    existing = subtitle_path_for(transcript_dir, video_id)
    if existing:
        return vtt_to_text(existing), "subtitle-cached"

    transcript_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        "yt-dlp",
        "--no-check-certificates",
        "--skip-download",
        "--write-auto-subs",
        "--write-subs",
        "--sub-langs",
        "en.*,en",
        "--sub-format",
        "vtt",
        "-o",
        str(transcript_dir / "%(id)s.%(ext)s"),
        *yt_dlp_auth_args(args),
        url,
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        return "", f"subtitle-unavailable:{explain_yt_dlp_error(exc)}"

    downloaded = subtitle_path_for(transcript_dir, video_id)
    if downloaded is None:
        return "", "subtitle-unavailable:yt-dlp completed without subtitle output"
    return vtt_to_text(downloaded), "subtitle"


def download_audio(audio_dir: Path, video_id: str, url: str, args: argparse.Namespace) -> Path:
    existing = audio_path_for(audio_dir, video_id)
    if existing:
        return existing

    audio_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        "yt-dlp",
        "--no-check-certificates",
        "-f",
        "bestaudio",
        "-o",
        str(audio_dir / "%(id)s.%(ext)s"),
        *yt_dlp_auth_args(args),
        url,
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(explain_yt_dlp_error(exc)) from exc
    downloaded = audio_path_for(audio_dir, video_id)
    if downloaded is None:
        raise FileNotFoundError(f"Audio download completed without a saved file for {video_id}")
    return downloaded


def transcribe_local(media_path: Path, model_name: str) -> str:
    from faster_whisper import WhisperModel

    model = WhisperModel(model_name, device="cpu", compute_type="int8")
    segments, _info = model.transcribe(
        str(media_path),
        vad_filter=True,
        beam_size=1,
        language="en",
    )
    return " ".join(segment.text.strip() for segment in segments if segment.text.strip()).strip()


def load_records(path: Path) -> tuple[dict, list[dict]]:
    payload = read_json(path)
    if isinstance(payload, dict):
        videos = payload.get("videos", [])
    elif isinstance(payload, list):
        videos = payload
        payload = {}
    else:
        videos = []
        payload = {}
    return payload, [normalize_video_record(record) for record in videos]


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_root) / args.output_prefix
    transcript_dir = transcripts_dir(output_dir)
    audio_dir = output_dir / "audio"
    payload, records = load_records(Path(args.input_json))
    if args.limit is not None:
        records = records[: args.limit]

    enriched_records: list[dict] = []
    total = len(records)
    for index, record in enumerate(records, start=1):
        video_id = record["video_id"]
        transcript_path = transcript_dir / f"{video_id}.txt"
        transcript_text = ""
        transcript_status = ""

        if transcript_path.exists():
            transcript_text = transcript_path.read_text(encoding="utf-8").strip()
            transcript_status = "cached"
        else:
            transcript_text, transcript_status = fetch_direct_transcript(video_id)
            if transcript_text:
                transcript_path.write_text(transcript_text + "\n", encoding="utf-8")
            else:
                transcript_text, transcript_status = fetch_caption_urls(record)
                if transcript_text:
                    transcript_path.write_text(transcript_text + "\n", encoding="utf-8")
                else:
                    transcript_text, transcript_status = download_subtitles(transcript_dir, video_id, record["url"], args)
                if transcript_text:
                    transcript_path.write_text(transcript_text + "\n", encoding="utf-8")
                else:
                    try:
                        media_path = download_audio(audio_dir, video_id, record["url"], args)
                    except RuntimeError as exc:
                        transcript_status = f"{transcript_status};audio-unavailable:{exc}"
                        transcript_text = ""
                    else:
                        transcript_text = transcribe_local(media_path, args.whisper_model)
                        transcript_status = "local"
                        transcript_path.write_text(transcript_text + "\n", encoding="utf-8")

        enriched = dict(record)
        enriched["transcript_text"] = transcript_text
        enriched["transcript_status"] = transcript_status
        enriched["transcript_word_count"] = len(transcript_text.split())
        enriched["summary"] = record.get("summary") or summary_from_record(enriched)
        enriched_records.append(enriched)

        print(
            f"Processed {index}/{total}: {record.get('title') or video_id} "
            f"[{transcript_status}] words={enriched['transcript_word_count']}",
            flush=True,
        )

    enriched_payload = dict(payload) if isinstance(payload, dict) else {}
    enriched_payload["videos"] = enriched_records
    write_json(
        output_dir / "filtered" / f"{args.output_prefix}_videos.transcripts.json",
        enriched_payload,
    )


if __name__ == "__main__":
    main()
