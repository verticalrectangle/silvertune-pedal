#pragma once

enum ScaleType {
    SCALE_MAJOR     = 0,
    SCALE_MINOR     = 1,
    SCALE_CHROMATIC = 2,
};

int quantize_to_scale(int midi_note, int root_key, ScaleType scale);
float midi_to_hz(float midi);
float hz_to_midi(float hz);
