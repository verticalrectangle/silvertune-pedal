#include "daisy_seed.h"
#include "yin.h"
#include "grain_shifter.h"
#include "scale.h"
#include <cmath>
#include <algorithm>

using namespace daisy;

// --- Terrarium pin mapping ---
// https://www.pedalpcb.com/docs/Terrarium-Daisy.pdf

// Knobs — ADC channels on Daisy Seed
enum {
    KNOB_1 = 0,  // Key (C through B)
    KNOB_2 = 1,  // (spare)
    KNOB_3 = 2,  // Mix
    KNOB_4 = 3,  // Tune Strength
    KNOB_5 = 4,  // (future: Character)
    KNOB_6 = 5,  // (unused)
    KNOB_COUNT = 6
};

// Terrarium ADC pin mapping (Seed pin numbers)
static constexpr Pin KNOB_PINS[KNOB_COUNT] = {
    seed::A0, seed::A1, seed::A2, seed::A3, seed::A4, seed::A5
};

// Toggle switches — SW1 = Major, SW2 = Minor, both off = Chromatic
static constexpr Pin PIN_SW1 = seed::D1;
static constexpr Pin PIN_SW2 = seed::D2;

// Footswitch and LEDs
static constexpr Pin PIN_FOOTSWITCH = seed::D25;
static constexpr Pin PIN_LED        = seed::D22;

// --- Globals ---

static DaisySeed hw;
static Switch footswitch;
static Switch sw1;
static Switch sw2;
static Led led;

static YinDetector yin;
static GrainShifter shifter;

static bool engaged = true;

// Knob values
static float knob_key_raw = 0.0f;
static float knob_mix     = 0.5f;
static float knob_snap    = 1.0f;

// --- Audio callback ---

static void audio_callback(AudioHandle::InputBuffer in,
                            AudioHandle::OutputBuffer out,
                            size_t size) {
    // Read footswitch and toggles (debounced)
    footswitch.Debounce();
    sw1.Debounce();
    sw2.Debounce();

    if (footswitch.RisingEdge())
        engaged = !engaged;

    // Read knobs
    knob_key_raw = hw.adc.GetFloat(KNOB_1);
    knob_mix     = hw.adc.GetFloat(KNOB_3);
    knob_snap    = hw.adc.GetFloat(KNOB_4);

    // Quantize key knob to 0-11
    int root_key = static_cast<int>(knob_key_raw * 11.99f);
    root_key = std::clamp(root_key, 0, 11);

    // Scale from toggle switches:
    // SW1 on = Major, SW2 on = Minor, both off = Chromatic
    ScaleType scale;
    if (sw1.Pressed())
        scale = SCALE_MAJOR;
    else if (sw2.Pressed())
        scale = SCALE_MINOR;
    else
        scale = SCALE_CHROMATIC;

    float snap = std::clamp(knob_snap, 0.0f, 1.0f);
    float mix  = std::clamp(knob_mix, 0.0f, 1.0f);

    for (size_t i = 0; i < size; ++i) {
        float dry = in[0][i];

        if (!engaged) {
            // Bypass: pass through
            out[0][i] = dry;
            continue;
        }

        // Feed pitch detector
        yin.push(dry);

        // Compute pitch ratio
        float pitch_ratio = 1.0f;

        if (yin.pitch_hz > 50.0f && yin.pitch_hz < 2000.0f && yin.confidence > 0.6f) {
            float detected_midi = hz_to_midi(yin.pitch_hz);
            int nearest_midi = quantize_to_scale(
                static_cast<int>(std::round(detected_midi)), root_key, scale);
            float target_hz = midi_to_hz(static_cast<float>(nearest_midi));

            pitch_ratio = target_hz / yin.pitch_hz;
            pitch_ratio = 1.0f + (pitch_ratio - 1.0f) * snap;
            pitch_ratio = std::clamp(pitch_ratio, 0.5f, 2.0f);
        }

        float wet = shifter.process(dry, static_cast<double>(pitch_ratio));
        out[0][i] = dry * (1.0f - mix) + wet * mix;
    }
}

// --- Main ---

int main(void) {
    hw.Init();
    hw.SetAudioBlockSize(48);
    hw.SetAudioSampleRate(SaiHandle::Config::SampleRate::SAI_48KHZ);

    float sr = hw.AudioSampleRate();

    // Init ADC for 6 knobs
    AdcChannelConfig adc_cfg[KNOB_COUNT];
    for (int i = 0; i < KNOB_COUNT; ++i)
        adc_cfg[i].InitSingle(KNOB_PINS[i]);
    hw.adc.Init(adc_cfg, KNOB_COUNT);
    hw.adc.Start();

    // Init footswitch and toggle switches
    footswitch.Init(PIN_FOOTSWITCH, 1000.0f / 48.0f);
    sw1.Init(PIN_SW1, 1000.0f / 48.0f, Switch::TYPE_TOGGLE, Switch::POLARITY_INVERTED, GPIO::Pull::PULLUP);
    sw2.Init(PIN_SW2, 1000.0f / 48.0f, Switch::TYPE_TOGGLE, Switch::POLARITY_INVERTED, GPIO::Pull::PULLUP);

    // Init LED
    led.Init(PIN_LED, false);
    led.Set(1.0f);
    led.Update();

    // Init DSP
    yin.init(sr);
    shifter.reset();

    // Start audio
    hw.StartAudio(audio_callback);

    // Main loop: just update LED
    while (true) {
        led.Set(engaged ? 1.0f : 0.0f);
        led.Update();
        System::Delay(10);
    }
}
