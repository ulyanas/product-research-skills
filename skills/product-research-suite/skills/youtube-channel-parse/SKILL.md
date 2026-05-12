---
name: youtube-channel-parse
description: Fetch, transcribe, summarize, and filter YouTube channels or individual videos. Use when asked to analyze a full YouTube channel, parse a single video, collect transcripts, group or filter videos by date, topic, speakers, or metadata criteria, or produce reusable summaries and structured outputs from YouTube content.
---

# YouTube Channel Parse

## Overview

This skill supports two workflows.

For an individual video:

- parse a specific video URL
- fetch or generate a transcript
- summarize the video
- extract structured notes or reusable outputs

For a YouTube channel:

- inventory channel videos
- select which videos to analyze by criteria such as topic, date range, speakers, or other metadata filters
- retrieve transcripts for the selected subset
- produce summaries and structured outputs for the filtered set

## Inputs

Accept these inputs:

- `channel_url` or `video_url`
- optional `since_date`
- optional `until_date`
- optional `topic_filter`
- optional `speaker_filter`
- optional `metadata_filters`
- `output_prefix`
- optional `whisper_model`

## Workflow Selection

Choose the workflow from the provided URL:

- if the user provides `video_url`, run the individual video workflow
- if the user provides `channel_url`, run the channel workflow
- if the user provides both, use the video workflow for the specific video request and the channel workflow for the filtered channel request

Check environment access early.

If the environment blocks YouTube network access, stop retrying after confirming the restriction and tell the user how to enable access before continuing.

## Individual Video Workflow

1. Normalize the video URL and derive the video id.
2. Fetch video metadata.
3. Retrieve the transcript.
4. Produce a transcript file.
5. Produce a markdown summary or notes file when the user asks for analysis, findings, or reusable notes.
6. Produce structured JSON output when the task calls for downstream reuse.

## Channel Workflow

1. Inventory the channel videos.
2. Normalize metadata for each video.
3. Apply selection criteria such as date range, topic, speakers, or metadata filters.
4. Write the filtered dataset before transcript work when the selection itself is part of the deliverable.
5. Retrieve transcripts for the selected subset.
6. Produce summaries, notes, and reports for the filtered set.

## Filtering Rules

Apply filters in this order:

1. date window
2. metadata filters
3. topic filter
4. speaker filter

Use metadata-based filtering before transcript retrieval when that narrows the set efficiently.

Use transcript-based filtering when the requested criteria depend on spoken content, such as speaker references, repeated themes, or terms not present in the title or description.

Read detailed filter semantics from `references/filtering.md` when the request depends on nuanced selection logic.

## Transcript Workflow

Retrieve direct transcripts first.

When direct transcripts are unavailable, try subtitle retrieval before full audio transcription.

When subtitle retrieval is unavailable, generate transcripts from downloaded audio and continue the workflow.

Reuse existing transcript files and cached audio files when they already match the current request.

Use `tiny.en` or `tiny` by default for fast transcription unless the user asks for higher accuracy.

If metadata retrieval works but captions or audio fail with bot-detection, `403`, or sign-in verification errors, treat that as a content-access restriction and explain the environment limits clearly.

## Outputs

- channel inventory in JSON and markdown when needed
- filtered video dataset in JSON, CSV, and markdown when needed
- transcript files per video
- filtered subsets by topic, speaker, date, or metadata criteria
- markdown report with findings, summaries, and caveats

Use markdown outputs for summaries, findings, reusable notes, and channel-level reports.

Read naming and directory conventions from `references/outputs.md` when writing artifacts.

## Capabilities

| Workflow | Capability | Result |
| --- | --- | --- |
| Channel | Analyze the entire channel | Inventory, selection, transcripts, and channel-level outputs |
| Video | Analyze an individual video | Transcript, summary, notes, and structured outputs |
| Channel | Filter videos by date window | A narrowed candidate set before transcript work |
| Channel | Filter or group videos by topic, date range, speakers, or metadata criteria | A selected subset for analysis and reporting |
| Video or Channel | Fetch direct transcripts when available | Faster transcript retrieval from existing sources |
| Video or Channel | Generate transcripts from downloaded audio when needed | Continued execution when direct transcripts are unavailable |
| Video or Channel | Generate concise summaries and reusable artifacts | Markdown reports, notes, and structured data outputs |

## Resources

Use these bundled scripts:

- `fetch_channel.py` for inventory, date filtering, and metadata normalization
- `transcribe_with_fallback.py` for transcript API attempts, `yt-dlp` audio download, and local Whisper transcription
- `build_report.py` for topic grouping, summaries, and markdown or CSV outputs

Use these reference files:

- `references/dependencies.md`
- `references/filtering.md`
- `references/outputs.md`

## Dependencies

This skill uses:

- `yt-dlp` for channel inventory and audio download
- `youtube-transcript-api` for direct transcript fetch
- `faster-whisper` for local transcription fallback

Use commands such as:

```bash
uv run --with yt-dlp --with youtube-transcript-api --with faster-whisper python scripts/<script>.py ...
```

Pass `--no-check-certificates` to `yt-dlp` when the environment requires it.

Read `references/dependencies.md` for command patterns and dependency notes.
