#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Affiliate Content Factory — โรงงานผลิตคอนเทนต์ affiliate
=========================================================
รัน:  python app.py        → เปิด http://localhost:8777

ทำไมไม่มี dependency:
    สมมติฐานของเครื่องนี้คือ "มีแค่คอมกับมือถือ"
    → ใช้ Python stdlib ล้วน ไม่ต้อง pip install อะไรเลย
    → ไม่ต้องมี API key (ทำงานออฟไลน์ได้ 100%)
    → ไม่มีค่าใช้จ่ายตอนใช้

สิ่งที่ทำ:
    ใส่สินค้า 1 ตัว → ได้ "content pack" พร้อมโพสต์
    - ลิงก์ affiliate + sub_id (หัวใจของการวัดผล)
    - hook 5 แบบ / สคริปต์ 15-30 วิ / แคปชัน / แฮชแท็ก / shot list
    - คอม/ออเดอร์ และจำนวนออเดอร์ที่ต้องขายถึง 1,500 บาท

ข้อจำกัดที่ตั้งใจ (ห้ามข้าม):
    - ไม่ auto-post  (มนุษย์กดโพสต์เสมอ)
    - ไม่ scrape     (ใช้ Product Feed ที่ดาวน์โหลดมาเอง)
    - ไม่แตะบัญชี Shopee ของใคร
"""

import contextlib
import json
import math
import sys
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime

PORT = 8777
PUBLISHER = "p01"

# ─────────────────────────────────────────────────────────────
# ข้อมูลหมวดสินค้า — pain point จริง + วิธีใช้ + แฮชแท็ก
# แก้/เพิ่มได้เลย นี่คือส่วนที่ทำให้คอนเทนต์ "พูดถูกปัญหา"
# ─────────────────────────────────────────────────────────────
CATEGORIES = {
    "ผัก/ปลูกเอง": {
        "pains": [
            "ปลูกแล้วตายทั้งชุด",
            "ใบเหลืองไม่รู้เป็นอะไร",
            "รากเน่าเงียบๆ",
            "อยากปลูกแต่พื้นที่น้อยมาก",
            "ไม่รู้จะเริ่มยังไงเลย",
        ],
        "howto": "ผสมปุ๋ย A/B ตามสัดส่วนในคู่มือ เช็คค่า EC/PPM อาทิตย์ละครั้ง แล้วเปลี่ยนน้ำทุก 7-14 วัน",
        "results": [
            "ผ่านไป 2 อาทิตย์ ใบเขียวขึ้นชัดเจน",
            "ผักโตเร็วกว่าเดิมเกือบเท่าตัว",
            "รากขาวสะอาด ไม่เน่าเลย",
        ],
        "tags": ["ปลูกผักกินเอง", "ไฮโดรโปรนิกส์", "ผักสลัด", "ปลูกผักในบ้าน", "สวนผักหลังบ้าน", "มือใหม่หัดปลูก"],
    },
    "ความงาม/สกินแคร์": {
        "pains": [
            "สิวขึ้นไม่หยุด",
            "หน้ามันกลางวัน ทั้งที่ล้างหน้าแล้ว",
            "รอยดำจากสิวไม่จางสักที",
            "ผิวแพ้ง่าย ใช้ครีมอะไรก็ไม่ถูก",
            "เครื่องสำอางแพงแต่ไม่เห็นผล",
        ],
        "howto": "ใช้หลังล้างหน้า ทาวันละ 1-2 ครั้ง ก่อนออกแดดควรทากันแดดทับ",
        "results": [
            "ผ่านไป 3 อาทิตย์ หน้ามันน้อยลง",
            "รอยดำจางลงแบบเห็นได้",
            "ผิวไม่แสบ ไม่แดงแล้ว",
        ],
        "tags": ["สกินแคร์", "ดูแลผิว", "ผิวสวย", "รีวิวสกินแคร์", "สิว", "ผิวแพ้ง่าย"],
    },
    "แม่และเด็ก": {
        "pains": [
            "ลูกไม่ยอมกินข้าว",
            "ผื่นผ้าอ้อมขึ้นซ้ำๆ",
            "ลูกนอนไม่หลับ กลางคืนตื่นบ่อย",
            "ของใช้เด็กเต็มบ้าน หาไม่เจอ",
            "อยากทำอาหารให้ลูกแต่ไม่มีเวลา",
        ],
        "howto": "ใช้ตอนลูกตื่น หลังมื้ออาหาร สังเกต 3-5 วันก่อนตัดสินใจ",
        "results": [
            "ลูกยอมกินมากขึ้นชัดเจน",
            "ผื่นหายภายใน 3 วัน",
            "กลางคืนตื่นน้อยลง",
        ],
        "tags": ["แม่และเด็ก", "ของใช้เด็ก", "เลี้ยงลูก", "แม่มือใหม่", "ของใช้แม่และเด็ก"],
    },
    "บ้าน/ครัว": {
        "pains": [
            "ครัวรก ของไม่มีที่เก็บ",
            "ของในตู้เย็นลืมกินจนเสีย",
            "ทำความสะอาดแล้วก็สกปรกอีก",
            "พื้นที่เล็ก เก็บของไม่พอ",
            "อุปกรณ์เยอะแต่ใช้จริงไม่กี่ชิ้น",
        ],
        "howto": "จัดหลังทำอาหาร ใช้บริเวณที่ใช้บ่อยที่สุดก่อน แล้วค่อยขยับไปจุดอื่น",
        "results": [
            "เคาน์เตอร์ว่างขึ้นทันที",
            "หาได้ใน 3 วิ ไม่ต้องรื้อทั้งตู้",
            "ของเสียในตู้เย็นลดลงชัดเจน",
        ],
        "tags": ["จัดบ้าน", "ของใช้ในบ้าน", "ครัว", "จัดระเบียบ", "ของมันต้องมี"],
    },
    "แกดเจ็ต": {
        "pains": [
            "สายชาร์จพังทุกเดือน",
            "หูฟังค้างตลอดเวลา",
            "โทรศัพท์ร้อนก็ชาร์จช้า",
            "ของชาร์จไม่มีพกพา ลำบากเวลาไปข้างนอก",
            "ซื้อของถูกแล้วพังเร็ว",
        ],
        "howto": "ชาร์จครั้งแรกให้เต็ม แล้วใช้งานตามปกติ สังเกตความร้อนตอนชาร์จ",
        "results": [
            "ใช้มา 2 เดือน ยังไม่พัง",
            "ชาร์จเร็วขึ้นจริง ไม่ร้อน",
            "พกง่าย ใส่กระเป๋าได้เลย",
        ],
        "tags": ["แกดเจ็ต", "ของใช้ไอที", "อุปกรณ์เสริม", "ของมันต้องมี", "รีวิวของใช้"],
    },
    "ทั่วไป": {
        "pains": [
            "ซื้อของถูกแล้วพังเร็ว",
            "ไม่รู้จะเลือกอันไหนดี",
            "ของเยอะแต่ไม่มีอันไหนถูกใจ",
        ],
        "howto": "ใช้ตามคู่มือ สังเกตผลลัพธ์ 7-14 วันก่อนตัดสินใจว่าใช้ได้จริงไหม",
        "results": ["ใช้มาเดือนกว่า ยังดีอยู่", "คุ้มกับราคาจริงๆ"],
        "tags": ["ของมันต้องมี", "รีวิวของใช้", "ของใช้ในชีวิตประจำวัน"],
    },
}

PLATFORMS = {
    "tt": "TikTok",
    "sv": "Shopee Video",
    "fb": "Facebook",
    "lm": "Lemon8",
}

FORMATS = {
    "vid": "Timelapse การเติบโต",
    "ba": "Before / After",
    "pr": "ปัญหา → สินค้า",
    "cmp": "เทียบของถูก vs ของที่ใช้",
    "hw": "สอน 30 วิ",
}

FLOW = {
    "vid": "เร่งความเร็ว 14 วันให้เห็นการเปลี่ยนแปลง",
    "ba": "วางภาพก่อน-หลังติดกัน ให้คนดู 'เห็น' ไม่ต้องจินตนาการ",
    "pr": "เปิดด้วยปัญหา 3 วิแรก แล้วโชว์ว่าอันนี้แก้ให้ได้",
    "cmp": "วางของถูกกับของที่ใช้จริงข้างกัน แล้วบอกว่าต่างกันตรงไหน (ไม่ด่าของถูก)",
    "hw": "สอนวิธีใช้ให้จบใน 30 วิ ไม่ขายก่อน 22 วิ",
}


def commission_per_order(price, pct):
    """คอมต่อออเดอร์ — Shopee cap 225 บาท/ออเดอร์"""
    return min(round(price * pct / 100.0, 2), 225.0)


def build_link(landing_url, affiliate_id, sub_id):
    """ลิงก์ affiliate ตามรูปแบบที่ Shopee กำหนด"""
    enc = urllib.parse.quote(landing_url, safe="")
    return (
        "https://shope.ee/an_redir?origin_link="
        + enc
        + "&affiliate_id="
        + str(affiliate_id)
        + "&sub_id="
        + sub_id
    )


def build_pack(item, opts):
    """สร้าง content pack 1 ชิ้น"""
    name = (item.get("name") or "").strip() or "สินค้า"
    try:
        price = float(item.get("price") or 0)
    except ValueError:
        price = 0.0
    try:
        pct = float(item.get("commission_pct") or 2)
    except ValueError:
        pct = 2.0

    landing = (item.get("url") or "").strip()
    category = opts.get("category") or "ทั่วไป"
    cat = CATEGORIES.get(category, CATEGORIES["ทั่วไป"])

    cid = (item.get("content_id") or "").strip() or opts.get("next_id", "c001")
    platform = opts.get("platform") or "tt"
    fmt = opts.get("format") or "pr"

    sub_id = "-".join([PUBLISHER, cid, platform, fmt])
    aff_link = build_link(landing, opts.get("affiliate_id") or "YOUR_ID", sub_id)

    pain = (item.get("pain") or "").strip() or cat["pains"][0]
    howto = cat["howto"]
    result = cat["results"][0]
    price_txt = f"{price:,.0f}" if price else "—"

    # ── hook 5 แบบ (ใช้ 5 แบบนี้ทดสอบ แล้วเก็บที่ชนะ)
    hooks = [
        f"{pain} — เราก็เคยเป็น แล้วมันแก้ได้จริง",
        "3 อย่างที่มือใหม่ซื้อผิด ราคาแพงคืออันที่ 2",
        f"ใช้ {price_txt} บาท คุ้มไหม? มาดูของจริง",
        "14 วันก่อน กับวันนี้ — ต่างกันขนาดนี้",
        f"{pain} อยู่ใช่ไหม? ดูอันนี้ก่อนตัดสินใจ",
    ]

    # ── สคริปต์ 15-30 วิ
    script = (
        "[0-3 วิ]  HOOK — ต้องจบปัญหาของคนดู ห้ามขึ้นด้วยชื่อสินค้า\n"
        f'         "{pain}"\n\n'
        "[3-10 วิ] โชว์ของจริงในมือ (ฟุตเทจของคุณเองเท่านั้น)\n"
        f'         "{name}" ราคา {price_txt} บาท\n\n'
        "[10-22 วิ] วิธีใช้ + ผลลัพธ์\n"
        f"         วิธีใช้: {howto}\n"
        f"         ผลลัพธ์: {result}\n\n"
        "[22-30 วิ] CTA\n"
        '         "ลิงก์อยู่ในคอมเมนต์แรกนะครับ"\n'
        '         "โพสต์นี้มีลิงก์ affiliate — ซื้อผ่านลิงก์นี้ราคาเท่าเดิม ผมได้ค่าคอมเล็กน้อย"\n'
    )

    # ── โชว์สิ่งที่ต้องถ่าย (กันตันตอนถ่ายจริง)
    shots = [
        "Shot 1 (3 วิ) — หน้าคุณพูด hook ตรงกล้อง หรือ close-up ปัญหา",
        "Shot 2 (5 วิ) — สินค้าในมือ หมุนให้เห็นรอบเดียว",
        "Shot 3 (8 วิ) — ใช้งานจริง ไม่ตัดต่อให้ดูเป็นธรรมชาติ",
        "Shot 4 (6 วิ) — ผลลัพธ์ / ก่อน-หลัง ติดกัน",
        "Shot 5 (5 วิ) — ยิ้ม + ชี้ลง (บอกให้ไปดูคอมเมนต์)",
    ]

    # ── แคปชัน
    tags = " ".join("#" + t for t in cat["tags"][:5])
    caption = (
        f"{pain} — เราก็เคยเป็น 😮‍💨\n\n"
        f"ลอง {name} แล้วพบว่า {result}\n"
        f"ราคา {price_txt} บาท\n\n"
        "📌 ลิงก์อยู่ในคอมเมนต์แรก\n"
        f"{tags}\n\n"
        "— โพสต์นี้มีลิงก์ affiliate ถ้าซื้อผ่านลิงก์ เราจะได้ค่าคอมเล็กน้อย "
        "โดยราคาที่คุณจ่ายเท่าเดิม"
    )

    cpo = commission_per_order(price, pct)
    orders_to_1500 = math.ceil(1500 / cpo) if cpo > 0 else None

    return {
        "content_id": cid,
        "sub_id": sub_id,
        "name": name,
        "price": price_txt,
        "commission_pct": pct,
        "commission_per_order": cpo,
        "orders_to_first_payout": orders_to_1500,
        "affiliate_link": aff_link,
        "platform": PLATFORMS.get(platform, platform),
        "format": FORMATS.get(fmt, fmt),
        "format_note": FLOW.get(fmt, ""),
        "hooks": hooks,
        "script": script,
        "shots": shots,
        "caption": caption,
        "hashtags": tags,
        "checklist": [
            "ฟุตเทจเป็นของคุณเอง 100% (ห้ามใช้คลิปคนอื่น — Shopee แบนข้อหา plagiarism)",
            "ลิงก์ใส่ในคอมเมนต์ ไม่ใช่ในตัวคลิป",
            "เปิดเผยว่าเป็นลิงก์ affiliate แล้ว",
            "นับลิงก์รวมทุกช่องวันนี้ไม่เกิน 30",
            "กดโพสต์ด้วยมือ — ห้ามใช้บอท",
        ],
    }


def parse_batch(text):
    """แต่ละบรรทัด: ชื่อสินค้า | ราคา | คอม% | ลิงก์สินค้า"""
    items = []
    for i, line in enumerate(text.splitlines(), start=1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        item = {
            "name": parts[0] if len(parts) > 0 else "",
            "price": parts[1] if len(parts) > 1 else "0",
            "commission_pct": parts[2] if len(parts) > 2 else "2",
            "url": parts[3] if len(parts) > 3 else "",
            "content_id": f"c{i:03d}",
        }
        items.append(item)
    return items


# ─────────────────────────────────────────────────────────────
# HTTP
# ─────────────────────────────────────────────────────────────
class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args, **kwargs):
        pass  # เงียบ — ไม่รก terminal

    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.startswith("/api/health"):
            self._send(200, json.dumps({"ok": True}))
            return
        self._send(200, PAGE, "text/html; charset=utf-8")

    def do_POST(self):
        if not self.path.startswith("/api/generate"):
            self._send(404, json.dumps({"error": "not found"}))
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception as exc:
            self._send(400, json.dumps({"error": str(exc)}, ensure_ascii=False))
            return

        opts = {
            "category": data.get("category"),
            "platform": data.get("platform"),
            "format": data.get("format"),
            "affiliate_id": data.get("affiliate_id"),
        }

        mode = data.get("mode", "single")
        if mode == "batch":
            items = parse_batch(data.get("batch_text", ""))
        else:
            items = [data.get("item", {})]

        packs = [build_pack(it, opts) for it in items]
        self._send(200, json.dumps(
            {"count": len(packs), "packs": packs, "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M")},
            ensure_ascii=False,
        ))


PAGE = r"""<!DOCTYPE html>
<html lang="th"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Affiliate Content Factory</title>
<style>
  :root{--bg:#0f1115;--card:#171a21;--line:#262b36;--fg:#e6e9ef;--dim:#8b93a3;--acc:#4ade80;--acc2:#60a5fa;--warn:#fbbf24}
  *{box-sizing:border-box}
  body{margin:0;font:15px/1.6 -apple-system,"Segoe UI",Roboto,"Noto Sans Thai",sans-serif;background:var(--bg);color:var(--fg)}
  .wrap{max-width:1080px;margin:0 auto;padding:28px 18px 80px}
  h1{font-size:22px;margin:0 0 4px}
  .sub{color:var(--dim);font-size:13px;margin-bottom:22px}
  .card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px;margin-bottom:16px}
  label{display:block;font-size:12px;color:var(--dim);margin:10px 0 4px;text-transform:uppercase;letter-spacing:.4px}
  input,select,textarea{width:100%;background:#0c0e12;border:1px solid var(--line);border-radius:8px;color:var(--fg);padding:9px 11px;font:inherit;font-size:14px}
  textarea{min-height:110px;resize:vertical;font-family:ui-monospace,Consolas,monospace;font-size:13px}
  input:focus,select:focus,textarea:focus{outline:none;border-color:var(--acc2)}
  .row{display:grid;gap:12px}
  .r2{grid-template-columns:1fr 1fr}.r3{grid-template-columns:1fr 1fr 1fr}
  @media(max-width:700px){.r2,.r3{grid-template-columns:1fr}}
  button{background:var(--acc);color:#07230f;border:0;border-radius:8px;padding:12px 20px;font:inherit;font-weight:700;cursor:pointer}
  button:hover{filter:brightness(1.08)}
  button.ghost{background:transparent;color:var(--dim);border:1px solid var(--line);font-weight:500;padding:6px 12px;font-size:12px}
  .tabs{display:flex;gap:8px;margin-bottom:14px}
  .tab{padding:7px 14px;border-radius:999px;border:1px solid var(--line);cursor:pointer;font-size:13px;color:var(--dim)}
  .tab.on{background:var(--acc2);color:#04203d;border-color:var(--acc2);font-weight:700}
  .pack{border:1px solid var(--line);border-radius:12px;padding:16px;margin-bottom:14px;background:#12151b}
  .pack h3{margin:0 0 2px;font-size:16px}
  .meta{color:var(--dim);font-size:12px;margin-bottom:12px}
  .box{background:#0c0e12;border:1px solid var(--line);border-radius:8px;padding:10px 12px;margin:8px 0;position:relative}
  .box pre{margin:0;white-space:pre-wrap;word-break:break-word;font-family:ui-monospace,Consolas,monospace;font-size:12.5px;color:#cfd6e4}
  .box .h{font-size:11px;color:var(--dim);text-transform:uppercase;letter-spacing:.4px;margin-bottom:6px;display:flex;justify-content:space-between;align-items:center}
  .copy{position:absolute;top:8px;right:8px}
  .kv{display:flex;gap:16px;flex-wrap:wrap;font-size:13px;margin-bottom:10px}
  .kv b{color:var(--acc)}
  .warn{color:var(--warn)}
  ul{margin:6px 0;padding-left:20px}
  li{font-size:13px;margin:3px 0}
  .hint{font-size:12px;color:var(--dim);margin-top:6px}
  .err{background:#2a1414;border-color:#5b2020;color:#fca5a5}
  code{background:#0c0e12;padding:1px 5px;border-radius:4px;font-size:12.5px}
</style></head>
<body><div class="wrap">

<h1>🏭 Affiliate Content Factory</h1>
<div class="sub">ใส่สินค้า → ได้ content pack พร้อมโพสต์ · รันออฟไลน์ · ไม่มีค่าใช้จ่าย · ไม่มี dependency</div>

<div class="card">
  <div class="tabs">
    <div class="tab on" data-mode="single">สินค้าเดี่ยว</div>
    <div class="tab" data-mode="batch">หลายสินค้า (แบทช์)</div>
  </div>

  <div class="row r3">
    <div>
      <label>หมวดสินค้า</label>
      <select id="category"></select>
    </div>
    <div>
      <label>ช่องทางที่จะโพสต์</label>
      <select id="platform">
        <option value="tt">TikTok</option>
        <option value="sv">Shopee Video</option>
        <option value="fb">Facebook</option>
        <option value="lm">Lemon8</option>
      </select>
    </div>
    <div>
      <label>รูปแบบคลิป</label>
      <select id="format">
        <option value="pr">ปัญหา → สินค้า</option>
        <option value="vid">Timelapse การเติบโต</option>
        <option value="ba">Before / After</option>
        <option value="cmp">เทียบของถูก vs ของที่ใช้</option>
        <option value="hw">สอน 30 วิ</option>
      </select>
    </div>
  </div>

  <label>Shopee Affiliate ID ของคุณ (ถ้ามี)</label>
  <input id="affiliate_id" placeholder="เช่น 1234567890 — ถ้าไม่ใส่จะขึ้น YOUR_ID ให้ไปแทนทีหลัง">

  <div id="pane-single">
    <div class="row r3">
      <div><label>ชื่อสินค้า</label><input id="name" placeholder="เช่น ชุดปลูกผักไฮโดร 36 หลุม"></div>
      <div><label>ราคา (บาท)</label><input id="price" placeholder="690"></div>
      <div><label>คอมมิชชัน (%)</label><input id="commission_pct" placeholder="2" value="2"></div>
    </div>
    <label>ลิงก์หน้าสินค้า (landing page)</label>
    <input id="url" placeholder="https://shopee.co.th/product/...">
    <label>ปัญหาที่สินค้านี้แก้ (เว้นว่างได้ — ระบบจะเลือกให้)</label>
    <input id="pain" placeholder="ปลูกแล้วตายทั้งชุด">
  </div>

  <div id="pane-batch" style="display:none">
    <label>วางทีละบรรทัด — รูปแบบ: <code>ชื่อสินค้า | ราคา | คอม% | ลิงก์สินค้า</code></label>
    <textarea id="batch_text" placeholder="ชุดปลูกผักไฮโดร 36 หลุม | 690 | 2 | https://shopee.co.th/product/...
ปุ๋ย AB สำหรับไฮโดร | 250 | 3 | https://shopee.co.th/product/...
เมล็ดผักสลัดรวม 5 ชนิด | 120 | 2 | https://shopee.co.th/product/..."></textarea>
    <div class="hint">บรรทัดที่ขึ้นต้นด้วย <code>#</code> จะถูกข้าม · เว้นบรรทัดว่างได้</div>
  </div>

  <div style="margin-top:18px"><button id="go">สร้าง Content Pack</button></div>
</div>

<div id="out"></div>

<div class="card">
  <b>⚠️ กฎที่ระบบนี้บังคับให้คุณทำตาม</b>
  <ul>
    <li>ฟุตเทจต้องเป็นของคุณเอง — ห้ามใช้คลิปคนอื่น (Shopee แบนข้อหา plagiarism)</li>
    <li>ลิงก์ affiliate ใส่ใน <b>คอมเมนต์</b> ไม่ใช่ในตัวคลิป</li>
    <li>รวมทุกช่องแล้ว <b>ไม่เกิน 30 ลิงก์/วัน</b> — เกินกว่านี้คือ spam flag</li>
    <li>กดโพสต์ด้วยมือเสมอ — ห้ามใช้บอท (ToS ข้อ 6.4)</li>
    <li>เปิดเผยว่าเป็นลิงก์ affiliate ทุกโพสต์</li>
  </ul>
</div>

<script>
const CATS = __CATEGORIES__;

const $ = id => document.getElementById(id);
let mode = "single";

Object.keys(CATS).forEach(k => {
  const o = document.createElement("option");
  o.value = k; o.textContent = k; $("category").appendChild(o);
});

document.querySelectorAll(".tab").forEach(t => t.onclick = () => {
  document.querySelectorAll(".tab").forEach(x => x.classList.remove("on"));
  t.classList.add("on");
  mode = t.dataset.mode;
  $("pane-single").style.display = mode === "single" ? "" : "none";
  $("pane-batch").style.display  = mode === "batch"  ? "" : "none";
});

function esc(s){return String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));}

function box(title, text){
  return `<div class="box"><div class="h"><span>${esc(title)}</span>
    <button class="ghost copy" data-copy="${esc(text)}">คัดลอก</button></div>
    <pre>${esc(text)}</pre></div>`;
}

function renderPacks(packs){
  const out = $("out");
  if(!packs.length){ out.innerHTML = '<div class="card err">ไม่มีข้อมูลให้สร้าง — ลองใส่สินค้าดูอีกที</div>'; return; }
  out.innerHTML = packs.map(p => `
    <div class="pack">
      <h3>${esc(p.name)}</h3>
      <div class="meta">ID <b>${esc(p.content_id)}</b> · sub_id <code>${esc(p.sub_id)}</code> · ${esc(p.platform)} · ${esc(p.format)}</div>
      <div class="kv">
        <span>ราคา <b>${esc(p.price)}</b> ฿</span>
        <span>คอม <b>${esc(p.commission_pct)}%</b></span>
        <span>คอม/ออเดอร์ <b>${esc(p.commission_per_order)}</b> ฿</span>
        ${p.orders_to_first_payout ? `<span>ต้องขาย <b>${p.orders_to_first_payout}</b> ออเดอร์ถึงถอนได้ (1,500 ฿)</span>` : ""}
      </div>
      ${box("ลิงก์ affiliate", p.affiliate_link)}
      ${box("Hook 5 แบบ — ใช้ทดสอบ แล้วเก็บที่ชนะ", p.hooks.map((h,i)=>`${i+1}. ${h}`).join("\n"))}
      ${box("สคริปต์ 15-30 วิ", p.script)}
      ${box("Shot list — ถ่ายตามนี้", p.shots.map((s,i)=>`${i+1}. ${s}`).join("\n"))}
      ${box("แคปชัน", p.caption)}
      ${box("แฮชแท็ก", p.hashtags)}
      ${box("✅ เช็กลิสต์ก่อนกดโพสต์", p.checklist.map(c=>"• "+c).join("\n"))}
    </div>`).join("") + `<div class="card sub" style="margin:0">สร้างเมื่อ ${esc(window.__ts||"")} · ${packs.length} ชิ้น</div>`;
  out.querySelectorAll(".copy").forEach(b => b.onclick = async () => {
    try { await navigator.clipboard.writeText(b.dataset.copy); b.textContent = "คัดลอกแล้ว ✓";
      setTimeout(()=>b.textContent="คัดลอก",1200); } catch(e){ b.textContent = "กด Ctrl+C"; }
  });
}

$("go").onclick = async () => {
  const payload = {
    mode,
    category: $("category").value,
    platform: $("platform").value,
    format: $("format").value,
    affiliate_id: $("affiliate_id").value.trim(),
    batch_text: $("batch_text").value,
    item: {
      name: $("name").value, price: $("price").value,
      commission_pct: $("commission_pct").value,
      url: $("url").value, pain: $("pain").value
    }
  };
  $("go").textContent = "กำลังสร้าง...";
  try {
    const r = await fetch("/api/generate", {
      method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify(payload)
    });
    const d = await r.json();
    if(d.error) throw new Error(d.error);
    window.__ts = d.generated_at;
    renderPacks(d.packs);
  } catch(e) {
    $("out").innerHTML = '<div class="card err">ผิดพลาด: ' + esc(e.message) + '</div>';
  }
  $("go").textContent = "สร้าง Content Pack";
};
</script></div></body></html>
"""


def main():
    # คอนโซล Windows บางตัวเป็น cp1252 → กันแอปพังตอน print ภาษาไทย/emoji
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    with contextlib.suppress(Exception):
        if reconfigure:
            reconfigure(encoding="utf-8", errors="replace")

    html = PAGE.replace("__CATEGORIES__", json.dumps(CATEGORIES, ensure_ascii=False))
    globals()["PAGE"] = html

    server = HTTPServer(("127.0.0.1", PORT), Handler)
    url = f"http://localhost:{PORT}"
    print("")
    print("  🏭  Affiliate Content Factory")
    print("  ─────────────────────────────────────────")
    print("  เปิดอยู่ที่:  " + url)
    print("  ปิด: กด Ctrl+C")
    print("")
    with contextlib.suppress(Exception):
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  ปิดแล้ว\n")


if __name__ == "__main__":
    main()
