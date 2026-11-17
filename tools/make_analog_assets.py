"""Draw Heritage Clean assets (RGBA PNGs, anti-aliased). Stdlib only.
Usage: python3 -I make_analog_assets.py <drawable_dir>
  hand_hour.png    34x150 pivot (17,128) -> pivotY 0.8533   white sword, dark inlay
  hand_minute.png  26x214 pivot (13,190) -> pivotY 0.8879   white sword, dark inlay
  hand_second.png  14x250 pivot (7,196)  -> pivotY 0.7840   white (tinted by theme), counterweight
  aod_hour.png     30x150 pivot (15,128)                      solid white, bold
  aod_minute.png   24x214 pivot (12,190)                      solid white, bold
  dial_active.png  450x450  60 minute ticks + 12 hour bars
  dial_aod.png     450x450  12 bright ticks (12/3/6/9 long)"""
import math
import os
import struct
import sys
import zlib

OUT = sys.argv[1]
SS = 4


def write_png(path, w, h, pix):
    rows = []
    for y in range(h):
        row = bytearray([0])
        for x in range(w):
            row += bytes(pix(x, y))
        rows.append(bytes(row))

    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    with open(os.path.join(OUT, path), "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
                + chunk(b"IDAT", zlib.compress(b"".join(rows), 9)) + chunk(b"IEND", b""))


def capsule(px, py, x0, y0, x1, y1, r0, r1):
    vx, vy = x1 - x0, y1 - y0
    t = max(0.0, min(1.0, ((px - x0) * vx + (py - y0) * vy) / (vx * vx + vy * vy)))
    cx, cy = x0 + t * vx, y0 + t * vy
    return math.hypot(px - cx, py - cy) <= r0 + (r1 - r0) * t


def render(w, h, layers):
    """layers: list of (inside_fn, rgb); later layers paint over earlier ones."""
    def pix(x, y):
        acc = [0.0, 0.0, 0.0, 0.0]
        for i in range(SS):
            for j in range(SS):
                px, py = x + (i + 0.5) / SS, y + (j + 0.5) / SS
                col = None
                for inside, rgb in layers:
                    if inside(px, py):
                        col = rgb
                if col:
                    acc[0] += col[0]; acc[1] += col[1]; acc[2] += col[2]; acc[3] += 1
        n = acc[3]
        if n == 0:
            return (0, 0, 0, 0)
        return (int(acc[0] / n), int(acc[1] / n), int(acc[2] / n), int(255 * n / (SS * SS)))
    return pix


WHITE, INLAY, GREY, LIGHT = (245, 245, 245), (24, 26, 30), (92, 97, 104), (210, 214, 220)


def sword(name, w, h, tip, pivot, tail, r_base, r_tip, inlay_from, inlay_to, inlay_r, cap_r):
    cx = w / 2
    write_png(name, w, h, render(w, h, [
        (lambda px, py: capsule(px, py, cx, tail, cx, tip, r_base, r_tip)
         or math.hypot(px - cx, py - pivot) <= cap_r, WHITE),
        (lambda px, py: capsule(px, py, cx, inlay_to, cx, inlay_from, inlay_r, inlay_r * 0.8), INLAY),
    ]))


def solid(name, w, h, tip, tail, r_base, r_tip):
    cx = w / 2
    write_png(name, w, h, render(w, h, [(lambda px, py: capsule(px, py, cx, tail, cx, tip, r_base, r_tip), WHITE)]))


sword("hand_hour.png", 34, 150, 12, 128, 142, 10.5, 7.0, 30, 112, 2.6, 8)
sword("hand_minute.png", 26, 214, 8, 190, 204, 8.0, 5.0, 26, 172, 2.2, 7)
write_png("hand_second.png", 14, 250, render(14, 250, [
    (lambda px, py: capsule(px, py, 7, 236, 7, 4, 1.8, 1.4)
     or math.hypot(px - 7, py - 226) <= 6.0 or math.hypot(px - 7, py - 196) <= 5.0, WHITE)]))
solid("aod_hour.png", 30, 150, 12, 140, 11.0, 8.5)
solid("aod_minute.png", 24, 214, 8, 202, 8.5, 6.0)

C = 225.0


def ticks_pix(specs):
    def inside_any(px, py):
        for x0, y0, x1, y1, r, col in specs:
            if capsule(px, py, x0, y0, x1, y1, r, r):
                return col
        return None

    def pix(x, y):
        # cheap reject: only the outer band holds ticks
        if math.hypot(x + 0.5 - C, y + 0.5 - C) < 170:
            return (0, 0, 0, 0)
        acc, n = [0, 0, 0], 0
        for i in range(SS):
            for j in range(SS):
                col = inside_any(x + (i + 0.5) / SS, y + (j + 0.5) / SS)
                if col:
                    acc = [acc[k] + col[k] for k in range(3)]; n += 1
        if n == 0:
            return (0, 0, 0, 0)
        return (acc[0] // n, acc[1] // n, acc[2] // n, 255 * n // (SS * SS))
    return pix


def tick(i, step_deg, r_out, length, r, col):
    a = math.radians(i * step_deg)
    sx, sy = math.sin(a), -math.cos(a)
    return (C + sx * r_out, C + sy * r_out, C + sx * (r_out - length), C + sy * (r_out - length), r, col)


active = [tick(i, 6, 214, 9, 1.0, GREY) for i in range(60) if i % 5]
active += [tick(i, 30, 214, 24, 3.4, WHITE) for i in range(12) if i]
write_png("dial_active.png", 450, 450, ticks_pix(active))
aod = [tick(i, 30, 214, 30 if i % 3 == 0 else 20, 5.0 if i % 3 == 0 else 3.4, WHITE if i % 3 == 0 else LIGHT)
       for i in range(12)]
write_png("dial_aod.png", 450, 450, ticks_pix(aod))
