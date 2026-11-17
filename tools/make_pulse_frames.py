"""ECG monitor sweep frames for the heart-rate sub-dial background (RGBA PNGs). Stdlib only.
Usage: python3 -I make_pulse_frames.py <drawable_dir>
  pulse_f00..pulse_f15.png 84x34: a red ECG trace drawn left to right with a bright head and a fading tail
  (one beat per sweep; 16 frames at 12 fps = 1.33 s per sweep). pulse_static.png = faint full trace."""
import math
import os
import struct
import sys
import zlib

OUT = sys.argv[1]
W, H, SS, N = 84, 34, 4, 16
# ECG polyline across the width: flat, P wave, QRS spike, T wave, flat
PTS = [(0, 20), (22, 20), (26, 17), (30, 20), (34, 20), (37, 24), (41, 3), (45, 30), (48, 20),
       (55, 20), (60, 15), (65, 20), (84, 20)]


def write_png(name, pix):
    rows = []
    for y in range(H):
        row = bytearray([0])
        for x in range(W):
            row += bytes(pix(x, y))
        rows.append(bytes(row))

    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    with open(os.path.join(OUT, name), "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 6, 0, 0, 0))
                + chunk(b"IDAT", zlib.compress(b"".join(rows), 9)) + chunk(b"IEND", b""))


def dist_to_trace(px, py):
    best = 1e9
    for (x0, y0), (x1, y1) in zip(PTS, PTS[1:]):
        vx, vy = x1 - x0, y1 - y0
        t = max(0.0, min(1.0, ((px - x0) * vx + (py - y0) * vy) / (vx * vx + vy * vy)))
        best = min(best, math.hypot(px - (x0 + t * vx), py - (y0 + t * vy)))
    return best


def frame(head_x, intensity):
    def pix(x, y):
        a_sum, glow = 0.0, 0.0
        for i in range(SS):
            for j in range(SS):
                px, py = x + (i + 0.5) / SS, y + (j + 0.5) / SS
                d = dist_to_trace(px, py)
                if head_x is None:
                    fade = 1.0
                elif 0 <= head_x - px <= 52:  # samples behind the sweep head fade out over 52 px
                    fade = 1 - (head_x - px) / 52
                else:
                    fade = 0.0
                if d <= 1.3:
                    a_sum += fade
                elif d <= 3.2:
                    glow += fade * (1 - (d - 1.3) / 1.9) * 0.35
        a = min(1.0, (a_sum + glow) / (SS * SS)) * intensity
        if a <= 0:
            return (0, 0, 0, 0)
        hot = 1.0 if head_x is not None and abs(x - head_x) < 3 else 0.0
        r, g, b = 255, int(60 + 120 * hot), int(70 + 110 * hot)
        return (r, g, b, int(a * 255))
    return pix


for k in range(N):
    write_png("pulse_f%02d.png" % k, frame((k + 1) * (W + 52) / N, 0.9))
write_png("pulse_static.png", frame(None, 0.35))
