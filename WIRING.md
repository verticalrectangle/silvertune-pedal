# Silvertune Pedal — Wiring Diagram

Stripboard 50x100mm. Daisy Seed sits across the center channel, pins going into strips on each side.

## Layout

```
50mm
|←————————————————————————————→|

+--+--+--+--+--+--+--+--+--+--+   ↑
|  GND  |  3V3  |       |       |  |
|  rail | rail  |  D  D |       |  |
|       |       |  A  A |       |  |
|  POT  |       |  I  I |       |  |
|  lugs |  POT  |  S  S |       | 100mm
|  (G/V)|  wipers  Y  Y |       |  |
|       |       |     S |       |  |
|       |       |  S  E |       |  |
|  LED  | OLED  |  E  E |  DC   |  |
|  FS   | wires |  E  D |  jack |  |
|       |       |       |       |  ↓
+--+--+--+--+--+--+--+--+--+--+
```

## Connections

### Power
| From | To |
|------|----|
| DC jack + | Daisy Seed VIN |
| DC jack − | GND rail |
| Daisy Seed 3V3 | 3V3 rail |
| Daisy Seed DGND | GND rail |
| Daisy Seed AGND | GND rail |

### Potentiometers
All pots: left lug → GND rail, right lug → 3V3 rail, wiper → ADC pin.

| Knob | Wiper → |
|------|---------|
| Knob 1 (Key) | Daisy A0 |
| Knob 2 (Scale) | Daisy A1 |
| Knob 3 (Mix) | Daisy A2 |
| Knob 4 (Tune Strength) | Daisy A3 |

### Audio
| From | To |
|------|----|
| Input jack tip | Daisy AUDIO IN L |
| Input jack sleeve | GND rail |
| Output jack tip | Daisy AUDIO OUT L |
| Output jack sleeve | GND rail |

### Footswitch
| From | To |
|------|----|
| Footswitch pin 1 | Daisy D25 |
| Footswitch pin 2 | GND rail |

### LED
| From | To |
|------|----|
| LED anode | 470Ω resistor → Daisy D22 |
| LED cathode | GND rail |

### OLED (off-board, mounts to enclosure face)
| OLED pin | To |
|----------|----|
| SDA | Daisy D12 |
| SCL | Daisy D11 |
| VCC | 3V3 rail |
| GND | GND rail |

## Notes

- Verify all Daisy Seed pin positions against the official pinout at electro-smith.com before soldering
- Use two strips along the long edge as GND and 3V3 power rails — everything taps from there
- Pots, jacks, footswitch, and LED mount to the enclosure and connect to the board via hookup wire
- OLED mounts in a rectangular slot cut in the enclosure face, 4 wires back to the board
