#pragma once

#include <cstdint>

// Bare YIN pitch detector — no dependencies, no allocations.
// Feed samples one at a time via push(). When the internal buffer
// is full it runs detection automatically. Read pitch_hz and
// confidence after each push() call.

class YinDetector {
public:
    static constexpr uint32_t BUF_SIZE = 1024;
    static constexpr uint32_t HALF     = BUF_SIZE / 2;
    static constexpr uint32_t HOP_SIZE = 256;

    float pitch_hz   = 0.0f;
    float confidence  = 0.0f;

    void init(float sample_rate);
    void push(float sample);

private:
    float sr_ = 48000.0f;
    float buf_[BUF_SIZE] = {};
    uint32_t pos_ = 0;

    // YIN workspace
    float diff_[HALF] = {};

    void detect();
};
