#!/usr/bin/env python3
"""
prep_photo.py — Prepare a source photo for ASCII art conversion.

Usage:
    python scripts/prep_photo.py <source-photo.jpg>

Output:
    source-prepped.png  — high-contrast grayscale image on white background.

Steps:
  1. Remove background (rembg)
  2. Boost local contrast (CLAHE via OpenCV)
  3. Composite onto pure white
"""

import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove


def prep_photo(input_path: str) -> None:
    src = Path(input_path)
    if not src.exists():
        print(f"Error: {src} not found", file=sys.stderr)
        sys.exit(1)

    # 1. Remove background
    print("Removing background…")
    with open(src, "rb") as f:
        raw = f.read()
    no_bg_bytes = remove(raw)
    no_bg = Image.open(__import__("io").BytesIO(no_bg_bytes)).convert("RGBA")

    # 2. Composite onto white
    white = Image.new("RGBA", no_bg.size, (255, 255, 255, 255))
    white.paste(no_bg, mask=no_bg.split()[3])
    gray_pil = white.convert("L")

    # 3. Boost local contrast with CLAHE
    gray_np = np.array(gray_pil)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray_np)

    out_path = src.parent / "source-prepped.png"
    Image.fromarray(enhanced).save(out_path)
    print(f"Saved → {out_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/prep_photo.py <source-photo.jpg>")
        sys.exit(1)
    prep_photo(sys.argv[1])
