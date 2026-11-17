"""Draw analog AOD assets (RGBA PNGs, anti-aliased). Stdlib only.
Usage: python3 -I make_aod_assets.py <drawable_dir>
  hand_hour.png   28x150, pivot at (14, 128)  -> pivotY 0.8533
  hand_minute.png 22x210, pivot at (11, 188)  -> pivotY 0.8952
  dial_aod.png    450x450, 12 tick marks (12/3/6/9 electric blue, others white)"""
import math
import os
import struct
import sys
import zlib

OUT = sys.argv[1]
SS = 4
WHITE, BLUE, ICE = (255, 255, 255), (46, 168, 255), (205, 232, 255)


def png(path, w, h, pix):
    rows = []
    for y in range(h):
        row = bytearray([0])
        for x in range(w):
            row += bytes(pix(x, y))
        rows.append(bytes(row))

    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    data = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)) \
        + chunk(b"IDAT", zlib.compress(b"".join(rows), 9)) + chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(data)


def coverage(x, y, inside):
    hits = sum(inside(x + (i + 0.5) / SS, y + (j + 0.5) / SS) for i in range(SS) for j in range(SS))
    return hits / (SS * SS)


def capsule(px, py, x0, y0, x1, y1, r0, r1):
    """Inside a tapered capsule from (x0,y0) radius r0 to (x1,y1) radius r1."""
    vx, vy = x1 - x0, y1 - y0
    t = max(0.0, min(1.0, ((px - x0) * vx + (py - y0) * vy) / (vx * vx + vy * vy)))
    cx, cy = x0 + t * vx, y0 + t * vy
    return math.hypot(px - cx, py - cy) <= r0 + (r1 - r0) * t


def hand(path, w, h, tip_y, pivot_y, tail_y, r_base, r_tip, tip_color_len):
    cx = w / 2

    def inside(px, py):
        return capsule(px, py, cx, tail_y, cx, tip_y, r_base, r_tip)

    def pix(x, y):
        a = coverage(x, y, inside)
        c = BLUE if y < tip_y + tip_color_len else WHITE
        return (*c, int(a * 255))

    png(path, w, h, pix)


# hour: tip at y=10, pivot y=128, short tail to y=140; bold (11 px radius at base, 8 at tip)
hand(os.path.join(OUT, "hand_hour.png"), 28, 150, 10, 128, 140, 11.0, 8.0, 0)
# minute: tip at y=8, pivot y=188, tail to y=200; 8 px base radius, 5.5 tip; blue tip 34 px
hand(os.path.join(OUT, "hand_minute.png"), 22, 210, 8, 188, 200, 8.0, 5.5, 34)

C = 225.0
ticks = []
for i in range(12):
    ang = math.radians(i * 30)
    major = i % 3 == 0
    r_out, length, rad = 214.0, (30.0 if major else 20.0), (5.0 if major else 3.2)
    sx, sy = math.sin(ang), -math.cos(ang)
    ticks.append((C + sx * r_out, C + sy * r_out, C + sx * (r_out - length), C + sy * (r_out - length),
                  rad, BLUE if major else ICE))


def dial_pix(x, y):
    for x0, y0, x1, y1, rad, col in ticks:
        if abs(x - x0) > 40 and abs(x - x1) > 40:
            continue
        if abs(y - y0) > 40 and abs(y - y1) > 40:
            continue
        a = coverage(x, y, lambda px, py: capsule(px, py, x0, y0, x1, y1, rad, rad))
        if a > 0:
            return (*col, int(a * 255))
    return (0, 0, 0, 0)


png(os.path.join(OUT, "dial_aod.png"), 450, 450, dial_pix)
