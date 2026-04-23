#!/usr/bin/env python3
"""
Silvertune Pedal — Pedal Face Mockup Generator
Run: python3 scripts/pedal_mockup.py
Output: pedal-mockup.png
"""

import cairo
import math
import os

OUTPUT = os.path.join(os.path.dirname(__file__), '..', 'pedal-mockup.png')

# ─── Canvas size ──────────────────────────────────────────────────────────────
# 125B enclosure: 122mm x 66mm face
MM     = 11        # pixels per mm — increase for higher DPI
EW     = int(122 * MM)
EH     = int(66  * MM)
PAD    = 60
TOP_H  = 110       # top edge section height (shows jacks)

W = EW + PAD * 2
H = EH + PAD * 2 + TOP_H + 40

# ─── Helpers ──────────────────────────────────────────────────────────────────

def from_hex(h):
    h = h.lstrip('#')
    return int(h[0:2],16)/255, int(h[2:4],16)/255, int(h[4:6],16)/255

surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
ctx = cairo.Context(surface)

def col(h, a=1.0):
    r,g,b = from_hex(h)
    ctx.set_source_rgba(r,g,b,a)

def rrect(x, y, w, h, r=8):
    ctx.new_sub_path()
    ctx.arc(x+w-r, y+r, r, -math.pi/2, 0)
    ctx.arc(x+w-r, y+h-r, r, 0, math.pi/2)
    ctx.arc(x+r, y+h-r, r, math.pi/2, math.pi)
    ctx.arc(x+r, y+r, r, math.pi, 3*math.pi/2)
    ctx.close_path()

def circ(x, y, r):
    ctx.arc(x, y, r, 0, 2*math.pi)

def txt(s, x, y, size=14, anchor='left', bold=False, color='#333333'):
    col(color)
    ctx.select_font_face("Monospace", cairo.FONT_SLANT_NORMAL,
        cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)
    te = ctx.text_extents(s)
    if anchor == 'center': x -= te.width / 2
    elif anchor == 'right': x -= te.width
    ctx.move_to(x, y)
    ctx.show_text(s)

# ─── Colors ───────────────────────────────────────────────────────────────────
BG_COLOR       = '#f2f0ed'   # page background
TOP_FILL       = '#d8d6d2'   # top edge fill
TOP_BORDER     = '#b8b6b2'
FACE_FILL      = '#d4d2ce'   # enclosure face silver
FACE_BORDER    = '#a8a6a2'
FACE_BEVEL     = '#e0dedb'
SCREW_FILL     = '#c0beba'
SCREW_BORDER   = '#888684'
JACK_FILL      = '#b0aeaa'
JACK_BORDER    = '#888684'
JACK_HOLE      = '#555555'
KNOB_RING_FILL = '#c0beba'
KNOB_RING_BDR  = '#888684'
KNOB_BODY      = '#2a2a2a'
KNOB_LABEL     = '#555555'
FS_PLATE_FILL  = '#c0beba'
FS_PLATE_BDR   = '#888684'
FS_BODY        = '#2a2a2a'
FS_INNER       = '#1e1e1e'
OLED_BEZEL     = '#888684'
OLED_BEZEL_BDR = '#666462'
OLED_SCREEN    = '#000508'
OLED_TINT      = '#0a1a3a'
LED_FILL       = '#ffaaaa'
LED_BORDER     = '#dd2200'
LED_GLOW       = '#ff3300'

# ─── Background ───────────────────────────────────────────────────────────────
col(BG_COLOR); ctx.paint()
txt('SILVERTUNE PEDAL', W/2, 30, 20, 'center', True, '#555555')

# ─── Top Edge (jacks) ─────────────────────────────────────────────────────────
TOP_Y = 45
col(TOP_FILL); rrect(PAD, TOP_Y, EW, TOP_H, 6); ctx.fill()
col(TOP_BORDER); ctx.set_line_width(2); rrect(PAD, TOP_Y, EW, TOP_H, 6); ctx.stroke()
txt('TOP EDGE', W/2, TOP_Y + 18, 12, 'center', False, '#999999')

jack_y = TOP_Y + TOP_H // 2 + 14
JACKS = [
    (PAD + EW * 0.22, 'IN'),
    (PAD + EW * 0.50, '9V DC'),
    (PAD + EW * 0.78, 'OUT'),
]
for jx, label in JACKS:
    col(JACK_FILL);   circ(jx, jack_y, 20); ctx.fill()
    col(JACK_BORDER); ctx.set_line_width(3); circ(jx, jack_y, 20); ctx.stroke()
    col(JACK_HOLE);   circ(jx, jack_y, 10); ctx.fill()
    col('#333333');   ctx.set_line_width(1.5); circ(jx, jack_y, 10); ctx.stroke()
    txt(label, jx, jack_y + 36, 13, 'center', False, '#666666')

# ─── Front Face ───────────────────────────────────────────────────────────────
FX = PAD
FY = TOP_Y + TOP_H + 10

col(FACE_FILL);   rrect(FX, FY, EW, EH, 8); ctx.fill()
col(FACE_BORDER); ctx.set_line_width(3); rrect(FX, FY, EW, EH, 8); ctx.stroke()
col(FACE_BEVEL, 0.6); rrect(FX+4, FY+4, EW-8, EH/2, 6); ctx.fill()

# Corner screws
for sx, sy in [(FX+14, FY+14), (FX+EW-14, FY+14),
               (FX+14, FY+EH-14), (FX+EW-14, FY+EH-14)]:
    col(SCREW_FILL);  circ(sx, sy, 7); ctx.fill()
    col(SCREW_BORDER); ctx.set_line_width(1.5); circ(sx, sy, 7); ctx.stroke()
    col('#999795'); ctx.set_line_width(1.5)
    ctx.move_to(sx-4, sy); ctx.line_to(sx+4, sy); ctx.stroke()
    ctx.move_to(sx, sy-4); ctx.line_to(sx, sy+4); ctx.stroke()

txt('SILVERTUNE', FX + EW*0.50, FY + 22, 14, 'center', True, '#888888')

# ─── OLED ─────────────────────────────────────────────────────────────────────
oled_w = int(EW * 0.35)
oled_h = int(EH * 0.30)
oled_x = int(FX + EW * 0.05)
oled_y = int(FY + EH * 0.20)

col(OLED_BEZEL);     rrect(oled_x-5, oled_y-5, oled_w+10, oled_h+10, 6); ctx.fill()
col(OLED_BEZEL_BDR); ctx.set_line_width(2); rrect(oled_x-5, oled_y-5, oled_w+10, oled_h+10, 6); ctx.stroke()
col(OLED_SCREEN);    rrect(oled_x, oled_y, oled_w, oled_h, 3); ctx.fill()
col(OLED_TINT, 0.85); rrect(oled_x, oled_y, oled_w, oled_h, 3); ctx.fill()
# Screen content
txt('C#',    oled_x + oled_w*0.5, oled_y + oled_h*0.60, 32, 'center', True,  '#3388ff')
txt('MAJOR', oled_x + oled_w*0.5, oled_y + oled_h*0.90, 13, 'center', False, '#1a4488')

# ─── LED ──────────────────────────────────────────────────────────────────────
led_x = oled_x + oled_w + 32
led_y = oled_y + oled_h // 2

col(LED_FILL);   circ(led_x, led_y, 10); ctx.fill()
col(LED_BORDER); ctx.set_line_width(2); circ(led_x, led_y, 10); ctx.stroke()
col(LED_GLOW, 0.15); circ(led_x, led_y, 20); ctx.fill()

# ─── Knobs (2×2 grid, right side) ────────────────────────────────────────────
knob_r = 26
right_x = FX + EW * 0.50
KNOBS = [
    (right_x + EW*0.13, FY + EH*0.30, 'KEY'),
    (right_x + EW*0.35, FY + EH*0.30, 'SCALE'),
    (right_x + EW*0.13, FY + EH*0.72, 'MIX'),
    (right_x + EW*0.35, FY + EH*0.72, 'TUNE'),
]
for kx, ky, label in KNOBS:
    col(SCREW_FILL, 0.5); circ(kx+3, ky+3, knob_r+4); ctx.fill()   # shadow
    col(KNOB_RING_FILL); circ(kx, ky, knob_r+4); ctx.fill()
    col(KNOB_RING_BDR);  ctx.set_line_width(2); circ(kx, ky, knob_r+4); ctx.stroke()
    col(KNOB_BODY);      circ(kx, ky, knob_r); ctx.fill()
    col('#444444');      ctx.set_line_width(1.5); circ(kx, ky, knob_r); ctx.stroke()
    col('#ffffff');      circ(kx, ky - knob_r + 7, 3.5); ctx.fill()  # indicator dot
    txt(label, kx, ky + knob_r + 18, 12, 'center', False, KNOB_LABEL)

# ─── Footswitch ───────────────────────────────────────────────────────────────
fs_x = FX + EW * 0.25
fs_y = FY + EH * 0.74
fs_r = 34

col(FS_PLATE_FILL); rrect(fs_x-fs_r-14, fs_y-fs_r*0.4,
                           (fs_r+14)*2, int(fs_r*1.2)+16, 6); ctx.fill()
col(FS_PLATE_BDR);  ctx.set_line_width(1.5)
rrect(fs_x-fs_r-14, fs_y-fs_r*0.4, (fs_r+14)*2, int(fs_r*1.2)+16, 6); ctx.stroke()
col(FS_BODY);  circ(fs_x, fs_y, fs_r); ctx.fill()
col('#444444'); ctx.set_line_width(3); circ(fs_x, fs_y, fs_r); ctx.stroke()
col(FS_INNER); circ(fs_x, fs_y, fs_r-10); ctx.fill()
col('#3a3a3a'); ctx.set_line_width(1.5); circ(fs_x, fs_y, fs_r-10); ctx.stroke()
txt('BYPASS', fs_x, fs_y + fs_r + 20, 12, 'center', False, '#666666')

# ─── Caption ──────────────────────────────────────────────────────────────────
txt('Vertical Rectangle', W/2, H-14, 12, 'center', False, '#aaaaaa')

# ─── Save ─────────────────────────────────────────────────────────────────────
surface.write_to_png(OUTPUT)
print(f"Saved to {OUTPUT}")
