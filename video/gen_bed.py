"""Synthesize a clean, royalty-free ambient scientific music bed (48 kHz stereo WAV).

Pure trigonometric additive harmonics + slow filter-like envelope modulation with zero
external audio assets, avoiding any Content ID flags while giving warm editorial cohesion
under sidechain ducking.
"""
from __future__ import annotations

import math
import struct
import wave
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT_WAV = HERE / "remotion" / "public" / "music" / "bed.wav"
SR = 48000
DUR_SEC = 195.0


def main() -> None:
    OUT_WAV.parent.mkdir(parents=True, exist_ok=True)
    n_samples = int(SR * DUR_SEC)
    # Warm D-minor/F-major modal progression frequencies (Hz) cycling every 16 s
    chords = [
        (146.83, 220.00, 261.63, 329.63),  # Dm9 color
        (174.61, 220.00, 293.66, 392.00),  # F6/9
        (130.81, 196.00, 246.94, 293.66),  # Cmaj9
        (110.00, 164.81, 220.00, 261.63),  # Am7
    ]
    bar_len = 16.0
    frames = bytearray()
    for i in range(n_samples):
        t = i / SR
        fade = min(1.0, t / 2.0, (DUR_SEC - t) / 3.0)
        chord_pos = (t / bar_len) % len(chords)
        idx0 = int(chord_pos)
        idx1 = (idx0 + 1) % len(chords)
        frac = chord_pos - idx0
        blend = 0.5 - 0.5 * math.cos(math.pi * min(1.0, max(0.0, (frac - 0.75) / 0.25))) if frac > 0.75 else 0.0

        c0 = chords[idx0]
        c1 = chords[idx1]
        lfo_l = 0.78 + 0.22 * math.sin(2.0 * math.pi * 0.11 * t)
        lfo_r = 0.78 + 0.22 * math.sin(2.0 * math.pi * 0.13 * t + 1.1)

        sig_l = 0.0
        sig_r = 0.0
        for k, (f0, f1) in enumerate(zip(c0, c1)):
            freq = f0 * (1.0 - blend) + f1 * blend
            wt = 0.26 / (1.0 + 0.45 * k)
            ph = 2.0 * math.pi * freq * t
            sig_l += wt * (math.sin(ph) + 0.18 * math.sin(2.0 * ph + 0.3))
            sig_r += wt * (math.sin(ph + 0.25) + 0.18 * math.sin(2.0 * ph - 0.2))

        pulse = 0.5 * (1.0 + math.sin(2.0 * math.pi * 0.25 * t))
        sig_l = (sig_l * lfo_l * (0.88 + 0.12 * pulse)) * fade * 0.32
        sig_r = (sig_r * lfo_r * (0.88 + 0.12 * pulse)) * fade * 0.32

        il = max(-32767, min(32767, int(sig_l * 32767)))
        ir = max(-32767, min(32767, int(sig_r * 32767)))
        frames.extend(struct.pack("<hh", il, ir))

    with wave.open(str(OUT_WAV), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(bytes(frames))
    print(f"wrote ambient bed: {OUT_WAV} ({DUR_SEC:.0f}s)")


if __name__ == "__main__":
    main()
