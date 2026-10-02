#!/usr/bin/env python3
"""
ชุดทดสอบความสามารถด้านกราฟฟิก
รัน:  python graphics-test.py

สร้างไฟล์ในโฟลเดอร์ test/:
  cover-dark.png          ภาพปก ธีมมืด
  cover-light.png         ภาพปก ธีมสว่าง
  cover-minimal.png       ภาพปก แบบมินิมอล
  diagram-before-after.png แผนภาพ ก่อน → หลัง
  chart-token-cost.png    กราฟเปรียบเทียบ (ข้อมูลตัวอย่าง)
  packages-compare.png    ภาพเปรียบเทียบแพ็กเกจ 4 ขั้น
  icons-row.png           ชุดไอคอน
  social-square.png       ภาพโพสต์โซเชียล 1080x1080
"""

import contextlib
import os
import sys

from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test")

FONT_CANDIDATES = [
    "C:/Windows/Fonts/LeelawUI.ttf",
    "C:/Windows/Fonts/tahoma.ttf",
    "C:/Windows/Fonts/arial.ttf",
]

DARK = {
    "bg": (15, 17, 21), "card": (23, 26, 33), "line": (48, 54, 66),
    "acc": (74, 222, 128), "fg": (230, 233, 239), "dim": (139, 147, 163),
}
LIGHT = {
    "bg": (247, 248, 250), "card": (255, 255, 255), "line": (222, 226, 232),
    "acc": (37, 99, 235), "fg": (17, 24, 39), "dim": (107, 114, 128),
}

_font_cache = {}


def font(size):
    if size in _font_cache:
        return _font_cache[size]
    chosen = ImageFont.load_default()
    for path in FONT_CANDIDATES:
        loaded = _try_font(path, size)
        if loaded is not None:
            chosen = loaded
            break
    _font_cache[size] = chosen
    return chosen


def _try_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return None


def canvas(size, theme):
    im = Image.new("RGB", size, theme["bg"])
    return im, ImageDraw.Draw(im)


def panel(d, box, theme, radius=28, width=2):
    d.rounded_rectangle(box, radius=radius, fill=theme["card"],
                        outline=theme["line"], width=width)


def accent_bar(d, box, theme, thickness=8):
    x0, y0, _, y1 = box
    d.rectangle([x0, y0, x0 + thickness, y1], fill=theme["acc"])


# ── 1. ภาพปก 3 สไตล์ ─────────────────────────────────────────────────
def cover(theme, style):
    im, d = canvas((1600, 900), theme)
    m = 80
    panel(d, [m, m, 1600 - m, 900 - m], theme)
    accent_bar(d, [m, m, 0, 900 - m], theme)
    x = m + 70

    title = ["ตั้งค่า AI Coding Agent", "ให้ตรงกับงานของคุณ"]
    if style == "minimal":
        d.rectangle([x, 150, x + 120, 156], fill=theme["acc"])
        for i, line in enumerate(title):
            d.text((x, 210 + i * 110), line, font=font(88), fill=theme["fg"])
    else:
        for i, line in enumerate(title):
            d.text((x, 150 + i * 112), line, font=font(84), fill=theme["fg"])

    d.text((x, 400), "Claude Code  ·  Cursor  ·  pi  ·  n8n",
           font=font(38), fill=theme["acc"])

    if style != "minimal":
        for i, t in enumerate(["ไม่ใช่ทฤษฎี — ตั้งค่าให้ใช้ได้เลย",
                               "ระบุชัดว่าได้อะไร กี่ชิ้น กี่วัน",
                               "ใช้ได้จริงในงานคุณ ไม่ใช่ demo"]):
            y = 505 + i * 62
            d.ellipse([x + 2, y + 16, x + 18, y + 32], fill=theme["acc"])
            d.text((x + 40, y), t, font=font(36), fill=theme["fg"])

    d.line([x, 742, 1600 - x, 742], fill=theme["line"], width=2)
    d.text((x, 772), "ปรึกษาฟรีก่อน · 15 นาที", font=font(34), fill=theme["dim"])
    return im


# ── 2. แผนภาพ ก่อน → หลัง ─────────────────────────────────────────────
def before_after(theme):
    W, H = 1600, 900
    im, d = canvas((W, H), theme)
    d.text((80, 60), "ก่อน", font=font(52), fill=theme["dim"])
    d.polygon([(196, 76), (226, 92), (196, 108)], fill=theme["acc"])
    d.text((250, 60), "หลัง", font=font(52), fill=theme["acc"])

    cols = [
        (80, "ก่อน", theme["dim"], [
            "ต้องอธิบายงานซ้ำทุกครั้ง",
            "Agent ไม่รู้จักโปรเจกต์เรา",
            "ใช้ความสามารถไม่ถึง 10%",
            "Token เปลืองโดยไม่รู้ตัว",
        ]),
        (840, "หลัง", theme["acc"], [
            "สั่งสั้นๆ ก็เข้าใจ",
            "Agent รู้จักงานเราตั้งแต่วินาทีแรก",
            "ได้เต็มตามที่เครื่องมือทำได้",
            "ลด token — วัดเป็นตัวเลขได้",
        ]),
    ]
    for x0, title, color, items in cols:
        panel(d, [x0, 150, x0 + 680, 800], theme)
        d.text((x0 + 50, 195), title, font=font(46), fill=color)
        d.line([x0 + 50, 275, x0 + 630, 275], fill=theme["line"], width=2)
        for i, t in enumerate(items):
            y = 315 + i * 105
            d.ellipse([x0 + 52, y + 14, x0 + 74, y + 36], fill=color)
            d.text((x0 + 100, y), t, font=font(33), fill=theme["fg"])

    cx, cy = 800, 475
    d.polygon([(cx - 30, cy - 26), (cx + 34, cy), (cx - 30, cy + 26)], fill=theme["acc"])
    return im


# ── 3. กราฟ (ข้อมูลตัวอย่าง) ───────────────────────────────────────────
def chart(theme):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager

    for cand in FONT_CANDIDATES:
        if os.path.exists(cand):
            with contextlib.suppress(Exception):
                font_manager.fontManager.addfont(cand)
            break
    plt.rcParams["font.family"] = ["Leelawadee UI", "Tahoma", "DejaVu Sans"]

    fig, ax = plt.subplots(figsize=(12, 7.5), dpi=100)
    fig.patch.set_facecolor("#0f1115")
    ax.set_facecolor("#171a21")

    labels = ["ไม่ตั้งค่า", "ตั้งค่าแล้ว"]
    values = [100, 38]
    bars = ax.bar(labels, values, color=["#6b7280", "#4ade80"], width=0.5)
    for bar, v in zip(bars, values, strict=True):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 2,
                f"{v}", ha="center", color="#e6e9ef", fontsize=22, fontweight="bold")

    ax.set_ylabel("ค่า token ต่อ 1 งาน (ดัชนี)", color="#8b93a3", fontsize=15)
    ax.set_title("ตัวอย่าง: ค่า token ก่อน/หลังตั้งค่า\n(ข้อมูลตัวอย่าง — ยังไม่ใช่ผลจริง)",
                 color="#e6e9ef", fontsize=19, pad=20)
    ax.tick_params(colors="#8b93a3", labelsize=16)
    for s in ax.spines.values():
        s.set_color("#262b36")
    ax.grid(axis="y", color="#262b36", linestyle=":", linewidth=1)
    ax.set_axisbelow(True)

    path = os.path.join(OUT, "chart-token-cost.png")
    fig.tight_layout()
    fig.savefig(path, facecolor=fig.get_facecolor())
    plt.close(fig)
    return path


# ── 4. เปรียบเทียบแพ็กเกจ ─────────────────────────────────────────────
def packages(theme):
    W, H = 1600, 900
    im, d = canvas((W, H), theme)
    d.text((80, 55), "แพ็กเกจ 4 ขั้น", font=font(50), fill=theme["fg"])

    tiers = [
        ("ขั้น 1", "QUICK SETUP", "฿1,500", "3 วัน", ["template 3 อัน", "ตั้ง context+model", "1 workflow"], False),
        ("ขั้น 2", "CUSTOM", "฿4,500", "7 วัน", ["skill 2-3 อัน", "template 6-8 อัน", "วิดีโอ 10 นาที"], True),
        ("ขั้น 3", "PRO", "฿9,900", "14 วัน", ["skill 4-6 อัน", "MCP server 1 อัน", "ดูแล 1 เดือน"], False),
        ("ขั้น 4", "FULL / TEAM", "฿24,900", "30 วัน", ["ครบทุก workflow", "แพ็กให้ทีม", "ดูแล 3 เดือน"], False),
    ]
    x0, w, gap = 70, 340, 30
    for i, (step, name, price, days, items, hit) in enumerate(tiers):
        x = x0 + i * (w + gap)
        box = [x, 150, x + w, 800]
        panel(d, box, theme, radius=22, width=3 if hit else 2)
        if hit:
            d.rounded_rectangle([x, 150, x + w, 158], radius=0, fill=theme["acc"])
        d.text((x + 28, 185), step, font=font(26), fill=theme["dim"])
        d.text((x + 28, 222), name, font=font(30), fill=theme["acc"] if hit else theme["fg"])
        d.text((x + 28, 285), price, font=font(46), fill=theme["fg"])
        d.text((x + 28, 350), days, font=font(26), fill=theme["dim"])
        d.line([x + 28, 400, x + w - 28, 400], fill=theme["line"], width=2)
        for j, t in enumerate(items):
            d.text((x + 28, 430 + j * 42), "·  " + t, font=font(24), fill=theme["fg"])
    return im


# ── 5. ชุดไอคอน ───────────────────────────────────────────────────────
def icons(theme):
    W, H = 1600, 420
    im, d = canvas((W, H), theme)
    labels = ["Extension", "Skill", "Template", "Context", "Model", "Package"]
    n = len(labels)
    cw = W // n
    for i, label in enumerate(labels):
        cx = cw * i + cw // 2
        cy = 175
        d.rounded_rectangle([cx - 55, cy - 55, cx + 55, cy + 55], radius=18,
                            outline=theme["line"], width=2)
        a = theme["acc"]
        if i == 0:
            d.rectangle([cx - 26, cy - 26, cx + 26, cy + 26], outline=a, width=4)
            d.rectangle([cx - 10, cy - 10, cx + 10, cy + 10], fill=a)
        elif i == 1:
            d.polygon([(cx, cy - 30), (cx + 30, cy), (cx, cy + 30), (cx - 30, cy)], outline=a, width=4)
        elif i == 2:
            d.line([cx - 28, cy, cx + 28, cy], fill=a, width=5)
            d.line([cx, cy - 28, cx, cy + 28], fill=a, width=5)
        elif i == 3:
            for k in range(3):
                d.line([cx - 28, cy - 18 + k * 18, cx + 28, cy - 18 + k * 18], fill=a, width=5)
        elif i == 4:
            d.ellipse([cx - 28, cy - 28, cx + 28, cy + 28], outline=a, width=4)
            d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=a)
        else:
            d.polygon([(cx - 30, cy - 6), (cx, cy - 30), (cx + 30, cy - 6)], outline=a, width=4)
            d.rectangle([cx - 30, cy - 6, cx + 30, cy + 30], outline=a, width=4)
        d.text((cx - 52, cy + 85), label, font=font(26), fill=theme["fg"])
    return im


# ── 6. ภาพโพสต์โซเชียล 1080 ───────────────────────────────────────────
def social(theme):
    S = 1080
    im, d = canvas((S, S), theme)
    m = 60
    panel(d, [m, m, S - m, S - m], theme)
    d.rectangle([m, m, m + 10, S - m], fill=theme["acc"])
    x = m + 70
    d.text((x, 170), "คุณใช้ AI agent", font=font(62), fill=theme["fg"])
    d.text((x, 250), "เต็มความสามารถ", font=font(62), fill=theme["fg"])
    d.text((x, 330), "แค่ไหน?", font=font(62), fill=theme["acc"])
    for i, t in enumerate(["ตั้งค่าให้ตรงกับงานคุณ",
                           "ลด token — วัดได้",
                           "ใช้ได้จริง ไม่ใช่ demo"]):
        y = 480 + i * 72
        d.ellipse([x, y + 16, x + 18, y + 34], fill=theme["acc"])
        d.text((x + 42, y), t, font=font(38), fill=theme["fg"])
    d.line([x, 810, S - x, 810], fill=theme["line"], width=2)
    d.text((x, 845), "ปรึกษาฟรี · 15 นาที", font=font(36), fill=theme["dim"])
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

    jobs = [
        ("cover-dark.png", lambda: cover(DARK, "full")),
        ("cover-light.png", lambda: cover(LIGHT, "full")),
        ("cover-minimal.png", lambda: cover(DARK, "minimal")),
        ("diagram-before-after.png", lambda: before_after(DARK)),
        ("packages-compare.png", lambda: packages(DARK)),
        ("icons-row.png", lambda: icons(DARK)),
        ("social-square.png", lambda: social(DARK)),
    ]
    for name, fn in jobs:
        im = fn()
        im.save(os.path.join(OUT, name), optimize=True)
        print(f"  {name}  {im.size[0]}x{im.size[1]}")
    path = chart(DARK)
    print(f"  {os.path.basename(path)}  (matplotlib)")
    print(f"\nทั้งหมดอยู่ใน: {OUT}")


if __name__ == "__main__":
    main()
