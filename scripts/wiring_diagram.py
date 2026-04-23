#!/usr/bin/env python3
"""
Silvertune Pedal — Wiring Diagram Generator
Run: python3 scripts/wiring_diagram.py
Output: wiring-diagram.png
"""

import cairo
import math
import os

OUTPUT = os.path.join(os.path.dirname(__file__), '..', 'wiring-diagram.png')

W, H = 1400, 1000

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

def txt(s, x, y, size=13, anchor='left', bold=False, color='#222222'):
    col(color)
    ctx.select_font_face("Monospace", cairo.FONT_SLANT_NORMAL,
        cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)
    te = ctx.text_extents(s)
    if anchor == 'center': x -= te.width / 2
    elif anchor == 'right': x -= te.width
    ctx.move_to(x, y)
    ctx.show_text(s)

def wire(pts, color, width=2.5):
    col(color)
    ctx.set_line_width(width)
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.stroke()

# ─── Colors ───────────────────────────────────────────────────────────────────
BG         = '#f2f0ed'
POWER_RED  = '#cc3333'
GND_GRAY   = '#999999'
ADC_BLUE   = '#2255bb'
I2C_TEAL   = '#009988'
AUDIO_IN   = '#228844'
AUDIO_OUT  = '#cc3333'
LED_ORANGE = '#cc6600'
FS_YELLOW  = '#997700'
SEED_GREEN = '#e8f4e8'
SEED_BDR   = '#5a9a5a'
RAIL_RED   = '#fde8e8'
RAIL_GRAY  = '#e8e8e8'

# ─── Background ───────────────────────────────────────────────────────────────
col(BG); ctx.paint()

txt('SILVERTUNE PEDAL — WIRING DIAGRAM', W/2, 38, 22, 'center', True, '#333333')
txt('Daisy Seed Rev7  ·  verify pin positions at electro-smith.com',
    W/2, 62, 13, 'center', False, '#888888')

# ─── Power Rails ──────────────────────────────────────────────────────────────
col(RAIL_GRAY); rrect(12, 130, 30, 720); ctx.fill()
col('#aaaaaa'); ctx.set_line_width(1.5); rrect(12, 130, 30, 720); ctx.stroke()
ctx.save(); ctx.translate(27, 490); ctx.rotate(-math.pi/2)
txt('GND RAIL', 0, 5, 13, 'center', False, '#555555')
ctx.restore()

col(RAIL_RED); rrect(48, 130, 26, 720); ctx.fill()
col('#cc8888'); ctx.set_line_width(1.5); rrect(48, 130, 26, 720); ctx.stroke()
ctx.save(); ctx.translate(61, 490); ctx.rotate(-math.pi/2)
txt('3V3 RAIL', 0, 5, 13, 'center', False, '#cc3333')
ctx.restore()

# ─── Daisy Seed ───────────────────────────────────────────────────────────────
DS_X, DS_Y, DS_W, DS_H = 460, 130, 290, 720

# Pin y-positions: 20 pins per side, evenly spaced
# Left side: pins 21-40, top to bottom
# Right side: pins 20-1, top to bottom
PIN_STEP = DS_H / 19

def left_pin_y(pin):
    """Pin 21=top, 40=bottom."""
    return DS_Y + (pin - 21) * PIN_STEP

def right_pin_y(pin):
    """Pin 20=top, 1=bottom."""
    return DS_Y + (20 - pin) * PIN_STEP

col(SEED_GREEN); rrect(DS_X, DS_Y, DS_W, DS_H); ctx.fill()
col(SEED_BDR); ctx.set_line_width(3); rrect(DS_X, DS_Y, DS_W, DS_H); ctx.stroke()
txt('DAISY SEED', DS_X + DS_W/2, 500, 24, 'center', True, '#2a6a10')

# Left pins (exit left from DS_X)
LEFT_PINS = [
    (left_pin_y(22), 'A0  pin 22'),
    (left_pin_y(23), 'A1  pin 23'),
    (left_pin_y(24), 'A2  pin 24'),
    (left_pin_y(25), 'A3  pin 25'),
    (left_pin_y(29), 'D22 pin 29'),
    (left_pin_y(32), 'D25 pin 32'),
    (left_pin_y(38), '3V3 pin 38'),
    (left_pin_y(39), 'VIN pin 39'),
    (left_pin_y(40), 'GND pin 40'),
]
for py, label in LEFT_PINS:
    col('#aaaaaa'); ctx.set_line_width(2.5)
    ctx.move_to(DS_X, py); ctx.line_to(DS_X - 25, py); ctx.stroke()
    txt(label, DS_X - 28, py + 5, 12, 'right', False, '#555555')

# Right pins (exit right from DS_X + DS_W)
RIGHT_PINS = [
    (right_pin_y(20), 'AGND        pin 20'),
    (right_pin_y(18), 'Audio Out 1 pin 18'),
    (right_pin_y(16), 'Audio In 1  pin 16'),
    (right_pin_y(13), 'D12  SDA    pin 13'),
    (right_pin_y(12), 'D11  SCL    pin 12'),
]
for py, label in RIGHT_PINS:
    col('#aaaaaa'); ctx.set_line_width(2.5)
    ctx.move_to(DS_X + DS_W, py); ctx.line_to(DS_X + DS_W + 25, py); ctx.stroke()
    txt(label, DS_X + DS_W + 30, py + 5, 12, 'left', False, '#555555')

# ─── OLED ─────────────────────────────────────────────────────────────────────
col('#eef0f8'); rrect(70, 148, 150, 82); ctx.fill()
col('#6688cc'); ctx.set_line_width(2.5); rrect(70, 148, 150, 82); ctx.stroke()
col('#001133'); rrect(78, 156, 134, 48); ctx.fill()
txt('OLED', 145, 186, 16, 'center', True, '#4499ff')
txt('SSD1306 I2C', 145, 218, 11, 'center', False, '#6688aa')

# ─── LED ──────────────────────────────────────────────────────────────────────
col('#ffe8e8'); circ(115, 385, 28); ctx.fill()
col('#cc3311'); ctx.set_line_width(2.5); circ(115, 385, 28); ctx.stroke()
txt('LED', 115, 390, 13, 'center', True, '#cc2200')
col('#f5f0e8'); rrect(150, 376, 60, 18); ctx.fill()
col('#888866'); ctx.set_line_width(1.5); rrect(150, 376, 60, 18); ctx.stroke()
txt('470 Ohm', 180, 389, 11, 'center', False, '#665500')

# ─── Footswitch ───────────────────────────────────────────────────────────────
col('#e8e6e2'); rrect(68, 470, 130, 80, 40); ctx.fill()
col('#aaaaaa'); ctx.set_line_width(2.5); rrect(68, 470, 130, 80, 40); ctx.stroke()
txt('FOOT',   133, 505, 14, 'center', True, '#444444')
txt('SWITCH', 133, 525, 14, 'center', True, '#444444')

# ─── Audio Jacks ──────────────────────────────────────────────────────────────
col('#e8e6e2'); rrect(1060, 150, 190, 58); ctx.fill()
col('#aaaaaa'); ctx.set_line_width(2); rrect(1060, 150, 190, 58); ctx.stroke()
col('#888888'); circ(1082, 179, 20); ctx.fill()
col('#555555'); circ(1082, 179, 11); ctx.fill()
txt('IN JACK  1/4"', 1108, 183, 14, False, False, '#333333')

col('#e8e6e2'); rrect(1060, 220, 190, 58); ctx.fill()
col('#aaaaaa'); ctx.set_line_width(2); rrect(1060, 220, 190, 58); ctx.stroke()
col('#888888'); circ(1082, 249, 20); ctx.fill()
col('#555555'); circ(1082, 249, 11); ctx.fill()
txt('OUT JACK 1/4"', 1108, 253, 14, False, False, '#333333')

# ─── Potentiometers ───────────────────────────────────────────────────────────
POT_X = 1120
POTS = [
    (540, 'K1  KEY'),
    (620, 'K2  SCALE'),
    (700, 'K3  MIX'),
    (780, 'K4  TUNE'),
]
for py, label in POTS:
    col('#e8e6e2'); circ(POT_X, py, 34); ctx.fill()
    col('#8899bb'); ctx.set_line_width(2.5); circ(POT_X, py, 34); ctx.stroke()
    col('#2a2a2a'); circ(POT_X, py, 22); ctx.fill()
    col('#ffffff'); circ(POT_X, py - 15, 4); ctx.fill()
    txt(label, POT_X, py + 5, 12, 'center', True, '#334466')
    for dx in [-14, 0, 14]:
        col('#888888'); circ(POT_X + dx, py + 34, 4); ctx.fill()

# ─── DC Jack ──────────────────────────────────────────────────────────────────
col('#e8e6e2'); rrect(500, 900, 220, 62); ctx.fill()
col('#aaaaaa'); ctx.set_line_width(2); rrect(500, 900, 220, 62); ctx.stroke()
txt('DC JACK  9V',        610, 935, 15, 'center', True,  '#333333')
txt('+ center positive -', 610, 952, 12, 'center', False, '#888888')

# ─── Wires ────────────────────────────────────────────────────────────────────

# OLED SDA → D12 (right side, pin 13)
# Route over the top of the Daisy
sda_y = right_pin_y(13)
wire([(220, 188), (DS_X+DS_W+55, 188), (DS_X+DS_W+55, sda_y), (DS_X+DS_W+25, sda_y)], I2C_TEAL, 2.5)

# OLED SCL → D11 (right side, pin 12)
scl_y = right_pin_y(12)
wire([(220, 178), (DS_X+DS_W+70, 178), (DS_X+DS_W+70, scl_y), (DS_X+DS_W+25, scl_y)], '#007766', 2.5)

# OLED VCC → 3V3 rail
wire([(74, 165), (62, 165)], POWER_RED, 2.5)
# OLED GND → GND rail
wire([(74, 172), (42, 172)], GND_GRAY, 2.5)

# LED anode → 470R → D22 (left side, pin 29)
d22_y = left_pin_y(29)
wire([(143, 385), (150, 385)], LED_ORANGE, 2.5)
wire([(210, 385), (DS_X-30, 385), (DS_X-30, d22_y), (DS_X, d22_y)], LED_ORANGE, 2.5)
# LED cathode → GND rail
wire([(87, 413), (87, 440), (42, 440)], GND_GRAY, 2.5)

# Footswitch → D25 (left side, pin 32)
d25_y = left_pin_y(32)
wire([(198, 510), (DS_X-45, 510), (DS_X-45, d25_y), (DS_X, d25_y)], FS_YELLOW, 2.5)
# Footswitch GND
wire([(198, 520), (42, 520)], GND_GRAY, 2.5)

# IN jack → Audio In 1 (right side, pin 16)
ain_y = right_pin_y(16)
wire([(1060, 179), (DS_X+DS_W+40, 179), (DS_X+DS_W+40, ain_y), (DS_X+DS_W+25, ain_y)], AUDIO_IN, 2.5)
# IN jack sleeve → GND rail
wire([(1060, 188), (1050, 188), (1050, 860), (42, 860)], GND_GRAY, 2.5)

# OUT jack → Audio Out 1 (right side, pin 18)
aout_y = right_pin_y(18)
wire([(1060, 249), (DS_X+DS_W+25, 249), (DS_X+DS_W+25, aout_y)], AUDIO_OUT, 2.5)
# OUT jack sleeve → GND rail
wire([(1060, 258), (1045, 258), (1045, 868), (42, 868)], GND_GRAY, 2.5)

# AGND (right side, pin 20) → GND rail
agnd_y = right_pin_y(20)
wire([(DS_X+DS_W, agnd_y), (DS_X+DS_W+85, agnd_y), (DS_X+DS_W+85, 876), (42, 876)], GND_GRAY, 2.5)

# Pot wipers → A0–A3 (left side, pins 22–25)
# Route: wiper → left → route behind left components → enter Daisy left side
POT_ADC = [
    (540, left_pin_y(22)),
    (620, left_pin_y(23)),
    (700, left_pin_y(24)),
    (780, left_pin_y(25)),
]
for ppy, apy in POT_ADC:
    wire([(1086, ppy), (DS_X-55, ppy), (DS_X-55, apy), (DS_X, apy)], ADC_BLUE, 2.5)

# Pot high lug → 3V3 rail
for py in [540, 620, 700, 780]:
    wire([(POT_X+34, py), (POT_X+50, py), (POT_X+50, py-45), (62, py-45)], POWER_RED, 2)

# Pot low lug → GND rail
for py in [540, 620, 700, 780]:
    wire([(POT_X-6, py+34), (POT_X-6, py+55), (42, py+55)], GND_GRAY, 2)

# Daisy 3V3 OUT (left side, pin 38) → 3V3 rail
v33_y = left_pin_y(38)
wire([(DS_X, v33_y), (DS_X-25, v33_y), (DS_X-25, 840), (62, 840)], POWER_RED, 2.5)

# Daisy DGND (left side, pin 40) → GND rail
dgnd_y = left_pin_y(40)
wire([(DS_X, dgnd_y), (DS_X-25, dgnd_y), (DS_X-25, 848), (42, 848)], GND_GRAY, 2.5)

# DC jack + → VIN (left side, pin 39)
vin_y = left_pin_y(39)
wire([(500, 920), (DS_X-70, 920), (DS_X-70, vin_y), (DS_X, vin_y)], POWER_RED, 3)
# DC jack − → GND rail
wire([(720, 920), (720, 890), (42, 890)], GND_GRAY, 3)

# ─── Legend ───────────────────────────────────────────────────────────────────
col('#ffffff', 0.9); rrect(940, 850, 400, 130); ctx.fill()
col('#cccccc'); ctx.set_line_width(1.5); rrect(940, 850, 400, 130); ctx.stroke()
txt('LEGEND', 1140, 872, 14, 'center', True, '#444444')

LEGEND = [
    (POWER_RED,  '3.3V / Power'),
    (GND_GRAY,   'GND'),
    (ADC_BLUE,   'ADC (pot wipers)'),
    (I2C_TEAL,   'I2C (OLED)'),
    (AUDIO_IN,   'Audio IN'),
    (AUDIO_OUT,  'Audio OUT'),
    (LED_ORANGE, 'LED signal'),
    (FS_YELLOW,  'Footswitch'),
]
for i, (lc, ll) in enumerate(LEGEND):
    c = i % 2; row = i // 2
    lx = 952 + c * 192
    ly = 892 + row * 20
    ctx.set_source_rgba(*from_hex(lc), 1.0)
    ctx.set_line_width(4)
    ctx.move_to(lx, ly); ctx.line_to(lx + 26, ly); ctx.stroke()
    ctx.set_source_rgba(*from_hex('#333333'), 1.0)
    ctx.select_font_face("Monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(12)
    ctx.move_to(lx + 32, ly + 5)
    ctx.show_text(ll)

# ─── Save ─────────────────────────────────────────────────────────────────────
surface.write_to_png(OUTPUT)
print(f"Saved to {OUTPUT}")
