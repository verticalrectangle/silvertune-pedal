#pragma once

#include <cstdint>

struct GrainShifter {
    static constexpr uint32_t BUF_SIZE = 4096;
    static constexpr uint32_t MASK = BUF_SIZE - 1;

    float buf[BUF_SIZE] = {};
    uint32_t write_pos = 0;
    double phase_a = 0.0;
    double phase_b = 0.5;
    uint32_t grain_size = 256;

    void reset();
    float process(float in, double pitch_ratio);
};
