#!/usr/bin/env python3
"""Generate dependency-free macOS icon resources for Kit Companion."""

from __future__ import annotations

import struct
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path


ICON_SIZES = {
    "icon_16x16.png": 16,
    "icon_16x16@2x.png": 32,
    "icon_32x32.png": 32,
    "icon_32x32@2x.png": 64,
    "icon_128x128.png": 128,
    "icon_128x128@2x.png": 256,
    "icon_256x256.png": 256,
    "icon_256x256@2x.png": 512,
    "icon_512x512.png": 512,
    "icon_512x512@2x.png": 1024,
}


def chunk(kind: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + kind
        + data
        + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    )


def write_png(path: Path, width: int, height: int, pixels: list[tuple[int, int, int, int]]) -> None:
    rows = []
    for y in range(height):
        start = y * width
        row = pixels[start : start + width]
        rows.append(b"\x00" + bytes(component for pixel in row for component in pixel))
    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    data = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", header)
        + chunk(b"IDAT", zlib.compress(b"".join(rows), 9))
        + chunk(b"IEND", b"")
    )
    path.write_bytes(data)


def rounded_rect(x: float, y: float, left: float, top: float, right: float, bottom: float, radius: float) -> bool:
    if x < left or x > right or y < top or y > bottom:
        return False
    cx = min(max(x, left + radius), right - radius)
    cy = min(max(y, top + radius), bottom - radius)
    return (x - cx) ** 2 + (y - cy) ** 2 <= radius**2


def line_distance(px: float, py: float, ax: float, ay: float, bx: float, by: float) -> float:
    dx = bx - ax
    dy = by - ay
    if dx == 0 and dy == 0:
        return ((px - ax) ** 2 + (py - ay) ** 2) ** 0.5
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    nx = ax + t * dx
    ny = ay + t * dy
    return ((px - nx) ** 2 + (py - ny) ** 2) ** 0.5


def kit_mark(x: float, y: float, stroke: float) -> bool:
    return (
        line_distance(x, y, 0.34, 0.25, 0.34, 0.76) <= stroke
        or line_distance(x, y, 0.34, 0.51, 0.66, 0.25) <= stroke
        or line_distance(x, y, 0.44, 0.49, 0.69, 0.76) <= stroke
    )


def icon_color(x: float, y: float) -> tuple[int, int, int, int]:
    if not rounded_rect(x, y, 0.07, 0.07, 0.93, 0.93, 0.20):
        return (0, 0, 0, 0)

    # Quiet graphite base with a green status accent and a crisp "k" mark.
    color = (26, 32, 44, 255)
    if rounded_rect(x, y, 0.12, 0.12, 0.88, 0.88, 0.16):
        color = (36, 48, 63, 255)
    if rounded_rect(x, y, 0.16, 0.16, 0.84, 0.84, 0.12):
        color = (45, 64, 79, 255)
    if 0.18 <= x <= 0.82 and 0.69 <= y <= 0.77:
        color = (34, 197, 94, 255)
    if rounded_rect(x, y, 0.56, 0.18, 0.76, 0.38, 0.055):
        color = (134, 239, 172, 255)
    if kit_mark(x, y, 0.035):
        color = (248, 250, 252, 255)
    if kit_mark(x, y, 0.018):
        color = (255, 255, 255, 255)
    return color


def render(size: int) -> list[tuple[int, int, int, int]]:
    samples = 4 if size <= 128 else 2
    pixels: list[tuple[int, int, int, int]] = []
    sample_count = samples * samples
    for y in range(size):
        for x in range(size):
            totals = [0, 0, 0, 0]
            for sy in range(samples):
                for sx in range(samples):
                    nx = (x + (sx + 0.5) / samples) / size
                    ny = (y + (sy + 0.5) / samples) / size
                    rgba = icon_color(nx, ny)
                    for index, component in enumerate(rgba):
                        totals[index] += component
            pixels.append(tuple(round(component / sample_count) for component in totals))
    return pixels


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: generate_macos_icons.py <resources-dir>", file=sys.stderr)
        return 2

    resources_dir = Path(sys.argv[1])
    resources_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="kit-iconset.") as tmp:
        iconset = Path(tmp) / "AppIcon.iconset"
        iconset.mkdir()
        for filename, size in ICON_SIZES.items():
            write_png(iconset / filename, size, size, render(size))
        subprocess.run(
            ["/usr/bin/iconutil", "-c", "icns", str(iconset), "-o", str(resources_dir / "AppIcon.icns")],
            check=True,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
