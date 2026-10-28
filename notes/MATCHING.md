# Matching techniques

Techniques that fixed a near-miss in this project, with the function where they were
found. Empty sections are placeholders until the compiler is known (`notes/COMPILER.md`).

## MIPS / Allegrex basics to keep in mind

- Branch delay slots: the instruction after a branch or jump runs before the target;
  the compiler fills the slot, so a source reorder can move an instruction into or out
  of a slot.
- `$gp`-relative access (`.sdata`/`.sbss`, `$gp` = 0x148898): variables small enough
  for the small-data threshold are reached through `$gp`; the threshold is a compiler
  flag (`-G`).
- Floats: single precision FPU (`lwc1`, `mul.s`, `c.lt.s` + `bc1t`); no doubles in
  hardware.
- VFPU: assembled as `.word` (`tools/vfpu_words.py`); in C it needs inline assembly or
  intrinsics, so VFPU functions stay assembly until the compiler's VFPU support is
  known.

## Loads, aliasing and const

## Registers and stack

## Floats

## Inlining and emission order

## Data layout

## Control flow

## C++ classes, virtual calls and RTTI

## Unsolved patterns
