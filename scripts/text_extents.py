"""Left/right extent of bright pixels in horizontal bands of a screenshot. Stdlib only (reuses region_diff.decode).
Usage: python3 -I text_extents.py shot.png x0 x1 y0:y1 [y0:y1 ...]  -> per band: first/last lit x and its centre."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from region_diff import decode  # noqa: E402

path, x0, x1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
rows, bpp = decode(path)
for band in sys.argv[4:]:
    y0, y1 = map(int, band.split(":"))
    xs = [x for y in range(y0, y1) for x in range(x0, x1)
          if max(rows[y][x * bpp:x * bpp + 3]) > 120]
    if xs:
        print(f"y {y0}-{y1}: x {min(xs)}..{max(xs)}  centre {(min(xs) + max(xs)) / 2:.1f}")
    else:
        print(f"y {y0}-{y1}: nothing lit")
