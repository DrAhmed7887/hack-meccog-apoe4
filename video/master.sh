#!/usr/bin/env bash
# Mix ElevenLabs narration + SFX with sidechain-ducked ElevenLabs /v1/music studio score,
# normalize to -16 LUFS, emit master 1080p MP4 + SRT captions (captions.vtt is written only by video/v2/build_data.py) + <15 MB web MP4 into docs/media/,
# extract contact_sheet_v2.png + per-scene full-res stills, and run ffprobe/ebur128/silencedetect/blackdetect QC.
set -euo pipefail

RAW="$1"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/video/remotion/out"
BED="$ROOT/video/remotion/public/v2/music/bed.wav"
DATA_JSON="$ROOT/video/remotion/src/v2/data.json"
FINAL="$OUT/MecCog_APOE4_Endosome_Bottleneck_1080p.mp4"
WEB_DIR="$ROOT/docs/media"
WEB_MP4="$WEB_DIR/apoe4_endosome_bottleneck_web.mp4"

mkdir -p "$OUT" "$WEB_DIR"

DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$RAW")
FADE_OUT_AT=$(python3 -c "print(max(0, float('$DUR') - 3.5))")
echo "Raw duration: ${DUR} s"

ffmpeg -v error -y -i "$RAW" -i "$BED" -filter_complex "
  [1:a]atrim=0:${DUR},asetpts=PTS-STARTPTS,volume=0.24,afade=t=in:d=1.5,afade=t=out:st=${FADE_OUT_AT}:d=3.5[bed];
  [0:a]asplit=2[vo][key];
  [bed][key]sidechaincompress=threshold=0.025:ratio=5:attack=40:release=450[duck];
  [vo][duck]amix=inputs=2:duration=first:normalize=0[mix]" \
  -map 0:v -map "[mix]" -c:v copy -c:a pcm_s16le "$OUT/mix_master_v2.mov"

read -r I TP LRA THRESH OFFSET < <(
  ffmpeg -hide_banner -i "$OUT/mix_master_v2.mov" -af loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 \
  | python3 -c "import sys,json; t=sys.stdin.read(); i=t.rindex('{'); d=json.loads(t[i:t.index('}', i)+1]); print(d['input_i'],d['input_tp'],d['input_lra'],d['input_thresh'],d['target_offset'])"
)

ffmpeg -v error -y -i "$OUT/mix_master_v2.mov" \
  -af "loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=${I}:measured_TP=${TP}:measured_LRA=${LRA}:measured_thresh=${THRESH}:offset=${OFFSET}:linear=true,aresample=48000" \
  -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -movflags +faststart -c:a aac -b:a 192k "$FINAL"

ffmpeg -v error -y -i "$FINAL" \
  -vf "scale=1280:720:flags=lanczos" -c:v libx264 -preset slow -crf 24 -pix_fmt yuv420p -movflags +faststart -c:a aac -b:a 128k "$WEB_MP4"

python3 - "$DATA_JSON" "${FINAL%.mp4}.srt" <<'PY'
import json, sys

d = json.load(open(sys.argv[1], encoding="utf-8"))

def ts_srt(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

srt_lines = []
n = 0
for s in d["scenes"]:
    base = s["from"] / d["fps"]
    caps = s["captions"]
    for i, c in enumerate(caps):
        nxt = caps[i + 1]["start"] if i + 1 < len(caps) else c["end"] + 0.55
        t0 = base + c["start"]
        t1 = base + min(nxt, c["end"] + 0.55) - 0.02
        n += 1
        srt_lines.append(f"{n}\n{ts_srt(t0)} --> {ts_srt(t1)}\n{c['text']}\n")

open(sys.argv[2], "w", encoding="utf-8").write("\n".join(srt_lines))
print(f"captions written: {n} cues")
PY

echo "== QC =="
ffprobe -v error -show_entries format=duration,size -of default=noprint_wrappers=1 "$FINAL"
ffprobe -v error -show_entries format=duration,size -of default=noprint_wrappers=1 "$WEB_MP4"
ffmpeg -hide_banner -i "$FINAL" -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I:|LRA:|Peak:)" | tail -3
echo "-- voice silences over 4 s:"
ffmpeg -hide_banner -i "$RAW" -af silencedetect=n=-45dB:d=4 -f null - 2>&1 | grep silence_ || echo "none"
echo "-- black frames:"
ffmpeg -hide_banner -i "$FINAL" -vf "blackdetect=d=0.1:pix_th=0.10" -an -f null - 2>&1 | grep blackdetect || echo "none"
ffmpeg -v error -y -i "$FINAL" -vf "fps=1/5,scale=384:-1,tile=6x6" -frames:v 1 "$OUT/contact_sheet_v2.png"

# Extract full-res 1920x1080 still at ~65% into each scene + set s3 peak caliper frame as docs/media/poster.jpg
python3 - "$DATA_JSON" "$FINAL" "$OUT" "$WEB_DIR/poster.jpg" <<'PY'
import json, subprocess, sys
from pathlib import Path
d = json.load(open(sys.argv[1], encoding="utf-8"))
mp4, out, poster = sys.argv[2], Path(sys.argv[3]), sys.argv[4]
for s in d["scenes"]:
    t = (s["from"] + 0.65 * s["frames"]) / d["fps"]
    dest = out / f"frame_{s['id']}.png"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", mp4, "-frames:v", "1", str(dest)], check=True)
    if s["id"] == "s3":
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", mp4, "-frames:v", "1", "-q:v", "2", poster], check=True)
print("extracted scene stills frame_s1..frame_s7 + poster.jpg")
PY
rm -f "$OUT/mix_master_v2.mov"
echo "DONE_MASTER_V2"
