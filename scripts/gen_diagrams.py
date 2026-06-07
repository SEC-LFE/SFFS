#!/usr/bin/env python3
"""
gen_diagrams.py — Generate the two diagrams missing from the SFFS report:
  - ER diagram (auth.db, audit.db, wrap_store.db)  -> assets/er_diagram.png
  - PERT chart (GP2 task network)                  -> assets/pert_chart.png

Pure-PIL (no graphviz/matplotlib needed). Dark theme to match the existing
report figures. Run: python scripts/gen_diagrams.py
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "docs" / "presentations" / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)

# ── palette (matches dark canvas look of the other figures) ──────────────────
BG = (22, 22, 26)
GRID = (34, 34, 40)
BOX = (38, 38, 46)
BOX_HDR = (30, 52, 128)      # navy header
BOX_BORDER = (120, 130, 150)
TEXT = (235, 238, 245)
SUBTLE = (165, 172, 185)
ACCENT = (60, 120, 240)      # relationship lines
GOLD = (249, 168, 37)
GREEN = (13, 148, 136)


def _font(size, bold=False):
    names = (["arialbd.ttf", "ArialBd.ttf"] if bold else ["arial.ttf", "Arial.ttf"])
    for n in names:
        for base in ("C:/Windows/Fonts/", ""):
            try:
                return ImageFont.truetype(base + n, size)
            except OSError:
                continue
    return ImageFont.load_default()


def _grid(d, w, h, step=28):
    for x in range(0, w, step):
        d.line([(x, 0), (x, h)], fill=GRID, width=1)
    for y in range(0, h, step):
        d.line([(0, y), (w, y)], fill=GRID, width=1)


def _text_w(d, s, f):
    return d.textbbox((0, 0), s, font=f)[2]


# ═════════════════════════════════════════════════════════════════════════════
#  ER DIAGRAM
# ═════════════════════════════════════════════════════════════════════════════
def entity(d, x, y, w, title, rows, f_hdr, f_row):
    """Draw an entity table; rows is list of (text, is_pk, is_fk). Returns box rect."""
    hdr_h = 34
    row_h = 24
    h = hdr_h + row_h * len(rows)
    d.rectangle([x, y, x + w, y + h], fill=BOX, outline=BOX_BORDER, width=2)
    d.rectangle([x, y, x + w, y + hdr_h], fill=BOX_HDR, outline=BOX_BORDER, width=2)
    tw = _text_w(d, title, f_hdr)
    d.text((x + (w - tw) / 2, y + 8), title, font=f_hdr, fill=TEXT)
    cy = y + hdr_h
    for text, is_pk, is_fk in rows:
        d.line([(x, cy), (x + w, cy)], fill=(60, 60, 70), width=1)
        marker = ""
        col = TEXT
        if is_pk:
            marker = "PK  "
            col = GOLD
        elif is_fk:
            marker = "FK  "
            col = GREEN
        label = marker + text
        d.text((x + 12, cy + 5), label, font=f_row, fill=col)
        if is_pk:
            # underline PK attribute name
            mw = _text_w(d, marker, f_row)
            nw = _text_w(d, text, f_row)
            uy = cy + 5 + 16
            d.line([(x + 12 + mw, uy), (x + 12 + mw + nw, uy)], fill=GOLD, width=1)
        cy += row_h
    return (x, y, x + w, y + h)


def crowfoot_rel(d, src_rect, dst_rect, f):
    """Draw a 1-to-many relationship line from src (the 'one') to dst (the 'many')."""
    sx = src_rect[2]
    sy = (src_rect[1] + src_rect[3]) / 2
    dx = dst_rect[0]
    dy = (dst_rect[1] + dst_rect[3]) / 2
    midx = (sx + dx) / 2
    pts = [(sx, sy), (midx, sy), (midx, dy), (dx, dy)]
    d.line(pts, fill=ACCENT, width=3, joint="curve")
    # "1" near source
    d.text((sx + 6, sy - 20), "1", font=f, fill=ACCENT)
    # crow's foot (many) at destination
    d.line([(dx, dy), (dx - 14, dy - 9)], fill=ACCENT, width=3)
    d.line([(dx, dy), (dx - 14, dy + 9)], fill=ACCENT, width=3)
    d.line([(dx, dy), (dx - 14, dy)], fill=ACCENT, width=3)
    d.text((dx - 26, dy - 22), "N", font=f, fill=ACCENT)


def gen_er():
    W, H = 1500, 980
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    _grid(d, W, H)

    f_title = _font(30, bold=True)
    f_hdr = _font(18, bold=True)
    f_row = _font(15)
    f_db = _font(17, bold=True)
    f_rel = _font(16, bold=True)

    d.text((40, 24), "SFFS — Entity Relationship Diagram", font=f_title, fill=TEXT)
    d.text((40, 64), "Three SQLite databases on the USB drive (sffs_data/)",
           font=_font(16), fill=SUBTLE)

    # DB group labels
    d.text((60, 110), "auth.db", font=f_db, fill=GREEN)
    d.text((900, 110), "audit.db", font=f_db, fill=GREEN)
    d.text((900, 560), "wrap_store.db", font=f_db, fill=GREEN)

    users = entity(d, 60, 150, 360, "users", [
        ("user_id : TEXT (UUID)", True, False),
        ("username : TEXT UNIQUE", False, False),
        ("password_hash : TEXT (Argon2id)", False, False),
        ("created_at : TEXT", False, False),
        ("last_login : TEXT", False, False),
        ("failed_attempts : INTEGER", False, False),
        ("locked_until : TEXT NULL", False, False),
    ], f_hdr, f_row)

    sessions = entity(d, 60, 470, 360, "sessions", [
        ("session_token : TEXT", True, False),
        ("user_id : TEXT", False, True),
        ("created_at : TEXT", False, False),
        ("expires_at : TEXT (+24h)", False, False),
    ], f_hdr, f_row)

    audit = entity(d, 900, 150, 420, "audit_log", [
        ("id : INTEGER", True, False),
        ("timestamp : TEXT", False, False),
        ("event : TEXT", False, False),
        ("level : TEXT (INFO..CRITICAL)", False, False),
        ("module : TEXT", False, False),
        ("user_id : TEXT", False, True),
        ("hash_chain : TEXT (HMAC)", False, False),
        ("metadata_json : TEXT", False, False),
    ], f_hdr, f_row)

    wrapped = entity(d, 900, 600, 420, "wrapped_keys", [
        ("sffs_path_hash : TEXT (SHA-256)", True, False),
        ("wrap_data_b64 : TEXT (RSA-OAEP)", False, False),
        ("user_id : TEXT", False, True),
        ("created_at : TEXT", False, False),
    ], f_hdr, f_row)

    # relationships (users is the "one" side)
    crowfoot_rel(d, users, sessions, f_rel)   # vertical within auth.db
    crowfoot_rel(d, users, audit, f_rel)
    crowfoot_rel(d, users, wrapped, f_rel)

    # legend
    ly = 880
    d.text((60, ly), "PK", font=f_row, fill=GOLD)
    d.text((100, ly), "primary key", font=f_row, fill=SUBTLE)
    d.text((240, ly), "FK", font=f_row, fill=GREEN)
    d.text((280, ly), "foreign key (logical, user_id)", font=f_row, fill=SUBTLE)
    d.text((600, ly), "1 — N", font=f_rel, fill=ACCENT)
    d.text((680, ly), "one-to-many relationship", font=f_row, fill=SUBTLE)

    out = ASSETS / "er_diagram.png"
    img.save(out)
    print("wrote", out)


# ═════════════════════════════════════════════════════════════════════════════
#  PERT CHART
# ═════════════════════════════════════════════════════════════════════════════
def gen_pert():
    W, H = 1700, 760
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    _grid(d, W, H)

    f_title = _font(30, bold=True)
    f_id = _font(20, bold=True)
    f_lbl = _font(13)
    f_dur = _font(13, bold=True)

    d.text((40, 24), "SFFS — PERT Chart (GP2 Task Network)", font=f_title, fill=TEXT)
    d.text((40, 64), "Nodes = tasks (duration in days); arrows = dependencies; "
                     "bold path = critical path", font=_font(15), fill=SUBTLE)

    # node: id, label lines, duration, (col,row) on a grid, critical flag
    NW, NH = 150, 84
    COLX = [40, 260, 480, 700, 920, 1140, 1360, 1530]
    ROWY = [120, 250, 380, 510]

    nodes = {
        1:  ("T1", ["Planning &", "requirements"], "7d", 0, 1, True),
        2:  ("T2", ["Architecture", "& design"], "7d", 1, 1, True),
        3:  ("T3", ["UI design &", "prototyping"], "21d", 2, 0, False),
        4:  ("T4", ["User auth", "module"], "14d", 2, 1, False),
        5:  ("T5", ["File encrypt/", "decrypt (AES)"], "35d", 2, 2, True),
        6:  ("T6", ["Key mgmt", "(RSA)"], "7d", 3, 2, True),
        7:  ("T7", ["Integrity", "(SHA-256)"], "7d", 3, 3, False),
        8:  ("T8", ["Isolated exec", "environment"], "42d", 2, 3, False),
        9:  ("T9", ["System", "integration"], "7d", 4, 2, True),
        10: ("T10", ["Cloud backup", "integration"], "7d", 5, 1, False),
        11: ("T11", ["Testing &", "debugging"], "7d", 5, 2, True),
        12: ("T12", ["Perf & security", "tuning"], "7d", 6, 2, True),
        13: ("T13", ["Documentation", "& final report"], "7d", 7, 2, True),
    }

    edges = [
        (1, 2, True),
        (2, 3, False), (2, 4, False), (2, 5, True), (2, 8, False),
        (5, 6, True), (5, 7, False),
        (3, 9, False), (4, 9, False), (6, 9, True), (7, 9, False), (8, 9, False),
        (9, 10, False), (9, 11, True),
        (10, 13, False), (11, 12, True), (12, 13, True),
    ]

    def center(n):
        _, _, _, c, r, _ = nodes[n]
        return (COLX[c] + NW / 2, ROWY[r] + NH / 2)

    # edges first (under nodes)
    for a, b, crit in edges:
        ax, ay = center(a)
        bx, by = center(b)
        ax += NW / 2
        bx -= NW / 2
        col = GOLD if crit else (90, 100, 120)
        wd = 4 if crit else 2
        midx = (ax + bx) / 2
        d.line([(ax, ay), (midx, ay), (midx, by), (bx, by)], fill=col, width=wd, joint="curve")
        # arrowhead
        d.polygon([(bx, by), (bx - 12, by - 6), (bx - 12, by + 6)], fill=col)

    # nodes
    for n, (nid, lines, dur, c, r, crit) in nodes.items():
        x, y = COLX[c], ROWY[r]
        border = GOLD if crit else BOX_BORDER
        d.rectangle([x, y, x + NW, y + NH], fill=BOX, outline=border, width=3 if crit else 2)
        d.rectangle([x, y, x + NW, y + 26], fill=BOX_HDR, outline=border, width=2)
        d.text((x + 10, y + 4), nid, font=f_id, fill=TEXT)
        dw = _text_w(d, dur, f_dur)
        d.text((x + NW - dw - 10, y + 5), dur, font=f_dur, fill=GOLD)
        for i, ln in enumerate(lines):
            d.text((x + 10, y + 34 + i * 18), ln, font=f_lbl, fill=TEXT)

    # legend
    ly = 690
    d.rectangle([40, ly, 70, ly + 16], fill=BOX, outline=GOLD, width=3)
    d.text((80, ly), "critical-path task", font=f_lbl, fill=SUBTLE)
    d.line([(260, ly + 8), (320, ly + 8)], fill=GOLD, width=4)
    d.text((330, ly), "critical path", font=f_lbl, fill=SUBTLE)
    d.line([(470, ly + 8), (530, ly + 8)], fill=(90, 100, 120), width=2)
    d.text((540, ly), "dependency", font=f_lbl, fill=SUBTLE)

    out = ASSETS / "pert_chart.png"
    img.save(out)
    print("wrote", out)


if __name__ == "__main__":
    gen_er()
    gen_pert()
