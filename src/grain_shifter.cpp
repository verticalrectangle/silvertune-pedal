#include "grain_shifter.h"
#include <cmath>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

static inline float hann(double phase) {
    return 0.5f * (1.0f - std::cos(2.0 * M_PI * phase));
}

static inline float lerp_read(const float *buf, uint32_t write_pos, double delay, uint32_t mask) {
    double read_pos = static_cast<double>(write_pos) - delay;
    double wrapped = std::fmod(read_pos, static_cast<double>(mask + 1));
    if (wrapped < 0) wrapped += (mask + 1);

    uint32_t i0 = static_cast<uint32_t>(wrapped) & mask;
    uint32_t i1 = (i0 + 1) & mask;
    float frac = static_cast<float>(wrapped - std::floor(wrapped));
    return buf[i0] * (1.0f - frac) + buf[i1] * frac;
}

void GrainShifter::reset() {
    for (auto &s : buf) s = 0.0f;
    write_pos = 0;
    phase_a = 0.0;
    phase_b = 0.5;
}

float GrainShifter::process(float in, double pitch_ratio) {
    buf[write_pos & MASK] = in;
    write_pos++;

    double phase_inc = (1.0 - pitch_ratio) / static_cast<double>(grain_size);

    phase_a += phase_inc;
    phase_b += phase_inc;
    phase_a -= std::floor(phase_a);
    phase_b -= std::floor(phase_b);

    double delay_a = phase_a * grain_size + 2.0;
    double delay_b = phase_b * grain_size + 2.0;

    float sample_a = lerp_read(buf, write_pos, delay_a, MASK);
    float sample_b = lerp_read(buf, write_pos, delay_b, MASK);

    return sample_a * hann(phase_a) + sample_b * hann(phase_b);
}
