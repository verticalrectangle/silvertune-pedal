#include "yin.h"
#include <cmath>

static constexpr float YIN_THRESHOLD = 0.15f;

void YinDetector::init(float sample_rate) {
    sr_ = sample_rate;
    pos_ = 0;
    pitch_hz = 0.0f;
    confidence = 0.0f;
    for (uint32_t i = 0; i < BUF_SIZE; ++i) buf_[i] = 0.0f;
    for (uint32_t i = 0; i < HALF; ++i)     diff_[i] = 0.0f;
}

void YinDetector::push(float sample) {
    buf_[pos_++] = sample;
    if (pos_ >= BUF_SIZE) {
        detect();
        // Shift buffer: keep last (BUF_SIZE - HOP_SIZE) samples
        for (uint32_t i = 0; i < BUF_SIZE - HOP_SIZE; ++i)
            buf_[i] = buf_[i + HOP_SIZE];
        pos_ = BUF_SIZE - HOP_SIZE;
    }
}

void YinDetector::detect() {
    // Step 1: Difference function
    //   d(tau) = sum_j (x[j] - x[j + tau])^2
    for (uint32_t tau = 0; tau < HALF; ++tau) {
        float sum = 0.0f;
        for (uint32_t j = 0; j < HALF; ++j) {
            float delta = buf_[j] - buf_[j + tau];
            sum += delta * delta;
        }
        diff_[tau] = sum;
    }

    // Step 2: Cumulative mean normalized difference
    //   d'(0) = 1
    //   d'(tau) = d(tau) / ((1/tau) * sum(d(j), j=1..tau))
    diff_[0] = 1.0f;
    float running_sum = 0.0f;
    for (uint32_t tau = 1; tau < HALF; ++tau) {
        running_sum += diff_[tau];
        diff_[tau] = diff_[tau] * static_cast<float>(tau) / running_sum;
    }

    // Step 3: Absolute threshold — find first tau where d'(tau) < threshold
    //   then pick the local minimum after that point
    uint32_t tau_est = 0;
    for (uint32_t tau = 2; tau < HALF; ++tau) {
        if (diff_[tau] < YIN_THRESHOLD) {
            // Walk forward to the local minimum
            while (tau + 1 < HALF && diff_[tau + 1] < diff_[tau])
                ++tau;
            tau_est = tau;
            break;
        }
    }

    if (tau_est == 0) {
        // No pitch found
        pitch_hz = 0.0f;
        confidence = 0.0f;
        return;
    }

    // Step 4: Parabolic interpolation for sub-sample accuracy
    float s0 = diff_[tau_est - 1];
    float s1 = diff_[tau_est];
    float s2 = diff_[tau_est + 1 < HALF ? tau_est + 1 : tau_est];

    float shift = 0.0f;
    float denom = 2.0f * (2.0f * s1 - s2 - s0);
    if (std::fabs(denom) > 1e-12f)
        shift = (s0 - s2) / denom;

    float refined_tau = static_cast<float>(tau_est) + shift;

    pitch_hz = sr_ / refined_tau;
    confidence = 1.0f - s1; // lower d' = higher confidence
    if (confidence < 0.0f) confidence = 0.0f;
    if (confidence > 1.0f) confidence = 1.0f;
}
