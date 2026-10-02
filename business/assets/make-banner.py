#!/usr/bin/env python3
"""
ออกแบบแบนเนอร์การ์ดหน้างาน Fastwork + mock การ์ดจริง
รัน:  python make-banner.py

สร้างไฟล์ใน banner/:
  A-benefit.png     แบบ A — เน้นผลลัพธ์
  B-split.png       แบบ B — แบ่งครึ่ง มีภาพเทอร์มินัล
  C-tools.png       แบบ C — เน้นชื่อเครื่องมือ
  card-preview.png  mock การ์ดจริง 3 ใบ (ดูว่าแบนเนอร์ + ชื่องานเข้ากันไหม)
  thumb-strip.png   แบนเนอร์ 3 แบบย่อเหลือ 320px (ทดสอบว่าอ่านออกตอนย่อไหม)
"""

import contextlib
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "banner")

BG, CARD, LINE = (15, 17, 21), (23, 26, 33), (48, 54, 66)
ACC, ACC2, FG, DIM = (74, 222, 128), (96, 165, 250), (230, 233, 239), (139, 147, 163)
W, H = 1600, 900

FONT_CANDIDATES = [
    "C:/Windows/Fonts/LeelawUI.ttf",
    "C:/Windows/Fonts/tahoma.ttf",
    "C:/Windows/Fonts/arial.ttf",
]
_fonts = {}


def font(size):
    if size not in _fonts:
        _fonts[size] = _pick_font(size)
    return _fonts[size]


def _pick_font(size):
    for path in FONT_CANDIDATES:
        got = _try_font(path, size)
        if got is not None:
            return got
    return ImageFont.load_default()


def _try_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return None


def new_canvas(size=(W, H)):
    im = Image.new("RGB", size, BG)
    return im, ImageDraw.Draw(im)


def terminal(d, box):
    """วาดภาพเทอร์มินัลจำลอง — เต็มแผง ไม่เหลือที่ว่าง"""
    x0, y0, x1, y1 = box
    d.rounded_rectangle(box, radius=16, fill=(11, 13, 16), outline=LINE, width=2)
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        cx = x0 + 28 + i * 26
        d.ellipse([cx - 7, y0 + 20, cx + 7, y0 + 34], fill=c)

    top = y0 + 64
    step = 27
    span = x1 - x0 - 56
    rows = max(1, (y1 - 34 - top) // step)
    widths = [0.55, 0.32, 0.72, 0.20, 0.44, 0.62, 0.28, 0.50,
              0.38, 0.66, 0.24, 0.48, 0.58, 0.30, 0.42]
    y = top
    for i in range(rows):
        w = widths[i % len(widths)]
        color = ACC if i % 2 == 0 else DIM
        d.rounded_rectangle([x0 + 28, y, x0 + 28 + int(span * w), y + 11],
                            radius=5, fill=color)
        y += step


# ── แบบ A — เน้นผลลัพธ์ ────────────────────────────────────────────────
def design_a():
    im, d = new_canvas()
    d.rounded_rectangle([60, 60, W - 60, H - 60], radius=30, fill=CARD, outline=LINE, width=2)
    d.rectangle([60, 60, 70, H - 60], fill=ACC)
    x = 130
    d.text((x, 150), "AI Agent", font=font(96), fill=FG)
    d.text((x, 262), "ที่เข้าใจงานคุณ", font=font(96), fill=ACC)
    d.text((x, 420), "Claude Code  ·  Cursor  ·  pi  ·  n8n",
           font=font(42), fill=ACC2)
    d.line([x, 520, W - 130, 520], fill=LINE, width=2)
    d.text((x, 565), "ตั้งค่าให้ ไม่ใช่สอน", font=font(46), fill=FG)
    d.text((x, 635), "ระบุชัดว่าได้อะไร กี่ชิ้น กี่วัน",
           font=font(38), fill=DIM)
    d.text((x, 700), "ปรึกษาฟรีก่อน · 15 นาที", font=font(36), fill=DIM)
    return im


# ── แบบ B — แบ่งครึ่ง ──────────────────────────────────────────────────
def design_b():
    im, d = new_canvas()
    d.text((120, 175), "ตั้งค่าให้", font=font(104), fill=FG)
    d.text((120, 300), "ตรงกับงานคุณ", font=font(104), fill=ACC)
    d.text((120, 470), "แล้วใช้ได้เลย", font=font(52), fill=DIM)
    d.line([120, 570, 700, 570], fill=LINE, width=3)
    d.text((120, 615), "Claude Code · Cursor · pi",
           font=font(40), fill=ACC2)
    d.text((120, 680), "ไม่ใช่ทฤษฎี — ตั้งค่าจริง",
           font=font(36), fill=DIM)
    terminal(d, [790, 150, W - 110, H - 150])
    return im


# ── แบบ C — เน้นชื่อเครื่องมือ ──────────────────────────────────────────
def design_c():
    im, d = new_canvas()
    y = 150
    for i, name in enumerate(["Claude Code", "Cursor", "pi"]):
        d.text((110, y), name, font=font(92), fill=ACC if i == 0 else FG)
        y += 132
    d.line([110, y + 5, 660, y + 5], fill=LINE, width=3)
    d.text((110, y + 50), "ตั้งค่าให้ตรงกับงานคุณ", font=font(46), fill=ACC2)
    d.text((110, y + 122), "ไม่ใช่ทฤษฎี · ใช้ได้จริง · วัดผลได้",
           font=font(32), fill=DIM)
    terminal(d, [740, 150, W - 110, H - 150])
    return im


# ── mock การ์ดจริง ─────────────────────────────────────────────────────
def mock_card(banner, title, price, sold):
    cw, ch = 340, 400
    im = Image.new("RGB", (cw, ch), (255, 255, 255))
    d = ImageDraw.Draw(im)
    cover = banner.resize(
        (cw, int(cw * banner.size[1] / banner.size[0])), Image.Resampling.LANCZOS
    )
    im.paste(cover, (0, 0))
    ch_cover = cover.size[1]

    y = ch_cover + 14
    # ชื่องาน — ตัด 2 บรรทัดเหมือนการ์ดจริง
    words, line, lines = title.split(), "", []
    for w_ in words:
        probe = (line + " " + w_).strip()
        if d.textlength(probe, font=font(19)) < cw - 24:
            line = probe
        else:
            lines.append(line)
            line = w_
        if len(lines) == 2:
            break
    if len(lines) < 2:
        lines.append(line)
    for t in lines[:2]:
        d.text((12, y), t, font=font(19), fill=(20, 24, 30))
        y += 26

    d.text((12, y + 10), price, font=font(24), fill=(20, 24, 30))
    d.text((12, y + 48), sold, font=font(16), fill=(120, 128, 140))
    return im


# ── ภาพปกพร้อมใช้ — ปรับผังตามสัดส่วน ───────────────────────────
def cover_final(w, h):
    im, d = new_canvas((w, h))
    pad = int(min(w, h) * 0.075)
    s = max(0.8, min(1.15, min(w, h) / 900))
    wide = (w / h) >= 1.35

    if wide:
        tx, ty = pad, int(h * 0.20)
        f_tool = font(int(92 * s))
        y = ty
        for i, name in enumerate(["Claude Code", "Cursor", "pi"]):
            d.text((tx, y), name, font=f_tool, fill=ACC if i == 0 else FG)
            y += int(f_tool.size * 1.42)
        d.line([tx, y + int(6 * s), tx + int(550 * s), y + int(6 * s)],
               fill=LINE, width=max(2, int(3 * s)))
        d.text((tx, y + int(48 * s)), "ตั้งค่าให้ตรงกับงานคุณ",
               font=font(int(46 * s)), fill=ACC2)
        d.text((tx, y + int(118 * s)), "ไม่ใช่ทฤษฎี · ใช้ได้จริง · วัดผลได้",
               font=font(int(32 * s)), fill=DIM)
        terminal(d, [int(w * 0.50), int(h * 0.18), w - pad, h - int(h * 0.18)])
    else:
        tx = pad
        d.text((tx, pad), "Claude Code  ·  Cursor  ·  pi",
               font=font(int(40 * s)), fill=ACC)
        d.text((tx, pad + int(72 * s)), "ตั้งค่าให้", font=font(int(78 * s)), fill=FG)
        d.text((tx, pad + int(174 * s)), "ตรงกับงานคุณ",
               font=font(int(78 * s)), fill=ACC2)
        d.text((tx, pad + int(282 * s)), "ไม่ใช่ทฤษฎี · ใช้ได้จริง · วัดผลได้",
               font=font(int(30 * s)), fill=DIM)
        terminal(d, [tx, pad + int(388 * s), w - pad, h - pad])
    return im


# ── ภาพ "ตัวอย่างสิ่งที่คุณจะได้รับ" — ใช้เป็นพอร์ตชั่วคราวได้ ────
def sample_deliverable():
    im, d = new_canvas()
    d.text((70, 50), "ตัวอย่างสิ่งที่คุณจะได้รับ", font=font(46), fill=FG)
    d.text((70, 112), "(ภาพตัวอย่าง — ไม่ใช่งานลูกค้า)", font=font(26), fill=DIM)

    doc = [70, 180, 780, 830]
    d.rounded_rectangle(doc, radius=18, fill=(250, 250, 250))
    d.text((110, 215), "SETUP GUIDE", font=font(30), fill=(20, 24, 30))
    d.line([110, 262, 740, 262], fill=(210, 214, 220), width=2)
    for i, w in enumerate([0.92, 0.78, 0.86, 0.62]):
        d.rounded_rectangle([110, 292 + i * 26, 110 + int(630 * w), 302 + i * 26],
                            radius=5, fill=(190, 196, 204))
    d.text((110, 430), "How to use", font=font(24), fill=(60, 66, 76))
    for i in range(5):
        y = 472 + i * 34
        d.ellipse([112, y + 8, 126, y + 22], fill=ACC)
        d.rounded_rectangle([142, y + 8, 142 + int(480 * (0.82 - i * 0.09)), y + 20],
                            radius=5, fill=(205, 210, 216))

    d.text((110, 660), "Notes", font=font(24), fill=(60, 66, 76))
    for i, w in enumerate([0.74, 0.62, 0.80]):
        y = 700 + i * 30
        d.rounded_rectangle([110, y, 110 + int(560 * w), y + 11],
                            radius=5, fill=(205, 210, 216))

    d.text((860, 195), "ไฟล์ที่ส่งมอบ", font=font(34), fill=ACC)
    tree = [("skills/", 0), ("  report-builder.md", 1), ("  data-cleanup.md", 1),
            ("prompt-templates/", 0), ("  review-code.md", 1), ("  write-docs.md", 1),
            ("config/", 0), ("  context.md", 1), ("SETUP-GUIDE.md", 0),
            ("walkthrough.mp4", 0)]
    y = 255
    for name, depth in tree:
        color = ACC2 if depth == 0 else FG
        d.text((860 + depth * 34, y), name, font=font(28), fill=color)
        y += 48
    return im


def preview(cards):
    pad = 24
    cw, ch = cards[0].size
    im = Image.new("RGB", (len(cards) * (cw + pad) + pad, ch + pad * 2), (238, 240, 243))
    for i, c in enumerate(cards):
        im.paste(c, (pad + i * (cw + pad), pad))
    return im


def thumb_strip(banners):
    tw = 320
    thumbs = [
        b.resize((tw, int(tw * b.size[1] / b.size[0])), Image.Resampling.LANCZOS)
        for b in banners
    ]
    th = thumbs[0].size[1]
    pad = 20
    im = Image.new("RGB", (len(thumbs) * (tw + pad) + pad, th + pad * 2), (238, 240, 243))
    for i, t in enumerate(thumbs):
        im.paste(t, (pad + i * (tw + pad), pad))
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

    banners = [("A-benefit.png", design_a()),
               ("B-split.png", design_b()),
               ("C-tools.png", design_c())]
    for name, im in banners:
        im.save(os.path.join(OUT, name), optimize=True)
        print(f"  {name}  {im.size[0]}x{im.size[1]}")

    extra = sample_deliverable()
    extra.save(os.path.join(OUT, "sample-deliverable.png"), optimize=True)
    print(f"  sample-deliverable.png  {extra.size[0]}x{extra.size[1]}")

    finals = [("cover-final-16x9.png", 1600, 900),
              ("cover-final-4x3.png", 1200, 900),
              ("cover-final-1x1.png", 1080, 1080)]
    for name, cw, chh in finals:
        cov = cover_final(cw, chh)
        cov.save(os.path.join(OUT, name), optimize=True)
        print(f"  {name}  {cov.size[0]}x{cov.size[1]}")

    title = "รับตั้งค่า AI Coding Agent (Claude Code · Cursor) ให้ตรงกับงานคุณ"
    cards = [mock_card(b, title, "฿1,500", "ยังไม่มีรีวิว · ตอบกลับเร็ว") for _, b in banners]
    pv = preview(cards)
    pv.save(os.path.join(OUT, "card-preview.png"), optimize=True)
    print(f"  card-preview.png  {pv.size[0]}x{pv.size[1]}")

    strip = thumb_strip([b for _, b in banners])
    strip.save(os.path.join(OUT, "thumb-strip.png"), optimize=True)
    print(f"  thumb-strip.png  {strip.size[0]}x{strip.size[1]}")
    print(f"\nทั้งหมดอยู่ใน: {OUT}")


if __name__ == "__main__":
    main()
