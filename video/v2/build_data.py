"""Build video/remotion/src/v2/data.json: every on-screen number and every cue for the V2 film.

Numbers come from the frozen sheets (data/extracted.json, data/H2/extracted.json) and
docs/data/explorer_data.json; timings come from the ElevenLabs alignment files in
video/remotion/public/v2/vo/. Spoken (phonetic) tokens are collapsed back into exact scientific
notation by `normalize_aligned_words`. Also writes docs/media/captions.vtt.

Run: python3 video/v2/build_data.py
"""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VO = ROOT / "video" / "remotion" / "public" / "v2" / "vo"
OUT = ROOT / "video" / "remotion" / "src" / "v2" / "data.json"
VTT_OUT = ROOT / "docs" / "media" / "captions.vtt"
FPS = 30

LEAD = 0.20    # silence before the voice in each scene (s)
TAIL = 0.50    # silence after the voice in each scene (s)
EXTRA_TAIL = {"s4": 1.2, "s5": 1.2, "s7": 1.8}   # holds: 3x zoom, proof board, locked close card
MAX_CAPTION_CHARS = 64
NARRATED_CHECKS = 74   # "Seventy-four automated checks passing" is baked into the s7 voiceover
FEATURED = ("H5-P4.F1", "H5-P6.F3", "H2-P2.F12", "H2-P3.F6", "H2-P5.F4")

_PUNCT = ",.;:"
_SPANS: dict[tuple[str, ...], str] = {
    ("a-p-o-e-four",): "APOE4",
    ("a-p-o-e-three",): "APOE3",
    ("kep-ree",): "Khepri",
    ("step", "one"): "Step 1",
    ("rule", "c-five"): "Rule C5",
    ("one-b-six-eight",): "1B68",
    ("one-n-f-n",): "1NFN",
    ("arginine", "one", "hundred", "twelve"): "Arg112",
    ("glutamate", "one", "hundred", "nine"): "Glu109",
    ("cysteine", "one", "hundred", "twelve"): "Cys112",
    ("arginine", "sixty-one", "to", "glutamate", "one", "hundred", "nine"): "Arg61–Glu109",
    ("arginine", "sixty-one"): "Arg61",
    ("two", "point", "five", "three", "angstrom"): "2.53 Å",
    ("three", "point", "five", "three", "angstrom"): "3.53 Å",
    ("three", "point", "five", "three"): "3.53",
    ("five", "point", "three", "four", "angstroms"): "5.34 Å",
    ("five", "point", "three", "four", "angstrom"): "5.34 Å",
    ("h-two",): "H2",
    ("h-five",): "H5",
    ("apo-e-r-two",): "ApoER2",
    ("n-h-e-six",): "NHE6",
    ("p-h",): "pH",
    ("l-r-p-one",): "LRP1",
    ("l-t-p",): "LTP",
    ("three-fold",): "3-fold",
    ("fifty-three", "of", "eighty-four"): "53 of 84",
    ("v-a-t-p-ases",): "V-ATPases",
    ("twenty-eight",): "28",
    ("thirty", "entries"): "30 entries",
    ("one", "hundred", "twenty-six"): "126",
    ("one", "hundred", "twenty"): "120",
    ("ninety-one",): "91",
    ("twenty-nine",): "29",
    ("about", "forty-five", "percent"): "~45%",
    ("forty-five", "percent"): "45%",
    ("zero", "tier", "one"): "0 Tier 1",   # must outrank ("zero","tier") and ("tier","one")
    ("tier", "one"): "Tier 1",
    ("seventy-four",): "74",
    ("three-d",): "3D",
    ("zero", "estimated"): "0 estimated",
    ("zero", "review-paper"): "0 review-paper",
    ("zero", "predicted"): "0 predicted",
    ("zero", "retracted"): "0 retracted",
    ("zero", "validator"): "0 validator",
    ("zero", "tier"): "0 Tier",
    ("four", "paywalled"): "4 paywalled",
}
# Longest match first, so "one hundred twenty-six" beats "one hundred twenty" and 3-word spans beat 2-word ones.
_SPANS_BY_LENGTH = sorted(_SPANS.items(), key=lambda kv: len(kv[0]), reverse=True)


def _key(word: str) -> str:
    return word.rstrip(_PUNCT).lower()


def _match(keys: list[str], i: int, span: tuple[str, ...]) -> str | None:
    """Return the suffix kept after a match ('' / "'s"), or None. Only the last token may carry 's."""
    n = len(span)
    if i + n > len(keys):
        return None
    if tuple(keys[i:i + n - 1]) != span[:-1]:
        return None
    last = keys[i + n - 1]
    if last == span[-1]:
        return ""
    if last == span[-1] + "'s":
        return "'s"
    return None


def normalize_aligned_words(words: list[dict]) -> list[dict]:
    """Collapse spoken-form spans into scientific notation.

    The merged word keeps the first word's `start` and the last word's `end`, plus the last word's
    trailing `,.;:` punctuation (and a possessive 's). Bare words that start a span but do not
    complete one (e.g. "thirty days") pass through untouched.
    """
    keys = [_key(w["w"]) for w in words]
    out: list[dict] = []
    i = 0
    while i < len(words):
        for span, repl in _SPANS_BY_LENGTH:
            poss = _match(keys, i, span)
            if poss is None:
                continue
            n = len(span)
            last = words[i + n - 1]["w"]
            trailing = last[len(last.rstrip(_PUNCT)):]
            out.append({**words[i], "w": repl + poss + trailing, "end": words[i + n - 1]["end"]})
            i += n
            break
        else:
            out.append(words[i])
            i += 1
    return out


def caption_chunks(words: list[dict], max_chars: int = MAX_CAPTION_CHARS) -> list[dict]:
    """Sentence-aware cues of <= max_chars: split a long sentence at the clause break nearest its middle."""
    sentences, cur = [], []
    for w in words:
        cur.append(w)
        if w["w"][-1] in ".?!":
            sentences.append(cur)
            cur = []
    if cur:
        sentences.append(cur)

    def text(ws: list[dict]) -> str:
        return " ".join(x["w"] for x in ws)

    def split(ws: list[dict]) -> list[list[dict]]:
        total = len(text(ws))
        if total <= max_chars or len(ws) < 2:
            return [ws]
        best, best_score = 1, 1e9
        for k in range(1, len(ws)):
            left = len(text(ws[:k]))
            score = abs(left - total / 2) - (14 if ws[k - 1]["w"][-1] in ",;:" else 0)
            if score < best_score:
                best, best_score = k, score
        return split(ws[:best]) + split(ws[best:])

    return [{"text": text(c), "start": c[0]["start"], "end": c[-1]["end"]} for s in sentences for c in split(s)]


def audio_seconds(mp3: Path, fallback: float) -> float:
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp3)],
            capture_output=True, text=True, check=True)
        return float(r.stdout.strip())
    except (OSError, subprocess.CalledProcessError, ValueError):
        return fallback


def count_tests() -> int:
    """Number of unit tests `python -m unittest discover -s tests` would run."""
    tests_dir = str(ROOT / "tests")
    for p in (str(ROOT), tests_dir):
        if p not in sys.path:
            sys.path.insert(0, p)

    def flatten(suite):
        for t in suite:
            if isinstance(t, unittest.TestSuite):
                yield from flatten(t)
            else:
                yield t

    return sum(1 for _ in flatten(unittest.TestLoader().discover(tests_dir)))


def vtt_time(t: float) -> str:
    ms = round(t * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d}.{ms % 1000:03d}"


def write_vtt(scenes: list[dict]) -> None:
    lines = ["WEBVTT", ""]
    n = 0
    for s in scenes:
        base = s["from"] / FPS
        caps = s["captions"]
        for i, c in enumerate(caps):
            start = base + c["start"]
            end = base + c["end"]
            if i + 1 < len(caps):
                end = min(end + 0.35, base + caps[i + 1]["start"] - 0.02)
            n += 1
            lines += [str(n), f"{vtt_time(start)} --> {vtt_time(max(end, start + 0.3))}", c["text"], ""]
    VTT_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    h5 = json.loads((ROOT / "data" / "extracted.json").read_text(encoding="utf-8"))
    h2 = json.loads((ROOT / "data" / "H2" / "extracted.json").read_text(encoding="utf-8"))
    ex = json.loads((ROOT / "docs" / "data" / "explorer_data.json").read_text(encoding="utf-8"))
    narr = json.loads((ROOT / "video" / "v2" / "narration.json").read_text(encoding="utf-8"))

    # frozen sheets and the explorer must agree before anything goes on screen
    if not (h5["n_findings"] == ex["hypotheses"]["H5"]["n_findings"] == 67):
        raise ValueError("H5 finding count drifted")
    if not (h2["n_findings"] == ex["hypotheses"]["H2"]["n_findings"] == 53):
        raise ValueError("H2 finding count drifted")
    if not (h5["n_papers"] == ex["hypotheses"]["H5"]["n_papers"]):
        raise ValueError("H5 paper count drifted")
    if not (h2["n_papers"] == ex["hypotheses"]["H2"]["n_papers"]):
        raise ValueError("H2 paper count drifted")

    scenes, t = [], 0.0
    for s in narr["scenes"]:
        sid = s["id"]
        al = json.loads((VO / f"{sid}.align.json").read_text(encoding="utf-8"))
        dur_audio = audio_seconds(VO / f"{sid}.mp3", al["duration"])
        frames = round((LEAD + dur_audio + TAIL + EXTRA_TAIL.get(sid, 0.0)) * FPS)
        words = [{"w": w["w"], "start": round(w["start"] + LEAD, 3), "end": round(w["end"] + LEAD, 3)}
                 for w in normalize_aligned_words(al["words"])]
        caps = caption_chunks(words)
        too_long = [c["text"] for c in caps if len(c["text"]) > MAX_CAPTION_CHARS]
        if too_long:
            print(f"warn: {sid} caption over {MAX_CAPTION_CHARS} chars: {too_long}")
        scenes.append({
            "id": sid, "theme": s["theme"], "title": s["title"], "from": round(t * FPS), "frames": frames,
            "voiceAt": LEAD, "audio": f"v2/vo/{sid}.mp3", "audioSeconds": round(dur_audio, 3),
            "words": words, "captions": caps,
        })
        t += frames / FPS
    total = sum(s["frames"] for s in scenes)

    tot, hy = ex["totals"], ex["hypotheses"]
    g = ex["geometry"]
    by_id = {f["id"]: f for f in ex["findings"]}
    featured = {}
    for fid in FEATURED:
        f = by_id[fid]
        featured[fid] = {
            "id": fid, "hyp": f["hyp"], "pmid": f["pmid"], "location": f["location"], "direction": f["direction"],
            "quote": f["quote"], "description": f["description"], "effect": f["stats"]["effect_size"]["value"],
            "pValue": f["p_value"], "year": f["year"], "tier": f["tier"],
        }

    tests = count_tests()
    if tests != NARRATED_CHECKS:
        raise ValueError(f"{tests} unit tests, but the voiceover says {NARRATED_CHECKS}: re-record or fix the tests")

    data = {
        "fps": FPS, "totalFrames": total, "scenes": scenes,
        "counts": {
            "entries": tot["n_papers_total"], "uniquePapers": tot["n_unique_papers"],
            "findings": tot["n_findings_total"], "contradicting": tot["n_contradicting_total"],
            "supporting": tot["n_findings_total"] - tot["n_contradicting_total"],
            "printedStats": tot["n_printed_stats_total"], "structures": tot["n_structures"],
            "tests": tests, "auditedPct": 100,
            "paywalled": (hy["H5"]["n_papers"] - hy["H5"]["n_fulltext_oa"]) + (hy["H2"]["n_papers"] - hy["H2"]["n_fulltext_oa"]),
            "tier1Def": "human non-AD/non-aged iPSC",
            **{h: {**{k: hy[h][k] for k in ("n_papers", "n_findings", "n_contradicting", "n_supporting", "n_printed_stats", "n_tier1")},
                   "n_unavailable": hy[h]["n_papers"] - hy[h]["n_fulltext_oa"]} for h in ("H5", "H2")},
        },
        "geometry": {
            "arg112": {"struct": "1B68", **g["1b68_Arg112_Glu109"]},
            "arg61Apoe4": {"struct": "1B68", **g["1b68_Arg61_Glu109"]},
            "arg61Apoe3": {"struct": "1NFN", **g["1nfn_Arg61_Glu109"]},
        },
        "featured": featured,
        "urls": {"site": "drahmed7887.github.io/hack-meccog-apoe4", "repo": "github.com/DrAhmed7887/hack-meccog-apoe4"},
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    write_vtt(scenes)
    print(f"tests {tests} | H5 {data['counts']['H5']['n_findings']} H2 {data['counts']['H2']['n_findings']} | "
          f"{data['counts']['uniquePapers']} papers {data['counts']['findings']} findings {data['counts']['contradicting']} contra")
    print(f"total {total} frames = {total / FPS:.2f} s -> {OUT.relative_to(ROOT)}, {VTT_OUT.relative_to(ROOT)}")
    for s in scenes:
        print(f"  {s['id']:3s} from {s['from'] / FPS:6.2f}s  {s['frames'] / FPS:5.2f}s  {len(s['captions'])} cues")


if __name__ == "__main__":
    main()
