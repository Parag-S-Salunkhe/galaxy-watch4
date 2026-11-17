"""AOD assets drawn in white/grey so the face can tint them with the accent colour. Stdlib only.
Usage: python3 -I make_aod_theme_assets.py <drawable_dir>
  dial_aod.png        450x450  12 ticks: 12/3/6/9 white (bright accent), others grey (deeper accent shade)
  aod_hour.png        30x150   pivot (15,128): white -> light grey gradient bold hand (tinted = accent shades)
  aod_minute.png      24x232   pivot (12,224): plain white bold hand (stays white)
  aod_minute_dot.png  24x232   pivot (12,224): only the rim dot at r=206 (tinted = accent)"""
import math
import os
import struct
import sys
import zlib

OUT = sys.argv[1]
SS = 4


def write_png(name, w, h, pix):
    rows = []
    for y in range(h):
        row = bytearray([0])
        for x in range(w):
            row += bytes(pix(x, y))
        rows.append(bytes(row))

    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    with open(os.path.join(OUT, name), "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
                + chunk(b"IDAT", zlib.compress(b"".join(rows), 9)) + chunk(b"IEND", b""))


def capsule(px, py, x0, y0, x1, y1, r0, r1):
    vx, vy = x1 - x0, y1 - y0
    t = max(0.0, min(1.0, ((px - x0) * vx + (py - y0) * vy) / (vx * vx + vy * vy)))
    cx, cy = x0 + t * vx, y0 + t * vy
    return math.hypot(px - cx, py - cy) <= r0 + (r1 - r0) * t


def supersample(color_at):
    def pix(x, y):
        r = g = b = a = 0.0
        for i in range(SS):
            for j in range(SS):
                c = color_at(x + (i + 0.5) / SS, y + (j + 0.5) / SS)
                if c:
                    r += c[0]; g += c[1]; b += c[2]; a += 1
        if a == 0:
            return (0, 0, 0, 0)
        return (int(r / a), int(g / a), int(b / a), int(255 * a / (SS * SS)))
    return pix


def grey(v):
    return (v, v, v)


write_png("aod_hour.png", 30, 150, supersample(
    lambda px, py: grey(int(255 - 50 * min(1.0, py / 140))) if capsule(px, py, 15, 140, 15, 12, 11.0, 8.5) else None))
write_png("aod_minute.png", 24, 232, supersample(
    lambda px, py: grey(250) if capsule(px, py, 12, 236 - 12, 12, 224 - 178, 8.5, 6.0) else None))
write_png("aod_minute_dot.png", 24, 232, supersample(
    lambda px, py: grey(255) if math.hypot(px - 12, py - (224 - 206)) <= 6.5 else None))

C = 225.0
ticks = []
for i in range(12):
    a = math.radians(i * 30)
    major = i % 3 == 0
    length, rad = (30.0, 5.0) if major else (20.0, 3.4)
    sx, sy = math.sin(a), -math.cos(a)
    ticks.append((C + sx * 214, C + sy * 214, C + sx * (214 - length), C + sy * (214 - length), rad, grey(255 if major else 180)))


def dial_at(px, py):
    if math.hypot(px - C, py - C) < 175:
        return None
    for x0, y0, x1, y1, r, col in ticks:
        if capsule(px, py, x0, y0, x1, y1, r, r):
            return col
    return None


write_png("dial_aod.png", 450, 450, supersample(dial_at))
