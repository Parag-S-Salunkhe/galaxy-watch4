"""Draw a simple 450x450 preview PNG (black, blue rings) for the face picker. Stdlib only.
Usage: python3 -I make_preview.py <out.png>"""
import math
import struct
import sys
import zlib

W = H = 450
C = 225.0
BG, TRACK, BLUE, CYAN = (0, 0, 0), (22, 36, 58), (46, 168, 255), (124, 212, 255)


def ring(px, py, a0, a1, color, r=209.0, half=6.0):
    """Return color if the pixel is on the ring between angles a0..a1 (0 = 12 o'clock, clockwise)."""
    dx, dy = px - C, py - C
    if abs(math.hypot(dx, dy) - r) > half:
        return None
    ang = math.degrees(math.atan2(dx, -dy)) % 360
    return color if a0 <= ang <= a1 else None


rows = []
for y in range(H):
    row = bytearray([0])
    for x in range(W):
        px = (ring(x, y, 200, 290, BLUE) or ring(x, y, 290, 340, TRACK)
              or ring(x, y, 55, 160, CYAN) or ring(x, y, 20, 55, TRACK) or BG)
        if math.hypot(x - C, y - C) > 225:
            px = BG
        row += bytes(px)
    rows.append(bytes(row))


def chunk(tag, data):
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)


png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)) \
    + chunk(b"IDAT", zlib.compress(b"".join(rows), 9)) + chunk(b"IEND", b"")
with open(sys.argv[1], "wb") as f:
    f.write(png)
