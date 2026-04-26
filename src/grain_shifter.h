#pragma once

#include <cstdint>

struct GrainShifter {
    static constexpr uint32_t BUF_SIZE = 4096;
    static constexpr uint32_t MASK = BUF_SIZE - 1;

    float buf[BUF_SIZE];
    uint32_t write_pos;
    double phase_a;
    double phase_b;
    uint32_t grain_size;

    void reset();
    float process(float in, double pitch_ratio);
};
