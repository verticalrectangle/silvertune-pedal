#include "daisy_seed.h"
#include "dev/oled_ssd130x.h"
#include "yin.h"
#include "grain_shifter.h"
#include "scale.h"
#include <cmath>
#include <algorithm>
#include <cstdio>

using namespace daisy;
using MyOled = OledDisplay<SSD130xI2c128x64Driver>;

enum {
    KNOB_KEY   = 0,
    KNOB_SCALE = 1,
    KNOB_WIDE  = 2,
    KNOB_TUNE  = 3,
    KNOB_COUNT = 6
};

static constexpr Pin KNOB_PINS[KNOB_COUNT] = {
    seed::A0, seed::A1, seed::A2, seed::A3, seed::A4, seed::A5
};

static constexpr Pin PIN_FOOTSWITCH = seed::D25;
static constexpr Pin PIN_LED        = seed::D22;

static DaisySeed  hw;
static Switch     footswitch;
static Led        led;
static MyOled     display;

static constexpr float DETUNE = 1.00463f; // +8 cents

static YinDetector  yin;
static GrainShifter shifter;
static GrainShifter doubler;

static bool     engaged      = true;
static float    held_ratio   = 1.0f;
static volatile int8_t current_note = -1; // 0-11, or -1 when no pitch

static volatile float v_key   = 0.0f;
static volatile float v_scale = 0.0f;
static volatile float v_mix   = 0.5f;
static volatile float v_tune  = 1.0f;
static volatile int   root_key  = 0;
static volatile int   scale_idx = 1;

static inline float knob(float v) {
    return std::clamp((v - 0.04f) / 0.95f, 0.0f, 1.0f);
}

static const char* KEY_NAMES[12]  = { "C","C#","D","D#","E","F","F#","G","G#","A","A#","B" };
static const char* SCALE_NAMES[3] = { "CHROMATIC", "MAJOR", "MINOR" };
static const ScaleType SCALE_MAP[3] = { SCALE_CHROMATIC, SCALE_MAJOR, SCALE_MINOR };

static void audio_callback(AudioHandle::InputBuffer in,
                            AudioHandle::OutputBuffer out,
                            size_t size) {
    footswitch.Debounce();
    if (footswitch.RisingEdge())
        engaged = !engaged;

    v_key   = knob(hw.adc.GetFloat(KNOB_KEY));
    v_scale = knob(hw.adc.GetFloat(KNOB_SCALE));
    v_mix   = knob(hw.adc.GetFloat(KNOB_WIDE));
    v_tune  = knob(hw.adc.GetFloat(KNOB_TUNE));

    root_key  = std::clamp((int)(v_key * 11.99f), 0, 11);
    scale_idx = std::clamp((int)(v_scale * 2.99f), 0, 2);

    ScaleType scale = SCALE_MAP[scale_idx];
    float snap = std::clamp((float)v_tune, 0.0f, 1.0f);
    float mix  = std::clamp((float)v_mix,  0.0f, 1.0f);

    if (yin.pitch_hz > 50.0f && yin.pitch_hz < 2000.0f && yin.confidence > 0.5f) {
        float detected_midi = hz_to_midi(yin.pitch_hz);
        int nearest_midi = quantize_to_scale(
            static_cast<int>(std::round(detected_midi)), root_key, scale);
        float target_hz = midi_to_hz(static_cast<float>(nearest_midi));
        held_ratio = target_hz / yin.pitch_hz;
        held_ratio = 1.0f + (held_ratio - 1.0f) * snap;
        held_ratio = std::clamp(held_ratio, 0.5f, 2.0f);
        current_note = nearest_midi % 12;
    }
    float pitch_ratio = held_ratio;

    for (size_t i = 0; i < size; ++i) {
        float dry = in[0][i];
        if (!engaged) {
            out[0][i] = dry;
            continue;
        }
        yin.push_sample(dry);
        float wet = shifter.process(dry, static_cast<double>(pitch_ratio));
        float dbl = doubler.process(dry, static_cast<double>(pitch_ratio * DETUNE));
        out[0][i] = wet + dbl * mix;
    }
}

// Piano layout: right 56px (x=72..127), full height
static constexpr int PX = 72;
static constexpr int PY = 8;
static constexpr int WW = 8;   // white key width
static constexpr int WH = 56;  // white key height
static constexpr int BW = 5;   // black key width
static constexpr int BH = 32;  // black key height

// note 0=C, white keys: C D E F G A B → notes 0 2 4 5 7 9 11
static const int8_t WHITE_NOTE[7] = {0, 2, 4, 5, 7, 9, 11};
// black key x offsets (relative to PX) and their notes
static const int8_t BLACK_REL_X[5] = {3, 11, 27, 35, 43};
static const int8_t BLACK_NOTE[5]  = {1, 3,  6,  8,  10};

static void fill_rect(int x, int y, int w, int h, bool on) {
    for (int iy = y; iy < y + h; iy++)
        for (int ix = x; ix < x + w; ix++)
            display.DrawPixel(ix, iy, on);
}

static void draw_piano(int8_t active) {
    // White keys: outlined normally, filled when active
    for (int i = 0; i < 7; i++) {
        int x0 = PX + i * WW;
        bool lit = (WHITE_NOTE[i] == active);
        fill_rect(x0, PY, WW, WH, lit);
        if (!lit) {
            for (int y = PY; y < PY + WH; y++) {
                display.DrawPixel(x0,          y, true);
                display.DrawPixel(x0 + WW - 1, y, true);
            }
            for (int x = x0; x < x0 + WW; x++) {
                display.DrawPixel(x, PY,          true);
                display.DrawPixel(x, PY + WH - 1, true);
            }
        }
    }

    // Black keys: dark interior + white border; filled white when active
    for (int i = 0; i < 5; i++) {
        int x0 = PX + BLACK_REL_X[i];
        bool lit = (BLACK_NOTE[i] == active);
        fill_rect(x0, PY, BW, BH, lit);
        if (!lit) {
            for (int y = PY; y < PY + BH; y++) {
                display.DrawPixel(x0,          y, true);
                display.DrawPixel(x0 + BW - 1, y, true);
            }
            for (int x = x0; x < x0 + BW; x++) {
                display.DrawPixel(x, PY,          true);
                display.DrawPixel(x, PY + BH - 1, true);
            }
        }
    }
}

static void update_display(bool show_temp, const char* temp_msg) {
    display.Fill(false);
    if (!engaged) {
        display.SetCursor(0, 11);
        display.WriteString(const_cast<char*>("BYPASS"), Font_7x10, true);
    } else if (show_temp) {
        display.SetCursor(0, 11);
        display.WriteString(const_cast<char*>(temp_msg), Font_7x10, true);
    } else {
        if (scale_idx == 0) {
            display.SetCursor(0, 11);
            display.WriteString(const_cast<char*>("CHROM"), Font_7x10, true);
        } else {
            char key[4];
            snprintf(key, sizeof(key), "%s", KEY_NAMES[root_key]);
            display.SetCursor(0, 0);
            display.WriteString(key, Font_11x18, true);
            display.SetCursor(0, 22);
            display.WriteString(const_cast<char*>(SCALE_NAMES[scale_idx]), Font_6x8, true);
        }
        draw_piano(engaged ? current_note : -1);
    }
    display.Update();
}

int main(void) {
    hw.Init();
    hw.SetAudioBlockSize(48);
    hw.SetAudioSampleRate(SaiHandle::Config::SampleRate::SAI_48KHZ);

    float sr = hw.AudioSampleRate();

    AdcChannelConfig adc_cfg[KNOB_COUNT];
    for (int i = 0; i < KNOB_COUNT; i++)
        adc_cfg[i].InitSingle(KNOB_PINS[i]);
    hw.adc.Init(adc_cfg, KNOB_COUNT);
    hw.adc.Start();

    footswitch.Init(PIN_FOOTSWITCH, 1000.0f / 48.0f);

    led.Init(PIN_LED, false);
    led.Set(1.0f);
    led.Update();

    MyOled::Config oled_cfg;
    oled_cfg.driver_config.transport_config.i2c_config.periph =
        I2CHandle::Config::Peripheral::I2C_1;
    oled_cfg.driver_config.transport_config.i2c_config.speed =
        I2CHandle::Config::Speed::I2C_400KHZ;
    oled_cfg.driver_config.transport_config.i2c_config.pin_config.scl = seed::D11;
    oled_cfg.driver_config.transport_config.i2c_config.pin_config.sda = seed::D12;
    oled_cfg.driver_config.transport_config.i2c_address = 0x3C;
    display.Init(oled_cfg);

    yin.init(sr);
    shifter.reset();
    doubler.reset();

    hw.StartAudio(audio_callback);

    float prev_key   = v_key;
    float prev_scale = v_scale;
    float prev_mix   = v_mix;
    float prev_tune  = v_tune;

    constexpr float    THRESH      = 0.02f;
    constexpr uint32_t HOLD_MS     = 2000;
    constexpr uint32_t DISPLAY_MS  = 50;
    uint32_t timeout_ms  = 0;
    uint32_t next_display = 0;
    char     temp_msg[32] = "";

    while (true) {
        if (yin.pending)
            yin.run_detect();

        uint32_t now = System::GetNow();
        if (now >= next_display) {
            next_display = now + DISPLAY_MS;

            float ck = v_key, cs = v_scale, cm = v_mix, ct = v_tune;

            if (fabsf(ck - prev_key) > THRESH) {
                snprintf(temp_msg, sizeof(temp_msg), "KEY: %s", KEY_NAMES[root_key]);
                timeout_ms = now + HOLD_MS;
                prev_key = ck;
            } else if (fabsf(cs - prev_scale) > THRESH) {
                snprintf(temp_msg, sizeof(temp_msg), "SCALE: %s", SCALE_NAMES[scale_idx]);
                timeout_ms = now + HOLD_MS;
                prev_scale = cs;
            } else if (fabsf(cm - prev_mix) > THRESH) {
                snprintf(temp_msg, sizeof(temp_msg), "WIDE: %d%%", (int)(cm * 100));
                timeout_ms = now + HOLD_MS;
                prev_mix = cm;
            } else if (fabsf(ct - prev_tune) > THRESH) {
                snprintf(temp_msg, sizeof(temp_msg), "TUNE: %d%%", (int)(ct * 100));
                timeout_ms = now + HOLD_MS;
                prev_tune = ct;
            }

            update_display(now < timeout_ms, temp_msg);

            led.Set(engaged ? 1.0f : 0.0f);
            led.Update();
        }
    }
}
