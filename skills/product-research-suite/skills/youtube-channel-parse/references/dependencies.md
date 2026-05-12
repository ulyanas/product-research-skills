# Dependencies

This skill uses these runtime dependencies:

- `yt-dlp` for channel inventory, metadata retrieval, and audio download
- `youtube-transcript-api` for direct transcript retrieval
- `faster-whisper` for local transcription from downloaded audio

Do not install Whisper as a separate manual system dependency by default.

Use portable command patterns that install dependencies for the current run:

```bash
uv run --with yt-dlp --with youtube-transcript-api --with faster-whisper python scripts/<script>.py ...
```

## Script Chain

Use the bundled scripts in this order:

```bash
uv run --with yt-dlp python scripts/fetch_channel.py ...
uv run --with yt-dlp --with youtube-transcript-api --with faster-whisper python scripts/transcribe_with_fallback.py ...
uv run python scripts/build_report.py ...
```

`fetch_channel.py` needs `yt-dlp`.

`transcribe_with_fallback.py` needs `yt-dlp`, `youtube-transcript-api`, and `faster-whisper`.

`build_report.py` uses the standard library only.

## Restricted Network Environments

Some hosted agent environments block YouTube at the network or allowlist level.

When `yt-dlp`, transcript retrieval, and basic fetch attempts all fail with access errors such as `403 Forbidden`, blocked domain errors, or allowlist restrictions, treat that as an environment limitation rather than a content issue.

Confirm the restriction once, then stop retrying broad variants of the same YouTube request.

Tell the user that the environment needs YouTube access enabled before the skill can fetch channel inventory, metadata, or audio.

For Claude web sessions, point the user to:

- `Settings -> Capabilities`
- `Code execution and file creation`
- enable network egress
- allow `youtube.com` and `*.youtube.com`, or switch to a broader domain policy if appropriate

Tell the user to start a new conversation after changing the setting, because the network allowlist is session-scoped.

If the user does not want to change the setting, offer the best limited fallback available from non-YouTube sources and state the coverage limits clearly.

## YouTube Bot Detection

YouTube can allow lightweight metadata requests while blocking content retrieval.

Expect this pattern:

- channel inventory or `--dump-single-json` works
- timedtext transcript requests fail
- subtitle downloads fail
- audio downloads from `googlevideo.com` fail

Common symptoms:

- `youtube-transcript-api` returns bot-detection or cookie/authentication errors
- `yt-dlp` returns `403 Forbidden`
- `yt-dlp` returns `Sign in to confirm you're not a bot`
- direct `curl` to caption URLs returns a Google bot-detection page

Treat those failures as content-access restrictions rather than a bug in the filter or report logic.

When cookies are available in the environment, prefer passing them to `yt-dlp`.

Supported recovery options:

- `--cookies /path/to/cookies.txt`
- `--cookies-from-browser <browser>`

If cookies are unavailable and the environment IP is blocked, explain that the skill can still catalog metadata while captions and media remain inaccessible.

## Whisper Runtime

Run local transcription through `faster-whisper` with `uv run`.

Example:

```bash
uv run --with yt-dlp --with youtube-transcript-api --with faster-whisper \
  python scripts/transcribe_with_fallback.py \
  --input-json output/<output_prefix>/filtered/<output_prefix>_videos.json \
  --output-root output \
  --output-prefix <output_prefix> \
  --whisper-model tiny.en
```

Use `--whisper-model tiny.en` by default for fast English transcription.

Use a larger model only when the user asks for higher accuracy or when transcript quality needs improvement.

The agent should let `faster-whisper` load the requested model at runtime.

On first use, model files may download automatically.

Treat that download as part of normal execution rather than a separate installation step.

If `uv run` is unavailable and a persistent Python install is required, use:

```bash
python3 -m pip install faster-whisper
```

Prefer `uv run --with faster-whisper` over manual installation when possible.

Use `--no-check-certificates` with `yt-dlp` when the environment requires it.

Use `tiny.en` or `tiny` for fast English transcription by default.

Use a larger Whisper model only when the user asks for higher accuracy or the transcript quality needs improvement.

Write scripts so they can reuse existing audio and transcript files from earlier runs.
