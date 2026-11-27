"""Generate ElevenLabs narration MP3s and character/word alignment JSON per scene.

Reads ELEVENLABS_API_KEY from environment or macOS Keychain (never prints the secret).
Skips scenes whose .mp3 and .align.json already exist unless --force or --only is set.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT_DIR = HERE / "remotion" / "public" / "vo"
CFG_PATH = HERE / "narration.json"


def get_elevenlabs_key() -> str:
    """Resolve ElevenLabs API key from env or macOS Keychain without logging it."""
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if key:
        return key
    for svc in ("ELEVENLABS_API_KEY", "elevenlabs-api", "elevenlabs"):
        try:
            res = subprocess.run(
                ["security", "find-generic-password", "-s", svc, "-w"],
                capture_output=True,
                text=True,
                check=True,
            )
            if res.stdout.strip():
                return res.stdout.strip()
        except subprocess.CalledProcessError:
            continue
    raise RuntimeError("ELEVENLABS_API_KEY not found in env or macOS Keychain")


def words_from_alignment(al: dict) -> list[dict]:
    """Convert ElevenLabs character alignment arrays into word timestamp intervals."""
    chars = al["characters"]
    starts = al["character_start_times_seconds"]
    ends = al["character_end_times_seconds"]
    words = []
    cur = ""
    s0 = None
    prev_end = 0.0
    for c, a, b in zip(chars, starts, ends):
        if c.isspace():
            if cur:
                words.append({"w": cur, "start": round(s0, 3), "end": round(prev_end, 3)})
                cur = ""
            continue
        if not cur:
            s0 = a
        cur += c
        prev_end = b
    if cur:
        words.append({"w": cur, "start": round(s0, 3), "end": round(prev_end, 3)})
    return words


def main() -> None:
    ap = argparse.ArgumentParser(description="Synthesize per-scene ElevenLabs narration")
    ap.add_argument("--only", help="Comma-separated scene IDs to regenerate")
    ap.add_argument("--force", action="store_true", help="Overwrite existing audio")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cfg = json.loads(CFG_PATH.read_text(encoding="utf-8"))
    key = get_elevenlabs_key()
    v = cfg["voice"]
    scenes = cfg["scenes"]
    only = set(args.only.split(",")) if args.only else None

    for i, s in enumerate(scenes):
        sid = s["id"]
        if only and sid not in only:
            continue
        mp3_path = OUT_DIR / f"{sid}.mp3"
        align_path = OUT_DIR / f"{sid}.align.json"
        if mp3_path.exists() and align_path.exists() and not args.force and not only:
            print(f"{sid}: cached")
            continue

        say_text = s.get("say", s["caption"])
        prev_text = scenes[i - 1].get("say", scenes[i - 1]["caption"]) if i > 0 else None
        next_text = scenes[i + 1].get("say", scenes[i + 1]["caption"]) if i + 1 < len(scenes) else None
        body = {
            "text": say_text,
            "model_id": v["model_id"],
            "voice_settings": {
                "stability": 0.52,
                "similarity_boost": 0.78,
                "style": 0.0,
                "use_speaker_boost": True,
                "speed": v["speed"],
            },
        }
        if prev_text:
            body["previous_text"] = prev_text
        if next_text:
            body["next_text"] = next_text

        req = urllib.request.Request(
            f"https://api.elevenlabs.io/v1/text-to-speech/{v['voice_id']}/with-timestamps?output_format=mp3_44100_192",
            data=json.dumps(body).encode("utf-8"),
            headers={"xi-api-key": key, "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read())

        mp3_path.write_bytes(base64.b64decode(data["audio_base64"]))
        al = data["alignment"]
        words = words_from_alignment(al)
        align_path.write_text(
            json.dumps(
                {
                    "id": sid,
                    "caption": s["caption"],
                    "say": say_text,
                    "duration": round(float(al["character_end_times_seconds"][-1]), 3),
                    "words": words,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"{sid}: synthesized {align_path.name} ({al['character_end_times_seconds'][-1]:.2f} s)")


if __name__ == "__main__":
    main()
