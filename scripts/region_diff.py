"""Compare one rectangle across several screenshots (8-bit RGB/RGBA PNG, as adb screencap writes). Stdlib only.
Usage: python3 -I region_diff.py x y w h a.png b.png [...]  -> prints a hash of the region per file."""
import hashlib
import struct
import sys
import zlib


def decode(path):
    data = open(path, "rb").read()
    pos, idat, w = 8, b"", 0
    while pos < len(data):
        n, tag = struct.unpack(">I4s", data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + n]
        if tag == b"IHDR":
            w, h, depth, ctype = struct.unpack(">IIBB", body[:10])
            bpp = {2: 3, 6: 4}[ctype]
        elif tag == b"IDAT":
            idat += body
        pos += 12 + n
    raw, stride, rows, prev = zlib.decompress(idat), w * bpp, [], bytearray(w * bpp)
    for y in range(h):
        f, line = raw[y * (stride + 1)], bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        for i in range(stride):
            a = line[i - bpp] if i >= bpp else 0
            b, c = prev[i], prev[i - bpp] if i >= bpp else 0
            if f == 1: line[i] = (line[i] + a) & 255
            elif f == 2: line[i] = (line[i] + b) & 255
            elif f == 3: line[i] = (line[i] + (a + b) // 2) & 255
            elif f == 4:
                p = a + b - c; pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[i] = (line[i] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        rows.append(bytes(line)); prev = line
    return rows, bpp


if __name__ == "__main__":
    x, y, w, h = map(int, sys.argv[1:5])
    for p in sys.argv[5:]:
        rows, bpp = decode(p)
        region = b"".join(r[x * bpp:(x + w) * bpp] for r in rows[y:y + h])
        lit = sum(1 for i in range(0, len(region), bpp) if region[i] > 150)
        print(p.rsplit("/", 1)[-1], hashlib.md5(region).hexdigest()[:10], "red-ish pixels:", lit)
