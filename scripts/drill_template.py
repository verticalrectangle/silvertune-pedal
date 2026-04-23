#!/usr/bin/env python3
"""
Silvertune Pedal — Drill Template (125B enclosure face)
Run: python3 scripts/drill_template.py
Output: drill-template.png

Print at EXACTLY 100% scale (no fit-to-page).
Verify the scale bar measures 50mm before drilling.
Cut out the face rectangle and tape to enclosure.
Center-punch each crosshair, then drill.
"""

import cairo
import math
import os

OUTPUT = os.path.join(os.path.dirname(__file__), '..', 'drill-template.png')

# ─── Scale ────────────────────────────────────────────────────────────────────
DPI = 300
MM  = DPI / 25.4   # pixels per mm at 300 DPI = 11.81

# 125B face dimensions
FACE_W_MM = 122.0
FACE_H_MM = 66.0

MARGIN_MM       = 20.0   # left/top/bottom margin
RIGHT_MARGIN_MM = 90.0   # extra space for drill size legend

# Canvas height: title + face + gap + top-edge section + scale bar + bottom margin
H_TOTAL_MM = MARGIN_MM + 18 + FACE_H_MM + 18 + 22 + 12 + MARGIN_MM

W = int((FACE_W_MM + MARGIN_MM + RIGHT_MARGIN_MM) * MM)
H = int(H_TOTAL_MM * MM)

# Face origin in pixels
FX = int(MARGIN_MM * MM)
FY = int(MARGIN_MM * MM)
FW = int(FACE_W_MM * MM)
FH = int(FACE_H_MM * MM)

# ─── Hole positions (mm from top-left of face) ────────────────────────────────
# Adjust these to move holes on the physical enclosure

# Knobs — 2x2 grid on right side
KNOB_DIAM_MM = 7.0   # 7mm = slightly over 1/4"
KNOBS = [
    (77,  20, 'KEY'),
    (104, 20, 'SCALE'),
    (77,  48, 'MIX'),
    (104, 48, 'TUNE'),
]

# OLED rectangular slot
# 0.96" SSD1306 128x64: PCB ~27x27mm, screen window ~24x13mm
OLED_X_MM  = 8.0
OLED_Y_MM  = 13.0
OLED_W_MM  = 24.0
OLED_H_MM  = 13.0

# OLED M2 mounting holes
# 0.96" SSD1306 PCB is ~27x27mm with M2 holes ~1.5mm from each corner.
M2_DIAM_MM = 3.2   # M3 clearance hole
OLED_PCB_W = 27.0
OLED_PCB_H = 27.0
_ox = OLED_X_MM + (OLED_W_MM - OLED_PCB_W) / 2  # PCB left edge
_oy = OLED_Y_MM + (OLED_H_MM - OLED_PCB_H) / 2  # PCB top edge
OLED_M2_HOLES = [
    (_ox + 2,            _oy + 2,            'M2'),
    (_ox + OLED_PCB_W-2, _oy + 2,            'M2'),
    (_ox + 2,            _oy + OLED_PCB_H-2, 'M2'),
    (_ox + OLED_PCB_W-2, _oy + OLED_PCB_H-2, 'M2'),
]

# LED
LED_X_MM   = 53.0
LED_Y_MM   = 23.0
LED_DIAM   = 5.0    # 5mm LED

# Footswitch
FS_X_MM    = 31.0
FS_Y_MM    = 49.0
FS_DIAM_MM = 12.0   # 12mm / ~1/2"

# Top edge jacks (on the 66mm tall edge — drill through the top edge)
# These are separate — use the top edge section of the enclosure
TOP_JACKS = [
    (27,  'IN',    9.0),
    (61,  '9V DC', 7.0),
    (95,  'OUT',   9.0),
]

# ─── Helpers ──────────────────────────────────────────────────────────────────
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
ctx = cairo.Context(surface)

def col(r, g, b, a=1.0):
    ctx.set_source_rgba(r, g, b, a)

def black(a=1.0):  col(0, 0, 0, a)
def red(a=1.0):    col(0.8, 0, 0, a)
def blue(a=1.0):   col(0, 0, 0.7, a)
def gray(a=1.0):   col(0.5, 0.5, 0.5, a)

def mm(v):
    """Convert mm to pixels."""
    return v * MM

def px(x_mm, y_mm):
    """Face-relative mm coords to pixel coords."""
    return FX + x_mm * MM, FY + y_mm * MM

def crosshair(cx, cy, r_mm=3.0):
    """Draw a crosshair + circle at pixel coords cx, cy."""
    r = mm(r_mm)
    ctx.set_line_width(0.5)
    ctx.move_to(cx - r * 1.6, cy); ctx.line_to(cx + r * 1.6, cy); ctx.stroke()
    ctx.move_to(cx, cy - r * 1.6); ctx.line_to(cx, cy + r * 1.6); ctx.stroke()
    ctx.arc(cx, cy, r, 0, 2 * math.pi); ctx.stroke()

def drill_hole(x_mm, y_mm, diam_mm, label=''):
    cx, cy = px(x_mm, y_mm)
    black()
    crosshair(cx, cy, diam_mm / 2)
    # Drill diameter circle (actual size)
    ctx.set_line_width(1.0)
    ctx.arc(cx, cy, mm(diam_mm / 2), 0, 2 * math.pi); ctx.stroke()
    if label:
        ctx.select_font_face("Helvetica", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(mm(2.8))
        te = ctx.text_extents(label)
        ctx.move_to(cx - te.width/2, cy + mm(diam_mm/2) + mm(3.5))
        ctx.show_text(label)

def oled_slot(x_mm, y_mm, w_mm, h_mm):
    """Draw OLED rectangular cutout with corner drill guides."""
    x, y = px(x_mm, y_mm)
    w, h = mm(w_mm), mm(h_mm)
    # Outline
    black()
    ctx.set_line_width(1.5)
    ctx.set_dash([mm(2), mm(1)])
    ctx.rectangle(x, y, w, h); ctx.stroke()
    ctx.set_dash([])
    # Corner crosshairs (drill corners, then file to rectangle)
    r = mm(2.5)
    for cx, cy in [(x, y), (x+w, y), (x, y+h), (x+w, y+h)]:
        crosshair(cx, cy, 1.5)
    # Label
    ctx.select_font_face("Helvetica", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(mm(2.8))
    te = ctx.text_extents('OLED SLOT')
    ctx.move_to(x + w/2 - te.width/2, y + h/2 + mm(1.2))
    ctx.show_text('OLED SLOT')
    ctx.set_font_size(mm(2.2))
    te2 = ctx.text_extents('drill corners, file to rectangle')
    ctx.move_to(x + w/2 - te2.width/2, y + h + mm(3.5))
    ctx.show_text('drill corners, file to rectangle')

def txt(s, x, y, size_mm=3.0, anchor='left'):
    black()
    ctx.select_font_face("Helvetica", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(mm(size_mm))
    te = ctx.text_extents(s)
    if anchor == 'center': x -= te.width / 2
    elif anchor == 'right': x -= te.width
    ctx.move_to(x, y); ctx.show_text(s)

# ─── Draw ─────────────────────────────────────────────────────────────────────

# White background
col(1, 1, 1); ctx.paint()

# Title
txt('SILVERTUNE PEDAL — DRILL TEMPLATE', W/2, mm(10), 4.5, 'center')
txt('Print at 100% scale. Do NOT scale to fit page.', W/2, mm(15), 3.0, 'center')

# Face outline (cut line)
black()
ctx.set_line_width(1.5)
ctx.rectangle(FX, FY, FW, FH)
ctx.stroke()

# Face label
gray()
ctx.set_line_width(0.5)
ctx.set_dash([mm(1), mm(1)])
ctx.rectangle(FX, FY, FW, FH)
ctx.stroke()
ctx.set_dash([])
gray()
txt(f'125B FACE  {FACE_W_MM:.0f}mm × {FACE_H_MM:.0f}mm', FX + mm(1), FY - mm(3), 2.5)

# ── Front face holes ──────────────────────────────────────────────────────────

# OLED slot
oled_slot(OLED_X_MM, OLED_Y_MM, OLED_W_MM, OLED_H_MM)

# OLED M2 mounting holes
for hx, hy, _ in OLED_M2_HOLES:
    cx, cy = px(hx, hy)
    black()
    ctx.set_line_width(0.8)
    crosshair(cx, cy, M2_DIAM_MM / 2)
    ctx.arc(cx, cy, mm(M2_DIAM_MM / 2), 0, 2 * math.pi); ctx.stroke()
# Label once
lx, ly = px(OLED_X_MM + OLED_W_MM + 1, OLED_Y_MM + OLED_H_MM + 6)
txt('M2 holes — verify against your module', lx, ly, 2.2)

# LED
black()
drill_hole(LED_X_MM, LED_Y_MM, LED_DIAM, f'LED  ⌀{LED_DIAM:.0f}mm')

# Knobs
for kx, ky, label in KNOBS:
    drill_hole(kx, ky, KNOB_DIAM_MM, f'{label}  ⌀{KNOB_DIAM_MM:.0f}mm')

# Footswitch
drill_hole(FS_X_MM, FS_Y_MM, FS_DIAM_MM, f'BYPASS  ⌀{FS_DIAM_MM:.0f}mm')

# ── Top edge jacks (separate section below) ───────────────────────────────────
EDGE_Y_OFFSET = FACE_H_MM + MARGIN_MM * 1.2 + 5

# Draw top edge outline
TE_X = FX
TE_Y = FY + FH + int(mm(MARGIN_MM * 0.8))
TE_W = FW
TE_H = int(mm(20))   # top edge is ~20mm tall

black()
ctx.set_line_width(1.5)
ctx.rectangle(TE_X, TE_Y, TE_W, TE_H)
ctx.stroke()
gray()
txt('TOP EDGE  (drill through narrow edge)', TE_X + mm(1), TE_Y - mm(3), 2.5)

for jx_mm, label, diam in TOP_JACKS:
    cx = TE_X + mm(jx_mm)
    cy = TE_Y + TE_H / 2
    black()
    crosshair(cx, cy, diam / 2)
    ctx.set_line_width(1.0)
    ctx.arc(cx, cy, mm(diam / 2), 0, 2 * math.pi); ctx.stroke()
    ctx.select_font_face("Helvetica", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(mm(2.8))
    te = ctx.text_extents(f'{label}  ⌀{diam:.0f}mm')
    ctx.move_to(cx - te.width/2, cy + mm(diam/2) + mm(4))
    ctx.show_text(f'{label}  ⌀{diam:.0f}mm')

# ── Scale verification bar ────────────────────────────────────────────────────
BAR_X = FX
BAR_Y = H - int(mm(12))
BAR_LEN = mm(50)

black()
ctx.set_line_width(1.2)
ctx.move_to(BAR_X, BAR_Y); ctx.line_to(BAR_X + BAR_LEN, BAR_Y); ctx.stroke()
ctx.move_to(BAR_X, BAR_Y - mm(1.5)); ctx.line_to(BAR_X, BAR_Y + mm(1.5)); ctx.stroke()
ctx.move_to(BAR_X + BAR_LEN, BAR_Y - mm(1.5))
ctx.line_to(BAR_X + BAR_LEN, BAR_Y + mm(1.5)); ctx.stroke()
txt('← 50mm — verify this before drilling →', BAR_X, BAR_Y - mm(3), 2.8)

# ── Drill size legend ─────────────────────────────────────────────────────────
LX = FX + FW + mm(5)
LY = FY + mm(5)
txt('DRILL SIZES', LX, LY, 3.2)
sizes = [
    ('Knobs',       f'⌀{KNOB_DIAM_MM:.0f}mm  (7/32")'),
    ('Jacks IN/OUT',f'⌀9mm   (3/8")'),
    ('DC Jack',     f'⌀7mm   (9/32")'),
    ('LED',         f'⌀{LED_DIAM:.0f}mm   (3/16")'),
    ('Footswitch',  f'⌀{FS_DIAM_MM:.0f}mm  (1/2")'),
    ('OLED',        'drill corners + file'),
    ('OLED mount',  'M3  (3.2mm clearance)'),
]
for i, (part, size) in enumerate(sizes):
    gray()
    txt(part,  LX,        LY + mm(7 + i*8), 2.5)
    black()
    txt(size,  LX,        LY + mm(11 + i*8), 2.8)

# ─── Save ─────────────────────────────────────────────────────────────────────
surface.write_to_png(OUTPUT)
print(f"Saved to {OUTPUT}")
print(f"Canvas: {W}x{H}px at {DPI}DPI")
print(f"Face:   {FACE_W_MM}x{FACE_H_MM}mm")
print("Print at 100% — do not scale to fit page!")
