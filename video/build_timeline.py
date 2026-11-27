"""Compile ElevenLabs word alignments into video/remotion/src/timeline.json."""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
VO_DIR = HERE / "remotion" / "public" / "vo"
CFG_PATH = HERE / "narration.json"
OUT_PATH = HERE / "remotion" / "src" / "timeline.json"
FPS = 30
TAIL_SEC = 0.55


def chunk_words(words: list[dict], max_words: int = 8) -> list[dict]:
    """Group aligned word intervals into concise readable caption cues."""
    cues: list[dict] = []
    cur: list[dict] = []
    for w in words:
        cur.append(w)
        ends_sentence = w["w"].endswith((".", ",", ";", ":"))
        if len(cur) >= max_words or (ends_sentence and len(cur) >= 4):
            cues.append(
                {
                    "text": " ".join(x["w"] for x in cur),
                    "start": cur[0]["start"],
                    "end": cur[-1]["end"],
                }
            )
            cur = []
    if cur:
        cues.append(
            {
                "text": " ".join(x["w"] for x in cur),
                "start": cur[0]["start"],
                "end": cur[-1]["end"],
            }
        )
    return cues


def main() -> None:
    cfg = json.loads(CFG_PATH.read_text(encoding="utf-8"))
    cursor = 0
    scenes_out = []
    for s in cfg["scenes"]:
        sid = s["id"]
        al = json.loads((VO_DIR / f"{sid}.align.json").read_text(encoding="utf-8"))
        dur_sec = float(al["duration"]) + TAIL_SEC
        dur_frames = max(60, int(round(dur_sec * FPS)))
        scenes_out.append(
            {
                "id": sid,
                "theme": s["theme"],
                "title": s["title"],
                "caption": s["caption"],
                "from": cursor,
                "durationInFrames": dur_frames,
                "audioSec": round(float(al["duration"]), 3),
                "captions": chunk_words(al["words"], max_words=8),
            }
        )
        cursor += dur_frames

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        json.dumps({"fps": FPS, "width": 1920, "height": 1080, "totalFrames": cursor, "scenes": scenes_out}, indent=2)
        + "\n",
        encoding="utf-8",
    )
    print(f"timeline.json: {len(scenes_out)} scenes, {cursor} frames ({cursor / FPS:.2f} s)")


if __name__ == "__main__":
    main()
