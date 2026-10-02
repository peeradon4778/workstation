#!/usr/bin/env python3
"""
แบนเนอร์การ์ดแบบมีโลโก้เครื่องมือจริง + ฟอนต์ไทยระดับมืออาชีพ
รัน:  python make-banner-v2.py

ต้องมี (ดาวน์โหลดไว้แล้วในโฟลเดอร์เดียวกัน):
  fonts/IBMPlexSansThai-Bold.ttf · fonts/IBMPlexSansThai-Regular.ttf
  logos/claude-4ade80.png · logos/cursor-ffffff.png · logos/n8n-ffffff.png

ลิขสิทธิ์ของ asset ที่ดาวน์โหลดมา:
  ฟอนต์ — Google Fonts (SIL Open Font License 1.1) เผยแพร่ซ้ำได้
  โลโก้ — simple-icons (CC0 1.0) — เครื่องหมายการค้ายังเป็นของเจ้าของแต่ละแบรนด์
         ใช้ในความหมาย "เครื่องมือที่รองรับ" ไม่ได้หมายความว่าได้รับการรับรองจากแบรนด์นั้น

ผลลัพธ์ใน banner-v2/:
  cover-logos-16x9.png   1600x900
  cover-logos-1x1.png    1080x1080
  cover-logos-4x3.png    1200x900
"""

import contextlib
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "banner-v2")
FONTS = os.path.join(HERE, "fonts")
LOGOS = os.path.join(HERE, "logos")

ACC = (74, 222, 128)
ACC2 = (125, 211, 252)
FG = (240, 243, 248)
DIM = (148, 158, 174)
LINE = (52, 60, 74)
TOP = (22, 28, 40)
BOTTOM = (9, 11, 15)

TOOLS = [
    ("claude-4ade80.png", "Claude Code"),
    ("cursor-ffffff.png", "Cursor"),
    ("n8n-ffffff.png", "n8n"),
    (None, "pi"),
]

_cache = {}


def font(name, size):
    key = (name, size)
    if key not in _cache:
        path = os.path.join(FONTS, name)
        try:
            _cache[key] = ImageFont.truetype(path, size)
        except OSError:
            _cache[key] = ImageFont.load_default()
    return _cache[key]


def gradient(size, top, bottom):
    w, h = size
    im = Image.new("RGB", size)
    d = ImageDraw.Draw(im)
    for y in range(h):
        t = y / max(1, h - 1)
        d.line([(0, y), (w, y)],
               fill=tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    return im


def add_glow(im, center, radius, color, strength=70):
    layer = Image.new("RGB", im.size, color)
    mask = Image.new("L", im.size, 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([center[0] - radius, center[1] - radius,
                center[0] + radius, center[1] + radius], fill=strength)
    mask = mask.filter(ImageFilter.GaussianBlur(radius * 0.55))
    im.paste(layer, (0, 0), mask)


def load_logo(name, box, tint=(255, 255, 255)):
    """โหลดโลโก้แล้วทำพื้นดำให้โปร่งใส — normalize ความสว่างให้เต็มช่วง"""
    src = Image.open(os.path.join(LOGOS, name)).convert("RGB")
    alpha = ImageOps.autocontrast(src.convert("L"))
    solid = Image.new("RGBA", src.size, tint + (255,))
    solid.putalpha(alpha)
    solid.thumbnail((box, box), Image.Resampling.LANCZOS)
    return solid


def draw_pi(d, box, color):
    """วาดสัญลักษณ์ π เอง — ฟอนต์ไทยส่วนใหญ่ไม่มี glyph นี้"""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    t = max(3, int(h * 0.09))
    d.rectangle([x0 - int(t * 0.4), y0, x1 + int(t * 0.4), y0 + t], fill=color)
    for frac in (0.24, 0.66):
        lx = x0 + int(w * frac)
        d.rectangle([lx, y0, lx + t, y1], fill=color)


def build(w, h):
    im = gradient((w, h), TOP, BOTTOM)
    add_glow(im, (int(w * 0.78), int(h * 0.16)), int(w * 0.34), (30, 58, 92), 110)
    add_glow(im, (int(w * 0.10), int(h * 0.88)), int(w * 0.30), (22, 62, 44), 90)

    d = ImageDraw.Draw(im)
    pad = int(min(w, h) * 0.075)
    wide = (w / h) >= 1.35

    f_h = font("IBMPlexSansThai-Bold.ttf", int(min(w, h) * (0.098 if wide else 0.088)))
    f_sub = font("IBMPlexSansThai-Regular.ttf", int(min(w, h) * 0.038))
    f_lab = font("IBMPlexSansThai-Bold.ttf", int(min(w, h) * 0.034))

    if wide:
        x = pad
        y = int(h * 0.15)
        d.text((x, y), "ตั้งค่า AI Coding Agent", font=f_h, fill=FG)
        d.text((x, y + int(f_h.size * 1.22)), "ให้ตรงกับงานคุณ", font=f_h, fill=ACC)
        d.text((x, y + int(f_h.size * 2.66)), "ไม่ใช่ทฤษฎี — ตั้งค่าให้ใช้ได้เลย",
               font=f_sub, fill=DIM)
        ly = int(h * 0.72)
    else:
        x = pad
        y = pad
        d.text((x, y), "ตั้งค่า", font=f_h, fill=FG)
        d.text((x, y + int(f_h.size * 1.14)), "AI Coding Agent", font=f_h, fill=ACC)
        d.text((x, y + int(f_h.size * 2.46)), "ให้ตรงกับงานคุณ", font=f_h, fill=FG)
        d.text((x, y + int(f_h.size * 3.92)), "ไม่ใช่ทฤษฎี — ตั้งค่าให้ใช้ได้เลย",
               font=f_sub, fill=DIM)
        ly = int(h * 0.72)

    d.line([pad, ly - int(h * 0.075), w - pad, ly - int(h * 0.075)], fill=LINE, width=2)

    avail = w - 2 * pad
    box, gap, sep = 0, 0, 0
    lab = f_lab
    for s in (1.0, 0.92, 0.85, 0.78, 0.72, 0.66, 0.60, 0.55):
        box = int(min(w, h) * 0.100 * s)
        gap = int(min(w, h) * 0.026 * s)
        sep = int(min(w, h) * 0.075 * s)
        lab = font("IBMPlexSansThai-Bold.ttf", max(14, int(min(w, h) * 0.034 * s)))
        need = sum(box + gap + int(d.textlength(lb, font=lab)) for _, lb in TOOLS)
        need += sep * (len(TOOLS) - 1)
        if need <= avail:
            break

    widths = [box + gap + int(d.textlength(lb, font=lab)) for _, lb in TOOLS]
    cx = (w - sum(widths) - sep * (len(TOOLS) - 1)) // 2

    cy = ly + int(min(w, h) * 0.005)
    for i, (name, label) in enumerate(TOOLS):
        if name is None:
            draw_pi(d, [cx + int(box * 0.16), cy + int(box * 0.14),
                        cx + box - int(box * 0.16), cy + box - int(box * 0.14)], FG)
        else:
            logo = load_logo(name, box)
            im.paste(logo, (cx + (box - logo.size[0]) // 2,
                            cy + (box - logo.size[1]) // 2), logo)
        d.text((cx + box + gap, cy + (box - lab.size) // 2 - int(box * 0.04)),
               label, font=lab, fill=FG)
        cx += widths[i] + sep

    return im


def main():
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if reconfigure:
        with contextlib.suppress(ValueError, OSError):
            reconfigure(encoding="utf-8", errors="replace")

    try:
        os.makedirs(OUT, exist_ok=True)
    except OSError as exc:
        print(f"สร้างโฟลเดอร์ไม่ได้: {exc}")
        return

    jobs = [("cover-logos-16x9.png", 1600, 900),
            ("cover-logos-4x3.png", 1200, 900),
            ("cover-logos-1x1.png", 1080, 1080)]
    for name, w, h in jobs:
        im = build(w, h)
        im.save(os.path.join(OUT, name), optimize=True)
        print(f"  {name}  {w}x{h}")
    print(f"\nทั้งหมดอยู่ใน: {OUT}")


if __name__ == "__main__":
    main()
