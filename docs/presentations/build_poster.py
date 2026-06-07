#!/usr/bin/env python3
"""Ciphered Order — SFFS poster. Pure-visual, museum-grade. PIL only."""
import random, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONTS = r"C:/Users/iblfe/.claude/skills/canvas-design/canvas-fonts"
def F(name, size): return ImageFont.truetype(f"{FONTS}/{name}", size)

# ---- palette ---------------------------------------------------------------
INK    = (16, 21, 27)        # sealed-vault blue-black
INK2   = (40, 48, 57)
HEX    = (92, 102, 112)      # muted lattice glyph
HEXF   = (60, 70, 80)
BONE   = (233, 228, 216)     # pressed paper
BONE2  = (224, 218, 204)
AMBER  = (190, 104, 42)      # oxidized signal — the key
AMBERD = (150, 80, 32)

# ---- canvas ----------------------------------------------------------------
SS = 2                       # supersample
W, H = 2400, 3200
W2, H2 = W*SS, H*SS
img = Image.new("RGB", (W2, H2), BONE)
d = ImageDraw.Draw(img)
def s(v): return int(round(v*SS))

# subtle paper tone — faint vertical bone gradient + grain
for y in range(0, H2, SS*3):
    t = y / H2
    c = (int(233-9*t), int(228-9*t), int(216-10*t))
    d.rectangle([0, y, W2, y+SS*3], fill=c)

M = 190                      # outer margin

# ---- header ----------------------------------------------------------------
mono   = F("JetBrainsMono-Regular.ttf", s(20))
monob  = F("JetBrainsMono-Bold.ttf", s(20))
hy = s(150)
d.text((s(M), hy), "PLATE 01 — CIPHERED ORDER", font=mono, fill=INK, anchor="lm")
rt = "AES·256   ARGON2id   SHA·256"
d.text((s(W-M), hy), rt, font=mono, fill=INK, anchor="rm")
d.line([s(M), s(178), s(W-M), s(178)], fill=INK, width=SS)

# ---- plate geometry --------------------------------------------------------
cell = 34
ax, ay = M, 360                       # plate top-left
plate_w = W - 2*M
cols = plate_w // cell
plate_w = cols*cell                   # snap
ax = (W - plate_w)//2
by = 2560                             # plate bottom
rows = (by - ay)//cell
plate_h = rows*cell
bx = ax + plate_w
by = ay + plate_h

# ---- carve mask: monumental "SFFS" -----------------------------------------
mask = Image.new("L", (W2, H2), 0)
md = ImageDraw.Draw(mask)
big = F("BigShoulders-Bold.ttf", s(1180))
word = "SFFS"
cx = (ax+bx)/2
cyw = (ay+by)/2 - 40
md.text((s(cx), s(cyw)), word, font=big, fill=255, anchor="mm")
mpx = mask.load()

def in_word(px, py):
    X, Y = s(px), s(py)
    if 0 <= X < W2 and 0 <= Y < H2:
        return mpx[X, Y] > 128
    return False

# ---- the fortify seam (diagonal where cipher hardens) ----------------------
slope = 0.62
# seam line: x = seam0 + slope*(y-ay); band half-width in px
seam0 = ax + plate_w*0.30
band  = cell*1.15
def seam_dist(px, py):
    sx = seam0 + slope*(py - ay)
    return px - sx                    # <0 plaintext side, >0 ciphertext side

glyphs = "0123456789ABCDEF"
cellfont = F("JetBrainsMono-Regular.ttf", s(int(cell*0.66)))
random.seed(7)

# key location: one cell on the seam, lower-center -> amber key + short shaft
key_r = ay + int(rows*0.66)*cell + cell//2
key_c_x = seam0 + slope*(key_r - ay)
key_col = ax + (round((key_c_x-ax)/cell))*cell

for r in range(rows):
    for c in range(cols):
        x = ax + c*cell
        y = ay + r*cell
        ccx, ccy = x+cell/2, y+cell/2
        if in_word(ccx, ccy):
            continue                                  # name = withheld message
        sd = seam_dist(ccx, ccy)
        # plaintext->ciphertext density along diagonal
        t = (sd)/(plate_w*0.5)
        # key + shaft (3 cells stacked) in amber
        if x == key_col and key_r <= y <= key_r+2*cell:
            pad = cell*0.10
            d.rectangle([s(x+pad), s(y+pad), s(x+cell-pad), s(y+cell-pad)],
                        fill=AMBER)
            continue
        if abs(sd) < band:                            # the seam: solid armor
            pad = cell*0.16
            tone = INK if random.random() > 0.18 else INK2
            d.rectangle([s(x+pad), s(y+pad), s(x+cell-pad), s(y+cell-pad)],
                        fill=tone)
            continue
        if sd > band:                                 # ciphertext: dense glyphs
            if random.random() < 0.10:                # occasional solid block
                pad = cell*0.16
                d.rectangle([s(x+pad), s(y+pad), s(x+cell-pad), s(y+cell-pad)],
                            fill=HEXF)
                continue
            g = random.choice(glyphs)
            d.text((s(ccx), s(ccy)), g, font=cellfont, fill=HEXF, anchor="mm")
        else:                                         # plaintext: sparse, soft
            if random.random() < 0.30:
                continue                              # breathing void
            g = random.choice(glyphs)
            d.text((s(ccx), s(ccy)), g, font=cellfont, fill=HEX, anchor="mm")

# crisp hairline frame around plate
d.rectangle([s(ax), s(ay), s(bx), s(by)], outline=INK, width=SS)
# corner registration ticks
for (px,py) in [(ax,ay),(bx,ay),(ax,by),(bx,by)]:
    d.line([s(px-22),s(py),s(px+22),s(py)], fill=INK, width=SS)
    d.line([s(px),s(py-22),s(px),s(py+22)], fill=INK, width=SS)

# clean crisp stroke tracing the carved word — interior stays bone (negative space)
d.text((s(cx), s(cyw)), word, font=big, anchor="mm",
       fill=None, stroke_width=SS*2, stroke_fill=INK)

# ---- captions under plate --------------------------------------------------
lab = F("JetBrainsMono-Regular.ttf", s(22))
cy = by + s(58)//SS
d.text((s(ax), s(by+58)), "PLAINTEXT", font=lab, fill=INK, anchor="lm")
d.text((s(ax+200), s(by+58)), "→", font=lab, fill=AMBER, anchor="lm")
d.text((s(ax+250), s(by+58)), "CIPHERTEXT", font=lab, fill=INK, anchor="lm")
d.text((s(bx), s(by+58)), "STATE: FORTIFIED", font=lab, fill=INK, anchor="rm")

# expanded name, letterspaced, centered
exp = "S M A R T   F I L E   F O R T I F Y   S Y S T E M"
ef = F("Jura-Medium.ttf", s(34))
d.text((s(W/2), s(by+128)), exp, font=ef, fill=INK, anchor="mm")

# ---- module lattice legend (the imaginary discipline) ----------------------
ly = 2760
d.line([s(M), s(ly-46), s(W-M), s(ly-46)], fill=INK, width=SS)
lt = F("JetBrainsMono-Bold.ttf", s(20))
d.text((s(M), s(ly-78)), "MODULE LATTICE", font=lt, fill=INK, anchor="lm")
d.text((s(W-M), s(ly-78)), "f01–f18", font=lt, fill=AMBER, anchor="rm")

groups = [
    ("code1", "CRYPTO", [("f01","KEYGEN"),("f02","ENCRYPT"),("f03","DECRYPT"),
        ("f04","HASH"),("f05","VERIFY"),("f06","KEYSTORE")]),
    ("code2", "SECURITY", [("f07","SANDBOX"),("f08","MEMWIPE"),("f09","AUTH"),
        ("f10","PROCMON"),("f11","AUDIT"),("f12","LOCK")]),
    ("code3", "UI / CLOUD", [("f13","DRIVE"),("f14","DASHBOARD"),("f15","FILEMGR"),
        ("f16","SYNC"),("f17","CONFIG"),("f18","THREADS")]),
]
gh = F("JetBrainsMono-Bold.ttf", s(22))
gs = F("JetBrainsMono-Regular.ttf", s(19))
gc = F("DMMono-Regular.ttf", s(19))
colw = (W - 2*M)//3
for i,(code,name,items) in enumerate(groups):
    gx = M + i*colw
    d.text((s(gx), s(ly)), code, font=gh, fill=INK, anchor="lm")
    d.text((s(gx+150), s(ly)), name, font=gs, fill=AMBER, anchor="lm")
    d.line([s(gx), s(ly+26), s(gx+colw-60), s(ly+26)], fill=INK2, width=SS)
    for j,(fc,fn) in enumerate(items):
        ry = ly + 64 + j*42
        d.text((s(gx), s(ry)), fc, font=gc, fill=INK, anchor="lm")
        d.text((s(gx+90), s(ry)), fn, font=gs, fill=HEXF, anchor="lm")
        # tiny status cell
        d.rectangle([s(gx+colw-92), s(ry-8), s(gx+colw-78), s(ry+6)],
                    fill=INK if j%5 else AMBER)

# ---- footer ----------------------------------------------------------------
d.line([s(M), s(H-150), s(W-M), s(H-150)], fill=INK, width=SS)
ft = F("JetBrainsMono-Regular.ttf", s(18))
d.text((s(M), s(H-118)), "SMART FILE FORTIFY SYSTEM", font=ft, fill=INK, anchor="lm")
d.text((s(W/2), s(H-118)), "PYTHON 3.11 · PyQt6 · AES-256 · ARGON2id",
       font=ft, fill=HEXF, anchor="mm")
d.text((s(W-M), s(H-118)), "ORDER IS THE ONLY FORTIFICATION", font=ft, fill=AMBER, anchor="rm")

# ---- finish ----------------------------------------------------------------
out = img.resize((W, H), Image.LANCZOS)
out.save(r"C:/Users/iblfe/Documents/collage/gp2/test/docs/presentations/SFFS-poster.png")
print("saved")
