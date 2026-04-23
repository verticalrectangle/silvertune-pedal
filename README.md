# Silvertune Pedal

Hard autotune in a stompbox. Same DSP brain as the [Silvertune](https://github.com/your-username/silvertune) CLAP plugin, running bare metal on a Daisy Seed.

Foot on = robot. Foot off = raw. Mid-song. Mid-word.

## Hardware

**Enclosure**
- 125B aluminum enclosure (~$5)

**On the PCB**
- Daisy Seed microcontroller (~$30) — [electro-smith.com](https://www.electro-smith.com/daisy/daisy)
- ElectroCookie breadboard-style PCB, 52.1×88.9mm (~$8)

**Mounted to enclosure, wired to board**
- 4× B10K vertical potentiometer (RK097 or equivalent)
- 2× 1/4" mono jack
- 1× DC power jack (5.5/2.1mm, center positive)
- 1× SPDT momentary footswitch
- 1× 5mm LED + 470Ω resistor
- 1× SSD1306 OLED display, 0.96", 128×64, I2C

Total: ~$55-65. All through-hole. No SMD. Soldering iron and patience.

## Knobs

| Control | Function | Range |
|---------|----------|-------|
| KEY | Root key | C through B |
| SCALE | Scale | Chromatic → Major → Minor |
| MIX | Dry/Wet blend | 0% dry → 100% wet |
| TUNE | Tune Strength | 0% = no correction, 100% = full robot |
| Footswitch | Bypass | Toggle on/off |
| LED | Status | On when engaged |

## Display

The OLED shows the current state at a glance:

- **Default (key set):** large key name on top, scale name below — e.g. `C#` / `MAJOR`
- **Default (chromatic):** just `CHROMATIC` centered
- **While adjusting a knob:** shows that parameter's value for 2 seconds, then returns — e.g. `MIX: 75%`, `KEY: C#`, `TUNE: 100%`, `SCALE: MAJOR`

The display mirrors the Silvertune plugin interface in a DAW.

## Wiring

See `WIRING.md` for full connection reference and `board-layout.png` for the PCB layout.

The Daisy Seed sits on the ElectroCookie PCB straddling the center gap (rows 6–25). All other components — pots, jacks, footswitch, LED, OLED — mount to the enclosure and connect back to the board via hookup wire.

| Signal | Daisy Seed pin |
|--------|---------------|
| OLED SDA | D12 (pin 13) |
| OLED SCL | D11 (pin 12) |
| LED anode | D22 (pin 29) via 470Ω |
| Footswitch | D25 (pin 32) |
| KEY knob | A0 (pin 22) |
| SCALE knob | A1 (pin 23) |
| MIX knob | A2 (pin 24) |
| TUNE knob | A3 (pin 25) |
| Audio IN | AUDIO IN L (pin 16) |
| Audio OUT | AUDIO OUT L (pin 18) |

## Build

### 1. Install the ARM toolchain

```bash
# Arch / CachyOS
sudo pacman -S arm-none-eabi-gcc arm-none-eabi-newlib

# Ubuntu / Debian
sudo apt install gcc-arm-none-eabi libnewlib-arm-none-eabi
```

### 2. Build the Daisy libraries

```bash
cd lib/libDaisy
make
cd ../DaisySP
make
```

### 3. Build the firmware

```bash
# From the project root
make
```

This produces `build/silvertune_pedal.bin`.

### 4. Flash to the Daisy Seed

Put the Daisy into DFU mode (hold BOOT, press RESET, release BOOT), then:

```bash
make program-dfu
```

## Live vocal setup

The Daisy Seed expects line/instrument level, not raw mic level. You need a preamp or DI box between your mic and the pedal.

```
Mic (XLR) → Preamp/DI Box (XLR in, 1/4" out) → Silvertune Pedal → PA / Mixer
```

Two easy options:
- **USB audio interface** (e.g. Arturia Minifuse 1): Mic → XLR in, turn on direct monitor, 1/4" out → pedal.
- **Small mixer** (e.g. Behringer Xenyx 502, ~$40): XLR in with built-in preamp, 1/4" out → pedal.

## How it works

1. Audio comes in mono from the input jack
2. A bare YIN pitch detector (~80 lines, no dependencies) finds the fundamental frequency
3. The detected pitch is quantized to the nearest note in the selected key/scale
4. A two-tap grain shifter with Hann window crossfade shifts the pitch to the target note
5. Mix knob blends dry and corrected signal
6. Zero latency. No FFT. No buffering. Sample by sample.

## License

GPL-3.0 — same as the plugin.
