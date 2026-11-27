#!/usr/bin/env bash
# Render 1080p 30fps MecCogFilmV2 in memory-safe 1000-frame video chunks + WAV audio, then run master.sh.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/video/remotion"
CHROME="$(ls -d ~/.cache/hyperframes/chrome/chrome-headless-shell/*/chrome-headless-shell-mac-arm64/chrome-headless-shell | head -1)"
TOTAL=$(python3 -c "import json; print(json.load(open('src/v2/data.json'))['totalFrames'])")

rm -rf out/chunks
mkdir -p out/chunks
: > out/chunks/list.txt
for ((a=0; a<TOTAL; a+=1000)); do
  b=$(( a+999 < TOTAL-1 ? a+999 : TOTAL-1 ))
  f="out/chunks/c_$(printf %05d "$a").mp4"
  npx remotion render src/index.ts MecCogFilmV2 "$f" --frames="$a-$b" --muted --concurrency=2 --crf=16 \
    --browser-executable="$CHROME" --log=error
  echo "file '$(basename "$f")'" >> out/chunks/list.txt
  echo "chunk $a-$b done $(date +%H:%M:%S)"
done

npx remotion render src/index.ts MecCogFilmV2 out/chunks/audio.wav --codec=wav --browser-executable="$CHROME" --log=error
ffmpeg -v error -y -f concat -safe 0 -i out/chunks/list.txt -i out/chunks/audio.wav -map 0:v -map 1:a -c:v copy -c:a pcm_s16le out/raw_combined_v2.mov
ffmpeg -v error -y -i out/raw_combined_v2.mov -c:v copy -c:a aac -b:a 256k out/raw_combined_v2.mp4
rm -f out/raw_combined_v2.mov

cd "$ROOT"
bash video/master.sh "$ROOT/video/remotion/out/raw_combined_v2.mp4"
