#!/usr/bin/env python3
"""
สร้างภาพปก / ภาพโพสต์ สำหรับหน้างาน Fastwork
รัน:  python make-cover.py                 → ใช้ข้อความตัวอย่าง
      python make-cover.py --out x.png     → ระบุชื่อไฟล์

แก้ข้อความที่บล็อก CONTENT ด้านล่างได้เลย
ไม่มี dependency เพิ่ม — ใช้ Pillow ที่มีอยู่แล้ว
"""

import argparse
import contextlib
import sys

from PIL import Image, ImageDraw, ImageFont

# ── CONTENT: แก้ตรงนี้ ────────────────────────────────────────────────
CONTENT = {
    "line1": "ตั้งค่า AI Coding Agent",
    "line2": "ให้ตรงกับงานของคุณ",
    "tools": "Claude Code  ·  Cursor  ·  pi  ·  n8n",
    "bullets": [
        "ไม่ใช่ทฤษฎี — ตั้งค่าให้ใช้ได้เลย",
        "ระบุชัดว่าได้อะไร กี่ชิ้น กี่วัน",
        "ใช้ได้จริงในงานคุณ ไม่ใช่ demo",
    ],
    "footer": "ปรึกษาฟรีก่อน · 15 นาที",
}
SIZE = (1600, 900)          # 16:9 — ใช้เป็นภาพปกได้
BG, CARD, LINE = (15, 17, 21), (23, 26, 33), (48, 54, 66)
ACC, FG, DIM = (74, 222, 128), (230, 233, 239), (139, 147, 163)

FONT_CANDIDATES = [
    "C:/Windows/Fonts/LeelawUI.ttf",   # มี Thai
    "C:/Windows/Fonts/tahoma.ttf",     # มี Thai
    "C:/Windows/Fonts/arial.ttf",
]
# ──────────────────────────────────────────────────────────────────────


def _try_font(path, size):
    """โหลดฟอนต์ คืน None ถ้าเครื่องนี้ไม่มีไฟล์นั้น"""
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return None


def load_font(size):
    """หาฟอนต์แรกที่ใช้ได้ — มี fallback เป็นฟอนต์พื้นฐานของ Pillow"""
    for path in FONT_CANDIDATES:
        f = _try_font(path, size)
        if f is not None:
            return f
    return ImageFont.load_default()


def build(content=CONTENT, size=SIZE):
    w, h = size
    im = Image.new("RGB", size, BG)
    d = ImageDraw.Draw(im)
    m = int(w * 0.05)          # margin

    d.rounded_rectangle([m, m, w - m, h - m], radius=28, fill=CARD, outline=LINE, width=2)
    d.rectangle([m, m, m + 8, h - m], fill=ACC)      # แถบสีซ้าย

    x = m + 70
    f_h1 = load_font(int(h * 0.093))
    f_sub = load_font(int(h * 0.042))
    f_bul = load_font(int(h * 0.040))
    f_ftr = load_font(int(h * 0.038))

    d.text((x, int(h * 0.167)), content["line1"], font=f_h1, fill=FG)
    d.text((x, int(h * 0.291)), content["line2"], font=f_h1, fill=FG)
    d.text((x, int(h * 0.436)), content["tools"], font=f_sub, fill=ACC)

    y0 = int(h * 0.556)
    for i, t in enumerate(content["bullets"]):
        y = y0 + i * int(h * 0.069)
        d.ellipse([x + 2, y + 16, x + 18, y + 32], fill=ACC)
        d.text((x + 40, y), t, font=f_bul, fill=FG)

    d.line([x, int(h * 0.824), w - x, int(h * 0.824)], fill=LINE, width=2)
    d.text((x, int(h * 0.858)), content["footer"], font=f_ftr, fill=DIM)
    return im


if __name__ == "__main__":
    # คอนโซล Windows บางตัวเป็น cp1252 → กันพังตอน print ภาษาไทย
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if reconfigure:
        with contextlib.suppress(ValueError, OSError):
            reconfigure(encoding="utf-8", errors="replace")

    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="sample-cover.png")
    a = ap.parse_args()
    im = build()
    im.save(a.out, optimize=True)
    print(f"บันทึกแล้ว: {a.out}  ขนาด {im.size[0]}x{im.size[1]}")
