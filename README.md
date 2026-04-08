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

| Knob | Function | Range |
|------|----------|-------|
| 1 | Key | C through B |
| 2 | Scale | Major / Minor / Chromatic (3 positions) |
| 3 | Mix | Dry/Wet blend |
| 4 | Tune Strength | 0% = no correction, 100% = full robot |
| 5 | *(reserved)* | Character knob in a future version |
| 6 | *(unused)* | |
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

A Behringer DI100 Ultra-DI (~$25) does the job — XLR in, 1/4" out, built like a tank. Three boxes, three cables, that's the whole rig.

## How it works

1. Audio comes in mono from the guitar/mic jack
2. A bare YIN pitch detector (~80 lines, no dependencies) finds the fundamental frequency
3. The detected pitch is quantized to the nearest note in the selected key/scale
4. A two-tap grain shifter with Hann window crossfade shifts the pitch to the target note
5. Mix knob blends dry and corrected signal
6. Zero latency. No FFT. No buffering. Sample by sample.

## License

GPL-3.0 — same as the plugin.
