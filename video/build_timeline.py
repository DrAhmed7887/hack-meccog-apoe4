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
TEASER_IDS = {"s1", "s3", "s7"}


_PUNCT = ",.;:"
_PHONETIC_SPANS: dict[tuple[str, ...], str] = {
    ("one", "hundred", "twenty-six"): "126",
    ("one", "hundred", "twenty"): "120",
    ("arginine", "one", "hundred", "twelve"): "Arg112",
    ("position", "one", "hundred", "twelve"): "position 112",
    ("glutamate", "one", "hundred", "nine"): "Glu109",
    ("two", "point", "five", "three", "angstrom"): "2.53 Å",
    ("five", "point", "three", "four", "angstroms"): "5.34 Å",
    ("three", "point", "five", "three"): "3.53",
    ("arginine", "sixty-one"): "Arg61",
    ("molstar", "three-d"): "Mol* 3D",
    ("one-b-six-eight",): "1B68",
    ("one-n-f-n",): "1NFN",
    ("three-d",): "3D",
    ("step", "one"): "Step 1",
    ("tier", "two"): "Tier 2",
    ("twenty-eight",): "28",
    ("twenty-nine",): "29",
    ("thirty",): "30",
    ("zero", "retracted"): "0 retracted",
    ("zero", "errors"): "0 errors",
    ("four", "gated"): "4 gated",
}
# Longest match first so 'one hundred twenty-six' wins over 'one hundred twenty'.
_SPANS_BY_LENGTH = sorted(_PHONETIC_SPANS.items(), key=lambda kv: len(kv[0]), reverse=True)


def normalize_aligned_words(words: list[dict]) -> list[dict]:
    """Replace spoken-form spans with scientific notation, keeping span timing."""
    keys = [w["w"].rstrip(_PUNCT).lower() for w in words]
    out: list[dict] = []
    i = 0
    while i < len(words):
        for span, repl in _SPANS_BY_LENGTH:
            n = len(span)
            if tuple(keys[i : i + n]) == span:
                last = words[i + n - 1]["w"]
                trailing = last[len(last.rstrip(_PUNCT)) :]
                out.append({**words[i], "w": repl + trailing, "end": words[i + n - 1]["end"]})
                i += n
                break
        else:
            out.append(words[i])
            i += 1
    return out


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
                "captions": chunk_words(normalize_aligned_words(al["words"]), max_words=8),
            }
        )
        cursor += dur_frames

    teaser_scenes: list[dict] = []
    teaser_cursor = 0
    for s in (s for s in scenes_out if s["id"] in TEASER_IDS):
        teaser_scenes.append({**s, "from": teaser_cursor})
        teaser_cursor += s["durationInFrames"]

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        json.dumps(
            {
                "fps": FPS,
                "width": 1920,
                "height": 1080,
                "totalFrames": cursor,
                "scenes": scenes_out,
                "teaserTotalFrames": teaser_cursor,
                "teaserScenes": teaser_scenes,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        f"timeline.json: {len(scenes_out)} scenes, {cursor} frames ({cursor / FPS:.2f} s); "
        f"teaser {len(teaser_scenes)} scenes, {teaser_cursor} frames"
    )


if __name__ == "__main__":
    main()
