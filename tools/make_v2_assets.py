"""Heritage Clean v2 assets (RGBA PNGs, anti-aliased). Stdlib only.
Usage: python3 -I make_v2_assets.py <drawable_dir>
  heart_f00..heart_f09.png  56x56  heartbeat "lub-dub" frames with soft glow (play at 12 fps = ~72 bpm)
  ecg.png                   48x14  small ECG trace (blood red)
  aod_hour.png              30x150 pivot (15,128)  orange gradient bold hour hand
  aod_minute.png            24x232 pivot (12,224)  -> pivotY 0.9655  white bold hand + orange rim dot at r=206
  dial_aod.png              450x450 12 ticks in shades of orange (12/3/6/9 long, bright)"""
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


def supersample(w, h, color_at):
    """color_at(px, py) -> (r,g,b,a 0..1) or None; averaged over SSxSS samples (premultiplied)."""
    def pix(x, y):
        r = g = b = a = 0.0
        for i in range(SS):
            for j in range(SS):
                c = color_at(x + (i + 0.5) / SS, y + (j + 0.5) / SS)
                if c:
                    r += c[0] * c[3]; g += c[1] * c[3]; b += c[2] * c[3]; a += c[3]
        n = SS * SS
        if a == 0:
            return (0, 0, 0, 0)
        return (int(r / a), int(g / a), int(b / a), int(255 * a / n))
    return pix


def lerp(c0, c1, t):
    return tuple(c0[i] + (c1[i] - c0[i]) * t for i in range(3))


# ---- heartbeat frames: lub (big), dub (smaller), then rest ----
HEART_TOP, HEART_BOT = (255, 72, 88), (130, 2, 16)
SCALES = [1.00, 1.17, 1.06, 1.12, 1.01, 0.99, 1.00, 1.00, 1.00, 1.00]
GLOWS = [0.00, 0.55, 0.25, 0.40, 0.10, 0.00, 0.00, 0.00, 0.00, 0.00]
FW = 56


def heart_inside(u, v):
    x = u * 1.25
    y = -v * 1.22 + 0.12
    return (x * x + y * y - 1) ** 3 - x * x * y ** 3 <= 0


for k, (s, glow) in enumerate(zip(SCALES, GLOWS)):
    base = 0.36 * FW * s  # heart half-size in px

    def color_at(px, py, base=base, glow=glow):
        u, v = (px - FW / 2) / base, (py - FW / 2) / base
        if heart_inside(u, v):
            t = min(1.0, max(0.0, (v + 1.0) / 2.1))
            c = lerp(HEART_TOP, HEART_BOT, t)
            hl = max(0.0, 1 - math.hypot(u + 0.42, v + 0.45) / 0.38) * 0.5  # glossy highlight
            c = lerp(c, (255, 255, 255), hl)
            return (*c, 1.0)
        if glow > 0:
            d = math.hypot(px - FW / 2, py - FW / 2 + 1) / (FW / 2)
            ga = max(0.0, 1 - d) ** 2 * glow * 0.8
            if ga > 0.01:
                return (220, 20, 40, ga)
        return None

    write_png("heart_f%02d.png" % k, FW, FW, supersample(FW, FW, color_at))

# ---- small ECG trace ----
ECG = [(0, 8), (12, 8), (15, 6), (18, 8), (21, 8), (23, 11), (26, 1), (29, 13), (31, 8), (36, 8), (39, 6), (42, 8), (48, 8)]


def ecg_at(px, py):
    for (x0, y0), (x1, y1) in zip(ECG, ECG[1:]):
        if capsule(px, py, x0, y0, x1, y1, 1.1, 1.1):
            return (232, 32, 52, 1.0)
    return None


write_png("ecg.png", 48, 14, supersample(48, 14, ecg_at))

# ---- AOD hands: orange hour, white minute with orange rim dot ----
ORANGE_HI, ORANGE_LO, ORANGE_DOT = (255, 176, 112), (232, 120, 48), (255, 140, 60)


def hour_at(px, py):
    if capsule(px, py, 15, 140, 15, 12, 11.0, 8.5):
        return (*lerp(ORANGE_HI, ORANGE_LO, min(1.0, py / 140)), 1.0)
    return None


write_png("aod_hour.png", 30, 150, supersample(30, 150, hour_at))


def minute_at(px, py):
    if capsule(px, py, 12, 236 - 12, 12, 224 - 178, 8.5, 6.0):
        return (250, 250, 250, 1.0)
    if math.hypot(px - 12, py - (224 - 206)) <= 6.5:
        return (*ORANGE_DOT, 1.0)
    return None


write_png("aod_minute.png", 24, 232, supersample(24, 232, minute_at))

# ---- AOD dial: shades of orange ----
C = 225.0
MAJOR, MINOR = (255, 150, 70), (196, 104, 40)
ticks = []
for i in range(12):
    a = math.radians(i * 30)
    major = i % 3 == 0
    length, rad = (30.0, 5.0) if major else (20.0, 3.4)
    sx, sy = math.sin(a), -math.cos(a)
    ticks.append((C + sx * 214, C + sy * 214, C + sx * (214 - length), C + sy * (214 - length), rad, MAJOR if major else MINOR))


def dial_at(px, py):
    if math.hypot(px - C, py - C) < 175:
        return None
    for x0, y0, x1, y1, r, col in ticks:
        if capsule(px, py, x0, y0, x1, y1, r, r):
            return (*col, 1.0)
    return None


write_png("dial_aod.png", 450, 450, supersample(450, 450, dial_at))
