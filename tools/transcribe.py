#!/usr/bin/env python3
"""Transcribe audio/video (file path or URL) to a markdown transcript with timestamps.

Usage:
  python3 transcribe.py <media-or-url> [out.md] [model]

- URL: downloaded via yt-dlp first (audio stream)
- model: tiny | base | small | medium | large-v3  (default: small)
"""
import os
import re
import subprocess
import sys
import tempfile

from faster_whisper import WhisperModel


def fmt_ts(sec: float) -> str:
    h = int(sec // 3600)
    m = int(sec % 3600 // 60)
    s = sec % 60
    return f"{h:02d}:{m:02d}:{s:05.2f}"


def fetch_media(src: str) -> str:
    """If src is a URL, download the audio track with yt-dlp; otherwise use the local file."""
    if re.match(r"^https?://", src):
        with tempfile.TemporaryDirectory() as tmp:
            cmd = [
                "yt-dlp",
                "-f", "bestaudio/best",
                "--audio-conversion", "mp3",
                "-x",
                "-o", os.path.join(tmp, "audio.%(ext)s"),
                src,
            ]
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            files = [os.path.join(tmp, f) for f in os.listdir(tmp)]
            return files[0]
    if not os.path.isfile(src):
        sys.exit(f"file not found: {src}")
    return src


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    src = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else None
    model_name = sys.argv[3] if len(sys.argv) > 3 else "small"

    if not out:
        base = re.sub(r"\.[^.]+$", "", os.path.basename(src))
        out = os.path.join("sources", base + ".md")
        os.makedirs("sources", exist_ok=True)

    media = fetch_media(src)
    print(f"transcribing {media} with model {model_name} ...", file=sys.stderr)

    import torch
    if torch.cuda.is_available():
        try:
            model = WhisperModel(model_name, device="cuda", compute_type="float16")
            device = "cuda"
        except ValueError:  # ctranslate2 without CUDA support
            model = WhisperModel(model_name, device="cpu", compute_type="int8")
            device = "cpu"
    else:
        model = WhisperModel(model_name, device="cpu", compute_type="int8")
        device = "cpu"
    segments, info = model.transcribe(media, vad_filter=True)
    lines = [
        f"# Transcript: {os.path.basename(src) or src}",
        "",
        f"- Source: {src}",
        f"- Language: {info.language}",
        f"- Duration: {fmt_ts(info.duration)}",
        f"- Model: {model_name} ({device})",
        "",
    ]
    for s in segments:
        lines.append(f"[{fmt_ts(s.start)}] {s.text.strip()}")
    with open(out, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(out)


if __name__ == "__main__":
    main()
