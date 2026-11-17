"""Draw an anti-aliased blood-red gradient heart (RGBA PNG). Stdlib only.
Usage: python3 -I make_heart.py <out.png> [size]"""
import math
import struct
import sys
import zlib

OUT = sys.argv[1]
S = int(sys.argv[2]) if len(sys.argv) > 2 else 96
SS = 4  # supersampling per axis
TOP, BOTTOM = (255, 70, 85), (138, 3, 18)  # bright crimson -> blood red


def inside(u, v):
    # classic heart curve: (x^2 + y^2 - 1)^3 - x^2 y^3 <= 0, x in [-1.25,1.25], y in [-1.1,1.35]
    x = (u - 0.5) * 2.5
    y = (0.5 - v) * 2.45 + 0.12
    return (x * x + y * y - 1) ** 3 - x * x * y ** 3 <= 0


rows = []
for py in range(S):
    row = bytearray([0])
    for px in range(S):
        hits = 0
        for sy in range(SS):
            for sx in range(SS):
                if inside((px + (sx + 0.5) / SS) / S, (py + (sy + 0.5) / SS) / S):
                    hits += 1
        a = hits / (SS * SS)
        t = py / (S - 1)
        r, g, b = (int(TOP[i] + (BOTTOM[i] - TOP[i]) * t) for i in range(3))
        # soft highlight on the upper-left lobe
        d = math.hypot(px / S - 0.32, py / S - 0.30)
        h = max(0.0, 1 - d / 0.16) * 0.55
        r, g, b = (int(c + (255 - c) * h) for c in (r, g, b))
        row += bytes((r, g, b, int(a * 255)))
    rows.append(bytes(row))


def chunk(tag, data):
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)


png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", S, S, 8, 6, 0, 0, 0)) \
    + chunk(b"IDAT", zlib.compress(b"".join(rows), 9)) + chunk(b"IEND", b"")
with open(OUT, "wb") as f:
    f.write(png)
