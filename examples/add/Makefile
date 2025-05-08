# Makefile for RISC-V add example

CC = gcc
CFLAGS = -O3
CFLAGS_VEC = -O3 -march=rv64gcv

# Default target with -O3
all: add_riscv add_riscv_vec

# Build with -O3 optimization
add_riscv: add_riscv.c
	$(CC) $(CFLAGS) -o add_riscv add_riscv.c
	$(CC) $(CFLAGS) -S -o add_riscv.s add_riscv.c

# Build with vector extensions
add_riscv_vec: add_riscv.c
	$(CC) $(CFLAGS_VEC) -o add_riscv_vec add_riscv.c
	$(CC) $(CFLAGS_VEC) -S -o add_riscv_vec.s add_riscv.c

# Clean up
clean:
	rm -f add_riscv add_riscv_vec add_riscv.s add_riscv_vec.s

.PHONY: all clean 