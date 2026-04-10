# Silvertune Pedal

Hard autotune in a stompbox. Same DSP brain as the [Silvertune](https://github.com/your-username/silvertune) CLAP plugin, running bare metal on a Daisy Seed.

Foot on = robot. Foot off = raw. Mid-song. Mid-word.

## Hardware

- **Daisy Seed** from [Electrosmith](https://www.electro-smith.com/daisy/daisy) (~$30)
- **Terrarium PCB** from [PedalPCB](https://www.pedalpcb.com/product/pcb351/) (~$10)
- **125B enclosure** from [Tayda](https://www.taydaelectronics.com/) (~$5, drill with Terrarium template)
- 6x B100K pots, 2x mono jacks, 1x DC jack, 1x 3PDT footswitch, 1x LED + resistor, pin headers

Total: ~$60-70. All through-hole. No SMD. Soldering iron and patience.

## Knobs

| Control | Function | Range |
|---------|----------|-------|
| Knob 1 | Key | C through B (mark 12 positions) |
| Knob 2 | *(spare)* | |
| Knob 3 | Mix | Dry/Wet blend |
| Knob 4 | Tune Strength | 0% = no correction, 100% = full robot |
| Knob 5 | *(reserved)* | Character knob in a future version |
| Knob 6 | *(unused)* | |
| SW1 | Scale: Major | Up = Major on |
| SW2 | Scale: Minor | Up = Minor on |
| SW1+SW2 off | Scale: Chromatic | Both off = no scale correction |
| Footswitch | Bypass | Toggle on/off |
| LED | Status | On when engaged |

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
- **USB audio interface** (e.g. Arturia Minifuse 1): Mic → XLR in, turn on direct monitor, 1/4" out → pedal. If you already own one, cost is just the pedal.
- **Small mixer** (e.g. Behringer Xenyx 502, ~$40): XLR in with built-in preamp, gain/EQ knobs, 1/4" out → pedal. Small enough to sit next to your pedalboard.

## How it works

1. Audio comes in mono from the guitar/mic jack
2. A bare YIN pitch detector (~80 lines, no dependencies) finds the fundamental frequency
3. The detected pitch is quantized to the nearest note in the selected key/scale
4. A two-tap grain shifter with Hann window crossfade shifts the pitch to the target note
5. Mix knob blends dry and corrected signal
6. Zero latency. No FFT. No buffering. Sample by sample.

## License

GPL-3.0 — same as the plugin.
