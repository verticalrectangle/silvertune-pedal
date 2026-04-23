#!/usr/bin/env python3
"""
Silvertune Pedal — Board Layout (ElectroCookie 52.1x88.9mm)
Run: python3 scripts/board_layout.py
Output: board-layout.png

ElectroCookie breadboard-style PCB:
  - 52.1mm x 88.9mm, black/gold (rendered in light theme)
  - Left power rails: − (outer) and + (inner)
  - Main grid: columns A–E | center gap | F–J  (30 rows, 5-pin connected rows)
  - Right power rails: + (inner) and − (outer)
  - 4 corner mounting holes
"""

import cairo
import math
import os

OUTPUT = os.path.join(os.path.dirname(__file__), '..', 'board-layout.png')

# ─── Scale ────────────────────────────────────────────────────────────────────
PX_PER_MM = 14.0

PCB_W_MM = 52.1
PCB_H_MM = 88.9

LEFT_MARGIN_MM  = 48.0   # room for off-board labels
RIGHT_MARGIN_MM = 16.0
LEGEND_MM       = 76.0

MARGIN_MM = LEFT_MARGIN_MM   # used by PCB_X

W = int((PCB_W_MM + LEFT_MARGIN_MM + RIGHT_MARGIN_MM + LEGEND_MM) * PX_PER_MM)
H = int((PCB_H_MM + LEFT_MARGIN_MM * 0.5 + 36) * PX_PER_MM)

def mm(v):
    return v * PX_PER_MM

PCB_X = mm(LEFT_MARGIN_MM)
PCB_Y = mm(20 + 16)

# ─── Grid geometry ────────────────────────────────────────────────────────────
ROWS    = 30
PAD_MM  = 2.54       # 0.1" standard

# Power rail positions (mm from PCB left edge)
RAIL_L_NEG_X = 3.0        # left  −
RAIL_L_POS_X = 5.54       # left  +
RAIL_R_POS_X = 43.56      # right +
RAIL_R_NEG_X = 46.10      # right −

# Main grid: col A starts at 9.5mm, 2.54mm apart, center gap of 5.08mm after col E
COL_A_X  = 9.5
CENTER_GAP_MM = 5.08

def col_x_mm(ci):
    """ci 0=A .. 9=J"""
    if ci < 5:
        return COL_A_X + ci * PAD_MM
    else:
        return COL_A_X + ci * PAD_MM + CENTER_GAP_MM

ROW_TOP_MM = 5.5

def row_y_mm(ri):
    return ROW_TOP_MM + ri * PAD_MM

def pcb_pt(x_mm, y_mm):
    return PCB_X + mm(x_mm), PCB_Y + mm(y_mm)

def pad_pt(ci, ri):
    return pcb_pt(col_x_mm(ci), row_y_mm(ri))

def rail_pt(rail_x, ri):
    return pcb_pt(rail_x, row_y_mm(ri))

# ─── Daisy Seed placement ─────────────────────────────────────────────────────
# Straddles center gap: col E (idx 4) and col F (idx 5), rows 5–24
DS_START = 5
DS_END   = 24   # inclusive (20 rows = 20 pins per side)

# Left side  (col E = idx 4): pins 1–20
DS_LEFT = [
    ('D30', '3V3 IN',     False),  # pin 1
    ('D29', '',           False),
    ('D28', '',           False),
    ('D27', '',           False),
    ('D26', '',           False),
    ('D25', '← FOOTSW',  True),   # pin 6
    ('D24', '',           False),
    ('D23', '',           False),
    ('D22', '← LED',     True),   # pin 9
    ('D21', '',           False),
    ('D20', '',           False),
    ('D11', '→ SCL',     True),   # pin 12
    ('D12', '→ SDA',     True),   # pin 13
    ('D13', '',           False),
    ('D14', '',           False),
    ('',    'AUDIO IN L', True),   # pin 16
    ('D10', '',           False),
    ('',    'AUDIO OUT L',True),   # pin 18
    ('D9',  '',           False),
    ('',    'AGND',       True),   # pin 20
]

# Right side (col F = idx 5): pins 21–40
DS_RIGHT = [
    ('',    'GND',        True),   # pin 21
    ('A0',  '← K1 KEY',  True),   # pin 22
    ('A1',  '← K2 SCL',  True),   # pin 23
    ('A2',  '← K3 MIX',  True),   # pin 24
    ('A3',  '← K4 TUNE', True),   # pin 25
    ('A4',  '',           False),
    ('A5',  '',           False),
    ('A6',  '',           False),
    ('A7',  '',           False),
    ('A8',  '',           False),
    ('A9',  '',           False),
    ('A10', '',           False),
    ('A11', '',           False),
    ('D6',  '',           False),
    ('D5',  '',           False),
    ('D4',  '',           False),
    ('D3',  '',           False),
    ('',    '3V3 OUT',    True),   # pin 38
    ('',    'VIN',        True),   # pin 39
    ('',    'DGND',       True),   # pin 40
]

# ─── Cairo setup ──────────────────────────────────────────────────────────────
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
ctx = cairo.Context(surface)

def from_hex(h):
    h = h.lstrip('#')
    return int(h[0:2],16)/255, int(h[2:4],16)/255, int(h[4:6],16)/255

def col(spec, a=1.0):
    if isinstance(spec, str):
        r,g,b = from_hex(spec)
        ctx.set_source_rgba(r,g,b,a)
    else:
        ctx.set_source_rgba(*spec, a)

def rrect(x, y, w, h, r=4):
    ctx.new_sub_path()
    ctx.arc(x+w-r, y+r,   r, -math.pi/2, 0)
    ctx.arc(x+w-r, y+h-r, r,  0,          math.pi/2)
    ctx.arc(x+r,   y+h-r, r,  math.pi/2,  math.pi)
    ctx.arc(x+r,   y+r,   r,  math.pi,    3*math.pi/2)
    ctx.close_path()

def circ(x, y, r):
    ctx.arc(x, y, r, 0, 2*math.pi)

def txt(s, x, y, size_mm=2.5, anchor='left', bold=False, color='#333333'):
    col(color)
    ctx.select_font_face("Monospace", cairo.FONT_SLANT_NORMAL,
        cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(mm(size_mm))
    te = ctx.text_extents(s)
    if anchor == 'center': x -= te.width / 2
    elif anchor == 'right': x -= te.width
    ctx.move_to(x, y)
    ctx.show_text(s)

def wire(pts, color, width_mm=0.5):
    col(color)
    ctx.set_line_width(mm(width_mm))
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.stroke()

# ─── Wire colors (adjusted for light theme) ───────────────────────────────────
WIRE_GND  = '#888888'
WIRE_3V3  = '#cc3333'
WIRE_ADC  = '#2255bb'
WIRE_I2C  = '#009988'
WIRE_AOUT = '#bb2222'
WIRE_AIN  = '#228833'
WIRE_LED  = '#cc6600'
WIRE_FS   = '#997700'

# ─── Background ───────────────────────────────────────────────────────────────
col('#f2f0ed'); ctx.paint()

txt('SILVERTUNE PEDAL — BOARD LAYOUT', W/2, mm(9), 4.0, 'center', True, '#333333')
txt('ElectroCookie 52.1×88.9mm  ·  Daisy Seed rows 6–25  ·  straddles center gap',
    W/2, mm(14.5), 2.4, 'center', False, '#888888')

# ─── PCB body ─────────────────────────────────────────────────────────────────
col('#d4e8d4')
rrect(PCB_X, PCB_Y, mm(PCB_W_MM), mm(PCB_H_MM), mm(2)); ctx.fill()
col('#5a9a5a'); ctx.set_line_width(mm(0.6))
rrect(PCB_X, PCB_Y, mm(PCB_W_MM), mm(PCB_H_MM), mm(2)); ctx.stroke()

# Corner mounting holes
for hx, hy in [(3.2, 3.2), (PCB_W_MM-3.2, 3.2),
               (3.2, PCB_H_MM-3.2), (PCB_W_MM-3.2, PCB_H_MM-3.2)]:
    px, py = pcb_pt(hx, hy)
    col('#f2f0ed'); circ(px, py, mm(1.5)); ctx.fill()
    col('#5a9a5a'); ctx.set_line_width(mm(0.3)); circ(px, py, mm(1.5)); ctx.stroke()

# ─── Power rail strips ────────────────────────────────────────────────────────
RAIL_H  = mm(PCB_H_MM - 7)
RAIL_Y  = PCB_Y + mm(3.5)
PAD_R   = mm(0.55)

def draw_rail_strip(x_mm, color_fill, color_border, label, label_color):
    sx = PCB_X + mm(x_mm) - mm(1.1)
    col(color_fill); ctx.rectangle(sx, RAIL_Y, mm(2.2), RAIL_H); ctx.fill()
    col(color_border); ctx.set_line_width(mm(0.2))
    ctx.rectangle(sx, RAIL_Y, mm(2.2), RAIL_H); ctx.stroke()
    ctx.save()
    ctx.translate(PCB_X + mm(x_mm), RAIL_Y + RAIL_H/2)
    ctx.rotate(-math.pi/2)
    txt(label, 0, 0, 1.8, 'center', True, label_color)
    ctx.restore()

draw_rail_strip(RAIL_L_NEG_X, '#ddeedd', '#88aa88', '−', '#446644')
draw_rail_strip(RAIL_L_POS_X, '#fde8e8', '#cc8888', '+', '#993333')
draw_rail_strip(RAIL_R_POS_X, '#fde8e8', '#cc8888', '+', '#993333')
draw_rail_strip(RAIL_R_NEG_X, '#ddeedd', '#88aa88', '−', '#446644')

# Rail pads
for ri in range(ROWS):
    for rx in [RAIL_L_NEG_X, RAIL_L_POS_X, RAIL_R_POS_X, RAIL_R_NEG_X]:
        px, py = rail_pt(rx, ri)
        col('#c8a800'); circ(px, py, PAD_R); ctx.fill()
        col('#a88800', 0.7); ctx.set_line_width(mm(0.12)); circ(px, py, PAD_R); ctx.stroke()

# Rail labels at top and bottom
for rx, sym in [(RAIL_L_NEG_X, '−'), (RAIL_L_POS_X, '+'),
                (RAIL_R_POS_X, '+'), (RAIL_R_NEG_X, '−')]:
    px = PCB_X + mm(rx)
    c = '#cc3333' if sym == '+' else '#446644'
    txt(sym, px, PCB_Y + mm(2.6), 2.0, 'center', True, c)
    txt(sym, px, PCB_Y + mm(PCB_H_MM - 1.0), 2.0, 'center', True, c)

# ─── Column labels and main pads ──────────────────────────────────────────────
COLS_LBL = list('ABCDEFGHIJ')

for ci in range(10):
    cx = PCB_X + mm(col_x_mm(ci))
    txt(COLS_LBL[ci], cx, PCB_Y + mm(2.6),             1.9, 'center', False, '#555555')
    txt(COLS_LBL[ci], cx, PCB_Y + mm(PCB_H_MM - 1.0),  1.9, 'center', False, '#555555')

for ri in range(ROWS):
    ry = PCB_Y + mm(row_y_mm(ri))
    s  = str(ri + 1)
    # Row numbers between left rails and col A
    txt(s, PCB_X + mm((RAIL_L_POS_X + col_x_mm(0))/2), ry + mm(0.5), 1.5, 'center', False, '#777777')
    # Row numbers between col J and right rails
    txt(s, PCB_X + mm((col_x_mm(9) + RAIL_R_POS_X)/2), ry + mm(0.5), 1.5, 'center', False, '#777777')

for ri in range(ROWS):
    for ci in range(10):
        px, py = pad_pt(ci, ri)
        # Daisy Seed pins: slightly highlighted
        if DS_START <= ri <= DS_END and ci in (4, 5):
            col('#b8e0b8'); circ(px, py, PAD_R); ctx.fill()
            col('#5a9a5a'); ctx.set_line_width(mm(0.15)); circ(px, py, PAD_R); ctx.stroke()
        else:
            col('#c8a800'); circ(px, py, PAD_R); ctx.fill()
            col('#a88800', 0.7); ctx.set_line_width(mm(0.12)); circ(px, py, PAD_R); ctx.stroke()

# ─── Daisy Seed body ──────────────────────────────────────────────────────────
ex0, ey0 = pad_pt(4, DS_START)
ex1, ey1 = pad_pt(5, DS_END)
pad_off  = mm(PAD_MM * 0.5)

SEED_X = ex0 - pad_off
SEED_Y = ey0 - pad_off
SEED_W = (ex1 - ex0) + pad_off * 2
SEED_H = (ey1 - ey0) + pad_off * 2

col('#1a3060'); rrect(SEED_X, SEED_Y, SEED_W, SEED_H, mm(1.2)); ctx.fill()
col('#3a5aaa'); ctx.set_line_width(mm(0.5))
rrect(SEED_X, SEED_Y, SEED_W, SEED_H, mm(1.2)); ctx.stroke()
txt('DAISY', SEED_X + SEED_W/2, SEED_Y + SEED_H/2 - mm(1.5), 2.2, 'center', True, '#8ab4ff')
txt('SEED',  SEED_X + SEED_W/2, SEED_Y + SEED_H/2 + mm(1.2), 2.2, 'center', True, '#8ab4ff')

# ─── Pin labels ───────────────────────────────────────────────────────────────
# Left side (col E, labels go rightward from col D toward left)
lbl_x = ex0 - mm(1.4)
PIN_COLOR = {
    'D25': WIRE_FS,   'D22': WIRE_LED,
    'D11': WIRE_I2C,  'D12': WIRE_I2C,
    'AUDIO IN L': WIRE_AIN, 'AUDIO OUT L': WIRE_AOUT,
    'AGND': WIRE_GND,
}
for i, (pin, note, highlight) in enumerate(DS_LEFT):
    ri = DS_START + i
    _, cy = pad_pt(4, ri)
    if not highlight:
        s = pin
        c = '#aaaaaa'
    else:
        s = pin if not note else (f'{pin} {note}' if pin else note)
        c = PIN_COLOR.get(pin, PIN_COLOR.get(note, '#444444'))
    txt(s, lbl_x, cy + mm(0.5), 1.55, 'right', highlight, c)

# Right side (col F, labels extend right)
rbl_x = ex1 + mm(1.4)
for i, (pin, note, highlight) in enumerate(DS_RIGHT):
    ri = DS_START + i
    _, cy = pad_pt(5, ri)
    if not highlight:
        s = pin
        c = '#aaaaaa'
    else:
        s = pin if not note else (f'{pin} {note}' if pin else note)
        c = PIN_COLOR.get(pin, PIN_COLOR.get(note.split()[0] if note else '', '#444444'))
        if '3V3' in note or 'VIN' in note:
            c = WIRE_3V3
        elif 'GND' in note or 'GND' in pin:
            c = WIRE_GND
        elif 'K1' in note: c = WIRE_ADC
        elif 'K2' in note: c = WIRE_ADC
        elif 'K3' in note: c = WIRE_ADC
        elif 'K4' in note: c = WIRE_ADC
    txt(s, rbl_x, cy + mm(0.5), 1.55, 'left', highlight, c)

# ─── Wires ────────────────────────────────────────────────────────────────────

def pp(ci, ri): return pad_pt(ci, ri)
def rp(rx, ri): return rail_pt(rx, ri)

# AGND (left pin row 19) → left − rail
wire([pp(4, DS_START+19), pp(3, DS_START+19), pp(2, DS_START+19),
      rp(RAIL_L_NEG_X, DS_START+19)], WIRE_GND, 0.45)

# DGND (right pin row 19) → right − rail
wire([pp(5, DS_START+19), pp(6, DS_START+19),
      rp(RAIL_R_NEG_X, DS_START+19)], WIRE_GND, 0.45)

# 3V3 OUT (right pin row 17) → left + rail (routed across bottom)
p5r17 = pp(5, DS_START+17)
bot_y  = PCB_Y + mm(PCB_H_MM - 3.0)
wire([p5r17,
      (p5r17[0] + mm(4), p5r17[1]),
      (p5r17[0] + mm(4), bot_y),
      (PCB_X + mm(RAIL_L_POS_X), bot_y),
      rp(RAIL_L_POS_X, ROWS-1)], WIRE_3V3, 0.45)

# VIN (right pin row 18) to off-board (arrow only — DC jack goes off-board)
p5r18 = pp(5, DS_START+18)
wire([p5r18, (p5r18[0] + mm(3), p5r18[1])], WIRE_3V3, 0.45)

# ADC: A0-A3 (right col F rows 1-4) → col H (right side, connection points)
for k in range(4):
    ri = DS_START + 1 + k
    wire([pp(5, ri), pp(7, ri)], WIRE_ADC, 0.45)

# I2C: SCL D11 / SDA D12 → col C
wire([pp(4, DS_START+11), pp(3, DS_START+11), pp(2, DS_START+11)], WIRE_I2C, 0.45)
wire([pp(4, DS_START+12), pp(3, DS_START+12), pp(2, DS_START+12)], WIRE_I2C, 0.45)

# LED D22 → col C
wire([pp(4, DS_START+8), pp(3, DS_START+8), pp(2, DS_START+8)], WIRE_LED, 0.45)

# Footswitch D25 → col C
wire([pp(4, DS_START+5), pp(3, DS_START+5), pp(2, DS_START+5)], WIRE_FS, 0.45)

# Audio IN → col C
wire([pp(4, DS_START+15), pp(3, DS_START+15), pp(2, DS_START+15)], WIRE_AIN, 0.45)

# Audio OUT → col C
wire([pp(4, DS_START+17), pp(3, DS_START+17), pp(2, DS_START+17)], WIRE_AOUT, 0.45)

# Highlight connection pads with ring
RINGS = [
    (2, DS_START+11, WIRE_I2C),
    (2, DS_START+12, WIRE_I2C),
    (2, DS_START+8,  WIRE_LED),
    (2, DS_START+5,  WIRE_FS),
    (2, DS_START+15, WIRE_AIN),
    (2, DS_START+17, WIRE_AOUT),
    (7, DS_START+1,  WIRE_ADC),
    (7, DS_START+2,  WIRE_ADC),
    (7, DS_START+3,  WIRE_ADC),
    (7, DS_START+4,  WIRE_ADC),
]
for ci, ri, c in RINGS:
    px, py = pad_pt(ci, ri)
    col(c); ctx.set_line_width(mm(0.4)); circ(px, py, PAD_R + mm(0.5)); ctx.stroke()

# ─── Off-board connection labels (right side of right rails) ──────────────────
RX_LBL = PCB_X + mm(RAIL_R_NEG_X) + mm(2.0)
ADC_LABELS = ['K1 KEY wiper', 'K2 SCALE wiper', 'K3 MIX wiper', 'K4 TUNE wiper']
for k, label in enumerate(ADC_LABELS):
    _, cy = pad_pt(7, DS_START + 1 + k)
    txt(f'→ {label}', RX_LBL, cy + mm(0.5), 1.8, 'left', False, WIRE_ADC)

# Left off-board labels
LX_LBL = PCB_X - mm(1.5)
LEFT_OB = {
    DS_START+11: ('← OLED SCL',   WIRE_I2C),
    DS_START+12: ('← OLED SDA',   WIRE_I2C),
    DS_START+8:  ('← LED + 470Ω', WIRE_LED),
    DS_START+5:  ('← FOOTSW',     WIRE_FS),
    DS_START+15: ('← IN jack',    WIRE_AIN),
    DS_START+17: ('← OUT jack',   WIRE_AOUT),
}
for ri, (label, c) in LEFT_OB.items():
    _, cy = pad_pt(2, ri)
    txt(label, LX_LBL, cy + mm(0.5), 1.8, 'right', False, c)

# ─── Legend panel ─────────────────────────────────────────────────────────────
LX = PCB_X + mm(PCB_W_MM) + mm(28)   # push right of the off-board labels
LY = PCB_Y

col('#ffffff', 0.92)
rrect(LX - mm(3), LY - mm(1), mm(LEGEND_MM - 18), mm(PCB_H_MM + 2), mm(2)); ctx.fill()
col('#cccccc'); ctx.set_line_width(mm(0.3))
rrect(LX - mm(3), LY - mm(1), mm(LEGEND_MM - 18), mm(PCB_H_MM + 2), mm(2)); ctx.stroke()

txt('CONNECTIONS', LX + mm(25), LY + mm(5), 3.0, 'center', True, '#333333')

LEGEND_ITEMS = [
    (WIRE_3V3,  '3V3 / Power'),
    (WIRE_GND,  'GND'),
    (WIRE_ADC,  'ADC pot wipers (A0–A3)'),
    (WIRE_I2C,  'I2C OLED (D11 SCL, D12 SDA)'),
    (WIRE_AIN,  'Audio IN L'),
    (WIRE_AOUT, 'Audio OUT L'),
    (WIRE_LED,  'LED signal (D22 → 470Ω)'),
    (WIRE_FS,   'Footswitch (D25 → GND)'),
]
for i, (lc, ll) in enumerate(LEGEND_ITEMS):
    lry = LY + mm(10 + i * 7)
    col(lc); ctx.set_line_width(mm(0.9))
    ctx.move_to(LX, lry); ctx.line_to(LX + mm(8), lry); ctx.stroke()
    txt(ll, LX + mm(10), lry + mm(0.6), 2.3, 'left', False, '#333333')

# ─── Pin summary table ────────────────────────────────────────────────────────
TY = LY + mm(68)
txt('PIN SUMMARY', LX, TY, 2.8, 'left', True, '#333333')

PIN_TABLE = [
    ('D11  pin 12', 'OLED SCL',         WIRE_I2C),
    ('D12  pin 13', 'OLED SDA',         WIRE_I2C),
    ('D22  pin 29', 'LED + 470Ω',       WIRE_LED),
    ('D25  pin 32', 'Footswitch pin 1', WIRE_FS),
    ('A0   pin 22', 'K1 KEY wiper',     WIRE_ADC),
    ('A1   pin 23', 'K2 SCALE wiper',   WIRE_ADC),
    ('A2   pin 24', 'K3 MIX wiper',     WIRE_ADC),
    ('A3   pin 25', 'K4 TUNE wiper',    WIRE_ADC),
    ('AUDIO IN L  pin 16',  'Input jack tip',  WIRE_AIN),
    ('AUDIO OUT L pin 18', 'Output jack tip', WIRE_AOUT),
    ('AGND  pin 20', '→ left − rail',  WIRE_GND),
    ('DGND  pin 40', '→ right − rail', WIRE_GND),
    ('3V3 OUT pin 38', '→ left + rail', WIRE_3V3),
    ('VIN     pin 39', '← DC jack +',  WIRE_3V3),
]

for i, (pin, dest, c) in enumerate(PIN_TABLE):
    ty = TY + mm(6 + i * 5.3)
    col(c, 0.15); rrect(LX - mm(0.5), ty - mm(3.5), mm(52), mm(4.4), mm(0.4)); ctx.fill()
    col(c); ctx.set_line_width(mm(0.25))
    rrect(LX - mm(0.5), ty - mm(3.5), mm(52), mm(4.4), mm(0.4)); ctx.stroke()
    txt(pin,  LX + mm(0.5), ty, 1.9, 'left',  True,  '#333333')
    txt(dest, LX + mm(26),  ty, 1.9, 'left',  False, '#555555')

# ─── Save ─────────────────────────────────────────────────────────────────────
surface.write_to_png(OUTPUT)
print(f"Saved to {OUTPUT}")
print(f"Canvas: {W}x{H}px")
print(f"PCB: {PCB_W_MM}x{PCB_H_MM}mm")
