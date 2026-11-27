"""Generate ElevenLabs Creator narration (George + timestamps), studio music (/v1/music), and soft SFX.

Reads ELEVENLABS_API_KEY from env or macOS Keychain (never logs secrets).
Converts the studio score into 48 kHz stereo WAV for sidechain mixing.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PUB = ROOT / "video" / "remotion" / "public" / "v2"
VO_DIR = PUB / "vo"
MUSIC_DIR = PUB / "music"
SFX_DIR = PUB / "sfx"
CFG_PATH = HERE / "narration.json"


def get_elevenlabs_key() -> str:
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if key:
        return key
    for svc in ("ELEVENLABS_API_KEY", "elevenlabs-api", "elevenlabs"):
        try:
            r = subprocess.run(
                ["security", "find-generic-password", "-s", svc, "-w"],
                capture_output=True, text=True, check=True,
            )
            if r.stdout.strip():
                return r.stdout.strip()
        except subprocess.CalledProcessError:
            continue
    raise RuntimeError("ELEVENLABS_API_KEY not found in env or Keychain")


def words_from_alignment(al: dict) -> list[dict]:
    chars = al["characters"]
    starts = al["character_start_times_seconds"]
    ends = al["character_end_times_seconds"]
    words, cur, s0, prev_end = [], "", None, 0.0
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


def api_post(url: str, key: str, body: dict, timeout: int = 240) -> bytes:
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"xi-api-key": key, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def synth_vo(key: str, force: bool = False) -> None:
    VO_DIR.mkdir(parents=True, exist_ok=True)
    cfg = json.loads(CFG_PATH.read_text(encoding="utf-8"))
    v = cfg["voice"]
    scenes = cfg["scenes"]
    for i, s in enumerate(scenes):
        sid = s["id"]
        mp3_path = VO_DIR / f"{sid}.mp3"
        align_path = VO_DIR / f"{sid}.align.json"
        if mp3_path.exists() and align_path.exists() and not force:
            print(f"vo {sid}: cached")
            continue
        say_text = s["say"]
        body = {
            "text": say_text,
            "model_id": v["model_id"],
            "voice_settings": {
                "stability": 0.50,
                "similarity_boost": 0.78,
                "style": 0.12,
                "use_speaker_boost": True,
                "speed": v.get("speed", 1.0),
            },
        }
        if i > 0:
            body["previous_text"] = scenes[i - 1]["say"]
        if i + 1 < len(scenes):
            body["next_text"] = scenes[i + 1]["say"]
        raw = api_post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{v['voice_id']}/with-timestamps?output_format=mp3_44100_192",
            key, body, timeout=120,
        )
        data = json.loads(raw)
        mp3_path.write_bytes(base64.b64decode(data["audio_base64"]))
        al = data["alignment"]
        words = words_from_alignment(al)
        align_path.write_text(
            json.dumps({
                "id": sid,
                "caption": s["caption"],
                "say": say_text,
                "duration": round(float(al["character_end_times_seconds"][-1]), 3),
                "words": words,
            }, indent=2),
            encoding="utf-8",
        )
        print(f"vo {sid}: synthesized {al['character_end_times_seconds'][-1]:.2f} s ({len(words)} words)")


def synth_music(key: str, force: bool = False) -> None:
    MUSIC_DIR.mkdir(parents=True, exist_ok=True)
    wav_path = MUSIC_DIR / "bed.wav"
    mp3_path = MUSIC_DIR / "bed_src.mp3"
    if wav_path.exists() and not force:
        print("music bed.wav: cached")
        return
    body = {
        "prompt": (
            "Intimate warm felt piano and soft cello harmonics scientific documentary underscore, "
            "delicate glass marimba pulse, gentle analog sub-bass, strictly instrumental, no vocals"
        ),
        "music_length_ms": 165000,
        "force_instrumental": True,
    }
    raw = api_post("https://api.elevenlabs.io/v1/music", key, body, timeout=300)
    mp3_path.write_bytes(raw)
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", str(mp3_path), "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", str(wav_path)],
        check=True,
    )
    print(f"music: synthesized {len(raw)} bytes -> {wav_path.name}")


def synth_sfx(key: str, force: bool = False) -> None:
    SFX_DIR.mkdir(parents=True, exist_ok=True)
    specs = {
        "wipe_soft.mp3": "Subtle warm felt air whoosh, quiet cinema editorial page turn transition, clean studio foley, no metallic ring",
        "lock_click.mp3": "Soft tactile wooden-glass microscope stage click, delicate precision instrument settle, studio foley",
    }
    for fname, prompt in specs.items():
        p = SFX_DIR / fname
        if p.exists() and not force:
            print(f"sfx {fname}: cached")
            continue
        raw = api_post(
            "https://api.elevenlabs.io/v1/sound-generation",
            key,
            {"text": prompt, "duration_seconds": 1.2, "prompt_influence": 0.4, "model_id": "eleven_text_to_sound_v2"},
            timeout=90,
        )
        p.write_bytes(raw)
        print(f"sfx {fname}: synthesized {len(raw)} bytes")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--skip-music", action="store_true")
    ap.add_argument("--skip-vo", action="store_true")
    ap.add_argument("--skip-sfx", action="store_true")
    args = ap.parse_args()
    key = get_elevenlabs_key()
    if not args.skip_vo:
        synth_vo(key, force=args.force)
    if not args.skip_sfx:
        synth_sfx(key, force=args.force)
    if not args.skip_music:
        synth_music(key, force=args.force)


if __name__ == "__main__":
    main()
