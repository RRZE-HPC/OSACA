# Makefile for RISC-V triad example

CC = gcc
CFLAGS = -O3
CFLAGS_VEC = -O3 -march=rv64gcv

# Default target with -O3
all: triad triad_vec

# Build with -O3 optimization
triad: triad.c
	$(CC) $(CFLAGS) -o triad triad.c
	$(CC) $(CFLAGS) -S -o triad.s triad.c

# Build with vector extensions
triad_vec: triad.c
	$(CC) $(CFLAGS_VEC) -o triad_vec triad.c
	$(CC) $(CFLAGS_VEC) -S -o triad_vec.s triad.c

# Clean up
clean:
	rm -f triad triad_vec triad.s triad_vec.s

.PHONY: all clean 