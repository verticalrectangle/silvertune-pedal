# Silvertune Pedal — hard autotune on a Daisy Seed + Terrarium PCB
TARGET = silvertune_pedal

CPP_SOURCES = \
	src/main.cpp \
	src/yin.cpp \
	src/grain_shifter.cpp \
	src/scale.cpp

OPT = -O2

LIBDAISY_DIR = lib/libDaisy
DAISYSP_DIR = lib/DaisySP

SYSTEM_FILES_DIR = $(LIBDAISY_DIR)/core

C_INCLUDES = -Isrc

include $(SYSTEM_FILES_DIR)/Makefile
